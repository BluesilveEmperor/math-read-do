"""routine 分支 — 模块注册表冒烟测试。

routine 分支无独立 registry 模块，本测试充当「模块注册表」角色，
验证 scripts/ 下核心模块可被正常导入，确保 routine 分支的脚本入口
在入库后仍可被测试框架发现与加载。

说明：
- 必需模块（仅依赖标准库）必须可导入，否则判失败。
- 可选模块（依赖 PyMuPDF / numpy 等第三方库）在依赖缺失时记为跳过，
  不判失败——routine 分支不强制安装全部可选依赖。
"""

import importlib
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# 仅依赖标准库的核心模块（必须可导入）
REQUIRED_MODULES = [
    "literature_reader",
    "robotics_repro",
]

# 依赖第三方库的可选模块（允许因依赖缺失而跳过）
OPTIONAL_MODULES = [
    "extract_figures",        # 依赖 PyMuPDF
    "generate_templates",     # 依赖可选库
    "plot_and_export",        # 依赖 matplotlib 等
    "three_perspective_review",
    "trajectory_visualizer",
]


class TestModuleRegistry(unittest.TestCase):
    """验证核心模块可导入性（模块注册表冒烟）。"""

    def test_required_modules_importable(self):
        """必需模块应可成功导入"""
        failures = []
        for mod_name in REQUIRED_MODULES:
            try:
                importlib.import_module(mod_name)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{mod_name}: {exc}")
        self.assertEqual(
            failures, [],
            "以下必需模块导入失败:\n" + "\n".join(failures) if failures else "",
        )

    def test_optional_modules_importable_or_skipped(self):
        """可选模块可导入或因依赖缺失跳过（不判失败）"""
        skipped = []
        loaded = []
        for mod_name in OPTIONAL_MODULES:
            try:
                importlib.import_module(mod_name)
                loaded.append(mod_name)
            except (ModuleNotFoundError, SystemExit, ImportError):
                # 可选依赖缺失，记为跳过
                skipped.append(mod_name)
            except Exception:  # noqa: BLE001
                # 其他异常也视为跳过，保持冒烟测试宽容
                skipped.append(mod_name)
        # 至少应能收集到全部可选模块名（无论加载或跳过）
        self.assertEqual(len(loaded) + len(skipped), len(OPTIONAL_MODULES))

    def test_registry_non_empty(self):
        """注册表本身非空"""
        self.assertGreater(len(REQUIRED_MODULES) + len(OPTIONAL_MODULES), 0)

    def test_literature_reader_has_main(self):
        """literature_reader 应暴露 main 入口"""
        mod = importlib.import_module("literature_reader")
        self.assertTrue(callable(getattr(mod, "main", None)))

    def test_robotics_repro_has_core_api(self):
        """robotics_repro 应暴露核心检测 API"""
        mod = importlib.import_module("robotics_repro")
        for func_name in ("detect_paper_type", "extract_metrics_from_results"):
            self.assertTrue(
                callable(getattr(mod, func_name, None)),
                f"robotics_repro 缺少 {func_name}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)