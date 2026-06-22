from __future__ import annotations

from typing import Any

from scripts.backup_sqlite_store import backup, validate_backup
from scripts.restore_sqlite_store import restore
from webui.persistent_jobs import SqliteJobStore


def test_backup_and_validate(tmp_path) -> None:
    db_path = tmp_path / "source.db"
    store = SqliteJobStore(db_path)
    store.create("demo", "baseline", False)
    backup_path = tmp_path / "backup.db"
    result: dict[str, Any] = backup(str(db_path), str(backup_path), validate=True)
    assert result["validation"]["status"] == "ok"


def test_backup_compress(tmp_path) -> None:
    db_path = tmp_path / "source.db"
    store = SqliteJobStore(db_path)
    store.create("demo", "baseline", False)
    backup_path = tmp_path / "backup.db"
    result: dict[str, Any] = backup(str(db_path), str(backup_path), compress=True)
    assert result.get("compressed") is True
    assert str(result["destination"]).endswith(".gz")


def test_restore(tmp_path) -> None:
    db_path = tmp_path / "source.db"
    store = SqliteJobStore(db_path)
    store.create("demo", "baseline", False)
    backup_path = tmp_path / "backup.db"
    backup(str(db_path), str(backup_path))
    restore_path = tmp_path / "restored.db"
    result: dict[str, Any] = restore(str(backup_path), str(restore_path), validate=True)
    assert result["validation"]["status"] == "ok"


def test_restore_compressed_backup(tmp_path) -> None:
    db_path = tmp_path / "source.db"
    store = SqliteJobStore(db_path)
    store.create("demo", "baseline", False)
    back_path = tmp_path / "backup.db"
    result: dict[str, Any] = backup(str(db_path), str(back_path), compress=True)
    gz_path: str = str(result["destination"])
    restore_path = tmp_path / "restored.db"
    result2: dict[str, Any] = restore(gz_path, str(restore_path), validate=True)
    assert result2["validation"]["status"] == "ok"


def test_validate_backup_fails_for_nonexistent(tmp_path) -> None:
    result: dict[str, Any] = validate_backup(str(tmp_path / "nonexistent.db"))
    assert result["status"] == "error"
