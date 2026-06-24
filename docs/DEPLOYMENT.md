# Deployment guide

This guide describes the supported VulnoraIQ `0.2.0` deployment posture.

> **Supported posture:** self-hosted laptop/workstation/internal-server AI security testing lab for authorised assessments.  
> **Safe default:** Docker Compose lab for real local AI-agent, RAG, webhook, Ollama-style, and tool-loop testing.  
> **Not claimed:** certified VAPT-grade assurance or permission to test systems without explicit approval.

## 1. Recommended Docker-first lab

Use this path for real local AI-agent testing and demonstrations of target validation, scan execution, evidence capture, reports, and WebUI target management.

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open <http://localhost:8787>.

The Docker lab sets:

```text
VULNORAIQ_CONFIG_DIR=/app/config
VULNORAIQ_TARGET_CONFIG=targets.docker.yaml
VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
VULNORAIQ_EVIDENCE_DIR=/data/evidence
VULNORAIQ_AUDIT_DIR=/data/audit
```

## 2. Docker services

| Service | Description |
| --- | --- |
| `vulnoraiq-web` | Hosted WebUI, scanner, CLI, SQLite job store, reports, evidence, audit logs, healthcheck. |
| `local-mock-agent` | Deterministic local mock AI target with chat-completions, Ollama-generate, RAG, webhook, and tool-loop endpoints. |
| `test-runner` | Optional test profile service. |

The lab network is private/internal. Do not replace it with host networking for normal use.

## 3. Production-mode internal server

For shared/internal-server use, run behind a reverse proxy with TLS and enable auth.

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
export VULNORAIQ_EVIDENCE_DIR=/data/evidence
export VULNORAIQ_AUDIT_DIR=/data/audit
# Legacy/user-file auth path is disabled for production; keep VULNORAIQ_WEB_USERS_PATH unset.

python scripts/validate_runtime_production_config.py
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Production mode fails closed when required controls are missing or unsafe.

## 4. Production Checklist

Before exposing the service beyond local loopback, confirm:

- `VULNORAIQ_ADMIN_TOKEN` is set to a strong secret;
- `VULNORAIQ_WEB_USERS_PATH` is not used as a production credential source;
- the service is behind a trusted reverse proxy;
- TLS is enabled at the reverse proxy;
- audit logs are stored under a controlled path;
- backup and restore procedures for SQLite, reports, and evidence are tested;
- `/metrics` access is protected by auth or network controls;
- only authorised targets and safety profiles are configured.

## 5. Reverse proxy and TLS

For remote internal access:

- terminate TLS at a trusted reverse proxy;
- keep `vulnoraiq-web` bound to loopback or an internal network;
- configure trusted proxy CIDRs before trusting forwarded headers;
- use strong environment-backed tokens or trusted reverse-proxy identity;
- protect `/metrics` with auth;
- store logs, reports, and backups in controlled locations.

## 6. Local standalone launcher

The local launcher remains supported for laptop/workstation demo and development use.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python launch-vulnoraiq-webui.py
```

Launcher mode is loopback/local. Do not use launcher-mode auth-disabled defaults for shared deployments.

## 7. WebUI deployment details

The supported WebUI is the React console:

- source: `webui/console/`;
- built static assets: `webui/static/console/`;
- runtime server: `webui/hosted_server.py`;
- Python package data: `webui/static/console/*` and `webui/static/console/assets/*`.

Node is required only to develop or rebuild the console. The Python server serves the built bundle at runtime.

## 8. Validation gates

Run before release or shared deployment:

```bash
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py --output-dir reports/output/production-readiness
python scripts/validate_runtime_production_config.py
```

For browser flow validation:

```bash
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

For Docker validation:

```bash
python scripts/docker_smoke_test.py
```

## 9. Data paths

| Path | Purpose |
| --- | --- |
| `/data/jobs.db` | SQLite job persistence. |
| `/data/reports` | Markdown, JSON, SARIF, dashboard, and HTML outputs. |
| `/data/evidence` | Evidence files. |
| `/data/audit` | Structured audit logs. |

Back up SQLite and report/evidence paths according to the runbook before upgrades or release validation.

## 10. Deployment limitations

The current codebase is suitable for self-hosted internal use with documented controls. Remaining maturity items include signed/notarised installers, OIDC/JWT integration, image signing/scanning, SAST/DAST pipeline, SIEM-specific rule packs, multi-instance shared state, and independent assurance validation.
