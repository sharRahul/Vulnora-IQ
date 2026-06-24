import { useEffect, useMemo, useState } from "react";
import { MousePointerSquareDashed, ScanSearch } from "lucide-react";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ToastProvider, useToast } from "@/components/ui/toast";
import { AppShell } from "@/components/AppShell";
import type { ConsoleView } from "@/components/HeaderBar";
import { WorkspaceLayout } from "@/components/WorkspaceLayout";
import { EmptyState } from "@/components/EmptyState";
import { DashboardOverview } from "@/components/dashboard/DashboardOverview";
import { AssetNavigationPane } from "@/components/navigation/AssetNavigationPane";
import { AnalysisWorkspace } from "@/components/workspace/AnalysisWorkspace";
import { IntelligencePanel } from "@/components/intelligence/IntelligencePanel";
import { TargetsManager } from "@/components/targets/TargetsManager";
import { useTheme } from "@/hooks/useTheme";
import {
  assets,
  dashboardMetrics,
  findings,
  severityDistribution,
  trendData,
} from "@/data/mock";
import type { Finding } from "@/types";

function ConsoleInner() {
  const { theme, toggleTheme } = useTheme();
  const { notify } = useToast();

  const [view, setView] = useState<ConsoleView>("overview");
  const [selectedFindingId, setSelectedFindingId] = useState<string | null>(null);
  const [appliedFindingIds, setAppliedFindingIds] = useState<Set<string>>(new Set());
  const [scanning, setScanning] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(true);

  const findingsById = useMemo<Record<string, Finding>>(
    () => Object.fromEntries(findings.map((f) => [f.id, f])),
    [],
  );

  // Initial dashboard load — skeleton then data.
  useEffect(() => {
    const t = window.setTimeout(() => setDashboardLoading(false), 900);
    return () => window.clearTimeout(t);
  }, []);

  const selectedFinding = selectedFindingId ? findingsById[selectedFindingId] : null;
  const selectedAsset = selectedFinding
    ? assets.find((a) => a.id === selectedFinding.assetId)
    : undefined;

  const handleSelectFinding = (id: string) => {
    setSelectedFindingId(id);
    setView("workspace");
  };

  // TODO(api): wire to POST /api/scans + SSE /api/scans/{id}/events for live progress.
  const handleToggleScan = () => {
    if (scanning) return;
    setScanning(true);
    if (view === "overview") setDashboardLoading(true);
    notify("Scan queued — analysing assets", "info");
    window.setTimeout(() => {
      setScanning(false);
      setDashboardLoading(false);
      notify("Scan complete — findings updated");
    }, 2400);
  };

  const handleApplyFix = (finding: Finding) => {
    // TODO(api): POST /api/findings/{id}/apply-fix to persist the remediation.
    setAppliedFindingIds((prev) => new Set(prev).add(finding.id));
    notify(`Fix applied to ${finding.affectedPath}`);
  };

  const handleMarkForReview = (finding: Finding) => {
    // TODO(api): PATCH /api/findings/{id} { status: "pending_review" }.
    notify(`"${finding.title}" marked for review`, "info");
  };

  const navPane = (
    <AssetNavigationPane
      assets={assets}
      findingsById={findingsById}
      selectedFindingId={selectedFindingId}
      onSelectFinding={handleSelectFinding}
    />
  );

  const middlePane = selectedFinding ? (
    <AnalysisWorkspace
      finding={selectedFinding}
      asset={selectedAsset}
      applied={appliedFindingIds.has(selectedFinding.id)}
      onApplyFix={() => handleApplyFix(selectedFinding)}
      onMarkForReview={() => handleMarkForReview(selectedFinding)}
    />
  ) : (
    <EmptyState
      icon={MousePointerSquareDashed}
      title="Select a finding to analyse"
      description="Choose an asset in the navigator, then pick a finding to see the vulnerable code, the AI-remediated fix, and the full report."
    />
  );

  const intelPane = selectedFinding ? (
    <IntelligencePanel finding={selectedFinding} />
  ) : (
    <EmptyState
      icon={ScanSearch}
      title="No finding selected"
      description="Vulnerability intelligence and the Ask VulnorAIQ assistant appear here once a finding is selected."
    />
  );

  return (
    <AppShell
      view={view}
      onChangeView={setView}
      theme={theme}
      onToggleTheme={toggleTheme}
      scanning={scanning}
      onToggleScan={handleToggleScan}
    >
      {view === "targets" ? (
        <TargetsManager />
      ) : view === "overview" ? (
        <div className="h-full overflow-y-auto scrollbar-thin p-4 sm:p-6">
          <div className="mx-auto max-w-[1400px]">
            <DashboardOverview
              metrics={dashboardMetrics}
              trend={trendData}
              distribution={severityDistribution}
              loading={dashboardLoading}
            />
          </div>
        </div>
      ) : (
        <WorkspaceLayout left={navPane} middle={middlePane} right={intelPane} />
      )}
    </AppShell>
  );
}

export default function App() {
  return (
    <TooltipProvider delayDuration={200}>
      <ToastProvider>
        <ConsoleInner />
      </ToastProvider>
    </TooltipProvider>
  );
}
