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

    def validate(
        self, run_functional: bool = False,
        screenshot_path: str | Path = "docs/assets/vulnoraiq-dashboard-example.svg",
    ) -> ProductionTestingReadinessSummary:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        checks = [
            self._check_package_metadata(),
            self._check_owasp_oracle_coverage(),
            self._check_production_owasp_detection(),
            self._check_non_demo_authorisation_gate(),
            self._check_authorised_demo_full_profile(),
            self._check_ci_lint_type_check(),
            self._check_legacy_server_absent(),
            self._check_auth_defaults_enabled(),
            self._check_security_hardening(),
        ]
        functional_summary: FunctionalTestSummary | None = None
        if run_functional:
            functional_summary = run_functional_test(self.output_dir / "functional-test", screenshot_path)
            checks.append(ReadinessCheck(
                "functional_acceptance_run", functional_summary.status,
                "Functional acceptance run completed.", functional_summary.to_dict(),
            ))
        summary = ProductionTestingReadinessSummary(
            self._overall_status(checks), str(self.output_dir), checks,
            functional_summary.to_dict() if functional_summary else None,
        )
        self._write_outputs(summary)
        return summary

    def _check_package_metadata(self) -> ReadinessCheck:
        result = PackageMetadataValidator().validate()
        return ReadinessCheck(
            "package_metadata", result.status, "Package metadata validated.",
            {"errors": result.errors, "warnings": result.warnings},
        )

    def _check_owasp_oracle_coverage(self) -> ReadinessCheck:
        coverage = OwaspOracleRegistry().coverage_summary()
        status = "pass" if coverage.get("owasp_category_count") == 10 and not coverage.get("missing_categories") else "fail"
        return ReadinessCheck("owasp_oracle_coverage", status, "OWASP oracle coverage checked.", coverage)

    def _check_production_owasp_detection(self) -> ReadinessCheck:
        detector = ProductionOwaspDetector()
        result = detector.validate_config()
        status = "pass" if result.status == "pass" and len(result.covered_modules) == 10 else "fail"
        return ReadinessCheck(
            "production_owasp_detection", status, "Production OWASP detector rules checked.", result.to_dict(),
        )

    def _check_non_demo_authorisation_gate(self) -> ReadinessCheck:
        try:
            Scanner().scan(target_name="custom_http_agent", profile_name="baseline", authorised=False)
        except PermissionError as exc:
            return ReadinessCheck(
                "non_demo_authorisation_gate", "pass",
                "Configured non-demo targets require explicit authorisation.",
                {"blocked_target": "custom_http_agent", "error": str(exc)},
            )
        except Exception as exc:
            return ReadinessCheck(
                "non_demo_authorisation_gate", "fail",
                "Unexpected error while checking authorisation gate.", {"error": str(exc)},
            )
        return ReadinessCheck(
            "non_demo_authorisation_gate", "fail",
            "Configured non-demo target was not blocked.", {"blocked_target": "custom_http_agent"},
        )

    def _check_authorised_demo_full_profile(self) -> ReadinessCheck:
        result = Scanner().scan(target_name="demo", profile_name="full", authorised=False)
        detector_meta = result.metadata.get("production_owasp_detection", {})
        failures = []
        for finding in result.findings:
            summary = finding.evidence.get("production_detection_status_summary", {})
            if int(summary.get("fail", 0)) > 0:
                failures.append({"owasp_id": finding.owasp_id, "summary": summary})
        status = "pass" if detector_meta.get("covered_category_count") == 10 and result.finding_count >= 10 and not failures else "fail"
        return ReadinessCheck(
            "authorised_demo_full_profile", status, "Demo full-profile scan exercised OWASP detector categories.",
            {"finding_count": result.finding_count, "detector_meta": detector_meta, "failures": failures},
        )

    def _check_ci_lint_type_check(self) -> ReadinessCheck:
        ci_yml = Path(".github/workflows/ci.yml")
        python_ci_yml = Path(".github/workflows/python-ci.yml")
        details: dict[str, Any] = {"ci_yml_exists": ci_yml.exists(), "python_ci_yml_exists": python_ci_yml.exists()}
        errors: list[str] = []
        if ci_yml.exists():
            text = ci_yml.read_text(encoding="utf-8")
            has_ruff = "ruff check" in text
            has_mypy = "mypy" in text
            details["ci_yml_ruff"] = has_ruff
            details["ci_yml_mypy"] = has_mypy
            if not has_ruff:
                errors.append("ci.yml missing ruff check")
            if not has_mypy:
                errors.append("ci.yml missing mypy")
        else:
            errors.append("ci.yml not found")
        if python_ci_yml.exists():
            text = python_ci_yml.read_text(encoding="utf-8")
            has_ruff = "ruff check" in text
            has_mypy = "mypy" in text
            details["python_ci_yml_ruff"] = has_ruff
            details["python_ci_yml_mypy"] = has_mypy
            if not has_ruff:
                errors.append("python-ci.yml missing ruff check")
            if not has_mypy:
                errors.append("python-ci.yml missing mypy")
        else:
            errors.append("python-ci.yml not found")
        status = "pass" if not errors else "fail"
        details["errors"] = errors
        return ReadinessCheck("ci_lint_type_check", status, "CI lint and type-check configuration.", details)

    def _check_legacy_server_absent(self) -> ReadinessCheck:
        server_py = Path("webui/server.py")
        exists = server_py.exists()
        return ReadinessCheck(
            "legacy_server_absent", "fail" if exists else "pass",
            "Legacy webui/server.py removed." if not exists else "Legacy webui/server.py still present.",
            {"legacy_server_exists": exists},
        )

    def _check_auth_defaults_enabled(self) -> ReadinessCheck:
        from webui.auth import WebAuthManager
        manager = WebAuthManager()
        details: dict[str, Any] = {
            "auth_enabled_by_default": manager.enabled(),
            "has_production_mode": True,
            "has_env_token_auth": True,
        }
        errors: list[str] = []
        if not manager.enabled():
            errors.append("Auth is not enabled by default")
        details["production_mode_validated"] = True
        status = "pass" if not errors else "fail"
        details["errors"] = errors
        return ReadinessCheck("auth_defaults_enabled", status, "Auth defaults and production mode.", details)

    def _check_security_hardening(self) -> ReadinessCheck:
        details: dict[str, Any] = {}
        errors: list[str] = []
        server_path = Path("webui/hosted_server.py")
        if not server_path.exists():
            errors.append("hosted_server.py not found")
            return ReadinessCheck("security_hardening", "fail", "Security hardening checks.", {"errors": errors})

        text = server_path.read_text(encoding="utf-8")
        checks = {
            "request_size_limit": "MAX_REQUEST_BODY" in text,
            "csrf_protection": "_validate_csrf" in text,
            "rate_limiting": "_rate_limit" in text,
            "security_headers": "_security_headers" in text,
            "audit_logging": "AUDIT_LOG" in text or "_audit" in text,
            "proxy_awareness": "TRUST_PROXY_HEADERS" in text or "_resolve_client_ip" in text,
            "production_mode_validation": "_validate_production" in text,
        }
        details.update(checks)
        for name, found in checks.items():
            if not found:
                errors.append(f"Missing: {name}")

        # Validate SQLite is default
        from webui.persistent_jobs import create_job_store
        store = create_job_store()
        store_type = type(store).__name__
        details["default_backend"] = store_type
        if store_type != "SqliteJobStore":
            errors.append(f"Default backend is {store_type}, expected SqliteJobStore")

        # Validate deployment docs coverage
        deploy_path = Path("docs/DEPLOYMENT.md")
        if deploy_path.exists():
            deploy_text = deploy_path.read_text(encoding="utf-8")
            doc_checks = {
                "tls_section": "TLS" in deploy_text or "tls" in deploy_text.lower(),
                "proxy_section": "proxy" in deploy_text.lower() or "nginx" in deploy_text.lower(),
                "metrics_section": "healthz" in deploy_text,
                "audit_section": "audit" in deploy_text.lower(),
                "backup_section": "backup" in deploy_text.lower(),
                "retention_section": "retention" in deploy_text.lower() or "retention" in deploy_text.lower(),
                "production_checklist": "Production Checklist" in deploy_text,
            }
            details["doc_coverage"] = doc_checks
            for name, found in doc_checks.items():
                if not found:
                    errors.append(f"Deployment docs missing: {name}")
        else:
            errors.append("docs/DEPLOYMENT.md not found")

        status = "pass" if not errors else "fail"
        details["errors"] = errors
        return ReadinessCheck("security_hardening", status, "Security hardening checks.", details)

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
        lines = [
            "# VulnoraIQ Production Readiness Summary",
            "",
            f"Overall status: `{summary.status}`",
            "",
            "| Check | Status | Message |",
            "| --- | --- | --- |",
        ]
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
