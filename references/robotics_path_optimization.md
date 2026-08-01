# 机器人路径优化论文复现参考手册
# Robotics Path Optimization Paper Reproduction Reference

本手册面向机器人路径优化方向的论文复现，涵盖：路径规划 (Path Planning)、轨迹规划 (Trajectory Planning)、运动规划 (Motion Planning)。

---

## 1. 问题分类 / Problem Taxonomy

### 1.1 按规划对象分类

| 类别 | 英文 | 典型平台 | 维度 | 关键约束 |
|------|------|---------|------|---------|
| 路径规划 | Path Planning | 移动机器人、UAV | 2D/3D | 几何约束、障碍物 |
| 轨迹规划 | Trajectory Planning | 机械臂、足式机器人 | 关节空间/任务空间 | 动力学约束、时间最优 |
| 运动规划 | Motion Planning | 人形机器人、协作臂 | 高维 | 运动学+动力学+接触 |

### 1.2 按算法范式分类

| 范式 | 代表方法 | 特点 | 复现要点 |
|------|---------|------|---------|
| 基于搜索 | A*, D*, RRT, PRM | 概率完备 | 随机种子、采样数 |
| 基于优化 | CHOMP, TrajOpt, GPMP | 凸/非凸优化 | 求解器选择、收敛性 |
| 基于凸优化 | MICP, GCS, FastPathPlanning | 完备+高效 | SOCP/SDP/MILP 求解器 |
| 基于采样 | RRT*, BIT*, PRM* | 渐近最优 | 采样上限、碰撞检测 |
| 基于学习 | Neural Motion Planner, DRL | 数据驱动 | 网络权重、推理时间 |

### 1.3 按安全保证分类

| 保证类型 | 实现方式 | 代表论文 |
|---------|---------|---------|
| 离散碰撞检查 | 栅格/占据图 | 传统 RRT/A* |
| 连续安全证书 | 凸包/间隔证书 | FastPathPlanning, GCS |
| 鲁棒安全 | Tube/收缩 | RMPC 系列 |

---

## 2. 核心算法模板 / Core Algorithm Templates

### 2.1 凸优化路径规划 (Convex Optimization-based)

**典型论文**: FastPathPlanning (Marcucci et al., TRO 2024), GCS (Marcucci & Tedrake, Science Robotics 2023)

**问题形式**:
```
minimize    J = ∫ ‖p^(i)(t)‖² dt      (平滑性)
subject to  p(0) = p_init, p(T) = p_term
            p(t) ∈ S (安全集)
```

**求解器栈**:
- SOCP: `clarabel`, `mosek`, `ecos`
- MILP: `gurobi`, `mosek`
- SDP: `mosek`, `scs`

**复现关键点**:
1. 安全集表示（盒子交集 vs 多面体）
2. 线图构建（Line Graph）的正确性
3. 求解器参数（MIP gap, tolerance）
4. 代表点优化的收敛性

### 2.2 基于搜索的方法 (Search-based)

**典型论文**: A* variants, Theta*, ANYA

**复现关键点**:
1. 启发式函数（admissible & consistent）
2. 图/栅格分辨率
3. 打破对称性（tie-breaking）
4. 内存占用

### 2.3 基于采样的方法 (Sampling-based)

**典型论文**: RRT*, BIT*, PRM*, Informed RRT*

**复现关键点**:
1. 碰撞检测精度
2. 采样分布（均匀 vs 高斯 vs Bridge）
3. Rewiring 策略
4. 终止条件（时间 vs 迭代 vs 收敛）

---

## 3. 评估指标体系 / Evaluation Metrics

### 3.1 路径质量指标

| 指标 | 定义 | 计算方式 |
|------|------|---------|
| Path Length | 路径长度 | Σ‖pᵢ₊₁ - pᵢ‖₂ |
| Path Cost | 路径成本 | 论文定义的代价函数 J |
| Clearance | 最小间隙 | min distance to obstacles |
| Smoothness | 平滑度 | 曲率变化率或导数积分 |
| Continuity | 连续性 | C⁰, C¹, C², Cᵏ |

### 3.2 计算效率指标

| 指标 | 定义 | 单位 |
|------|------|------|
| Preprocessing Time | 预处理时间 | s |
| Online Planning Time | 在线规划时间 | s |
| Total Time | 总时间 | s |
| Memory Usage | 内存占用 | MB/GB |

### 3.3 算法性能指标

| 指标 | 定义 | 范围 |
|------|------|------|
| Success Rate | 成功率 | 0-100% |
| Optimality Gap | 最优性差距 | % |
| Completeness | 完备性 | 概率/分辨率 |

---

## 4. 常见求解器与工具链 / Solver & Toolchain

### 4.1 优化求解器对比

| 求解器 | 许可 | SOCP | SDP | MILP | 推荐场景 |
|--------|------|------|-----|------|---------|
| CLARABEL | Apache-2.0 (免费) | ✅ | ✅ | ❌ | 首选开源 |
| MOSEK | 商业/学术 | ✅ | ✅ | ✅ | 工业级 |
| GUROBI | 商业/学术 | ✅ | ❌ | ✅ | MILP 首选 |
| ECOS | GPL-3 (免费) | ✅ | ❌ | ❌ | 嵌入式 |
| SCS | MIT (免费) | ✅ | ✅ | ❌ | 大规模 SDP |
| OSQP | Apache-2.0 (免费) | QP | ❌ | ❌ | QP 问题 |

### 4.2 机器人仿真/可视化工具

| 工具 | 用途 | 推荐 |
|------|------|------|
| MeshCat | 3D 可视化（Julia/Python） | ✅ 论文常用 |
| RViz | ROS 可视化 | ✅ |
| Gazebo | 物理仿真 | ⚠️ 重 |
| MuJoCo | 接触动力学 | ✅ 强化学习 |
| CoppeliaSim | 教育/研究 | ✅ |

---

## 5. 复现工作流 / Reproduction Workflow

### 5.1 针对凸优化路径规划的特殊步骤

1. **安全集验证**: 检查盒子交集计算正确性
2. **线图验证**: 确认图构建与论文一致
3. **求解器对齐**: 使用相同求解器和参数
4. **收敛性检查**: 验证迭代次数和收敛精度

### 5.2 针对采样方法的特殊步骤

1. **种子控制**: 记录所有随机种子
2. **碰撞检测**: 确认碰撞检测器一致
3. **终止条件**: 精确复现论文的停止准则
4. **多次运行**: 至少 N=30 次以获得统计显著性

### 5.3 通用验证清单

- [ ] 路径长度/成本与论文报告一致
- [ ] 计算时间在合理范围内
- [ ] 成功率达到论文水平
- [ ] 可视化结果与论文图表一致
- [ ] 消融实验趋势一致

---

## 6. 典型数据集 / Typical Datasets

### 6.1 路径规划基准

| 数据集 | 维度 | 描述 |
|--------|------|------|
| 2D Grid Maps | 2D | BMP/PNG 地图 |
| Random Boxes | 2D/3D | 随机障碍物 |
| Maze | 2D | 迷宫环境 |
| Willow Garage | 2D | 真实办公室 |
| Mavreet | 3D | 复杂 3D 环境 |

### 6.2 轨迹规划基准

| 数据集 | 描述 |
|--------|------|
| AMP | 人形运动 |
| TOC | 任务与运动规划 |
| RoboMimic | 模仿学习数据 |

---

## 7. 常见陷阱与解决方案 / Common Pitfalls

| 陷阱 | 原因 | 解决方案 |
|------|------|---------|
| 路径长度偏差大 | 安全集表示不同 | 精确复现论文的安全集 |
| 计算时间不一致 | 求解器/参数不同 | 使用相同求解器和容差 |
| 成功率低 | 随机种子/采样不足 | 增加运行次数 |
| 收敛失败 | 初始点/步长不当 | 使用论文的初始化策略 |
| 碰撞检测差异 | 碰撞模型不同 | 使用相同碰撞检测库 |

---

## 8. 相关领域论文索引 / Related Papers

### 8.1 凸优化路径规划

- Marcucci et al., "Fast Path Planning Through Large Collections of Safe Boxes", TRO 2024
- Marcucci & Tedrake, "Motion Planning Around Obstacles with Convex Optimization", Science Robotics 2023
- Deits & Tedrake, "Footstep planning on uneven terrain with mixed-integer convex optimization", Humanoids 2014

### 8.2 基于搜索/采样的方法

- Karaman & Frazzoli, "Sampling-based Algorithms for Optimal Motion Planning", IJRR 2011
- Gammell et al., "Informed RRT*: Optimal Sampling-based Path Planning Focused via Direct Sampling of an Ellipsoidal Heuristic", IROS 2014

### 8.3 轨迹规划

- Richter et al., "Polynomial Trajectory Planning for Aggressive Quadrotor Flight in Indoor Environments", ISRR 2013
- Mellinger & Kumar, "Minimum Snap Trajectory Generation and Control for Quadrotors", ICRA 2011

---

*Reference for math-read-do-routine skill — Robotics Path Optimization Track*
