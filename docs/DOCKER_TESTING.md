# Docker-first VulnoraIQ lab

VulnoraIQ's current safe path for real AI-agent, RAG, webhook, Ollama-style, and tool-loop testing is the Docker Compose lab.

The host should run Docker commands or use the platform launcher, open the WebUI at <http://localhost:8787>, and inspect exported reports. Scans, target validation, evidence capture, report generation, and smoke testing run inside containers.

## Start the lab with the platform launcher

For normal laptop/workstation use, the launcher files are the point of start:

| Platform | Launcher |
| --- | --- |
| Windows | `launch-vulnoraiq-webui.bat` |
| macOS | `launch-vulnoraiq-webui.command` |
| Linux | `launch-vulnoraiq-webui.sh` |

The only prerequisite for this path is Docker Desktop or a compatible Docker Engine with Docker Compose v2.

Each launcher performs these steps:

1. checks Docker is installed and running;
2. runs `docker compose build`;
3. runs `docker compose up -d`;
4. shows `docker compose ps`;
5. waits for `vulnoraiq-web` to become healthy;
6. opens <http://127.0.0.1:8787> in the default browser.

## Manual Docker startup

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open <http://localhost:8787>.

The WebUI is published as `127.0.0.1:8787:8787`. Keep this loopback binding for normal laptop/workstation use. Do not change it to `8787:8787` unless you are intentionally moving to a shared/internal-server deployment with production auth, reverse proxy, TLS, and documented network controls.

## Services

| Service | Purpose |
| --- | --- |
| `vulnoraiq-web` | Non-root hosted WebUI and CLI container. Stores `/data/jobs.db`, `/data/reports`, `/data/evidence`, `/data/audit`, and Agent Lab imports under `/data/agent_lab`. |
| `test-runner` | Optional Docker-only utility service under the `test` profile. |

All services run on the private `vulnoraiq-lab` bridge network. The Compose file does not use host networking or privileged mode. Experimental Agent Lab intentionally uses local Docker engine access from the WebUI container so it can build and run imported agent projects.

## Current Docker target configuration

The Docker service sets:

```text
VULNORAIQ_CONFIG_DIR=/app/config
VULNORAIQ_TARGET_CONFIG=targets.docker.yaml
VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
VULNORAIQ_EVIDENCE_DIR=/data/evidence
VULNORAIQ_AUDIT_DIR=/data/audit
VULNORAIQ_AGENT_LAB_ROOT=/data/agent_lab
VULNORAIQ_AGENT_LAB_PROJECTS_ROOT=/data/agent_lab/projects
```

Docker lab targets are defined in `config/targets.docker.yaml`. You must configure your own targets with real endpoints, or use Agent Lab to auto-create runtime targets for imported real agent projects.

## Experimental Agent Lab

Open:

```text
http://localhost:8787/agent-lab
```

Agent Lab supports importing a real project, configuring model-provider environment, choosing CPU or GPU runtime options, building/running the agent, creating a runtime target, and launching an authorised scan.

For local LLM providers running on the host, Docker Compose configures `host.docker.internal` through the host gateway.

GPU mode requires host Docker support for GPU containers. Agent Lab only passes runtime options; it does not install host drivers.

## CLI from Docker

```bash
docker compose exec vulnoraiq-web vulnoraiq targets list
docker compose exec vulnoraiq-web vulnoraiq targets validate --target <target_name>
docker compose exec vulnoraiq-web vulnoraiq scan --target <target_name> --profile ai_agent_foundation --authorised
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
docker compose exec vulnoraiq-web vulnoraiq jobs show --job-id <job-id>
```

## WebUI workflow

1. Start Docker Compose through the platform launcher or manual Docker commands.
2. Open <http://localhost:8787>.
3. Use the target workspace to search/filter targets, or open `/agent-lab` to import and run a real agent.
4. Validate target connectivity.
5. Confirm the authorisation checklist.
6. Select a profile such as `ai_agent_foundation`, `baseline`, `rag`, `agent`, `full`, or a single focused profile.
7. Start the scan.
8. Review live progress, findings, policy status, recent jobs, and report outputs.
9. Update finding status/remediation actions when needed.

## Smoke and acceptance checks

```bash
python scripts/docker_smoke_test.py
python scripts/validate_target_configs.py
python scripts/validate_production_testing_readiness.py --output-dir reports/output/production-readiness
python scripts/validate_production_testing_readiness.py --run-functional --output-dir reports/output/production-readiness
```

For browser testing on a host with Playwright installed:

```bash
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

## Stop the lab

```bash
docker compose down
```

Use a volume reset only when you intentionally want to remove jobs, reports, evidence, Agent Lab imports, and audit data:

```bash
docker compose down -v
```

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Launcher says Docker was not found | Install Docker Desktop or make sure the Docker CLI is on PATH. |
| Launcher says Docker is not running | Start Docker Desktop and wait until it is ready. |
| WebUI does not open | `docker compose ps`, then `docker compose logs vulnoraiq-web` |
| WebUI is not reachable from another device | Expected for the local lab; it is bound to `127.0.0.1` on the host |
| Target validation fails | Check the target endpoint is reachable from inside the container |
| No reports appear | Check `/data/reports` in the container and `VULNORAIQ_WEB_OUTPUT_ROOT` |
| Jobs are missing | Check `/data/jobs.db` and whether the Docker volume was reset |
| Browser tests fail locally | Confirm Playwright Chromium is installed and the environment can download browser binaries |

## Assurance boundary

Passing Docker smoke tests proves the lab wiring, target adapters, scanner path, and report/evidence generation work. It does not prove real-world target assurance or certified VAPT-grade coverage. Agent Lab scans are evidence from the imported agent runtime and still require human review.
