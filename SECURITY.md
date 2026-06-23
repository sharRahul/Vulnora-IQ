# Security Policy

This document defines VulnoraIQ's security boundary, supported versions, responsible-use rules, vulnerability reporting process, production controls, and validation expectations.

---

## Security posture

VulnoraIQ is a defensive AI security assessment framework for authorised testing of LLM applications, RAG pipelines, AI agents, tool-using systems, GenAI data-security surfaces, and orchestration layers.

`0.2.0` has passed the **controlled internal enterprise production-readiness gate** for a single-organisation/internal deployment model. GenAI Security readiness is **working starter complete** for controlled internal assessment use with safe synthetic `DSGAI01–DSGAI21` scenario coverage.

It is **not**:

- a public SaaS platform
- a multi-tenant platform
- an unsupervised internet-facing service
- a certified VAPT-grade assurance tool
- a substitute for independent testing
- independently validated real-world GenAI detection coverage for every category

Do not expose VulnoraIQ directly to the public internet without additional controls, external review, and operational safeguards.

---

## Supported deployment boundary

| Deployment model | Status | Notes |
| --- | --- | --- |
| Local demo / development | Supported | Safe demo target; no external API keys required |
| Controlled internal enterprise deployment | Supported | Requires production configuration validation and real secrets |
| GenAI Security internal assessment readiness | Working starter | `DSGAI01–DSGAI21` safe synthetic scenarios, deterministic evaluators, and CI validation |
| Public internet-facing deployment | Not recommended | Requires extra WAF/CDN/DDoS, external testing, and hardening |
| Multi-tenant SaaS hosting | Not supported | No tenant isolation model in `0.2.0` |
| Certified VAPT-grade assurance | Not claimed | Findings require human review and deeper validation |

See also:

- [`README.md`](README.md) — maturity and quick start
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
| `0.2.0` / `0.2.0-rc1` | Active | Controlled internal enterprise deployment candidate with GenAI working-starter readiness |
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

---

## Production security controls in `0.2.0`

The controlled-internal production path includes:

### Authentication and authorisation

- auth enabled by default
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
- audit events for auth failure, authz failure, CSRF failure, rate limiting, scan creation, scan queue full, artifact download, unsafe artifact paths, malformed JSON, oversized requests, and internal errors

### GenAI Security readiness controls

- source-confirmed `DSGAI01–DSGAI21` scenario coverage in `benchmarks/fixtures/genai/scenarios.yaml`
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

Minimum controlled-internal production configuration:

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

The following are accepted only for controlled internal deployment and block public SaaS/multi-tenant claims:

- no native OIDC/JWT validation yet
- trusted-proxy identity is the current enterprise identity bridge
- CSRF token store is in-memory and single-instance
- rate-limit store is in-memory and single-instance
- SQLite is single-node and not high availability
- no tenant isolation model
- no built-in WAF/CDN/DDoS controls
- no distributed worker or shared queue architecture
- no certified third-party testing report for the Web UI or assessment engine
- scanner/evaluator results are starter/framework evidence requiring human review
- GenAI Security coverage is working starter and based on safe synthetic scenarios until validated in authorised real environments

---

## Reporting vulnerabilities

Please report vulnerabilities privately.

Preferred channels:

1. Open a GitHub Security Advisory for the repository.
2. If advisories are not available, contact the maintainer through a private repository-owner channel.

Do **not** publicly disclose an exploitable issue before maintainers have had a reasonable opportunity to investigate and remediate it.

Include:

- affected version or commit
- affected component: Web UI, auth, proxy trust, persistence, reporting, scanner, GenAI readiness, CI, docs, or packaging
- reproduction steps
- expected and actual behaviour
- whether the issue affects local-only, controlled internal, or broader deployment assumptions
