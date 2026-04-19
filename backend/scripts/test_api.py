"""測試 FastAPI endpoints（uvicorn 要開著）"""
import json
import requests

BASE = "http://localhost:8000"


def test_health():
    r = requests.get(f"{BASE}/health")
    print(f"GET /health  -> {r.status_code} {r.json()}")


def test_parse():
    print("\n=== POST /parse ===")
    r = requests.post(f"{BASE}/parse", json={"query": "幫我回測低 PE 前 20% 的策略"})
    print(f"status: {r.status_code}")
    data = r.json()
    print(f"explanation: {data['explanation']}")
    print(f"params: {json.dumps(data['params'], indent=2, ensure_ascii=False)}")
    return data["params"]


def test_research_backtest(params):
    print("\n=== POST /research (backtest) ===")
    r = requests.post(f"{BASE}/research", json={"params": params})
    print(f"status: {r.status_code}")
    data = r.json()
    if "metrics" in data:
        m = data["metrics"]
        print(f"mode: {data['mode']}")
        print(f"  Annualized return: {m['annualized_return']:.1%}")
        print(f"  Sharpe: {m['sharpe_ratio']:.2f}")
        print(f"  Max DD: {m['max_drawdown']:.1%}")
        print(f"  Equity curve points: {len(data['equity_curve'])}")


def test_research_screen():
    print("\n=== POST /research (screen) ===")
    params = {
        "mode": "screen",
        "factor": "eps",
        "feature": {"type": "growth_rate", "window": 12},
        "direction": "top",
        "percentile": 6.0,
        "start_date": "2023-01-01",
        "end_date": "2024-12-31",
        "rebalance": "monthly",
    }
    r = requests.post(f"{BASE}/research", json={"params": params})
    print(f"status: {r.status_code}")
    data = r.json()
    print(f"as_of: {data['as_of_date']}, picks: {data['num_selected']}")
    for p in data["picks"][:5]:
        print(f"  #{p['rank']} {p['stock_id']} {p['stock_name']} {p['factor_value']:.2%}")


if __name__ == "__main__":
    test_health()
    params = test_parse()
    test_research_backtest(params)
    test_research_screen()
