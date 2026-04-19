"""驗證因子引擎的實際輸出數值。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date
from app.schemas import ParsedParams, FeatureConfig
from app.factor_engine import run_backtest, run_screen


def main():
    print("=" * 60)
    print("低 PE 回測 (2018-2024)")
    print("=" * 60)
    p = ParsedParams(
        mode="backtest", factor="pe", direction="bottom", percentile=20.0,
        start_date=date(2018, 1, 1), end_date=date(2024, 12, 31),
    )
    r = run_backtest(p)
    print(f"Total return:       {r.metrics.total_return:>8.1%}")
    print(f"Annualized return:  {r.metrics.annualized_return:>8.1%}")
    print(f"Annualized vol:     {r.metrics.annualized_vol:>8.1%}")
    print(f"Sharpe ratio:       {r.metrics.sharpe_ratio:>8.2f}")
    print(f"Max drawdown:       {r.metrics.max_drawdown:>8.1%}")
    print(f"Win rate:           {r.metrics.win_rate:>8.1%}")
    print(f"Rebalances:         {r.metrics.num_rebalances:>8d}")
    print(f"Equity curve pts:   {len(r.equity_curve):>8d}")
    print(f"First point:        {r.equity_curve[0].date} port={r.equity_curve[0].portfolio:.4f}")
    print(f"Last point:         {r.equity_curve[-1].date} port={r.equity_curve[-1].portfolio:.4f} bench={r.equity_curve[-1].benchmark:.4f}")

    print()
    print("=" * 60)
    print("EPS top 20% 選股 (as of latest in 2024)")
    print("=" * 60)
    p = ParsedParams(
        mode="screen", factor="eps", direction="top", percentile=20.0,
        start_date=date(2023, 1, 1), end_date=date(2024, 12, 31),
    )
    r = run_screen(p)
    print(f"As of: {r.as_of_date}, selected: {r.num_selected}")
    for pick in r.picks[:15]:
        print(f"  #{pick.rank:>3}  {pick.stock_id:<8} {pick.stock_name:<20} EPS={pick.factor_value:>7.2f}")

    print()
    print("=" * 60)
    print("EPS 成長率 top 20% 選股 (feature=growth_rate, window=12)")
    print("=" * 60)
    p = ParsedParams(
        mode="screen", factor="eps", direction="top", percentile=20.0,
        feature=FeatureConfig(type="growth_rate", window=12),
        start_date=date(2023, 1, 1), end_date=date(2024, 12, 31),
    )
    r = run_screen(p)
    print(f"As of: {r.as_of_date}, selected: {r.num_selected}")
    for pick in r.picks[:15]:
        print(f"  #{pick.rank:>3}  {pick.stock_id:<8} {pick.stock_name:<20} EPS_growth={pick.factor_value:>7.2%}")


if __name__ == "__main__":
    main()
