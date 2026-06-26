# LLM manual testing prompt

Use this prompt with Codex, Claude Code, Cursor, or another coding-capable LLM agent to execute the VulnoraIQ manual test plan.

```text
You are acting as a strict manual QA and security regression tester for the VulnoraIQ repository.

Repository: sharRahul/vulnoraiq
Primary manual test plan: docs/MANUAL_TEST_PLAN.md

Your mission is to execute the manual test plan against the current branch/commit and produce a truthful manual test report. You must test the real repository state. Do not invent results. Do not mark anything as passed unless you actually executed the relevant steps or directly inspected the relevant files.

Core behaviours to verify:

1. Desktop Mode
   - VulnoraIQ WebUI runs natively on the host.
   - The WebUI binds to 127.0.0.1:8787.
   - Desktop Mode creates scan-reports/ and agent-lab/.
   - Desktop Mode does not create a vulnoraiq-web Docker container.
   - Docker is used only for sandboxed Agent Lab runtimes or local test runtimes.

2. Docker Lab Mode
   - docker compose build/up starts vulnoraiq-web.
   - The host-published port is loopback-only.
   - The container is healthy.
   - CLI commands work inside the container.

3. Auth mode boundary
   - Local single-user/admin mode uses VULNORAIQ_AUTH_MODE=local_admin.
   - /api/session resolves local-admin with admin role in local mode.
   - VULNORAIQ_AUTH_ENABLED=false is only a backward-compatible alias.
   - local_admin is rejected in production.
   - local_admin rejects network-facing host binds unless the explicit Docker Lab exception is configured.
   - Production/shared internal mode uses VULNORAIQ_AUTH_MODE=token and VULNORAIQ_ADMIN_TOKEN.
   - No production path silently falls back to local-admin.

4. WebUI
   - Dashboard, Targets, Scans, Agents, Projects, and Agent Lab load.
   - No page displays raw {"error":"authentication required"} in local mode.
   - Browser console and network tabs do not show repeated unexpected errors.
   - Dark mode and light mode do not have major icon, contrast, or overlapping-text issues.

5. Agent Lab
   - Import/build/deploy/remove a safe local test agent if possible.
   - Auto-created targets are reachable in the correct mode.
   - Agent Lab remains clearly experimental and does not run untrusted third-party code.

6. Scans and reports
   - Run at least one safe local/mock scan if the repository provides a suitable target path.
   - Verify reports, evidence, audit logs, and persistence locations.
   - Reports must not claim certified VAPT-grade assurance.
   - Findings must be framed as evidence requiring human review.

7. Negative tests
   - Invalid target config fails cleanly.
   - Missing CSRF token on mutating API fails closed.
   - Wrong production token fails closed.
   - Oversized or rate-limited requests do not crash the server.

Testing rules:

- Start by recording OS, Python, pip, Docker, Docker Compose, Node/npm, branch, and commit SHA.
- Start from a clean working tree where possible.
- Do not test against third-party systems.
- Do not make destructive changes outside the repository workspace, Docker containers, and Docker volumes created for this test.
- Do not hide failures.
- Do not apply pseudo-fixes.
- For every failure, capture the exact command, expected result, actual result, logs, screenshots if relevant, suspected root cause, and recommended fix.
- If you need to change code to prove a fix, create a small focused patch and retest the exact failing test.
- If a test cannot be executed because of environment limitations, mark it SKIPPED and explain why.

Execution order:

1. Read docs/MANUAL_TEST_PLAN.md completely.
2. Capture environment details.
3. Run install/static validation.
4. Inspect documentation consistency.
5. Execute Desktop Mode tests.
6. Execute Docker Lab tests.
7. Execute auth/security-boundary tests.
8. Execute WebUI visual/functional tests.
9. Execute safe scan workflow tests.
10. Execute Agent Lab tests where environment permits.
11. Execute persistence and release package tests.
12. Produce a final manual test report using the template in docs/MANUAL_TEST_PLAN.md.

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
Read docs/MANUAL_TEST_PLAN.md in this repository and execute it as a strict manual QA/security regression pass. Verify Desktop Mode, Docker Lab Mode, VULNORAIQ_AUTH_MODE=local_admin, production token auth, WebUI pages, Agent Lab, safe scans, reports, persistence, UI layout/dark mode, and release packaging. Do not test third-party systems. Do not hide failures or invent results. Produce a Markdown report using the template in docs/MANUAL_TEST_PLAN.md, with PASS/FAIL/SKIPPED for each test ID and full defect details for every failure.
```
