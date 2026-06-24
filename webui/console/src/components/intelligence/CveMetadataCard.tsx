import { CalendarDays, ShieldX } from "lucide-react";
import type { CveMetadata } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CvssBadge } from "./CvssBadge";

export function CveMetadataCard({ cve }: { cve: CveMetadata }) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <ShieldX className="size-4 text-[var(--accent-slate)]" />
          {cve.id ?? "No CVE assigned"}
        </CardTitle>
        {typeof cve.cvssScore === "number" && <CvssBadge score={cve.cvssScore} />}
      </CardHeader>
      <CardContent className="space-y-2">
        {cve.publishedDate && (
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <CalendarDays className="size-3.5" />
            Published {cve.publishedDate}
          </p>
        )}
        {cve.description && (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {cve.description}
          </p>
        )}
        {cve.cvssVector && (
          <p className="code-wrap rounded-sm border border-border bg-muted px-2 py-1 font-mono text-[11px] text-foreground">
            {cve.cvssVector}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
