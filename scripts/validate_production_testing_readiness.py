from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from benchmarks.fixture_validation import BenchmarkFixtureValidator
from core.evidence_model import OwaspOracleRegistry
from core.mitre_atlas import MitreAtlasMapping
from core.production_detection import ProductionOwaspDetector
from core.scanner import Scanner
from integrations.contract_validation import TargetContractValidator
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
    """Runs local gates before authorised production-assessment testing."""

    def __init__(self, output_dir: str | Path = "reports/output/production-readiness") -> None:
        self.output_dir = Path(output_dir)

    def validate(self, run_functional: bool = False, screenshot_path: str | Path = "docs/assets/vulnoraiq-dashboard-example.svg") -> ProductionTestingReadinessSummary:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        checks = [
            self._check_package_metadata(),
            self._check_target_contracts(),
            self._check_benchmark_fixtures(),
            self._check_mitre_atlas_mapping(),
            self._check_owasp_oracle_coverage(),
            self._check_production_owasp_detection(),
            self._check_non_demo_authorisation_gate(),
            self._check_authorised_demo_full_profile(),
            self._check_documentation_and_ci_wiring(),
        ]
        functional_summary: FunctionalTestSummary | None = None
        if run_functional:
            functional_summary = run_functional_test(self.output_dir / "functional-test", screenshot_path)
            checks.append(ReadinessCheck("functional_acceptance_run", functional_summary.status, "Functional acceptance run completed with production detector checks.", functional_summary.to_dict()))

        summary = ProductionTestingReadinessSummary(self._overall_status(checks), str(self.output_dir), checks, functional_summary.to_dict() if functional_summary else None)
        self._write_outputs(summary)
        return summary

    def _check_package_metadata(self) -> ReadinessCheck:
        result = PackageMetadataValidator().validate()
        return ReadinessCheck("package_metadata", result.status, "Package metadata, CLI entry points, notices, and release assets were validated.", {"errors": result.errors, "warnings": result.warnings})

    def _check_target_contracts(self) -> ReadinessCheck:
        result = TargetContractValidator().validate()
        status = "fail" if result.status == "fail" else "warn" if result.warnings else "pass"
        return ReadinessCheck("target_contracts", status, "Configured target adapter contracts were checked.", {"target_count": result.target_count, "validated_count": result.validated_count, "errors": result.errors, "warnings": result.warnings})

    def _check_benchmark_fixtures(self) -> ReadinessCheck:
        result = BenchmarkFixtureValidator().validate()
        return ReadinessCheck("benchmark_fixtures", result.status, "OWASP benchmark fixtures were validated for category coverage and required fields.", {"fixture_count": result.fixture_count, "covered_modules": result.covered_modules, "errors": result.errors})

    def _check_mitre_atlas_mapping(self) -> ReadinessCheck:
        result = MitreAtlasMapping().validate()
        return ReadinessCheck("mitre_atlas_mapping", result.status, "Local MITRE ATLAS mapping catalog was validated.", {"mapping_path": result.mapping_path, "technique_count": result.technique_count, "module_mapping_count": result.module_mapping_count, "errors": result.errors, "warnings": result.warnings})

    def _check_owasp_oracle_coverage(self) -> ReadinessCheck:
        coverage = OwaspOracleRegistry().coverage_summary()
        missing = coverage.get("missing_categories", [])
        status = "pass" if coverage.get("owasp_category_count") == 10 and not missing else "fail"
        return ReadinessCheck("owasp_oracle_coverage", status, "OWASP LLM oracle coverage was checked across all 10 categories.", coverage)

    def _check_production_owasp_detection(self) -> ReadinessCheck:
        detector = ProductionOwaspDetector()
        result = detector.validate_config()
        details = result.to_dict()
        status = "pass" if result.status == "pass" and len(result.covered_modules) == 10 else "fail"
        return ReadinessCheck("production_owasp_detection", status, "Production OWASP detector rules were validated for all 10 OWASP LLM categories.", details)

    def _check_non_demo_authorisation_gate(self) -> ReadinessCheck:
        try:
            Scanner().scan(target_name="custom_http_agent", profile_name="baseline", authorised=False)
        except PermissionError as exc:
            return ReadinessCheck("non_demo_authorisation_gate", "pass", "Configured non-demo targets are blocked unless explicit authorisation is supplied.", {"blocked_target": "custom_http_agent", "error": str(exc)})
        except Exception as exc:
            return ReadinessCheck("non_demo_authorisation_gate", "fail", "Non-demo authorisation gate raised an unexpected error.", {"error": str(exc)})
        return ReadinessCheck("non_demo_authorisation_gate", "fail", "Configured non-demo target scan was not blocked without explicit authorisation.", {"blocked_target": "custom_http_agent"})

    def _check_authorised_demo_full_profile(self) -> ReadinessCheck:
        result = Scanner().scan(target_name="demo", profile_name="full", authorised=False)
        detector_meta = result.metadata.get("production_owasp_detection", {})
        failures = []
        for finding in result.findings:
            summary = finding.evidence.get("production_detection_status_summary", {})
            if int(summary.get("fail", 0)) > 0:
                failures.append({"owasp_id": finding.owasp_id, "summary": summary})
        status = "pass" if detector_meta.get("covered_category_count") == 10 and not failures and result.finding_count >= 10 else "fail"
        return ReadinessCheck("authorised_demo_full_profile", status, "Safe demo full-profile scan exercised all OWASP production detector categories without detector failures.", {"finding_count": result.finding_count, "detector_meta": detector_meta, "failures": failures})

    def _check_documentation_and_ci_wiring(self) -> ReadinessCheck:
        errors: list[str] = []
        warnings: list[str] = []
        required_paths = [Path("README.md"), Path("docs/IMPLEMENTATION_STATUS.md"), Path("docs/assets/vulnoraiq-dashboard-example.svg"), Path(".github/workflows/ci.yml"), Path("config/production_owasp_detection.yaml"), Path("core/production_detection.py")]
        for path in required_paths:
            if not path.exists():
                errors.append(f"Missing required file: {path}")
        readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else ""
        status_doc = Path("docs/IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8") if Path("docs/IMPLEMENTATION_STATUS.md").exists() else ""
        ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8") if Path(".github/workflows/ci.yml").exists() else ""
        if "authorised production-assessment testing" not in readme.lower():
            warnings.append("README should describe authorised production-assessment testing readiness.")
        if "production owasp detector" not in status_doc.lower():
            warnings.append("Implementation status should mention the production OWASP detector.")
        if "validate_production_testing_readiness.py" not in ci:
            errors.append("CI must run the production-testing readiness gate.")
        if "run_functional_test.py" not in ci and "--run-functional" not in ci:
            errors.append("CI must run the functional acceptance path.")
        return ReadinessCheck("documentation_and_ci_wiring", "fail" if errors else "warn" if warnings else "pass", "Documentation, dashboard example asset, production detector config, and CI wiring were checked.", {"errors": errors, "warnings": warnings})

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
        lines = ["# VulnoraIQ Production-Assessment Testing Readiness Summary", "", f"Overall status: `{summary.status}`", "", "> This gate confirms controlled readiness for authorised security-assessment testing. It is not a certification of exploitability or business risk.", "", "| Check | Status | Message |", "| --- | --- | --- |"]
        for check in summary.checks:
            lines.append(f"| `{check.id}` | `{check.status}` | {check.message.replace('|', '\\|')} |")
        markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate VulnoraIQ production-assessment testing readiness gates.")
    parser.add_argument("--output-dir", default="reports/output/production-readiness")
    parser.add_argument("--screenshot", default="docs/assets/vulnoraiq-dashboard-example.svg")
    parser.add_argument("--run-functional", action="store_true", help="Run the safe demo/baseline functional acceptance path.")
    parser.add_argument("--fail-on-warn", action="store_true", help="Treat readiness warnings as command failures.")
    args = parser.parse_args()
    summary = ProductionTestingReadinessValidator(args.output_dir).validate(args.run_functional, args.screenshot)
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True, default=str))
    if summary.status == "fail" or (args.fail_on_warn and summary.status == "warn"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
