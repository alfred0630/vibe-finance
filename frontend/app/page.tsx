"use client";

import { useState } from "react";
import { QueryInput } from "@/components/QueryInput";
import { ParamsPanel } from "@/components/ParamsPanel";
import { BacktestView } from "@/components/BacktestView";
import { ScreenView } from "@/components/ScreenView";
import { parseQuery, runResearch } from "@/lib/api";
import type { ParsedParams, ResearchResult } from "@/lib/types";

export default function Home() {
  const [parsed, setParsed] = useState<ParsedParams | null>(null);
  const [explanation, setExplanation] = useState<string>("");
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [parsing, setParsing] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleParse = async (query: string) => {
    setParsing(true);
    setError(null);
    try {
      const r = await parseQuery(query);
      setParsed(r.params);
      setExplanation(r.explanation);
      setResult(null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setParsing(false);
    }
  };

  const handleResearch = async (params: ParsedParams) => {
    setRunning(true);
    setError(null);
    try {
      const r = await runResearch(params);
      setResult(r);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-background subtle-grid">
      <header className="border-b border-border/40 bg-background/80 backdrop-blur">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-primary/20 border border-primary/40 flex items-center justify-center">
              <div className="w-3 h-3 rounded-sm bg-primary" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">Vibe Finance</h1>
              <p className="text-xs text-muted-foreground">Chill quant research for people who don&apos;t speak Python</p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              API Connected
            </div>
            <span>506 stocks · 2003–2026</span>
          </div>
        </div>
      </header>

      <main className="max-w-[1600px] mx-auto px-6 py-6">
        {error && (
          <div className="mb-4 rounded-md bg-destructive/10 border border-destructive/40 px-3 py-2 text-xs text-destructive">
            {error}
          </div>
        )}

        <div className="grid grid-cols-12 gap-6" style={{ minHeight: "calc(100vh - 160px)" }}>
          {/* Left column */}
          <div className="col-span-12 lg:col-span-5 flex flex-col gap-6">
            <section className="glass-card rounded-lg p-5">
              <QueryInput onSubmit={handleParse} loading={parsing} />
            </section>

            <section className="glass-card rounded-lg p-5 flex-1 overflow-y-auto">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Parsed Parameters
                </span>
                {parsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/15 text-primary border border-primary/30">
                    可編輯
                  </span>
                )}
              </div>
              <ParamsPanel
                params={parsed}
                explanation={explanation}
                onRunResearch={handleResearch}
                running={running}
              />
            </section>
          </div>

          {/* Right column */}
          <div className="col-span-12 lg:col-span-7 flex flex-col gap-6">
            <section className="glass-card rounded-lg p-5 flex-1 min-h-[600px] flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Research Result
                </span>
                {result && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-primary/15 text-primary border border-primary/30 font-mono-num">
                    {result.mode.toUpperCase()}
                  </span>
                )}
              </div>

              <div className="flex-1 min-h-0">
                {running ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="flex flex-col items-center gap-3 text-muted-foreground">
                      <div className="relative">
                        <div className="w-10 h-10 rounded-full border-2 border-border/40" />
                        <div className="absolute inset-0 w-10 h-10 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                      </div>
                      <span className="text-xs">執行因子研究中...</span>
                    </div>
                  </div>
                ) : !result ? (
                  <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-sm gap-2">
                    <span>輸入查詢並執行研究後，結果會顯示在這裡</span>
                    <span className="text-[11px] text-muted-foreground/60">
                      回測將顯示績效指標與淨值曲線，選股將顯示當期清單
                    </span>
                  </div>
                ) : result.mode === "backtest" ? (
                  <BacktestView result={result} />
                ) : (
                  <ScreenView result={result} />
                )}
              </div>
            </section>
          </div>
        </div>

        <footer className="mt-8 pt-4 border-t border-border/40 flex items-center justify-between text-xs text-muted-foreground">
          <span>Powered by Gemini 2.5 Flash · FastAPI · DuckDB</span>
          <span className="font-mono-num">v0.1.0</span>
        </footer>
      </main>
    </div>
  );
}
