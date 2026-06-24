import { ArrowDownRight, ArrowUpRight, Minus, type LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  /** Positive/negative delta vs. previous period. */
  trend?: number;
  /** When true, a downward trend is good (e.g. critical count, pending). */
  invertTrend?: boolean;
  accent?: string;
  suffix?: string;
}

export function KpiCard({
  label,
  value,
  icon: Icon,
  trend,
  invertTrend = false,
  accent = "var(--accent-slate)",
  suffix,
}: KpiCardProps) {
  const hasTrend = typeof trend === "number" && trend !== 0;
  const positive = hasTrend ? (invertTrend ? trend! < 0 : trend! > 0) : false;
  const TrendIcon = !hasTrend ? Minus : trend! > 0 ? ArrowUpRight : ArrowDownRight;

  return (
    <Card className="group p-4 transition-shadow hover:shadow-card-hover">
      <div className="flex items-start justify-between">
        <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {label}
        </span>
        <span
          className="flex size-8 items-center justify-center rounded-md border border-border"
          style={{ color: accent, background: `color-mix(in srgb, ${accent} 12%, transparent)` }}
        >
          <Icon className="size-4" />
        </span>
      </div>
      <div className="mt-3 flex items-end gap-2">
        <span className="font-sans text-3xl font-extrabold leading-none tabular-nums text-foreground">
          {value}
          {suffix && <span className="text-lg font-bold text-muted-foreground">{suffix}</span>}
        </span>
        {hasTrend && (
          <span
            className={cn(
              "mb-0.5 inline-flex items-center gap-0.5 text-xs font-bold tabular-nums",
              positive ? "text-severity-low" : "text-severity-high",
            )}
          >
            <TrendIcon className="size-3" />
            {Math.abs(trend!)}
            {suffix === "%" ? "pts" : ""}
          </span>
        )}
      </div>
    </Card>
  );
}
