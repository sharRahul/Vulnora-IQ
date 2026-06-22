# Implementation Status

This document separates current working capability from roadmap items so users can understand what is ready today.

> **Current maturity:** VulnoraIQ version `0.2.0` has passed the **controlled internal enterprise production-readiness gate** with security hardening, SQLite persistence, auth, CSRF, rate limiting, audit logging, metrics, backup/restore tooling, container support, and production startup validation. It is **not ready for public internet-facing, multi-tenant SaaS, or unsupervised production hosting** without additional controls such as OIDC/SSO, horizontal scaling, external penetration testing, WAF/CDN/DDoS protection, HA persistence, and tenant isolation. See [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) for scored readiness and [`ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md) for scanner/evaluator assurance limitations.

> **Important limitation:** OWASP LLM 2025 coverage now has implementation specs, safe starter oracle coverage, deterministic local evaluator primitives, and local good/bad fixtures for all 10 categories. MITRE ATLAS AI technique coverage now has a source-driven planning matrix and unmapped backlog preservation, but the matrix is not the same as active production-validated detection coverage. MITRE ATLAS-derived documentation is tracked in `THIRD_PARTY_NOTICES.md`. Treat output as development evidence, not validated security assurance or certified VAPT output.

## Seven-phase implementation status

| Phase | Status | Completed implementation |
| --- | --- | --- |
| Phase 1 — OWASP depth | Working-alpha starter | `docs/owasp/` contains implementation specs for all 10 OWASP LLM 2025 categories. |
| Phase 2 — Safe demo fixtures | Working-alpha starter | `examples/local_demo_targets/owasp_fixture_targets.py` models local good/bad control behaviour for all 10 categories. |
| Phase 3 — Stronger evaluators | Working-alpha starter | `core/evaluators.py` adds deterministic local evaluators for text checks, schema checks, source access, provenance, approval, citations, action boundaries, resource limits, and manual review. |
| Phase 4 — Contract-tested adapters | Working starter | `config/target_contracts.yaml` and `integrations/contract_validation.py` validate configured target adapter shapes before authorised testing. |
| Phase 5 — Web UI hardening | Controlled-internal production ready | `webui/hosted_server.py`, `webui/auth.py`, `webui/persistent_jobs.py`, and `webui/production_checks.py` provide the hardened Web UI with env-token auth, trusted proxy identity mode, CSRF, rate limiting, security headers, proxy trust, audit logging, metrics, request IDs, concurrency limits, and startup validation. |
| Phase 6 — Report quality and presentation | Working starter | Report generation includes structured evidence; `reports/html_export_package.py` builds a branded export bundle; `docs/assets/vulnoraiq-dashboard-example.svg` provides a README dashboard example image. |
| Phase 7 — Release gates | Controlled-internal production ready | `scripts/validate_package_metadata.py`, `scripts/validate_production_testing_readiness.py`, `scripts/validate_runtime_production_config.py`, backup/restore scripts, Docker smoke tooling, and CI gates validate package, runtime, docs, readiness, and functional acceptance. |

## Current working capability

| Area | Status | Notes |
| --- | --- | --- |
| Python package scaffold | Working starter | VulnoraIQ version `0.2.0` installs as a Python package with CLI entry points. |
| Functional acceptance runner | Working starter | `scripts/run_functional_test.py` runs a safe demo/baseline assessment, validates outputs, and refreshes dashboard example SVG. |
| Production readiness gate | Controlled-internal production ready | `scripts/validate_production_testing_readiness.py` validates all production controls and documentation guardrails. |
| Production runtime config validation | Controlled-internal production ready | `scripts/validate_runtime_production_config.py` validates runtime environment before startup. |
| Dashboard example image | Working starter | `docs/assets/vulnoraiq-dashboard-example.svg` is referenced in `README.md`. |
| Modern Web UI | Controlled-internal production ready | `webui/hosted_server.py` — hardened HTTP server with auth, CSRF, rate limiting, security headers, proxy trust, audit logging, metrics, request IDs, concurrency limits, and structured error handling. |
| Authentication | Controlled-internal production ready | `webui/auth.py` — env-driven token auth with hmac constant-time comparison, production-mode validation, trusted reverse-proxy identity headers, role-based access control. |
| CSRF protection | Controlled-internal production ready | Per-session CSRF tokens with configurable TTL, periodic cleanup, validated on state-changing requests. |
| Rate limiting | Controlled-internal production ready | IP-based in-memory rate limiting with configurable window/max and periodic cleanup. Use proxy/WAF/shared controls for public or multi-instance deployments. |
| Security headers | Controlled-internal production ready | CSP, HSTS conditional behaviour, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy on every response. |
| Proxy IP trust | Controlled-internal production ready | `X-Forwarded-For` and trusted proxy identity are trusted only from configured CIDRs. |
| Audit logging | Controlled-internal production ready | Structured JSON-line audit with request IDs, 15+ event types, no token/secret/request-body leakage. |
| Prometheus metrics | Controlled-internal production ready | `/metrics` endpoint with request/scan/auth counters, protected by default. |
| Job persistence | Controlled-internal production ready | SQLite default with WAL mode, schema versioning, foreign keys, and busy timeout. JSON store is legacy/dev only. |
| Backup and restore | Controlled-internal production ready | `scripts/backup_sqlite_store.py` and `scripts/restore_sqlite_store.py` use the SQLite online backup API, validation, compression, and retention. |
| Container deployment | Controlled-internal production ready | Dockerfile with non-root user, `/data` volume, healthcheck; `docker-compose.yml` with production env example. |
| Concurrency limits | Controlled-internal production ready | Configurable max concurrent scans and queue limit, with audit of rejected requests. |
| Scan artifact security | Controlled-internal production ready | Path-traversal prevention, allowlist-based artifact lookup, audit logging, proper Content-Disposition. |
| Runbook and incident response | Controlled-internal production ready | `docs/RUNBOOK.md`, `docs/INCIDENT_RESPONSE.md`, `docs/RELEASE_CHECKLIST.md`. |
| Demo target | Working | The default `demo` target uses an in-memory echo client and requires no external API keys. |
| Local demo targets | Working-alpha starter | Safe HTTP JSON, control-gap, and OWASP good/bad fixture targets for local demonstration and tests. |
| Configured target adapters | Working starter | Chat-completions-compatible, Ollama-style generate, webhook JSON, and HTTP JSON endpoint shapes. |
| Profiles | Working starter | `baseline`, `rag`, `agent`, and `full` profiles defined; coverage depth is still starter-level. |
| Scanner | Working starter | Scanner loads config, runs profile modules, scores findings, evaluates policy, and creates evidence. Findings are not yet validated as production-grade security assertions. |
| OWASP LLM 2025 oracle coverage | Working starter | Safe starter oracle coverage for all 10 OWASP LLM 2025 categories. |
| MITRE ATLAS AI matrix | Working starter | Planning matrix with source-driven generation and unmapped backlog preservation. |
| Package metadata validation | Working starter | Validates package name, version, CLI entries, README maturity warnings, OWASP docs, MITRE ATLAS doc, third-party notices, functional test assets, evaluators, fixtures before release. |
| CI | Controlled-internal production ready | GitHub Actions across Python 3.10/3.11/3.12; Ruff, mypy, pytest, pip check, pip-audit, metadata validation, production readiness validation, demo scan, functional acceptance readiness path. |

## Current safe usage

Run the Web UI in development mode:

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Run the Web UI in production mode:

```bash
VULNORAIQ_ENV=production \
VULNORAIQ_AUTH_ENABLED=true \
VULNORAIQ_ADMIN_TOKEN="your-strong-token-min-20-chars" \
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Validate production config before starting:

```bash
python scripts/validate_runtime_production_config.py
```

Run backup:

```bash
python scripts/backup_sqlite_store.py \
  /data/jobs.db \
  /data/backups/jobs-$(date +%Y%m%d).db \
  --compress \
  --validate \
  --retention 90
```

Validate production readiness:

```bash
python scripts/validate_production_testing_readiness.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness \
  --screenshot docs/assets/vulnoraiq-dashboard-example.svg
```

For any configured target outside demo mode:

1. Confirm the target is owned by you or explicitly approved for assessment.
2. Replace the placeholder endpoint in `config/targets.yaml`.
3. Validate target contracts before testing.
4. Set any required token environment variable.
5. Run with the CLI authorisation flag or tick the Web UI authorisation confirmation.
6. Treat results as experimental until OWASP and ATLAS coverage checks are validated.
7. Store reports securely and review evidence before sharing.

## Implementation roadmap status

All production hardening blockers PRD-001 through PRD-010 are closed for controlled internal enterprise deployment. The project has gate-level 10/10 controlled-internal readiness, while the detailed scorecard remains lower where non-blocking improvements are still tracked.

The next phases should focus on:

- Public internet / SaaS / multi-tenant readiness: OIDC/JWT-native identity, tenant isolation, WAF/CDN/DDoS controls, distributed rate limiting, HA persistence, and external penetration testing.
- Scanner/evaluator depth: deeper check logic, evaluator thresholds, fixture realism, and real-world validation.
- Report language and assurance validation for real-world VAPT claims.

## Documentation rule

README, `SECURITY.md`, and all top-level docs must remain aligned. If a capability is only a starter, placeholder, partial, experimental, accepted risk, or roadmap item, mark it as such everywhere it appears.