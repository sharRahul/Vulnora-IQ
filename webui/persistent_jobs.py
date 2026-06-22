from __future__ import annotations

import json
import os
import sqlite3
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Protocol, runtime_checkable


@dataclass(slots=True)
class PersistedScanEvent:
    timestamp: str
    stage: str
    message: str
    progress: int
    level: str = "info"


@dataclass(slots=True)
class PersistedScanJob:
    id: str
    target: str
    profile: str
    authorised: bool
    created_by: str = "anonymous"
    status: str = "queued"
    progress: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    events: list[PersistedScanEvent] = field(default_factory=list)
    outputs: dict[str, str] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)

    def add_event(self, stage: str, message: str, progress: int, level: str = "info") -> None:
        self.progress = progress
        self.events.append(PersistedScanEvent(datetime.now(timezone.utc).isoformat(), stage, message, progress, level))

    def to_dict(self, include_events: bool = True) -> dict[str, Any]:
        data = asdict(self)
        if not include_events:
            data.pop("events", None)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PersistedScanJob:
        events = [PersistedScanEvent(**event) for event in data.get("events", [])]
        data = {**data, "events": events}
        return cls(**data)


@runtime_checkable
class JobStore(Protocol):
    """Storage interface for scan job persistence."""

    def create(self, target: str, profile: str, authorised: bool, created_by: str = "anonymous") -> PersistedScanJob:
        ...

    def get(self, job_id: str) -> PersistedScanJob | None:
        ...

    def list(self) -> list[PersistedScanJob]:
        ...

    def update(self, job_id: str, fn) -> PersistedScanJob | None:
        ...


class PersistentJobStore:
    """JSON-backed scan job store. Backward-compatible name for JsonJobStore."""

    def __init__(self, path: str | Path = "reports/output/webui/jobs.json") -> None:
        self.path = Path(path)
        self._lock = RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def create(self, target: str, profile: str, authorised: bool, created_by: str = "anonymous") -> PersistedScanJob:
        job = PersistedScanJob(uuid.uuid4().hex[:12], target, profile, authorised, created_by=created_by)
        job.add_event("queued", "Scan queued and waiting for worker thread.", 0)
        with self._lock:
            jobs = self._load_all()
            jobs[job.id] = job
            self._save_all(jobs)
        return job

    def get(self, job_id: str) -> PersistedScanJob | None:
        with self._lock:
            return self._load_all().get(job_id)

    def list(self) -> list[PersistedScanJob]:
        with self._lock:
            return sorted(self._load_all().values(), key=lambda item: item.created_at, reverse=True)

    def update(self, job_id: str, fn) -> PersistedScanJob | None:
        with self._lock:
            jobs = self._load_all()
            job = jobs.get(job_id)
            if not job:
                return None
            fn(job)
            jobs[job_id] = job
            self._save_all(jobs)
            return job

    def _load_all(self) -> dict[str, PersistedScanJob]:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text(encoding="utf-8") or "{}")
        return {job_id: PersistedScanJob.from_dict(value) for job_id, value in raw.items()}

    def _save_all(self, jobs: dict[str, PersistedScanJob]) -> None:
        self.path.write_text(
            json.dumps({job_id: job.to_dict() for job_id, job in jobs.items()}, indent=2, sort_keys=True),
            encoding="utf-8",
        )


class SqliteJobStore:
    """SQLite-backed scan job store for production use."""

    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path = "reports/output/webui/jobs.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;")
        self._lock = RLock()
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS _schema_version (
                version INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                profile TEXT NOT NULL,
                authorised INTEGER NOT NULL DEFAULT 0,
                created_by TEXT NOT NULL DEFAULT 'anonymous',
                status TEXT NOT NULL DEFAULT 'queued',
                progress INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                error TEXT,
                outputs TEXT NOT NULL DEFAULT '{}',
                summary TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                timestamp TEXT NOT NULL,
                stage TEXT NOT NULL,
                message TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                level TEXT NOT NULL DEFAULT 'info'
            );
            CREATE INDEX IF NOT EXISTS idx_events_job_id ON events(job_id);
            CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
        """)
        self._conn.commit()
        self._ensure_schema_version()

    def _ensure_schema_version(self) -> None:
        row = self._conn.execute("SELECT MAX(version) FROM _schema_version").fetchone()
        current_version = row[0] if row and row[0] else 0
        if current_version < self.SCHEMA_VERSION:
            self._conn.execute("INSERT OR REPLACE INTO _schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,))
            self._conn.commit()

    def create(self, target: str, profile: str, authorised: bool, created_by: str = "anonymous") -> PersistedScanJob:
        job = PersistedScanJob(uuid.uuid4().hex[:12], target, profile, authorised, created_by=created_by)
        job.add_event("queued", "Scan queued and waiting for worker thread.", 0)
        with self._lock:
            self._insert_job(job)
        return job

    def get(self, job_id: str) -> PersistedScanJob | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not row:
                return None
            return self._row_to_job(row)

    def list(self) -> list[PersistedScanJob]:
        with self._lock:
            rows = self._conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
            return [self._row_to_job(row) for row in rows]

    def update(self, job_id: str, fn) -> PersistedScanJob | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not row:
                return None
            job = self._row_to_job(row)
            fn(job)
            self._update_job(job)
            return job

    def _insert_job(self, job: PersistedScanJob) -> None:
        self._conn.execute(
            """INSERT INTO jobs (id, target, profile, authorised, created_by, status, progress,
               created_at, started_at, completed_at, error, outputs, summary)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job.id, job.target, job.profile, int(job.authorised), job.created_by,
                job.status, job.progress, job.created_at, job.started_at,
                job.completed_at, job.error,
                json.dumps(job.outputs, sort_keys=True),
                json.dumps(job.summary, default=str, sort_keys=True),
            ),
        )
        for ev in job.events:
            self._insert_event(job.id, ev)
        self._conn.commit()

    def _update_job(self, job: PersistedScanJob) -> None:
        self._conn.execute(
            """UPDATE jobs SET status=?, progress=?, started_at=?, completed_at=?, error=?,
               outputs=?, summary=? WHERE id=?""",
            (
                job.status, job.progress, job.started_at, job.completed_at, job.error,
                json.dumps(job.outputs, sort_keys=True),
                json.dumps(job.summary, default=str, sort_keys=True),
                job.id,
            ),
        )
        self._conn.execute("DELETE FROM events WHERE job_id = ?", (job.id,))
        for ev in job.events:
            self._insert_event(job.id, ev)
        self._conn.commit()

    def _insert_event(self, job_id: str, ev: PersistedScanEvent) -> None:
        self._conn.execute(
            "INSERT INTO events (job_id, timestamp, stage, message, progress, level) VALUES (?, ?, ?, ?, ?, ?)",
            (job_id, ev.timestamp, ev.stage, ev.message, ev.progress, ev.level),
        )

    def _row_to_job(self, row: sqlite3.Row) -> PersistedScanJob:
        events = self._conn.execute(
            "SELECT timestamp, stage, message, progress, level FROM events WHERE job_id = ? ORDER BY id",
            (row["id"],),
        ).fetchall()
        return PersistedScanJob(
            id=row["id"],
            target=row["target"],
            profile=row["profile"],
            authorised=bool(row["authorised"]),
            created_by=row["created_by"],
            status=row["status"],
            progress=row["progress"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            error=row["error"],
            events=[PersistedScanEvent(**dict(ev)) for ev in events],
            outputs=json.loads(row["outputs"] or "{}"),
            summary=json.loads(row["summary"] or "{}"),
        )


def create_job_store() -> JobStore:
    """Factory: returns SqliteJobStore or PersistentJobStore based on VULNORAIQ_JOB_STORE env var."""
    backend = os.getenv("VULNORAIQ_JOB_STORE_BACKEND", "sqlite").strip().lower()
    path = os.getenv("VULNORAIQ_JOB_STORE_PATH", "")
    if backend == "json":
        return PersistentJobStore(path or "reports/output/webui/jobs.json")
    return SqliteJobStore(path or "reports/output/webui/jobs.db")
