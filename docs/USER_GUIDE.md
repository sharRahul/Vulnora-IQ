# VulnoraIQ User Guide

This guide explains how to use VulnoraIQ as a local or internal AI security testing application. It assumes you are testing only systems you own or are explicitly authorised to assess.

## 1. Choose how to run VulnoraIQ

Use one of these supported paths:

| Path | Best for | Start command |
| --- | --- | --- |
| Desktop Mode | Recommended laptop/workstation use | `launch-vulnoraiq-webui.bat`, `.command`, or `.sh` |
| Docker GUI lab / Docker Lab Mode | Servers, VMs, CI, reproducible dev labs | `launch-vulnoraiq-docker-lab.*` or `docker compose up -d` |
| Python package/source checkout | CLI and local WebUI development | `vulnoraiq-web --host 127.0.0.1 --port 8787` |
| Internal server | Shared controlled environment | production config validation plus reverse proxy/TLS/auth |

For a clean first run, the dashboard is intentionally empty. VulnoraIQ does not show sample findings, mock assets, or dummy dashboard data.

## 2. Start the local browser GUI

The default local path is Desktop Mode:

| Platform | Launcher |
| --- | --- |
| Windows | `launch-vulnoraiq-webui.bat` |
| macOS | `launch-vulnoraiq-webui.command` |
| Linux | `launch-vulnoraiq-webui.sh` |

In the current source/release-package implementation, Desktop Mode requires Python 3.10+ on PATH plus Docker Desktop or a compatible Docker Engine. The long-term packaged app should bundle the Python runtime so Docker remains the only external runtime prerequisite for normal users.

Desktop Mode starts VulnoraIQ on the host machine, uses Docker only for sandboxed Agent Lab runtimes, and stores local data here:

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

Advanced Docker Lab launchers:

| Platform | Launcher |
| --- | --- |
| Windows | `launch-vulnoraiq-docker-lab.bat` |
| macOS | `launch-vulnoraiq-docker-lab.command` |
| Linux | `launch-vulnoraiq-docker-lab.sh` |

Manual Docker Lab flow:

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

## 5. Run a scan

After a target is configured and validated:

1. select the target in the WebUI;
2. choose a profile such as `baseline`, `rag`, `agent`, `full`, `ai_agent_foundation`, or a focused single-test profile;
3. confirm the authorisation checklist;
4. start the scan;
5. watch live progress and scan events.

CLI equivalent in Docker Lab Mode:

```bash
docker compose exec vulnoraiq-web vulnoraiq scan --target <target_name> --profile baseline --authorised
```

CLI equivalent in Desktop Mode after installing the package locally:

```bash
vulnoraiq scan --target <target_name> --profile baseline --authorised
```

## 6. Review and act on findings

After the scan completes, review:

- findings and severity;
- evidence snippets and redaction state;
- policy status;
- generated reports;
- finding history and remediation notes.

In Desktop Mode, local reports and evidence are written under `scan-reports/`. In Docker Lab Mode, they are written under the Docker `/data` volume unless the deployment maps them elsewhere.

Treat VulnoraIQ output as framework evidence that requires human review before sharing, closing, or treating a finding as confirmed.

## 7. Experimental Agent Lab

Open this path after startup:

```text
http://localhost:8787/agent-lab
```

Use Agent Lab to import a real AI-agent project, configure provider/API key settings, select CPU/GPU Docker runtime mode, build/run the agent, auto-create a target, and launch an authorised scan.

In Desktop Mode, auto-created Agent Lab targets use published localhost ports so the host-based scanner can reach the sandboxed agent container. In Docker Lab Mode, targets use container DNS on the Docker network.

Agent Lab remains experimental because it builds and runs imported code through local Docker. Use it only for code and systems you own or are authorised to assess.

## 8. Operate safely

Use VulnoraIQ only for authorised assessment work.

- Keep local launchers bound to loopback.
- Do not expose the WebUI on a shared network without production auth, TLS, reverse proxy controls, audit retention, and backup controls.
- Store API keys outside the repository and pass them through runtime environment variables or approved secret handling.
- Review reports and evidence before sharing them.
- Stop Docker Lab with `docker compose down` when you are finished.
