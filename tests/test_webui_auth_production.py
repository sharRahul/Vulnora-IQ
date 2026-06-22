from __future__ import annotations

import pytest

from webui.auth import WebAuthManager


def test_production_mode_rejects_disabled_auth(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    monkeypatch.setenv("VULNORAIQ_AUTH_ENABLED", "false")
    manager = WebAuthManager()
    with pytest.raises(RuntimeError, match="Production mode requires"):
        manager._validate_production()


def test_production_mode_accepts_valid_config(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    manager = WebAuthManager()
    manager._validate_production()


def test_production_mode_rejects_short_token(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "short")
    manager = WebAuthManager()
    with pytest.raises(RuntimeError, match="at least 20 characters"):
        manager._validate_production()


def test_production_mode_rejects_no_admin_token(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    manager = WebAuthManager()
    with pytest.raises(RuntimeError, match="VULNORAIQ_ADMIN_TOKEN"):
        manager._validate_production()


def test_production_mode_disables_internal_admin_token(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    manager = WebAuthManager()
    principal = manager.authenticate_token("vulnoraiq-internal-admin-token")
    assert principal is None


def test_production_mode_rejects_file_fallback(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    manager = WebAuthManager()
    principal = manager.authenticate_token("this-is-a-long-enough-admin-token-12345")
    assert principal is not None
    assert principal.authenticated
    assert principal.role == "admin"


def test_proxy_identity_from_trusted_source(monkeypatch) -> None:
    manager = WebAuthManager()
    principal = manager.authenticate_proxy_identity(
        {"X-Authenticated-User": "alice", "X-VulnoraIQ-Role": "admin"},
        trusted=True,
    )
    assert principal is not None
    assert principal.authenticated
    assert principal.username == "proxy:alice"
    assert principal.role == "admin"


def test_proxy_identity_rejected_from_untrusted_source(monkeypatch) -> None:
    manager = WebAuthManager()
    principal = manager.authenticate_proxy_identity(
        {"X-Authenticated-User": "alice", "X-VulnoraIQ-Role": "admin"},
        trusted=False,
    )
    assert principal is None


def test_proxy_identity_defaults_to_viewer(monkeypatch) -> None:
    manager = WebAuthManager()
    principal = manager.authenticate_proxy_identity(
        {"X-Authenticated-User": "bob"},
        trusted=True,
    )
    assert principal is not None
    assert principal.role == "viewer"


def test_proxy_identity_maps_roles(monkeypatch) -> None:
    manager = WebAuthManager()
    for header_role, expected in [("admin", "admin"), ("analyst", "analyst"), ("viewer", "viewer"), ("unknown", "viewer")]:
        principal = manager.authenticate_proxy_identity(
            {"X-Authenticated-User": "user", "X-VulnoraIQ-Role": header_role},
            trusted=True,
        )
        assert principal is not None
        assert principal.role == expected, f"Expected {expected} for role {header_role}, got {principal.role}"


def test_proxy_identity_permissions(monkeypatch) -> None:
    manager = WebAuthManager()
    principal = manager.authenticate_proxy_identity(
        {"X-Authenticated-User": "admin-user", "X-VulnoraIQ-Role": "admin"},
        trusted=True,
    )
    assert principal is not None
    assert manager.can(principal, "start_configured_scan")
    assert manager.can(principal, "manage_runtime")

    viewer = manager.authenticate_proxy_identity(
        {"X-Authenticated-User": "viewer-user", "X-VulnoraIQ-Role": "viewer"},
        trusted=True,
    )
    assert viewer is not None
    assert not manager.can(viewer, "start_demo_scan")
    assert manager.can(viewer, "view_scans")


def test_proxy_identity_requires_username(monkeypatch) -> None:
    manager = WebAuthManager()
    principal = manager.authenticate_proxy_identity(
        {"X-VulnoraIQ-Role": "admin"},
        trusted=True,
    )
    assert principal is None


def test_token_and_proxy_auth_modes(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "real-admin-token-here-12345")
    manager = WebAuthManager()
    assert manager.auth_mode() == "token"
    principal = manager.authenticate_token("real-admin-token-here-12345")
    assert principal is not None
    assert principal.authenticated


def test_auth_fail_closed_by_default() -> None:
    manager = WebAuthManager()
    assert manager.enabled()


def test_constant_time_comparison(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "real-token-value-here")
    monkeypatch.setenv("VULNORAIQ_ANALYST_TOKEN", "analyst-token-here")
    manager = WebAuthManager()
    p1 = manager.authenticate_token("real-token-value-here")
    assert p1 is not None
    assert p1.role == "admin"
    p2 = manager.authenticate_token("wrong-token")
    assert p2 is None
    p3 = manager.authenticate_token("analyst-token-here")
    assert p3 is not None
    assert p3.role == "analyst"
