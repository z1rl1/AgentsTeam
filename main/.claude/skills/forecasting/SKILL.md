---
name: forecasting
description: Time series forecasting — trend analysis, seasonality detection, ARIMA, moving averages, predictions with confidence intervals. Use for any time-based data prediction task.
triggers:
  - "прогноз"
  - "forecasting"
  - "временной ряд"
  - "time series"
  - "предсказание"
  - "тренд"
  - "будущее значение"
---

# Forecasting Skill

## Workflow

### 1. Decompose Time Series
```python
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd

ts = df.set_index('date')['value']
decomposition = seasonal_decompose(ts, model='additive', period=12)

# Plot: trend, seasonal, residual → save as decomposition.png
```

### 2. Check Stationarity
```python
from statsmodels.tsa.stattools import adfuller

result = adfuller(ts)
is_stationary = result[1] < 0.05  # p-value < 0.05 → stationary
```

### 3. Choose Model
| Model | When |
|-------|------|
| Moving Average | Simple trend, no seasonality |
| ARIMA | Stationary or near-stationary |
| SARIMA | Seasonal data |
| Linear trend | Clear linear growth |

### 4. Fit & Forecast
```python
from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(ts, order=(1, 1, 1))
fit = model.fit()
forecast = fit.forecast(steps=12)

# Plot historical + forecast with confidence interval
# Save as forecast.png
```

### 5. Evaluate
```python
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

mae = mean_absolute_error(actual, predicted)
rmse = np.sqrt(mean_squared_error(actual, predicted))
mape = np.mean(np.abs((actual - predicted) / actual)) * 100
```

## Output
- `decomposition.png` — trend/seasonal/residual
- `forecast.png` — historical + predicted + confidence band
- Forecast table: next N periods with values
- Model accuracy: MAE, RMSE, MAPE
- Plain language interpretation of the trend
