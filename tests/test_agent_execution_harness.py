from __future__ import annotations

from agent_testing.execution_harness import AgentExecutionHarness


def test_agent_execution_harness_passes_expected_scenarios() -> None:
    result = AgentExecutionHarness().run()

    assert result.status == "pass"
    assert result.scenario_count == 3
    assert result.failed_count == 0


def test_agent_execution_harness_validates_disallowed_action_as_expected_fail() -> None:
    result = AgentExecutionHarness().run()

    scenario = next(item for item in result.results if item.scenario_id == "agent-plan-002")
    assert scenario.status == "pass"
    assert scenario.tool_call_count == 1
