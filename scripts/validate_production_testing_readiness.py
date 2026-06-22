from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.evidence_model import OwaspOracleRegistry
from core.production_detection import ProductionOwaspDetector
from core.scanner import Scanner
from scripts.run_functional_test import FunctionalTestSummary, run_functional_test
from scripts.validate_package_metadata import PackageMetadataValidator


@dataclass(slots=True)
class ReadinessCheck:
    id: str
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProductionTestingReadinessSummary:
    status: str
    output_dir: str
    checks: list[ReadinessCheck]
    functional_test: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProductionTestingReadinessValidator:
    def __init__(self, output_dir: str | Path = "reports/output/production-readiness") -> None:
        self.output_dir = Path(output_dir)

    def validate(self, run_functional: bool = False, screenshot_path: str | Path = "docs/assets/vulnoraiq-dashboard-example.svg") -> ProductionTestingReadinessSummary:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        checks = [
            self._check_package_metadata(),
            self._check_owasp_oracle_coverage(),
            self._check_production_owasp_detection(),
            self._check_non_demo_authorisation_gate(),
            self._check_authorised_demo_full_profile(),
        ]
        functional_summary: FunctionalTestSummary | None = None
        if run_functional:
            functional_summary = run_functional_test(self.output_dir / "functional-test", screenshot_path)
            checks.append(ReadinessCheck("functional_acceptance_run", functional_summary.status, "Functional acceptance run completed.", functional_summary.to_dict()))
        summary = ProductionTestingReadinessSummary(self._overall_status(checks), str(self.output_dir), checks, functional_summary.to_dict() if functional_summary else None)
        self._write_outputs(summary)
        return summary

    def _check_package_metadata(self) -> ReadinessCheck:
        result = PackageMetadataValidator().validate()
        return ReadinessCheck("package_metadata", result.status, "Package metadata validated.", {"errors": result.errors, "warnings": result.warnings})

    def _check_owasp_oracle_coverage(self) -> ReadinessCheck:
        coverage = OwaspOracleRegistry().coverage_summary()
        status = "pass" if coverage.get("owasp_category_count") == 10 and not coverage.get("missing_categories") else "fail"
        return ReadinessCheck("owasp_oracle_coverage", status, "OWASP oracle coverage checked.", coverage)

    def _check_production_owasp_detection(self) -> ReadinessCheck:
        detector = ProductionOwaspDetector()
        result = detector.validate_config()
        status = "pass" if result.status == "pass" and len(result.covered_modules) == 10 else "fail"
        return ReadinessCheck("production_owasp_detection", status, "Production OWASP detector rules checked.", result.to_dict())

    def _check_non_demo_authorisation_gate(self) -> ReadinessCheck:
        try:
            Scanner().scan(target_name="custom_http_agent", profile_name="baseline", authorised=False)
        except PermissionError as exc:
            return ReadinessCheck("non_demo_authorisation_gate", "pass", "Configured non-demo targets require explicit authorisation.", {"blocked_target": "custom_http_agent", "error": str(exc)})
        except Exception as exc:
            return ReadinessCheck("non_demo_authorisation_gate", "fail", "Unexpected error while checking authorisation gate.", {"error": str(exc)})
        return ReadinessCheck("non_demo_authorisation_gate", "fail", "Configured non-demo target was not blocked.", {"blocked_target": "custom_http_agent"})

    def _check_authorised_demo_full_profile(self) -> ReadinessCheck:
        result = Scanner().scan(target_name="demo", profile_name="full", authorised=False)
        detector_meta = result.metadata.get("production_owasp_detection", {})
        failures = []
        for finding in result.findings:
            summary = finding.evidence.get("production_detection_status_summary", {})
            if int(summary.get("fail", 0)) > 0:
                failures.append({"owasp_id": finding.owasp_id, "summary": summary})
        status = "pass" if detector_meta.get("covered_category_count") == 10 and result.finding_count >= 10 and not failures else "fail"
        return ReadinessCheck("authorised_demo_full_profile", status, "Demo full-profile scan exercised OWASP detector categories.", {"finding_count": result.finding_count, "detector_meta": detector_meta, "failures": failures})

    @staticmethod
    def _overall_status(checks: list[ReadinessCheck]) -> str:
        statuses = {check.status for check in checks}
        if "fail" in statuses:
            return "fail"
        if "warn" in statuses:
            return "warn"
        return "pass"

    def _write_outputs(self, summary: ProductionTestingReadinessSummary) -> None:
        json_path = self.output_dir / "production-testing-readiness-summary.json"
        markdown_path = self.output_dir / "production-testing-readiness-summary.md"
        json_path.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True, default=str), encoding="utf-8")
        lines = ["# VulnoraIQ Production Readiness Summary", "", f"Overall status: `{summary.status}`", "", "| Check | Status | Message |", "| --- | --- | --- |"]
        for check in summary.checks:
            message = check.message.replace("|", "\\|")
            lines.append(f"| `{check.id}` | `{check.status}` | {message} |")
        markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate VulnoraIQ readiness gates.")
    parser.add_argument("--output-dir", default="reports/output/production-readiness")
    parser.add_argument("--screenshot", default="docs/assets/vulnoraiq-dashboard-example.svg")
    parser.add_argument("--run-functional", action="store_true")
    parser.add_argument("--fail-on-warn", action="store_true")
    args = parser.parse_args()
    summary = ProductionTestingReadinessValidator(args.output_dir).validate(args.run_functional, args.screenshot)
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True, default=str))
    if summary.status == "fail" or (args.fail_on_warn and summary.status == "warn"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
