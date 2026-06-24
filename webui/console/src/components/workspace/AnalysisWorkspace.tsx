import { useState } from "react";
import {
  Columns2,
  FileCode2,
  Rows2,
  Sparkles,
} from "lucide-react";
import type { Asset, Finding } from "@/types";
import { statusStyles } from "@/lib/severity";
import { cn } from "@/lib/utils";
import { SeverityBadge } from "@/components/SeverityBadge";
import { RiskScoreBadge } from "@/components/RiskScoreBadge";
import { Button } from "@/components/ui/button";
import { VulnerableCodeBlock } from "./VulnerableCodeBlock";
import { RemediatedCodeBlock } from "./RemediatedCodeBlock";
import { FindingMarkdownReader } from "./FindingMarkdownReader";

interface AnalysisWorkspaceProps {
  finding: Finding;
  asset?: Asset;
  applied: boolean;
  onApplyFix: () => void;
  onMarkForReview: () => void;
}

export function AnalysisWorkspace({
  finding,
  asset,
  applied,
  onApplyFix,
  onMarkForReview,
}: AnalysisWorkspaceProps) {
  const [split, setSplit] = useState(true);
  const status = statusStyles[applied ? "fixed" : finding.status];

  return (
    <div className="flex h-full flex-col">
      {/* Top area */}
      <header className="border-b border-border bg-card/60 p-4">
        <div className="flex flex-wrap items-center gap-2">
          <SeverityBadge severity={finding.severity} withIcon />
          <RiskScoreBadge score={finding.riskScore} size="md" />
          <span
            className={cn(
              "inline-flex items-center rounded-sm border px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide",
              status.className,
            )}
          >
            {status.label}
          </span>
        </div>

        <h1 className="mt-2.5 font-sans text-lg font-extrabold leading-tight tracking-tight text-foreground">
          {finding.title}
        </h1>

        <p className="mt-1 flex items-center gap-1.5 font-mono text-xs text-muted-foreground">
          <FileCode2 className="size-3.5" />
          {asset ? `${asset.name} · ` : ""}
          {finding.affectedPath}
        </p>

        <div className="mt-3 flex gap-2 rounded-md border border-border bg-[color-mix(in_srgb,var(--accent-slate)_8%,transparent)] p-3">
          <Sparkles className="mt-0.5 size-4 shrink-0 text-[var(--accent-slate)]" />
          <p className="text-sm leading-relaxed text-foreground">
            <span className="font-semibold">AI explanation · </span>
            {finding.aiSummary}
          </p>
        </div>
      </header>

      {/* Main analysis area */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
            Remediation View
          </h2>
          <div className="hidden items-center gap-1 rounded-md border border-border bg-muted p-0.5 lg:flex">
            <Button
              variant={split ? "primary" : "ghost"}
              size="sm"
              className="h-7"
              onClick={() => setSplit(true)}
              aria-pressed={split}
            >
              <Columns2 className="size-3.5" /> Split
            </Button>
            <Button
              variant={!split ? "primary" : "ghost"}
              size="sm"
              className="h-7"
              onClick={() => setSplit(false)}
              aria-pressed={!split}
            >
              <Rows2 className="size-3.5" /> Stacked
            </Button>
          </div>
        </div>

        <div
          className={cn(
            "grid gap-4",
            split ? "lg:grid-cols-2" : "grid-cols-1",
          )}
        >
          <VulnerableCodeBlock block={finding.vulnerableCode} />
          <RemediatedCodeBlock
            remediation={finding.remediation}
            applied={applied}
            onApplyFix={onApplyFix}
            onMarkForReview={onMarkForReview}
          />
        </div>

        <div className="mt-4">
          <FindingMarkdownReader sections={finding.report} />
        </div>
      </div>
    </div>
  );
}
