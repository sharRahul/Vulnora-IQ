from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from core.scanner import Scanner
from reports.json_report_generator import JsonReportGenerator

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass(slots=True)
class BenchmarkResult:
    benchmark_id: str
    status: str
    report_path: str
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BenchmarkSuiteResult:
    status: str
    benchmark_count: int
    passed_count: int
    failed_count: int
    results: list[BenchmarkResult]


def _enable_fixture_targets_for_benchmarks() -> None:
    os.environ.setdefault("VULNORAIQ_ALLOW_TEST_FIXTURE_TARGETS", "true")
    os.environ.setdefault("VULNORAIQ_TARGET_CONFIG", "targets.test.yaml")


def run_benchmarks(
    manifest_path: str | Path = "benchmarks/benchmark_suite.yaml",
    output_dir: str | Path = "reports/output/benchmarks",
) -> BenchmarkSuiteResult:
    _enable_fixture_targets_for_benchmarks()
    manifest = yaml.safe_load(Path(manifest_path).read_text(encoding="utf-8")) or {}
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    scanner = Scanner()
    results: list[BenchmarkResult] = []
    for benchmark in manifest.get("benchmarks", []):
        result = scanner.scan(target_name=str(benchmark["target"]), profile_name=str(benchmark["profile"]))
        report_path = JsonReportGenerator().generate(result, output / f"{benchmark['id']}.json")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        errors = _validate_report(report, benchmark)
        results.append(BenchmarkResult(str(benchmark["id"]), "fail" if errors else "pass", str(report_path), errors))
    failed = sum(1 for item in results if item.status == "fail")
    passed = sum(1 for item in results if item.status == "pass")
    return BenchmarkSuiteResult("fail" if failed else "pass", len(results), passed, failed, results)


def _validate_report(report: dict[str, Any], benchmark: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("policy_status") != benchmark.get("expected_policy_status"):
        errors.append(f"Expected policy_status {benchmark.get('expected_policy_status')}, got {report.get('policy_status')}")
    if int(report.get("finding_count", 0)) < int(benchmark.get("minimum_finding_count", 0)):
        errors.append("Finding count below benchmark minimum")
    maximum = str(benchmark.get("max_highest_severity", "critical"))
    observed = str(report.get("highest_severity", "info"))
    if SEVERITY_ORDER.get(observed, 0) > SEVERITY_ORDER.get(maximum, 4):
        errors.append(f"Highest severity {observed} exceeds benchmark maximum {maximum}")
    policies = {item.get("policy_id"): item for item in report.get("policy_results", [])}
    for policy_id, evidence_expectations in benchmark.get("required_policy_evidence", {}).items():
        evidence = policies.get(policy_id, {}).get("evidence", {})
        for key, expected in evidence_expectations.items():
            if evidence.get(key) != expected:
                errors.append(f"Policy {policy_id} evidence {key} expected {expected}, got {evidence.get(key)}")
    return errors


def write_result(result: BenchmarkSuiteResult, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(result), indent=2, sort_keys=True), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local regression benchmarks.")
    parser.add_argument("--manifest", default="benchmarks/benchmark_suite.yaml")
    parser.add_argument("--output-dir", default="reports/output/benchmarks")
    parser.add_argument("--summary-output", default="reports/output/benchmarks/benchmark-summary.json")
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args()
    result = run_benchmarks(args.manifest, args.output_dir)
    summary = write_result(result, args.summary_output)
    print(f"Benchmark summary written to {summary}. Status: {result.status}")
    if args.fail_on_regression and result.status == "fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
