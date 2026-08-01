#!/usr/bin/env bash
#=============================================================================
# math-read-do-routine Auto-Update Script
# 自动检查远程仓库是否有更新，若有则同步到本地
#
# 远程仓库: https://github.com/BluesilveEmperor/math-read-do
# 分支:     math-read-do-obj
#=============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

# ----- 颜色定义 -----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REMOTE_NAME="origin"
REPO_URL="https://github.com/BluesilveEmperor/math-read-do"
BRANCH="math-read-do-routine"

echo -e "${CYAN}[auto-update] 检查 ${REPO_URL} (${BRANCH}) 是否有更新...${NC}"

# ----- 检查是否已是 git 仓库 -----
if [ ! -d .git ]; then
    echo -e "${YELLOW}  初始化 git 仓库...${NC}"
    git init
    git remote add "$REMOTE_NAME" "$REPO_URL" 2>/dev/null || git remote set-url "$REMOTE_NAME" "$REPO_URL"
fi

# ----- 确保 remote 已配置 -----
if ! git remote | grep -q "^${REMOTE_NAME}$"; then
    git remote add "$REMOTE_NAME" "$REPO_URL"
fi

# ----- fetch 远程 -----
if ! git fetch --depth=1 "$REMOTE_NAME" "$BRANCH" --quiet 2>/dev/null; then
    echo -e "${RED}  ⚠️ 无法连接远程仓库，跳过更新（使用本地版本）${NC}"
    exit 0
fi

# ----- 比较本地与远程 -----
LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null || echo "0")
REMOTE_HASH=$(git rev-parse "${REMOTE_NAME}/${BRANCH}" 2>/dev/null || echo "0")

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    echo -e "${GREEN}  ✅ 已是最新版本${NC}"
    exit 0
fi

# ----- 有更新：stash 本地修改 -> pull -> pop -----
echo -e "${YELLOW}  🔄 检测到更新，正在同步...${NC}"

HAS_STASH=0
if ! git diff --quiet HEAD 2>/dev/null; then
    git stash push -m "auto-update-stash-$(date +%s)" --quiet
    HAS_STASH=1
fi

git merge --ff-only "${REMOTE_NAME}/${BRANCH}" --quiet 2>/dev/null || {
    echo -e "${RED}  ⚠️ 快进合并失败，尝试 rebase...${NC}"
    git rebase "${REMOTE_NAME}/${BRANCH}" --quiet 2>/dev/null || {
        echo -e "${RED}  ❌ 更新失败，请手动解决冲突${NC}"
        git rebase --abort 2>/dev/null
        [ $HAS_STASH -eq 1 ] && git stash pop --quiet 2>/dev/null
        exit 1
    }
}

[ $HAS_STASH -eq 1 ] && git stash pop --quiet 2>/dev/null

echo -e "${GREEN}  ✅ math-read-do-routine 已自动更新到最新版本${NC}"
