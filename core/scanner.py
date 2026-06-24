from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from core.evidence_model import OwaspOracleRegistry
from core.policy_engine import PolicyEngine
from core.production_detection import ProductionOwaspDetector
from core.real_scan import run_real_target_modules
from core.test_runner import TestRunner
from core.types import ScanContext, ScanResult, TargetClient
from integrations.base import DemoEchoClient
from integrations.target_adapters import RealTargetClient


class Scanner:
    """High-level assessment entry point."""

    def __init__(self, config_dir: str | Path = "config") -> None:
        self.config_dir = Path(config_dir)
        self.runner = TestRunner()
        self.policy_engine = PolicyEngine()
        self.oracle_registry = OwaspOracleRegistry()
        self.production_detector = ProductionOwaspDetector()

    def scan(
        self,
        target_name: str = "demo",
        profile_name: str = "baseline",
        target: TargetClient | None = None,
        authorised: bool = False,
    ) -> ScanResult:
        config = self._load_config()
        profile = config["attack_profiles"].get("profiles", {}).get(profile_name)
        if not profile:
            raise ValueError(f"Unknown assessment profile: {profile_name}")

        self._require_authorisation(target_name=target_name, target=target, authorised=authorised, config=config)
        target_client = target or self._default_target(target_name, config=config)
        context = ScanContext(
            target_name=target_name,
            profile_name=profile_name,
            target=target_client,
            config=config,
        )
        if isinstance(target_client, RealTargetClient):
            findings = run_real_target_modules(context, profile, self.runner.payload_library)
        else:
            findings = self.runner.run_modules(profile["modules"], context)
        result = ScanResult(
            target_name=target_name,
            profile_name=profile_name,
            findings=findings,
            started_at=context.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata={
                "framework": config.get("default", {}).get("framework", {}),
                "profile_description": profile.get("description", ""),
                "authorised": authorised or target_name == "demo",
                "owasp_oracle_coverage": self.oracle_registry.coverage_summary(),
                "production_owasp_detection": self.production_detector.coverage_summary(),
                "production_validation_status": "authorised_production_assessment_testing_ready",
                "assessment_scope_warning": (
                    "Run only against systems you own or are explicitly authorised to test; "
                    "findings still require tester review and business-context validation."
                ),
            },
        )
        result.policy_results = self.policy_engine.evaluate(result, config)
        return result

    def _require_authorisation(
        self,
        target_name: str,
        target: TargetClient | None,
        authorised: bool,
        config: dict[str, Any],
    ) -> None:
        policy = config.get("policies", {}).get("policies", {}).get("authorised_testing_required", {})
        policy_enabled = bool(policy.get("enabled", True))
        is_demo = target_name == "demo" and target is None
        if policy_enabled and not is_demo and not authorised:
            raise PermissionError(
                "Configured targets require explicit authorisation. Re-run with the CLI authorisation flag "
                "only for systems you own or are permitted to assess."
            )

    def _default_target(self, target_name: str, config: dict[str, Any]) -> TargetClient:
        target_config = config.get("targets", {}).get("targets", {}).get(target_name)
        if target_name == "demo":
            return DemoEchoClient()
        if not target_config:
            raise ValueError(f"Unknown target: {target_name}")
        self._reject_placeholder(target_name, target_config.get("endpoint") or target_config.get("base_url"))
        return RealTargetClient(target_name, target_config)

    @staticmethod
    def _reject_placeholder(target_name: str, endpoint: Any) -> None:
        if not endpoint or "example.invalid" in str(endpoint):
            raise ValueError(f"Target '{target_name}' is a placeholder. Configure a real authorised endpoint before assessment.")

    def _load_config(self) -> dict[str, Any]:
        def load_yaml(name: str) -> dict[str, Any]:
            path = self.config_dir / name
            with path.open("r", encoding="utf-8") as handle:
                return yaml.safe_load(handle) or {}

        targets = load_yaml("targets.yaml")
        self._merge_runtime_targets(targets)
        return {
            "default": load_yaml("default.yaml"),
            "targets": targets,
            "attack_profiles": load_yaml("attack_profiles.yaml"),
            "policies": load_yaml("policies.yaml"),
        }

    @staticmethod
    def _merge_runtime_targets(targets: dict[str, Any]) -> None:
        runtime_targets_path = Path(os.getenv("VULNORAIQ_RUNTIME_TARGETS_PATH", "reports/output/webui/runtime_targets.yaml"))
        if not runtime_targets_path.exists():
            return
        runtime_targets = yaml.safe_load(runtime_targets_path.read_text(encoding="utf-8")) or {}
        if not isinstance(runtime_targets, dict):
            return
        configured_targets = targets.setdefault("targets", {})
        for name, target in (runtime_targets.get("targets") or {}).items():
            if isinstance(target, dict):
                configured_targets[str(name)] = target
