# Vibe Finance

> Chill quant research for people who don't speak Python. Ask in plain Chinese, get backtests or stock picks — with every parameter shown and editable before execution.

![status](https://img.shields.io/badge/status-demo-10b981) ![python](https://img.shields.io/badge/python-3.11-3776ab) ![next](https://img.shields.io/badge/next.js-14-000000) ![gemini](https://img.shields.io/badge/gemini-2.5%20flash-4285f4) ![license](https://img.shields.io/badge/license-MIT-lightgrey)

## Screenshots


![Main dashboard](./docs/screenshot-main.png)
![Parsed parameters panel](./docs/screenshot-params.png)


## Why

Most "AI finance assistants" are black boxes: you ask a question, you get an answer, and you have no idea how your intent was interpreted. **Vibe Finance** takes a different approach — every natural language query is first parsed into an editable, structured parameter panel that you can verify and tweak before anything runs. The LLM is a parser, not an oracle.

Built as an end-to-end demo covering data engineering (506 Taiwan stocks × 23 years), factor computation, feature engineering, NL parsing, backtesting, and a Bloomberg-inspired dark UI.

## Features

- **Ask in Chinese** — `回測低 PE 前 20% 的策略` or `現在 EPS 成長率最高的前 30 檔` just works
- **Transparent parameter panel** — parsed parameters are shown as editable cards; override anything before execution
- **Two modes**
  - **Backtest** — total/annualized return, Sharpe, max drawdown, win rate, equity curve vs equal-weighted market
  - **Screen** — latest-period picks ranked by factor, with Chinese names
- **Four factors** — EPS, revenue YoY growth, P/E, P/B
- **Four feature transforms** — raw, growth rate, rolling z-score, momentum
- **No look-ahead** — portfolio at t formed from t's factor values, held through t+1

## Tech

| Layer | Stack |
|---|---|
| Frontend | Next.js 14 App Router, TypeScript, Tailwind, shadcn/ui, Recharts |
| Backend | FastAPI, Pydantic v2, pandas, numpy |
| Storage | DuckDB (single-file, fast pivots) |
| NL parsing | Gemini 2.5 Flash with structured output |
| Tests | pytest |

## Architecture

```
Chinese NL query
       │
       ▼
  Gemini 2.5 Flash ──▶ ParsedParams (editable in UI)
                              │
                              ▼
                     ┌────────────────────┐
                     │  Factor Engine     │
                     │  feature eng.      │
                     │       ↓            │
                     │  cross-sectional   │
                     │  rank & select     │
                     │       ↓            │
                     │  backtest / screen │
                     └────────┬───────────┘
                              │
                              ▼
                    metrics + curve / picks
```

## Project structure

```
vibe-finance/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI entry
│   │   ├── db.py                DuckDB connection & schema
│   │   ├── schemas.py           Pydantic contract
│   │   ├── features.py          feature engineering
│   │   ├── factor_engine.py     ranking, backtest, screen
│   │   ├── gemini.py            NL → params
│   │   └── routers/
│   ├── scripts/                 seed_data, smoke_test
│   ├── tests/                   pytest
│   └── data/                    (gitignored)
└── frontend/
    ├── app/                     page.tsx, layout, globals.css
    ├── components/              QueryInput, ParamsPanel, BacktestView, ScreenView
    └── lib/                     types, api client
```

## Setup

**Prerequisites:** Python 3.11+, Node 18+, Gemini API key from [AI Studio](https://aistudio.google.com/apikey).

```
git clone https://github.com/<your-username>/vibe-finance.git
cd vibe-finance
```

### Backend

```
cd backend
python -m venv venv
source venv/bin/activate             # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # paste your Gemini key into .env
# put your CSVs in data/ (see data/README.md for format)
python -m scripts.seed_data          # builds market.duckdb
uvicorn app.main:app --reload --port 8000
```

### Frontend

```
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Example queries

Type in Chinese, directly in the UI:

- `回測低 PE 前 20% 的策略` → backtest bottom-20% P/E
- `現在 EPS 成長率最高的前 30 檔` → screen top-30 EPS YoY growth
- `從 2020 年開始，高 EPS 的策略年化報酬多少` → backtest high-EPS since 2020
- `PB 最低的前 10% 股票現在是哪些` → screen lowest-P/B stocks now

## Design decisions

**DuckDB over Postgres** — single file, zero setup, fast analytical pivots over 2M+ rows. Perfect for research workloads.

**Gemini structured output** — `response_schema` gives type-safe round-trips to Pydantic without prompt wrangling. Consistent parsing across different phrasings.

**Editable parameters in the UI** — NL is ambiguous. Users need to verify interpretation before running compute. This is the product differentiator vs opaque AI tools.

**Equal-weighted benchmark** — the portfolio is equal-weighted, so comparing against a market-cap index conflates factor alpha with size. Equal-weighted market = cleaner attribution.

## What's intentionally out of scope

Transaction costs, slippage, survivorship bias, sector neutrality, factor stacking, walk-forward optimization. This is a transparency and UX demo, not a production quant platform.

## Sample run

506 Taiwan stocks, 2018–2024, monthly rebalance:

| Strategy | Ann. Return | Sharpe | Max DD |
|---|---|---|---|
| Low P/E bottom 20% | ~20.1% | ~1.17 | -31.4% |

For illustration only. Not investment advice.

## Roadmap

- [ ] Multi-factor composite scoring
- [ ] Rolling IC / IR analysis
- [ ] Transaction cost modelling
- [ ] Sector-neutral weighting
- [ ] Save & compare named strategies
- [ ] Parquet / CSV export

## License

MIT

## Notes

Built as a weekend demo exploring "verifiable AI" in financial research — the LLM parses intent, humans verify, engines compute.
