from __future__ import annotations

from pathlib import Path

from agent_testing.runtime_manifest import AgentRuntimeValidator
from core.scanner import Scanner


def test_agent_runtime_manifest_validates() -> None:
    result = AgentRuntimeValidator().validate(Path("config/agent_runtime.yaml"))

    assert result.status == "pass"
    assert result.tool_count == 3
    assert result.memory_store_count == 2
    assert not result.errors


def test_agent_profile_policy_uses_runtime_manifest() -> None:
    result = Scanner().scan(target_name="demo", profile_name="agent")

    tool_policy = next(policy for policy in result.policy_results if policy.policy_id == "tool_execution_requires_allowlist")
    approval_policy = next(policy for policy in result.policy_results if policy.policy_id == "critical_ai_action_requires_human_approval")

    assert tool_policy.status == "pass"
    assert approval_policy.status == "pass"
    assert tool_policy.evidence["tool_count"] == 3
    assert approval_policy.evidence["memory_store_count"] == 2
