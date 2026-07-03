# Common Patterns — Nature Figure Making

Reusable layout and encoding patterns used across publication-grade scripts.

## Pattern 1: Ultra-wide multi-metric bar panel

```python
fig = plt.figure(figsize=(45, 12))
gs = gridspec.GridSpec(1, n_metrics)
for i, metric in enumerate(metrics):
    ax = fig.add_subplot(gs[i])
    ax.bar(x, values[metric], color=colors, ...)
    ax.set_ylabel(metric, fontsize=54, labelpad=12)
    ax.set_xticks([])
ax_leg = fig.add_subplot(gs[-1])
ax_leg.legend(handles, labels, fontsize=38, loc='center', frameon=False)
ax_leg.set_axis_off()
fig.tight_layout(pad=2)
```

## Pattern 2: Dedicated legend panel

```python
fig, axes = plt.subplots(1, n_data + 1, figsize=(...))
for i, ax in enumerate(axes[:-1]):
    bars = ax.bar(...)
    if i == 0:
        handles, labels = ax.get_legend_handles_labels()
axes[-1].legend(handles, labels, fontsize=28, loc='center', frameon=False)
axes[-1].set_axis_off()
```

## Pattern 5: Alpha-graduated ablation bars

```python
blue_rgb = (0.215686, 0.458824, 0.729412)
n_ablations = len(ablation_configs)
alphas = np.linspace(0.2, 1.0, n_ablations)
colors = [(blue_rgb[0], blue_rgb[1], blue_rgb[2], a) for a in alphas]
```

## Pattern 7: Semantic or family color mapping

```python
method_colors = {
    'ResNet1d18': '#484878',
    'ResNet1d34': '#7884B4',
    'ECGFounder': '#B4C0E4',
    'CSFM-Tiny':  '#E4E4F0',
    'CSFM-Base':  '#E4CCD8',
    'CSFM-Large': '#F0C0CC',
}
```

## Pattern 12: Schematic hero panel with supporting quant row

```python
fig = plt.figure(figsize=(7.2, 6.2))
gs = fig.add_gridspec(2, 4, height_ratios=[2.2, 1.0], hspace=0.18, wspace=0.28)
ax_top = fig.add_subplot(gs[0, :])
ax_b = fig.add_subplot(gs[1, 0])
ax_c = fig.add_subplot(gs[1, 1:3])
ax_d = fig.add_subplot(gs[1, 3])
```

## Pattern 14: Clinical triptych

```python
fig = plt.figure(figsize=(7.2, 6.8))
gs = fig.add_gridspec(3, 3, height_ratios=[1.0, 1.35, 0.8], hspace=0.28, wspace=0.32)
axes_top = [fig.add_subplot(gs[0, i]) for i in range(3)]
axes_mid = [fig.add_subplot(gs[1, i]) for i in range(3)]
axes_bot = [fig.add_subplot(gs[2, i]) for i in range(3)]
```

## Pattern 15: Asymmetric hero panel

```python
fig = plt.figure(figsize=(7.2, 5.8))
gs = fig.add_gridspec(3, 4, hspace=0.25, wspace=0.28)
ax_a = fig.add_subplot(gs[0, :2])
ax_b = fig.add_subplot(gs[0, 2])
ax_c = fig.add_subplot(gs[1, :2])
ax_d = fig.add_subplot(gs[1, 2])
ax_e = fig.add_subplot(gs[:, 3])
ax_f = fig.add_subplot(gs[2, :2])
```
