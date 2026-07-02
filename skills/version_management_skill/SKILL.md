# Version Management Skill / 版本管理技能

## Description / 描述
安装并锁定语言运行时版本、编译器、CUDA 等，确保跨环境一致。

## Phase / 阶段
environment

## Steps / 步骤

### Step 1: Version Requirement Detection / 版本需求检测
从仓库和论文中检测所有语言运行时版本需求，写入 `env/version_spec.json`。

### Step 2: Version Manager Installation / 版本管理器安装
按检测结果安装所需的版本管理器 (pyenv/juliaup/rig/nvm/sdkman)。

### Step 3: Specific Version Installation / 特定版本安装
安装每个语言运行时的精确版本。

### Step 4: Version Locking / 版本锁定
生成锁定文件:
- `env/conda-lock.yml`
- `env/requirements-locked.txt`
- `env/system-packages.txt`

### Step 5: Consistency Verification / 一致性验证
```bash
bash scripts/verify_versions.sh env/version_spec.json
```

## Outputs / 产出
- `env/version_spec.json`: 版本声明
- `env/reproduction_manifest.json`: 复现清单
- `env/conda-lock.yml`: Conda锁定
