# Implementation status

This document separates current implemented capability from future assurance and maturity work.

> **Current maturity:** VulnoraIQ `0.2.0` is a Docker-first, self-hosted AI security testing lab with controlled internal production-readiness gates. It supports authorised local/internal testing of LLM, RAG, tool-using, agentic, and GenAI data-security scenarios through a Python scanner, target adapters, a hosted React WebUI, WebUI assistant backend/model controls, expanded target templates, CLI, SQLite job persistence, reports, evidence, on-demand signed release packages, and CI validation. This is complete for self-hosted laptop/server use within the current authorised local/internal scope.

> **Assurance limitation:** OWASP, GenAI, Agentic, and MITRE mappings are framework evidence and planning/validation controls. They are not independently validated VAPT-grade assurance. See [`ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md) for the full assurance boundary.

## Mainline status as of 2026-06-24

| Area | Status | Evidence |
| --- | --- | --- |
| Version/package | Complete for `0.2.0` beta | `pyproject.toml`, package entry points, metadata validation. |
| Docker-first safe lab | Complete for current scope | `docker-compose.yml`, `Dockerfile`, `config/targets.docker.yaml`, `docker/mock-agent/`, `scripts/docker_smoke_test.py`. |
| Real authorised target testing | Complete for current local/internal scope | Target adapters, target validation, scanner wiring, runtime target APIs, mock-agent targets. |
| React WebUI | Complete as supported WebUI | `webui/console/` source and `webui/static/console/` built assets. Legacy static console has been removed. |
| WebUI target workspace | Complete for current backend APIs | Search/filtering, readiness metrics, health/status pills, safety checklist, target save/delete, validation, scan launch, recent jobs. |
| CLI | Complete for current scope | `targets list`, `targets validate`, `scan`, `reports list`, `jobs list`, `jobs show`. |
| Auth/security hardening | Complete for self-hosted internal scope | Token auth, trusted proxy mode, CSRF, rate limiting, request limits, security headers, audit logs, metrics, artifact path protection. |
| Persistence | Complete for current scope | SQLite job store with WAL, schema versioning, foreign keys, busy timeout. |
| OWASP LLM | Complete for current safe local/internal scope | OWASP docs, oracles, fixtures, profile/module coverage, mapping validation. |
| OWASP AI Testing Guide | Foundation integration complete; full 32-test roadmap planned | `ai_testing_guide_foundation`, safe payloads, integration docs, implementation roadmap. |
| GenAI Security | Complete for current controlled scenario-harness scope | `DSGAI01–DSGAI21`, 84 scenario cases, deterministic evaluators, validator, tests, docs. |
| Agentic Applications | Complete for repo-level self-hosted readiness gates | Agentic readiness plan, mapping validation, CI gates. |
| MITRE ATLAS | Complete for planning/mapping governance scope | Matrix docs, crosswalk, mapping validator, third-party notices. |
| Release packaging | Complete for self-hosted package scope | Manual release workflow, double-click launchers, bootstrap `.venv`, checksums, GitHub artifact attestations, optional GPG signatures. |
| CI | Complete gate set, subject to external Playwright browser availability in local environments | Python matrix, Ruff, mypy, pytest, pip check/audit, validation scripts, hosted WebUI flow, demo scan, functional acceptance. |

## Recent codebase changes reflected here

| PR | Status reflected in docs |
| --- | --- |
| #45 | Legacy static WebUI removed; React console is the supported WebUI. |
| #46 | Real authorised target testing added: adapters, scanner wiring, runtime target APIs, target validation, mock agent, and docs. |
| #47 | Docker-first lab added with mock agent, Docker target config, safety profiles, smoke tests, and Docker-first docs. |
| #49 | React target-management workspace enhanced with backend scan/target API wiring, readiness metrics, safety checklist, and recent job display. |

## Current complete capability

| Capability | Current implementation |
| --- | --- |
| Safe local demo | `demo` target remains an in-memory safe target requiring no external keys. |
| Docker mock-agent lab | Deterministic local target with chat-completions, Ollama-generate, RAG, webhook, and dry-run tool-loop contracts. |
| Configured target adapters | HTTP JSON, chat-completions, Ollama-generate, webhook JSON, RAG query, and agent tool-loop shapes. |
| Authorisation gate | CLI `--authorised` and WebUI checklist for non-demo scans. |
| Scanner/reporting | Markdown, JSON, SARIF, Markdown dashboard, HTML dashboard, branded export and evidence output. |
| Policy and scoring | Findings, scores, policy status, exceptions, and approval evidence validation. |
| WebUI server | Hardened Python hosted server with security headers, CSRF, rate limiting, structured errors, metrics, audit logs, and assistant chat API wrapper. |
| WebUI console | React TypeScript SecOps console with target management, dashboards, findings/intelligence panels, live assistant chat, and typed UI data models. |
| Target template library | Common LLM APIs, RAG endpoints, local model servers, agent frameworks, and provider gateway templates with dry-run defaults and validator coverage. |
| Persistence | SQLite default with operational backup/restore tooling. |
| Release packages | Windows `.zip`, Linux `.tar.gz`, and macOS `.dmg` packages with double-click bootstrap launchers, checksums, artifact attestations, and optional GPG signatures. |
| Release validation | Package metadata, OWASP/ATLAS mapping, GenAI readiness, production readiness, runtime config, and functional acceptance scripts. |

## Known incomplete or future maturity items

| Area | Status |
| --- | --- |
| WebUI live progress | SSE `/api/scans/{id}/events` backend is implemented with persisted events and React live progress consumption. |
| WebUI finding mutations | Persisted finding remediation/status APIs, audit history, and React actions are implemented. |
| WebUI assistant chat | Backend assistant API and React model controls are implemented for the self-hosted WebUI path. |
| Full OWASP AI Testing Guide | Full 32-test AITG manifest, validator, and `owasp-aitg-full` profile are implemented for safe synthetic coverage. |
| Real-world GenAI assurance | Current harness uses safe synthetic scenarios and controlled validation; approved-environment validation support is implemented with explicit authorisation, allow-list, dry-run defaults, expanded target templates, redaction, and local fake-target CI coverage. |
| Enterprise identity | Trusted proxy identity exists; direct OIDC/JWT remains future work. |
| Native installer certificates | On-demand release packages are signed/attested; Authenticode Windows installers, notarised macOS app/pkg installers, and distro-native Linux packages remain future work. |
| Independent assurance | Independent assurance workflow, checklist, and evidence bundle generation are implemented; external independent review remains required before stronger assurance claims. |

## Safe usage summary

```bash
docker compose build
docker compose up -d
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
```

For host-native demo/development:

```bash
python launch-vulnoraiq-webui.py
vulnoraiq --target demo --profile baseline
```

## Documentation rule

Keep `README.md`, `docs/README.md`, this file, WebUI/CLI/Docker docs, safety/target docs, scorecard, backlog, assurance doc, `SECURITY.md`, and `CHANGELOG.md` aligned whenever code changes affect deployment posture, target support, WebUI behaviour, CI gates, or release claims.
