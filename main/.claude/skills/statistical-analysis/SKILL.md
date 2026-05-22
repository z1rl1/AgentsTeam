---
name: statistical-analysis
description: Statistical analysis — descriptive stats, hypothesis testing, distributions, confidence intervals, ANOVA, regression. Use when deep statistical insight is needed.
triggers:
  - "статистика"
  - "гипотеза"
  - "статистический анализ"
  - "распределение"
  - "корреляция"
  - "regression"
  - "t-test"
  - "ANOVA"
---

# Statistical Analysis Skill

## Workflow

### 1. Descriptive Statistics
```python
import scipy.stats as stats
import numpy as np

# Full profile of a variable
def describe_full(data):
    return {
        'mean': np.mean(data),
        'median': np.median(data),
        'std': np.std(data),
        'skewness': stats.skew(data),
        'kurtosis': stats.kurtosis(data),
        'ci_95': stats.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=stats.sem(data))
    }
```

### 2. Distribution Testing
```python
# Normality test
stat, p = stats.shapiro(data)  # n < 5000
stat, p = stats.kstest(data, 'norm')  # any n

# Fit best distribution
from scipy.stats import norm, expon, lognorm
distributions = [norm, expon, lognorm]
# Fit each, compare AIC
```

### 3. Hypothesis Testing
| Test | When to use |
|------|-------------|
| t-test | Compare 2 group means, normal data |
| Mann-Whitney U | Compare 2 groups, non-normal |
| ANOVA | Compare 3+ group means |
| Chi-square | Categorical independence |
| Pearson/Spearman | Correlation between variables |

```python
# Always report: statistic, p-value, interpretation
stat, p = stats.ttest_ind(group1, group2)
print(f"p={p:.4f} — {'significant' if p < 0.05 else 'not significant'} at α=0.05")
```

### 4. Regression
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

model = LinearRegression()
model.fit(X_train, y_train)
# Report: R², RMSE, coefficients, p-values
```

## Output
Always include:
- Test name + result + interpretation in plain language
- Confidence intervals where applicable
- Effect size (not just p-value)
- Visualization of the result
