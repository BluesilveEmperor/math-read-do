#!/usr/bin/env bash
#=============================================================================
# math-read-do-finance Auto-Update Script
# 自动检查远程仓库是否有更新，若有则同步到本地
#
# 远程仓库: https://github.com/BluesilveEmperor/math-read-do
# 分支:     financial
#
# 特性:
#   - TTL 缓存 (24h)，缓存命中时跳过网络请求
#   - --force  跳过缓存，立即联网检查
#   - --background  后台执行同步，不阻塞主流程
#   - 网络操作加超时 (curl --max-time 10, timeout 30 git fetch)
#=============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REMOTE_NAME="origin"
REPO_URL="https://github.com/BluesilveEmperor/math-read-do"
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "financial")

# ----- 参数解析 -----
FORCE=0
BACKGROUND=0
for arg in "$@"; do
    case "$arg" in
        --force|-f)     FORCE=1 ;;
        --background|-b) BACKGROUND=1 ;;
        --help|-h)
            echo "用法: auto_update.sh [--force] [--background]"
            echo "  --force      跳过 TTL 缓存，立即联网检查"
            echo "  --background 后台执行同步，不阻塞主流程"
            exit 0 ;;
    esac
done

# ----- TTL 缓存配置 -----
CACHE_DIR=".cache"
CACHE_FILE="${CACHE_DIR}/update_cache.json"
TTL_SECONDS=86400  # 24 小时

cache_valid() {
    [ "$FORCE" -eq 1 ] && return 1
    [ ! -f "$CACHE_FILE" ] && return 1
    local last_check
    last_check=$(grep -o '"last_check"[[:space:]]*:[[:space:]]*"[^"]*"' "$CACHE_FILE" \
        | sed 's/.*: *"//;s/"$//' 2>/dev/null || echo "")
    [ -z "$last_check" ] && return 1
    local now_epoch last_epoch
    now_epoch=$(date +%s)
    last_epoch=$(date -d "$last_check" +%s 2>/dev/null || echo 0)
    [ "$last_epoch" -eq 0 ] && return 1
    local age=$(( now_epoch - last_epoch ))
    [ "$age" -lt "$TTL_SECONDS" ]
}

write_cache() {
    local remote_hash="$1"
    mkdir -p "$CACHE_DIR"
    cat > "$CACHE_FILE" <<EOF
{
  "last_check": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "branch": "${BRANCH}",
  "remote_hash": "${remote_hash}"
}
EOF
}

echo -e "${CYAN}[auto-update] 检查 ${REPO_URL} (${BRANCH}) 是否有更新...${NC}"

if cache_valid; then
    echo -e "${GREEN}  ✅ 缓存有效（24h 内已检查），跳过网络请求${NC}"
    echo -e "${CYAN}  提示: 使用 --force 立即联网检查${NC}"
    exit 0
fi

if [ "$BACKGROUND" -eq 1 ]; then
    echo -e "${YELLOW}  🔄 后台启动更新检查...${NC}"
    nohup bash "$0" --force > /dev/null 2>&1 &
    disown 2>/dev/null || true
    exit 0
fi

if [ ! -d .git ]; then
    echo -e "${YELLOW}  初始化 git 仓库...${NC}"
    git init
    git remote add "$REMOTE_NAME" "$REPO_URL" 2>/dev/null || \
        git remote set-url "$REMOTE_NAME" "$REPO_URL"
fi

if ! git remote | grep -q "^${REMOTE_NAME}$"; then
    git remote add "$REMOTE_NAME" "$REPO_URL"
fi

# ----- 网络可达性探测（超时 10s）-----
if ! curl --max-time 10 --silent --head --fail "${REPO_URL}" > /dev/null 2>&1; then
    echo -e "${RED}  ⚠️ 网络不可达（curl 超时 10s），跳过更新（使用本地版本）${NC}"
    write_cache "unknown"
    exit 0
fi

# ----- fetch 远程（超时 30s）-----
if ! timeout 30 git fetch --depth=1 "$REMOTE_NAME" "$BRANCH" --quiet 2>/dev/null; then
    echo -e "${RED}  ⚠️ 无法连接远程仓库（fetch 超时 30s），跳过更新（使用本地版本）${NC}"
    write_cache "unknown"
    exit 0
fi

LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null || echo "0")
REMOTE_HASH=$(git rev-parse "${REMOTE_NAME}/${BRANCH}" 2>/dev/null || echo "0")

write_cache "$REMOTE_HASH"

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    echo -e "${GREEN}  ✅ 已是最新版本${NC}"
    exit 0
fi

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
        git rebase --abort 2>/dev/null || true
        [ $HAS_STASH -eq 1 ] && git stash pop --quiet 2>/dev/null
        exit 1
    }
}

[ $HAS_STASH -eq 1 ] && git stash pop --quiet 2>/dev/null

echo -e "${GREEN}  ✅ math-read-do-finance 已自动更新到最新版本${NC}"
