#!/usr/bin/env bash
# detect_wsl.sh - WSL 环境检测与复现平台选择
# 检测用户是否已有 WSL 且 Linux 环境已配置好（Python + 关键依赖）
# 若已配置好 → recommend: "wsl"（使用 WSL Linux 进行实验复现）
# 否则 → recommend: "native"（在用户当前所在系统进行实验复现）
# 额外检测环境管理工具: uv 优先, conda 兜底
# 输出 JSON 到指定文件（默认 infra/wsl_detection.json）
set -euo pipefail

OUTPUT_FILE="${1:-infra/wsl_detection.json}"

WSL_AVAILABLE="false"
LINUX_READY="false"
DISTRO=""
PYTHON_PATH=""
UV_AVAILABLE="false"
CONDA_AVAILABLE="false"
ENV_MANAGER="none"
RECOMMEND="native"

# 检测 wsl 命令是否可用
if command -v wsl &>/dev/null; then
    WSL_AVAILABLE="true"
    # 获取默认发行版（去掉可能的回车和空格）
    DISTRO=$(wsl -l -q 2>/dev/null | head -1 | tr -d '\r\n[:space:]' || echo "")
    if [[ -n "$DISTRO" ]]; then
        # 检测 WSL 中 python3 是否可用
        PYTHON_PATH=$(wsl -d "$DISTRO" -- which python3 2>/dev/null | tr -d '\r\n' || echo "")
        if [[ -n "$PYTHON_PATH" ]]; then
            # 检测关键依赖 numpy + scipy 是否就绪
            NUMPY_OK=$(wsl -d "$DISTRO" -- python3 -c "import numpy; print('ok')" 2>/dev/null | tr -d '\r\n' || echo "fail")
            SCIPY_OK=$(wsl -d "$DISTRO" -- python3 -c "import scipy; print('ok')" 2>/dev/null | tr -d '\r\n' || echo "fail")
            if [[ "$NUMPY_OK" == "ok" && "$SCIPY_OK" == "ok" ]]; then
                LINUX_READY="true"
                RECOMMEND="wsl"
            fi
        fi

        # 检测环境管理工具 (uv 优先, conda 兜底)
        UV_CHECK=$(wsl -d "$DISTRO" -- bash -c "command -v uv && echo 'found'" 2>/dev/null | tr -d '\r\n' || echo "")
        if [[ "$UV_CHECK" == *"found"* ]]; then
            UV_AVAILABLE="true"
            ENV_MANAGER="uv"
        fi
        CONDA_CHECK=$(wsl -d "$DISTRO" -- bash -c "command -v conda && echo 'found'" 2>/dev/null | tr -d '\r\n' || echo "")
        if [[ "$CONDA_CHECK" == *"found"* ]]; then
            CONDA_AVAILABLE="true"
            if [[ "$ENV_MANAGER" == "none" ]]; then
                ENV_MANAGER="conda"
            fi
        fi
    fi
fi

# 检测 ~/projects 目录（全平台适用）
PROJECTS_DIR=""
PROJECTS_EXISTS="false"
if [[ "$WSL_AVAILABLE" == "true" && -n "$DISTRO" ]]; then
    PROJECTS_DIR=$(wsl -d "$DISTRO" -- bash -c 'echo ~/projects' 2>/dev/null | tr -d '\r\n' || echo "")
    if [[ -n "$PROJECTS_DIR" ]]; then
        PROJECTS_CHECK=$(wsl -d "$DISTRO" -- bash -c "test -d ~/projects && echo 'exists'" 2>/dev/null | tr -d '\r\n' || echo "")
        if [[ "$PROJECTS_CHECK" == "exists" ]]; then
            PROJECTS_EXISTS="true"
        fi
    fi
else
    PROJECTS_DIR="$HOME/projects"
    if [[ -d "$PROJECTS_DIR" ]]; then
        PROJECTS_EXISTS="true"
    fi
fi

# 输出 JSON
mkdir -p "$(dirname "$OUTPUT_FILE")" 2>/dev/null || true
cat > "$OUTPUT_FILE" <<EOF
{
  "wsl_available": $WSL_AVAILABLE,
  "linux_ready": $LINUX_READY,
  "distro": "$DISTRO",
  "python_path": "$PYTHON_PATH",
  "uv_available": $UV_AVAILABLE,
  "conda_available": $CONDA_AVAILABLE,
  "env_manager": "$ENV_MANAGER",
  "recommend": "$RECOMMEND",
  "projects_dir": "$PROJECTS_DIR",
  "projects_exists": $PROJECTS_EXISTS
}
EOF

echo "WSL 环境检测完成 → $OUTPUT_FILE"
echo "  wsl_available:   $WSL_AVAILABLE"
echo "  linux_ready:     $LINUX_READY"
echo "  distro:          $DISTRO"
echo "  python_path:     $PYTHON_PATH"
echo "  uv_available:    $UV_AVAILABLE"
echo "  conda_available: $CONDA_AVAILABLE"
echo "  env_manager:     $ENV_MANAGER"
echo "  recommend:       $RECOMMEND"
echo "  projects_dir:   $PROJECTS_DIR"
echo "  projects_exists: $PROJECTS_EXISTS"