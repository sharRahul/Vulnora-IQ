# VulnoraIQ Documentation

This folder contains the operational, security, production-readiness, assurance, OWASP, GenAI, Agentic, and MITRE ATLAS documentation for VulnoraIQ.

> **Current version:** `0.2.0`  
> **Current posture:** controlled internal enterprise production-readiness gate passed.  
> **Boundary:** not public internet-facing SaaS, not multi-tenant ready, and not certified VAPT-grade assurance.

## Start here

| Need | Document |
| --- | --- |
| Quick start, feature overview, maturity statement | [`../README.md`](../README.md) |
| Security policy and vulnerability reporting | [`../SECURITY.md`](../SECURITY.md) |
| Deployment, env vars, TLS/reverse proxy, metrics, backups | [`DEPLOYMENT.md`](DEPLOYMENT.md) |
| Day-2 operations and troubleshooting | [`RUNBOOK.md`](RUNBOOK.md) |
| Incident handling | [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md) |
| Release gates and RC/final tagging | [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) |
| Upgrade from `0.0.1.x` to `0.2.0` | [`MIGRATION.md`](MIGRATION.md) |
| Readiness scoring | [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) |
| Hardening backlog and accepted risks | [`PRODUCTION_HARDENING_BACKLOG.md`](PRODUCTION_HARDENING_BACKLOG.md) |
| What scan findings do and do not prove | [`ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md) |
| Current implementation status | [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) |

## Production-readiness boundary

VulnoraIQ `0.2.0` may be described as:

> Controlled internal enterprise production-readiness gate passed.

It must **not** be described as:

- public SaaS ready
- multi-tenant ready
- unsupervised public internet ready
- certified VAPT-grade assurance
- a substitute for external penetration testing

## Current control summary

| Area | Status |
| --- | --- |
| Auth | Fail-closed token auth; trusted reverse-proxy identity mode available |
| Production startup validation | Runtime checks via `webui/production_checks.py` and `scripts/validate_runtime_production_config.py` |
| Web hardening | CSRF, request-size limits, rate limiting, security headers, structured errors |
| Persistence | SQLite default with WAL, foreign keys, busy timeout, schema versioning |
| Observability | `/healthz`, `/readyz`, auth-protected `/metrics`, structured JSON audit logs |
| Backup/restore | SQLite online backup and restore scripts with validation |
| Container | Non-root Dockerfile, `/data` volume, healthcheck, Docker Compose example |
| CI gates | Ruff, mypy, pytest, pip check, pip-audit, metadata validation, readiness validation, functional acceptance |

## OWASP, GenAI, Agentic, and MITRE documentation

| Area | Document |
| --- | --- |
| OWASP LLM 2025 category specs | [`owasp/`](owasp/) |
| OWASP LLM production-readiness plan | [`owasp/PRODUCTION_READINESS_PLAN.md`](owasp/PRODUCTION_READINESS_PLAN.md) |
| OWASP to MITRE ATLAS crosswalk | [`owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`](owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md) |
| GenAI security implementation plan | [`genai/`](genai/) |
| GenAI production-readiness plan | [`genai/PRODUCTION_READINESS_PLAN.md`](genai/PRODUCTION_READINESS_PLAN.md) |
| Agentic Applications implementation plan | [`agentic/`](agentic/) |
| Agentic Applications production-readiness plan | [`agentic/PRODUCTION_READINESS_PLAN.md`](agentic/PRODUCTION_READINESS_PLAN.md) |
| MITRE ATLAS AI planning matrix | [`MITRE_ATLAS_AI_MATRIX.md`](MITRE_ATLAS_AI_MATRIX.md) |
| MITRE ATLAS mapping notes | [`mitre-atlas-mapping.md`](mitre-atlas-mapping.md) |

The OWASP, GenAI, Agentic, and MITRE documents are planning and implementation references. They should not be interpreted as proof that every mapped technique has production-validated active detection coverage.

## Source document review queue

The following PDFs are stored locally for source review and category confirmation:

- `owasp-documents/OWASP-GenAI-COMPASS-RunBook-1.0.pdf`
- `owasp-documents/OWASP-GenAI-Data-Security-Risks-and-Mitigations-2026-v1.0.pdf`
- `owasp-documents/OWASP-Top-10-for-Agentic-Applications-2026-12.6.pdf`
- `owasp-documents/OWASP-Top10-for-Agentic-Applications_AIUC-1-Crosswalk-May26.pdf`
- `owasp-documents/State-of-Agentic-AI-Security-and-Governance-v2.01.pdf`

Until the PDF text is extracted and reviewed, GenAI and Agentic category IDs/names in the new planning docs must remain `Planning` or `candidate` mappings.

## Documentation maintenance rule

When production posture or assessment coverage changes, update these together:

1. `README.md`
2. `SECURITY.md`
3. `docs/README.md`
4. `docs/DEPLOYMENT.md`
5. `docs/IMPLEMENTATION_STATUS.md`
6. `docs/PRODUCTION_READINESS_SCORECARD.md`
7. `docs/PRODUCTION_HARDENING_BACKLOG.md`
8. `docs/ASSESSMENT_ASSURANCE.md`
9. `docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`
10. `docs/genai/`
11. `docs/agentic/`
12. `CHANGELOG.md`

If a capability is starter-level, partial, experimental, accepted risk, source-review pending, or roadmap-only, mark it clearly in every document that mentions it.