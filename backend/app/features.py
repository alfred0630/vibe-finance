"""特徵工程模組

所有函式的輸入/輸出都是 pandas DataFrame：
- index: DatetimeIndex（月底日期）
- columns: stock_id (str)
- values: float，NaN 代表當時沒有該檔資料
"""
import pandas as pd
import numpy as np


def apply_feature(df: pd.DataFrame, feature_type: str, window: int = 12) -> pd.DataFrame:
    """統一入口：根據 feature_type 呼叫對應函式。"""
    if feature_type == "none":
        return df.copy()
    elif feature_type == "growth_rate":
        return growth_rate(df, window)
    elif feature_type == "zscore":
        return zscore(df, window)
    elif feature_type == "momentum":
        return momentum(df, window)
    else:
        raise ValueError(f"Unknown feature type: {feature_type}")


def growth_rate(df: pd.DataFrame, window: int = 12) -> pd.DataFrame:
    """時序成長率 = (x_t - x_{t-window}) / |x_{t-window}|

    用 abs 處理分母負值（如 EPS 從 -1 到 1 應該算成長，不是衰退）。
    避免除以零：分母絕對值 < 1e-6 時設為 NaN。
    """
    prev = df.shift(window)
    denom = prev.abs()
    denom = denom.where(denom > 1e-6)  # 太小的分母當 NaN
    return (df - prev) / denom


def zscore(df: pd.DataFrame, window: int = 12) -> pd.DataFrame:
    """時序 rolling z-score = (x_t - rolling_mean) / rolling_std

    每檔股票獨立計算自己的時序 z-score。
    """
    rolling_mean = df.rolling(window=window, min_periods=max(2, window // 2)).mean()
    rolling_std = df.rolling(window=window, min_periods=max(2, window // 2)).std()
    rolling_std = rolling_std.where(rolling_std > 1e-6)
    return (df - rolling_mean) / rolling_std


def momentum(df: pd.DataFrame, window: int = 12) -> pd.DataFrame:
    """動能 = 最近 window 期的平均變動率

    對於單調因子（如 pe）這代表最近 N 期的平均變化。
    對於成長類因子（revenue_growth）這代表最近 N 期的平均成長動能。
    用 pct_change 加總後取平均。
    """
    pct = df.pct_change()
    return pct.rolling(window=window, min_periods=max(2, window // 2)).mean()
