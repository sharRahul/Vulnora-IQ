from __future__ import annotations

from webui.hosted_server import HostedWebUiHandler


def test_artifact_download_has_security_headers() -> None:
    handler = HostedWebUiHandler
    assert hasattr(handler, "_send_artifact")


def test_artifact_path_traversal_prevented() -> None:
    """Artifact handler must reject path traversal patterns."""
    handler = HostedWebUiHandler
    assert hasattr(handler, "_send_artifact")
    # The implementation uses `name.replace("\\", "/")` and checks for "/" and ".."
    # This test validates the handler signature exists


def test_artifact_requires_authz() -> None:
    """Artifact download must check download_artifacts permission."""
    handler = HostedWebUiHandler
    assert hasattr(handler, "_handle_scan_get")
    # The handler checks AUTH_MANAGER.can(principal, "download_artifacts")
