"use client";

import { useState } from "react";
import { ArrowUpDown, TrendingUp, Hash, Building2 } from "lucide-react";
import type { ScreenResult } from "@/lib/types";

const num = (x: number, d = 2) => x.toFixed(d);
const pct = (x: number) => `${(x * 100).toFixed(1)}%`;

interface Props {
  result: ScreenResult;
}

type SortKey = "rank" | "stock_id" | "factor_value";

export function ScreenView({ result }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("rank");
  const [sortDesc, setSortDesc] = useState(false);

  const sorted = [...result.picks].sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    if (typeof av === "string" && typeof bv === "string") {
      return sortDesc ? bv.localeCompare(av) : av.localeCompare(bv);
    }
    return sortDesc ? (bv as number) - (av as number) : (av as number) - (bv as number);
  });

  const toggleSort = (k: SortKey) => {
    if (k === sortKey) setSortDesc(!sortDesc);
    else { setSortKey(k); setSortDesc(false); }
  };

  const isRatio = result.params.feature.type === "growth_rate" || result.params.feature.type === "momentum";
  const formatFactor = (v: number) => isRatio ? pct(v) : num(v);

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* 摘要列 */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-md bg-background/30 border border-border/40 p-3 flex items-center gap-3">
          <Hash className="w-4 h-4 text-primary" />
          <div>
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Selected</div>
            <div className="font-mono-num text-lg text-primary">{result.num_selected}</div>
          </div>
        </div>
        <div className="rounded-md bg-background/30 border border-border/40 p-3 flex items-center gap-3">
          <TrendingUp className="w-4 h-4 text-muted-foreground" />
          <div>
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Top factor</div>
            <div className="font-mono-num text-sm text-foreground">
              {formatFactor(sorted[0]?.factor_value ?? 0)}
            </div>
          </div>
        </div>
        <div className="rounded-md bg-background/30 border border-border/40 p-3 flex items-center gap-3">
          <Building2 className="w-4 h-4 text-muted-foreground" />
          <div>
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground">As of</div>
            <div className="font-mono-num text-sm text-foreground">{result.as_of_date}</div>
          </div>
        </div>
      </div>

      {/* 表格 */}
      <div className="flex-1 rounded-md bg-background/30 border border-border/40 overflow-hidden flex flex-col min-h-0">
        <div className="overflow-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-background/80 backdrop-blur z-10 border-b border-border/40">
              <tr className="text-[10px] uppercase tracking-wider text-muted-foreground">
                <Th onClick={() => toggleSort("rank")} active={sortKey === "rank"}>#</Th>
                <Th onClick={() => toggleSort("stock_id")} active={sortKey === "stock_id"}>代碼</Th>
                <th className="text-left px-3 py-2.5 font-medium">名稱</th>
                <Th onClick={() => toggleSort("factor_value")} active={sortKey === "factor_value"} align="right">
                  因子值
                </Th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((p) => (
                <tr
                  key={p.stock_id}
                  className="border-b border-border/20 hover:bg-accent/30 transition-colors"
                >
                  <td className="px-3 py-2 text-muted-foreground font-mono-num">{p.rank}</td>
                  <td className="px-3 py-2 font-mono-num text-foreground">{p.stock_id}</td>
                  <td className="px-3 py-2 text-foreground">{p.stock_name}</td>
                  <td className="px-3 py-2 text-right font-mono-num text-primary">
                    {formatFactor(p.factor_value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Th({
  children, onClick, active, align = "left",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  active?: boolean;
  align?: "left" | "right";
}) {
  return (
    <th
      onClick={onClick}
      className={`px-3 py-2.5 font-medium cursor-pointer select-none ${
        align === "right" ? "text-right" : "text-left"
      } ${active ? "text-primary" : "hover:text-foreground"}`}
    >
      <span className="inline-flex items-center gap-1">
        {children}
        {onClick && <ArrowUpDown className="w-3 h-3 opacity-50" />}
      </span>
    </th>
  );
}
