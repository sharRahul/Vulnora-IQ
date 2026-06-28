# Agent Lab implementation plan

**Status:** Implemented for the current experimental local-lab scope.

This active stub preserves the original documentation path for discoverability and validation stability. The full historical implementation plan is staged for maintainer review in [`ready-to-remove/AGENT_LAB_PLAN.md`](ready-to-remove/AGENT_LAB_PLAN.md).

## Current source of truth

- Operator guide: [`AGENT_LAB.md`](AGENT_LAB.md)
- User guide: [`USER_GUIDE.md`](USER_GUIDE.md)
- Run modes: [`RUN_MODES_DESKTOP_AND_DOCKER_LAB.md`](RUN_MODES_DESKTOP_AND_DOCKER_LAB.md)
- Implementation status: [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md)

## Current implemented scope

Agent Lab supports importing real AI-agent projects through browser local folder upload, ZIP upload, Git import, and read-only mapped project refresh. It can configure LLM/provider runtime settings, select CPU/GPU Docker runtime options, build and run sandboxed containers, auto-create runtime targets, and launch authorised scans.

Agent Lab remains experimental because it builds and runs operator-provided code through Docker. Use it only for code and systems you own or are explicitly authorised to assess.

## Maintainer note

Delete or archive the full historical copy in `docs/ready-to-remove/` only after maintainer review.
