# VulnoraIQ Production Runbook

This runbook is for VulnoraIQ `0.2.0` controlled internal enterprise deployments.

> **Scope:** adapt paths, hostnames, secret-management steps, reverse proxy, and backup destinations to your environment. VulnoraIQ `0.2.0` is not public SaaS or multi-tenant ready. See [`DEPLOYMENT.md`](DEPLOYMENT.md), [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md), and [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md).

## 1. Service management

### Start service: Docker Compose

```bash
cp .env.production.example .env.production
# Edit .env.production and replace placeholders.
docker compose up -d --build
```

### Start service: direct runtime

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="replace-with-strong-token-min-20-chars"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports

python scripts/validate_runtime_production_config.py
vulnoraiq-web --host 127.0.0.1 --port 8787
```

### Start service: systemd

```bash
sudo systemctl start vulnoraiq
sudo systemctl status vulnoraiq --no-pager
```

### Stop service

```bash
# Docker Compose
docker compose down

# systemd
sudo systemctl stop vulnoraiq
```

### Restart service

```bash
# Docker Compose
docker compose restart

# systemd
sudo systemctl restart vulnoraiq
```

## 2. Health, readiness, and metrics

### Liveness

```bash
curl -f http://127.0.0.1:8787/healthz
```

Expected: HTTP `200` with service status and `started_at`.

### Readiness

```bash
curl -f http://127.0.0.1:8787/readyz
```

Expected: HTTP `200` when targets and profiles are loaded. HTTP `503` means the service is alive but not ready.

### Metrics

`/metrics` is auth-protected by default.

```bash
curl -H "X-VulnoraIQ-Token: $VULNORAIQ_ADMIN_TOKEN" \
  http://127.0.0.1:8787/metrics
```

Key metrics to monitor:

- `vulnoraiq_up`
- `vulnoraiq_auth_failures_total`
- `vulnoraiq_authz_failures_total`
- `vulnoraiq_csrf_failures_total`
- `vulnoraiq_rate_limit_exceeded_total`
- `vulnoraiq_scans_created_total`
- `vulnoraiq_scans_completed_total`
- `vulnoraiq_scans_failed_total`
- `vulnoraiq_active_scans`
- `vulnoraiq_scan_queue_full_total`
- `vulnoraiq_internal_errors_total`

## 3. Logs and audit events

### Docker logs

```bash
docker compose logs -f --tail=100
```

### systemd logs

```bash
sudo journalctl -u vulnoraiq -n 100 -f
```

### Audit log format

Audit events are JSON lines emitted by the `vulnoraiq.audit` logger. Events include:

- `server_start`
- `auth_failure`
- `authz_failure`
- `csrf_failure`
- `rate_limit_exceeded`
- `oversized_request`
- `malformed_json`
- `scan_created`
- `scan_queue_full`
- `artifact_download`
- `artifact_traversal_attempt`
- `internal_error`

Example:

```json
{"timestamp":"2026-06-22T10:30:00+00:00","event":"auth_failure","request_id":"abc123","user":"anonymous","role":"viewer","authenticated":"false","client_ip":"10.0.0.10","method":"GET","path":"/api/scans","status":401,"detail":"no token provided"}
```

Audit logs must not contain tokens, CSRF tokens, request bodies, secrets, or full report contents.

## 4. Runtime configuration validation

Run before starting or after changing environment variables:

```bash
python scripts/validate_runtime_production_config.py
```

Important checks:

- auth enabled
- admin token set and strong enough
- no demo/default production token
- SQLite backend in production
- writable output path
- readable config path
- trusted proxy CIDRs valid when enabled
- `0.0.0.0` / `::` binding fails unless trusted proxy config is present
- sane rate limit, request body, and CSRF TTL values

## 5. Token rotation

1. Generate a new token:

   ```bash
   openssl rand -hex 32
   ```

2. Update the secret source or runtime env var, for example `VULNORAIQ_ADMIN_TOKEN`.
3. Restart the service.
4. Verify old token is rejected and new token works:

   ```bash
   curl -i -H "X-VulnoraIQ-Token: $NEW_TOKEN" http://127.0.0.1:8787/api/scans
   ```

5. Review audit logs for failed use of the old token.

## 6. Backup and restore

### Create SQLite backup

```bash
mkdir -p /data/backups
python scripts/backup_sqlite_store.py \
  /data/jobs.db \
  /data/backups/jobs-$(date +%Y%m%d-%H%M%S).db \
  --compress \
  --validate \
  --retention 90
```

### Restore SQLite backup

```bash
# 1. Stop service
sudo systemctl stop vulnoraiq || docker compose down

# 2. Preserve current DB
cp /data/jobs.db /data/jobs.db.before-restore-$(date +%Y%m%d-%H%M%S)

# 3. Restore
python scripts/restore_sqlite_store.py \
  /data/backups/jobs-YYYYMMDD-HHMMSS.db.gz \
  /data/jobs.db \
  --compressed \
  --validate

# 4. Start service
sudo systemctl start vulnoraiq || docker compose up -d

# 5. Verify
curl -f http://127.0.0.1:8787/healthz
curl -f http://127.0.0.1:8787/readyz
```

### Restore drill

Run once per release candidate:

1. Create a backup from a test DB.
2. Restore to a temporary DB path.
3. Start the service against the restored DB.
4. Confirm scan history and artifacts still work.
5. Record result in release checklist.

## 7. Clear stuck scans

There is no separate job-management CLI yet. Use this controlled manual procedure:

1. Stop the service.
2. Back up `/data/jobs.db`.
3. Inspect stuck rows:

   ```bash
   sqlite3 /data/jobs.db "SELECT id,target,profile,status,started_at FROM jobs WHERE status='running';"
   ```

4. If a job is confirmed stale, mark failed:

   ```bash
   sqlite3 /data/jobs.db "UPDATE jobs SET status='failed', error='manually marked failed after stale running state', completed_at=datetime('now') WHERE id='<job_id>';"
   ```

5. Restart the service and verify `/api/scans`.

## 8. Reverse proxy and TLS checks

### nginx

```bash
sudo nginx -t
curl -f -H "Host: vulnoraiq.example.com" https://vulnoraiq.example.com/healthz
```

### Caddy

```bash
caddy validate --config /etc/caddy/Caddyfile
curl -f https://vulnoraiq.example.com/healthz
```

### Certificate expiry

```bash
echo | openssl s_client -servername vulnoraiq.example.com \
  -connect vulnoraiq.example.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

## 9. Troubleshooting

| Symptom | Check | Likely resolution |
| --- | --- | --- |
| Service exits on startup | `docker compose logs` or `journalctl -u vulnoraiq` | Run `scripts/validate_runtime_production_config.py`; fix failed production check |
| `401 authentication required` | Token header missing or wrong | Send `X-VulnoraIQ-Token`; rotate/regenerate token if needed |
| `403 forbidden` | Role lacks permission or CSRF missing | Use admin/analyst token as appropriate; fetch `/api/csrf-token` before POST |
| `413 request too large` | Body exceeds `VULNORAIQ_MAX_REQUEST_BODY` | Reduce request size or raise limit within production validation bounds |
| `429 rate limit exceeded` | IP exceeded app rate limit | Check client retry behaviour; tune env vars; add proxy/WAF limits |
| `scan queue at capacity` | Too many active/queued scans | Tune `VULNORAIQ_MAX_CONCURRENT_SCANS` / `VULNORAIQ_SCAN_QUEUE_LIMIT` or wait |
| `/metrics` returns 401 | Metrics auth required | Add `X-VulnoraIQ-Token` or intentionally disable auth only in a protected monitoring network |
| Ready check returns 503 | Targets/profiles failed to load | Check `VULNORAIQ_CONFIG_DIR`, `config/targets.yaml`, and `config/attack_profiles.yaml` |
| SQLite error | DB missing, corrupted, or not writable | Check `/data` permissions; run backup/restore validation |
| Artifacts return 404 | Report path missing or job incomplete | Confirm job status and `/data/reports` persistence |

## 10. Upgrade procedure

1. Review `CHANGELOG.md` and `docs/MIGRATION.md`.
2. Back up SQLite DB.
3. Pull or build the new image.
4. Run validation commands:

   ```bash
   ruff check .
   mypy .
   pytest -q
   python scripts/validate_package_metadata.py
   python scripts/validate_production_testing_readiness.py
   ```

5. Start the release candidate.
6. Verify `/healthz`, `/readyz`, `/metrics`, Web UI auth, scan creation, artifact download, backup, and restore.
7. Monitor logs and metrics for at least one hour.

## 11. Rollback procedure

1. Stop the service.
2. Restore the previous image/tag or code revision.
3. Restore the pre-upgrade SQLite backup if schema/data changed.
4. Start the previous version.
5. Verify `/healthz`, `/readyz`, scan history, and artifacts.
6. Document the rollback reason in `CHANGELOG.md` or release notes.

## 12. Reference

### Default ports

| Component | Port |
| --- | --- |
| VulnoraIQ Web UI | `8787` |
| Reverse proxy HTTPS | `443` |
| Reverse proxy HTTP redirect | `80` |

### Important paths

| Artifact | Typical path |
| --- | --- |
| SQLite job store | `/data/jobs.db` |
| Reports/artifacts | `/data/reports` |
| Backups | `/data/backups` |
| Production env file | `.env.production` or secret-manager injected env |
| Example env file | `.env.production.example` |

### Core environment variables

| Variable | Purpose |
| --- | --- |
| `VULNORAIQ_ENV=production` | Enable production validation |
| `VULNORAIQ_ADMIN_TOKEN` | Required admin token |
| `VULNORAIQ_AUTH_MODE` | `token` or `trusted_proxy` |
| `VULNORAIQ_JOB_STORE_BACKEND=sqlite` | Production persistence backend |
| `VULNORAIQ_JOB_STORE_PATH` | SQLite path |
| `VULNORAIQ_WEB_OUTPUT_ROOT` | Report/artifact output path |
| `VULNORAIQ_TRUST_PROXY_HEADERS` | Trust proxy headers when enabled |
| `VULNORAIQ_TRUSTED_PROXY_CIDRS` | Allowed proxy source networks |
| `VULNORAIQ_METRICS_AUTH_REQUIRED` | Protect `/metrics`; default true |

## 13. Escalation

Use [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md) for security events. Escalate immediately for:

- suspected token leak
- auth bypass or trusted-proxy spoofing
- artifact exposure
- path traversal attempt with successful access
- repeated rate-limit spikes or scan queue exhaustion
- corrupted SQLite store
- dependency vulnerability affecting runtime security