# Data directory

CSV files live here. Not shipped with the repo (see .gitignore).

## Required files — all wide format, first column is date

**Monthly (date format: YYYY-MM, month-end implied):**
- `eps.csv` — earnings per share
- `earn_yoy.csv` — revenue YoY growth (unit: %)
- `pe_ratio.csv` — P/E ratio
- `pb_ratio.csv` — P/B ratio

**Daily (date format: YYYY-MM-DD):**
- `price.csv` — close price
- `vix_index.csv` — VIX index (columns: 日期, VIX_收盤價)

**Mapping:**
- `stock_names.json` — `{"2330": "台積電", ...}`

## Load into DuckDB

```
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate
python -m scripts.seed_data
```

This creates `backend/market.duckdb`.
