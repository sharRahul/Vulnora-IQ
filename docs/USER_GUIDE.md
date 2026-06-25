# VulnoraIQ User Guide

This guide explains how to use VulnoraIQ as a local or internal AI security testing application. It assumes you are testing only systems you own or are explicitly authorised to assess.

## 1. Choose how to run VulnoraIQ

Use one of these supported paths:

| Path | Best for | Start command |
| --- | --- | --- |
| Double-click launcher | Recommended simple local use | `.bat`, `.command`, or `.sh` launcher |
| Docker GUI lab | Manual Docker use | `docker compose build` then `docker compose up -d` |
| Python package/source checkout | CLI and local WebUI development | `vulnoraiq-web --host 127.0.0.1 --port 8787` |
| Internal server | Shared controlled environment | production config validation plus reverse proxy/TLS/auth |

For a clean first run, the dashboard is intentionally empty. VulnoraIQ does not show sample findings, mock assets, or dummy dashboard data.

## 2. Start the local browser GUI

The simplest local path is to use the platform launcher:

| Platform | Launcher |
| --- | --- |
| Windows | `launch-vulnoraiq-webui.bat` |
| macOS | `launch-vulnoraiq-webui.command` |
| Linux | `launch-vulnoraiq-webui.sh` |

The only prerequisite for this path is Docker Desktop or a compatible Docker Engine with Docker Compose v2. The launchers do not require host Python.

Each launcher performs the startup steps in order:

1. checks Docker is installed and the Docker engine is running;
2. runs `docker compose build`;
3. runs `docker compose up -d`;
4. shows `docker compose ps`;
5. waits for `vulnoraiq-web` to become healthy;
6. opens the WebUI in the default browser.

Manual Docker flow:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open the GUI in your browser:

```text
http://localhost:8787
```

The default Docker lab binds the WebUI to loopback only: `127.0.0.1:8787:8787`.

Cleanly stop the Docker lab:

```bash
docker compose down
```

Delete local jobs, reports, evidence, audit data, Agent Lab imports, and Docker volumes only when you intentionally want a full reset:

```bash
docker compose down -v
```

## 3. Clean workspace dashboard

A clean workspace shows:

- zero dashboard metrics;
- no assets;
- no findings;
- no sample vulnerability data;
- a message explaining that scans must be run before evidence appears.

After you run scans, VulnoraIQ loads saved backend scan data and shows only your scan jobs, findings, statuses, evidence, and reports.

## 4. Configure targets

Open **Targets** in the WebUI to manage authorised AI systems.

For each non-demo target, confirm:

- target name and target ID;
- endpoint/base URL;
- request type and payload template;
- response extraction path;
- owner/contact details;
- authorised environment/safety profile.

## 5. Experimental Agent Lab

Open this path after startup:

```text
http://localhost:8787/agent-lab
```

Use Agent Lab to import a real AI-agent project, configure provider/API key settings, select CPU/GPU Docker runtime mode, build/run the agent, auto-create a target, and launch an authorised scan.

Agent Lab remains experimental because it builds and runs imported code through local Docker. Use it only for code and systems you own or are authorised to assess.
