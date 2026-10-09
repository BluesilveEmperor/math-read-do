"""评测框架包：统一评测集 + 评分器 + 指标采集。

四分支（main / routine / financial / obj）共享此框架，避免评测逻辑漂移。
入口：
    - 评分器：``python -m _shared.eval.grader --branch obj``
    - 指标采集：``python -m _shared.eval.metrics_collector --branch obj``
"""