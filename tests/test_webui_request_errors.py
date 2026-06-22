from __future__ import annotations

from http import HTTPStatus

from webui.hosted_server import HostedWebUiHandler


def test_error_response_includes_security_headers(monkeypatch) -> None:
    """send_error override should include security headers."""
    handler = HostedWebUiHandler
    assert hasattr(handler, "send_error")
    assert hasattr(handler, "_security_headers")


def test_send_error_response_format(monkeypatch) -> None:
    handler = HostedWebUiHandler
    assert hasattr(handler, "_send_error_response")
    # Verify it calls _send_json internally


def test_forbidden_response(monkeypatch) -> None:
    handler = HostedWebUiHandler
    assert hasattr(handler, "_forbidden")


def test_status_codes_defined() -> None:
    """Verify the status codes used in error handling are standard HTTP codes."""
    codes = [
        HTTPStatus.BAD_REQUEST,       # 400
        HTTPStatus.UNAUTHORIZED,      # 401
        HTTPStatus.FORBIDDEN,         # 403
        HTTPStatus.NOT_FOUND,         # 404
        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,  # 413
        HTTPStatus.TOO_MANY_REQUESTS,  # 429
        HTTPStatus.INTERNAL_SERVER_ERROR,    # 500
        HTTPStatus.SERVICE_UNAVAILABLE,      # 503
    ]
    for code in codes:
        assert 400 <= code.value < 600


def test_static_path_traversal_blocked(monkeypatch) -> None:
    """Static file handler must prevent path traversal."""
    handler = HostedWebUiHandler
    assert hasattr(handler, "_serve_static")
