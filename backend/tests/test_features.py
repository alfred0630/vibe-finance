"""pytest tests/test_features.py"""
import pandas as pd
import numpy as np
import pytest
from app.features import apply_feature, growth_rate, zscore, momentum


@pytest.fixture
def sample_df():
    """3 個月 × 2 檔股票的小測試資料。"""
    dates = pd.date_range("2024-01-31", periods=12, freq="ME")
    return pd.DataFrame({
        "A": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1],
        "B": [10.0, 9.0, 10.0, 11.0, 10.0, 9.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0],
    }, index=dates)


def test_none_returns_copy(sample_df):
    result = apply_feature(sample_df, "none")
    pd.testing.assert_frame_equal(result, sample_df)
    assert result is not sample_df  # 是 copy


def test_growth_rate_basic(sample_df):
    result = growth_rate(sample_df, window=1)
    # 第 0 列應為 NaN（沒有前值）
    assert result.iloc[0].isna().all()
    # A: (1.1 - 1.0) / 1.0 = 0.1
    assert result.iloc[1]["A"] == pytest.approx(0.1)
    # B: (9.0 - 10.0) / 10.0 = -0.1
    assert result.iloc[1]["B"] == pytest.approx(-0.1)


def test_growth_rate_handles_negative_denom():
    df = pd.DataFrame({"X": [-2.0, -1.0, 0.5]}, index=pd.date_range("2024-01-31", periods=3, freq="ME"))
    result = growth_rate(df, window=1)
    # (-1 - (-2)) / |-2| = 0.5
    assert result.iloc[1]["X"] == pytest.approx(0.5)


def test_zscore_window(sample_df):
    result = zscore(sample_df, window=3)
    # 前兩列應該是 NaN 或近似（min_periods 設為 window//2 = 1）
    # 第 2 列開始有足夠資料，應為有限值
    assert result.iloc[3:]["A"].notna().all()


def test_momentum(sample_df):
    result = momentum(sample_df, window=3)
    assert result.iloc[-1]["A"] > 0  # A 持續上漲，動能為正
    assert isinstance(result.iloc[-1]["A"], float)


def test_unknown_feature_raises(sample_df):
    with pytest.raises(ValueError, match="Unknown"):
        apply_feature(sample_df, "bogus")
