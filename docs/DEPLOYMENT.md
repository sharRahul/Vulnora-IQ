# Deployment Guide

## Quick Start

```bash
# Install
pip install -e .

# Run the web UI (binds to 127.0.0.1:8787 by default)
vulnoraiq-web

# Health checks
curl http://127.0.0.1:8787/healthz
curl http://127.0.0.1:8787/readyz
```

## Container

Build and run with persistent data:

```bash
docker build -t vulnoraiq:local .
docker run --rm -p 8787:8787 \
  -v vulnoraiq-data:/data \
  -e VULNORAIQ_ADMIN_TOKEN="<strong-random-token>" \
  -e VULNORAIQ_ENV=production \
  vulnoraiq:local
```

The container runs as a non-root user, uses `/data` for SQLite DB and reports,
and sets production defaults (`VULNORAIQ_ENV=production`, `VULNORAIQ_AUTH_ENABLED=true`).

## Production Mode

Set `VULNORAIQ_ENV=production` to enable production-mode validation on startup:

- Auth **must** be enabled
- At least `VULNORAIQ_ADMIN_TOKEN` must be set (minimum 20 characters)
- File-based demo users are rejected
- Internal admin development shortcuts are disabled

The server will refuse to start if these conditions are not met.

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_ANALYST_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_VIEWER_TOKEN="$(openssl rand -hex 32)"
vulnoraiq-web
```

## Authentication

Auth is **enabled by default** and fail-closed — anonymous requests receive HTTP 401.

### Token-based auth via environment variables (recommended for production)

```bash
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="<generate-a-strong-random-token>"
export VULNORAIQ_ANALYST_TOKEN="<another-random-token>"
export VULNORAIQ_VIEWER_TOKEN="<yet-another-random-token>"
```

Role permissions:

| Role | Permissions |
| --- | --- |
| `viewer` | view scans, download artifacts |
| `analyst` | viewer + start demo scans |
| `admin` | analyst + start configured-target scans, manage runtime |

Clients pass the token via the `X-VulnoraIQ-Token` header. Tokens are compared
using constant-time comparison (`hmac.compare_digest`) to mitigate timing attacks.

### File-based auth fallback

If no token env vars are set, the manager reads `config/web_users.yaml`.
This fallback is **not allowed in production mode** (`VULNORAIQ_ENV=production`).
For development, copy `config/web_users.example.yaml` to `config/web_users.yaml`
and set real token hashes.

### Disabling auth

Not recommended for production, but available for development:

```bash
export VULNORAIQ_AUTH_ENABLED=false
```

## Proxy IP Trust

By default, the server does **not** trust `X-Forwarded-For` headers. This prevents
IP spoofing from untrusted sources.

To enable proxy support, set:

```bash
export VULNORAIQ_TRUST_PROXY_HEADERS=true
export VULNORAIQ_TRUSTED_PROXY_CIDRS="10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
```

The server will only trust `X-Forwarded-For` when the direct connection comes from
a CIDR in `VULNORAIQ_TRUSTED_PROXY_CIDRS`. Spoofed headers from untrusted IPs are ignored.

## Security Features

All features are enabled by default and configurable via environment variables.

### Request size limit

Rejects requests with bodies larger than `VULNORAIQ_MAX_REQUEST_BODY` bytes (default: 10 MB).
Returns HTTP 400 for malformed JSON or invalid Content-Length.

### Rate limiting

In-memory sliding-window rate limiter. Default: 60 requests per 60-second window per IP.

| Variable | Default | Description |
| --- | --- | --- |
| `VULNORAIQ_RATE_LIMIT_WINDOW` | `60` | Window in seconds |
| `VULNORAIQ_RATE_LIMIT_MAX` | `60` | Max requests per window |

**Limitation:** The in-memory rate limiter is per-process. For multi-instance deployments,
use a proxy-level rate limiter (see Reverse Proxy section) or a shared backend (Redis).

### CSRF protection

CSRF tokens are bound to the authenticated principal (or client IP for anonymous users)
and expire after `VULNORAIQ_CSRF_TOKEN_TTL` seconds (default: 300 / 5 minutes).

- `GET /api/csrf-token` — obtain a token: `{"csrf_token": "..."}`
- `POST /api/scans` — requires `X-CSRF-Token` header

### Security headers

Every response includes:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 0`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (conditional on TLS detection)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; form-action 'self'; base-uri 'self'; frame-ancestors 'none'`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

HSTS is conditionally emitted: when `VULNORAIQ_TRUST_PROXY_HEADERS=true` and
`X-Forwarded-Proto: https` is received, or when the connection is not localhost.

## Persistence

Two backends are available, selected via `VULNORAIQ_JOB_STORE_BACKEND`:

### SQLite (default, recommended for production)

```bash
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
```

Production settings applied automatically:
- WAL mode for concurrent read/write performance
- Foreign keys enforced
- Busy timeout of 5 seconds
- Schema versioning for future migrations

Suitable for single-server deployments. Back up the database file regularly.

### JSON file (legacy/dev only)

```bash
export VULNORAIQ_JOB_STORE_BACKEND=json
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.json
```

Thread-safe with `RLock`. Suitable for low-traffic development use only.
Not recommended for production.

## Audit Log

An audit log is emitted on a dedicated `vulnoraiq.audit` logger. Events include:

- `server_start` — service startup
- `auth_failure` — unauthenticated request
- `authz_failure` — authenticated but insufficient permissions
- `csrf_failure` — missing or invalid CSRF token
- `rate_limit_exceeded` — rate limit triggered
- `scan_created` — new scan with target, profile, job ID
- `artifact_download` — artifact downloaded with job ID and artifact name

Each event includes: event name, username, role, authenticated flag, client IP, and detail.

```
2025-01-15 10:30:00,000 AUDIT event=server_start user=anonymous role=viewer authenticated=false ip= detail=env=production host=127.0.0.1 port=8787
2025-01-15 10:30:05,000 AUDIT event=scan_created user=admin role=admin authenticated=true ip=10.0.0.1 detail=target=demo profile=baseline job_id=abc123
2025-01-15 10:30:06,000 AUDIT event=artifact_download user=admin role=admin authenticated=true ip=10.0.0.1 detail=artifact=json job=abc123
```

No secrets, tokens, request bodies, or sensitive report contents are logged.

Configure a log shipper (Filebeat, Fluentd) to forward the audit log to your SIEM.

## Reverse Proxy & TLS

The built-in HTTP server is intended to run behind a reverse proxy that terminates TLS.

### nginx

```nginx
server {
    listen 443 ssl;
    server_name vulnoraiq.example.com;

    ssl_certificate /etc/ssl/certs/vulnoraiq.crt;
    ssl_certificate_key /etc/ssl/private/vulnoraiq.key;

    # Rate limiting at proxy layer
    limit_req_zone $binary_remote_addr zone=vulnoraiq:10m rate=30r/s;
    limit_req zone=vulnoraiq burst=10 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8787;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }
}
```

### Caddy

```
vulnoraiq.example.com {
    rate_limit {
        zone dynamic {
            key {remote_host}
            events 30
            window 1s
        }
    }

    reverse_proxy 127.0.0.1:8787 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

## Metrics & Monitoring

- `/healthz` — liveness probe (returns `{"status": "ok"}`)
- `/readyz` — readiness probe (checks targets and profiles are loaded)

Integrate with your monitoring stack. Example Prometheus blackbox exporter:

```yaml
modules:
  vulnoraiq_health:
    prober: http
    http:
      valid_status_codes: [200]
      method: GET
      url: "http://127.0.0.1:8787/healthz"
```

## Log Rotation

Example `logrotate` configuration for the application and audit logs:

```
/var/log/vulnoraiq/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

## Backup & Restore

### SQLite online backup

```bash
# Backup (online, low-traffic periods recommended)
sqlite3 /data/jobs.db ".backup /data/backups/jobs-$(date +%Y%m%d-%H%M%S).db"

# Restore
sqlite3 /data/jobs.db ".restore /data/backups/jobs-20250115-120000.db"

# Verify backup integrity
sqlite3 /data/backups/jobs-20250115.db "PRAGMA integrity_check;"
```

### JSON

Simply copy `jobs.json` to your backup destination.

### Retention

Implement a cron or systemd timer:

```
0 2 * * * find /data/backups -name "jobs-*.db" -mtime +90 -delete
```

### Rollback procedure

1. Stop the vulnoraiq-web service
2. Rename current database: `mv /data/jobs.db /data/jobs.db.rollback-$(date +%Y%m%d)`
3. Restore from backup: `sqlite3 /data/jobs.db ".restore /data/backups/jobs-YYYYMMDD.db"`
4. Start the service and verify `/healthz` and `/readyz`
5. Verify scan history appears correctly in the web UI

## Filesystem Permissions

When running directly (not containerized), apply least-privilege permissions:

```bash
# Create dedicated user
sudo useradd --system --no-create-home vulnoraiq

# Set ownership
sudo chown -R vulnoraiq:vulnoraiq /data
sudo chmod 750 /data
sudo chmod 640 /data/jobs.db

# Config directory should be read-only for the runtime user
sudo chown -R root:vulnoraiq /app/config
sudo chmod 750 /app/config
sudo chmod 640 /app/config/*.yaml
```

## Secrets Management

- **Never bake secrets into Docker images**
- Use environment variables or a secrets manager (HashiCorp Vault, AWS Secrets Manager, etc.)
- Rotate tokens periodically: generate new tokens, update env vars, restart service, revoke old tokens
- The internal admin development token (`vulnoraiq-internal-admin-token`) is disabled in production mode

## systemd Service

```ini
[Unit]
Description=VulnoraIQ Web UI
After=network.target

[Service]
Type=simple
User=vulnoraiq
Group=vulnoraiq
WorkingDirectory=/app
Environment=VULNORAIQ_ENV=production
Environment=VULNORAIQ_ADMIN_TOKEN=...
Environment=VULNORAIQ_ANALYST_TOKEN=...
Environment=VULNORAIQ_VIEWER_TOKEN=...
Environment=VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
Environment=VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
ExecStart=/usr/local/bin/vulnoraiq-web
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## Production env file example

```bash
# .env.production — source this before starting vulnoraiq-web
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="<openssl rand -hex 32>"
export VULNORAIQ_ANALYST_TOKEN="<openssl rand -hex 32>"
export VULNORAIQ_VIEWER_TOKEN="<openssl rand -hex 32>"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
export VULNORAIQ_LOG_LEVEL=INFO
export VULNORAIQ_HOST=127.0.0.1
export VULNORAIQ_PORT=8787
```

## Environment Variables Reference

| Variable | Default | Description |
| --- | --- | --- |
| `VULNORAIQ_ENV` | — | Set to `production` for production-mode validation |
| `VULNORAIQ_HOST` | `127.0.0.1` | Bind address |
| `VULNORAIQ_PORT` | `8787` | Bind port |
| `VULNORAIQ_AUTH_ENABLED` | `true` | Enable authentication |
| `VULNORAIQ_ADMIN_TOKEN` | — | Admin bearer token (min 20 chars in production) |
| `VULNORAIQ_ANALYST_TOKEN` | — | Analyst bearer token |
| `VULNORAIQ_VIEWER_TOKEN` | — | Viewer bearer token |
| `VULNORAIQ_LOG_LEVEL` | `INFO` | Python logging level |
| `VULNORAIQ_CONFIG_DIR` | `config` | Config directory |
| `VULNORAIQ_WEB_USERS_PATH` | `config/web_users.yaml` | Auth config path |
| `VULNORAIQ_WEB_OUTPUT_ROOT` | `reports/output/webui` | Report output root |
| `VULNORAIQ_JOB_STORE_BACKEND` | `sqlite` | Persistence backend (`sqlite` or `json`) |
| `VULNORAIQ_JOB_STORE_PATH` | `reports/output/webui/jobs.db` | Store path |
| `VULNORAIQ_MAX_REQUEST_BODY` | `10485760` | Max request body in bytes (10 MB) |
| `VULNORAIQ_RATE_LIMIT_WINDOW` | `60` | Rate limit window in seconds |
| `VULNORAIQ_RATE_LIMIT_MAX` | `60` | Max requests per window per IP |
| `VULNORAIQ_CSRF_TOKEN_TTL` | `300` | CSRF token lifetime in seconds |
| `VULNORAIQ_TRUST_PROXY_HEADERS` | `false` | Trust `X-Forwarded-For` headers |
| `VULNORAIQ_TRUSTED_PROXY_CIDRS` | — | Comma-separated CIDRs of trusted proxies |

## Production Checklist

- [ ] Set `VULNORAIQ_ENV=production` to enable production-mode validation
- [ ] Set `VULNORAIQ_ADMIN_TOKEN`, `VULNORAIQ_ANALYST_TOKEN`, `VULNORAIQ_VIEWER_TOKEN` (min 20 chars each)
- [ ] Verify `VULNORAIQ_AUTH_ENABLED=true` (default)
- [ ] Run behind a reverse proxy with TLS termination
- [ ] Configure `VULNORAIQ_TRUST_PROXY_HEADERS=true` and `VULNORAIQ_TRUSTED_PROXY_CIDRS`
- [ ] Add rate limiting at the proxy layer (nginx `limit_req`, Caddy `rate_limit`)
- [ ] Use SQLite backend (`VULNORAIQ_JOB_STORE_BACKEND=sqlite`, default)
- [ ] Mount persistent volume for `/data` in container deployments
- [ ] Configure audit log shipping to SIEM
- [ ] Set up periodic database backups and test restore procedure
- [ ] Set up monitoring on `/healthz` and `/readyz`
- [ ] Configure log rotation for audit and application logs
- [ ] Apply least-privilege filesystem permissions
- [ ] Use a secrets manager or restricted `.env` file (never in VCS)
- [ ] Remove or do not rely on `config/web_users.yaml` with demo hashes
- [ ] Test rollback procedure
- [ ] Document incident response procedures
