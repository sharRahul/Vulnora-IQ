from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_testing.execution_harness import AgentExecutionHarness
from agent_testing.runtime_manifest import AgentRuntimeValidator
from core.exception_registry import PolicyExceptionRegistry
from core.types import Finding, PolicyResult, ScanResult
from rag_testing.corpus_manifest import CorpusManifestValidator
from rag_testing.retrieval_harness import LocalRetrievalHarness


SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


class PolicyEngine:
    """Evaluates governance policies against assessment results.

    This engine keeps policy decisions explicit and reportable. It does not replace
    human review; it creates consistent pass, warn, and fail signals for CI/CD and
    audit evidence.
    """

    def __init__(self, exception_registry: PolicyExceptionRegistry | None = None) -> None:
        self.exception_registry = exception_registry or PolicyExceptionRegistry()

    def evaluate(self, result: ScanResult, config: dict[str, Any]) -> list[PolicyResult]:
        policies = config.get("policies", {}).get("policies", {})
        evaluations: list[PolicyResult] = []

        if policies.get("no_secret_disclosure", {}).get("enabled", False):
            evaluations.append(self._evaluate_sensitive_marker_policy(result.findings, policies["no_secret_disclosure"]))

        if policies.get("severity_threshold", {}).get("enabled", False):
            evaluations.append(self._evaluate_severity_threshold(result, policies["severity_threshold"]))

        if policies.get("tool_execution_requires_allowlist", {}).get("enabled", False):
            evaluations.append(self._evaluate_tool_allowlist_policy(result, config, policies["tool_execution_requires_allowlist"]))

        if policies.get("rag_corpus_integrity_required", {}).get("enabled", False):
            evaluations.append(self._evaluate_rag_integrity_policy(result, config, policies["rag_corpus_integrity_required"]))

        if policies.get("critical_ai_action_requires_human_approval", {}).get("enabled", False):
            evaluations.append(self._evaluate_approval_policy(result, config, policies["critical_ai_action_requires_human_approval"]))

        return self.exception_registry.apply(result, evaluations)

    def _evaluate_sensitive_marker_policy(self, findings: list[Finding], policy: dict[str, Any]) -> PolicyResult:
        markers = [str(item).lower() for item in policy.get("patterns", [])]
        matches: list[dict[str, str]] = []

        for finding in findings:
            for interaction in finding.evidence.get("interaction_evidence", []):
                text = str(interaction.get("response_preview", "")).lower()
                for marker in markers:
                    if marker and marker in text:
                        matches.append({"finding": finding.title, "payload_id": str(interaction.get("payload_id", "")), "marker": marker})

        if matches:
            return PolicyResult(
                policy_id="no_secret_disclosure",
                status="fail",
                decision=policy.get("decision", "fail_on_high"),
                message="Sensitive data markers were found in observed target responses.",
                evidence={"matches": matches, "scope": "observed_response_preview_only"},
            )

        return PolicyResult(
            policy_id="no_secret_disclosure",
            status="pass",
            decision=policy.get("decision", "fail_on_high"),
            message="No configured sensitive data markers were found in observed target responses.",
            evidence={"markers_checked": markers, "scope": "observed_response_preview_only"},
        )

    def _evaluate_severity_threshold(self, result: ScanResult, policy: dict[str, Any]) -> PolicyResult:
        maximum = str(policy.get("maximum_allowed_severity", "high")).lower()
        observed = result.highest_severity.lower()
        if SEVERITY_ORDER.get(observed, 0) > SEVERITY_ORDER.get(maximum, 3):
            return PolicyResult(
                policy_id="severity_threshold",
                status="fail",
                decision=policy.get("decision", "fail_on_critical"),
                message=f"Highest severity '{observed}' exceeds maximum allowed severity '{maximum}'.",
                evidence={"highest_severity": observed, "maximum_allowed_severity": maximum},
            )
        return PolicyResult(
            policy_id="severity_threshold",
            status="pass",
            decision=policy.get("decision", "fail_on_critical"),
            message=f"Highest severity '{observed}' is within maximum allowed severity '{maximum}'.",
            evidence={"highest_severity": observed, "maximum_allowed_severity": maximum},
        )

    def _evaluate_tool_allowlist_policy(self, result: ScanResult, config: dict[str, Any], policy: dict[str, Any]) -> PolicyResult:
        if result.profile_name != "agent":
            return PolicyResult(
                policy_id="tool_execution_requires_allowlist",
                status="pass",
                decision=policy.get("decision", "fail_on_medium"),
                message="Agent tool allowlist policy is not applicable to this profile.",
                evidence={"profile": result.profile_name},
            )

        validation = self._validate_agent_runtime(config)
        execution = self._run_agent_execution(config)
        status = "fail" if "fail" in {validation.status, execution.status} else "warn" if "warn" in {validation.status, execution.status} else "pass"
        return PolicyResult(
            policy_id="tool_execution_requires_allowlist",
            status=status,
            decision=policy.get("decision", "fail_on_medium"),
            message=f"Agent tool and execution governance validation completed with status: {status}.",
            evidence={
                "manifest_path": validation.manifest_path,
                "tool_count": validation.tool_count,
                "memory_store_count": validation.memory_store_count,
                "runtime_errors": validation.errors,
                "runtime_warnings": validation.warnings,
                "execution_status": execution.status,
                "execution_scenario_count": execution.scenario_count,
                "execution_passed_count": execution.passed_count,
                "execution_failed_count": execution.failed_count,
                "execution_results": self._serialise_agent_execution_results(execution),
            },
        )

    def _evaluate_rag_integrity_policy(self, result: ScanResult, config: dict[str, Any], policy: dict[str, Any]) -> PolicyResult:
        if result.profile_name != "rag":
            return PolicyResult(
                policy_id="rag_corpus_integrity_required",
                status="pass",
                decision=policy.get("decision", "warn"),
                message="RAG corpus integrity policy is not applicable to this profile.",
                evidence={"profile": result.profile_name},
            )

        corpus = config.get("default", {}).get("rag_corpus", {})
        manifest_path = corpus.get("manifest_path")
        if not manifest_path:
            return PolicyResult(
                policy_id="rag_corpus_integrity_required",
                status="warn",
                decision=policy.get("decision", "warn"),
                message="RAG profile selected but no corpus manifest is configured.",
                evidence={"configured": corpus},
            )

        corpus_validation = CorpusManifestValidator().validate(Path(manifest_path))
        retrieval = LocalRetrievalHarness(
            corpus_manifest_path=manifest_path,
            scenario_path=corpus.get("retrieval_scenarios_path", "config/rag_retrieval_scenarios.yaml"),
        ).run()
        status = "fail" if "fail" in {corpus_validation.status, retrieval.status} else "warn" if "warn" in {corpus_validation.status, retrieval.status} else "pass"
        return PolicyResult(
            policy_id="rag_corpus_integrity_required",
            status=status,
            decision=policy.get("decision", "warn"),
            message=f"RAG corpus and retrieval validation completed with status: {status}.",
            evidence={
                "manifest_path": corpus_validation.manifest_path,
                "document_count": corpus_validation.document_count,
                "corpus_errors": corpus_validation.errors,
                "corpus_warnings": corpus_validation.warnings,
                "retrieval_status": retrieval.status,
                "retrieval_scenario_count": retrieval.scenario_count,
                "retrieval_passed_count": retrieval.passed_count,
                "retrieval_failed_count": retrieval.failed_count,
                "minimum_source_trust_score": retrieval.minimum_source_trust_score,
                "retrieval_results": [
                    {
                        "scenario_id": item.scenario_id,
                        "status": item.status,
                        "retrieved_documents": item.retrieved_documents,
                        "source_trust_score": item.source_trust_score,
                        "errors": item.errors,
                        "warnings": item.warnings,
                    }
                    for item in retrieval.results
                ],
            },
        )

    def _evaluate_approval_policy(self, result: ScanResult, config: dict[str, Any], policy: dict[str, Any]) -> PolicyResult:
        if result.profile_name == "agent":
            validation = self._validate_agent_runtime(config)
            execution = self._run_agent_execution(config)
            status = "fail" if "fail" in {validation.status, execution.status} else "warn" if "warn" in {validation.status, execution.status} else "pass"
            return PolicyResult(
                policy_id="critical_ai_action_requires_human_approval",
                status=status,
                decision=policy.get("decision", "fail_on_high"),
                message=f"Agent approval, memory, and orchestration validation completed with status: {status}.",
                evidence={
                    "manifest_path": validation.manifest_path,
                    "tool_count": validation.tool_count,
                    "memory_store_count": validation.memory_store_count,
                    "runtime_errors": validation.errors,
                    "runtime_warnings": validation.warnings,
                    "execution_status": execution.status,
                    "execution_scenario_count": execution.scenario_count,
                    "execution_passed_count": execution.passed_count,
                    "execution_failed_count": execution.failed_count,
                    "execution_results": self._serialise_agent_execution_results(execution),
                },
            )

        approval = config.get("default", {}).get("approval_gates", {})
        if not approval.get("high_impact_actions_require_approval", False):
            return PolicyResult(
                policy_id="critical_ai_action_requires_human_approval",
                status="warn",
                decision=policy.get("decision", "fail_on_high"),
                message="Human approval gate for high-impact AI actions is not configured.",
                evidence={"configured": approval},
            )

        return PolicyResult(
            policy_id="critical_ai_action_requires_human_approval",
            status="pass",
            decision=policy.get("decision", "fail_on_high"),
            message="Human approval gate for high-impact AI actions is configured.",
            evidence={"configured": approval},
        )

    @staticmethod
    def _validate_agent_runtime(config: dict[str, Any]):
        manifest_path = config.get("default", {}).get("agent_runtime", {}).get("manifest_path", "config/agent_runtime.yaml")
        return AgentRuntimeValidator().validate(Path(manifest_path))

    @staticmethod
    def _run_agent_execution(config: dict[str, Any]):
        agent_config = config.get("default", {}).get("agent_runtime", {})
        return AgentExecutionHarness(
            runtime_manifest_path=agent_config.get("manifest_path", "config/agent_runtime.yaml"),
            scenario_path=agent_config.get("execution_scenarios_path", "config/agent_execution_scenarios.yaml"),
        ).run()

    @staticmethod
    def _serialise_agent_execution_results(execution) -> list[dict[str, Any]]:
        return [
            {
                "scenario_id": item.scenario_id,
                "status": item.status,
                "observed_status": item.observed_status,
                "expected_status": item.expected_status,
                "tool_call_count": item.tool_call_count,
                "memory_write_count": item.memory_write_count,
                "errors": item.errors,
                "warnings": item.warnings,
            }
            for item in execution.results
        ]
