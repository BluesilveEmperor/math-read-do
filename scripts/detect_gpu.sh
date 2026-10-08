#!/usr/bin/env bash
# detect_gpu.sh - GPU + CUDA 检测脚本
# GPU + CUDA detection script
#
# 按需探测（P2 优化）：先用 nvidia-smi / 环境变量快速判断是否存在 GPU，
# 仅在检测到 GPU 时才 import torch / tensorflow，避免无 GPU 环境下
# 顺序加载两个重量级框架导致 Phase 0 首响慢数秒。
set -euo pipefail

echo "=== GPU Detection / GPU检测 ==="

# 快速门控：判断是否需要进入重量级框架检测
HAVE_NVIDIA_GPU=0
HAVE_ROCM_GPU=0
HAVE_INTEL_GPU=0

# NVIDIA GPU
if command -v nvidia-smi &>/dev/null; then
    echo "--- nvidia-smi ---"
    if nvidia-smi --query-gpu=index,name,driver_version,memory.total,compute_cap --format=csv; then
        HAVE_NVIDIA_GPU=1
    fi
    echo ""
    echo "--- CUDA Version ---"
    nvcc --version 2>/dev/null || echo "nvcc not found / nvcc未找到"
else
    echo "No NVIDIA driver detected / 未检测到NVIDIA驱动"
fi

# 也认 CUDA_VISIBLE_DEVICES 环境变量：非空且不等于空集才视为有 GPU
if [[ "${CUDA_VISIBLE_DEVICES:-}" != "" && "${CUDA_VISIBLE_DEVICES:-}" != "-1" ]]; then
    HAVE_NVIDIA_GPU=1
    echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES} -> 视为存在 NVIDIA GPU"
fi

# ROCm (AMD)
if command -v rocminfo &>/dev/null; then
    echo "--- ROCm Info ---"
    if rocminfo | grep -E "Name:|Version:" | head -10; then
        HAVE_ROCM_GPU=1
    fi
fi

# Intel GPU
if command -v xpu-smi &>/dev/null; then
    echo "--- Intel XPU Info ---"
    if xpu-smi discovery; then
        HAVE_INTEL_GPU=1
    fi
fi

echo ""
echo "=== Framework GPU Detection / 框架 GPU 检测（按需）==="

# 门控：仅当检测到任一 GPU 时才 import 重量级框架，避免无 GPU 时
# 顺序加载 torch + tensorflow 拖慢首响。
if [[ "${HAVE_NVIDIA_GPU}" == "0" && "${HAVE_ROCM_GPU}" == "0" && "${HAVE_INTEL_GPU}" == "0" ]]; then
    echo "No GPU detected by fast probes (nvidia-smi/rocminfo/xpu-smi/CUDA_VISIBLE_DEVICES)."
    echo "未通过快速探测发现 GPU，跳过 PyTorch/TensorFlow 重量级 import 以缩短首响。"
    echo "如需强制检测框架，设置环境变量 FORCE_FRAMEWORK_PROBE=1。"
else
    echo "Detected GPU by fast probe; proceeding to framework import."
    echo "通过快速探测发现 GPU，继续加载框架。"
fi

# PyTorch：仅在有 GPU 或强制探测时才 import
if [[ "${HAVE_NVIDIA_GPU}" == "1" || "${HAVE_ROCM_GPU}" == "1" || "${HAVE_INTEL_GPU}" == "1" || "${FORCE_FRAMEWORK_PROBE:-0}" == "1" ]]; then
    echo ""
    echo "--- PyTorch GPU Detection / PyTorch GPU检测 ---"
    python3 -c "
import torch
if torch.cuda.is_available():
    print(f'CUDA Available: True')
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'Device Count: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'  [{i}] {torch.cuda.get_device_name(i)}')
else:
    print('CUDA Available: False')
" 2>/dev/null || echo "PyTorch not installed / PyTorch未安装"
else
    echo "PyTorch probe skipped (no GPU). / 跳过 PyTorch 探测（无 GPU）"
fi

# TensorFlow：仅在有 GPU 或强制探测时才 import
if [[ "${HAVE_NVIDIA_GPU}" == "1" || "${HAVE_ROCM_GPU}" == "1" || "${HAVE_INTEL_GPU}" == "1" || "${FORCE_FRAMEWORK_PROBE:-0}" == "1" ]]; then
    echo ""
    echo "--- TensorFlow GPU Detection / TensorFlow GPU检测 ---"
    python3 -c "
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f'GPU Available: True ({len(gpus)} device(s))')
    for gpu in gpus:
        print(f'  {gpu}')
else:
    print('GPU Available: False')
" 2>/dev/null || echo "TensorFlow not installed / TensorFlow未安装"
else
    echo "TensorFlow probe skipped (no GPU). / 跳过 TensorFlow 探测（无 GPU）"
fi
