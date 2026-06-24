import {
  BookText,
  FileSearch,
  Gavel,
  Link2,
  ListChecks,
  Target,
  TriangleAlert,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { MarkdownSection } from "@/types";

const sectionIcons: Record<string, LucideIcon> = {
  Evidence: FileSearch,
  "Attack scenario": Target,
  "Business impact": TriangleAlert,
  "Remediation guidance": Gavel,
  "Validation steps": ListChecks,
  References: Link2,
};

/** Light-weight inline renderer: highlights `code` spans without a markdown dep. */
function renderInline(text: string) {
  const parts = text.split(/(`[^`]+`)/g);
  return parts.map((part, i) =>
    part.startsWith("`") && part.endsWith("`") ? (
      <code
        key={i}
        className="rounded-sm bg-muted px-1 py-0.5 font-mono text-[12px] text-foreground"
      >
        {part.slice(1, -1)}
      </code>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}

function renderBody(body: string) {
  const lines = body.split("\n").filter((l) => l.trim().length > 0);
  return (
    <div className="space-y-1.5">
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (/^[-*]\s+/.test(trimmed)) {
          return (
            <p key={i} className="flex gap-2 text-sm leading-relaxed text-muted-foreground">
              <span className="mt-2 size-1.5 shrink-0 rounded-full bg-[var(--accent-slate)]" />
              <span>{renderInline(trimmed.replace(/^[-*]\s+/, ""))}</span>
            </p>
          );
        }
        return (
          <p key={i} className="text-sm leading-relaxed text-muted-foreground">
            {renderInline(trimmed)}
          </p>
        );
      })}
    </div>
  );
}

export function FindingMarkdownReader({
  sections,
}: {
  sections: MarkdownSection[];
}) {
  return (
    <section className="rounded-lg border border-border bg-card shadow-card">
      <header className="flex items-center gap-2 border-b border-border px-4 py-2.5">
        <BookText className="size-4 text-[var(--accent-slate)]" />
        <h3 className="text-sm font-bold text-foreground">Findings Report</h3>
      </header>
      <div className="divide-y divide-border">
        {sections.map((section) => {
          const Icon = sectionIcons[section.title] ?? BookText;
          return (
            <article key={section.title} className="p-4">
              <h4 className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-foreground">
                <Icon className="size-3.5 text-muted-foreground" />
                {section.title}
              </h4>
              {renderBody(section.body)}
            </article>
          );
        })}
      </div>
    </section>
  );
}
