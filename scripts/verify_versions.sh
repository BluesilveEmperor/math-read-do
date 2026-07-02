#!/usr/bin/env bash
# verify_versions.sh - 版本一致性校验脚本
# Version consistency verification script
set -euo pipefail

VERSION_SPEC="${1:-env/version_spec.json}"
PASS=0
FAIL=0

echo "=== Version Consistency Check / 版本一致性校验 ==="
echo "Spec file / 规格文件: $VERSION_SPEC"
echo ""

check_version() {
    local name="$1"
    local expected="$2"
    local actual="$3"
    if [ "$expected" = "$actual" ]; then
        echo "  ✅ $name: $actual (matches / 匹配)"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $name: expected / 期望 $expected, got / 实际 $actual"
        FAIL=$((FAIL + 1))
    fi
}

check_command() {
    local name="$1"
    local cmd="$2"
    local expected="$3"
    local actual
    actual=$(eval "$cmd" 2>/dev/null || echo "NOT_FOUND")
    check_version "$name" "$expected" "$actual"
}

if [ ! -f "$VERSION_SPEC" ]; then
    echo "Version spec not found / 未找到版本规格: $VERSION_SPEC"
    echo "Running basic version detection only / 仅运行基础版本检测"
    # Python
    echo "Python: $(python3 --version 2>&1 || python --version 2>&1 || echo 'NOT_FOUND')"
    # Julia
    echo "Julia: $(julia --version 2>/dev/null || echo 'NOT_FOUND')"
    # GCC
    echo "GCC: $(gcc --version 2>/dev/null | head -1 || echo 'NOT_FOUND')"
    # CUDA
    echo "CUDA: $(nvcc --version 2>/dev/null | grep release | sed 's/.*release //;s/,.*//' || echo 'NOT_FOUND')"
    exit 1
fi

# Parse and check
echo "--- Python ---"
PY_SPEC=$(python3 -c "import json; d=json.load(open('$VERSION_SPEC')); print(d.get('python', 'N/A'))" 2>/dev/null || echo "N/A")
PY_ACTUAL=$(python3 --version 2>&1 | awk '{print $2}')
check_version "Python" "$PY_SPEC" "$PY_ACTUAL"

echo "--- Julia ---"
JL_SPEC=$(python3 -c "import json; d=json.load(open('$VERSION_SPEC')); print(d.get('julia', 'N/A'))" 2>/dev/null || echo "N/A")
JL_ACTUAL=$(julia --version 2>/dev/null | awk '{print $3}' || echo "NOT_FOUND")
check_version "Julia" "$JL_SPEC" "$JL_ACTUAL"

echo "--- GCC ---"
GCC_SPEC=$(python3 -c "import json; d=json.load(open('$VERSION_SPEC')); print(d.get('gcc', 'N/A'))" 2>/dev/null || echo "N/A")
GCC_ACTUAL=$(gcc --version 2>/dev/null | head -1 | grep -oP '\d+\.\d+\.\d+' || echo "NOT_FOUND")
check_version "GCC" "$GCC_SPEC" "$GCC_ACTUAL"

echo "--- CUDA ---"
CUDA_SPEC=$(python3 -c "import json; d=json.load(open('$VERSION_SPEC')); print(d.get('cuda', 'N/A'))" 2>/dev/null || echo "N/A")
CUDA_ACTUAL=$(nvcc --version 2>/dev/null | grep "release" | sed 's/.*release //;s/,.*//' || echo "NOT_FOUND")
check_version "CUDA" "$CUDA_SPEC" "$CUDA_ACTUAL"

echo ""
echo "=== Summary / 摘要 ==="
echo "Passed / 通过: $PASS"
echo "Failed / 失败: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    echo "⚠️  Some version mismatches detected, check env/version_spec.json"
    echo "⚠️  检测到版本不匹配，请检查 env/version_spec.json"
    exit 1
else
    echo "✅ All versions match / 所有版本一致"
    exit 0
fi
