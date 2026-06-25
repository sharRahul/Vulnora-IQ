# VulnoraIQ

**VulnoraIQ** is a self-hosted AI security testing application for authorised assessment of LLM applications, RAG systems, AI agents, and orchestration layers.

VulnoraIQ is a **self-hosted internal application** for controlled **laptop/server** AI security testing, including controlled **internal server** deployment when production auth, reverse proxy, TLS, audit retention, and backup controls are configured. It provides a browser WebUI, CLI, Agent Lab, target configuration, scan execution, evidence capture, reports, audit logs, and CI validation workflows. Findings are **assessment evidence for human review**; VulnoraIQ does not claim certified VAPT-grade assurance. See [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md).

## Product direction

VulnoraIQ now has two explicit run modes.

| Mode | Best for | Where VulnoraIQ runs | Where imported AI agents run | Report location |
| --- | --- | --- | --- | --- |
| **Desktop Mode** | Normal desktop/laptop users | Host machine | Docker containers | `./scan-reports/` |
| **Advanced Docker Lab Mode** | Servers, VMs, CI, dev/test labs | Docker Compose container | Docker containers | Docker `/data` volume or mapped folders |

The intended product experience is:

```text
User clicks launcher
  -> VulnoraIQ WebUI opens
  -> User imports/selects an AI agent in Agent Lab
  -> VulnoraIQ stores the project under agent-lab/
  -> User configures API key, local LLM, remote LLM, CPU/GPU runtime
  -> Docker runs only the sandboxed imported agent/runtime
  -> VulnoraIQ auto-creates a target
  -> User runs authorised scans from the WebUI
  -> Results are visible on the dashboard and saved under scan-reports/
```

## Current status

| Area | Status |
| --- | --- |
| Version | `0.2.0` beta |
| WebUI | React browser console served by `webui.assistant_server` / `vulnoraiq-web`. |
| Desktop Mode | Phase 1 source/package foundation. Primary launchers start VulnoraIQ on the host and create local `scan-reports/` and `agent-lab/` folders. |
| Advanced Docker Lab Mode | Full Docker Compose lab remains available through explicit Docker Lab launchers and manual Compose commands. |
| Agent Lab | Experimental workflow at `/agent-lab` for importing real AI-agent projects, configuring provider/runtime settings, building/running agents in Docker, auto-creating targets, and launching scans. |
| Persistence | SQLite job store, reports, evidence, audit logs, and Agent Lab metadata. |
| Identity | Local/single-user auth model for current scope; direct OIDC/JWT is future work. |

## Prerequisites

| Run path | Requirements |
| --- | --- |
| Desktop Mode from source/package | Docker Engine or Docker Desktop with Docker Compose v2, Python 3.10 or newer, internet access for first dependency/image builds, and a modern browser. |
| Advanced Docker Lab / Docker GUI lab | Docker Engine or Docker Desktop with Docker Compose v2, internet access for first image/dependency builds, and a modern browser. |
| Agent Lab GPU mode | Host GPU container support. Agent Lab passes Docker GPU runtime flags; it does not install host GPU drivers. |
| Local Ollama / LM Studio | Provider running on the host. Agent containers reach host providers through `host.docker.internal` where supported/configured. |
| Development tests | Python 3.10 or newer, Node.js 20 or newer, npm, Playwright browser dependencies, and a modern browser. |

**Packaging note:** Desktop Mode currently requires Python when running from a source checkout or source-style release package. The next packaging phase should bundle/freeze the runtime so normal users only need Docker Desktop plus the downloaded VulnoraIQ package.

## Quick start: Desktop Mode

Use this for normal laptop/workstation use.

| Platform | Launcher |
| --- | --- |
| Windows | `launch-vulnoraiq-webui.bat` |
| macOS | `launch-vulnoraiq-webui.command` |
| Linux | `launch-vulnoraiq-webui.sh` |

Desktop Mode performs the following steps:

1. starts VulnoraIQ natively on the host;
2. checks Docker is available for sandboxed Agent Lab runtimes;
3. creates local output folders;
4. starts the WebUI on `127.0.0.1:8787`;
5. opens the browser.

Desktop Mode folder contract:

```text
scan-reports/
  jobs.db
  reports/
  evidence/
  audit/
  exports/

agent-lab/
  projects/
  deployments.yaml
```

After startup, open:

```text
http://127.0.0.1:8787
```

Agent Lab is available at:

```text
http://127.0.0.1:8787/agent-lab
```

## Quick start: Advanced Docker Lab Mode

Use this for servers, VMs, CI, or fully containerised development/testing.

| Platform | Launcher |
| --- | --- |
| Windows | `launch-vulnoraiq-docker-lab.bat` |
| macOS | `launch-vulnoraiq-docker-lab.command` |
| Linux | `launch-vulnoraiq-docker-lab.sh` |

Manual equivalent:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open:

```text
http://127.0.0.1:8787
```

The Docker Lab WebUI is published on host loopback only:

```text
127.0.0.1:8787:8787
```

Useful Docker Lab commands:

```bash
docker compose exec vulnoraiq-web vulnoraiq targets list
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
docker compose logs vulnoraiq-web
```

Stop Docker Lab Mode:

```bash
docker compose down
```

Only use this when you intentionally want to delete local Docker volumes, jobs, reports, evidence, audit logs, and Agent Lab imports:

```bash
docker compose down -v
```

## Agent Lab workflow

Agent Lab is the WebUI flow for testing real AI agents.

```text
Import Agent
  -> Configure LLM/API keys
  -> Select CPU/GPU runtime
  -> Build/Run sandboxed Docker container
  -> Auto-create VulnoraIQ target
  -> Run authorised scan
  -> Review dashboard, evidence, and reports
```

Supported provider patterns include:

- Ollama local/OpenAI-compatible
- LM Studio local/OpenAI-compatible
- OpenRouter
- custom OpenAI-compatible endpoints
- custom environment variables

In **Desktop Mode**, VulnoraIQ scans the sandboxed agent through a published localhost endpoint such as:

```text
http://127.0.0.1:<port>
```

In **Advanced Docker Lab Mode**, VulnoraIQ scans the sandboxed agent through Docker container DNS such as:

```text
http://vulnoraiq-agent-lab-<project>:8000
```

Agent Lab remains experimental because it builds and runs operator-provided code. Import and test only code and systems you own or are explicitly authorised to assess.

## Source/package local development

Install from a source checkout:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .[dev]
```

Run Desktop Mode backend directly:

```bash
python scripts/desktop_launch.py
```

Run Docker Lab backend directly:

```bash
python scripts/bootstrap_launch.py
```

Run only the WebUI server:

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
```

## Security boundary

VulnoraIQ is intended for authorised local or controlled internal use.

- Keep local launchers bound to `127.0.0.1`.
- Do not expose the WebUI on a shared network without production auth, TLS, reverse proxy controls, audit retention, and backups.
- Store API keys outside the repository and pass them through approved environment/secret handling.
- Treat reports and findings as evidence requiring human review.
- Review imported Agent Lab source before running it.

Production/internal-server mode requires explicit hardening. For a shared internal server, configure production auth, a trusted reverse proxy, TLS, audit retention, and backups before exposing the service.

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
python scripts/validate_runtime_production_config.py
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Use trusted reverse-proxy identity only when the proxy authenticates users and strips spoofed identity headers. Direct OIDC/JWT remains future work and is not required for current local single-user use.

## Validation

Core validation commands:

```bash
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py --output-dir reports/output/production-readiness
python scripts/validate_runtime_production_config.py
```

WebUI browser flow:

```bash
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

## Documentation

| Need | Document |
| --- | --- |
| User guide | [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) |
| Desktop vs Docker Lab run modes | [`docs/RUN_MODES_DESKTOP_AND_DOCKER_LAB.md`](docs/RUN_MODES_DESKTOP_AND_DOCKER_LAB.md) |
| Agent Lab | [`docs/AGENT_LAB.md`](docs/AGENT_LAB.md), [`docs/AGENT_LAB_PLAN.md`](docs/AGENT_LAB_PLAN.md) |
| Docker Lab | [`docs/DOCKER_TESTING.md`](docs/DOCKER_TESTING.md) |
| WebUI | [`docs/WEBUI_GUIDE.md`](docs/WEBUI_GUIDE.md), [`docs/WEB_UI_TEST_CATALOG.md`](docs/WEB_UI_TEST_CATALOG.md) |
| CLI | [`docs/CLI_GUIDE.md`](docs/CLI_GUIDE.md) |
| Safety and targets | [`docs/SAFETY_MODEL.md`](docs/SAFETY_MODEL.md), [`docs/TARGET_CONFIGURATION.md`](docs/TARGET_CONFIGURATION.md) |
| Deployment and operations | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md), [`docs/RUNBOOK.md`](docs/RUNBOOK.md), [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md) |
| Release and supply chain | [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md), [`docs/RELEASE_ARTIFACTS.md`](docs/RELEASE_ARTIFACTS.md), [`docs/SUPPLY_CHAIN_PIPELINE.md`](docs/SUPPLY_CHAIN_PIPELINE.md), [`docs/PYPI_PACKAGE.md`](docs/PYPI_PACKAGE.md) |
| Assurance limits | [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md), [`docs/PRODUCTION_READINESS_SCORECARD.md`](docs/PRODUCTION_READINESS_SCORECARD.md), [`docs/PRODUCTION_HARDENING_BACKLOG.md`](docs/PRODUCTION_HARDENING_BACKLOG.md) |
| Future identity | [`docs/future-plans/OIDC_JWT_AUTH_PLAN.md`](docs/future-plans/OIDC_JWT_AUTH_PLAN.md) |

## License and notices

VulnoraIQ-specific source code and documentation are licensed under Apache-2.0. See [`LICENSE`](LICENSE).

Some documentation and planning data is derived from MITRE ATLAS. MITRE ATLAS data is copyright 2021-2026 MITRE and licensed under the Apache License, Version 2.0. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
