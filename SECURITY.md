# Security Policy

This document defines VulnoraIQ's security boundary, supported versions, responsible-use rules, vulnerability reporting process, production controls, and validation expectations.

---

## Security posture

VulnoraIQ is a defensive AI security assessment framework for authorised testing of LLM applications, RAG pipelines, AI agents, tool-using systems, and orchestration layers.

`0.2.0` has passed the **controlled internal enterprise production-readiness gate** for a single-organisation/internal deployment model.

It is **not**:

- a public SaaS platform
- a multi-tenant platform
- an unsupervised internet-facing service
- a certified VAPT-grade assurance tool
- a substitute for independent penetration testing

Do not expose VulnoraIQ directly to the public internet without additional controls, external review, and operational safeguards.

---

## Supported deployment boundary

| Deployment model | Status | Notes |
| --- | --- | --- |
| Local demo / development | Supported | Safe demo target; no external API keys required |
| Controlled internal enterprise deployment | Supported | Requires production configuration validation and real secrets |
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
- [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md) — scanner/evaluator limits

---

## Supported versions

| Version | Security support | Status |
| --- | --- | --- |
| `0.2.0` / `0.2.0-rc1` | Active | Controlled internal enterprise deployment candidate |
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

Prohibited use:

- unauthorised testing of third-party systems
- credential theft or phishing
- malware delivery or command execution
- persistence, stealth, evasion, or bypass workflows
- exploitation outside an approved scope
- attempts to exfiltrate secrets from systems you do not own or administer

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
- artifact path-traversal protection
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
- audit events for auth failure, authz failure, CSRF failure, rate limiting, scan creation, scan queue full, artifact download, traversal attempts, malformed JSON, oversized requests, and internal errors

### Container and CI

- non-root Dockerfile
- `/data` volume for SQLite DB and reports
- healthcheck
- Docker Compose example
- `.env.production.example` with placeholders only
- Ruff, mypy, pytest, `pip check`, `pip-audit`, package metadata validation, production readiness validation, and functional acceptance in CI/release flow

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
- no certified third-party penetration-test report for the Web UI or assessment engine
- scanner/evaluator results are starter/framework evidence requiring human review

---

## Reporting vulnerabilities

Please report vulnerabilities privately.

Preferred channels:

1. Open a GitHub Security Advisory for the repository.
2. If advisories are not available, contact the maintainer through a private repository-owner channel.

Do **not** publicly disclose an exploitable issue before maintainers have had a reasonable opportunity to investigate and remediate it.

Include:

- affected version or commit
- affected component: Web UI, auth, proxy trust, persistence, reporting, scanner, CI, docs, or packaging
- reproduction steps
- expected vs actual behaviour
- impact and exploitability
- whether tokens, reports, artifacts, or target data may be exposed
- logs or screenshots with secrets redacted
- suggested mitigation if known

Do not include real production tokens, API keys, private customer data, or sensitive scan artifacts in the report.

---

## Severity guide

| Severity | Examples |
| --- | --- |
| Critical | auth bypass, production token leakage, arbitrary file read/write, RCE, cross-user artifact exposure, production fail-open behaviour |
| High | CSRF bypass on scan creation, trusted proxy spoofing, path traversal, audit-log secret leakage, unauthorised report access |
| Medium | controlled-deployment DoS, missing security header on sensitive route, overly verbose error disclosure, broken backup validation |
| Low | documentation mismatch, safe-demo-only issue, non-sensitive monitoring bug |

---

## Maintainer remediation workflow

For security fixes:

1. Confirm scope and affected versions.
2. Reproduce safely with a failing regression test.
3. Fix the root cause without weakening production controls.
4. Add or update tests.
5. Run quality gates and production-readiness validation.
6. Update `CHANGELOG.md`, `README.md`, `SECURITY.md`, and relevant docs if user action is required.
7. Publish a release note or advisory when appropriate.

Required validation:

```bash
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
python scripts/validate_package_metadata.py
python scripts/validate_production_testing_readiness.py
python scripts/validate_runtime_production_config.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness \
  --screenshot docs/assets/vulnoraiq-dashboard-example.svg
```

If Docker is available:

```bash
docker build -t vulnoraiq:security-fix .
python scripts/container_smoke_test.py
```

---

## Payload and fixture safety policy

Payloads and fixtures in this repository must remain safe starter examples.

Allowed:

- local demo prompts
- deterministic local good/bad fixtures
- synthetic control-gap examples
- benign OWASP/MITRE mapping examples
- examples that demonstrate detection logic without enabling real-world abuse

Not allowed:

- live credential harvesting workflows
- exploit chains against third-party systems
- malware, persistence, or stealth payloads
- instructions to bypass access controls in real environments
- payloads intended to exfiltrate secrets outside an authorised test scope
- destructive payloads that could harm third-party systems

---

## Secret handling

Never commit:

- real `VULNORAIQ_ADMIN_TOKEN`, analyst token, or viewer token
- target-system API keys
- production `.env` files
- private scan reports
- customer artifacts
- production SQLite databases or backups
- SIEM credentials
- webhook secrets

Use `.env.production.example` only as a placeholder template. Real deployment values must come from environment variables, a secret manager, or secure runtime configuration.

---

## Incident response

Use [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md) for response procedures covering:

- auth token leak
- unauthorised access attempt
- trusted proxy spoofing attempt
- CSRF failure spike
- rate-limit spike or scan queue exhaustion
- report or artifact exposure
- corrupted SQLite store
- failed backup or restore
- dependency vulnerability
- Web UI security bug

Immediate containment for high/critical issues:

1. Preserve logs and affected SQLite/report artifacts.
2. Restrict network access at the reverse proxy if exposure is suspected.
3. Rotate relevant tokens.
4. Validate runtime config.
5. Back up the SQLite store before destructive actions.
6. Open a private advisory or security issue.

---

## Assessment assurance boundary

VulnoraIQ scan output is evidence for investigation. It is not automatically a confirmed vulnerability.

Current coverage includes safe starter oracles, local fixtures, and implementation specs for OWASP LLM 2025 categories, plus MITRE ATLAS planning mappings. This does not prove real-world detection depth across production AI systems.

Before any VAPT-grade claim, the project needs deeper evaluator logic, calibrated thresholds, richer real-world fixtures, external penetration testing, and report-language review.

---

## Security boundary summary

VulnoraIQ `0.2.0` is suitable for controlled internal enterprise deployment when configured according to [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) and validated with the production-readiness scripts.

It is not yet suitable for unsupervised public internet exposure, multi-tenant SaaS hosting, or certified VAPT-grade assurance claims.