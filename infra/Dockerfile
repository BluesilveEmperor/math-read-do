# Dockerfile - Math Reproduction Environment (Container alternative to Vagrant VM)
# Dockerfile - 数学复现环境 (容器替代Vagrant VM方案)

# Multi-stage build for minimal final image size / 多阶段构建以获得最小最终镜像
# ===== Stage 1: Base / 基础层 =====
FROM ubuntu:24.04 AS base

LABEL description="Math Paper Reproduction Environment / 数学论文复现环境"
LABEL maintainer="Math Reproduction Workflow"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# System packages / 系统包
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ===== Stage 2: HPC Libraries / HPC库层 =====
FROM base AS hpc

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenmpi-dev \
    libfftw3-dev \
    libhdf5-dev \
    liblapack-dev \
    libblas-dev \
    && rm -rf /var/lib/apt/lists/*

# ===== Stage 3: Python + Conda / Python环境层 =====
FROM hpc AS python-env

ARG PYTHON_VERSION=3.10.14
ARG CONDA_ENV_NAME=math-repro

# Install Miniconda / 安装Miniconda
RUN curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh

ENV PATH=/opt/conda/bin:$PATH

# Create environment with specific Python / 创建指定Python版本的环境
RUN conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VERSION} -y

ENV CONDA_PREFIX=/opt/conda/envs/${CONDA_ENV_NAME}
ENV PATH=${CONDA_PREFIX}/bin:$PATH

# Default environment.yml (override at build time / 构建时可覆盖)
COPY env/environment.yml /tmp/environment.yml
RUN conda env update -n ${CONDA_ENV_NAME} -f /tmp/environment.yml 2>/dev/null || \
    echo "No environment.yml found / 未找到environment.yml"

# ===== Stage 4: Julia / Julia层 =====
FROM python-env AS julia-env

ARG JULIA_VERSION=1.9.4

RUN curl -fsSL https://install.julialang.org | sh -s -- -y && \
    export PATH="$HOME/.juliaup/bin:$PATH" && \
    juliaup add ${JULIA_VERSION} && \
    juliaup default ${JULIA_VERSION}

ENV PATH="$HOME/.juliaup/bin:$PATH"

# ===== Stage 5: CUDA (NVIDIA base, optional) =====
# 启用方式: docker build --build-arg USE_CUDA=true -t math-repro .
# Enable: docker build --build-arg USE_CUDA=true -t math-repro .
ARG USE_CUDA=false

FROM julia-env AS cuda-env
ARG USE_CUDA
RUN if [ "$USE_CUDA" = "true" ]; then \
        apt-get update && apt-get install -y --no-install-recommends \
        nvidia-cuda-toolkit && \
        rm -rf /var/lib/apt/lists/*; \
    fi
ENV CUDA_VISIBLE_DEVICES="0"
ENV CUDA_DEVICE_ORDER="PCI_BUS_ID"

# ===== Stage 6: GPU Validation =====
FROM cuda-env AS gpu-validated
RUN python3 -c "
import torch
if torch.cuda.is_available():
    print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
    print(f'   CUDA: {torch.version.cuda}')
else:
    print('⚠️  No GPU detected, running in CPU mode')
" 2>/dev/null || echo "PyTorch not installed / PyTorch未安装"

# ===== Final Stage =====
FROM gpu-validated AS final

WORKDIR /workspace/reproduction

# Copy reproduction workspace / 复制复现工作区
COPY . /workspace/reproduction/

# Entry point / 入口
CMD ["/bin/bash"]
