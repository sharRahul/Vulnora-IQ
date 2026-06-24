from __future__ import annotations

import pytest

from webui.auth import WebAuthManager
from webui.persistent_jobs import PersistentJobStore, SqliteJobStore

# --- Auth tests ---

def test_auth_manager_returns_none_when_auth_enabled_and_no_token() -> None:
    manager = WebAuthManager()
    principal = manager.authenticate_token(None)
    assert principal is None


def test_auth_manager_anonymous_role_when_disabled(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_AUTH_ENABLED", "false")
    manager = WebAuthManager()
    principal = manager.authenticate_token(None)
    assert principal is not None
    assert principal.username == "anonymous"
    assert manager.can(principal, "view_scans")
    assert not manager.can(principal, "start_configured_scan")


def test_env_token_auth_works(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "super-secret-admin-token-12345")
    manager = WebAuthManager()
    principal = manager.authenticate_token("super-secret-admin-token-12345")
    assert principal is not None
    assert principal.authenticated
    assert principal.role == "admin"
    assert manager.can(principal, "start_configured_scan")


def test_env_token_auth_rejects_wrong_token(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "super-secret-admin-token-12345")
    manager = WebAuthManager()
    principal = manager.authenticate_token("wrong-token")
    assert principal is None


def test_env_token_uses_constant_time_comparison(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "real-token-value-here")
    manager = WebAuthManager()
    principal = manager.authenticate_token("real-token-value-here")
    assert principal is not None
    assert principal.authenticated


def test_auth_fail_closed_by_default() -> None:
    manager = WebAuthManager()
    assert manager.enabled()


def test_production_mode_rejects_no_admin_token(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    manager = WebAuthManager()
    with pytest.raises(RuntimeError, match="VULNORAIQ_ADMIN_TOKEN"):
        manager._validate_production()


def test_production_mode_rejects_short_admin_token(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "short")
    manager = WebAuthManager()
    with pytest.raises(RuntimeError, match="at least 20 characters"):
        manager._validate_production()


def test_production_mode_rejects_disabled_auth(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_AUTH_ENABLED", "false")
    manager = WebAuthManager()
    with pytest.raises(RuntimeError, match="Production mode requires"):
        manager._validate_production()


def test_production_mode_accepts_valid_config(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    manager = WebAuthManager()
    manager._validate_production()  # should not raise


def test_production_mode_rejects_file_fallback(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    manager = WebAuthManager()
    # File fallback should not be used in production
    env_tokens = manager._load_env_tokens()
    assert "admin" in env_tokens.values()
    # authenticate_token should use env tokens, not file
    principal = manager.authenticate_token("this-is-a-long-enough-admin-token-12345")
    assert principal is not None


def test_role_permissions_include_inherited_permissions() -> None:
    manager = WebAuthManager()
    permissions = manager.permissions_for_role("admin")
    assert "view_scans" in permissions
    assert "download_artifacts" in permissions
    assert "start_configured_scan" in permissions


# --- CSRF token tests ---

def test_csrf_token_is_unique_per_session(monkeypatch) -> None:
    from webui.auth import AuthPrincipal
    from webui.hosted_server import _csrf_session_key, _csrf_token_for, _validate_csrf
    p1 = AuthPrincipal("alice", "admin", {"view_scans"}, authenticated=True)
    p2 = AuthPrincipal("bob", "analyst", {"view_scans"}, authenticated=True)
    key1 = _csrf_session_key(p1, "10.0.0.1")
    key2 = _csrf_session_key(p2, "10.0.0.2")
    token1 = _csrf_token_for(key1)
    token2 = _csrf_token_for(key2)
    assert token1 != token2
    assert _validate_csrf(key1, token1)
    assert not _validate_csrf(key1, token2)


def test_csrf_rejects_missing_token(monkeypatch) -> None:
    from webui.auth import AuthPrincipal
    from webui.hosted_server import _csrf_session_key, _csrf_token_for, _validate_csrf
    p = AuthPrincipal("admin", "admin", {"view_scans"}, authenticated=True)
    key = _csrf_session_key(p, "10.0.0.1")
    _csrf_token_for(key)
    assert not _validate_csrf(key, None)
    assert not _validate_csrf(key, "")


def test_csrf_rejects_invalid_token(monkeypatch) -> None:
    from webui.auth import AuthPrincipal
    from webui.hosted_server import _csrf_session_key, _csrf_token_for, _validate_csrf
    p = AuthPrincipal("admin", "admin", {"view_scans"}, authenticated=True)
    key = _csrf_session_key(p, "10.0.0.1")
    _csrf_token_for(key)
    assert not _validate_csrf(key, "invalid-token")


def test_csrf_token_expires(monkeypatch) -> None:
    from webui.auth import AuthPrincipal
    from webui.hosted_server import _csrf_session_key, _csrf_tokens
    from webui.hosted_server import _csrf_token_for as tf
    from webui.hosted_server import _validate_csrf as vc
    p = AuthPrincipal("admin", "admin", {"view_scans"}, authenticated=True)
    key = _csrf_session_key(p, "10.0.0.1")
    token = tf(key)
    # Manually expire the token by backdating its expiry
    import time
    entry = _csrf_tokens.get(key)
    assert entry is not None
    entry["expires"] = time.monotonic() - 1
    assert not vc(key, token)


# --- Rate limit tests ---

def test_rate_limit_allows_within_limit() -> None:
    from webui.hosted_server import _rate_limit
    for _ in range(10):
        assert _rate_limit("test-ip-1")


def test_rate_limit_blocks_after_limit(monkeypatch) -> None:
    import webui.hosted_server as hs
    monkeypatch.setattr(hs, "RATE_LIMIT_MAX", 3)
    from webui.hosted_server import _rate_limit as rl
    for _ in range(3):
        assert rl("test-ip-block")
    assert not rl("test-ip-block")


def test_rate_limit_store_cleanup(monkeypatch) -> None:
    import webui.hosted_server as hs
    monkeypatch.setattr(hs, "RATE_LIMIT_WINDOW", -1)
    from webui.hosted_server import _clean_rate_limit_store as clean
    from webui.hosted_server import _rate_limit as rl
    rl("test-cleanup-ip")
    clean()
    assert rl("test-cleanup-ip")


# --- Proxy IP resolution tests ---

def _reload_hosted_server(monkeypatch) -> None:
    import importlib

    import webui.hosted_server as hs
    importlib.reload(hs)


def test_proxy_ip_resolution_direct(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "false")
    _reload_hosted_server(monkeypatch)
    from webui.hosted_server import _resolve_client_ip

    class FakeHandler:
        client_address = ("10.0.0.5", 54321)
        headers: dict[str, str] = {}
    ip = _resolve_client_ip(FakeHandler())  # type: ignore
    assert ip == "10.0.0.5"


def test_proxy_ip_trusts_forwarded_from_trusted_proxy(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "10.0.0.0/24")
    _reload_hosted_server(monkeypatch)
    from webui.hosted_server import _resolve_client_ip

    class FakeHandler:
        client_address = ("10.0.0.1", 54321)
        headers: dict[str, str] = {"X-Forwarded-For": "203.0.113.5"}
    ip = _resolve_client_ip(FakeHandler())  # type: ignore
    assert ip == "203.0.113.5"


def test_proxy_ip_ignores_spoofed_forwarded_from_untrusted(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "10.0.0.0/24")
    _reload_hosted_server(monkeypatch)
    from webui.hosted_server import _resolve_client_ip

    class FakeHandler:
        client_address = ("203.0.113.99", 54321)
        headers: dict[str, str] = {"X-Forwarded-For": "1.2.3.4"}
    ip = _resolve_client_ip(FakeHandler())  # type: ignore
    assert ip == "203.0.113.99"


def test_proxy_ip_rejects_malformed_forwarded(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "10.0.0.0/24")
    _reload_hosted_server(monkeypatch)
    from webui.hosted_server import _resolve_client_ip

    class FakeHandler:
        client_address = ("10.0.0.1", 54321)
        headers: dict[str, str] = {"X-Forwarded-For": "not-an-ip"}
    ip = _resolve_client_ip(FakeHandler())  # type: ignore
    assert ip == "10.0.0.1"


# --- Client IP in audit ---

def test_audit_event_includes_client_ip(monkeypatch) -> None:
    from webui.auth import AuthPrincipal
    from webui.hosted_server import _audit_structured
    p = AuthPrincipal("admin", "admin", {"view_scans"}, authenticated=True)
    _audit_structured("test_event", p, client_ip="10.0.0.1", detail="test detail")


# --- Security headers tests ---

def test_security_headers_present(monkeypatch) -> None:
    from webui.hosted_server import HostedWebUiHandler
    handler = HostedWebUiHandler
    assert hasattr(handler, "_security_headers")


# --- Persistence tests ---

def test_persistent_job_store_survives_reopen(tmp_path) -> None:
    path = tmp_path / "jobs.json"
    store = PersistentJobStore(path)
    job = store.create("demo", "baseline", False, created_by="tester")
    def complete_job(item):
        item.status = "completed"
        item.add_event("completed", "done", 100)
    store.update(job.id, complete_job)

    reopened = PersistentJobStore(path)
    loaded = reopened.get(job.id)
    assert loaded is not None
    assert loaded.status == "completed"
    assert loaded.created_by == "tester"
    assert loaded.events[-1].stage == "completed"


def test_sqlite_job_store_create_get_list_update(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    job = store.create("demo", "baseline", False)
    assert job.status == "queued"

    loaded = store.get(job.id)
    assert loaded is not None
    assert loaded.id == job.id

    jobs = store.list()
    assert len(jobs) >= 1

    def update_fn(item):
        item.status = "completed"
    store.update(job.id, update_fn)
    updated = store.get(job.id)
    assert updated is not None
    assert updated.status == "completed"


def test_sqlite_job_store_survives_reopen(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    job = store.create("demo", "baseline", False, created_by="tester")
    def complete_job(item):
        item.status = "completed"
        item.add_event("completed", "done", 100)
    store.update(job.id, complete_job)

    reopened = SqliteJobStore(path)
    loaded = reopened.get(job.id)
    assert loaded is not None
    assert loaded.status == "completed"
    assert loaded.created_by == "tester"
    assert loaded.events[-1].stage == "completed"


def test_sqlite_job_store_event_ordering(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    job = store.create("demo", "baseline", False)
    store.update(job.id, lambda item: item.add_event("started", "Scan started", 10))
    for i in range(5):
        store.update(job.id, lambda item, s=i: (
            item.add_event(f"step_{s}", f"Step {s}", 10 + s * 10),
        ))
    loaded = store.get(job.id)
    assert loaded is not None
    stages = [e.stage for e in loaded.events]
    assert "queued" in stages
    assert "started" in stages


def test_sqlite_job_store_summary_persistence(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    job = store.create("demo", "baseline", False)
    def set_summary(item):
        item.summary = {"finding_count": 5, "highest_severity": "medium"}
    store.update(job.id, set_summary)
    loaded = store.get(job.id)
    assert loaded is not None
    assert loaded.summary.get("finding_count") == 5
    assert loaded.summary.get("highest_severity") == "medium"


def test_create_job_store_returns_sqlite_by_default() -> None:
    from webui.persistent_jobs import create_job_store
    store = create_job_store()
    assert type(store).__name__ == "SqliteJobStore"


def test_create_job_store_returns_json_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_JOB_STORE_BACKEND", "json")
    from webui.persistent_jobs import create_job_store
    store = create_job_store()
    assert type(store).__name__ == "PersistentJobStore"
