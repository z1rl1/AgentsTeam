---
name: data-cleaning
description: Clean and preprocess raw data — handle missing values, fix types, remove duplicates, normalize, encode categoricals. Always run before analysis.
triggers:
  - "очистка данных"
  - "preprocessing"
  - "пропущенные значения"
  - "data cleaning"
  - "подготовка данных"
---

# Data Cleaning Skill

## Pipeline

```python
import pandas as pd
import numpy as np

def clean_dataframe(df):
    report = []

    # 1. Remove exact duplicates
    n_dup = df.duplicated().sum()
    df = df.drop_duplicates()
    report.append(f"Removed {n_dup} duplicates")

    # 2. Fix column names
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.strip()

    # 3. Handle missing values
    for col in df.columns:
        pct_missing = df[col].isna().mean()
        if pct_missing > 0.5:
            df = df.drop(columns=[col])
            report.append(f"Dropped {col} ({pct_missing:.0%} missing)")
        elif df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown')

    # 4. Fix numeric types
    for col in df.select_dtypes(include='object').columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass

    # 5. Remove outliers (optional, configurable)
    # IQR method for numeric columns
    for col in df.select_dtypes(include='number').columns:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        # Mark but don't remove by default

    return df, report
```

## Output
- Cleaned DataFrame
- Cleaning report (what was done, how many rows/cols affected)
- Before/after comparison: shape, missing %, dtypes
