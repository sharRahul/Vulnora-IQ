#!/usr/bin/env python3
"""SQLite restore script.

Usage:
    python scripts/restore_sqlite_store.py <backup_path> <restore_destination>
    python scripts/restore_sqlite_store.py <backup_path> <restore_destination> --validate
"""

from __future__ import annotations

import argparse
import gzip
import logging
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("restore_sqlite")


def restore(backup_path: str, dest_path: str, validate: bool = False) -> dict[str, Any]:
    backup_file = Path(backup_path).resolve()
    dest = Path(dest_path).resolve()

    if not backup_file.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    dest.parent.mkdir(parents=True, exist_ok=True)

    compressed = backup_file.suffix == ".gz"
    if compressed:
        LOGGER.info("Decompressing gzipped backup...")
        tmp_path = dest.parent / f".restore_{backup_file.stem.replace('.db', '')}.db"
        with gzip.open(str(backup_file), "rb") as f_in, open(str(tmp_path), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        restore_source = tmp_path
    else:
        restore_source = backup_file

    # Use SQLite backup API to restore
    src_conn = sqlite3.connect(str(restore_source))
    dest_conn = sqlite3.connect(str(dest))
    src_conn.backup(dest_conn, pages=1000, progress=None)
    dest_conn.close()
    src_conn.close()

    if compressed and restore_source.exists():
        restore_source.unlink()

    result = {"source": str(backup_file), "destination": str(dest), "size_bytes": dest.stat().st_size}

    if validate:
        conn = sqlite3.connect(str(dest))
        cursor = conn.execute("SELECT MAX(version) FROM _schema_version")
        schema_version = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM jobs")
        job_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        conn.close()
        result["validation"] = {
            "status": "ok",
            "schema_version": schema_version,
            "job_count": job_count,
            "event_count": event_count,
        }

    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Restore SQLite job store from backup.")
    parser.add_argument("backup", help="Path to backup file (.db or .db.gz)")
    parser.add_argument("destination", help="Destination path for restored database")
    parser.add_argument("--validate", action="store_true", help="Validate restored database")
    args = parser.parse_args()

    try:
        result = restore(args.backup, args.destination, validate=args.validate)
        LOGGER.info("Restore completed: %s -> %s (%.1f MB)",
                    result["source"], result["destination"],
                    result["size_bytes"] / (1024 * 1024))
        if result.get("validation"):
            v = result["validation"]
            LOGGER.info("Validation passed: schema v%s, %d jobs, %d events",
                        v.get("schema_version"), v.get("job_count"), v.get("event_count"))
    except Exception as exc:
        LOGGER.error("Restore failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
