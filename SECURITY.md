
## Docker-first safe lab status

VulnoraIQ is now configured as a Docker-first, self-hosted AI-agent security testing lab. Real target validation, scan execution, mock-agent traffic, evidence capture, report generation, and automated checks are expected to run inside Docker Compose by default. The host should only run Docker commands, open the WebUI at `http://localhost:8787`, and read explicitly exported reports.

Quick start:

```bash
docker compose build
docker compose up -d
docker compose ps
```

CLI examples must be run inside the container:

```bash
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
```

See `docs/DOCKER_TESTING.md`, `docs/SAFETY_MODEL.md`, `docs/TARGET_CONFIGURATION.md`, `docs/AI_AGENT_TESTING.md`, `docs/WEBUI_GUIDE.md`, and `docs/CLI_GUIDE.md`.

# Security Policy

This document defines VulnoraIQ's security boundary, supported versions, responsible-use rules, vulnerability reporting process, production controls, and validation expectations.

---

## Security posture

VulnoraIQ is a self-hosted defensive AI security assessment application for authorised testing of LLM applications, RAG pipelines, AI agents, tool-using systems, GenAI data-security surfaces, and orchestration layers.

`0.2.0` has passed the **controlled internal production-readiness gate** for a laptop, workstation, lab-machine, or internal-server deployment model. GenAI Security readiness is **complete for the current controlled-internal scenario-harness scope** with safe synthetic `DSGAI01–DSGAI21` scenario coverage.

VulnoraIQ findings are framework evidence for authorised review. They are not certified VAPT-grade assurance, a substitute for independent testing, or independently validated real-world GenAI detection coverage for every category.

---

## Supported deployment boundary

| Deployment model | Status | Notes |
| --- | --- | --- |
| Local laptop / workstation demo | Complete | Safe demo target; no external API keys required |
| Standalone local Web UI launcher | Complete | Loopback-only laptop/workstation convenience path with startup checks and local stop control; not for shared/exposed deployment |
| Self-hosted internal server deployment | Complete | Requires production configuration validation and real secrets |
| GenAI Security internal assessment readiness | Complete for current scope | `DSGAI01–DSGAI21` safe synthetic scenarios, deterministic evaluators, and CI validation |
| Certified VAPT-grade assurance | Not claimed | Findings require human review and deeper validation |

See also:

- [`README.md`](README.md) — maturity, standalone launcher, and quick start
- [`ACCEPTABLE_USE.md`](ACCEPTABLE_USE.md) — acceptable-use and misuse disclaimer
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — deployment controls
- [`docs/RUNBOOK.md`](docs/RUNBOOK.md) — operations procedures
- [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md) — incident playbooks
- [`docs/PRODUCTION_READINESS_SCORECARD.md`](docs/PRODUCTION_READINESS_SCORECARD.md) — readiness scoring
- [`docs/PRODUCTION_HARDENING_BACKLOG.md`](docs/PRODUCTION_HARDENING_BACKLOG.md) — remaining risks
- [`docs/genai/PRODUCTION_READINESS_PLAN.md`](docs/genai/PRODUCTION_READINESS_PLAN.md) — GenAI Security readiness plan
- [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md) — scanner/evaluator limits

---

## Supported versions

| Version | Security support | Status |
| --- | --- | --- |
| `0.2.0` / `0.2.0-rc1` | Active | Self-hosted internal deployment candidate with complete current-scope GenAI readiness |
| `0.0.1.x` | Deprecated | Local/demo use only; upgrade before production-like use |
| Earlier versions | Unsupported | No production-readiness claim |

Security fixes should target the latest supported `0.2.x` branch unless a maintainer explicitly decides otherwise.

---

## Responsible use

Use VulnoraIQ only against systems you own or are explicitly authorised to assess.

Allowed use:

- safe local demo testing
- internal AI security validation
- authorised AI red-team exercises
- defensive control testing
- CI regression checks for your own AI systems
- evidence collection for internal review
- GenAI data-security scenario validation for approved systems

Configured non-demo targets require explicit authorisation. Reports and artifacts may contain sensitive evidence and must be handled accordingly.

Users are solely responsible for complying with [`ACCEPTABLE_USE.md`](ACCEPTABLE_USE.md), obtaining required authorisation, and using VulnoraIQ only within the defensive assessment scope. To the fullest extent permitted by law, the maintainer and contributors disclaim responsibility for prohibited, unlawful, unauthorised, or otherwise improper use by any user or third party.

---

## Local standalone launcher security boundary

The standalone launcher files (`launch-vulnoraiq-webui.bat`, `launch-vulnoraiq-webui.command`, `launch-vulnoraiq-webui.sh`, and `launch-vulnoraiq-webui.py`) are intended for local laptop/workstation use.

Launcher mode:

- binds to loopback by default;
- prepares local runtime output under `reports/output/webui/`;
- opens the Web UI in the user's browser;
- exposes startup/dependency checks in the Web UI;
- enables the **Stop local server** action only for the explicit local launcher runtime;
- uses local development settings for convenience.

Do **not** expose launcher mode on a shared network interface. For shared, remote, or internal-server deployments, use production mode with auth enabled, strong tokens or trusted reverse-proxy identity, production configuration validation, and the standard `vulnoraiq-web` startup path.

---

## Production security controls in `0.2.0`

The self-hosted internal production path includes:

### Authentication and authorisation

- auth enabled by default for the hosted server and required in production
- fail-closed protected endpoints
- `VULNORAIQ_ENV=production` runtime validation
- required `VULNORAIQ_ADMIN_TOKEN` in production
- minimum 20-character admin token in production
- known demo/default token rejection
- internal development admin token disabled in production
- constant-time token comparison using `hmac.compare_digest`
- token mode via `VULNORAIQ_AUTH_MODE=token`
- trusted reverse-proxy identity mode via `VULNORAIQ_AUTH_MODE=trusted_proxy`
- trusted proxy identity accepted only from configured CIDRs
- viewer, analyst, and admin roles

### Web hardening

- CSRF protection for `POST /api/scans`
- launcher-mode CSRF validation for local stop-server requests
- configurable CSRF TTL and cleanup
- request body size limit
- malformed JSON and invalid `Content-Length` handling
- standard JSON API errors
- security headers on normal and error responses
- artifact path protection
- role-aware `/api/config`
- auth-protected `/metrics` by default

### Abuse and workload controls

- per-IP in-memory rate limiting
- scan concurrency limit
- scan queue limit
- audit events for rate-limit and queue rejections

### Persistence and operations

- SQLite default job store
- WAL mode
- foreign keys
- busy timeout
- schema versioning
- JSON backend marked legacy/development only and rejected in production
- SQLite backup and restore scripts with validation, compression, and retention support

### Observability

- `/healthz` liveness endpoint
- `/readyz` readiness endpoint
- Prometheus-format `/metrics` endpoint
- structured JSON audit logs with request correlation IDs
- audit events for auth failure, authz failure, CSRF failure, rate limiting, scan creation, scan queue full, artifact download, unsafe artifact paths, malformed JSON, oversized requests, server shutdown request, and internal errors

### GenAI Security readiness controls

- complete source-confirmed `DSGAI01–DSGAI21` scenario coverage in `benchmarks/fixtures/genai/scenarios.yaml` for the current controlled-internal scope
- `DSGAI22–DSGAI25` preserved as source discrepancy / map-later items
- deterministic evaluator primitives in `core/genai_evaluators.py`
- GenAI readiness validator in `scripts/validate_genai_readiness.py`
- regression tests in `tests/test_genai_readiness_validation.py`
- CI gates in both workflow paths
- package metadata validation fails if GenAI readiness assets drift

### Container and CI

- non-root Dockerfile
- `/data` volume for SQLite DB and reports
- healthcheck
- Docker Compose example
- `.env.production.example` with placeholders only
- Ruff, mypy, pytest, `pip check`, `pip-audit`, package metadata validation, OWASP/ATLAS mapping validation, GenAI readiness validation, production readiness validation, and functional acceptance in CI/release flow

---

## Required production configuration

Minimum self-hosted internal production configuration:

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="replace-with-a-strong-random-token-min-20-chars"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
```

Validate before start:

```bash
python scripts/validate_runtime_production_config.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
```

For reverse proxy deployments:

```bash
export VULNORAIQ_TRUST_PROXY_HEADERS=true
export VULNORAIQ_TRUSTED_PROXY_CIDRS="127.0.0.1/32,::1/128"
```

For trusted proxy identity mode:

```bash
export VULNORAIQ_AUTH_MODE=trusted_proxy
```

Only enable trusted proxy identity mode when the proxy authenticates users and strips spoofed identity headers from external requests.

---

## Remaining accepted risks

The following are accepted for the self-hosted internal deployment model and should be revisited as the application matures:

- no native OIDC/JWT validation yet
- trusted-proxy identity is the current enterprise identity bridge
- launcher mode is local-loopback convenience only and must not be exposed as a shared service
- CSRF token store is in-memory and single-instance
- rate-limit store is in-memory and single-instance
- SQLite is single-node and not high availability
- no distributed worker or shared queue architecture
- no certified third-party testing report for the Web UI or assessment engine
- scanner/evaluator results are framework evidence requiring human review
- GenAI Security coverage is complete for the current safe synthetic `DSGAI01–DSGAI21` scenario-harness scope; authorised real-environment validation remains a future maturity item

---

## Reporting vulnerabilities

Please report vulnerabilities privately.

Preferred channels:

1. Open a GitHub Security Advisory for the repository.
2. If advisories are not available, contact the maintainer through a private repository-owner channel.

Do **not** publicly disclose an exploitable issue before maintainers have had a reasonable opportunity to investigate and remediate it.

Include:

- affected version or commit
- affected component: Web UI, auth, proxy trust, persistence, reporting, scanner, GenAI readiness, CI, docs, packaging, local launcher, or stop-server control
- reproduction steps
- expected and actual behaviour
- whether the issue affects local-only or self-hosted internal deployment assumptions