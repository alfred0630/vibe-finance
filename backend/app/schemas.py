from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ==============================================
# 使用者的自然語言查詢 → Gemini 解析的參數
# ==============================================

FactorName = Literal["eps", "revenue_growth", "pe", "pb"]
FeatureType = Literal["none", "growth_rate", "zscore", "momentum"]
Mode = Literal["backtest", "screen"]
Direction = Literal["top", "bottom"]


class FeatureConfig(BaseModel):
    type: FeatureType = "none"
    window: int = Field(default=12, ge=1, le=60, description="特徵工程的 lookback window（月）")


class ParsedParams(BaseModel):
    """Gemini 從自然語言解析出的結構化參數。這就是前端參數面板要顯示的內容。"""
    mode: Mode = Field(description="backtest 回測 or screen 當期選股")
    factor: FactorName = Field(description="要研究的因子")
    feature: FeatureConfig = Field(default_factory=FeatureConfig)
    direction: Direction = Field(description="top 挑因子值最高的 (買強); bottom 挑最低的 (買便宜)")
    percentile: float = Field(default=20.0, ge=1.0, le=50.0, description="取前/後 x% 作為投組")
    start_date: date = Field(default=date(2015, 1, 1))
    end_date: date = Field(default=date(2025, 12, 31))
    rebalance: Literal["monthly"] = "monthly"  # 目前只支援月頻 rebalance


# ==============================================
# API request / response
# ==============================================

class ParseRequest(BaseModel):
    query: str = Field(description="使用者的自然語言問題")


class ParseResponse(BaseModel):
    params: ParsedParams
    explanation: str = Field(description="Gemini 給的簡短中文解釋，顯示在 UI 上增加可信度")


class ResearchRequest(BaseModel):
    params: ParsedParams


class BacktestMetrics(BaseModel):
    total_return: float        # 累計報酬
    annualized_return: float   # 年化報酬
    annualized_vol: float      # 年化波動
    sharpe_ratio: float        # 無風險利率視為 0
    max_drawdown: float        # 最大回撤 (負值)
    win_rate: float            # 月勝率
    num_rebalances: int


class EquityPoint(BaseModel):
    date: date
    portfolio: float           # 投組淨值（起始 = 1）
    benchmark: float           # 等權重全市場基準（起始 = 1）


class BacktestResult(BaseModel):
    mode: Literal["backtest"] = "backtest"
    params: ParsedParams
    metrics: BacktestMetrics
    equity_curve: list[EquityPoint]


class Pick(BaseModel):
    stock_id: str
    stock_name: str
    factor_value: float        # 該股當期的因子值
    rank: int                  # 在當期排名


class ScreenResult(BaseModel):
    mode: Literal["screen"] = "screen"
    params: ParsedParams
    as_of_date: date           # 選股基準日
    num_selected: int
    picks: list[Pick]


# Union type for the /research endpoint response
ResearchResult = BacktestResult | ScreenResult
