# Nature Figure Design Theory

Derived from scripts in the [figures4papers](https://github.com/ChenLiu-1996/figures4papers) repository
(published in *Nature Machine Intelligence* and top ML/bioinformatics venues).

## Typography

### Font stack (priority order)
- **Nature standard**: `font.family = 'sans-serif'`, `font.sans-serif = ['Arial']`
- **Fallback stack**: `['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']`
- SVG/PDF editable text: always set `svg.fonttype = 'none'`

### Font size hierarchy
| Context | font.size |
|---------|-----------|
| Journal-final dense multi-panel figure at publication width | 7–9 |
| Large comparison bar panels (figsize > 28in wide) | 24 |
| Compact subfigures / analytic plots | 15–16 |
| In-bar annotations | 32–36 |
| Legend text on large panels | 28–38 |

## Axes & Spines

```python
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['legend.frameon'] = False
```

## Color Palette

Semantic: blue = proposed method, green = positive variants, red = baselines, neutral = reference/background.

### Unified-family rule (recommended for NMI-style pages)

Prefer one cool family for baselines and one lilac/rose family for the proposed method line.

```python
PALETTE_NMI_PASTEL = {
    "baseline_dark": "#484878",
    "baseline_mid":  "#7884B4",
    "baseline_soft": "#B4C0E4",
    "ours_tiny":  "#E4E4F0",
    "ours_base":  "#E4CCD8",
    "ours_large": "#F0C0CC",
    "delta_up":   "#2E9E44",
    "delta_down": "#E53935",
}
```

Rules:
1. Keep related baselines in one cool family.
2. Keep `Tiny / Base / Large` or sibling variants in one hero family.
3. Reserve green/red for arrows, gains, drops, thresholds, or signed biological direction.

## Layout and Composition

### Figure sizes
| Figure type | Typical figsize |
|-------------|----------------|
| Journal-width composite page / asymmetric multi-panel | (7.0–7.4, 5.5–7.8) |
| Multi-metric bar (3–4 metrics + legend) | (28–45, 6–12) |
| Compact single bar | (9–16, 5–8) |
| Trend / line multi-panel | (14, 4) or (9, 8) |
| Heatmap single | (8–20, 5–9) |

### Dedicated legend panel
```python
ax_legend = fig.add_subplot(1, n+1, n+1)
ax_legend.legend(handles, labels, fontsize=..., loc='center', frameon=False)
ax_legend.set_axis_off()
```

### Panel labels and gutters
- Use small bold lowercase panel letters near the top-left edge.
- Keep gutters tight but real.
- Avoid decorative panel boxes. Alignment and whitespace should carry the structure.

## Bar Chart Rules

### Vertical bars (comparison)
```python
bars = ax.bar(x_positions, values, yerr=std_values, capsize=5, color=colors, label=method_names, edgecolor='black', linewidth=1.5)
```

### Horizontal bars (ablation)
```python
ax.barh(y_positions, values, xerr=std_values, color=[(r, g, b, alpha) for alpha in alphas], ecolor='k', capsize=5)
```

## Export Policy

SVG is the required primary format. Always save SVG first.

```python
fig.savefig('./figures/name.svg', bbox_inches='tight')
fig.savefig('./figures/name.png', dpi=300, bbox_inches='tight')
plt.close(fig)
```

## Multi-Panel Information Architecture

Each panel must answer a unique scientific question.

**Recommended three-level progression**:
| Level | Question answered | Typical encoding |
|-------|------------------|-----------------|
| Overview | "What is the landscape?" | Stacked bar, composition |
| Deviation | "What is distinctive per group?" | Z-score heatmap (diverging cmap) |
| Relationship | "How do variables co-vary?" | Scatter / bubble plot |

## Reproduction Checklist

- [ ] MANDATORY first lines: `font.family='sans-serif'`, `font.sans-serif=['Arial','DejaVu Sans','Liberation Sans']`, `svg.fonttype='none'`
- [ ] Save as SVG (primary). PNG dpi=300 as optional raster preview.
- [ ] Top and right spines off; frameless legend
- [ ] Font size >= 16 base
- [ ] Colors from blue-green-red-neutral semantic palette
- [ ] Black background used only for imaging plates
- [ ] Y-limits tightened to data range
- [ ] `tight_layout(pad=2)` before save
- [ ] `plt.close(fig)` after save
