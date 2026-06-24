import { riskTier, severityStyles } from "@/lib/severity";
import { cn } from "@/lib/utils";

/** Maps a CVSS base score (0–10) to the severity palette. */
function cvssTier(score: number) {
  if (score >= 9) return "critical";
  if (score >= 7) return "high";
  if (score >= 4) return "medium";
  if (score > 0) return "low";
  return "info";
}

export function CvssBadge({
  score,
  className,
}: {
  score: number;
  className?: string;
}) {
  const style = severityStyles[cvssTier(score) as ReturnType<typeof riskTier>];
  return (
    <span
      className={cn(
        "inline-flex items-baseline gap-1 rounded-md border px-2 py-1 font-bold tabular-nums",
        style.soft,
        style.border,
        className,
      )}
      title={`CVSS base score ${score} (${style.label})`}
    >
      <span className="text-base leading-none">{score.toFixed(1)}</span>
      <span className="text-[10px] uppercase opacity-70">CVSS</span>
    </span>
  );
}
