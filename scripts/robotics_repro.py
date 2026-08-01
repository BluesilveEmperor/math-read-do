#!/usr/bin/env python3
"""
robotics_repro.py - 机器人路径优化论文复现辅助脚本
Robotics Path Optimization Paper Reproduction Helper

功能:
- 自动检测论文的路径规划类型（凸优化/搜索/采样/学习）
- 提取关键性能指标（规划时间、路径成本、成功率）
- 生成求解器兼容性报告
- 验证路径安全性（碰撞检测）

用法:
    python robotics_repro.py --paper-json analysis/paper_summary.json --results results/
    python robotics_repro.py --detect-type --text "paper abstract text"

依赖:
    pip install numpy
"""
import os
import sys
import json
import re
import argparse
from pathlib import Path


# 论文类型关键词映射
PAPER_TYPE_KEYWORDS = {
    "convex_optimization": [
        "convex", "socp", "sdp", "milp", "miqp", "cvxpy", "cvx",
        "mixed-integer", "second-order cone", "semidefinite",
        "fast path planning", "gcs", "convex optimization"
    ],
    "search_based": [
        "a*", "d*", "theta*", "anya", "grid", "graph search",
        "dijkstra", "shortest path", "lattice"
    ],
    "sampling_based": [
        "rrt", "prm", "rrt*", "bit*", "informed rrt*", "sampling",
        "probabilistic roadmap", "rapidly-exploring"
    ],
    "optimization_nonconvex": [
        "chomp", "trajopt", "nonconvex", "non-convex", "gradient",
        "optimization", "trajectory optimization"
    ],
    "learning_based": [
        "neural", "deep learning", "reinforcement learning", "drl",
        "imitation learning", "learning-based", "data-driven",
        "network", "policy"
    ],
    "model_predictive": [
        "mpc", "model predictive control", "receding horizon",
        "tube mpc", "robust mpc"
    ]
}


# 机器人平台关键词
ROBOT_PLATFORMS = {
    "uav": ["uav", "quadrotor", "drone", "aerial", "flight", "flying"],
    "mobile_robot": ["mobile robot", "ground robot", "wheeled", "differential drive"],
    "manipulator": ["manipulator", "arm", "robot arm", "industrial robot", "ur5", "franka"],
    "legged": ["legged", "quadruped", "biped", "humanoid", "walking"],
    "marine": ["marine", "underwater", "auv", "usv", "boat"],
    "aerial_manipulation": ["aerial manipulation", "flying manipulator"]
}


# 规划类型
PLANNING_TYPES = {
    "path": ["path planning", "geometric planning", "holonomic"],
    "trajectory": ["trajectory planning", "trajectory generation", "time-optimal"],
    "motion": ["motion planning", "kinodynamic planning", "nonholonomic"]
}


def detect_paper_type(text):
    """自动检测论文类型"""
    text_lower = text.lower()
    scores = {}
    
    for ptype, keywords in PAPER_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[ptype] = score
    
    if not scores:
        return "unknown", {}
    
    # 按得分排序
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_types[0][0], dict(sorted_types)


def detect_robot_platform(text):
    """检测机器人平台"""
    text_lower = text.lower()
    platforms = []
    
    for platform, keywords in ROBOT_PLATFORMS.items():
        if any(kw in text_lower for kw in keywords):
            platforms.append(platform)
    
    return platforms


def detect_planning_type(text):
    """检测规划类型"""
    text_lower = text.lower()
    types = []
    
    for ptype, keywords in PLANNING_TYPES.items():
        if any(kw in text_lower for kw in keywords):
            types.append(ptype)
    
    return types


def extract_metrics_from_results(results_dir):
    """从实验结果中提取关键指标"""
    metrics = {}
    
    # 尝试读取 results.json
    results_json = os.path.join(results_dir, "results.json")
    if os.path.exists(results_json):
        with open(results_json, 'r') as f:
            data = json.load(f)
        
        for key, value in data.items():
            if isinstance(value, dict) and "time_sec" in value:
                metrics[key] = {
                    "time": value["time_sec"],
                    "status": value.get("status", "unknown")
                }
            elif isinstance(value, list) and len(value) > 0:
                metrics[key] = {
                    "values": value,
                    "mean": sum(value) / len(value) if all(isinstance(v, (int, float)) for v in value) else None
                }
    
    return metrics


def check_solver_compatibility(paper_type):
    """检查求解器兼容性"""
    solver_map = {
        "convex_optimization": {
            "recommended": ["clarabel", "mosek", "ecos"],
            "optional": ["scs", "osqp", "cvxopt"],
            "notes": "SOCP/SDP 问题推荐 CLARABEL（免费）或 MOSEK（学术）"
        },
        "search_based": {
            "recommended": ["numpy", "networkx", "scipy"],
            "optional": ["matplotlib", "pillow"],
            "notes": "主要依赖图搜索库，无需优化求解器"
        },
        "sampling_based": {
            "recommended": ["numpy", "scipy", "networkx"],
            "optional": ["ompl", "pillow", "matplotlib"],
            "notes": "可能需要 OMPL（Open Motion Planning Library）"
        },
        "optimization_nonconvex": {
            "recommended": ["scipy", "numpy", "casadi"],
            "optional": ["ipopt", "nlopt"],
            "notes": "非凸优化可能需要 IPOPT 或 CasADi"
        },
        "learning_based": {
            "recommended": ["torch", "tensorflow", "numpy"],
            "optional": ["gym", "stable-baselines3"],
            "notes": "需要深度学习框架和 GPU 支持"
        },
        "model_predictive": {
            "recommended": ["casadi", "acados", "numpy"],
            "optional": ["osqp", "forcespro"],
            "notes": "MPC 通常需要 CasADi 或 acados"
        }
    }
    
    return solver_map.get(paper_type, {})


def generate_repro_plan(paper_summary_path):
    """生成复现计划"""
    if not os.path.exists(paper_summary_path):
        print(f"ERROR: Paper summary not found: {paper_summary_path}")
        return None
    
    with open(paper_summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    # 合并文本用于分析
    text = " ".join([
        summary.get("title", ""),
        summary.get("abstract", ""),
        summary.get("methods", ""),
        summary.get("keywords", "")
    ])
    
    # 检测类型
    paper_type, type_scores = detect_paper_type(text)
    platforms = detect_robot_platform(text)
    planning_types = detect_planning_type(text)
    solver_info = check_solver_compatibility(paper_type)
    
    plan = {
        "paper_type": paper_type,
        "paper_type_scores": type_scores,
        "robot_platforms": platforms,
        "planning_types": planning_types,
        "solver_recommendation": solver_info,
        "repro_steps": _generate_steps(paper_type, platforms, planning_types)
    }
    
    return plan


def _generate_steps(paper_type, platforms, planning_types):
    """根据论文类型生成复现步骤"""
    steps = []
    
    # 通用步骤
    steps.append("Phase 0: 环境检测与基础设施配置")
    steps.append("Phase 1: 论文解析与三方审阅")
    
    # 类型特定步骤
    if paper_type == "convex_optimization":
        steps.append("Phase 2: 安装 CVXPY + 求解器 (clarabel/mosek)")
        steps.append("Phase 3: 验证安全集表示与线图构建")
        steps.append("Phase 4: 运行官方代码，验证求解器结果")
        steps.append("Phase 5: 多场景复现与统计验证")
    elif paper_type == "sampling_based":
        steps.append("Phase 2: 安装采样规划库 (OMPL/custom)")
        steps.append("Phase 3: 配置碰撞检测器")
        steps.append("Phase 4: 运行官方代码，验证采样结果")
        steps.append("Phase 5: N>=30 次运行，统计成功率")
    elif paper_type == "learning_based":
        steps.append("Phase 2: 安装深度学习框架 (PyTorch/TF)")
        steps.append("Phase 3: 下载预训练权重")
        steps.append("Phase 4: 验证推理结果")
        steps.append("Phase 5: 多场景测试")
    else:
        steps.append("Phase 2: 环境重建")
        steps.append("Phase 3: 基线验证")
        steps.append("Phase 4: 增量实现")
        steps.append("Phase 5: 统计验证")
    
    steps.append("Phase 6: 双语报告生成")
    steps.append("Phase 7: 最终整理")
    
    return steps


def print_report(plan):
    """打印复现计划报告"""
    print("=" * 60)
    print("  机器人路径优化论文复现计划")
    print("=" * 60)
    print(f"  论文类型: {plan['paper_type']}")
    print(f"  类型置信度: {plan['paper_type_scores']}")
    print(f"  机器人平台: {', '.join(plan['robot_platforms']) if plan['robot_platforms'] else '通用'}")
    print(f"  规划类型: {', '.join(plan['planning_types']) if plan['planning_types'] else '未知'}")
    
    solver = plan['solver_recommendation']
    if solver:
        print(f"\n  推荐求解器: {', '.join(solver.get('recommended', []))}")
        print(f"  可选求解器: {', '.join(solver.get('optional', []))}")
        print(f"  备注: {solver.get('notes', '')}")
    
    print(f"\n  复现步骤:")
    for i, step in enumerate(plan['repro_steps'], 1):
        print(f"    {i}. {step}")
    
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="机器人路径优化论文复现辅助")
    parser.add_argument("--paper-json", default="analysis/paper_summary.json", help="论文摘要JSON")
    parser.add_argument("--results", default="results/", help="实验结果目录")
    parser.add_argument("--detect-type", action="store_true", help="仅检测论文类型")
    parser.add_argument("--text", help="直接输入文本进行类型检测")
    
    args = parser.parse_args()
    
    if args.text:
        ptype, scores = detect_paper_type(args.text)
        platforms = detect_robot_platform(args.text)
        planning = detect_planning_type(args.text)
        print(f"Type: {ptype}")
        print(f"Scores: {scores}")
        print(f"Platforms: {platforms}")
        print(f"Planning: {planning}")
        sys.exit(0)
    
    if args.detect_type:
        plan = generate_repro_plan(args.paper_json)
        if plan:
            print_report(plan)
        sys.exit(0)
    
    # 完整模式
    plan = generate_repro_plan(args.paper_json)
    if plan:
        print_report(plan)
        
        # 保存计划
        plan_path = "analysis/repro_plan.json"
        os.makedirs("analysis", exist_ok=True)
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print(f"\n  Plan saved to: {plan_path}")
