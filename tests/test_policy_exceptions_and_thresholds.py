from __future__ import annotations

from datetime import datetime, timezone

from core.exception_registry import PolicyExceptionRegistry
from core.policy_engine import PolicyEngine
from core.types import Finding, PolicyResult, ScanResult


def test_severity_threshold_policy_passes_demo_scan() -> None:
    result = ScanResult(
        target_name="demo",
        profile_name="baseline",
        findings=[
            Finding(
                title="Info finding",
                description="Safe finding",
                severity="info",
                owasp_id="LLM00:2025",
                affected_component="demo",
            )
        ],
        started_at=datetime.now(timezone.utc),
    )
    config = {"policies": {"policies": {"severity_threshold": {"enabled": True, "maximum_allowed_severity": "high"}}}}

    policies = PolicyEngine().evaluate(result, config)

    threshold = next(policy for policy in policies if policy.policy_id == "severity_threshold")
    assert threshold.status == "pass"


def test_severity_threshold_policy_fails_critical() -> None:
    result = ScanResult(
        target_name="demo",
        profile_name="baseline",
        findings=[
            Finding(
                title="Critical finding",
                description="Critical result",
                severity="critical",
                owasp_id="LLM00:2025",
                affected_component="demo",
            )
        ],
        started_at=datetime.now(timezone.utc),
    )
    config = {"policies": {"policies": {"severity_threshold": {"enabled": True, "maximum_allowed_severity": "high"}}}}

    policies = PolicyEngine().evaluate(result, config)

    threshold = next(policy for policy in policies if policy.policy_id == "severity_threshold")
    assert threshold.status == "fail"


def test_active_policy_exception_suppresses_fail_to_warn(tmp_path) -> None:
    exception_file = tmp_path / "policy_exceptions.yaml"
    exception_file.write_text(
        """
exceptions:
  - id: EX-001
    policy_id: severity_threshold
    status: active
    owner: security-team
    reason: Approved temporary acceptance for test fixture.
    expires_on: 2999-01-01
    target: demo
    profile: baseline
    approval_reference: TEST-APPROVAL-001
    compensating_controls:
      - Manual review required.
""",
        encoding="utf-8",
    )
    result = ScanResult(
        target_name="demo",
        profile_name="baseline",
        findings=[],
        started_at=datetime.now(timezone.utc),
    )
    registry = PolicyExceptionRegistry(exception_file)
    policy = PolicyResult(
        policy_id="severity_threshold",
        status="fail",
        decision="fail_on_critical",
        message="Original failure",
        evidence={},
    )

    updated = registry.apply(result, [policy])

    assert updated[0].status == "warn"
    assert updated[0].evidence["original_status"] == "fail"
    assert updated[0].evidence["active_exceptions"] == ["EX-001"]
