interface Props {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "positive" | "negative" | "primary";
}

export function MetricCard({ label, value, hint, tone = "default" }: Props) {
  const toneClass = {
    default: "text-foreground",
    positive: "text-emerald-400",
    negative: "text-red-400",
    primary: "text-primary",
  }[tone];

  return (
    <div className="rounded-md bg-background/30 border border-border/40 p-3 flex flex-col gap-1">
      <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">
        {label}
      </span>
      <span className={`font-mono-num text-xl font-medium tabular-nums ${toneClass}`}>
        {value}
      </span>
      {hint && (
        <span className="text-[10px] text-muted-foreground/70">{hint}</span>
      )}
    </div>
  );
}
