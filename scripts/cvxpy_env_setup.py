#!/usr/bin/env python3
"""
cvxpy_env_setup.py - CVXPY 凸优化论文环境重建脚本
专为使用 CVXPY/凸优化建模的论文（如 FastPathPlanning）设计

用法:
    python cvxpy_env_setup.py --solver clarabel --paper-json analysis/paper_summary.json

依赖:
    pip install cvxpy networkx scipy clarabel numpy matplotlib
"""
import os
import sys
import json
import subprocess
import argparse
from pathlib import Path


SOLVER_COMPATIBILITY = {
    "clarabel": {"pip": "clarabel", "min_version": "0.6", "free": True, "license": "Apache-2.0"},
    "mosek": {"pip": "mosek", "min_version": "10.0", "free": False, "license": "Commercial/Academic"},
    "gurobi": {"pip": "gurobipy", "min_version": "10.0", "free": False, "license": "Commercial/Academic"},
    "ecos": {"pip": "ecos", "min_version": "2.0", "free": True, "license": "GPL-3"},
    "scs": {"pip": "scs", "min_version": "3.0", "free": True, "license": "MIT"},
    "osqp": {"pip": "osqp", "min_version": "0.6", "free": True, "license": "Apache-2.0"},
    "cvxopt": {"pip": "cvxopt", "min_version": "1.3", "free": True, "license": "GPL-3"},
}

CVXPY_CONSTRAINT_TYPES = [
    "SOC",    # 二阶锥约束 (Second-Order Cone)
    "SDP",    # 半正定约束 (Semidefinite Programming)
    "EXP",    # 指数锥约束 (Exponential Cone)
    "POW",    # 幂锥约束 (Power Cone)
    "QP",     # 二次规划 (Quadratic Programming)
    "LP",     # 线性规划 (Linear Programming)
    "MILP",   # 混合整数线性规划
    "MIQP",   # 混合整数二次规划
]


def check_cvxpy_installation():
    """检查 CVXPY 及其求解器安装状态"""
    results = {"cvxpy": None, "solvers": {}, "available": []}
    
    try:
        import cvxpy
        results["cvxpy"] = cvxpy.__version__
    except ImportError:
        results["cvxpy"] = None
        return results
    
    for solver_name, info in SOLVER_COMPATIBILITY.items():
        try:
            solver_module = __import__(info["pip"].replace("-", "_"))
            version = getattr(solver_module, "__version__", "unknown")
            results["solvers"][solver_name] = {"installed": True, "version": version}
            
            # 检查是否被 CVXPY 识别
            if solver_name in cvxpy.installed_solvers():
                results["available"].append(solver_name)
        except ImportError:
            results["solvers"][solver_name] = {"installed": False}
    
    return results


def setup_cvxpy_env(solver="clarabel", env_name="cvxpy-env"):
    """创建并配置 CVXPY 环境"""
    
    print("=" * 60)
    print("  CVXPY 环境配置")
    print("=" * 60)
    
    # 检查当前状态
    status = check_cvxpy_installation()
    
    if status["cvxpy"]:
        print(f"  ✅ CVXPY {status['cvxpy']} 已安装")
    else:
        print("  ❌ CVXPY 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cvxpy>=1.3"])
        print("  ✅ CVXPY 安装完成")
    
    # 安装求解器
    if solver not in status.get("available", []):
        solver_info = SOLVER_COMPATIBILITY.get(solver)
        if solver_info:
            print(f"  📦 安装求解器 {solver} ({solver_info['pip']})...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", solver_info["pip"]])
                print(f"  ✅ {solver} 安装完成")
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️ {solver} 安装失败: {e}")
                print("     将使用默认求解器")
    
    # 输出最终状态
    final_status = check_cvxpy_installation()
    print("\n" + "=" * 60)
    print("  最终状态")
    print("=" * 60)
    print(f"  CVXPY 版本: {final_status['cvxpy']}")
    print(f"  可用求解器: {', '.join(final_status['available']) if final_status['available'] else '无'}")
    
    return final_status


def analyze_problem_structure(json_path):
    """分析论文中的优化问题结构"""
    if not os.path.exists(json_path):
        print(f"⚠️ 论文摘要文件不存在: {json_path}")
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    # 检测问题类型
    problem_types = []
    if "optimization" in summary.get("keywords", []) or "convex" in summary.get("keywords", []):
        problem_types.append("convex_optimization")
    if "path_planning" in summary.get("keywords", []) or "trajectory" in summary.get("keywords", []):
        problem_types.append("path_planning")
    if "robotics" in summary.get("keywords", []) or "uav" in summary.get("keywords", []):
        problem_types.append("robotics")
    
    # 检测约束类型
    constraints = []
    text = summary.get("full_text", "") + summary.get("methods", "")
    if "SOCP" in text or "second-order" in text.lower():
        constraints.append("SOCP")
    if "SDP" in text or "semidefinite" in text.lower():
        constraints.append("SDP")
    if "MIQP" in text or "mixed-integer" in text.lower():
        constraints.append("MIQP")
    
    analysis = {
        "problem_types": problem_types,
        "constraint_types": constraints,
        "recommended_solver": _recommend_solver(constraints),
        "deterministic": True,
    }
    
    print("\n" + "=" * 60)
    print("  论文优化问题分析")
    print("=" * 60)
    print(f"  问题类型: {', '.join(problem_types)}")
    print(f"  约束类型: {', '.join(constraints) if constraints else '通用'}")
    print(f"  推荐求解器: {analysis['recommended_solver']}")
    
    return analysis


def _recommend_solver(constraints):
    """根据约束类型推荐求解器"""
    if "MIQP" in constraints or "MILP" in constraints:
        return "gurobi"  # 或 mosek
    if "SDP" in constraints:
        return "mosek"  # 或 clarabel
    if "SOCP" in constraints:
        return "clarabel"  # 或 mosek, ecos
    return "clarabel"


def generate_env_lock(output_dir):
    """生成环境锁定文件"""
    os.makedirs(output_dir, exist_ok=True)
    lock_file = os.path.join(output_dir, "requirements-cvxpy.txt")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True, text=True
        )
        with open(lock_file, 'w') as f:
            f.write(result.stdout)
        print(f"  ✅ 环境锁定文件: {lock_file}")
    except Exception as e:
        print(f"  ⚠️ 生成锁定文件失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CVXPY 环境配置脚本")
    parser.add_argument("--solver", default="clarabel", help="求解器名称")
    parser.add_argument("--paper-json", default="analysis/paper_summary.json", help="论文摘要JSON路径")
    parser.add_argument("--output-dir", default="env", help="输出目录")
    parser.add_argument("--analyze-only", action="store_true", help="仅分析不安装")
    
    args = parser.parse_args()
    
    if args.analyze_only:
        analyze_problem_structure(args.paper_json)
    else:
        setup_cvxpy_env(args.solver)
        analyze_problem_structure(args.paper_json)
        generate_env_lock(args.output_dir)
