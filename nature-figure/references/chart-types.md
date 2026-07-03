# Chart Types — Nature Figure Making

## Radar / Polar Charts

```python
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='polar')
categories = ['Accuracy', 'Precision', 'Recall', 'F1', 'Speed']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

values_baseline = [85, 82, 80, 83, 70]
values_method = [92, 91, 90, 91, 85]
values_baseline += values_baseline[:1]
values_method += values_method[:1]

ax.plot(angles, values_baseline, 'o-', linewidth=2, label='Baseline', color='#B4C0E4')
ax.fill(angles, values_baseline, alpha=0.1, color='#B4C0E4')
ax.plot(angles, values_method, 'o-', linewidth=2, label='Method-X', color='#484878')
ax.fill(angles, values_method, alpha=0.1, color='#484878')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=14)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), frameon=False)
fig.tight_layout()
```

## 3D Sphere / Illustration

```python
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_surface(x, y, z, color='#3775BA', alpha=0.6, rstride=4, cstride=4)
ax.set_axis_off()
```

## Fill-between / Stacked Area

```python
x = np.arange(10)
y1 = np.random.rand(10) * 5
y2 = y1 + np.random.rand(10) * 3
y3 = y2 + np.random.rand(10) * 2
fig, ax = plt.subplots(figsize=(10, 6))
ax.fill_between(x, 0, y1, color='#3775BA', alpha=0.7, label='Category A')
ax.fill_between(x, y1, y2, color='#8BCF8B', alpha=0.7, label='Category B')
ax.fill_between(x, y2, y3, color='#B64342', alpha=0.7, label='Category C')
ax.legend(frameon=False)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
```

## Log-scale Bar

```python
fig, ax = plt.subplots(figsize=(10, 6))
categories = ['A', 'B', 'C', 'D', 'E']
values = [10, 100, 1000, 5000, 25000]
ax.bar(categories, values, color='#3775BA', edgecolor='black', linewidth=1.5)
ax.set_yscale('log')
ax.set_ylabel('Count (log scale)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
```
