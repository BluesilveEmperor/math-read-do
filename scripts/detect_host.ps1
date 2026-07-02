# detect_host.ps1 - 宿主环境检测脚本 (Windows)
# Host environment detection script (Windows)
param(
    [string]$OutputFile = "infra/host_detection.json"
)

$result = @{}

# OS Detection
$os = Get-CimInstance Win32_OperatingSystem
$result["os"] = @{
    name = "Windows"
    version = $os.Version
    caption = $os.Caption
    build = $os.BuildNumber
    arch = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "x86" }
}

# Memory
$mem = Get-CimInstance Win32_ComputerSystem
$totalGB = [math]::Round($mem.TotalPhysicalMemory / 1GB, 1)
$result["memory"] = @{
    total_bytes = $mem.TotalPhysicalMemory
    total_gb = $totalGB
}

# CPU
$cpu = Get-CimInstance Win32_Processor
$result["cpu"] = @{
    cores = $cpu.NumberOfCores
    logical_processors = $cpu.NumberOfLogicalProcessors
    model = $cpu.Name.Trim()
}

# GPU
$gpuInfo = @{}
try {
    $gpu = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match "NVIDIA|AMD" } | Select-Object -First 1
    if ($gpu) {
        $gpuInfo["present"] = $true
        $gpuInfo["name"] = $gpu.Name.Trim()
        $gpuInfo["driver_version"] = $gpu.DriverVersion
        $gpuInfo["memory_gb"] = [math]::Round($gpu.AdapterRAM / 1GB, 1)

        # Try nvidia-smi for CUDA version
        $nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
        if ($nvidiaSmi) {
            $cudaVersion = & nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>$null
            $gpuInfo["cuda_version"] = $cudaVersion
        }
    } else {
        $gpuInfo["present"] = $false
    }
} catch {
    $gpuInfo["present"] = $false
    $gpuInfo["error"] = $_.Exception.Message
}
$result["gpu"] = $gpuInfo

# Virtualization capability
$result["virtualization"] = @{
    wsl2 = (Get-Command wsl -ErrorAction SilentlyContinue) -ne $null
    docker = (Get-Command docker -ErrorAction SilentlyContinue) -ne $null
    vagrant = (Get-Command vagrant -ErrorAction SilentlyContinue) -ne $null
    hyperv = (Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -ErrorAction SilentlyContinue).State -eq "Enabled"
}

# Disk
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$result["disk"] = @{
    total = "$([math]::Round($disk.Size / 1GB))GB"
    used = "$([math]::Round(($disk.Size - $disk.FreeSpace) / 1GB))GB"
    available = "$([math]::Round($disk.FreeSpace / 1GB))GB"
    filesystem = "C:"
    fstype = "NTFS"
}

# Shell
$result["shell"] = @{
    name = "PowerShell"
    version = $PSVersionTable.PSVersion.ToString()
}

# Timestamp
$result["timestamp"] = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

# Write output
$json = $result | ConvertTo-Json -Depth 3
$OutputFile = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputFile)
$null = New-Item -ItemType Directory -Path (Split-Path $OutputFile -Parent) -Force -ErrorAction SilentlyContinue
$json | Set-Content -Path $OutputFile -Encoding UTF8

Write-Host "Host detection complete / 宿主检测完成: $OutputFile"
Write-Host $json
