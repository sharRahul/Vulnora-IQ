# WebUI release hardening

This document captures release checks for the current VulnoraIQ WebUI.

## Current WebUI release baseline

- The supported WebUI source is `webui/console/`.
- The built runtime assets are committed under `webui/static/console/`.
- `webui/hosted_server.py` serves the built console at runtime.
- Python package metadata includes the built console assets as package data.
- The legacy static console is no longer the supported UI.

## Metadata alignment

- Python package metadata uses `Apache-2.0`.
- Docker image metadata should also use `Apache-2.0`.
- Static WebUI assets must stay aligned with the React source build.
- Release docs must identify the WebUI as React/Vite, not the removed legacy console.

## Release validation checklist

Before a WebUI release:

1. Run Python CI gates.
2. Run package metadata validation.
3. Run OWASP/ATLAS and GenAI readiness validators.
4. Run production-readiness validation.
5. Run React typecheck and build.
6. Run hosted WebUI browser flow.
7. Confirm `webui/static/console/` contains the current production build.
8. Confirm Docker lab startup still works.
9. Confirm docs/screenshots reflect the shipped layout.
10. Confirm production deployments keep auth enabled and fail closed.

## Commands

```bash
ruff check .
mypy .
pytest -q
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py --output-dir reports/output/production-readiness
```

```bash
cd webui/console
npm install
npm run typecheck
npm run build
cd ../..
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

## Accepted boundaries

- Node is a build/development dependency for the React console, not a runtime dependency for the hosted Python server.
- Docker Compose is the recommended current path for local lab operation.
- Host-native launcher mode remains local/loopback and should not be used as the shared production deployment path.
- OIDC/JWT, signed installers, image signing/scanning, SIEM rule packs, and independent assurance remain future maturity items.
