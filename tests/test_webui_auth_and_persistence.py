from __future__ import annotations

from webui.auth import WebAuthManager
from webui.persistent_jobs import PersistentJobStore


def test_auth_manager_anonymous_role_when_disabled() -> None:
    manager = WebAuthManager()
    principal = manager.authenticate_token(None)

    assert principal is not None
    assert principal.username == "anonymous"
    assert manager.can(principal, "start_demo_scan")
    assert not manager.can(principal, "start_configured_scan")


def test_role_permissions_include_inherited_permissions() -> None:
    manager = WebAuthManager()
    permissions = manager.permissions_for_role("admin")

    assert "view_scans" in permissions
    assert "download_artifacts" in permissions
    assert "start_demo_scan" in permissions
    assert "start_configured_scan" in permissions


def test_persistent_job_store_survives_reopen(tmp_path) -> None:
    path = tmp_path / "jobs.json"
    store = PersistentJobStore(path)
    job = store.create("demo", "baseline", False, created_by="tester")
    store.update(job.id, lambda item: (setattr(item, "status", "completed"), item.add_event("completed", "done", 100)))

    reopened = PersistentJobStore(path)
    loaded = reopened.get(job.id)

    assert loaded is not None
    assert loaded.status == "completed"
    assert loaded.created_by == "tester"
    assert loaded.events[-1].stage == "completed"
