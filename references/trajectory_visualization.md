# 轨迹可视化参考 / Trajectory Visualization Reference

本参考手册描述如何在复现报告中嵌入交互式 3D 轨迹可视化。

---

## 1. 技术方案 / Technical Approach

基于 **MeshCat** (https://github.com/rdeits/meshcat) — Julia/Python 3D 可视化库，通过 CDN 在浏览器中直接渲染。

**为什么选 MeshCat**:
- 无需安装，浏览器直接渲染
- 支持动画、交互式相机
- 轻量级（~500KB JS）
- 论文级渲染质量

---

## 2. 两种相机模式 / Camera Modes

### 2.1 绕起点旋转 (Orbit Start)

**用途**: 自动环绕观察整条轨迹的全貌

**实现原理**:
- 相机绕起点所在垂直轴（Z 轴）做圆周运动
- 相机始终看向起点
- 旋转速度可调（默认 0.5 rad/s）

**适用场景**:
- 展示轨迹整体形状
- 演示路径规划结果
- 对比不同算法的路径

### 2.2 自由旋转 (Free Rotate)

**用途**: 用户自主观察细节

**实现原理**:
- 鼠标左键拖拽: 旋转视角
- 滚轮: 缩放
- 双击: 重置视角

**适用场景**:
- 观察轨迹局部细节
- 检查碰撞/间隙
- 分析曲率变化

---

## 3. 数据格式 / Data Format

轨迹数据 JSON 格式：

```json
{
  "t_samples": [0.0, 0.03, 0.06, ...],
  "positions": [[x1,y1,z1], [x2,y2,z2], ...]
}
```

- `t_samples`: N 个时间戳（秒）
- `positions`: N×3 坐标数组
- N 建议 100-2000 点（过多会影响性能）

---

## 4. 使用方式 / Usage

### 4.1 从实验数据生成

```bash
python scripts/trajectory_visualizer.py \
    --data results/uav_path_data.json \
    --output results/trajectory.html \
    --mode orbit-start \
    --orbit-speed 0.5
```

### 4.2 演示模式（无数据时）

```bash
python scripts/trajectory_visualizer.py \
    --demo-maze \
    --output results/demo.html
```

### 4.3 带障碍物

```bash
python scripts/trajectory_visualizer.py \
    --data results/path.json \
    --obstacles results/obstacles.json \
    --output results/trajectory.html
```

障碍物格式：
```json
[
    {"center": [x,y,z], "size": [sx,sy,sz], "color": [r,g,b]},
    ...
]
```

---

## 5. 自定义选项 / Customization

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--orbit-axis` | 旋转轴 (z/x/y) | z |
| `--orbit-speed` | 旋转速度 (rad/s) | 0.5 |
| `--path-color` | 轨迹颜色 R,G,B | 0,0,255 |
| `--bg-color` | 背景颜色 R,G,B | 255,255,255 |
| `--title` | 页面标题 | Trajectory Visualization |

---

## 6. 与报告集成 / Integration with Reports

生成的 HTML 文件应放在 `实验复刻结果汇总/实验图表（含代码）/` 目录下，并在复现报告中引用：

```markdown
## 轨迹可视化

双击打开 [trajectory.html](../实验图表（含代码）/trajectory.html) 查看交互式 3D 轨迹。

- 支持绕起点自动旋转和自由旋转两种模式
- 可播放动画观察运动过程
- 绿色球 = 起点，红色球 = 终点
```

---

## 7. 实现细节 / Implementation Details

### 7.1 MeshCat 协议

MeshCat 使用自定义二进制协议通信。动画数据编码为 `set_animation` 命令，格式：
- 头部: 动画元数据 (fps, name, tracks)
- 每个 track: 路径 + 类型 (如 position) + 关键帧

### 7.2 相机控制

Orbit 模式使用参数方程：
```
cam_x = start_x + R * cos(θ)
cam_y = start_y + R * sin(θ)
cam_z = start_z + h
θ += speed * dt
```

Free 模式使用 MeshCat 内置的轨道相机控制器。

### 7.3 性能优化

- 轨迹点超过 1000 时自动降采样
- 使用 `requestAnimationFrame` 保证流畅
- 障碍物实例化（复用几何体）

---

*Reference for math-read-do-routine skill — Trajectory Visualization*
