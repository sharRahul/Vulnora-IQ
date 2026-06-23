# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-06-22

### Added

- Production startup validation (`webui/production_checks.py`, `scripts/validate_runtime_production_config.py`)
- Trusted reverse-proxy identity auth mode (`VULNORAIQ_AUTH_MODE=trusted_proxy`)
- Structured JSON-line audit logging with request correlation IDs
- Prometheus `/metrics` endpoint (auth-protected by default)
- SQLite backup and restore scripts (`scripts/backup_sqlite_store.py`, `scripts/restore_sqlite_store.py`)
- Docker Compose production-like environment (`docker-compose.yml`, `.env.production.example`)
- Scan concurrency limits (`VULNORAIQ_MAX_CONCURRENT_SCANS`, `VULNORAIQ_SCAN_QUEUE_LIMIT`)
- Container smoke test script
- Production readiness scorecard, runbook, incident response, release checklist, migration guide, assessment assurance docs
- Dependency checks (pip-audit, pip check) in CI
- Regression tests for trusted proxy identity mode (spoofed headers, CIDR enforcement, role mapping, permissions)
- Validator checks: listen_address_safe reachability, no SaaS overclaim in README, SQLite/WAL persistence claim, public/SaaS limitations documented, assessment assurance doc discoverable
- OWASP-to-MITRE ATLAS planning crosswalk (`docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`)
- OWASP-to-MITRE ATLAS metadata validator (`scripts/validate_owasp_atlas_mappings.py`)
- CLI entry `vulnoraiq-validate-owasp-atlas-mappings`
- Regression tests that fail CI if active OWASP oracles/checks lack OWASP family, OWASP ID, MITRE ATLAS tactics, mapping status, evidence surface, or manual-review flag
- GenAI security implementation planning docs (`docs/genai/`)
- Agentic Applications security implementation planning docs (`docs/agentic/`)
- OWASP source document review index (`docs/owasp-documents/README.md`)
- Source-confirmed GenAI Data Security category extraction for `DSGAI01–DSGAI21`
- Source-confirmed OWASP Top 10 for Agentic Applications category extraction for `ASI01–ASI10`
- Updated OWASP/GenAI/Agentic-to-MITRE ATLAS crosswalk mappings for LLM, DSGAI, and ASI categories

### Changed

- Version bumped to 0.2.0
- Auth: env-driven token auth with hmac constant-time comparison, production-mode validation, trusted proxy identity support
- CSRF: per-session tokens with TTL/cleanup
- Rate limiting: configurable window/max, periodic store cleanup
- Security headers: CSP, HSTS (conditional), X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy on every response
- Proxy IP resolution with trusted CIDR support
- SQLite job store as default (WAL mode, schema versioning)
- HTTP error handling standardized with correct status codes and security headers
- Config endpoint is role-aware (admin sees full config, viewers see safe subset)
- Artifact download hardened against path traversal
- Metrics counters for auth, CSRF, rate limit, scan, artifact events
- Deployment guide with production checklist, runbook, incident response docs
- **listen_address_safe** added to `_ALL_CHECKS` (was unreachable); 4 new `validate_all` tests for 127.0.0.1/0.0.0.0+proxy/0.0.0.0+no-proxy/invalid-CIDR scenarios
- Production readiness scorecard updated: rating scale scoped to controlled internal; stale "no trusted_proxy test coverage" claim removed
- PRODUCTION_HARDENING_BACKLOG.md: added "Notes on scoring" clarifying 10/10 gate vs 8.4/10 scorecard average; remaining gaps section updated
- RUNBOOK.md: added disclaimer that it is a template requiring adaptation
- RELEASE_CHECKLIST.md: version/date updated
- README.md and SECURITY.md fully rewritten for the `0.2.0` controlled-internal production posture
- `docs/README.md` updated to link OWASP, GenAI, Agentic, MITRE planning docs, and source-review status
- `docs/owasp-documents/README.md` updated from pending source-review queue to category extraction status
- `docs/genai/` updated from placeholder planning IDs to source-confirmed `DSGAI01–DSGAI21`
- `docs/agentic/` updated from placeholder planning IDs to source-confirmed `ASI01–ASI10`
- `config/owasp_oracles.yaml` and `config/production_owasp_detection.yaml` now include OWASP-to-ATLAS mapping metadata for every active LLM oracle/check
- `scripts/validate_package_metadata.py` now fails when the OWASP-to-ATLAS mapping validator fails
- **`_ALL_CHECKS` in `production_checks.py`**: `listen_address_safe` entry added so the check is actually reachable

### Fixed

- CSRF test expiry now uses direct store manipulation instead of unreliable monkeypatch
- Ruff import ordering across test files
- README, IMPLEMENTATION_STATUS, PRODUCTION_HARDENING_BACKLOG maturity claims updated
- HTTP error responses now include security headers and request IDs
- Scanner exceptions no longer leak internals
- `listen_address_safe` was defined but never added to `_ALL_CHECKS` — now reachable via `validate_all()`
- `.env.production.example` excluded by `.gitignore` `.env.*` pattern — added negation rule

### Security

- Production mode fails closed on unsafe config
- Demo tokens rejected in production
- Internal admin token disabled in production
- Known demo credentials blocked in production
- Oversized requests return 413, not 400
- Malformed JSON returns 400
- Path traversal blocked on artifact download
- SQLite path validated against ephemeral locations
- Rate limit, request body, CSRF TTL validated as sane/positive
- Audit logs never include tokens, CSRF tokens, request bodies, or secrets
- **listen_address_safe**: listening on 0.0.0.0/:: without proxy trust fails production checks

### Breaking

- Legacy `webui/server.py` removed (use `webui/hosted_server.py` only)
- JSON job store backend is legacy/dev only; SQLite is default
- File-based auth is disabled in production mode
- `VULNORAIQ_ADMIN_TOKEN` is required in production (min 20 characters)
- Minimum Python 3.10 required
- `VULNORAIQ_AUTH_MODE=token` is default; set to `trusted_proxy` for proxy-based identity

## [0.1.0] - 2026-05-13

### Added

- Initial enterprise-ready repository scaffold.
- OWASP LLM Top 10 2025-aligned module structure.
- Core scanner, runner, orchestrator, risk scoring, and results engine.
- RAG, agent, payload, reporting, dashboard, and CI scaffolding.
- Safe demo target and unit tests.
- Policy-as-code and MITRE ATLAS mapping documentation.