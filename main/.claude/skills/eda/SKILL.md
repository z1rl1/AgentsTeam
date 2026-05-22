---
name: eda
description: Exploratory Data Analysis — full EDA pipeline on any dataset or topic. Loads data, profiles it, finds patterns, outliers, correlations, and distributions. Use when starting any data analysis task.
triggers:
  - "exploratory data analysis"
  - "EDA"
  - "анализ данных"
  - "изучи данные"
  - "профиль данных"
---

# Exploratory Data Analysis (EDA)

## Goal
Perform a complete EDA on the provided dataset or topic data. Understand the structure, quality, and patterns before deeper analysis.

## Steps

1. **Load & inspect**
   - Shape, dtypes, head/tail
   - Memory usage
   - Column descriptions

2. **Data quality**
   - Missing values (count + % per column)
   - Duplicates
   - Outliers (IQR method + z-score)
   - Invalid values (negatives where impossible, etc.)

3. **Univariate analysis**
   - Numeric: mean, median, std, skewness, kurtosis + histogram
   - Categorical: value counts, top-N + bar chart

4. **Bivariate analysis**
   - Correlation matrix (Pearson + Spearman)
   - Scatter plots for top correlated pairs
   - Group comparisons

5. **Key findings summary**
   - Top 5 insights in plain language
   - Data quality score
   - Recommended next steps

## Output
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Always save plots, never plt.show()
plt.savefig('output/eda_plot.png', dpi=150, bbox_inches='tight')
plt.close()
```

Always save all plots to `~/analytics_output/` directory.
Report findings as structured text + list of saved plot paths.
