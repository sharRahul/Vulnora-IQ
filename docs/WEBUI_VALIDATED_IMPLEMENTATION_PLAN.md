# VulnoraIQ WebUI validated implementation plan

This document records the original WebUI implementation plan and its current status after later WebUI work.

## Current status

The original staged plan has been superseded in part by the React SecOps console.

Current supported WebUI:

- source: `webui/console/`;
- framework: React 18 + TypeScript;
- build: Vite;
- runtime assets: `webui/static/console/`;
- server: `webui/hosted_server.py`.

The legacy static console has been removed.

## Original PR sequence and current outcome

| PR | Original theme | Current outcome |
| --- | --- | --- |
| 1 | Responsive, dark mode, accessibility, loading/error feedback | Superseded by React/Tailwind console direction. |
| 2 | Frontend structure cleanup | Superseded by React component structure. |
| 3 | WebUI tests and CI | Browser testing remains part of current CI direction. |
| 4 | Optional build pipeline | Superseded by React/Vite as the supported WebUI source. |
| 5 | Auth/session hardening | Production auth is enforced by hosted server controls. |
| 6 | Docker dependency automation | Docker guidance remains useful; Docker Compose is now the recommended lab path. |
| 7 | Docker/package metadata and release hardening | Still relevant for release validation. |
| 8 | Final documentation and layout plan | Refreshed by current docs. |
| 9 | Interaction gaps | Superseded by target-management workspace and later React updates. |

## Current implemented WebUI capabilities

- React app shell and dashboard panels.
- Target search and environment filtering.
- Target readiness metrics and status indicators.
- Runtime target save/delete.
- Target connectivity validation.
- Authorised scan creation.
- Recent scan job list.
- Built static assets served by the Python hosted server.
- Hosted browser-flow test path.

## Current deferred items

- Real SSE progress stream integration.
- Persisted finding state transitions.
- Persisted remediation actions.
- Assistant chat backend.
- Deeper OWASP/GenAI dashboard drill-downs.
- Signed/native release installers.

## Documentation rule

Keep this document as a historical status note. Current operator guidance belongs in:

- `docs/WEBUI_GUIDE.md`
- `docs/WEB_UI_TEST_CATALOG.md`
- `docs/WEBUI_LAYOUT_PLAN.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `webui/console/README.md`
