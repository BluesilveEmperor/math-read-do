# 实验结果对比表 / Experimental Results Comparison

## 简化参数 / Simplification Parameters

- **Input model / 输入模型**: {{ input_model }}
- **Original faces / 原始面数**: {{ orig_faces }}
- **Target faces / 目标面数**: {{ target_faces }}
- **Actual output faces / 实际输出面数**: {{ out_faces }}

## 多模型对比 / Multi-Model Comparison

| Model / 模型 | Original Verts / 原始顶点 | Original Faces / 原始面 | Simplified Verts / 简化顶点 | Simplified Faces / 简化面 | Time / 时间 | Error / 误差 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
{% for model in models -%}
| {{ model.name }} | {{ model.orig_v }} | {{ model.orig_f }} | {{ model.out_v }} | {{ model.out_f }} | {{ model.time }}s | {{ model.error }} |
{% endfor %}

## 不同简化比对比 / Multi-Ratio Comparison

| Ratio / 比例 | Original Faces / 原始面 | Target / 目标 | Output / 输出 | Hausdorff / Hausdorff | Time / 时间 |
|:---|:---:|:---:|:---:|:---:|:---:|
{% for row in ratios -%}
| {{ row.ratio }}% | {{ row.orig_f }} | {{ row.target }} | {{ row.out_f }} | {{ row.hausdorff }} | {{ row.time }}s |
{% endfor %}

## 与原始 C++ 实现对比 / Comparison with Original C++

| Metric / 指标 | Original C++ | Python (this impl) | Delta / 偏差 |
|:---|:---:|:---:|:---:|
| Output faces / 输出面数 | {{ cpp_faces }} | {{ py_faces }} | {{ faces_delta }} |
| Output verts / 输出顶点 | {{ cpp_verts }} | {{ py_verts }} | {{ verts_delta }} |
| Time / 时间 | {{ cpp_time }}s | {{ py_time }}s | {{ time_delta }} |
