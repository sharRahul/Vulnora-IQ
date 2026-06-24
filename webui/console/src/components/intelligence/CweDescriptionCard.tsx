import { Bug } from "lucide-react";
import type { CweMetadata } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function CweDescriptionCard({ cwe }: { cwe: CweMetadata }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bug className="size-4 text-[var(--accent-slate)]" />
          {cwe.id} · {cwe.name}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-relaxed text-muted-foreground">
          {cwe.description}
        </p>
      </CardContent>
    </Card>
  );
}
