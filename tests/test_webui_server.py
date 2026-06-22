from __future__ import annotations

from pathlib import Path

import pytest

import webui.server as web_server
from webui.server import JobStore, ScanJob, validate_scan_request


def test_validate_scan_request_accepts_demo_defaults() -> None:
    target, profile, authorised = validate_scan_request({})

    assert target == "demo"
    assert profile == "baseline"
    assert authorised is False


def test_validate_scan_request_rejects_unknown_target() -> None:
    with pytest.raises(ValueError):
        validate_scan_request({"target": "missing", "profile": "baseline"})


def test_scan_job_serialisation_can_exclude_events() -> None:
    job = ScanJob(id="job1", target="demo", profile="baseline", authorised=False)
    job.add_event("queued", "queued", 0)

    data = job.to_dict(include_events=False)

    assert data["id"] == "job1"
    assert "events" not in data


def test_job_store_create_and_list() -> None:
    store = JobStore()

    job = store.create("demo", "baseline", False)

    assert store.get(job.id) is job
    assert store.list()[0].id == job.id


def test_run_scan_job_generates_webui_outputs(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(web_server, "OUTPUT_ROOT", Path(tmp_path))
    store = JobStore()
    monkeypatch.setattr(web_server, "JOB_STORE", store)
    job = store.create("demo", "baseline", False)

    web_server.run_scan_job(job.id)

    completed = store.get(job.id)
    assert completed is not None
    assert completed.status == "completed"
    assert completed.progress == 100
    assert completed.summary["finding_count"] >= 1
    assert set(completed.outputs) == {"markdown", "json", "sarif", "dashboard_markdown", "dashboard_html"}
    assert all(Path(path).exists() for path in completed.outputs.values())
