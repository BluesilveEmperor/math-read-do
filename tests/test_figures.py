#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figuregen 单测：状态机 / 门禁 / manifest 校验 / 路线图补充模式。

运行：python -m unittest tests.test_figures -v
（渲染类验收用例 T7~T13 依赖 Node，见 test_figures_integration.py 的说明：
  这里只测纯 Python 逻辑，保证无 Node 也能回归门禁与状态机。）
"""

import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from figuregen import gates as G          # noqa: E402
from figuregen import manifest as MF      # noqa: E402
from figuregen import presets as P        # noqa: E402
from figuregen import state as ST         # noqa: E402


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8"))
    return path


class TestStageMachine(unittest.TestCase):
    def test_first_render_allows_any_stage(self):
        stage, note = ST.resolve_stage("final", None, "sha")
        self.assertEqual(stage, "final")
        self.assertIsNone(note)

    def test_spec_change_downgrades_to_draft(self):
        stage, note = ST.resolve_stage("final", {"stage": "final", "spec_sha256": "old"}, "new")
        self.assertEqual(stage, "draft")
        self.assertIn("draft", note)

    def test_unchanged_spec_keeps_stage(self):
        stage, note = ST.resolve_stage("final", {"stage": "confirmed", "spec_sha256": "same"}, "same")
        self.assertEqual(stage, "final")
        self.assertIsNone(note)

    def test_only_ascending(self):
        stage, _ = ST.resolve_stage("draft", {"stage": "final", "spec_sha256": "same"}, "same")
        self.assertEqual(stage, "final")

    def test_draft_title_suffix(self):
        self.assertIn("（初稿）", ST.title_with_stage("技术路线图", "draft"))
        self.assertNotIn("（初稿）", ST.title_with_stage("技术路线图", "final"))
        self.assertEqual(ST.title_with_stage("实验流程图（预计流程）", "draft"), "实验流程图（预计流程）")


class TestGates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_gate_none_always_ok(self):
        for stage in P.STAGES:
            self.assertTrue(G.gate_none(stage, self.tmp).ok)

    def test_soft_gate_blocks_final_without_evidence(self):
        res = G.gate_soft_code_verified("final", self.tmp)
        self.assertTrue(res.ok)                     # soft 门禁不失败，只降级
        self.assertEqual(res.stage_cap, "confirmed")

    def test_soft_gate_passes_final_with_evidence(self):
        write_json(os.path.join(self.tmp, "implementation", "delta_report.json"), {"ok": True})
        res = G.gate_soft_code_verified("final", self.tmp)
        self.assertTrue(res.ok)
        self.assertIsNone(res.stage_cap)

    def test_soft_gate_ignores_non_final(self):
        res = G.gate_soft_code_verified("draft", self.tmp)
        self.assertIsNone(res.stage_cap)

    def _counts(self):
        return {
            "initial_n": 120,
            "excluded": [{"n": 8, "reason": "重复发表"}, {"n": 12, "reason": "数据缺失"}],
            "included_n": 100,
            "groups": [{"name": "实验组", "n": 50, "allocation": "随机"},
                       {"name": "对照组", "n": 50, "allocation": "随机"}],
            "attrition": [{"n": 5, "reason": "失访", "type": "lost"}],
            "analyzed_n": 95,
            "metrics": ["准确率"],
            "raw_metrics_sha256": "a" * 64,
        }

    def test_hard_gate_requires_data_file(self):
        res = G.gate_requires_experiment_data("final", self.tmp)
        self.assertFalse(res.ok)
        self.assertIn("experiment_counts.json", res.blocked_reason)

    def test_hard_gate_passes_with_complete_data(self):
        write_json(os.path.join(self.tmp, G.EXPERIMENT_DATA_REL), self._counts())
        res = G.gate_requires_experiment_data("final", self.tmp)
        self.assertTrue(res.ok, res.blocked_reason)

    def test_hard_gate_ignores_draft(self):
        res = G.gate_requires_experiment_data("draft", self.tmp)
        self.assertTrue(res.ok)
        self.assertEqual(res.label_suffix, "（预计流程）")

    def test_hard_gate_missing_fields(self):
        c = self._counts()
        del c["analyzed_n"]
        write_json(os.path.join(self.tmp, G.EXPERIMENT_DATA_REL), c)
        res = G.gate_requires_experiment_data("final", self.tmp)
        self.assertFalse(res.ok)
        self.assertIn("analyzed_n", res.blocked_reason)

    def test_hard_gate_missing_metrics_sha(self):
        c = self._counts()
        del c["raw_metrics_sha256"]
        write_json(os.path.join(self.tmp, G.EXPERIMENT_DATA_REL), c)
        self.assertFalse(G.gate_requires_experiment_data("final", self.tmp).ok)

    def test_hard_gate_group_sum_overflow(self):
        c = self._counts()
        c["groups"][0]["n"] = 80          # 80+50=130 > included_n=100
        write_json(os.path.join(self.tmp, G.EXPERIMENT_DATA_REL), c)
        res = G.gate_requires_experiment_data("final", self.tmp)
        self.assertFalse(res.ok)
        self.assertIn("自相矛盾", res.blocked_reason)

    def test_hard_gate_prisma_needs_reasons(self):
        c = self._counts()
        c["flow_diagram_kind"] = "PRISMA"
        c["excluded"] = [{"n": 8}]        # 缺 reason
        write_json(os.path.join(self.tmp, G.EXPERIMENT_DATA_REL), c)
        self.assertFalse(G.gate_requires_experiment_data("final", self.tmp).ok)


class TestManifest(unittest.TestCase):
    def _valid(self):
        return {
            "schema_version": P.MANIFEST_SCHEMA_VERSION,
            "paper": "示例论文",
            "engine": {"internal": "figuregen", "version": "0.1.0",
                       "upstream_commit": P.ENGINE_UPSTREAM_COMMIT},
            "global_motion": "off",
            "figures": [{
                "id": "fig-framework", "type": "framework", "stage": "final",
                "gate": "none", "spec": "figures/specs/framework.json",
                "output_html": "figures/out/framework.html", "quality": "showcase",
                "spec_sha256": "a" * 64,
                "sha256": {"spec": "b" * 64, "html": "c" * 64},
                "checks": {"passed": 11, "total": 11, "errors": 0, "warnings": 0},
            }],
        }

    def test_valid_manifest_passes(self):
        self.assertEqual(MF.validate(self._valid()), [])

    def test_error_check_rejected(self):
        m = self._valid()
        m["figures"][0]["checks"]["errors"] = 2
        errs = MF.validate(m)
        self.assertTrue(any("error" in e for e in errs))

    def test_bad_type_rejected(self):
        m = self._valid()
        m["figures"][0]["type"] = "未知类型"
        self.assertTrue(MF.validate(m))

    def test_missing_receipt_rejected(self):
        m = self._valid()
        del m["figures"][0]["sha256"]["html"]
        self.assertTrue(MF.validate(m))

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            m = self._valid()
            MF.save(d, m)
            back = MF.load(d)
            self.assertEqual(back["figures"][0]["id"], "fig-framework")


class TestSupplementTopology(unittest.TestCase):
    """路线图补充模式的拓扑规则（方案 §7）——与 figures.py 内联校验同逻辑。"""

    @staticmethod
    def check(old, new):
        problems = []
        old_ids = [m["id"] for m in old.get("modules") or []]
        new_ids = [m["id"] for m in new.get("modules") or []]
        removed = [i for i in old_ids if i not in new_ids]
        if removed:
            problems.append("删除了既有节点：%s" % "、".join(removed))

        def pairs(spec):
            return set((c["from"], c["to"]) for c in (spec.get("connections") or []))

        lost = pairs(old) - pairs(new)
        if lost:
            problems.append("删除/改向了既有连线：%s" % "、".join("%s→%s" % p for p in sorted(lost)))
        for c in (new.get("connections") or []):
            if (c.get("from"), c.get("to")) not in pairs(old) and not (c.get("label") or "").strip():
                problems.append("新增连线 %s→%s 缺少 label" % (c["from"], c["to"]))
        return problems

    def test_append_allowed(self):
        old = {"modules": [{"id": "a"}, {"id": "b"}],
               "connections": [{"from": "a", "to": "b"}]}
        new = {"modules": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
               "connections": [{"from": "a", "to": "b"},
                               {"from": "b", "to": "c", "label": "复现结论"}]}
        self.assertEqual(self.check(old, new), [])

    def test_delete_node_rejected(self):
        old = {"modules": [{"id": "a"}, {"id": "b"}], "connections": []}
        new = {"modules": [{"id": "a"}], "connections": []}
        self.assertTrue(self.check(old, new))

    def test_drop_connection_rejected(self):
        old = {"modules": [{"id": "a"}, {"id": "b"}],
               "connections": [{"from": "a", "to": "b"}]}
        new = {"modules": [{"id": "a"}, {"id": "b"}], "connections": []}
        self.assertTrue(self.check(old, new))

    def test_new_edge_without_label_rejected(self):
        old = {"modules": [{"id": "a"}], "connections": []}
        new = {"modules": [{"id": "a"}, {"id": "c"}],
               "connections": [{"from": "a", "to": "c"}]}
        self.assertTrue(self.check(old, new))


class TestTemplates(unittest.TestCase):
    """六类骨架必须齐全、可解析，且与内核的类型词表一致。"""

    def test_six_skeletons_exist_and_parse(self):
        tdir = os.path.join(ROOT, "scripts", "figuregen", "templates")
        for t in P.DIAGRAM_TYPES:
            p = os.path.join(tdir, t + ".json")
            self.assertTrue(os.path.exists(p), "缺少骨架：%s" % p)
            spec = json.loads(open(p, "rb").read().decode("utf-8-sig"))
            self.assertEqual(spec["schema_version"], P.SCHEMA_VERSION)
            self.assertEqual(spec["diagram_type"], t)
            self.assertGreaterEqual(len(spec["modules"]), 1)
            self.assertTrue(spec["meta"]["title"])
            for m in spec["modules"]:
                self.assertGreaterEqual(m["size"][0], 24)
                self.assertGreaterEqual(m["size"][1], 18)

    def test_skeleton_labels_are_chinese(self):
        """zh-CN 图要求标签含中文（内核检查 11 text-language）。"""
        import re
        tdir = os.path.join(ROOT, "scripts", "figuregen", "templates")
        for t in P.DIAGRAM_TYPES:
            spec = json.loads(open(os.path.join(tdir, t + ".json"), "rb").read().decode("utf-8-sig"))
            texts = [spec["meta"]["title"]] + [m["label"] for m in spec["modules"]]
            for s in texts:
                self.assertRegex(s, re.compile(r"[\u2e80-\u9fff]"), "%s：%r 缺中文" % (t, s))


if __name__ == "__main__":
    unittest.main()
