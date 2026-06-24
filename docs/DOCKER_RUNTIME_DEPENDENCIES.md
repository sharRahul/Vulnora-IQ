# Docker runtime dependencies

Docker is now the recommended path for VulnoraIQ's current local lab workflow. The Docker Compose lab starts the hosted WebUI, deterministic mock AI target, SQLite job store, reports, evidence, and audit paths in a controlled environment.

Docker is still optional for simple host-native demo use with the `demo` target and local launcher, but real local AI-agent/RAG/tool-loop lab testing should use Docker Compose.

## Check Docker availability

Use the runtime check script:

```bash
python scripts/check_docker_runtime.py
python scripts/check_docker_runtime.py --json
```

The script uses the same Docker discovery logic as the WebUI agent runtime manager, including the `VULNORAIQ_DOCKER_CLI` override.

## Recommended Docker lab startup

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open <http://localhost:8787>.

## Installation boundary

VulnoraIQ should not silently install Docker as part of normal dependency setup. Docker installation can require administrator rights, service changes, virtualization changes, and operating-system package changes.

The WebUI and launcher should therefore:

- detect whether Docker is available;
- show clear remediation guidance when it is missing;
- allow the user to set `VULNORAIQ_DOCKER_CLI` when Docker is installed outside `PATH`;
- keep host-native demo use available where Docker is unavailable;
- keep Docker-dependent checks clearly separated from host-native checks.

## CI behavior

Normal Python CI validates the package, scanner, WebUI server, mappings, GenAI readiness, and functional paths. Docker-dependent checks should remain explicit and report a clear skip/failure reason when Docker is unavailable.

## Current boundary

- Docker Compose is recommended for current local lab operation.
- Host-native launcher mode is for local demo/development use.
- Docker should be installed and maintained by the user or organisation, not silently modified by VulnoraIQ.
