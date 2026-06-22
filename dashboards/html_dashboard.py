from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


class HtmlDashboardGenerator:
    """Builds a self-contained HTML dashboard from a structured report."""

    def generate_from_report(self, report: dict[str, Any], output_path: str | Path) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self._render(report), encoding="utf-8")
        return output

    def _render(self, report: dict[str, Any]) -> str:
        target = html.escape(str(report.get("target", "unknown")))
        profile = html.escape(str(report.get("profile", "unknown")))
        policy_status = html.escape(str(report.get("policy_status", "pass")))
        highest = html.escape(str(report.get("highest_severity", "info")))
        findings = report.get("findings", [])
        policy_results = report.get("policy_results", [])

        severity_rows = "".join(
            f"<tr><td>{html.escape(str(sev))}</td><td>{count}</td></tr>"
            for sev, count in sorted(report.get("severity_counts", {}).items())
        )
        policy_rows = "".join(
            "<tr>"
            f"<td>{html.escape(str(policy.get('policy_id', '')))}</td>"
            f"<td>{html.escape(str(policy.get('status', '')))}</td>"
            f"<td>{html.escape(str(policy.get('decision', '')))}</td>"
            f"<td>{html.escape(str(policy.get('message', '')))}</td>"
            "</tr>"
            for policy in policy_results
        )
        finding_rows = "".join(
            "<tr>"
            f"<td>{html.escape(str(finding.get('severity', '')))}</td>"
            f"<td>{html.escape(str(finding.get('score', '')))}</td>"
            f"<td>{html.escape(str(finding.get('title', '')))}</td>"
            f"<td>{html.escape(str(finding.get('owasp_id', '')))}</td>"
            f"<td>{html.escape(str(finding.get('affected_component', '')))}</td>"
            "</tr>"
            for finding in sorted(findings, key=lambda item: item.get("score") or 0, reverse=True)
        )
        raw_json = html.escape(json.dumps(report, indent=2, sort_keys=True, default=str))

        return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>VulnoraIQ Assessment Dashboard - {target}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; line-height: 1.5; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
    .card {{ border: 1px solid #d0d7de; border-radius: 8px; padding: 1rem; background: #f6f8fa; }}
    .value {{ font-size: 1.6rem; font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
    th, td {{ border: 1px solid #d0d7de; padding: 0.5rem; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
    pre {{ white-space: pre-wrap; background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 8px; padding: 1rem; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>VulnoraIQ Assessment Dashboard</h1>
  <div class=\"cards\">
    <div class=\"card\"><div>Target</div><div class=\"value\">{target}</div></div>
    <div class=\"card\"><div>Profile</div><div class=\"value\">{profile}</div></div>
    <div class=\"card\"><div>Findings</div><div class=\"value\">{len(findings)}</div></div>
    <div class=\"card\"><div>Highest severity</div><div class=\"value\">{highest}</div></div>
    <div class=\"card\"><div>Policy status</div><div class=\"value\">{policy_status}</div></div>
  </div>

  <h2>Severity distribution</h2>
  <table><thead><tr><th>Severity</th><th>Count</th></tr></thead><tbody>{severity_rows}</tbody></table>

  <h2>Policy evaluation</h2>
  <table><thead><tr><th>Policy</th><th>Status</th><th>Decision</th><th>Message</th></tr></thead><tbody>{policy_rows}</tbody></table>

  <h2>Findings</h2>
  <table><thead><tr><th>Severity</th><th>Score</th><th>Title</th><th>OWASP</th><th>Component</th></tr></thead><tbody>{finding_rows}</tbody></table>

  <h2>Raw structured report</h2>
  <pre>{raw_json}</pre>
</body>
</html>
"""
