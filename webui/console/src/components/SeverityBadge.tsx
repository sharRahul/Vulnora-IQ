import { ShieldAlert } from "lucide-react";
import type { Severity } from "@/types";
import { severityStyles } from "@/lib/severity";
import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  severity: Severity;
  withIcon?: boolean;
  className?: string;
}

export function SeverityBadge({
  severity,
  withIcon = false,
  className,
}: SeverityBadgeProps) {
  const style = severityStyles[severity];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-sm px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide",
        style.solid,
        className,
      )}
    >
      {withIcon && <ShieldAlert className="size-3" />}
      {style.label}
    </span>
  );
}
