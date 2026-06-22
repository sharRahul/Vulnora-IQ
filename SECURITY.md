# Security Policy

## Project security posture

VulnoraIQ is a defensive AI security assessment framework for authorised testing of LLM applications, RAG pipelines, AI agents, and orchestration layers.

Version `0.2.0` has passed the **controlled internal enterprise production-readiness gate** for a single-organisation/internal deployment model. It is **not** a public SaaS or multi-tenant hosting platform. Do not expose it directly to the public internet without additional deployment controls, external security review, and operational safeguards.

Current supported deployment boundary:

| Deployment model | Status |
| --- | --- |
| Local demo / development | Supported |
| Controlled internal enterprise deployment | Supported with production configuration validation |
| Public internet-facing deployment | Not recommended without extra controls |
| Multi-tenant SaaS hosting | Not supported |
| Certified VAPT-grade assessment assurance | Not claimed |

See:

- [`README.md`](README.md) for current maturity and quick start guidance
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for production deployment controls
- [`docs/PRODUCTION_READINESS_SCORECARD.md`](docs/PRODUCTION_READINESS_SCORECARD.md) for readiness scoring
- [`docs/PRODUCTION_HARDENING_BACKLOG.md`](docs/PRODUCTION_HARDENING_BACKLOG.md) for remaining gaps and accepted risks
- [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md) for scanner/evaluator limitations
- [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md) for incident handling playbooks

## Responsible use

Use VulnoraIQ only against systems you own or are explicitly authorised to assess.

Do not use this repository, its payloads, or its generated reports for:

- unauthorised testing of third-party systems
- credential theft or phishing
- malware delivery or command execution
- evasion, persistence, or stealth workflows
- bypassing production access controls
- exploiting systems outside an approved test scope

Configured non-demo targets require an explicit authorisation flag. The safe demo target is local and does not require external API keys.

## Supported versions

| Version | Security support | Notes |
| --- | --- | --- |
| `0.2.0` / `0.2.0-rc1` | Active | Controlled internal enterprise deployment candidate |
| `0.0.1.x` | Deprecated | Local/demo framework only; upgrade to `0.2.0` before production-like use |
| Earlier versions | Unsupported | No production-readiness claim |

## Production security controls in `0.2.0`

The hosted Web UI and production deployment path include:

- auth enabled by default and fail-closed
- `VULNORAIQ_ENV=production` runtime validation
- required `VULNORAIQ_ADMIN_TOKEN` in production, minimum 20 characters
- known demo/default token rejection in production
- internal development admin token disabled in production
- constant-time token comparison via `hmac.compare_digest`
- `VULNORAIQ_AUTH_MODE=token` for environment-token auth
- `VULNORAIQ_AUTH_MODE=trusted_proxy` for trusted reverse-proxy identity headers
- trusted proxy CIDR validation via `VULNORAIQ_TRUSTED_PROXY_CIDRS`
- production failure when binding to `0.0.0.0` / `::` without trusted proxy configuration
- CSRF protection on state-changing scan requests
- CSRF token TTL and cleanup
- request body size limits and malformed JSON handling
- per-IP rate limiting and scan concurrency/queue limits
- security headers on normal and error responses
- artifact path-traversal protection
- role-aware `/api/config` output
- auth-protected `/metrics` endpoint by default
- structured JSON audit logging with request correlation IDs
- SQLite job persistence by default with WAL mode, foreign keys, busy timeout, and schema versioning
- backup and restore scripts for SQLite stores
- Dockerfile running as a non-root user with `/data` volume and healthcheck
- Docker Compose production-like example and `.env.production.example`
- CI gates for Ruff, mypy, tests, package metadata, production readiness, dependency checks, and functional acceptance

## Required production configuration

For production-like operation, set at minimum:

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="replace-with-a-strong-random-token-min-20-chars"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
```

When deploying behind a reverse proxy and trusting forwarded identity or client IP headers:

```bash
export VULNORAIQ_TRUST_PROXY_HEADERS=true
export VULNORAIQ_TRUSTED_PROXY_CIDRS="127.0.0.1/32,::1/128"
```

For trusted reverse-proxy identity mode:

```bash
export VULNORAIQ_AUTH_MODE=trusted_proxy
```

Only enable trusted-proxy identity mode when a trusted upstream proxy authenticates users and strips spoofed identity headers from untrusted clients.

Validate runtime configuration before starting production-like deployments:

```bash
python scripts/validate_runtime_production_config.py
python scripts/validate_production_testing_readiness.py
```

## Remaining accepted risks

The following are documented and accepted for controlled internal deployment, but block public SaaS or internet-scale claims:

- no native OIDC/JWT validation yet; trusted-proxy identity mode is the supported enterprise identity bridge
- CSRF and rate-limit stores are in-memory and single-instance
- SQLite is single-node and not high availability
- no built-in WAF, CDN, or DDoS protection
- no SaaS tenant isolation model
- no built-in centralised SIEM pipeline, although structured audit logs are emitted
- scanner/evaluator coverage is starter/framework evidence and not certified VAPT-grade assurance

## Reporting vulnerabilities in this project

Please report vulnerabilities in VulnoraIQ privately.

Preferred options:

1. Open a GitHub Security Advisory for the repository.
2. If advisories are unavailable, open a private issue or contact the maintainer through the repository owner channel.

Do **not** publicly disclose an exploitable vulnerability before maintainers have had a reasonable opportunity to investigate and remediate it.

Include:

- affected version or commit
- affected component, such as Web UI, auth, persistence, reporting, scanner, or CI
- reproduction steps
- expected vs actual behaviour
- impact and exploitability
- whether secrets, tokens, reports, or artifacts may be exposed
- suggested mitigation if known

Please avoid including real secrets, production tokens, private customer data, or sensitive scan artifacts in the report.

## Vulnerability handling expectations

Maintainers should triage reports using the following severity guide:

| Severity | Examples |
| --- | --- |
| Critical | auth bypass, production token leakage, arbitrary file read/write, remote code execution, artifact exposure across users |
| High | CSRF bypass on scan creation, trusted proxy spoofing, path traversal, audit-log secret leakage, production fail-open behaviour |
| Medium | denial of service in controlled deployment, missing security header on sensitive route, overly verbose error disclosure |
| Low | documentation error, safe-demo-only issue, non-sensitive observability bug |

Expected remediation workflow:

1. Confirm scope and affected version.
2. Reproduce in a safe local environment.
3. Add or update regression tests.
4. Fix the root cause without weakening production checks.
5. Run quality gates and production-readiness validation.
6. Update `CHANGELOG.md`, `README.md`, `SECURITY.md`, and relevant runbooks if user action is required.
7. Publish a release note or advisory when appropriate.

## Payload safety policy

Payloads in this repository must remain safe starter examples. Contributions that enable real-world credential theft, malware deployment, harmful bypass workflows, stealth, persistence, or unauthorised exploitation will not be accepted.

Allowed payloads and fixtures:

- safe local demo prompts
- deterministic local good/bad fixtures
- synthetic control-gap examples
- benign OWASP/MITRE mapping examples
- examples that demonstrate detection logic without enabling real-world abuse

Not allowed:

- live credential harvesting workflows
- exploit chains against third-party systems
- malware or persistence payloads
- instructions to bypass access controls in real environments
- payloads intended to exfiltrate secrets from systems outside an authorised test scope

## Secret handling

Never commit:

- real `VULNORAIQ_ADMIN_TOKEN`, analyst tokens, or viewer tokens
- API keys for target systems
- production `.env` files
- private scan reports or customer artifacts
- SQLite production databases or backups
- SIEM credentials or webhook secrets

Use `.env.production.example` as a placeholder-only template. Real deployment values must come from environment variables, a secret manager, or a secure runtime configuration system.

## Security validation commands

Run these before opening a release PR or tagging a production-readiness release candidate:

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
docker build -t vulnoraiq:0.2.0-rc .
python scripts/container_smoke_test.py
```

## Incident response

Use [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md) for response playbooks covering:

- auth token leak
- suspicious scan activity
- rate-limit spikes
- unauthorised access attempt
- report or artifact exposure
- corrupted SQLite store
- failed backup
- dependency vulnerability
- Web UI security issue

## Security boundary summary

VulnoraIQ `0.2.0` is suitable for controlled internal enterprise deployment when configured according to `docs/DEPLOYMENT.md` and validated with the production-readiness scripts. It is not a substitute for external penetration testing, a tenant-isolated SaaS architecture, or certified VAPT-grade assurance.