---
name: visualization
description: Create publication-quality charts and visualizations — line plots, bar charts, heatmaps, scatter plots, pie charts, box plots, violin plots. Use when data needs to be visualized.
triggers:
  - "график"
  - "диаграмма"
  - "визуализация"
  - "построй график"
  - "chart"
  - "plot"
  - "heatmap"
---

# Visualization Skill

## Goal
Create clear, publication-quality visualizations saved as PNG files.

## Chart Types & When to Use

| Chart | Use case |
|-------|----------|
| Line plot | Time series, trends over time |
| Bar chart | Categorical comparisons |
| Histogram | Distribution of numeric data |
| Scatter plot | Relationship between two numeric vars |
| Heatmap | Correlation matrices, 2D density |
| Box/Violin | Distribution + outliers by group |
| Pie chart | Part-to-whole (use sparingly, max 6 slices) |

## Style Standards
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Always set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Figure size
fig, ax = plt.subplots(figsize=(10, 6))

# Always: title, axis labels, grid
ax.set_title('Title', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('X Label', fontsize=12)
ax.set_ylabel('Y Label', fontsize=12)

# Save — NEVER plt.show()
plt.tight_layout()
plt.savefig('~/analytics_output/chart_name.png', dpi=150, bbox_inches='tight')
plt.close()
```

## Rules
- Save ALL plots to `~/analytics_output/`
- Filename: descriptive snake_case (e.g., `correlation_matrix.png`)
- Always close figures after saving to free memory
- Include legend when multiple series
- Russian labels are OK
- Upload saved PNGs to 0x0.st and return URLs
