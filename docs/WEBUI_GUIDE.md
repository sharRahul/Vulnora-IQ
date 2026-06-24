# WebUI guide

The supported VulnoraIQ WebUI is the React 18 + TypeScript SecOps console in `webui/console/`, built to `webui/static/console/` and served by the Python hosted WebUI entry point.

The legacy static console has been removed. Static files under `webui/static/console/` are build output for the React console and are included as Python package data.

## Start the recommended Docker lab

```bash
docker compose build
docker compose up -d
```

Open <http://localhost:8787>.

## WebUI workspace areas

| Area | Current behaviour |
| --- | --- |
| Dashboard / overview | Shows high-level security and assessment status using React console data models and live backend scan progress. |
| Target management | Loads configured/runtime targets, supports search and environment filters, shows readiness metrics and status pills, validates targets, saves/deletes runtime targets, launches authorised scans, and refreshes recent jobs. |
| Findings and intelligence | Provides analyst-facing panels for findings, triage context, persisted remediation/status actions, finding history, and assistant-backed analysis. |
| Assessment options | Uses configured profiles and single-test options from `config/attack_profiles.yaml`. |

## Current backend API wiring

The WebUI is wired to:

- `GET /api/targets`
- `POST /api/targets/save`
- `POST /api/targets/delete`
- `POST /api/targets/{id}/validate`
- `GET /api/scans`
- `POST /api/scans`
- `GET /api/scans/{id}`
- `GET /api/scans/{id}/events`
- `GET /api/scans/{id}/findings`
- `PATCH /api/scans/{id}/findings/{finding_id}`
- `GET /api/scans/{id}/findings/{finding_id}/history`
- `GET /api/assistant/config`
- `POST /api/assistant/chat`

The scan launch path keeps the non-demo authorisation guard. Target validation uses the same target adapter/connectivity logic as the CLI. Assistant requests require authentication and CSRF protection and pass model controls from the React panel to the backend orchestrator.

## Assistant model controls

The Ask VulnorAIQ panel sends live chat payloads to `/api/assistant/chat`. Operators can adjust:

- model selection from the server-provided allow-list;
- temperature, constrained by backend validation;
- instruction text used for the backend assistant request.

The default backend provider is local/deterministic so self-hosted deployments work without outbound network access. Operators can configure provider settings with environment variables documented in deployment/runbook material. Assistant output is advisory and requires human review before closure or remediation.

## Remaining WebUI backend work

No current WebUI critical path uses local-only scan or finding mutation state. Future maturity work is focused on enterprise identity, SIEM/SOAR integrations, signed/native packaging, and external independent assurance.

## Operator flow

1. Start Docker Compose and open the WebUI.
2. Go to the target workspace.
3. Search or filter for the target.
4. Validate target connectivity.
5. Review the readiness checklist.
6. Select an assessment profile or focused single-test option.
7. Confirm authorisation for non-demo targets.
8. Launch the scan.
9. Review recent jobs, findings, live progress, assistant guidance, and report artifacts.

## Development flow

```bash
cd webui/console
npm install
npm run typecheck
npm run build
```

The production build emits assets into `webui/static/console/`. The Python hosted server serves the built console; Node is not required at runtime.

## Browser test flow

```bash
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

The hosted WebUI Playwright flow is also part of the GitHub Actions CI path on Python 3.12.

## Security boundary

Launcher/local mode is for loopback laptop/workstation use. For shared/internal-server use, enable production mode, auth, reverse-proxy/TLS controls, and the documented deployment/runbook process.

## Live scan progress and finding actions

The hosted React console now consumes `/api/scans/{scan_id}/events` with `EventSource` for persisted live progress. The target workspace shows stream state, latest phase, progress, event timeline, finding count, completion, and error states. Finding remediation/status APIs are available under `/api/scans/{scan_id}/findings/...`; mutations require authentication and CSRF protection and create persistent history/audit records.
