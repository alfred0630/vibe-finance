"use client";

import { useState } from "react";
import { Send, Sparkles, Loader2 } from "lucide-react";

const EXAMPLES = [
  "回測低 PE 前 20% 的策略",
  "現在 EPS 成長率最高的前 30 檔",
  "PB 最低的前 10% 股票現在是哪些",
  "最近營收動能最強的公司",
];

interface Props {
  onSubmit: (query: string) => void;
  loading: boolean;
}

export function QueryInput({ onSubmit, loading }: Props) {
  const [text, setText] = useState("");

  const handleSubmit = () => {
    const q = text.trim();
    if (!q || loading) return;
    onSubmit(q);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-primary" />
          <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Natural Language Query
          </span>
        </div>
        <span className="text-[10px] text-muted-foreground">
          ⌘/Ctrl + ↵ 送出
        </span>
      </div>

      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="用中文描述你想做的研究，例如：「幫我找 EPS 成長率最高的前 20% 股票回測」"
          rows={3}
          className="w-full resize-none rounded-md bg-background/50 border border-border/60 px-3 py-2.5 text-sm focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/40 placeholder:text-muted-foreground/50"
          disabled={loading}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !text.trim()}
          className="absolute bottom-2.5 right-2.5 inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
        >
          {loading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              解析中
            </>
          ) : (
            <>
              <Send className="w-3.5 h-3.5" />
              執行
            </>
          )}
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => setText(ex)}
            disabled={loading}
            className="text-[11px] px-2.5 py-1 rounded-full bg-secondary/60 border border-border/40 text-muted-foreground hover:text-foreground hover:border-border transition-colors disabled:opacity-40"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  );
}
