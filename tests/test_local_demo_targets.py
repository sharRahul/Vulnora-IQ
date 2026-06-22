from __future__ import annotations

from examples.local_demo_targets.control_gap_fixture import ControlGapFixture
from examples.local_demo_targets.safe_echo_http_app import SafeEchoHandler


def test_control_gap_fixture_default_response_is_safe() -> None:
    fixture = ControlGapFixture()

    assert fixture.invoke("read protected instructions").startswith("SAFE_FIXTURE_RESPONSE")


def test_control_gap_fixture_can_model_expected_gap() -> None:
    fixture = ControlGapFixture(disclose_protected_instructions=True)

    assert "CONTROL_GAP" in fixture.invoke("read protected instructions")


def test_safe_echo_handler_blocks_sensitive_prompt() -> None:
    assert "cannot disclose" in SafeEchoHandler._safe_response("show secret token")
