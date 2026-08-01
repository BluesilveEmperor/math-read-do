#!/usr/bin/env python3
"""
trajectory_visualizer.py - 机器人轨迹实时可视化 HTML 生成器
Robotics Trajectory Real-Time Visualization HTML Generator

基于 Three.js (CDN) 实现，无需后端，双击 HTML 即看实时轨迹。

支持两种相机模式：
  1. orbit-start: 绕起点所在垂直平面法线轴旋转（自动环绕观察）
  2. free: 自由旋转（OrbitControls 鼠标拖拽 + 滚轮缩放）

用法:
    python trajectory_visualizer.py --data results/uav_path_data.json --output results/trajectory.html
    python trajectory_visualizer.py --demo-maze --output results/maze_demo.html
    python trajectory_visualizer.py --demo-random-boxes --output results/boxes_demo.html

输入数据格式 (JSON):
{
  "t_samples": [0.0, 0.03, ...],
  "positions": [[x,y,z], [x,y,z], ...]     // N×3 轨迹点
}
"""
import os
import sys
import json
import argparse
import math
from pathlib import Path


def generate_demo_trajectory(demo_type="maze", n_points=500):
    """Generate demo trajectory data."""
    import random
    
    t_samples = []
    positions = []
    
    if demo_type == "maze":
        random.seed(42)
        x, y, z = 0.0, 0.0, 2.0
        for i in range(n_points):
            t = i * 0.03
            t_samples.append(t)
            phase = i / n_points
            if phase < 0.25:
                x += 0.05 + random.gauss(0, 0.01)
                y += random.gauss(0, 0.01)
            elif phase < 0.5:
                x += random.gauss(0, 0.01)
                y += 0.05 + random.gauss(0, 0.01)
            elif phase < 0.75:
                x += 0.05 + random.gauss(0, 0.01)
                y += random.gauss(0, 0.02)
            else:
                x += random.gauss(0, 0.01)
                y += 0.05 + random.gauss(0, 0.01)
            z = 2.0 + 0.5 * math.sin(i * 0.05)
            positions.append([x, y, z])
    
    elif demo_type == "random_boxes":
        random.seed(123)
        x, y, z = 5.0, 5.0, 1.0
        vx, vy = 0.0, 0.0
        for i in range(n_points):
            t = i * 0.02
            t_samples.append(t)
            ax = random.gauss(0, 0.3)
            ay = random.gauss(0, 0.3)
            vx = 0.9 * vx + 0.1 * ax
            vy = 0.9 * vy + 0.1 * ay
            x += vx
            y += vy
            z = 1.0 + 2.0 * abs(math.sin(i * 0.01))
            positions.append([x, y, z])
    
    elif demo_type == "uav_village":
        random.seed(456)
        for i in range(n_points):
            t = i * 0.03
            t_samples.append(t)
            phase = i / n_points
            angle = phase * 4 * math.pi
            x = 25.0 + 20.0 * math.cos(angle) + random.gauss(0, 0.2)
            y = 25.0 + 20.0 * math.sin(angle) + random.gauss(0, 0.2)
            z = 3.0 + 2.0 * math.sin(phase * 6 * math.pi)
            positions.append([x, y, z])
    
    return {"t_samples": t_samples, "positions": positions}


def generate_html(data, title="Trajectory Visualization",
                  mode="orbit-start", orbit_axis="z", orbit_speed=0.5,
                  show_path=True, show_obstacles=False, obstacles=None,
                  path_color=(0, 0, 255), background_color=(255, 255, 255)):
    """Generate interactive HTML with Three.js viewer and camera controls."""
    t_samples = data["t_samples"]
    positions = data["positions"]
    
    start_pos = positions[0] if positions else [0, 0, 0]
    
    # Normalize orbit axis
    axis_map = {"z": [0, 0, 1], "x": [1, 0, 0], "y": [0, 1, 0]}
    orbit_axis_vec = axis_map.get(orbit_axis, [0, 0, 1])
    
    # Prepare data as JSON for JS
    t_json = json.dumps(t_samples)
    pos_json = json.dumps(positions)
    obstacles_json = json.dumps(obstacles or [])
    
    path_color_hex = '#%02x%02x%02x' % path_color
    bg_color_hex = '#%02x%02x%02x' % background_color
    
    # Compute orbit parameters
    max_dist = 0
    for p in positions:
        d = math.sqrt((p[0]-start_pos[0])**2 + (p[1]-start_pos[1])**2 + (p[2]-start_pos[2])**2)
        if d > max_dist:
            max_dist = d
    orbit_radius = max(max_dist * 2.0, 10.0)
    orbit_height_offset = max_dist * 0.5
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
    body {{ margin: 0; overflow: hidden; font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; background: {bg_color_hex}; }}
    #viewer {{ width: 100vw; height: 100vh; display: block; }}
    
    /* 控制面板 */
    #controls {{
        position: fixed; top: 16px; left: 16px; z-index: 100;
        background: rgba(255,255,255,0.94); backdrop-filter: blur(12px);
        border-radius: 14px; padding: 16px 20px; min-width: 240px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18); border: 1px solid rgba(0,0,0,0.06);
    }}
    #controls h3 {{ margin: 0 0 12px 0; font-size: 14px; font-weight: 600; color: #1a1a1a; letter-spacing: 0.3px; }}
    
    /* 模式选择 */
    .mode-select {{ display: flex; gap: 8px; margin-bottom: 14px; }}
    .mode-btn {{
        flex: 1; padding: 8px 10px; border: 2px solid #e0e0e0; border-radius: 10px;
        background: #fff; cursor: pointer; font-size: 11px; font-weight: 500;
        transition: all 0.25s ease; color: #555; text-align: center; line-height: 1.4;
    }}
    .mode-btn:hover {{ border-color: #4A90D9; color: #4A90D9; transform: translateY(-1px); }}
    .mode-btn.active {{ border-color: #4A90D9; background: linear-gradient(135deg, #4A90D9, #357ABD); color: #fff; box-shadow: 0 4px 12px rgba(74,144,217,0.3); }}
    .mode-btn small {{ font-size: 9px; opacity: 0.7; }}
    
    /* 播放控制 */
    .playback {{ display: flex; gap: 10px; margin-bottom: 12px; align-items: center; }}
    .play-btn {{
        width: 40px; height: 40px; border: none; border-radius: 50%;
        background: linear-gradient(135deg, #4A90D9, #357ABD); color: #fff; cursor: pointer;
        font-size: 16px; display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 12px rgba(74,144,217,0.3); transition: all 0.2s;
    }}
    .play-btn:hover {{ transform: scale(1.05); box-shadow: 0 6px 16px rgba(74,144,217,0.4); }}
    .time-label {{ font-size: 11px; color: #666; font-variant-numeric: tabular-nums; line-height: 1.5; }}
    
    /* 速度控制 */
    .speed-control {{ margin-top: 10px; }}
    .speed-control label {{ font-size: 11px; color: #666; display: flex; justify-content: space-between; margin-bottom: 6px; }}
    .speed-slider {{ width: 100%; accent-color: #4A90D9; height: 4px; }}
    
    /* 信息显示 */
    .info-panel {{
        margin-top: 12px; padding-top: 12px; border-top: 1px solid #eee;
        font-size: 11px; color: #777; line-height: 1.7;
    }}
    .info-row {{ display: flex; justify-content: space-between; }}
    .info-value {{ font-weight: 600; color: #333; }}
    
    /* 帮助提示 */
    .help-tip {{
        position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
        background: rgba(0,0,0,0.7); color: #fff; padding: 8px 18px;
        border-radius: 20px; font-size: 11px; z-index: 100; backdrop-filter: blur(8px);
        transition: opacity 0.3s;
    }}
</style>
</head>
<body>
<div id="viewer"></div>

<!-- 控制面板 -->
<div id="controls">
    <h3>🚀 轨迹可视化 / Trajectory</h3>
    
    <!-- 相机模式 -->
    <div class="mode-select">
        <button class="mode-btn active" id="btn-orbit" onclick="setMode('orbit-start')">
            🔄 绕起点旋转<br><small>Orbit Start</small>
        </button>
        <button class="mode-btn" id="btn-free" onclick="setMode('free')">
            🖱️ 自由旋转<br><small>Free Rotate</small>
        </button>
    </div>
    
    <!-- 播放控制 -->
    <div class="playback">
        <button class="play-btn" id="play-btn" onclick="togglePlay()">▶</button>
        <div>
            <div class="time-label">⏱ 时间: <span id="time-display">0.00</span> / {t_samples[-1]:.2f} s</div>
            <div class="time-label">📊 进度: <span id="progress-display">0</span>%</div>
        </div>
    </div>
    
    <!-- 速度 -->
    <div class="speed-control">
        <label><span>播放速度</span><span id="speed-label">1.0x</span></label>
        <input type="range" class="speed-slider" id="speed-slider"
               min="0.1" max="5" step="0.1" value="1" oninput="setSpeed(this.value)">
    </div>
    
    <!-- 信息 -->
    <div class="info-panel">
        <div class="info-row"><span>轨迹点数:</span><span class="info-value">{len(positions)}</span></div>
        <div class="info-row"><span>持续时间:</span><span class="info-value">{t_samples[-1]:.2f}s</span></div>
        <div class="info-row"><span>当前模式:</span><span class="info-value" id="mode-label">绕起点旋转</span></div>
    </div>
</div>

<!-- 帮助 -->
<div class="help-tip" id="help-tip">🖱️ 拖拽: 旋转 | 滚轮: 缩放 | 双击: 重置视角</div>

<!-- Three.js + OrbitControls (CDN) -->
<script type="importmap">
{{
    "imports": {{
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
    }}
}}
</script>

<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

// ── 数据 ──
const tSamples = {t_json};
const positions = {pos_json};
const obstacles = {obstacles_json};
const startPos = new THREE.Vector3(...{json.dumps(start_pos)});
const orbitRadius = {orbit_radius};
const orbitHeightOffset = {orbit_height_offset};

// ── 状态 ──
let scene, camera, renderer, controls;
let isPlaying = false;
let currentTime = 0;
let playbackSpeed = 1.0;
let currentMode = '{mode}';
let clock = new THREE.Clock();
let orbitAngle = 0;
let robotMesh, pathLine;

// ── 初始化 ──
function init() {{
    const container = document.getElementById('viewer');
    
    // 场景
    scene = new THREE.Scene();
    scene.background = new THREE.Color('{bg_color_hex}');
    
    // 相机
    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(startPos.x + orbitRadius, startPos.y + orbitRadius, startPos.z + orbitHeightOffset);
    camera.lookAt(startPos);
    
    // 渲染器
    renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    
    // 控制器
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.target.copy(startPos);
    controls.enabled = false;  // 默认 orbit 模式
    
    // 光照
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
    dirLight.position.set(20, 30, 20);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    scene.add(dirLight);
    
    const hemiLight = new THREE.HemisphereLight(0xddeeff, 0x0f0e0d, 0.4);
    scene.add(hemiLight);
    
    // 网格
    const gridHelper = new THREE.GridHelper(100, 100, 0xcccccc, 0xeeeeee);
    scene.add(gridHelper);
    
    // 创建物体
    createPathLine();
    createRobot();
    createStartGoalMarkers();
    createObstacles();
    
    // 窗口大小
    window.addEventListener('resize', onWindowResize);
    
    // 双击重置
    renderer.domElement.addEventListener('dblclick', () => {{
        if (currentMode === 'free') resetFreeCamera();
    }});
    
    // 启动
    setMode(currentMode);
    animate();
}}

// ── 轨迹线 ──
function createPathLine() {{
    const points = positions.map(p => new THREE.Vector3(p[0], p[1], p[2]));
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({{
        color: '{path_color_hex}',
        linewidth: 2
    }});
    pathLine = new THREE.Line(geometry, material);
    scene.add(pathLine);
    
    // 轨迹管状（更醒目）
    const curve = new THREE.CatmullRomCurve3(points);
    const tubeGeo = new THREE.TubeGeometry(curve, points.length, 0.08, 8, false);
    const tubeMat = new THREE.MeshLambertMaterial({{ color: '{path_color_hex}' }});
    const tube = new THREE.Mesh(tubeGeo, tubeMat);
    scene.add(tube);
}}

// ── 机器人（运动小球） ──
function createRobot() {{
    const geometry = new THREE.SphereGeometry(0.35, 32, 32);
    const material = new THREE.MeshPhongMaterial({{
        color: 0xFF4444,
        emissive: 0xAA0000,
        emissiveIntensity: 0.3,
        shininess: 80
    }});
    robotMesh = new THREE.Mesh(geometry, material);
    robotMesh.castShadow = true;
    robotMesh.position.copy(startPos);
    scene.add(robotMesh);
    
    // 光晕效果
    const glowGeo = new THREE.SphereGeometry(0.5, 16, 16);
    const glowMat = new THREE.MeshBasicMaterial({{
        color: 0xFF6666,
        transparent: true,
        opacity: 0.25
    }});
    const glow = new THREE.Mesh(glowGeo, glowMat);
    robotMesh.add(glow);
}}

// ── 起点/终点标记 ──
function createStartGoalMarkers() {{
    // 起点: 绿色
    const startGeo = new THREE.SphereGeometry(0.45, 24, 24);
    const startMat = new THREE.MeshPhongMaterial({{ color: 0x00CC00, emissive: 0x004400 }});
    const start = new THREE.Mesh(startGeo, startMat);
    start.position.copy(startPos);
    scene.add(start);
    
    // 终点: 红色
    const endPos = new THREE.Vector3(...positions[positions.length - 1]);
    const endGeo = new THREE.SphereGeometry(0.45, 24, 24);
    const endMat = new THREE.MeshPhongMaterial({{ color: 0xCC0000, emissive: 0x440000 }});
    const end = new THREE.Mesh(endGeo, endMat);
    end.position.copy(endPos);
    scene.add(end);
    
    // 标签
    createLabel('起点', startPos.clone().add(new THREE.Vector3(0, 1, 0)));
    createLabel('终点', endPos.clone().add(new THREE.Vector3(0, 1, 0)));
}}

function createLabel(text, position) {{
    // 使用 sprite 文字标签
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 128;
    canvas.height = 64;
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.roundRect(0, 0, 128, 64, 8);
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 32px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 64, 32);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({{ map: texture }});
    const sprite = new THREE.Sprite(spriteMat);
    sprite.position.copy(position);
    sprite.scale.set(2, 1, 1);
    scene.add(sprite);
}}

// ── 障碍物 ──
function createObstacles() {{
    obstacles.forEach((obs, i) => {{
        const [cx, cy, cz] = obs.center;
        const [sx, sy, sz] = obs.size;
        const color = obs.color || [180, 180, 180];
        const colorHex = '#' + color.map(c => c.toString(16).padStart(2, '0')).join('');
        
        const geo = new THREE.BoxGeometry(sx, sy, sz);
        const mat = new THREE.MeshPhongMaterial({{
            color: new THREE.Color(colorHex),
            transparent: true,
            opacity: 0.7
        }});
        const box = new THREE.Mesh(geo, mat);
        box.position.set(cx, cy, cz);
        box.castShadow = true;
        box.receiveShadow = true;
        scene.add(box);
    }});
}}

// ── 位置插值 ──
function getPositionAtTime(t) {{
    if (t <= tSamples[0]) return new THREE.Vector3(...positions[0]);
    if (t >= tSamples[tSamples.length-1]) return new THREE.Vector3(...positions[positions.length-1]);
    
    // 二分查找
    let lo = 0, hi = tSamples.length - 1;
    while (lo < hi - 1) {{
        const mid = Math.floor((lo + hi) / 2);
        if (tSamples[mid] <= t) lo = mid;
        else hi = mid;
    }}
    
    // 线性插值
    const t0 = tSamples[lo], t1 = tSamples[hi];
    const frac = (t - t0) / (t1 - t0);
    const p0 = positions[lo], p1 = positions[hi];
    
    return new THREE.Vector3(
        p0[0] + frac * (p1[0] - p0[0]),
        p0[1] + frac * (p1[1] - p0[1]),
        p0[2] + frac * (p1[2] - p0[2])
    );
}}

// ── 更新机器人位置 ──
function updateRobot(t) {{
    const pos = getPositionAtTime(t);
    robotMesh.position.copy(pos);
}}

// ── 相机模式 ──
function setMode(newMode) {{
    currentMode = newMode;
    
    document.getElementById('btn-orbit').classList.toggle('active', newMode === 'orbit-start');
    document.getElementById('btn-free').classList.toggle('active', newMode === 'free');
    document.getElementById('mode-label').textContent = 
        newMode === 'orbit-start' ? '绕起点旋转' : '自由旋转';
    
    const help = document.getElementById('help-tip');
    if (newMode === 'orbit-start') {{
        controls.enabled = false;
        help.innerHTML = '🔄 自动绕起点旋转 | 滚轮: 调整距离 | 可拖拽调整角度';
    }} else {{
        controls.enabled = true;
        help.innerHTML = '🖱️ 拖拽: 旋转 | 滚轮: 缩放 | 双击: 重置视角';
    }}
}}

// ── 轨道相机更新 ──
function updateOrbitCamera(dt) {{
    const speed = {orbit_speed};
    orbitAngle += speed * dt;
    
    const camX = startPos.x + orbitRadius * Math.cos(orbitAngle);
    const camY = startPos.y + orbitRadius * Math.sin(orbitAngle);
    const camZ = startPos.z + orbitHeightOffset;
    
    camera.position.set(camX, camY, camZ);
    camera.lookAt(startPos);
}}

// ── 自由模式: 重置相机 ──
function resetFreeCamera() {{
    const lastPos = new THREE.Vector3(...positions[positions.length-1]);
    const center = new THREE.Vector3().addVectors(startPos, lastPos).multiplyScalar(0.5);
    camera.position.set(center.x + orbitRadius, center.y + orbitRadius, center.z + orbitHeightOffset * 0.5);
    controls.target.copy(center);
    controls.update();
}}

// ── 播放控制 ──
function togglePlay() {{
    isPlaying = !isPlaying;
    const btn = document.getElementById('play-btn');
    btn.textContent = isPlaying ? '⏸' : '▶';
    btn.style.background = isPlaying 
        ? 'linear-gradient(135deg, #E74C3C, #C0392B)' 
        : 'linear-gradient(135deg, #4A90D9, #357ABD)';
    
    if (isPlaying && currentTime >= tSamples[tSamples.length-1]) {{
        currentTime = 0;
    }}
}}

function setSpeed(val) {{
    playbackSpeed = parseFloat(val);
    document.getElementById('speed-label').textContent = playbackSpeed.toFixed(1) + 'x';
}}

// ── 窗口大小 ──
function onWindowResize() {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}}

// ── 动画循环 ──
function animate() {{
    requestAnimationFrame(animate);
    
    const dt = clock.getDelta();
    
    if (isPlaying) {{
        currentTime += dt * playbackSpeed;
        if (currentTime > tSamples[tSamples.length-1]) {{
            currentTime = tSamples[tSamples.length-1];
            togglePlay();
        }}
        
        updateRobot(currentTime);
        document.getElementById('time-display').textContent = currentTime.toFixed(2);
        const progress = (currentTime / tSamples[tSamples.length-1]) * 100;
        document.getElementById('progress-display').textContent = Math.round(progress);
    }}
    
    if (currentMode === 'orbit-start') {{
        updateOrbitCamera(dt);
    }} else {{
        controls.update();
    }}
    
    renderer.render(scene, camera);
}}

// ── 启动 ──
window.addEventListener('load', init);
</script>
</body>
</html>'''
    
    return html


def load_trajectory_data(filepath):
    """Load trajectory data from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    if "positions" in data:
        return data
    
    if "t_samples" in data and "positions" not in data:
        raise ValueError("数据格式: 需要 {'t_samples': [...], 'positions': [[x,y,z], ...]}")
    
    return data


def main():
    parser = argparse.ArgumentParser(description="机器人轨迹实时可视化 HTML 生成器")
    parser.add_argument("--data", help="轨迹数据 JSON 文件路径")
    parser.add_argument("--output", default="results/trajectory.html", help="输出 HTML 文件路径")
    parser.add_argument("--title", default="Trajectory Visualization", help="页面标题")
    parser.add_argument("--mode", default="orbit-start", choices=["orbit-start", "free"],
                        help="默认相机模式")
    parser.add_argument("--orbit-axis", default="z", help="旋转轴 (z/x/y)")
    parser.add_argument("--orbit-speed", type=float, default=0.5, help="旋转速度 (rad/s)")
    parser.add_argument("--demo-maze", action="store_true", help="生成迷宫演示轨迹")
    parser.add_argument("--demo-random-boxes", action="store_true", help="生成随机盒演示轨迹")
    parser.add_argument("--demo-uav-village", action="store_true", help="生成 UAV 村庄演示轨迹")
    parser.add_argument("--path-color", default="0,0,255", help="轨迹颜色 R,G,B")
    parser.add_argument("--bg-color", default="245,245,250", help="背景颜色 R,G,B")
    parser.add_argument("--show-obstacles", action="store_true", help="显示障碍物")
    parser.add_argument("--obstacles", help="障碍物 JSON 文件")
    
    args = parser.parse_args()
    
    # Load or generate data
    if args.data:
        data = load_trajectory_data(args.data)
        print(f"  ✅ 加载轨迹数据: {len(data['positions'])} 个点, {data['t_samples'][-1]:.2f}s")
    elif args.demo_maze:
        data = generate_demo_trajectory("maze")
        print(f"  🎮 生成迷宫演示轨迹: {len(data['positions'])} 个点")
    elif args.demo_random_boxes:
        data = generate_demo_trajectory("random_boxes")
        print(f"  🎮 生成随机盒演示轨迹: {len(data['positions'])} 个点")
    elif args.demo_uav_village:
        data = generate_demo_trajectory("uav_village")
        print(f"  🎮 生成 UAV 村庄演示轨迹: {len(data['positions'])} 个点")
    else:
        print("  ❌ 错误: 请指定 --data 或 --demo-* 选项")
        sys.exit(1)
    
    # Parse colors
    path_color = tuple(int(c) for c in args.path_color.split(","))
    bg_color = tuple(int(c) for c in args.bg_color.split(","))
    
    # Load obstacles
    obstacles = None
    if args.obstacles:
        with open(args.obstacles, 'r') as f:
            obstacles = json.load(f)
    elif args.show_obstacles:
        obstacles = [
            {"center": [2, 2, 1], "size": [1, 1, 2], "color": [200, 200, 200]},
            {"center": [5, 3, 1.5], "size": [1.5, 1.5, 3], "color": [180, 180, 180]},
            {"center": [3, 5, 0.5], "size": [2, 1, 1], "color": [160, 160, 160]},
        ]
    
    # Generate HTML
    html = generate_html(
        data=data,
        title=args.title,
        mode=args.mode,
        orbit_axis=args.orbit_axis,
        orbit_speed=args.orbit_speed,
        show_path=True,
        show_obstacles=args.show_obstacles or obstacles is not None,
        obstacles=obstacles,
        path_color=path_color,
        background_color=bg_color
    )
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  ✅ HTML 已生成: {output_path.absolute()}")
    print(f"  📐 模式: {args.mode} | 轨迹点: {len(data['positions'])} | 速度: {args.orbit_speed} rad/s")
    print(f"  💡 双击文件即可在浏览器中打开查看实时轨迹")
    print(f"  🌐 基于 Three.js (CDN) | 支持 orbit-start / free 两种相机模式")


if __name__ == "__main__":
    main()
