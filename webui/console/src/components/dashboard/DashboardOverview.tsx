import { PieChart, TrendingDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type {
  DashboardMetrics,
  SeverityDistributionPoint,
  VulnerabilityTrendPoint,
} from "@/types";
import { BurnDownChart } from "./BurnDownChart";
import { KpiGrid } from "./KpiGrid";
import { SeverityDonutChart } from "./SeverityDonutChart";
import { SkeletonDashboard } from "./SkeletonDashboard";

interface DashboardOverviewProps {
  metrics: DashboardMetrics;
  trend: VulnerabilityTrendPoint[];
  distribution: SeverityDistributionPoint[];
  loading?: boolean;
}

export function DashboardOverview({
  metrics,
  trend,
  distribution,
  loading = false,
}: DashboardOverviewProps) {
  if (loading) return <SkeletonDashboard />;

  return (
    <div className="space-y-4 animate-fade-in">
      <div>
        <h2 className="font-sans text-lg font-extrabold tracking-tight text-foreground">
          AI Security Posture
        </h2>
        <p className="text-sm text-muted-foreground">
          Executive overview across repositories, images, agents, and RAG systems.
        </p>
      </div>

      <KpiGrid metrics={metrics} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="size-4 text-[var(--accent-slate)]" />
              Vulnerability Burn-down Rate
            </CardTitle>
            <span className="text-xs text-muted-foreground">Last 7 days</span>
          </CardHeader>
          <CardContent>
            <div className="h-[220px] w-full">
              <BurnDownChart data={trend} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="size-4 text-[var(--accent-slate)]" />
              Severity Distribution
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[220px]">
            <SeverityDonutChart data={distribution} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
