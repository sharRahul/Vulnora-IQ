# Production Hardening Backlog

Status: live blocker register  
Current operational readiness: 10/10 for self-hosted internal deployment  
Target: laptop/workstation/internal-server assessment readiness.

## Current verdict

VulnoraIQ is ready for **self-hosted internal deployment** with the security, operational, deployment, Agentic Applications, and GenAI Security working-starter controls listed below. The Agentic Applications Production Readiness Plan is complete for the intended laptop/server application model. The GenAI Security Production Readiness Plan is complete at working-starter level for `DSGAI01–DSGAI21` with safe synthetic scenario manifests, deterministic evaluators, and CI validation. VulnoraIQ does not claim certified VAPT-grade assurance.

See [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) for detailed scoring, [`AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) for agentic phase gates, and [`genai/PRODUCTION_READINESS_PLAN.md`](genai/PRODUCTION_READINESS_PLAN.md) for GenAI Security phase gates.

## Closed blockers

| ID | Area | Required outcome | Evidence |
| --- | --- | --- | --- |
| PRD-001 | Logging | Structured application logging with request, job, scan, error, and audit events. | `webui/hosted_server.py`; `tests/test_webui_audit_logging.py` |
| PRD-002 | Web server | Documented self-hosted laptop/server deployment path. | `docs/DEPLOYMENT.md`; `docs/RUNBOOK.md` |
| PRD-003 | Web UI consolidation | One supported web runtime with legacy paths removed. | `webui/server.py` removed; only `webui/hosted_server.py` remains |
| PRD-004 | Authentication | Auth enabled for self-hosted production-mode deployments, env/secret token source, no shared credentials. | `webui/auth.py`; `tests/test_webui_auth_production.py` |
| PRD-005 | Web hardening | CSRF, rate limiting, security headers, request limits. | `webui/hosted_server.py`; `tests/test_webui_csrf.py`; `tests/test_webui_rate_limit.py`; `tests/test_webui_security_headers.py` |
| PRD-006 | Configuration | Environment-variable overrides for all runtime paths. | `webui/hosted_server.py` runtime env support |
| PRD-007 | Persistence | SQLite-backed job persistence with migrations. | `webui/persistent_jobs.py`; `tests/test_sqlite_job_store.py` |
| PRD-008 | Containerisation | Deployable container baseline. | `Dockerfile`; `.dockerignore`; `docker-compose.yml` |
| PRD-009 | Quality gates | Ruff, mypy, CI enforcement. | `.github/workflows/ci.yml`; `.github/workflows/python-ci.yml` |
| PRD-010 | Observability | Health, readiness, metrics endpoints. | `/healthz`, `/readyz`, `/metrics`; `tests/test_metrics.py` |
| PRD-011 | Agentic mapping governance | CI fails if active oracle/check mapping metadata is missing. | `scripts/validate_owasp_atlas_mappings.py`; `tests/test_owasp_atlas_mapping_validation.py`; CI workflows |
| PRD-012 | GenAI Security readiness governance | CI fails if GenAI scenario coverage, evidence fields, source discrepancy tracking, or docs readiness drift. | `benchmarks/fixtures/genai/scenarios.yaml`; `core/genai_evaluators.py`; `scripts/validate_genai_readiness.py`; `tests/test_genai_readiness_validation.py`; CI workflows |

## Current self-hosted readiness

All blockers PRD-001 through PRD-012 are **Closed** for the self-hosted internal deployment and assessment-readiness scope.

## Remaining maturity items

| Area | Gap | Priority |
| --- | --- | --- |
| TLS termination | Relies on reverse proxy such as nginx/Caddy for internal server deployments | Medium |
| Multi-instance operation | No shared-nothing / stateless design | Medium |
| OIDC/SSO | Proxy-header identity only; no direct OIDC | Medium |
| Database HA | SQLite is single-file; requires backup/restore discipline | Low |
| Full audit trail | Missing user-management events such as create/delete/role-change | Low |
| Independent assurance | No third-party assessment results | High |
| Rate limiting per-user | IP-based only; not per-authenticated-user | Medium |
| Secrets rotation | Documented but no automated rotation tool | Medium |
| GenAI environment validation | Current GenAI coverage is safe synthetic working-starter coverage | High |
| GenAI provider/data inventory | No native provider inventory connector or organisation-specific data catalogue integration | Medium |

### Notes on scoring

The 10/10 gate-compliance score means all PRD-001 through PRD-012 blockers are closed. The actual scorecard average for self-hosted internal deployment remains lower because it includes non-blocking maturity items such as SIEM integration, OIDC, signed releases, SAST/DAST, GenAI approved-environment validation, and independent assurance.

## Production claim rule

Describe VulnoraIQ as a self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed. Do not describe VulnoraIQ as certified VAPT-grade, independently production-validated for all GenAI categories, or a replacement for independent assessment. Self-hosted internal deployment readiness is attested by this register, the scorecard, the completed Agentic Applications readiness plan, the completed GenAI Security working-starter readiness plan, and the production-readiness validation gates.
