# Ready-to-remove documentation review queue

This folder is a staging area for documentation that appears to be completed, superseded, or no longer useful as active operator guidance.

Nothing in this folder is deleted automatically. Review each file, then either delete it in a follow-up cleanup PR or move it back into the active documentation tree if it still has current value.

Some original paths keep lightweight active stubs because CI validators, release checks, or external links still expect those paths to exist. The full historical content lives here until maintainers approve final deletion.

## Current candidates

| File | Why it was moved here |
| --- | --- |
| `AGENT_LAB_PLAN.md` | The current operator flow is documented in `docs/AGENT_LAB.md`, `docs/USER_GUIDE.md`, and `docs/RUN_MODES_DESKTOP_AND_DOCKER_LAB.md`; this implementation plan is mostly historical. |
| `AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md` | The full AITG manifest/profile/validator path is now represented in implementation-status and integration docs; the plan still contains planned-state wording. |
| `AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md` | The plan marks the current self-hosted/internal readiness tranche complete; active status now belongs in `docs/IMPLEMENTATION_STATUS.md`, the scorecard, and assurance docs. |
| `GENAI_PRODUCTION_READINESS_PLAN.md` | The GenAI internal scenario-harness tranche is complete for the current scope; active status now belongs in implementation/status and assurance docs. |
| `OWASP_PRODUCTION_READINESS_PLAN.md` | The document still describes an early planning posture that conflicts with the current `0.3.0` implementation status. |

## Review rule

Keep this folder out of normal user-facing guidance. Active docs should link to current guides, status, assurance boundaries, and future-plan documents instead of these candidate-removal files.
