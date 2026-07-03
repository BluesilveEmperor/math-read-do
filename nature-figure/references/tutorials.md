# Tutorials — Nature Figure Making

End-to-end walkthroughs for common publication figure types. Each tutorial follows
the figure-contract-first approach: conclusion, evidence hierarchy, then code.

## Tutorial 1: Grouped bar chart

### Contract

- Core conclusion: "Method X outperforms all baselines across 4 metrics"
- Archetype: quantitative grid
- Backend: Python

### Implementation

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'

metrics = ['Accuracy', 'Precision', 'Recall', 'F1']
methods = ['Baseline-A', 'Baseline-B', 'Method-X']
data = np.array([
    [85.2, 83.1, 81.5, 82.0],
    [87.3, 86.0, 84.8, 85.4],
    [92.1, 91.3, 90.5, 91.0],
])
errors = np.array([
    [1.2, 1.5, 1.8, 1.6],
    [1.1, 1.3, 1.5, 1.4],
    [0.8, 0.9, 1.0, 0.9],
])

colors = ['#B4C0E4', '#7884B4', '#484878']
fig, axes = plt.subplots(1, 5, figsize=(32, 8))
gs = axes[0].get_gridspec()
for i, (metric, ax) in enumerate(zip(metrics, axes[:4])):
    x = np.arange(len(methods))
    bars = ax.bar(x, data[:, i], yerr=errors[:, i], capsize=5, color=colors, edgecolor='black', linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels([])
    ax.set_title(metric, fontsize=24, pad=12)
    ax.set_ylabel('Score (%)', fontsize=20)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    if i == 0:
        handles, labels = ax.get_legend_handles_labels()
axes[4].legend(handles, methods, fontsize=20, loc='center', frameon=False)
axes[4].set_axis_off()
fig.tight_layout(pad=2)
fig.savefig('grouped_bar.svg', bbox_inches='tight')
fig.savefig('grouped_bar.png', dpi=300, bbox_inches='tight')
plt.close(fig)
```

## Tutorial 2: Trend / line plot with uncertainty

### Contract

- Core conclusion: "Model performance scales with data size, but saturates after 10K samples"
- Archetype: quantitative grid
- Backend: Python

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'

x = np.array([100, 500, 1000, 5000, 10000, 50000])
baseline_mean = np.array([72, 78, 82, 86, 87, 87.5])
baseline_std = np.array([3, 2.5, 2, 1.5, 1.2, 1.0])
method_mean = np.array([70, 76, 83, 89, 91.5, 92])
method_std = np.array([4, 3, 2.5, 1.8, 1.0, 0.8])

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(x, baseline_mean, 'o-', color='#7884B4', linewidth=2.5, markersize=8, label='Baseline')
ax.fill_between(x, baseline_mean - baseline_std, baseline_mean + baseline_std, color='#7884B4', alpha=0.15)
ax.plot(x, method_mean, 's-', color='#484878', linewidth=2.5, markersize=8, label='Method-X')
ax.fill_between(x, method_mean - method_std, method_mean + method_std, color='#484878', alpha=0.15)
ax.set_xlabel('Training samples', fontsize=16)
ax.set_ylabel('Accuracy (%)', fontsize=16)
ax.set_xscale('log')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.legend(frameon=False, fontsize=14)
fig.tight_layout(pad=2)
fig.savefig('trend_plot.svg', bbox_inches='tight')
fig.savefig('trend_plot.png', dpi=300, bbox_inches='tight')
plt.close(fig)
```
