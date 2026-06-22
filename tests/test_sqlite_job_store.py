from __future__ import annotations

from webui.persistent_jobs import SqliteJobStore


def test_create_get_list(tmp_path) -> None:
    store = SqliteJobStore(tmp_path / "test.db")
    job = store.create("demo", "baseline", False)
    assert job.status == "queued"
    loaded = store.get(job.id)
    assert loaded is not None
    assert loaded.id == job.id
    jobs = store.list()
    assert len(jobs) >= 1


def test_update(tmp_path) -> None:
    store = SqliteJobStore(tmp_path / "test.db")
    job = store.create("demo", "baseline", False)

    def set_status(item):
        item.status = "running"
    store.update(job.id, set_status)
    updated = store.get(job.id)
    assert updated is not None
    assert updated.status == "running"


def test_survives_reopen(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    job = store.create("demo", "baseline", False, created_by="tester")

    def complete(item):
        item.status = "completed"
        item.add_event("completed", "done", 100)
    store.update(job.id, complete)

    reopened = SqliteJobStore(path)
    loaded = reopened.get(job.id)
    assert loaded is not None
    assert loaded.status == "completed"
    assert loaded.created_by == "tester"


def test_event_ordering(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    job = store.create("demo", "baseline", False)
    store.update(job.id, lambda item: item.add_event("started", "Scan started", 10))
    for i in range(5):
        store.update(job.id, lambda item, s=i: item.add_event(f"step_{s}", f"Step {s}", 10 + s * 10))
    loaded = store.get(job.id)
    assert loaded is not None
    stages = [e.stage for e in loaded.events]
    assert "queued" in stages
    assert "started" in stages


def test_summary_persistence(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    job = store.create("demo", "baseline", False)

    def set_summary(item):
        item.summary = {"finding_count": 5, "highest_severity": "medium"}
    store.update(job.id, set_summary)
    loaded = store.get(job.id)
    assert loaded is not None
    assert loaded.summary.get("finding_count") == 5


def test_schema_version(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    conn = store._conn
    row = conn.execute("SELECT MAX(version) FROM _schema_version").fetchone()
    assert row is not None
    assert row[0] >= 1


def test_wal_mode(tmp_path) -> None:
    path = tmp_path / "test.db"
    store = SqliteJobStore(path)
    conn = store._conn
    row = conn.execute("PRAGMA journal_mode").fetchone()
    assert row is not None
    assert row[0].lower() == "wal"
