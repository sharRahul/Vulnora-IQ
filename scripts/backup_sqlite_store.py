#!/usr/bin/env python3
"""SQLite online backup script using the SQLite backup API.

Usage:
    python scripts/backup_sqlite_store.py <source_db> <backup_destination>
    python scripts/backup_sqlite_store.py <source_db> <backup_destination> --compress
    python scripts/backup_sqlite_store.py <source_db> <backup_destination> --compress --retention 7
    python scripts/backup_sqlite_store.py <source_db> <backup_destination> --validate
"""

from __future__ import annotations

import argparse
import gzip
import logging
import shutil
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("backup_sqlite")


def backup(
    source_path: str,
    dest_path: str,
    compress: bool = False,
    validate: bool = False,
    retention_days: int = 0,
) -> dict[str, Any]:
    source = Path(source_path).resolve()
    dest = Path(dest_path).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source database not found: {source}")
    if not source.is_file():
        raise ValueError(f"Source is not a file: {source}")

    dest.parent.mkdir(parents=True, exist_ok=True)

    # Use online backup API
    src_conn = sqlite3.connect(str(source))
    backup_conn = sqlite3.connect(str(dest))
    start = time.monotonic()
    src_conn.backup(backup_conn, pages=1000, progress=None)
    elapsed = time.monotonic() - start
    backup_conn.close()
    src_conn.close()

    result = {
        "source": str(source),
        "destination": str(dest),
        "size_bytes": dest.stat().st_size,
        "elapsed_seconds": round(elapsed, 3),
    }

    if compress:
        gz_path = dest.with_suffix(dest.suffix + ".gz")
        with dest.open("rb") as f_in, gzip.open(str(gz_path), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        dest.unlink()
        result["compressed"] = True
        result["compressed_size_bytes"] = gz_path.stat().st_size
        result["destination"] = str(gz_path)

    if validate:
        validation = validate_backup(str(dest) if not compress else str(gz_path), compressed=compress)
        result["validation"] = validation

    if retention_days > 0:
        cleanup_old_backups(dest.parent, retention_days)
        result["retention_days"] = retention_days

    return result


def validate_backup(backup_path: str, compressed: bool = False) -> dict[str, Any]:
    path = Path(backup_path).resolve()
    if not path.exists():
        return {"status": "error", "error": "file not found"}

    try:
        if compressed:
            import gzip
            with gzip.open(str(path), "rb") as f:
                data = f.read(1024)
            if not data:
                return {"status": "error", "error": "compressed backup is empty"}
            # Validate decompressed content is valid SQLite
            tmp_path = path.parent / f".validate_{path.name}"
            with gzip.open(str(path), "rb") as f_in, open(str(tmp_path), "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            conn = sqlite3.connect(str(tmp_path))
        else:
            conn = sqlite3.connect(str(path))

        cursor = conn.execute("SELECT MAX(version) FROM _schema_version")
        schema_version = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM jobs")
        job_count = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]

        conn.close()

        if compressed and tmp_path.exists():
            tmp_path.unlink()

        return {
            "status": "ok",
            "schema_version": schema_version,
            "job_count": job_count,
            "event_count": event_count,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def cleanup_old_backups(directory: Path, retention_days: int) -> list[str]:
    removed: list[str] = []
    now = time.time()
    cutoff = now - (retention_days * 86400)
    for f in directory.iterdir():
        if f.is_file() and (f.suffix in (".db", ".db.gz") or f.name.endswith(".db") or f.name.endswith(".db.gz")):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                removed.append(str(f))
    return removed


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Backup SQLite job store with online backup API.")
    parser.add_argument("source", help="Path to source SQLite database")
    parser.add_argument("destination", help="Backup destination path")
    parser.add_argument("--compress", action="store_true", help="Compress backup with gzip")
    parser.add_argument("--validate", action="store_true", help="Validate backup after creation")
    parser.add_argument("--retention", type=int, default=0, help="Remove backups older than N days")
    args = parser.parse_args()

    try:
        result = backup(
            source_path=args.source,
            dest_path=args.destination,
            compress=args.compress,
            validate=args.validate,
            retention_days=args.retention,
        )
        LOGGER.info("Backup completed: %s -> %s (%.1f MB in %.2fs)",
                    result["source"], result["destination"],
                    result["size_bytes"] / (1024 * 1024),
                    result["elapsed_seconds"])
        if result.get("validation"):
            v = result["validation"]
            if v.get("status") == "ok":
                LOGGER.info("Validation passed: schema v%s, %d jobs, %d events",
                            v.get("schema_version"), v.get("job_count"), v.get("event_count"))
            else:
                LOGGER.error("Validation failed: %s", v.get("error"))
                sys.exit(1)
    except Exception as exc:
        LOGGER.error("Backup failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
