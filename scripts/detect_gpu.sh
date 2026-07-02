#!/usr/bin/env bash
# detect_gpu.sh - GPU + CUDA 检测脚本
# GPU + CUDA detection script
set -euo pipefail

echo "=== GPU Detection / GPU检测 ==="

# NVIDIA GPU
if command -v nvidia-smi &>/dev/null; then
    echo "--- nvidia-smi ---"
    nvidia-smi --query-gpu=index,name,driver_version,memory.total,compute_cap --format=csv
    echo ""
    echo "--- CUDA Version ---"
    nvcc --version 2>/dev/null || echo "nvcc not found / nvcc未找到"
else
    echo "No NVIDIA driver detected / 未检测到NVIDIA驱动"
fi

# ROCm (AMD)
if command -v rocminfo &>/dev/null; then
    echo "--- ROCm Info ---"
    rocminfo | grep -E "Name:|Version:" | head -10
fi

# Intel GPU
if command -v xpu-smi &>/dev/null; then
    echo "--- Intel XPU Info ---"
    xpu-smi discovery
fi

echo ""
echo "=== PyTorch GPU Detection / PyTorch GPU检测 ==="
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

echo ""
echo "=== TensorFlow GPU Detection / TensorFlow GPU检测 ==="
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
