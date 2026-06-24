import {
  Activity,
  BadgeCheck,
  Clock,
  Flame,
  ScanSearch,
  ShieldAlert,
} from "lucide-react";
import type { DashboardMetrics } from "@/types";
import { KpiCard } from "./KpiCard";

export function KpiGrid({ metrics }: { metrics: DashboardMetrics }) {
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-6">
      <KpiCard
        label="Total Scanned"
        value={metrics.totalScanned}
        icon={ScanSearch}
        accent="var(--accent-slate)"
      />
      <KpiCard
        label="Critical"
        value={metrics.critical}
        icon={Flame}
        trend={metrics.trend.critical}
        invertTrend
        accent="var(--sev-critical)"
      />
      <KpiCard
        label="High"
        value={metrics.high}
        icon={ShieldAlert}
        trend={metrics.trend.high}
        invertTrend
        accent="var(--sev-high)"
      />
      <KpiCard
        label="Auto-Remediation"
        value={metrics.autoRemediationRate}
        suffix="%"
        icon={BadgeCheck}
        trend={metrics.trend.autoRemediationRate}
        accent="var(--accent-sage)"
      />
      <KpiCard
        label="Pending Reviews"
        value={metrics.pendingReviews}
        icon={Activity}
        trend={metrics.trend.pendingReviews}
        invertTrend
        accent="var(--accent-sand)"
      />
      <KpiCard
        label="MTTR"
        value={metrics.meanTimeToRemediateHours}
        suffix="h"
        icon={Clock}
        accent="var(--accent-slate)"
      />
    </div>
  );
}
