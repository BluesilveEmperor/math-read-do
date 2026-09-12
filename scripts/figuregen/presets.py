#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figuregen · 枚举与默认值

与内核（scripts/figuregen/engine）保持一致的事实清单：
- 六类图          : framework / route / model / system / structure / experiment
- 十种视觉预设    : 素白 paper（默认推荐）/ 深色 paper-dark / 制图线稿 blueprint-print /
                    新粗野 brutalism / 趣味插画 playful / 新拟态 neumorphism /
                    孟菲斯 memphis / 玻璃拟态 glass / 包豪斯 bauhaus / 苹果风 apple
- 数据流动形式    : off（静止）/ hover（悬停）/ flow（流动）/ tour（巡演）
- 文字语言        : zh-CN / en
- 排版规格        : single / double
- 输出格式        : html（默认）/ pdf / eps
- 定稿阶段        : draft / confirmed / final
"""

SCHEMA_VERSION = 1
MANIFEST_SCHEMA_VERSION = "1.0"
ENGINE_VERSION = "0.1.0"
ENGINE_UPSTREAM_COMMIT = "3d092689e12f5e630ada0d31550a53436875b6b7"

DIAGRAM_TYPES = ["framework", "route", "model", "system", "structure", "experiment"]

DIAGRAM_TYPES_CN = {
    "framework": "研究框架图",
    "route": "技术路线图",
    "model": "方法/模型架构图",
    "system": "系统架构图",
    "structure": "论文结构图",
    "experiment": "实验流程图",
}

VISUAL_PRESETS = {
    "paper": "素白（默认推荐，投稿印刷友好）",
    "paper-dark": "深色",
    "blueprint-print": "制图线稿",
    "brutalism": "新粗野",
    "playful": "趣味插画",
    "neumorphism": "新拟态",
    "memphis": "孟菲斯",
    "glass": "玻璃拟态",
    "bauhaus": "包豪斯",
    "apple": "苹果风",
}
DEFAULT_PRESET = "paper"

MOTIONS = {"off": "静止", "hover": "悬停", "flow": "流动", "tour": "巡演"}
LANGS = {"zh-CN": "中文（强制中文优先检查）", "en": "英文"}
COLUMNS = {"single": "单栏（默认）", "double": "双栏"}
FORMATS = {
    "html": "HTML（默认；自包含，字体子集已内嵌）",
    "pdf": "PDF（内核尚未实现，见已知限制）",
    "eps": "EPS（内核尚未实现，见已知限制）",
}
STAGES = ("draft", "confirmed", "final")

# 每类图的定稿门禁（方案 §4.3）
GATES = {
    "framework": "none",
    "structure": "none",
    "route": "none",
    "model": "soft_code_verified",
    "system": "soft_code_verified",
    "experiment": "requires_experiment_data",
}

# §2.4 出图前必问清单（缺任一项且用户未弃权 → exit 2）
ASK_ITEMS = ("preset", "motion", "lang", "column", "format", "stage")
ASK_ITEM_CN = {
    "preset": "主题（视觉预设）",
    "motion": "数据流动形式（静止/悬停/流动/巡演）",
    "lang": "文字语言（zh-CN / en）",
    "column": "排版规格（单栏 / 双栏）",
    "format": "输出格式（HTML / PDF / EPS）",
    "stage": "定稿阶段（draft / confirmed / final）",
}

# 用户弃权后的回落默认（方案 §2.4 问答协议第 ③ 条）
DECLINE_FALLBACK = {
    "preset": "paper",
    "motion": "off",
    "lang": "zh-CN",
    "column": "single",
    "format": "html",
}

# 交付说明里要写明的回落说明（不允许静默采用默认）
DECLINE_NOTE = {
    "preset": "主题未指定，按素白（paper）交付",
    "motion": "数据流动形式未指定，按静止（off）交付；动效不进打印产物",
    "lang": "文字语言未指定，按中文（zh-CN）交付",
    "column": "排版规格未指定，按单栏交付",
    "format": "输出格式未指定，按 HTML 交付",
}


def declined_notes(declined):
    """返回「未指定项按默认交付」的说明列表。"""
    out = []
    for k in declined:
        if k in DECLINE_NOTE:
            out.append("%s：%s" % (ASK_ITEM_CN.get(k, k), DECLINE_NOTE[k]))
    return out
