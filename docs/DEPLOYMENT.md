# Deployment Guide

This guide describes the supported VulnoraIQ `0.2.0` deployment posture.

> **Scope:** VulnoraIQ `0.2.0` is a self-hosted application for authorised AI-agent and LLM-application testing. It is designed to run on a laptop, workstation, lab machine, or internal server controlled by the assessor or organisation. GenAI Security readiness is complete for the current controlled-internal scenario-harness scope.

## Quick start: local development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]

# Safe local CLI demo
vulnoraiq --target demo --profile baseline

# Local Web UI, bound to localhost
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Stop the local Web UI with `Ctrl+C` in the terminal where `vulnoraiq-web` is running.

Health checks:

```bash
curl http://127.0.0.1:8787/healthz
curl http://127.0.0.1:8787/readyz
```

The demo target is safe and local. Configured non-demo targets require explicit authorisation.

## Quick start: self-hosted production-mode validation

Production mode fails closed when required runtime settings are missing or unsafe.

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
export VULNORAIQ_WEB_USERS_PATH=/data/web_users.yaml

python scripts/validate_runtime_production_config.py
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Stop the production-mode Web UI with `Ctrl+C` when it is running in the foreground. If it was started in the background, identify and stop the process listening on port `8787`:

```bash
lsof -ti :8787 | xargs kill
```

Use a forced stop only if the process does not stop cleanly:

```bash
lsof -ti :8787 | xargs kill -9
```

## Release and readiness validation

Run these after checkout, before a release candidate, and after changing docs, mappings, GenAI scenarios, or runtime settings:

```bash
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py
python scripts/validate_runtime_production_config.py
```

The GenAI readiness validator checks `DSGAI01–DSGAI21` coverage, `DSGAI22–DSGAI25` discrepancy tracking, fixture coverage, evidence fields, MITRE ATLAS tactic format, and documentation alignment.

## Container deployment

Build and run with persistent data:

```bash
docker build -t vulnoraiq:0.2.0-rc .
docker run --rm -p 8787:8787 \
  -v vulnoraiq-data:/data \
  -e VULNORAIQ_ENV=production \
  -e VULNORAIQ_AUTH_ENABLED=true \
  -e VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)" \
  -e VULNORAIQ_JOB_STORE_BACKEND=sqlite \
  -e VULNORAIQ_JOB_STORE_PATH=/data/jobs.db \
  -e VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports \
  vulnoraiq:0.2.0-rc
```

The container runs as a non-root user, uses `/data` for SQLite DB and reports, exposes port `8787`, and includes a `/healthz` healthcheck.

Stop a foreground `docker run` container with `Ctrl+C`. For a detached container, stop it by container ID or name:

```bash
docker ps
docker stop <container-id-or-name>
```

## Docker Compose

```bash
cp .env.production.example .env.production
# Edit .env.production and replace every placeholder token before starting.
docker compose up --build
```

Stop Docker Compose deployments with:

```bash
docker compose down
```

Do not commit real `.env.production` files. Commit only `.env.production.example` with placeholders.

## Authentication and roles

Auth is enabled by default. Use token mode for direct self-hosted runs and trusted reverse-proxy identity mode only when an approved reverse proxy performs authentication and strips inbound identity headers before setting its own.

```bash
export VULNORAIQ_AUTH_MODE=token
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_ANALYST_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_VIEWER_TOKEN="$(openssl rand -hex 32)"
```

| Role | Permissions |
| --- | --- |
| `viewer` | view scans, download artifacts |
| `analyst` | viewer + start demo scans |
| `admin` | analyst + start configured-target scans, manage runtime |

## Reverse proxy and TLS

For internal server deployments, the built-in HTTP server can run behind a reverse proxy such as nginx or Caddy for TLS termination and enterprise network controls. Local laptop/workstation demos can remain bound to `127.0.0.1`.

```bash
export VULNORAIQ_TRUST_PROXY_HEADERS=true
export VULNORAIQ_TRUSTED_PROXY_CIDRS="127.0.0.1/32,::1/128"
```

## Persistence, backup, and audit

SQLite is the default and production-supported backend for controlled internal deployment.

```bash
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
```

Audit events are emitted as JSON lines on the `vulnoraiq.audit` logger. Audit logs must not include auth tokens, CSRF tokens, request bodies, secrets, or full report contents.

Backup and restore commands:

```bash
python scripts/backup_sqlite_store.py /data/jobs.db /data/backups/jobs-$(date +%Y%m%d-%H%M%S).db --compress --validate --retention 90
python scripts/restore_sqlite_store.py /data/backups/jobs-YYYYMMDD-HHMMSS.db.gz /tmp/vulnoraiq-restore-test.db --compressed --validate
```

## GenAI Security deployment notes

GenAI readiness assets are repository assets, not runtime secrets:

- scenario manifest: `benchmarks/fixtures/genai/scenarios.yaml`
- evaluator suite: `core/genai_evaluators.py`
- readiness validator: `scripts/validate_genai_readiness.py`
- tests: `tests/test_genai_readiness_validation.py`

Run the GenAI validator before release and after modifying GenAI docs, scenario coverage, evidence fields, or source discrepancy tracking. The validator passing means the current-scope GenAI readiness gate is consistent; it does not prove production-validated real-world GenAI detection assurance.

## Production Checklist

Confirm each item before a self-hosted internal deployment:

- [ ] `python scripts/validate_runtime_production_config.py` passes with `VULNORAIQ_ENV=production`.
- [ ] `VULNORAIQ_AUTH_ENABLED=true` and a strong `VULNORAIQ_ADMIN_TOKEN` are set.
- [ ] Persistent state — `VULNORAIQ_JOB_STORE_PATH`, `VULNORAIQ_WEB_OUTPUT_ROOT`, and `VULNORAIQ_WEB_USERS_PATH` — lives on the mounted `/data` volume.
- [ ] For internal server deployments, the service runs behind an approved reverse proxy terminating TLS when remote access is required.
- [ ] Scheduled backup of the SQLite store is in place and a restore has been validated.
- [ ] Audit logging is enabled and audit logs are shipped and retained per internal policy.
- [ ] `python scripts/validate_genai_readiness.py` passes after any GenAI docs or scenario changes.
