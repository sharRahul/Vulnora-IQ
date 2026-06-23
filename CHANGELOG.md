# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Quick-start guidance for stopping the Web UI in foreground, background, Docker, and Docker Compose runs.

### Changed

- Documentation now consistently describes VulnoraIQ as a self-hosted laptop/workstation/internal-server application for authorised AI assessment work.
- Current-scope readiness items are now consistently marked **Complete** for the self-hosted/internal assessment scope.
- README, docs index, deployment guide, security policy, implementation status, readiness scorecard, backlog, release checklist, assurance, runbook, incident response, GenAI readiness plan, and Agentic Applications readiness plan were aligned to the same product positioning and completion vocabulary.

### Notes

- VulnoraIQ findings remain framework evidence requiring human review.
- This release does not claim certified VAPT-grade assurance or independently validated real-environment GenAI detection coverage.

## [0.2.0] - 2026-06-22

### Added

- Production startup validation.
- Trusted reverse-proxy identity auth mode.
- Structured audit logging with request correlation IDs.
- Prometheus-format metrics endpoint protected by default.
- SQLite backup and restore scripts.
- Docker Compose production-like environment.
- Scan concurrency limits.
- Container smoke test script.
- Production readiness scorecard, runbook, incident response, release checklist, migration guide, and assessment assurance docs.
- Dependency checks in CI.
- OWASP-to-MITRE ATLAS planning crosswalk and mapping metadata validator.
- GenAI security implementation planning docs.
- Agentic Applications security implementation planning docs.
- OWASP source document review index.
- Source-confirmed GenAI Data Security category extraction for `DSGAI01–DSGAI21`.
- Source-confirmed OWASP Top 10 for Agentic Applications category extraction for `ASI01–ASI10`.

### Changed

- Version bumped to 0.2.0.
- Auth, CSRF, rate limiting, security headers, proxy IP resolution, SQLite persistence, HTTP errors, configuration output, metrics, and deployment docs were hardened for the self-hosted application model.
- Production readiness docs were updated for self-hosted internal scope.
- README, SECURITY.md, and docs index were rewritten for the `0.2.0` self-hosted production posture.
- `docs/genai/` and `docs/agentic/` were updated from placeholder planning IDs to source-confirmed ranges.
- Active LLM oracle/check configs now include OWASP-to-ATLAS mapping metadata.

### Fixed

- CSRF expiry test stability.
- Ruff import ordering across test files.
- README, implementation status, and hardening backlog maturity claims.
- HTTP error response consistency.
- Scanner exception handling.
- Production listen-address validation reachability.
- `.env.production.example` ignore-rule exception.

### Breaking

- Legacy `webui/server.py` removed.
- JSON job store backend is legacy/dev only; SQLite is default.
- File-based auth is disabled in production mode.
- `VULNORAIQ_ADMIN_TOKEN` is required in production.
- Minimum Python 3.10 required.
- `VULNORAIQ_AUTH_MODE=token` is default; set to `trusted_proxy` for proxy-based identity.

## [0.1.0] - 2026-05-13

### Added

- Initial repository scaffold.
- OWASP LLM Top 10 2025-aligned module structure.
- Core scanner, runner, orchestrator, risk scoring, and results engine.
- RAG, agent, payload, reporting, dashboard, and CI scaffolding.
- Safe demo target and unit tests.
- Policy-as-code and MITRE ATLAS mapping documentation.
