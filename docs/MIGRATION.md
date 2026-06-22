# Migration Guide: VulnoraIQ 0.2.0

This guide covers migrating from legacy 0.0.1.x deployments to version 0.2.0,
which introduces SQLite-backed job persistence, environment-variable-based
authentication, and hardened production mode enforcement.

---

## 1. Overview of Changes

| Area               | 0.0.1.x (Legacy)              | 0.2.0 (Current)                         |
| ------------------ | ------------------------------ | --------------------------------------- |
| Job store          | JSON file (`jobs.json`)        | SQLite (`jobs.db`)                      |
| Auth mechanism     | `config/web_users.yaml` (file) | `VULNORAIQ_ADMIN_TOKEN` env var         |
| Auth mode          | Always token                   | `token` or `trusted_proxy`              |
| Production mode    | No enforcement                 | `VULNORAIQ_ENV=production` enforces     |
| Config-based auth  | Always allowed                 | Disabled in production                  |
| Web UI entry point | `webui/server.py` (removed)    | `webui/hosted_server.py`                |
| Min Python         | 3.8+                           | 3.10+                                   |

---

## 2. JSON to SQLite Migration

### 2.1 Export Existing Jobs from JSON

If you have scan jobs in the legacy JSON store, export them with a one-shot
Python snippet **before** upgrading.

```python
# export_jobs.py — run against the old codebase before upgrading
import json
from pathlib import Path

src = Path("reports/output/webui/jobs.json")
dst = Path("jobs_export.json")

if src.exists():
    data = json.loads(src.read_text(encoding="utf-8"))
    dst.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Exported {len(data)} jobs to {dst}")
else:
    print("No legacy jobs.json found — nothing to export.")
```

### 2.2 Create the New SQLite Store

Start the 0.2.0 server. The SQLite store is created automatically on first use:

```bash
# Ensure the env points to SQLite (this is the default)
export VULNORAIQ_JOB_STORE_BACKEND=sqlite

# Start the web UI
vulnoraiq-web
```

Verify the database was created:

```bash
ls -l reports/output/webui/jobs.db
```

### 2.3 Validate Migration

Use the built-in backup validation script to inspect the new store:

```bash
python scripts/backup_sqlite_store.py \
  reports/output/webui/jobs.db \
  /tmp/migration_validation.db \
  --validate
```

Expected output:

```
INFO Validation passed: schema v1, N jobs, M events
```

If you exported legacy jobs and want to re-import them (manual operation):

```python
# import_jobs.py — optional, one-time re-import helper
import json
import sqlite3
from pathlib import Path

export = Path("jobs_export.json")
if not export.exists():
    print("No export file found.")
    exit(0)

jobs = json.loads(export.read_text(encoding="utf-8"))
db = Path("reports/output/webui/jobs.db")
conn = sqlite3.connect(str(db))

for job_id, job in jobs.items():
    conn.execute(
        """INSERT OR IGNORE INTO jobs
           (id, target, profile, authorised, created_by, status,
            progress, created_at, started_at, completed_at, error,
            outputs, summary)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            job_id, job["target"], job["profile"], int(job.get("authorised", False)),
            job.get("created_by", "migrated"), job.get("status", "unknown"),
            job.get("progress", 0), job.get("created_at", ""),
            job.get("started_at"), job.get("completed_at"), job.get("error"),
            json.dumps(job.get("outputs", {})),
            json.dumps(job.get("summary", {})),
        ),
    )
    for event in job.get("events", []):
        conn.execute(
            "INSERT INTO events (job_id, timestamp, stage, message, progress, level) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (job_id, event["timestamp"], event["stage"], event["message"],
             event.get("progress", 0), event.get("level", "info")),
        )

conn.commit()
conn.close()
print("Import complete.")
```

> **Note:** The JSON backend is still available for development use by setting
> `VULNORAIQ_JOB_STORE_BACKEND=json`. It is **rejected** in production mode.

---

## 3. Environment Variable Changes

### 3.1 New Required Variables

| Variable                          | Description                        | Required In Production |
| --------------------------------- | ---------------------------------- | ---------------------- |
| `VULNORAIQ_ADMIN_TOKEN`           | Admin auth token (min 20 chars)    | Yes                    |
| `VULNORAIQ_ENV=production`        | Enables production mode            | Yes (recommended)      |

### 3.2 New Optional Variables

| Variable                          | Default    | Description                                      |
| --------------------------------- | ---------- | ------------------------------------------------ |
| `VULNORAIQ_AUTH_MODE`             | `token`    | Auth strategy: `token` or `trusted_proxy`        |
| `VULNORAIQ_ANALYST_TOKEN`         | (none)     | Analyst-level token                              |
| `VULNORAIQ_VIEWER_TOKEN`          | (none)     | Viewer-level token                               |
| `VULNORAIQ_MAX_CONCURRENT_SCANS`  | `5`        | Max concurrent scan jobs                         |
| `VULNORAIQ_SCAN_QUEUE_LIMIT`      | `20`       | Max queued scans before rejection                |
| `VULNORAIQ_METRICS_AUTH_REQUIRED` | `true`     | Require auth for `/metrics` endpoint             |
| `VULNORAIQ_CSRF_TOKEN_TTL`        | `300`      | CSRF token lifetime in seconds                   |
| `VULNORAIQ_JOB_STORE_BACKEND`     | `sqlite`   | Backend type (`sqlite` or `json`)                |
| `VULNORAIQ_JOB_STORE_PATH`        | (auto)     | Custom path for the job store                    |
| `VULNORAIQ_WEB_OUTPUT_ROOT`       | (auto)     | Output root for scan reports                     |
| `VULNORAIQ_RATE_LIMIT_MAX`        | `60`       | Max requests per rate-limit window               |
| `VULNORAIQ_RATE_LIMIT_WINDOW`     | `60`       | Rate-limit window in seconds                     |
| `VULNORAIQ_MAX_REQUEST_BODY`      | `10485760` | Max POST body in bytes (10 MB)                   |
| `VULNORAIQ_TRUST_PROXY_HEADERS`   | `false`    | Enable trusted reverse-proxy identity headers    |
| `VULNORAIQ_TRUSTED_PROXY_CIDRS`   | (none)     | Comma-separated CIDRs of trusted proxies         |
| `VULNORAIQ_LOG_LEVEL`             | `INFO`     | Logging level                                    |
| `VULNORAIQ_CONFIG_DIR`            | `config`   | Path to the config directory                     |
| `VULNORAIQ_WEB_USERS_PATH`        | (auto)     | Path to `web_users.yaml` (fallback only)         |

### 3.3 Removed / Deprecated Variables

- `VULNORAIQ_AUTH_ENABLED` — still respected but **overridden** in production
  mode (production always requires auth). In production, setting this to
  `false` will cause the server to refuse to start.
- File-based `config/web_users.yaml` — still read as a **fallback** in
  development, but **ignored** in production when env token vars are set.

### 3.4 Minimal Production `.env` Example

```ini
VULNORAIQ_ENV=production
VULNORAIQ_ADMIN_TOKEN=a-strong-random-token-that-is-at-least-20-chars
VULNORAIQ_JOB_STORE_BACKEND=sqlite
VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
VULNORAIQ_LOG_LEVEL=INFO
```

---

## 4. Authentication Migration

### 4.1 From File-Based Users to Env Token Auth

**Before (0.0.1.x):**

```yaml
# config/web_users.yaml
users:
  - username: admin
    token_hash: "abc123deadbeef..."
    role: admin
    status: active
```

**After (0.2.0):**

```bash
export VULNORAIQ_ADMIN_TOKEN="your-strong-random-token"
```

Tokens are checked via constant-time comparison (`hmac.compare_digest`). The
file-based `config/web_users.yaml` is **only** consulted when no
`VULNORAIQ_ADMIN_TOKEN` / `VULNORAIQ_ANALYST_TOKEN` / `VULNORAIQ_VIEWER_TOKEN`
env vars are set.

### 4.2 Production Mode Enforces Token Auth

When `VULNORAIQ_ENV=production`:

- Auth **must** be enabled (cannot set `VULNORAIQ_AUTH_ENABLED=false`).
- At least `VULNORAIQ_ADMIN_TOKEN` must be set and be 20+ characters.
- File-based `web_users.yaml` fallback is **rejected**.
- The internal admin token (`vulnoraiq-internal-admin-token`) is **disabled**.
- Known demo/default tokens (`demo`, `admin`, `password`, `test`, `changeme`)
  are **rejected** by the production config check.

### 4.3 Trusted Proxy Identity Mode

Set `VULNORAIQ_AUTH_MODE=trusted_proxy` to delegate authentication to a
reverse proxy. The server reads identity from these headers:

| Header                 | Purpose          |
| ---------------------- | ---------------- |
| `X-Authenticated-User` | Username          |
| `X-Authenticated-Email`| Email (info only)|
| `X-Authenticated-Groups`| Group memberships|
| `X-VulnoraIQ-Role`     | Role (`admin`, `analyst`, `viewer`) |

You must also set:

```ini
VULNORAIQ_TRUST_PROXY_HEADERS=true
VULNORAIQ_TRUSTED_PROXY_CIDRS=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

Requests from non-trusted IPs will be treated as unauthenticated.

---

## 5. Breaking Changes

1. **`webui/server.py` removed** — The legacy entry point has been deleted.
   Use `webui/hosted_server.py` (invoked via `vulnoraiq-web`).

2. **JSON backend is legacy/dev only** — SQLite is now the default.
   The JSON backend (`PersistentJobStore`) remains available for development
   but is **blocked** in production mode. Set
   `VULNORAIQ_JOB_STORE_BACKEND=json` to opt in for dev.

3. **Minimum Python 3.10 required** — The codebase uses `from __future__ import
   annotations`, `dataclass(slots=True)`, `str.removeprefix`, and other 3.10+
   features.

4. **Config-based auth disabled in production** — `config/web_users.yaml` is
   not consulted when `VULNORAIQ_ENV=production`. Only env-var-based tokens
   are accepted.

5. **CSRF protection enforced** — All mutating API calls (`POST /api/scans`)
   require a valid `X-CSRF-Token` header obtained from `GET /api/csrf-token`.

6. **Rate limiting enabled by default** — 60 requests per 60-second window per
   client IP. Configure via `VULNORAIQ_RATE_LIMIT_MAX` and
   `VULNORAIQ_RATE_LIMIT_WINDOW`.

7. **Metrics endpoint requires auth by default** — Set
   `VULNORAIQ_METRICS_AUTH_REQUIRED=false` to restore the old behaviour (not
   recommended in production).

---

## 6. Rollback Procedure

If the migration fails, revert to the previous version:

### 6.1 Roll Back the Application

```bash
# Install the previous version
pip install vulnoraiq==0.0.1.8   # or the last working version

# If using Docker, redeploy the old image
docker pull vulnoraiq:<previous-tag>
```

### 6.2 Roll Back the Job Store

If you migrated to SQLite and need to go back to JSON:

```bash
# Export SQLite data back to JSON
python -c "
import json, sqlite3
from pathlib import Path

conn = sqlite3.connect('reports/output/webui/jobs.db')
conn.row_factory = sqlite3.Row
jobs = {}
for row in conn.execute('SELECT * FROM jobs'):
    job = dict(row)
    events = [
        dict(e) for e in
        conn.execute('SELECT * FROM events WHERE job_id = ? ORDER BY id', (row['id'],))
    ]
    job['events'] = events
    jobs[row['id']] = job
conn.close()

dst = Path('reports/output/webui/jobs.json')
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(json.dumps(jobs, indent=2, sort_keys=True, default=str), encoding='utf-8')
print(f'Exported {len(jobs)} jobs back to {dst}')
"

# Switch back to JSON backend
export VULNORAIQ_JOB_STORE_BACKEND=json
```

### 6.3 Restore Auth Config

If you were using `config/web_users.yaml` with file-based auth:

```bash
# Restore from backup
cp config/web_users.yaml.bak config/web_users.yaml

# Unset the env token vars
unset VULNORAIQ_ADMIN_TOKEN
unset VULNORAIQ_ENV
```

### 6.4 Full Rollback Checklist

- [ ] Reinstall old package or redeploy old Docker image
- [ ] Restore `config/web_users.yaml` from backup
- [ ] Restore `reports/output/webui/jobs.json` from backup or re-export from SQLite
- [ ] Unset `VULNORAIQ_ADMIN_TOKEN`, `VULNORAIQ_ANALYST_TOKEN`, `VULNORAIQ_VIEWER_TOKEN`
- [ ] Unset `VULNORAIQ_ENV`
- [ ] Set `VULNORAIQ_JOB_STORE_BACKEND=json`
- [ ] Verify the server starts and lists previous jobs

---

## 7. Verification Steps After Migration

Run these checks to confirm the migration succeeded:

### 7.1 Server Starts Correctly

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Expected log line:

```
INFO web_ui_started env=development url=http://127.0.0.1:8787 auth_enabled=true backend=sqlite
```

### 7.2 Health and Readiness Endpoints

```bash
curl http://127.0.0.1:8787/healthz
# {"status": "ok", "service": "vulnoraiq-web", "started_at": "..."}

curl http://127.0.0.1:8787/readyz
# {"status": "ready", "targets_loaded": N, "profiles_loaded": N, "auth_enabled": true}
```

### 7.3 Authentication Works

```bash
# Without a token — should get 401
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8787/api/config
# 401

# With a valid token
curl -s -H "X-VulnoraIQ-Token: <your-admin-token>" http://127.0.0.1:8787/api/config | head -5
# {"profiles": {...}, "targets": {...}, "web_auth_enabled": true}
```

### 7.4 Job Store Is SQLite

```bash
# Verify the database file
file reports/output/webui/jobs.db
# reports/output/webui/jobs.db: SQLite 3.x database

# Check schema
python -c "
import sqlite3
conn = sqlite3.connect('reports/output/webui/jobs.db')
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print('Tables:', [t[0] for t in tables])
conn.close()
"
# Tables: ['_schema_version', 'jobs', 'events']
```

### 7.5 Previous Jobs Are Accessible

```bash
# If you imported legacy jobs
curl -s -H "X-VulnoraIQ-Token: <token>" http://127.0.0.1:8787/api/scans | python -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"jobs\"])} jobs found')"
```

### 7.6 Production Mode Validation (If Applicable)

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_ADMIN_TOKEN="a-strong-random-token-that-is-at-least-20-chars"

vulnoraiq-web --host 127.0.0.1 --port 8787
```

Expected: server starts and logs `env=production`. If any production check
fails, the server exits with a descriptive error.

### 7.7 Run a Test Scan

```bash
# Get a CSRF token first
CSRF=$(curl -s -H "X-VulnoraIQ-Token: <token>" http://127.0.0.1:8787/api/csrf-token | python -c "import sys,json; print(json.load(sys.stdin)['csrf_token'])")

# Start a scan
curl -s -X POST \
  -H "X-VulnoraIQ-Token: <token>" \
  -H "X-CSRF-Token: $CSRF" \
  -H "Content-Type: application/json" \
  -d '{"target":"demo","profile":"baseline","authorised":false}' \
  http://127.0.0.1:8787/api/scans
```

---

## Appendix: Quick-Migration Checklist

- [ ] Upgrade Python to 3.10+
- [ ] Export legacy jobs from `jobs.json` (`export_jobs.py`)
- [ ] Update any scripts / Docker images to the 0.2.0 package
- [ ] Set `VULNORAIQ_ADMIN_TOKEN` in your environment or Docker compose file
- [ ] Set `VULNORAIQ_ENV=production` for production deployments
- [ ] Verify `config/web_users.yaml` is no longer needed (or remove it)
- [ ] Start the server and confirm it uses SQLite
- [ ] Validate with `scripts/backup_sqlite_store.py --validate`
- [ ] Run the verification steps in [Section 7](#7-verification-steps-after-migration)
- [ ] Keep `jobs.json` backup until the new store is verified
