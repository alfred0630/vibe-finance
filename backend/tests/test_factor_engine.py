"""integration tests for factor_engine"""
from datetime import date
import pytest
from app.schemas import ParsedParams, FeatureConfig
from app.factor_engine import run_backtest, run_screen, run_research


def make_params(mode, **overrides):
    defaults = dict(
        mode=mode,
        factor="pe",
        feature=FeatureConfig(type="none", window=12),
        direction="bottom",
        percentile=20.0,
        start_date=date(2018, 1, 1),
        end_date=date(2024, 12, 31),
        rebalance="monthly",
    )
    defaults.update(overrides)
    return ParsedParams(**defaults)


def test_backtest_low_pe():
    """低 PE 回測，應能跑出合理的 Sharpe / 報酬。"""
    params = make_params("backtest", factor="pe", direction="bottom", percentile=20.0)
    result = run_backtest(params)
    assert result.mode == "backtest"
    assert len(result.equity_curve) > 10
    assert result.metrics.num_rebalances > 50  # 7 年 * 12 月
    assert -1.0 < result.metrics.max_drawdown <= 0.0
    assert result.metrics.annualized_vol > 0


def test_screen_high_eps():
    """選出當期 EPS 最高的前 20%。"""
    params = make_params("screen", factor="eps", direction="top", percentile=20.0)
    result = run_screen(params)
    assert result.mode == "screen"
    assert result.num_selected > 0
    # ranking 遞增、factor_value 遞減（因為是 top）
    for i in range(len(result.picks) - 1):
        assert result.picks[i].rank < result.picks[i + 1].rank
        assert result.picks[i].factor_value >= result.picks[i + 1].factor_value
    # 應該帶出中文名（或至少不是空字串）
    assert all(p.stock_name for p in result.picks)


def test_screen_with_growth_feature():
    """EPS 成長率 top 20%。"""
    params = make_params(
        "screen", factor="eps", direction="top", percentile=20.0,
        feature=FeatureConfig(type="growth_rate", window=12),
    )
    result = run_screen(params)
    assert result.num_selected > 0


def test_run_research_dispatches():
    """run_research 應該依 mode 分派。"""
    bt = run_research(make_params("backtest"))
    assert bt.mode == "backtest"
    sc = run_research(make_params("screen"))
    assert sc.mode == "screen"
