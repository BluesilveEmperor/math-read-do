#!/usr/bin/env bash
# detect_host.sh - 宿主环境检测脚本 (Linux/macOS)
# Host environment detection script (Linux/macOS)
set -euo pipefail

OUTPUT_FILE="${1:-infra/host_detection.json}"

echo "{\"os\": {" > "$OUTPUT_FILE"

# OS Detection
OS_NAME=""
OS_VERSION=""
KERNEL=""
ARCH=""

if [[ "$(uname)" == "Darwin" ]]; then
    OS_NAME="macOS"
    OS_VERSION=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
elif [[ "$(uname)" == "Linux" ]]; then
    if [ -f /etc/os-release ]; then
        OS_NAME=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
        OS_VERSION=$(grep -oP '(?<=^VERSION_ID=).+' /etc/os-release | tr -d '"')
    else
        OS_NAME="Linux"
        OS_VERSION=$(uname -r)
    fi
fi
KERNEL=$(uname -r)
ARCH=$(uname -m)

cat >> "$OUTPUT_FILE" <<OSEOF
  "name": "$OS_NAME",
  "version": "$OS_VERSION",
  "kernel": "$KERNEL",
  "arch": "$ARCH",
  "family": "$(uname)"
}
OSEOF

# Memory
echo ',  "memory": {' >> "$OUTPUT_FILE"
if [[ "$(uname)" == "Linux" ]]; then
    MEM_TOTAL_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MEM_TOTAL_GB=$(echo "scale=1; $MEM_TOTAL_KB / 1024 / 1024" | bc)
    echo "    \"total_kb\": $MEM_TOTAL_KB," >> "$OUTPUT_FILE"
    echo "    \"total_gb\": $MEM_TOTAL_GB" >> "$OUTPUT_FILE"
elif [[ "$(uname)" == "Darwin" ]]; then
    MEM_TOTAL_BYTES=$(sysctl -n hw.memsize)
    MEM_TOTAL_GB=$(echo "scale=1; $MEM_TOTAL_BYTES / 1024 / 1024 / 1024" | bc)
    echo "    \"total_bytes\": $MEM_TOTAL_BYTES," >> "$OUTPUT_FILE"
    echo "    \"total_gb\": $MEM_TOTAL_GB" >> "$OUTPUT_FILE"
fi
echo "}," >> "$OUTPUT_FILE"

# CPU
echo '  "cpu": {' >> "$OUTPUT_FILE"
if [[ "$(uname)" == "Linux" ]]; then
    CPU_COUNT=$(nproc)
    CPU_MODEL=$(grep -m1 'model name' /proc/cpuinfo | sed 's/.*: //')
elif [[ "$(uname)" == "Darwin" ]]; then
    CPU_COUNT=$(sysctl -n hw.ncpu)
    CPU_MODEL=$(sysctl -n machdep.cpu.brand_string)
fi
echo "    \"cores\": $CPU_COUNT," >> "$OUTPUT_FILE"
echo "    \"model\": \"$CPU_MODEL\"" >> "$OUTPUT_FILE"
echo "}," >> "$OUTPUT_FILE"

# GPU
echo '  "gpu": {' >> "$OUTPUT_FILE"
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    GPU_DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>/dev/null | head -1)
    CUDA_VERSION=$(nvcc --version 2>/dev/null | grep "release" | sed 's/.*release //;s/,.*//')
    echo "    \"present\": true," >> "$OUTPUT_FILE"
    echo "    \"vendor\": \"nvidia\"," >> "$OUTPUT_FILE"
    echo "    \"name\": \"$GPU_NAME\"," >> "$OUTPUT_FILE"
    echo "    \"driver_version\": \"$GPU_DRIVER\"," >> "$OUTPUT_FILE"
    echo "    \"memory\": \"$GPU_MEM\"," >> "$OUTPUT_FILE"
    echo "    \"cuda_version\": \"${CUDA_VERSION:-not_found}\"" >> "$OUTPUT_FILE"
else
    echo "    \"present\": false," >> "$OUTPUT_FILE"
    echo "    \"vendor\": \"unknown\"" >> "$OUTPUT_FILE"
fi
echo "}," >> "$OUTPUT_FILE"

# Virtualization capability
echo '  "virtualization": {' >> "$OUTPUT_FILE"
echo "    \"docker\": $(command -v docker &>/dev/null && echo 'true' || echo 'false')," >> "$OUTPUT_FILE"
echo "    \"wsl2\": $(grep -qi microsoft /proc/version 2>/dev/null && echo 'true' || echo 'false')," >> "$OUTPUT_FILE"
echo "    \"vagrant\": $(command -v vagrant &>/dev/null && echo 'true' || echo 'false')" >> "$OUTPUT_FILE"
echo "}," >> "$OUTPUT_FILE"

# Disk
echo '  "disk": {' >> "$OUTPUT_FILE"
if [[ "$(uname)" == "Linux" ]]; then
    DF_OUTPUT=$(df -BG / | tail -1)
    DISK_TOTAL=$(echo "$DF_OUTPUT" | awk '{print $2}')
    DISK_USED=$(echo "$DF_OUTPUT" | awk '{print $3}')
    DISK_AVAIL=$(echo "$DF_OUTPUT" | awk '{print $4}')
    FILESYSTEM=$(echo "$DF_OUTPUT" | awk '{print $1}')
    echo "    \"total\": \"$DISK_TOTAL\"," >> "$OUTPUT_FILE"
    echo "    \"used\": \"$DISK_USED\"," >> "$OUTPUT_FILE"
    echo "    \"available\": \"$DISK_AVAIL\"," >> "$OUTPUT_FILE"
    echo "    \"filesystem\": \"$FILESYSTEM\"," >> "$OUTPUT_FILE"
    echo "    \"fstype\": \"$(df -T / | tail -1 | awk '{print $2}')\"" >> "$OUTPUT_FILE"
fi
echo "}," >> "$OUTPUT_FILE"

# Shell
echo '  "shell": {' >> "$OUTPUT_FILE"
echo "    \"name\": \"$(basename "$SHELL")\"" >> "$OUTPUT_FILE"
echo "}," >> "$OUTPUT_FILE"

# Timestamp
echo '  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"' >> "$OUTPUT_FILE"

echo "}" >> "$OUTPUT_FILE"

echo "Host detection complete / 宿主检测完成: $OUTPUT_FILE"
cat "$OUTPUT_FILE"
