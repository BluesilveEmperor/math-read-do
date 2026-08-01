#!/usr/bin/env bash
#=============================================================================
# math-read-do-obj Auto-Update Script
# 自动检查网络状态，选择最快仓库拉取更新
#
# 检查源 (按优先级排列):
#   1. https://github.com/BluesilveEmperor/math-read-do-obj
#   2. https://gitcode.com/GLY-NXD/math-read-do-obj
#
# 行为:
#   - 如果项目尚未初始化 Git 仓库，自动 init 并添加可用 remote
#   - 如果已有 Git 仓库，执行 pull 更新
#   - 无网络时跳过，不阻塞后续流程
#=============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

# ----- 颜色定义 -----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

REMOTE_NAME="upstream"

# ----- 候选仓库 -----
REPOS=(
  "https://github.com/BluesilveEmperor/math-read-do-obj"
  "https://gitcode.com/GLY-NXD/math-read-do-obj"
)

# ----- 检测网络连通性（超时 3 秒，取最快响应）-----
check_repo() {
  local url="$1"
  local host
  host=$(echo "$url" | sed -E 's|https?://([^/]+)/.*|\1|')

  # 用 curl 检测连通性（--connect-timeout 3，只检测连接，不下载）
  if curl -sS --connect-timeout 3 --max-time 5 -o /dev/null -w "%{http_code}" "https://${host}" 2>/dev/null | grep -qE '^[0-9]+$'; then
    return 0
  fi
  return 1
}

select_fastest_repo() {
  local fastest_url=""
  local fastest_time=9999

  echo -e "${CYAN}[更新] 正在检测网络环境...${NC}"

  for url in "${REPOS[@]}"; do
    local host
    host=$(echo "$url" | sed -E 's|https?://([^/]+)/.*|\1|')
    echo -ne "  检测 ${host} ... "

    local start_time end_time elapsed
    start_time=$(date +%s%N 2>/dev/null || date +%s)

    if check_repo "$url"; then
      end_time=$(date +%s%N 2>/dev/null || date +%s)
      if command -v bc &>/dev/null; then
        elapsed=$(echo "scale=2; ($end_time - $start_time) / 1000000" | bc 2>/dev/null || echo 0)
      else
        elapsed=$(( (end_time - start_time) / 1000000 2>/dev/null || 0 ))
      fi
      echo -e "${GREEN}连通 ✓ (${elapsed}ms)${NC}"

      # 取最快响应
      if (( $(echo "$elapsed < $fastest_time" | bc -l 2>/dev/null || echo 1) )); then
        fastest_time=$elapsed
        fastest_url=$url
      fi
    else
      echo -e "${RED}不可达 ✗${NC}"
    fi
  done

  echo "$fastest_url"
}

# ----- Git 操作 -----
setup_or_update() {
  local remote_url="$1"

  if [ -z "$remote_url" ]; then
    echo -e "${YELLOW}[更新] 无可达的远程仓库，跳过更新。${NC}"
    return 0
  fi

  if [ ! -d ".git" ]; then
    # ----- 首次初始化 -----
    echo -e "${CYAN}[更新] 初始化 Git 仓库...${NC}"
    git init
    git remote add "$REMOTE_NAME" "$remote_url"
    echo -e "${GREEN}[更新] 已添加 remote: ${REMOTE_NAME} → ${remote_url}${NC}"

    # 尝试 fetch
    echo -e "${CYAN}[更新] 正在拉取最新代码...${NC}"
    if git fetch "$REMOTE_NAME" --depth=1 2>/dev/null; then
      # 如果当前没有文件（空目录），尝试 reset
      if ! git rev-parse HEAD &>/dev/null; then
        # 尝试匹配分支名
        local branch
        branch=$(git ls-remote --heads "$REMOTE_NAME" 2>/dev/null | head -1 | sed 's|.*refs/heads/||')
        if [ -n "$branch" ]; then
          git branch -M "$branch"
          git reset "$REMOTE_NAME/$branch" --soft
          echo -e "${GREEN}[更新] 已同步 ${branch} 分支代码。${NC}"
        fi
      fi
    else
      echo -e "${YELLOW}[更新] 拉取失败（可能是空仓库或网络问题），继续使用本地代码。${NC}"
    fi
  else
    # ----- 已有 Git 仓库，执行更新 -----
    echo -e "${CYAN}[更新] 检查远程仓库更新...${NC}"

    # 检查是否已存在该 remote
    if git remote get-url "$REMOTE_NAME" &>/dev/null; then
      local current_url
      current_url=$(git remote get-url "$REMOTE_NAME")
      if [ "$current_url" != "$remote_url" ]; then
        echo -e "${YELLOW}[更新] remote URL 变更: ${current_url} → ${remote_url}${NC}"
        git remote set-url "$REMOTE_NAME" "$remote_url"
      fi
    else
      git remote add "$REMOTE_NAME" "$remote_url"
    fi

    # stash 本地修改（如果有），避免 pull 冲突
    local has_changes=false
    if ! git diff --quiet 2>/dev/null; then
      has_changes=true
      echo -e "${YELLOW}[更新] 暂存本地修改...${NC}"
      git stash push -m "auto-update-stash-$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
    fi

    # fetch + merge
    if git fetch "$REMOTE_NAME" --depth=1 2>/dev/null; then
      local branch
      branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "master")
      local remote_branch="${REMOTE_NAME}/${branch}"

      if git rev-parse "$remote_branch" &>/dev/null; then
        echo -e "${CYAN}[更新] 合并远程 ${branch} 分支更新...${NC}"
        if git merge "$remote_branch" --ff-only 2>/dev/null; then
          echo -e "${GREEN}[更新] ✅ 已更新到最新版本。${NC}"
        else
          echo -e "${YELLOW}[更新] 快速前进合并失败，尝试 rebase...${NC}"
          git rebase "$remote_branch" 2>/dev/null || {
            echo -e "${YELLOW}[更新] Rebase 也失败，中止并回退。若有本地修改请手动处理。${NC}"
            git rebase --abort 2>/dev/null || true
          }
        fi
      else
        echo -e "${YELLOW}[更新] 远程分支 ${branch} 不存在，跳过合并。${NC}"
      fi
    else
      echo -e "${YELLOW}[更新] 获取远程更新失败，继续使用本地代码。${NC}"
    fi

    # 恢复 stash
    if $has_changes; then
      echo -e "${GREEN}[更新] 恢复本地修改...${NC}"
      git stash pop 2>/dev/null || true
    fi
  fi
}

# ----- 主流程 -----
echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo -e "${CYAN}  math-read-do-obj 自动更新${NC}"
echo -e "${CYAN}══════════════════════════════════════════${NC}"

BEST_REPO=$(select_fastest_repo)

if [ -n "$BEST_REPO" ]; then
  echo -e "${GREEN}[更新] 已选择: ${BEST_REPO}${NC}"
  setup_or_update "$BEST_REPO"
else
  echo -e "${YELLOW}[更新] 所有远程仓库均不可达，跳过更新。${NC}"
fi

echo -e "${CYAN}══════════════════════════════════════════${NC}"
exit 0
