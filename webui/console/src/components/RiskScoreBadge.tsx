import { riskTier, severityStyles } from "@/lib/severity";
import { cn } from "@/lib/utils";

interface RiskScoreBadgeProps {
  score: number;
  size?: "sm" | "md";
  className?: string;
}

export function RiskScoreBadge({
  score,
  size = "sm",
  className,
}: RiskScoreBadgeProps) {
  const tier = riskTier(score);
  const style = severityStyles[tier];
  return (
    <span
      title={`Risk score ${score}/100 (${style.label})`}
      className={cn(
        "inline-flex items-center gap-1 rounded-sm border font-bold tabular-nums",
        style.soft,
        style.border,
        size === "sm" ? "px-1.5 py-0.5 text-[11px]" : "px-2 py-1 text-sm",
        className,
      )}
    >
      <span className="opacity-60">RISK</span>
      {score}
    </span>
  );
}
