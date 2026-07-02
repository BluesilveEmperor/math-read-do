# enable_gpu.ps1 - 独立显卡自动检测与启用 (Windows)
# Auto-detect and enable discrete GPU (Windows)
param(
    [string]$OutputDir = "infra"
)

$null = New-Item -ItemType Directory -Path $OutputDir -Force

Write-Host "========================================="
Write-Host "  GPU Detection & Configuration"
Write-Host "========================================="

# ---------- Detect NVIDIA via nvidia-smi ----------
$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
$gpuDetected = $false

if ($nvidiaSmi) {
    Write-Host "  ✅ NVIDIA GPU detected / 检测到NVIDIA显卡"

    $gpuName = & nvidia-smi --query-gpu=name --format=csv,noheader 2>$null | Select-Object -First 1
    $gpuCount = (& nvidia-smi --query-gpu=count --format=csv,noheader 2>$null | Select-Object -First 1)
    $gpuMem = & nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>$null | Select-Object -First 1
    $driverVer = & nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>$null | Select-Object -First 1

    Write-Host "  GPU: $gpuName"
    Write-Host "  Count / 数量: $gpuCount"
    Write-Host "  Memory / 显存: $gpuMem"
    Write-Host "  Driver / 驱动: $driverVer"

    # Set environment variable / 设置环境变量
    [Environment]::SetEnvironmentVariable("CUDA_VISIBLE_DEVICES", "0", "Process")
    [Environment]::SetEnvironmentVariable("CUDA_DEVICE_ORDER", "PCI_BUS_ID", "Process")

    Write-Host "  ✅ CUDA_VISIBLE_DEVICES=0 set / 已设置"

    # Check WSL2 GPU / 检查WSL2 GPU
    $wsl = Get-Command wsl -ErrorAction SilentlyContinue
    if ($wsl) {
        $wslGpu = & wsl nvidia-smi --query-gpu=name --format=csv,noheader 2>$null | Select-Object -First 1
        if ($wslGpu) {
            Write-Host "  ✅ WSL2 GPU accessible: $wslGpu"
        }
    }

    $gpuDetected = $true
} else {
    # Check via WMI / 通过WMI检测
    try {
        $gpu = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match "NVIDIA|AMD|Radeon" } | Select-Object -First 1
        if ($gpu) {
            Write-Host "  ⚠️  GPU detected via WMI / 通过WMI检测到显卡: $($gpu.Name)"
            Write-Host "  → nvidia-smi not found. Install NVIDIA driver for CUDA support."
            Write-Host "  → 未找到 nvidia-smi, 请安装NVIDIA驱动以启用CUDA"
            $gpuDetected = $true
        }
    } catch {
        $gpuDetected = $false
    }
}

if (-not $gpuDetected) {
    Write-Host "  ❌ No discrete GPU detected / 未检测到独立显卡"
    Write-Host "  → Running in CPU mode / 将使用CPU模式运行"
}

# ---------- Framework validation / 框架验证 ----------
Write-Host ""
Write-Host "--- Framework Validation / 框架GPU验证 ---"

$pytorchOk = $false
$tfOk = $false

try {
    $pytorchGpu = & python -c "
import torch
if torch.cuda.is_available():
    print(f'PyTorch: ✅ CUDA available')
    print(f'  Device: {torch.cuda.get_device_name(0)}')
    print(f'  Count: {torch.cuda.device_count()}')
else:
    print('PyTorch: ❌ CUDA not available')
" 2>$null
    Write-Host $pytorchGpu
    $pytorchOk = $true
} catch {
    Write-Host "  PyTorch: not installed / 未安装"
}

try {
    $tfGpu = & python -c "
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f'TensorFlow: ✅ GPU available ({len(gpus)} device(s))')
    for g in gpus:
        print(f'  {g}')
else:
    print('TensorFlow: ❌ GPU not available')
" 2>$null
    Write-Host $tfGpu
    $tfOk = $true
} catch {
    Write-Host "  TensorFlow: not installed / 未安装"
}

# ---------- Write GPU manifest / 写入GPU清单 ----------
$manifest = @{
    gpu = @{
        present = $gpuDetected
        vendor = if ($nvidiaSmi) { "nvidia" } elseif ($gpuDetected) { "amd" } else { "none" }
        name = if ($nvidiaSmi) { $gpuName } else { "" }
        count = if ($nvidiaSmi) { $gpuCount } else { 0 }
        driver_version = if ($nvidiaSmi) { $driverVer } else { "" }
        memory = if ($nvidiaSmi) { $gpuMem } else { "" }
    }
    frameworks = @{
        pytorch = $pytorchOk
        tensorflow = $tfOk
    }
    env = @{
        CUDA_DEVICE_ORDER = "PCI_BUS_ID"
        CUDA_VISIBLE_DEVICES = "0"
    }
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$manifestPath = Join-Path $OutputDir "gpu_manifest.json"
$manifest | ConvertTo-Json -Depth 3 | Set-Content -Path $manifestPath -Encoding UTF8
Write-Host "`n  ✅ GPU manifest written / GPU清单已写入: $manifestPath"

# Generate .bat for environment persistence / 生成.bat环境变量文件
$batPath = Join-Path $OutputDir "gpu_env.bat"
@"
@echo off
set CUDA_DEVICE_ORDER=PCI_BUS_ID
set CUDA_VISIBLE_DEVICES=0
"@ | Set-Content -Path $batPath -Encoding ASCII
Write-Host "  ✅ GPU env script written / GPU环境脚本已写入: $batPath"
