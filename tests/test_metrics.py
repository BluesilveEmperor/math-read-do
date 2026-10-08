"""routine 分支 — 指标提取测试。

测试 robotics_repro.py 的论文类型检测、平台检测、规划类型检测
与实验结果指标提取功能。
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# 添加项目根目录与 scripts 到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from robotics_repro import (  # noqa: E402
    detect_paper_type,
    detect_robot_platform,
    detect_planning_type,
    extract_metrics_from_results,
    check_solver_compatibility,
)


class TestDetectPaperType(unittest.TestCase):
    """测试论文类型自动检测。"""

    def test_detect_convex_optimization(self):
        """含 cvxpy 关键词 → convex_optimization"""
        text = "We use cvxpy to solve the convex optimization problem."
        ptype, scores = detect_paper_type(text)
        self.assertEqual(ptype, "convex_optimization")
        self.assertGreater(scores["convex_optimization"], 0)

    def test_detect_mpc(self):
        """含 MPC 关键词 → model_predictive"""
        text = "This paper proposes a model predictive control (MPC) approach."
        ptype, scores = detect_paper_type(text)
        self.assertEqual(ptype, "model_predictive")

    def test_detect_unknown(self):
        """无匹配关键词 → unknown"""
        text = "A generic paper about cooking recipes."
        ptype, scores = detect_paper_type(text)
        self.assertEqual(ptype, "unknown")
        self.assertEqual(scores, {})

    def test_return_type_is_tuple(self):
        """返回值应为 (str, dict) 二元组"""
        ptype, scores = detect_paper_type("rrt star sampling")
        self.assertIsInstance(ptype, str)
        self.assertIsInstance(scores, dict)


class TestDetectRobotPlatform(unittest.TestCase):
    """测试机器人平台检测。"""

    def test_detect_uav(self):
        """含 drone 关键词 → ['uav']"""
        platforms = detect_robot_platform("We fly a drone in the field.")
        self.assertIn("uav", platforms)

    def test_detect_manipulator(self):
        """含 robot arm 关键词 → ['manipulator']"""
        platforms = detect_robot_platform("A 6-DOF robot arm is used.")
        self.assertIn("manipulator", platforms)

    def test_detect_empty(self):
        """无匹配 → 空列表"""
        platforms = detect_robot_platform("No robot here, just math.")
        self.assertEqual(platforms, [])

    def test_return_type_is_list(self):
        """返回值应为列表"""
        platforms = detect_robot_platform("legged quadruped robot")
        self.assertIsInstance(platforms, list)


class TestDetectPlanningType(unittest.TestCase):
    """测试规划类型检测。"""

    def test_detect_trajectory(self):
        """含 trajectory planning → ['trajectory']"""
        types = detect_planning_type("We study trajectory planning for arms.")
        self.assertIn("trajectory", types)

    def test_detect_empty(self):
        """无匹配 → 空列表"""
        types = detect_planning_type("Just a paper about probability.")
        self.assertEqual(types, [])


class TestExtractMetrics(unittest.TestCase):
    """测试实验结果指标提取。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_extract_time_sec(self):
        """含 time_sec 字段 → 提取 time 与 status"""
        data = {
            "exp1": {"time_sec": 12.5, "status": "success"},
            "exp2": {"time_sec": 8.0},
        }
        with open(os.path.join(self.tmpdir, "results.json"), "w") as f:
            json.dump(data, f)
        metrics = extract_metrics_from_results(self.tmpdir)
        self.assertIn("exp1", metrics)
        self.assertEqual(metrics["exp1"]["time"], 12.5)
        self.assertEqual(metrics["exp1"]["status"], "success")
        self.assertEqual(metrics["exp2"]["status"], "unknown")

    def test_extract_list_metric(self):
        """列表型指标 → 计算 mean"""
        data = {"costs": [1.0, 2.0, 3.0]}
        with open(os.path.join(self.tmpdir, "results.json"), "w") as f:
            json.dump(data, f)
        metrics = extract_metrics_from_results(self.tmpdir)
        self.assertIn("costs", metrics)
        self.assertAlmostEqual(metrics["costs"]["mean"], 2.0)

    def test_no_results_json(self):
        """目录无 results.json → 返回空 dict"""
        metrics = extract_metrics_from_results(self.tmpdir)
        self.assertEqual(metrics, {})

    def test_empty_dict_values(self):
        """空 dict 值不被提取"""
        data = {"exp1": {}}
        with open(os.path.join(self.tmpdir, "results.json"), "w") as f:
            json.dump(data, f)
        metrics = extract_metrics_from_results(self.tmpdir)
        self.assertNotIn("exp1", metrics)


class TestSolverCompatibility(unittest.TestCase):
    """测试求解器兼容性检查。"""

    def test_known_type_returns_result(self):
        """已知论文类型 → 返回兼容性结果"""
        result = check_solver_compatibility("convex_optimization")
        self.assertIsNotNone(result)

    def test_return_type(self):
        """返回值类型检查"""
        result = check_solver_compatibility("model_predictive")
        # check_solver_compatibility 返回 dict 或 list，均非 None
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)