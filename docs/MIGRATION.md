# Migration Guide: VulnoraIQ 0.2.0

This guide covers migrating from legacy `0.0.1.x` deployments to version `0.2.0`, which introduces SQLite-backed job persistence, environment-variable-based authentication, hardened production mode enforcement, Agentic Applications readiness gates, and GenAI Security working-starter readiness assets.

---

## 1. Overview of changes

| Area | `0.0.1.x` legacy | `0.2.0` current |
| --- | --- | --- |
| Job store | JSON file (`jobs.json`) | SQLite (`jobs.db`) |
| Auth mechanism | `config/web_users.yaml` fallback | `VULNORAIQ_ADMIN_TOKEN` env var |
| Auth mode | Token only | `token` or `trusted_proxy` |
| Production mode | No enforcement | `VULNORAIQ_ENV=production` enforces runtime checks |
| Config-based auth | Always allowed | Disabled in production |
| Web UI entry point | `webui/server.py` | `webui/hosted_server.py` |
| OWASP/ATLAS mapping governance | Not enforced | `scripts/validate_owasp_atlas_mappings.py` |
| GenAI Security readiness | Planning docs only | `DSGAI01–DSGAI21` safe synthetic scenario manifest, evaluator suite, validator, and CI gate |
| Min Python | 3.8+ | 3.10+ |

---

## 2. JSON to SQLite migration

### 2.1 Export existing jobs from JSON

If you have scan jobs in the legacy JSON store, export them before upgrading.

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

### 2.2 Create the new SQLite store

Start the `0.2.0` server. The SQLite store is created automatically on first use:

```bash
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
vulnoraiq-web
```

Verify the database was created:

```bash
ls -l reports/output/webui/jobs.db
```

### 2.3 Validate migration

```bash
python scripts/backup_sqlite_store.py \
  reports/output/webui/jobs.db \
  /tmp/migration_validation.db \
  --validate
```

Expected output includes schema and job/event validation.

> **Note:** The JSON backend is still available for development use by setting `VULNORAIQ_JOB_STORE_BACKEND=json`. It is rejected in production mode.

---

## 3. Environment variable changes

### 3.1 New required variables

| Variable | Description | Required in production |
| --- | --- | --- |
| `VULNORAIQ_ADMIN_TOKEN` | Admin auth token (min 20 chars) | Yes |
| `VULNORAIQ_ENV=production` | Enables production mode | Recommended / expected |

### 3.2 New optional variables

| Variable | Default | Description |
| --- | --- | --- |
| `VULNORAIQ_AUTH_MODE` | `token` | Auth strategy: `token` or `trusted_proxy` |
| `VULNORAIQ_ANALYST_TOKEN` | none | Analyst-level token |
| `VULNORAIQ_VIEWER_TOKEN` | none | Viewer-level token |
| `VULNORAIQ_MAX_CONCURRENT_SCANS` | `5` | Max concurrent scan jobs |
| `VULNORAIQ_SCAN_QUEUE_LIMIT` | `20` | Max queued scans before rejection |
| `VULNORAIQ_METRICS_AUTH_REQUIRED` | `true` | Require auth for `/metrics` endpoint |
| `VULNORAIQ_CSRF_TOKEN_TTL` | `300` | CSRF token lifetime in seconds |
| `VULNORAIQ_JOB_STORE_BACKEND` | `sqlite` | Backend type (`sqlite` or `json`) |
| `VULNORAIQ_JOB_STORE_PATH` | auto | Custom path for the job store |
| `VULNORAIQ_WEB_OUTPUT_ROOT` | auto | Output root for scan reports |
| `VULNORAIQ_RATE_LIMIT_MAX` | `60` | Max requests per rate-limit window |
| `VULNORAIQ_RATE_LIMIT_WINDOW` | `60` | Rate-limit window in seconds |
| `VULNORAIQ_MAX_REQUEST_BODY` | `10485760` | Max POST body in bytes |
| `VULNORAIQ_TRUST_PROXY_HEADERS` | `false` | Enable trusted reverse-proxy identity headers |
| `VULNORAIQ_TRUSTED_PROXY_CIDRS` | none | Comma-separated CIDRs of trusted proxies |
| `VULNORAIQ_LOG_LEVEL` | `INFO` | Logging level |
| `VULNORAIQ_CONFIG_DIR` | `config` | Path to the config directory |

### 3.3 Minimal production `.env` example

```ini
VULNORAIQ_ENV=production
VULNORAIQ_ADMIN_TOKEN=a-strong-random-token-that-is-at-least-20-chars
VULNORAIQ_JOB_STORE_BACKEND=sqlite
VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
VULNORAIQ_LOG_LEVEL=INFO
```

---

## 4. Authentication migration

### 4.1 From file-based users to env token auth

Before `0.2.0`, local user records could be stored in `config/web_users.yaml`. In `0.2.0`, production mode must use environment-backed tokens.

```bash
export VULNORAIQ_ADMIN_TOKEN="your-strong-random-token"
```

Tokens are checked via constant-time comparison (`hmac.compare_digest`). The file-based fallback is only for development and is not allowed in production mode.

### 4.2 Trusted proxy identity mode

Set `VULNORAIQ_AUTH_MODE=trusted_proxy` to delegate authentication to a reverse proxy. You must also set:

```ini
VULNORAIQ_TRUST_PROXY_HEADERS=true
VULNORAIQ_TRUSTED_PROXY_CIDRS=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

Requests from non-trusted IPs will be treated as unauthenticated.

---

## 5. GenAI Security readiness asset migration

`0.2.0` now includes GenAI Security readiness assets. These are repository assets, not runtime secrets:

| Asset | Purpose |
| --- | --- |
| `benchmarks/fixtures/genai/scenarios.yaml` | Source-confirmed `DSGAI01–DSGAI21` scenario coverage and `DSGAI22–DSGAI25` discrepancy tracking |
| `core/genai_evaluators.py` | Deterministic GenAI evaluator primitives |
| `scripts/validate_genai_readiness.py` | Release/CI gate for GenAI readiness |
| `tests/test_genai_readiness_validation.py` | Regression tests for validator/evaluator behaviour |
| `docs/genai/PRODUCTION_READINESS_PLAN.md` | Phase-by-phase GenAI Security readiness decision |

After upgrading, run:

```bash
python scripts/validate_genai_readiness.py
pytest tests/test_genai_readiness_validation.py -q
python scripts/validate_package_metadata.py
```

Passing this gate means the GenAI working-starter manifest and docs are aligned. It does not mean real-world GenAI detection has been independently validated.

---

## 6. Breaking changes

1. **`webui/server.py` removed** — use `webui/hosted_server.py` through `vulnoraiq-web`.
2. **JSON backend is legacy/dev only** — SQLite is now the default and JSON is blocked in production mode.
3. **Minimum Python 3.10 required**.
4. **Config-based auth disabled in production** — env-var-based tokens are required.
5. **CSRF protection enforced** — mutating API calls require a valid CSRF token.
6. **Rate limiting enabled by default**.
7. **Metrics endpoint requires auth by default**.
8. **GenAI readiness drift blocks release** — package metadata validation now checks the GenAI readiness validator when assets are present.

---

## 7. Rollback procedure

If the migration fails, revert to the previous version:

```bash
# Install the previous version
pip install vulnoraiq==0.0.1.8   # or the last working version

# If using Docker, redeploy the old image
docker pull vulnoraiq:<previous-tag>
```

If you migrated to SQLite and need to go back to JSON, export SQLite data back to JSON before setting `VULNORAIQ_JOB_STORE_BACKEND=json` for development-mode rollback.

Rollback checklist:

- [ ] Reinstall old package or redeploy old Docker image
- [ ] Restore `config/web_users.yaml` from backup if previously used
- [ ] Restore `reports/output/webui/jobs.json` from backup or re-export from SQLite
- [ ] Unset `VULNORAIQ_ADMIN_TOKEN`, `VULNORAIQ_ANALYST_TOKEN`, `VULNORAIQ_VIEWER_TOKEN`
- [ ] Unset `VULNORAIQ_ENV`
- [ ] Set `VULNORAIQ_JOB_STORE_BACKEND=json` only for development-mode rollback
- [ ] Verify the server starts and lists previous jobs

---

## 8. Verification steps after migration

Run these checks to confirm the migration succeeded:

```bash
ruff check .
mypy .
pytest -q
python scripts/validate_runtime_production_config.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_package_metadata.py
```

Verify the Web UI starts:

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
curl http://127.0.0.1:8787/healthz
curl http://127.0.0.1:8787/readyz
```

Verify the job store is SQLite:

```bash
file reports/output/webui/jobs.db
```

Run a safe demo scan with auth and CSRF enabled before using configured targets.

---

## Appendix: Quick-migration checklist

- [ ] Upgrade Python to 3.10+
- [ ] Export legacy jobs from `jobs.json` if required
- [ ] Update scripts / Docker images to the `0.2.0` package
- [ ] Set `VULNORAIQ_ADMIN_TOKEN` in your environment or Docker Compose file
- [ ] Set `VULNORAIQ_ENV=production` for production deployments
- [ ] Start the server and confirm it uses SQLite
- [ ] Validate with `scripts/backup_sqlite_store.py --validate`
- [ ] Run `python scripts/validate_owasp_atlas_mappings.py`
- [ ] Run `python scripts/validate_genai_readiness.py`
- [ ] Run `python scripts/validate_package_metadata.py`
- [ ] Run the verification steps in this guide
- [ ] Keep `jobs.json` backup until the new store is verified
