# 轨迹可视化参考 / Trajectory Visualization Reference

本参考手册描述如何在复现报告中嵌入交互式 3D 轨迹可视化。

---

## 1. 技术方案 / Technical Approach

基于 **MeshCat** (https://github.com/rdeits/meshcat) 或 **Three.js** — 3D 可视化库，通过 CDN 在浏览器中直接渲染。

| 方案 | 库 | CDN 状态 | 推荐场景 |
|------|-----|---------|---------|
| A (首选) | MeshCat | ⚠️ meshcat@0.0.6 和 latest CDN 404 | 内部网络或本地缓存 |
| B (fallback) | Three.js | ✅ jsdelivr 可用 | 公网环境、长期维护 |

**为什么选 MeshCat**:
- 无需安装，浏览器直接渲染
- 支持动画、交互式相机
- 轻量级（~500KB JS）
- 论文级渲染质量

**为什么备选 Three.js**:
- MeshCat CDN 在 unpkg/jsdelivr 上 404（meshcat@0.0.6 和 latest）
- Three.js 在 cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js 可用
- OrbitControls 从 examples/jsm/controls/OrbitControls.js 加载
- 完全可控，无版本漂移风险

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

### 4.1 MeshCat 方案（首选，需确认 CDN 可用）

```bash
python scripts/trajectory_visualizer.py \
    --data results/uav_path_data.json \
    --output trajectory.html \
    --mode orbit-start \
    --orbit-speed 0.5
```

### 4.2 Three.js 方案（fallback）

当 MeshCat CDN 404 时，使用 Three.js 直接渲染：

```html
<!-- 在 trajectory.html 中引入 -->
<script type="module">
  import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
  import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';
  
  // 场景初始化
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);
  const controls = new OrbitControls(camera, renderer.domElement);
  
  // 轨迹用 THREE.TubeGeometry + THREE.CatmullRomCurve3
  // 障碍物用 THREE.Mesh + THREE.BoxGeometry
  // 起点/终点用 THREE.Mesh + THREE.SphereGeometry（彩色）
  // OrbitControls 内置自由旋转；Orbit 模式用 requestAnimationFrame 绕起点插值
</script>
```

### 4.3 演示模式（无数据时）

```bash
python scripts/trajectory_visualizer.py \
    --demo-maze \
    --output results/demo.html
```

### 4.4 带障碍物

```bash
python scripts/trajectory_visualizer.py \
    --data results/path.json \
    --obstacles results/obstacles.json \
    --output trajectory.html
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

双击打开 [trajectory.html](trajectory.html) 查看交互式 3D 轨迹。

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

### 7.2 Three.js 实现要点

**场景初始化**:
```javascript
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
```

**轨迹渲染**: 使用 `THREE.TubeGeometry` 沿 `THREE.CatmullRomCurve3` 生成平滑管道；障碍物用 `THREE.BoxMesh`；起点/终点用 `THREE.SphereMesh` 彩色标记。

**相机模式**: OrbitControls 内置自由旋转；Orbit 模式用 `requestAnimationFrame` 绕起点做圆周运动插值。

### 7.3 相机控制

Orbit 模式使用参数方程：
```
cam_x = start_x + R * cos(θ)
cam_y = start_y + R * sin(θ)
cam_z = start_z + h
θ += speed * dt
```

Free 模式使用 MeshCat 内置的轨道相机控制器。

### 7.4 性能优化

- 轨迹点超过 1000 时自动降采样
- 使用 `requestAnimationFrame` 保证流畅
- 障碍物实例化（复用几何体）

---

*Reference for math-read-do-routine skill — Trajectory Visualization (updated with Three.js fallback)*
