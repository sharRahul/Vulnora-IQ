# Docker-first VulnoraIQ lab

VulnoraIQ now defaults to a Docker Compose lab for real AI-agent testing. The host runs Docker commands, opens `http://localhost:8787`, and optionally reads exported reports. Scans, mock agents, validation, evidence capture, report generation, and automated tests run inside containers.

## Start

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open <http://localhost:8787>.

## Services

- `vulnoraiq-web`: non-root WebUI and CLI container, stores `/data/jobs.db`, `/data/reports`, `/data/evidence`, and `/data/audit`.
- `local-mock-agent`: deterministic mock AI-agent with chat-completions, Ollama-generate, RAG, webhook, and dry-run tool-loop endpoints.
- `test-runner`: Docker-only test utility service.

All services are on the private `vulnoraiq-lab` bridge network. No service uses privileged mode, host networking, or the host Docker socket.

## CLI from Docker

```bash
docker compose exec vulnoraiq-web vulnoraiq targets list
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
```

## Docker automated checks

```bash
docker compose run --rm test-runner pytest -q
docker compose run --rm test-runner ruff check .
docker compose run --rm test-runner mypy .
docker compose run --rm test-runner python scripts/validate_target_configs.py
docker compose run --rm test-runner python scripts/docker_smoke_test.py
```

Do not run real scans directly on the host. If a standalone Python command exists in older docs, treat it as optional development-only behaviour; the safe path is Docker Compose.
