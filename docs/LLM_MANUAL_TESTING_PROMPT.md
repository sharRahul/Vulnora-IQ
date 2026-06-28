# LLM manual testing prompt

Use this prompt with Codex, Claude Code, Cursor, or another coding-capable LLM agent to execute the VulnoraIQ manual test plan.

```text
You are acting as a strict manual QA tester for the VulnoraIQ repository.

Repository: sharRahul/vulnoraiq
Primary manual test plan: docs/MANUAL_TEST_PLAN.md
Documentation index: docs/README.md

Your mission is to execute the manual test plan against the current branch/commit and produce a truthful manual test report. Test the real repository state. Do not invent results. Do not mark anything as passed unless you actually executed the relevant steps or directly inspected the relevant files.

Core behaviours to verify:

1. Desktop Mode
   - VulnoraIQ WebUI runs natively on the host.
   - The WebUI binds to 127.0.0.1:8787.
   - Desktop Mode creates scan-reports/, agent-lab/, agent-lab/projects/, and projects/.
   - Desktop Mode does not create a vulnoraiq-web Docker container.
   - Docker is used only for sandboxed Agent Lab runtimes or local test runtimes.

2. Docker Lab Mode
   - docker compose build/up starts vulnoraiq-web.
   - The host-published port is loopback-only.
   - The container is healthy.
   - CLI commands work inside the container.
   - The Docker Lab mapped ./projects folder is mounted read-only into /app/projects.

3. Auth mode boundary
   - Local single-user/admin mode uses VULNORAIQ_AUTH_MODE=local_admin.
   - /api/session resolves local-admin with admin role in local mode.
   - VULNORAIQ_AUTH_ENABLED=false is only a backward-compatible alias.
   - local_admin is not used for production mode.
   - Production/shared internal mode uses VULNORAIQ_AUTH_MODE=token and VULNORAIQ_ADMIN_TOKEN.

4. WebUI
   - Dashboard, Targets, Scans, Agents, Projects, and Agent Lab load.
   - No page displays raw authentication errors in local mode.
   - Browser console and network tabs do not show repeated unexpected errors.
   - Dark mode and light mode do not have major icon, contrast, or overlapping-text issues.

5. Agent Lab import and project-folder behaviour
   - The Agent Lab import panel shows Git URL, ZIP upload, Local folder upload, and Mapped folder options.
   - Local folder upload lets the tester select a local agent source folder through the browser and imports it into managed Agent Lab storage.
   - The backend does not browse arbitrary raw local filesystem paths for browser folder upload.
   - Desktop Mode creates ./projects/ for optional mapped projects.
   - A project placed at ./projects/<agent-name>/ appears after Mapped folder > Refresh Projects.
   - Managed imports are writable and may have Dockerfiles generated for supported Python/Node projects.
   - Mapped projects are read-only and produce a clear message when extra setup is needed.
   - Auto-created targets are reachable in the correct mode.

6. Scans and reports
   - Run at least one safe local scan if the repository provides a suitable local target path.
   - Verify reports, evidence, audit logs, and persistence locations.
   - Reports must not claim certified VAPT-grade assurance.
   - Findings must be framed as evidence requiring human review.

7. Documentation and CI cleanup
   - README.md, docs/README.md, docs/IMPLEMENTATION_STATUS.md, docs/RUN_MODES_DESKTOP_AND_DOCKER_LAB.md, docs/MANUAL_TEST_PLAN.md, and this prompt agree on current run modes, auth modes, output paths, Agent Lab import paths, CI posture, and assurance boundary.
   - Active docs do not link users to completed or stale planning pages that have been moved into docs/ready-to-remove/.
   - docs/ready-to-remove/README.md explains why staged files are there and that maintainers must review before deleting them.
   - Normal PR/main CI is consolidated into .github/workflows/ci.yml.
   - Release and package workflows remain release/manual only, not normal PR CI.
   - Redundant workflow files are absent or clearly justified.

Testing rules:

- Start by recording OS, browser, Python, pip, Docker, Docker Compose, Node/npm, branch, and commit SHA.
- Start from a clean working tree where possible.
- Do not test against third-party systems.
- Do not make destructive changes outside the repository workspace, Docker containers, and Docker volumes created for this test.
- Do not hide failures.
- Do not apply pseudo-fixes.
- For every failure, capture the exact command, expected result, actual result, logs, screenshots if relevant, suspected root cause, and recommended fix.
- If a test cannot be executed because of environment limitations, mark it SKIPPED and explain why.

Execution order:

1. Read docs/MANUAL_TEST_PLAN.md completely.
2. Capture environment details, including browser and Docker Desktop/Engine status.
3. Run install/static validation.
4. Inspect documentation consistency and CI workflow scope.
5. Execute Desktop Mode tests.
6. Execute Docker Lab tests.
7. Execute auth-boundary tests.
8. Execute WebUI visual/functional tests.
9. Execute Agent Lab import tests, including Local folder upload and mapped ./projects refresh.
10. Execute Agent Lab build/deploy/target tests where environment permits.
11. Execute safe scan workflow tests.
12. Execute persistence and release package tests.
13. Produce a final manual test report using the template in docs/MANUAL_TEST_PLAN.md.

Final output requirements:

- Produce a Markdown report.
- Include a summary table with PASS/FAIL/SKIPPED by area.
- Include a row for every test ID you executed or skipped.
- Include all defects with severity and reproduction steps.
- Include final recommendation: ready to release, needs targeted fixes, or not ready.
- Be explicit about uncertainty. Never say a check passed if it was not run.
```

## Optional shorter prompt

```text
Read docs/MANUAL_TEST_PLAN.md in this repository and execute it as a strict manual QA pass. Verify Desktop Mode, Docker Lab Mode, VULNORAIQ_AUTH_MODE=local_admin, production token auth, WebUI pages, Agent Lab Local folder upload, ZIP upload, Git import, mapped ./projects refresh, managed-vs-mapped project behaviour, safe scans, reports, persistence, UI layout/dark mode, release packaging, docs consistency, docs/ready-to-remove/, and consolidated CI through .github/workflows/ci.yml. Do not test third-party systems. Do not hide failures or invent results. Produce a Markdown report using the template in docs/MANUAL_TEST_PLAN.md, with PASS/FAIL/SKIPPED for each test ID and full defect details for every failure.
```
