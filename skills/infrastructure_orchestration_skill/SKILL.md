# Infrastructure Orchestration Skill / 基础设施编排技能

## Description / 描述
检测宿主环境，决策并配置最佳运行环境（WSL2 / Vagrant VM / Docker / Native）。

## Phase / 阶段
infrastructure

## Steps / 步骤

### Step 1: Host Detection / 宿主检测
```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts/detect_host.ps1

# Linux / macOS
bash scripts/detect_host.sh
```

### Step 2: Decision Matrix / 决策矩阵
根据 `infra/host_detection.json` 和论文需求决策：

| 宿主 | 论文需求 | 推荐方案 |
|------|---------|---------|
| Windows | 无Linux依赖 | Native (Conda) |
| Windows | 需Linux工具 | WSL2 |
| Windows | 需完整隔离 | Vagrant VM |
| Windows | CI对齐 | Docker Desktop |
| macOS | 需Linux | Docker / Lima VM |
| Linux | - | Native + Docker |

### Step 3: Environment Provisioning / 环境配置
按 Step 2 决策执行对应配置脚本，产出 `infra/infra_manifest.json`。

## Outputs / 产出
- `infra/host_detection.json`: 检测结果
- `infra/infra_manifest.json`: 完整基础设施清单
- `infra/Vagrantfile` 或 `infra/Dockerfile`: 环境配置
