"""因子研究引擎"""
from datetime import date
from typing import Optional
import numpy as np
import pandas as pd
import duckdb

from .db import get_conn
from .features import apply_feature
from .schemas import (
    ParsedParams, BacktestResult, BacktestMetrics, EquityPoint,
    ScreenResult, Pick, ResearchResult, FactorName,
)


# ==============================================
# 資料讀取
# ==============================================

def load_factor_matrix(
    conn: duckdb.DuckDBPyConnection,
    factor: FactorName,
    start: date,
    end: date,
) -> pd.DataFrame:
    """從 monthly_data 讀出 wide 格式的因子矩陣。

    多讀 24 個月的歷史，讓 feature engineering 的 lookback window 夠用。
    """
    pad_start = pd.Timestamp(start) - pd.DateOffset(months=24)
    q = f"""
        SELECT date, stock_id, {factor} AS value
        FROM monthly_data
        WHERE date >= ? AND date <= ? AND {factor} IS NOT NULL
    """
    df = conn.execute(q, [pad_start.date(), end]).fetchdf()
    wide = df.pivot(index="date", columns="stock_id", values="value")
    wide.index = pd.to_datetime(wide.index)
    return wide.sort_index()


def load_price_matrix(
    conn: duckdb.DuckDBPyConnection,
    start: date,
    end: date,
    stock_ids: Optional[list[str]] = None,
) -> pd.DataFrame:
    """從 daily_price 讀出 wide 格式收盤價矩陣。"""
    if stock_ids is not None and len(stock_ids) > 0:
        placeholders = ",".join(["?"] * len(stock_ids))
        q = f"""
            SELECT date, stock_id, close
            FROM daily_price
            WHERE date >= ? AND date <= ? AND stock_id IN ({placeholders})
        """
        params = [start, end, *stock_ids]
    else:
        q = """
            SELECT date, stock_id, close
            FROM daily_price
            WHERE date >= ? AND date <= ?
        """
        params = [start, end]
    df = conn.execute(q, params).fetchdf()
    wide = df.pivot(index="date", columns="stock_id", values="close")
    wide.index = pd.to_datetime(wide.index)
    return wide.sort_index()


def load_stock_names(conn: duckdb.DuckDBPyConnection) -> dict[str, str]:
    df = conn.execute("SELECT stock_id, stock_name FROM stocks").fetchdf()
    return dict(zip(df["stock_id"], df["stock_name"]))


# ==============================================
# 選股邏輯
# ==============================================

def select_picks(
    factor_row: pd.Series,
    direction: str,
    percentile: float,
) -> list[str]:
    """從單一橫截面的因子值中，取前/後 x% 的股票代碼。

    - 先過濾掉 NaN
    - 用 percentile（1~50）決定取多少檔；例如 percentile=20 代表前 20%
    - top: 因子值最高的 x%；bottom: 最低的 x%
    """
    valid = factor_row.dropna()
    if len(valid) == 0:
        return []
    n = max(1, int(len(valid) * percentile / 100))
    ranked = valid.sort_values(ascending=(direction == "bottom"))
    return ranked.head(n).index.tolist()


# ==============================================
# 回測核心
# ==============================================

def run_backtest(params: ParsedParams) -> BacktestResult:
    conn = get_conn()
    try:
        # 1. 讀原始因子矩陣（含 padding for feature engineering）
        raw_factor = load_factor_matrix(conn, params.factor, params.start_date, params.end_date)
        if raw_factor.empty:
            raise ValueError(f"No factor data for {params.factor} in range")

        # 2. 套用特徵工程
        factor_df = apply_feature(raw_factor, params.feature.type, params.feature.window)

        # 3. 裁切回使用者指定的 start_date 之後（丟棄 padding）
        factor_df = factor_df[factor_df.index >= pd.Timestamp(params.start_date)]
        factor_df = factor_df[factor_df.index <= pd.Timestamp(params.end_date)]
        if factor_df.empty:
            raise ValueError("No factor data after applying feature engineering within date range.")

        # 4. 讀收盤價（整段期間 + 多讀 15 天作為 buffer）
        price_end = pd.Timestamp(params.end_date) + pd.Timedelta(days=15)
        prices = load_price_matrix(conn, params.start_date, price_end.date())

        # 5. 逐 rebalance 日決定投組，計算下一期持有報酬
        rebalance_dates = factor_df.index.tolist()
        equity_dates = []
        equity_values = []       # portfolio 淨值
        benchmark_values = []    # 等權重全市場基準淨值
        monthly_returns = []     # 記錄每月報酬，用來算 win_rate

        nav = 1.0
        bench_nav = 1.0

        for i, t in enumerate(rebalance_dates):
            picks = select_picks(factor_df.loc[t], params.direction, params.percentile)
            if not picks:
                continue

            # 持有區間：t 之後的第一個交易日 到 下一個 rebalance 日（含）之間
            start_hold = t
            end_hold = rebalance_dates[i + 1] if i + 1 < len(rebalance_dates) else pd.Timestamp(params.end_date)

            # 取持有期間的日報酬（取所有股票）
            hold_prices = prices.loc[(prices.index > start_hold) & (prices.index <= end_hold)]
            if hold_prices.empty:
                continue

            # 把 t 當天的價格當起點（拼前一列）
            t_prices = prices.loc[prices.index <= start_hold]
            if t_prices.empty:
                continue
            t_close = t_prices.iloc[-1]
            hold_prices = pd.concat([t_close.to_frame().T, hold_prices])

            # 投組：picks 的等權重日報酬
            picks_in_data = [s for s in picks if s in hold_prices.columns]
            if not picks_in_data:
                continue
            picks_prices = hold_prices[picks_in_data].ffill()
            picks_daily_ret = picks_prices.pct_change().dropna(how="all")
            picks_port_ret = picks_daily_ret.mean(axis=1).fillna(0)

            # 基準：全市場等權重
            bench_prices = hold_prices.ffill()
            bench_daily_ret = bench_prices.pct_change().dropna(how="all")
            bench_port_ret = bench_daily_ret.mean(axis=1).fillna(0)

            # 累積淨值
            month_start_nav = nav
            for d, r in picks_port_ret.items():
                nav *= (1.0 + r)
                equity_dates.append(d.date())
                equity_values.append(nav)
            for d, r in bench_port_ret.items():
                bench_nav *= (1.0 + r)
                benchmark_values.append(bench_nav)

            # 本月報酬（for win_rate）
            monthly_returns.append(nav / month_start_nav - 1.0)

        if len(equity_values) < 2:
            raise ValueError("Not enough data points for backtest.")

        # 對齊 equity_values 與 benchmark_values 長度（取較短）
        n = min(len(equity_values), len(benchmark_values))
        equity_dates = equity_dates[:n]
        equity_values = equity_values[:n]
        benchmark_values = benchmark_values[:n]

        # 6. 計算績效指標
        eq = pd.Series(equity_values, index=pd.to_datetime(equity_dates))
        daily_ret = eq.pct_change().dropna()
        total_return = eq.iloc[-1] / eq.iloc[0] - 1.0
        years = (eq.index[-1] - eq.index[0]).days / 365.25
        ann_return = (eq.iloc[-1] / eq.iloc[0]) ** (1 / years) - 1 if years > 0 else 0.0
        ann_vol = daily_ret.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0

        # Max drawdown
        running_max = eq.cummax()
        drawdown = eq / running_max - 1.0
        max_dd = drawdown.min()

        win_rate = np.mean([r > 0 for r in monthly_returns]) if monthly_returns else 0.0

        metrics = BacktestMetrics(
            total_return=float(total_return),
            annualized_return=float(ann_return),
            annualized_vol=float(ann_vol),
            sharpe_ratio=float(sharpe),
            max_drawdown=float(max_dd),
            win_rate=float(win_rate),
            num_rebalances=len(monthly_returns),
        )

        curve = [
            EquityPoint(date=d, portfolio=float(p), benchmark=float(b))
            for d, p, b in zip(equity_dates, equity_values, benchmark_values)
        ]
        # 抽稀到最多 500 個點，前端繪圖比較順
        if len(curve) > 500:
            step = len(curve) // 500
            curve = curve[::step] + [curve[-1]]

        return BacktestResult(params=params, metrics=metrics, equity_curve=curve)
    finally:
        conn.close()


# ==============================================
# 選股（當期）
# ==============================================

def run_screen(params: ParsedParams) -> ScreenResult:
    conn = get_conn()
    try:
        raw_factor = load_factor_matrix(conn, params.factor, params.start_date, params.end_date)
        if raw_factor.empty:
            raise ValueError(f"No factor data for {params.factor}.")

        factor_df = apply_feature(raw_factor, params.feature.type, params.feature.window)
        factor_df = factor_df[factor_df.index >= pd.Timestamp(params.start_date)]
        factor_df = factor_df[factor_df.index <= pd.Timestamp(params.end_date)]
        if factor_df.empty:
            raise ValueError("No data within date range after feature engineering.")

        # 取最新一期
        as_of = factor_df.index[-1]
        row = factor_df.loc[as_of].dropna()
        if row.empty:
            raise ValueError(f"All NaN on {as_of.date()}.")

        ranked = row.sort_values(ascending=(params.direction == "bottom"))
        n = max(1, int(len(ranked) * params.percentile / 100))
        top = ranked.head(n)

        name_map = load_stock_names(conn)
        picks = [
            Pick(
                stock_id=sid,
                stock_name=name_map.get(sid, sid),
                factor_value=float(val),
                rank=rank,
            )
            for rank, (sid, val) in enumerate(top.items(), start=1)
        ]

        return ScreenResult(
            params=params,
            as_of_date=as_of.date(),
            num_selected=len(picks),
            picks=picks,
        )
    finally:
        conn.close()


# ==============================================
# 統一入口
# ==============================================

def run_research(params: ParsedParams) -> ResearchResult:
    if params.mode == "backtest":
        return run_backtest(params)
    elif params.mode == "screen":
        return run_screen(params)
    else:
        raise ValueError(f"Unknown mode: {params.mode}")
