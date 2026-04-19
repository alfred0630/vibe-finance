"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { MetricCard } from "./MetricCard";
import type { BacktestResult } from "@/lib/types";

const pct = (x: number) => `${(x * 100).toFixed(1)}%`;
const num = (x: number, d = 2) => x.toFixed(d);

interface Props {
  result: BacktestResult;
}

export function BacktestView({ result }: Props) {
  const { metrics, equity_curve } = result;

  const data = equity_curve.map((p) => ({
    date: p.date,
    portfolio: p.portfolio,
    benchmark: p.benchmark,
  }));

  return (
    <div className="flex flex-col gap-5 h-full">
      {/* Metric cards */}
      <div className="grid grid-cols-3 gap-3">
        <MetricCard
          label="Total Return"
          value={pct(metrics.total_return)}
          tone={metrics.total_return >= 0 ? "positive" : "negative"}
          hint="累計報酬"
        />
        <MetricCard
          label="Annualized Return"
          value={pct(metrics.annualized_return)}
          tone={metrics.annualized_return >= 0 ? "positive" : "negative"}
          hint="年化報酬"
        />
        <MetricCard
          label="Sharpe Ratio"
          value={num(metrics.sharpe_ratio)}
          tone="primary"
          hint="風險調整後報酬"
        />
        <MetricCard
          label="Annualized Vol"
          value={pct(metrics.annualized_vol)}
          hint="年化波動"
        />
        <MetricCard
          label="Max Drawdown"
          value={pct(metrics.max_drawdown)}
          tone="negative"
          hint="歷史最大回撤"
        />
        <MetricCard
          label="Win Rate"
          value={pct(metrics.win_rate)}
          hint={`共 ${metrics.num_rebalances} 次 rebalance`}
        />
      </div>

      {/* Equity curve */}
      <div className="flex-1 rounded-md bg-background/30 border border-border/40 p-4 flex flex-col min-h-[320px]">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground font-medium">
              Equity Curve
            </div>
            <div className="text-[10px] text-muted-foreground/70">
              起始淨值 = 1.0 · 基準為全市場等權重
            </div>
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-[2px] bg-primary" />
              <span className="text-muted-foreground">Portfolio</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-4 border-t-2 border-dashed border-muted-foreground/50" />
              <span className="text-muted-foreground">Benchmark</span>
            </div>
          </div>
        </div>
        <div className="flex-1 min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -10 }}>
              <CartesianGrid stroke="rgba(148,163,184,0.08)" strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{ fill: "rgb(148 163 184)", fontSize: 10 }}
                tickFormatter={(v: string) => v.slice(0, 7)}
                minTickGap={60}
                stroke="rgba(148,163,184,0.2)"
              />
              <YAxis
                tick={{ fill: "rgb(148 163 184)", fontSize: 10 }}
                stroke="rgba(148,163,184,0.2)"
                width={48}
                tickFormatter={(v: number) => v.toFixed(2)}
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length) return null;
                  return (
                    <div style={{
                      backgroundColor: "rgba(15,23,42,0.95)",
                      border: "1px solid rgba(148,163,184,0.2)",
                      borderRadius: 6,
                      fontSize: 11,
                      padding: "8px 10px",
                    }}>
                      <p style={{ color: "rgb(226 232 240)", marginBottom: 4 }}>{String(label).slice(0, 7)}</p>
                      {payload.map((entry) => (
                        <p key={entry.dataKey as string} style={{ color: entry.color, margin: "2px 0" }}>
                          {entry.dataKey === "portfolio" ? "Portfolio" : "Benchmark"}: {Number(entry.value).toFixed(4)}
                        </p>
                      ))}
                    </div>
                  );
                }}
              />
              <Line
                type="monotone"
                dataKey="portfolio"
                stroke="hsl(160 84% 45%)"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="benchmark"
                stroke="rgb(148 163 184)"
                strokeWidth={1}
                strokeDasharray="4 3"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
