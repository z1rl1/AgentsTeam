---
name: scraping
description: Collect real data from the web — scrape websites, call public APIs, download datasets. Use when analysis needs real-world data on a topic.
triggers:
  - "собери данные"
  - "парсинг"
  - "scraping"
  - "данные из интернета"
  - "реальные данные"
  - "API данные"
---

# Web Scraping & Data Collection Skill

## Priority Order (fastest to slowest)
1. **Public API** — always prefer if available
2. **Downloadable dataset** — Kaggle, UCI, data.gov
3. **HTML scraping** — last resort

## Public APIs (no auth needed)

| Topic | API |
|-------|-----|
| Криптовалюты | CoinGecko API |
| Акции/финансы | Yahoo Finance (yfinance) |
| Погода | Open-Meteo |
| Новости | NewsAPI |
| Страны/население | RestCountries |
| COVID данные | disease.sh |

```python
import requests
import pandas as pd

# CoinGecko example
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100}
resp = requests.get(url, params=params, timeout=10)
df = pd.DataFrame(resp.json())
```

## HTML Scraping
```python
from bs4 import BeautifulSoup
import requests
import time

headers = {'User-Agent': 'Mozilla/5.0 (research bot)'}
resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# Always: respect robots.txt, add delays
time.sleep(1)  # between requests
```

## Rules
- Always handle errors (try/except, timeouts)
- Save raw data to `~/analytics_output/raw_data.csv`
- Log how many records collected
- Note data freshness (when collected)
- Never scrape more than needed
