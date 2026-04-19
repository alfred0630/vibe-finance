export type Mode = "backtest" | "screen";
export type FactorName = "eps" | "revenue_growth" | "pe" | "pb";
export type FeatureType = "none" | "growth_rate" | "zscore" | "momentum";
export type Direction = "top" | "bottom";

export interface FeatureConfig {
  type: FeatureType;
  window: number;
}

export interface ParsedParams {
  mode: Mode;
  factor: FactorName;
  feature: FeatureConfig;
  direction: Direction;
  percentile: number;
  start_date: string;
  end_date: string;
  rebalance: "monthly";
}

export interface ParseResponse {
  params: ParsedParams;
  explanation: string;
}

export interface BacktestMetrics {
  total_return: number;
  annualized_return: number;
  annualized_vol: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  num_rebalances: number;
}

export interface EquityPoint {
  date: string;
  portfolio: number;
  benchmark: number;
}

export interface BacktestResult {
  mode: "backtest";
  params: ParsedParams;
  metrics: BacktestMetrics;
  equity_curve: EquityPoint[];
}

export interface Pick {
  stock_id: string;
  stock_name: string;
  factor_value: number;
  rank: number;
}

export interface ScreenResult {
  mode: "screen";
  params: ParsedParams;
  as_of_date: string;
  num_selected: number;
  picks: Pick[];
}

export type ResearchResult = BacktestResult | ScreenResult;

// UI label maps
export const FACTOR_LABELS: Record<FactorName, string> = {
  eps: "EPS 每股盈餘",
  revenue_growth: "營收年增率",
  pe: "PE 本益比",
  pb: "PB 股價淨值比",
};

export const FEATURE_LABELS: Record<FeatureType, string> = {
  none: "原始值",
  growth_rate: "成長率",
  zscore: "Z-Score",
  momentum: "動能",
};

export const DIRECTION_LABELS: Record<Direction, string> = {
  top: "前段 (最高)",
  bottom: "後段 (最低)",
};

export const MODE_LABELS: Record<Mode, string> = {
  backtest: "歷史回測",
  screen: "當期選股",
};
