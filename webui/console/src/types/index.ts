// Strongly typed domain model for the VulnorAIQ SecOps console.

export type Severity = "critical" | "high" | "medium" | "low" | "info";

export type FindingStatus =
  | "open"
  | "pending_review"
  | "auto_fix_available"
  | "fixed";

export type AssetType =
  | "repository"
  | "file"
  | "container_image"
  | "ai_agent"
  | "llm_app"
  | "rag_store";

export interface Asset {
  id: string;
  name: string;
  type: AssetType;
  /** Filesystem path or image tag, depending on asset type. */
  locator: string;
  vulnerabilityCount: number;
  highestSeverity: Severity;
  /** 0–100 composite risk score. */
  riskScore: number;
  lastScanned: string; // ISO timestamp
  findingIds: string[];
}

export interface CodeBlock {
  language: string;
  filename: string;
  code: string;
  /** 1-based line numbers to highlight. */
  highlightLines?: number[];
  startLine?: number;
}

export interface Remediation {
  summary: string;
  /** Why the fix works, in plain language. */
  rationale: string;
  /** 0–100 model confidence in the remediation. */
  confidence: number;
  secureCode: CodeBlock;
}

export interface CveMetadata {
  id: string | null;
  publishedDate?: string;
  cvssScore?: number;
  cvssVector?: string;
  description?: string;
}

export interface CweMetadata {
  id: string;
  name: string;
  description: string;
}

export interface IntelligenceMapping {
  owaspLlm?: string;
  mitreAtlas?: string;
  exploitability: "theoretical" | "poc" | "functional" | "active";
  affectedComponent: string;
  recommendedPriority: Severity;
  policyStatus: "pass" | "warn" | "fail" | "manual_review";
  complianceTags: string[];
}

export interface MarkdownSection {
  title: string;
  body: string;
}

export interface Finding {
  id: string;
  assetId: string;
  title: string;
  severity: Severity;
  riskScore: number;
  status: FindingStatus;
  affectedPath: string;
  /** Short AI-generated explanation shown in the workspace header. */
  aiSummary: string;
  vulnerableCode: CodeBlock;
  remediation: Remediation;
  cve: CveMetadata;
  cwe: CweMetadata;
  intelligence: IntelligenceMapping;
  /** Evidence / attack scenario / impact / guidance / validation / references. */
  report: MarkdownSection[];
}

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  pending?: boolean;
}

export interface DashboardMetrics {
  totalScanned: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  autoRemediationRate: number; // percentage
  pendingReviews: number;
  meanTimeToRemediateHours: number;
  trend: {
    critical: number;
    high: number;
    autoRemediationRate: number;
    pendingReviews: number;
  };
}

export interface VulnerabilityTrendPoint {
  date: string; // e.g. "Jun 18"
  discovered: number;
  remediated: number;
  open: number;
}

export interface SeverityDistributionPoint {
  severity: Severity;
  count: number;
}
