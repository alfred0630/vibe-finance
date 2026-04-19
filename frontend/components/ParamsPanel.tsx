"use client";

import { useState, useEffect } from "react";
import {
  Sparkles, Play, Loader2, TrendingUp, TrendingDown,
  FlaskConical, Calendar, Percent, Target, Zap,
} from "lucide-react";
import {
  ParsedParams, FactorName, FeatureType, Direction, Mode,
  FACTOR_LABELS, FEATURE_LABELS, DIRECTION_LABELS, MODE_LABELS,
} from "@/lib/types";

interface Props {
  params: ParsedParams | null;
  explanation: string;
  onRunResearch: (params: ParsedParams) => void;
  running: boolean;
}

export function ParamsPanel({ params, explanation, onRunResearch, running }: Props) {
  const [local, setLocal] = useState<ParsedParams | null>(params);

  useEffect(() => {
    setLocal(params);
  }, [params]);

  if (!local) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 text-center">
        <div className="w-12 h-12 rounded-full bg-secondary/40 border border-border/40 flex items-center justify-center mb-3">
          <FlaskConical className="w-5 h-5 text-muted-foreground/60" />
        </div>
        <p className="text-sm text-muted-foreground">
          輸入自然語言查詢後，解析出的參數會顯示在這裡
        </p>
        <p className="text-xs text-muted-foreground/60 mt-1">
          每個參數都可手動編輯，確保執行前可驗證
        </p>
      </div>
    );
  }

  const update = <K extends keyof ParsedParams>(k: K, v: ParsedParams[K]) =>
    setLocal({ ...local, [k]: v });

  return (
    <div className="flex flex-col gap-4">
      {/* Gemini explanation */}
      {explanation && (
        <div className="rounded-md bg-primary/5 border border-primary/20 px-3 py-2 flex gap-2">
          <Sparkles className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
          <p className="text-xs text-foreground/80 leading-relaxed">{explanation}</p>
        </div>
      )}

      {/* Mode */}
      <ParamCard icon={<Target className="w-3.5 h-3.5" />} label="Mode · 研究模式">
        <div className="grid grid-cols-2 gap-1.5">
          {(["backtest", "screen"] as Mode[]).map((m) => (
            <ToggleButton
              key={m}
              active={local.mode === m}
              onClick={() => update("mode", m)}
            >
              {MODE_LABELS[m]}
            </ToggleButton>
          ))}
        </div>
      </ParamCard>

      {/* Factor */}
      <ParamCard icon={<FlaskConical className="w-3.5 h-3.5" />} label="Factor · 因子">
        <div className="grid grid-cols-2 gap-1.5">
          {(["eps", "revenue_growth", "pe", "pb"] as FactorName[]).map((f) => (
            <ToggleButton
              key={f}
              active={local.factor === f}
              onClick={() => update("factor", f)}
            >
              {FACTOR_LABELS[f]}
            </ToggleButton>
          ))}
        </div>
      </ParamCard>

      {/* Direction + Percentile */}
      <div className="grid grid-cols-2 gap-3">
        <ParamCard
          icon={local.direction === "top"
            ? <TrendingUp className="w-3.5 h-3.5" />
            : <TrendingDown className="w-3.5 h-3.5" />}
          label="Direction"
        >
          <div className="grid grid-cols-2 gap-1.5">
            {(["top", "bottom"] as Direction[]).map((d) => (
              <ToggleButton
                key={d}
                active={local.direction === d}
                onClick={() => update("direction", d)}
              >
                {d === "top" ? "高" : "低"}
              </ToggleButton>
            ))}
          </div>
        </ParamCard>

        <ParamCard icon={<Percent className="w-3.5 h-3.5" />} label="Percentile">
          <div className="flex items-center gap-2">
            <input
              type="range"
              min={1}
              max={50}
              step={1}
              value={local.percentile}
              onChange={(e) => update("percentile", Number(e.target.value))}
              className="flex-1 accent-primary"
            />
            <span className="font-mono-num text-sm tabular-nums w-12 text-right text-primary">
              {local.percentile.toFixed(0)}%
            </span>
          </div>
        </ParamCard>
      </div>

      {/* Feature */}
      <ParamCard icon={<Zap className="w-3.5 h-3.5" />} label="Feature Engineering">
        <div className="grid grid-cols-4 gap-1.5">
          {(["none", "growth_rate", "zscore", "momentum"] as FeatureType[]).map((t) => (
            <ToggleButton
              key={t}
              active={local.feature.type === t}
              onClick={() => update("feature", { ...local.feature, type: t })}
            >
              {FEATURE_LABELS[t]}
            </ToggleButton>
          ))}
        </div>
        {local.feature.type !== "none" && (
          <div className="flex items-center gap-2 mt-2">
            <span className="text-[11px] text-muted-foreground">Window</span>
            <input
              type="number"
              min={1}
              max={60}
              value={local.feature.window}
              onChange={(e) =>
                update("feature", { ...local.feature, window: Number(e.target.value) })
              }
              className="font-mono-num w-16 bg-background/60 border border-border/60 rounded px-2 py-0.5 text-xs text-right focus:outline-none focus:border-primary/60"
            />
            <span className="text-[11px] text-muted-foreground">months</span>
          </div>
        )}
      </ParamCard>

      {/* Date range */}
      <ParamCard icon={<Calendar className="w-3.5 h-3.5" />} label="Date Range">
        <div className="grid grid-cols-2 gap-2">
          <input
            type="date"
            value={local.start_date}
            onChange={(e) => update("start_date", e.target.value)}
            className="font-mono-num bg-background/60 border border-border/60 rounded px-2 py-1 text-xs focus:outline-none focus:border-primary/60"
          />
          <input
            type="date"
            value={local.end_date}
            onChange={(e) => update("end_date", e.target.value)}
            className="font-mono-num bg-background/60 border border-border/60 rounded px-2 py-1 text-xs focus:outline-none focus:border-primary/60"
          />
        </div>
      </ParamCard>

      {/* Execute button */}
      <button
        onClick={() => onRunResearch(local)}
        disabled={running}
        className="mt-1 inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
      >
        {running ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            運算中...
          </>
        ) : (
          <>
            <Play className="w-4 h-4" />
            執行研究
          </>
        )}
      </button>
    </div>
  );
}

function ParamCard({
  icon,
  label,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-md bg-background/30 border border-border/40 p-3">
      <div className="flex items-center gap-1.5 mb-2 text-muted-foreground">
        {icon}
        <span className="text-[10px] uppercase tracking-wider font-medium">{label}</span>
      </div>
      {children}
    </div>
  );
}

function ToggleButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`text-[11px] px-2 py-1.5 rounded border transition-all ${
        active
          ? "bg-primary/15 border-primary/50 text-primary"
          : "bg-background/40 border-border/40 text-muted-foreground hover:text-foreground hover:border-border"
      }`}
    >
      {children}
    </button>
  );
}
