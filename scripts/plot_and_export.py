#!/usr/bin/env python3
"""
plot_and_export.py - 通用图表生成与代码导出工具
Generic figure generation with self-contained code export.

用法 / Usage:
    python plot_and_export.py --data results/raw_metrics.csv --config config.yaml --output results/figures/

此文件可作为图表生成脚本的基类或直接使用的轻量工具。
This file serves as a base class or lightweight utility for figure generation.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def export_plot_script(script_path, plot_func_source, metadata):
    """
    导出可独立运行的图表生成脚本 / Export self-contained plot script.

    Parameters
    ----------
    script_path : str
        输出脚本路径 / Output script path
    plot_func_source : str
        绘图函数源码 / Source code of the plotting function
    metadata : dict
        元信息，包含论文引用/数据来源等 / Metadata including paper ref, data source
    """
    header = f'''#!/usr/bin/env python3
"""
{metadata.get("title_en", "Figure")}
{metadata.get("title_zh", "图表")}

Paper / 论文: {metadata.get("paper_title", "")}
Figure / 图号: {metadata.get("figure_number", "")}
Data source / 数据来源: {metadata.get("data_source", "")}

This script is self-contained. Run it directly to reproduce the figure:
此脚本自包含，直接运行即可复现图表:
    python {os.path.basename(script_path)}
"""

import matplotlib
matplotlib.use("Agg")  # headless backend / 无头后端
import matplotlib.pyplot as plt
import numpy as np

# === Config / 配置 ===
OUTPUT_FILE = "{metadata.get("output_file", "figure.png")}"
RANDOM_SEED = {metadata.get("random_seed", 42)}
np.random.seed(RANDOM_SEED)

'''
    body = f'''
# === Data / 数据 ===
# 数据来源 / Data source: {metadata.get("data_source", "")}
{plot_func_source}

# === Execute / 执行 ===
if __name__ == "__main__":
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    plot(ax)
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
    print(f"Figure saved to {{OUTPUT_FILE}} / 图表已保存: {{OUTPUT_FILE}}")
'''

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(body)

    # Make executable / 添加可执行权限
    os.chmod(script_path, 0o755)

    print(f"  ✅ Plot script exported / 图表脚本已导出: {script_path}")


def plot_convergence_curve(ax, data, title_en="Convergence Curve", title_zh="收敛曲线"):
    """
    收敛曲线绘制模板 / Convergence curve plot template.
    对应论文中的训练损失/误差下降曲线.
    Corresponds to training loss / error descent curves in papers.
    """
    epochs = data.get("epochs", range(len(data.get("loss", []))))
    loss = data.get("loss", [])
    val_loss = data.get("val_loss", [])

    if loss:
        ax.plot(epochs, loss, label=f"Train {data.get('label', 'Loss')}", linewidth=1.5)
    if val_loss:
        ax.plot(epochs, val_loss, label=f"Val {data.get('label', 'Loss')}", linewidth=1.5,
                linestyle="--")

    ax.set_xlabel(data.get("xlabel_en", "Epoch") + " / " + data.get("xlabel_zh", "轮次"))
    ax.set_ylabel(data.get("ylabel_en", "Loss") + " / " + data.get("ylabel_zh", "损失"))
    ax.set_title(f"{title_en}\\n{title_zh}")
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_bar_comparison(ax, data, title_en="Result Comparison", title_zh="结果对比"):
    """
    柱状图对比模板 / Bar chart comparison template.
    对应论文中的方法对比表/消融实验.
    Corresponds to method comparison tables / ablation studies in papers.
    """
    labels = data.get("labels", [])
    values = data.get("values", [])
    bar_labels = data.get("bar_labels", [])

    x = np.arange(len(labels))
    width = 0.8 / max(len(bar_labels), 1)

    for i, (bl, vals) in enumerate(zip(bar_labels, values)):
        offset = (i - len(bar_labels) / 2 + 0.5) * width
        bars = ax.bar(x + offset, vals, width, label=bl)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(data.get("ylabel_en", "Value") + " / " + data.get("ylabel_zh", "值"))
    ax.set_title(f"{title_en}\\n{title_zh}")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)


def generate_example():
    """
    示例：生成收敛曲线 + 对比柱状图及其独立脚本
    Example: generate convergence curve + bar chart with standalone scripts
    """
    output_dir = Path("results/figures")
    code_dir = output_dir / "code"
    output_dir.mkdir(parents=True, exist_ok=True)
    code_dir.mkdir(parents=True, exist_ok=True)

    # === Example 1: Convergence curve / 收敛曲线 ===
    np.random.seed(42)
    epochs = np.arange(1, 101)
    train_loss = 2.0 * np.exp(-0.05 * epochs) + 0.1 * np.random.randn(100)
    val_loss = 2.0 * np.exp(-0.04 * epochs) + 0.1 * np.random.randn(100)

    conv_data = {
        "epochs": epochs, "loss": train_loss, "val_loss": val_loss,
        "label": "MSE", "xlabel_en": "Epoch", "xlabel_zh": "轮次",
        "ylabel_en": "MSE Loss", "ylabel_zh": "MSE损失",
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    plot_convergence_curve(ax, conv_data)
    plt.tight_layout()
    plt.savefig(output_dir / "convergence.png", dpi=150)
    plt.close()
    print(f"  ✅ Figure saved / 图表已保存: {output_dir}/convergence.png")

    # Export standalone script / 导出独立脚本
    plot_source = '''
def plot(ax):
    """Convergence curve / 收敛曲线 (Paper Figure 1 / 论文图1)"""
    import numpy as np
    np.random.seed(42)

    epochs = np.arange(1, 101)
    train_loss = 2.0 * np.exp(-0.05 * epochs) + 0.1 * np.random.randn(100)
    val_loss = 2.0 * np.exp(-0.04 * epochs) + 0.1 * np.random.randn(100)

    ax.plot(epochs, train_loss, label="Train MSE", linewidth=1.5)
    ax.plot(epochs, val_loss, label="Val MSE", linewidth=1.5, linestyle="--")
    ax.set_xlabel("Epoch / 轮次")
    ax.set_ylabel("MSE Loss / MSE损失")
    ax.set_title("Convergence Curve\\n收敛曲线")
    ax.legend()
    ax.grid(True, alpha=0.3)
'''

    export_plot_script(
        code_dir / "plot_convergence.py",
        plot_source,
        {
            "title_en": "Convergence Curve",
            "title_zh": "收敛曲线",
            "paper_title": "Example Paper",
            "figure_number": "Figure 1",
            "data_source": "Synthetic data / 合成数据",
            "output_file": "../convergence.png",
            "random_seed": 42,
        }
    )

    # === Example 2: Bar comparison / 对比柱状图 ===
    bar_data = {
        "labels": ["Method A", "Method B", "Ours"],
        "bar_labels": ["Metric 1", "Metric 2"],
        "values": [[85.2, 87.1, 92.3], [78.5, 80.2, 88.7]],
        "ylabel_en": "Accuracy (%)", "ylabel_zh": "准确率(%)",
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    plot_bar_comparison(ax, bar_data)
    plt.tight_layout()
    plt.savefig(output_dir / "comparison.png", dpi=150)
    plt.close()
    print(f"  ✅ Figure saved / 图表已保存: {output_dir}/comparison.png")

    # Export standalone script / 导出独立脚本
    plot_source2 = '''
def plot(ax):
    """Method comparison bar chart / 方法对比柱状图 (Paper Table 1 / 论文表1)"""
    import numpy as np
    np.random.seed(42)

    labels = ["Method A", "Method B", "Ours"]
    x = np.arange(len(labels))
    width = 0.35

    values_1 = [85.2, 87.1, 92.3]
    values_2 = [78.5, 80.2, 88.7]

    ax.bar(x - width/2, values_1, width, label="Metric 1")
    ax.bar(x + width/2, values_2, width, label="Metric 2")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Accuracy (%) / 准确率(%)")
    ax.set_title("Result Comparison\\n结果对比")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
'''

    export_plot_script(
        code_dir / "plot_comparison.py",
        plot_source2,
        {
            "title_en": "Result Comparison",
            "title_zh": "结果对比",
            "paper_title": "Example Paper",
            "figure_number": "Table 1 / Figure 2",
            "data_source": "results/raw_metrics.csv",
            "output_file": "../comparison.png",
            "random_seed": 42,
        }
    )

    # Generate requirements for plotting / 生成绘图依赖
    with open(code_dir / "requirements.txt", "w") as f:
        f.write("matplotlib>=3.7\nnumpy>=1.24\n")
    print(f"  ✅ Plot dependencies written / 绘图依赖已写入: {code_dir}/requirements.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Figure generation with code export / 图表生成与源码导出")
    parser.add_argument("--data", help="Data file path / 数据文件路径")
    parser.add_argument("--config", help="Config file path / 配置文件路径")
    parser.add_argument("--output", default="results/figures",
                        help="Output directory / 输出目录")
    parser.add_argument("--mode", choices=["convergence", "comparison", "all"],
                        default="all", help="Plot type / 图表类型")
    args = parser.parse_args()

    if args.mode == "all":
        generate_example()
    else:
        # User mode: read data from file and plot / 用户模式: 从文件读取数据并绘图
        if args.data:
            print(f"Reading data from / 从文件读取数据: {args.data}")
        print(f"Output to / 输出到: {args.output}")
        print("Custom plotting not yet implemented / 自定义绘图尚未实现, using example")
        generate_example()

    print("\\nDone / 完成")
