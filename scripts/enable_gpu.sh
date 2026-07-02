#!/usr/bin/env bash
# enable_gpu.sh - 独立显卡自动检测与启用 (Linux/macOS)
# Auto-detect and enable discrete GPU (Linux/macOS)
set -euo pipefail

OUTPUT_DIR="${1:-infra}"
mkdir -p "$OUTPUT_DIR"

echo "========================================="
echo "  GPU Detection & Configuration / GPU检测与配置"
echo "========================================="

# ---------- NVIDIA ----------
detect_nvidia() {
    if ! command -v nvidia-smi &>/dev/null; then
        return 1
    fi

    echo "  ✅ NVIDIA GPU detected / 检测到NVIDIA显卡"

    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader 2>/dev/null | head -1)
    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>/dev/null | head -1)
    DRIVER_VER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
    CUDA_VER=$(nvcc --version 2>/dev/null | grep "release" | sed 's/.*release //;s/,.*//' || echo "unknown")

    echo "  GPU: $GPU_NAME"
    echo "  Count / 数量: $GPU_COUNT"
    echo "  Memory / 显存: $GPU_MEM"
    echo "  Driver / 驱动: $DRIVER_VER"
    echo "  CUDA: ${CUDA_VER:-not found / 未找到}"

    # Set CUDA environment variables / 设置CUDA环境变量
    export CUDA_DEVICE_ORDER="PCI_BUS_ID"
    export CUDA_VISIBLE_DEVICES="0"
    echo "  ✅ CUDA_VISIBLE_DEVICES=0 set / 已设置"

    # Persist to .env for reproduction manifest / 持久化到.env
    cat > "$OUTPUT_DIR/gpu_env.sh" <<EOF
export CUDA_DEVICE_ORDER="PCI_BUS_ID"
export CUDA_VISIBLE_DEVICES="0"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128"
EOF

    # Multi-GPU / 多卡
    if [ "$GPU_COUNT" -gt 1 ]; then
        VISIBLE=""
        for ((i=0; i<GPU_COUNT; i++)); do
            [ -n "$VISIBLE" ] && VISIBLE+=","
            VISIBLE+="$i"
        done
        export CUDA_VISIBLE_DEVICES="$VISIBLE"
        echo "  ✅ Multi-GPU: CUDA_VISIBLE_DEVICES=$VISIBLE"
        sed -i "s/CUDA_VISIBLE_DEVICES=.*/CUDA_VISIBLE_DEVICES=\"$VISIBLE\"/" "$OUTPUT_DIR/gpu_env.sh"
    fi

    return 0
}

# ---------- AMD ROCm ----------
detect_amd() {
    if ! command -v rocminfo &>/dev/null; then
        return 1
    fi

    echo "  ✅ AMD GPU detected / 检测到AMD显卡"

    export HIP_VISIBLE_DEVICES=0
    export HSA_OVERRIDE_GFX_VERSION=10.3.0  # adjust per GPU / 按GPU调整

    cat > "$OUTPUT_DIR/gpu_env.sh" <<EOF
export HIP_VISIBLE_DEVICES="0"
export HSA_OVERRIDE_GFX_VERSION="10.3.0"
EOF

    echo "  ✅ HIP_VISIBLE_DEVICES=0 set / 已设置"
    return 0
}

# ---------- Intel XPU ----------
detect_intel() {
    if ! command -v xpu-smi &>/dev/null; then
        return 1
    fi

    echo "  ✅ Intel GPU detected / 检测到Intel显卡"
    export ZE_AFFINITY_MASK="0"

    cat > "$OUTPUT_DIR/gpu_env.sh" <<EOF
export ZE_AFFINITY_MASK="0"
EOF

    echo "  ✅ ZE_AFFINITY_MASK=0 set / 已设置"
    return 0
}

# ---------- Framework validation / 框架验证 ----------
validate_frameworks() {
    echo ""
    echo "--- Framework Validation / 框架GPU验证 ---"

    # PyTorch
    if python3 -c "import torch" 2>/dev/null; then
        PYTORCH_GPU=$(python3 -c "
import torch
if torch.cuda.is_available():
    print(f'PyTorch: ✅ CUDA available')
    print(f'  Device: {torch.cuda.get_device_name(0)}')
    print(f'  Count: {torch.cuda.device_count()}')
else:
    print('PyTorch: ❌ CUDA not available')
" 2>/dev/null)
        echo "$PYTORCH_GPU"
    fi

    # TensorFlow
    if python3 -c "import tensorflow as tf" 2>/dev/null; then
        TF_GPU=$(python3 -c "
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f'TensorFlow: ✅ GPU available ({len(gpus)} device(s))')
    for g in gpus:
        print(f'  {g}')
else:
    print('TensorFlow: ❌ GPU not available')
" 2>/dev/null)
        echo "$TF_GPU"
    fi

    # JAX
    if python3 -c "import jax" 2>/dev/null; then
        JAX_GPU=$(python3 -c "
import jax
devices = jax.devices()
gpu_count = sum(1 for d in devices if d.platform == 'gpu')
if gpu_count > 0:
    print(f'JAX: ✅ GPU available ({gpu_count} device(s))')
else:
    print(f'JAX: ❌ GPU not available (devices: {devices})')
" 2>/dev/null)
        echo "$JAX_GPU"
    fi
}

# ---------- Write GPU manifest / 写入GPU清单 ----------
write_manifest() {
    local gpu_vendor="$1"
    local gpu_name="$2"
    local driver_ver="$3"
    local cuda_ver="$4"
    local mem="$5"

    cat > "$OUTPUT_DIR/gpu_manifest.json" <<EOF
{
  "gpu": {
    "present": true,
    "vendor": "$gpu_vendor",
    "name": "$gpu_name",
    "count": $GPU_COUNT,
    "driver_version": "$driver_ver",
    "cuda_version": "$cuda_ver",
    "memory": "$mem"
  },
  "frameworks": {
    "pytorch": $(python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo false),
    "tensorflow": $(python3 -c "import tensorflow as tf; print(len(tf.config.list_physical_devices('GPU')) > 0)" 2>/dev/null || echo false),
    "jax": $(python3 -c "import jax; print(sum(1 for d in jax.devices() if d.platform == 'gpu') > 0)" 2>/dev/null || echo false)
  },
  "env": {
    "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
    "CUDA_VISIBLE_DEVICES": "${CUDA_VISIBLE_DEVICES:-0}"
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
    echo ""
    echo "  ✅ GPU manifest written / GPU清单已写入: $OUTPUT_DIR/gpu_manifest.json"
}

# ---------- Main ----------
main() {
    if detect_nvidia; then
        write_manifest "nvidia" "$GPU_NAME" "$DRIVER_VER" "${CUDA_VER:-}" "$GPU_MEM"
    elif detect_amd; then
        GPU_NAME=$(rocminfo 2>/dev/null | grep "Name:" | head -1 | awk '{print $2}')
        write_manifest "amd" "${GPU_NAME:-AMD}" "" "" ""
    elif detect_intel; then
        GPU_NAME=$(xpu-smi discovery 2>/dev/null | grep "Device Name" | head -1 | cut -d: -f2 | xargs)
        write_manifest "intel" "${GPU_NAME:-Intel}" "" "" ""
    else
        echo "  ❌ No discrete GPU detected / 未检测到独立显卡"
        echo "  → Running in CPU mode / 将使用CPU模式运行"
        cat > "$OUTPUT_DIR/gpu_manifest.json" <<EOF
{
  "gpu": { "present": false, "vendor": "none" },
  "frameworks": {},
  "env": {},
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
        # Source gpu_env.sh if it exists / 如存在则引用
        [ -f "$OUTPUT_DIR/gpu_env.sh" ] && source "$OUTPUT_DIR/gpu_env.sh"
    fi

    validate_frameworks
}

main
