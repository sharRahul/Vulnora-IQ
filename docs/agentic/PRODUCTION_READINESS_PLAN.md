# Agentic Applications Production Readiness Plan

This document extends VulnoraIQ's OWASP LLM implementation plan into Agentic Application testing.

> **Current status:** planning.  
> **Readiness claim:** no Agentic Application category should be marked `Working` until source-category wording, fixtures, evaluators, evidence, reporting, and CI gates are implemented.

## Current baseline

VulnoraIQ already has:

- `LLM06: Excessive Agency` starter planning and oracle coverage
- agent runtime governance docs and starter scenarios under `agent_testing/`
- policy exceptions and approval evidence concepts
- structured scan results and report generation
- Web UI production controls for controlled internal deployment
- MITRE ATLAS planning register and OWASP crosswalk

Agentic Application work should extend these into runtime behaviour testing rather than duplicating the existing LLM test plan.

## Maturity ladder

| Level | Meaning | Required evidence |
| --- | --- | --- |
| Planning | Risk/control area identified but no active check. | Source doc reference, candidate OWASP/ATLAS mapping, owner. |
| Working-alpha starter | One safe local fixture and minimal evaluator exist. | Good/bad fixture, minimal plan/tool evidence, unit test. |
| Working starter | Representative agent scenario set and report evidence exist. | secure/vulnerable/ambiguous/edge-case scenarios, report fields, negative controls. |
| Working | Stable confidence, benchmark thresholds, false-positive handling, and operator guidance exist. | CI gates, benchmark thresholds, evidence schema, reviewed docs. |
| Production-ready candidate | Authorised validation guidance, runtime safety guardrails, and governance approvals exist. | validation runbook, approval gates, evidence retention policy, release sign-off. |

## Phase AGENTIC-1 — Source extraction and ASI category normalisation

Actions:

1. Extract exact category IDs, names, descriptions, examples, and mitigations from:
   - `OWASP-Top-10-for-Agentic-Applications-2026-12.6.pdf`
   - `OWASP-Top10-for-Agentic-Applications_AIUC-1-Crosswalk-May26.pdf`
   - `State-of-Agentic-AI-Security-and-Governance-v2.01.pdf`
2. Confirm official `ASIxx` IDs and names.
3. Map each confirmed `ASIxx` item to a VulnoraIQ planning row.
4. Preserve unmapped rows as `Unmapped / map later`.
5. Update `docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`.

Acceptance:

- exact official wording is captured
- planning IDs are replaced or linked to official IDs
- uncertain mappings remain visible

## Phase AGENTIC-2 — Agent scenario manifests

Create safe scenario manifests under:

```text
benchmarks/fixtures/agentic/
```

Required fields:

- `scenario_id`
- `agentic_id`: confirmed ASI ID or planning ID
- `risk_area`
- `fixture_type`: secure, vulnerable, ambiguous, edge_case
- `agent_loop`: plan, act, observe, reflect, delegate
- `tool_surface`: none, read_only, write, external_network, credentialed, high_impact
- `memory_surface`: none, session, long_term, vector_store, external_state
- `input_fixture`
- `expected_secure_outcome`
- `expected_vulnerable_signal`
- `required_evidence_fields`
- `mitre_atlas_tactics`
- `manual_review_required`

Minimum scenarios:

| Planning ID | Required scenarios |
| --- | --- |
| AGENTIC-01 | direct instruction injection, indirect retrieved injection, tool-description injection, secure refusal |
| AGENTIC-02 | allowed read-only tool, blocked high-impact tool, over-scoped connector, missing approval |
| AGENTIC-03 | safe delegation, untrusted agent handoff, role escalation through delegation, ambiguous chain |
| AGENTIC-04 | trusted tool manifest, poisoned tool description, unknown connector owner, version drift |
| AGENTIC-05 | safe memory write, malicious memory seed, stale poisoned memory, plan tampering |
| AGENTIC-06 | allowed data flow, credential-bearing tool trace, restricted data exfil attempt, report artifact leak |
| AGENTIC-07 | bounded loop, runaway retry, tool-call fan-out, cost-limit breach |
| AGENTIC-08 | approved high-impact action, missing approval, denied action, expired exception |
| AGENTIC-09 | complete trace, missing request ID, missing tool trace, missing memory diff |
| AGENTIC-10 | safe goal decomposition, unsafe plan, policy conflict, high-impact manual review |

## Phase AGENTIC-3 — Evaluator composition

Potential module:

```text
core/agentic_evaluators.py
```

Evaluator types:

- instruction hierarchy evaluator
- indirect-instruction boundary evaluator
- tool permission evaluator
- tool manifest/provenance evaluator
- delegation boundary evaluator
- memory integrity evaluator
- plan safety evaluator
- approval checkpoint evaluator
- loop/resource budget evaluator
- action trace completeness evaluator
- data-flow and exfiltration evaluator
- policy conflict evaluator
- manual-review routing evaluator

Each evaluator should return:

- `status`: pass, warn, fail, review
- `confidence`
- `reason`
- `evidence_fields`
- `agent_loop_stage`
- `tool_surface`
- `memory_surface`
- `manual_review_required`

## Phase AGENTIC-4 — Evidence schema expansion

Extend report JSON and finding evidence with:

- `agentic_id`
- `agentic_risk_area`
- `agent_loop_stage`
- `goal`
- `plan_summary`
- `policy_decision`
- `tool_name`
- `tool_permission_scope`
- `tool_provenance_status`
- `action_type`
- `approval_required`
- `approval_status`
- `memory_surface`
- `memory_write_status`
- `delegation_target`
- `delegation_trust_status`
- `loop_budget_status`
- `cost_budget_status`
- `trace_completeness_status`
- `mitre_atlas_tactics`
- `manual_review_reason`

## Phase AGENTIC-5 — Safe local agent fixtures

Add or extend fixtures under `agent_testing/` and `examples/local_demo_targets/`.

Fixtures must avoid real external action and use simulated tools only:

- `safe_read_tool`
- `blocked_write_tool`
- `credentialed_tool_stub`
- `network_tool_stub`
- `approval_required_tool`
- `memory_write_stub`
- `delegate_to_agent_stub`
- `costly_loop_stub`

Each tool should emit structured traces without performing real external calls.

## Phase AGENTIC-6 — Reports and dashboards

Reports must explain:

- what agent behaviour was tested
- which loop stage was affected
- which tool/memory/delegation surface was involved
- whether a real action occurred or a simulated action was blocked
- whether approval was required and present
- whether traceability was complete
- whether data left an approved boundary
- why human review is required
- what the finding does not prove

Dashboard additions:

- Agentic risk coverage table
- tool/action surface coverage
- memory/state integrity status
- approval-gate status
- loop/resource-budget status
- trace completeness status
- OWASP Agentic to MITRE ATLAS coverage view

## Phase AGENTIC-7 — CI and release gates

Add gates that fail if:

- confirmed ASI categories lack planning rows
- scenario manifests are missing required fields
- vulnerable agent fixtures are missed
- secure fixtures are flagged high-confidence without reason
- high-impact actions lack approval evidence
- tool traces or memory traces are missing for relevant scenarios
- report output lacks agentic ID, MITRE tactic, confidence, and manual-review fields
- docs and machine-readable crosswalk drift

## Agentic implementation matrix

| Planning ID | Current baseline | Next implementation focus | Working target |
| --- | --- | --- | --- |
| AGENTIC-01 | LLM01/LLM07 starter prompt boundary checks. | Multi-step direct/indirect/tool-description injection scenarios. | Agent refuses or isolates injected instructions with traceable boundary evidence. |
| AGENTIC-02 | LLM06 starter tool governance. | Tool scopes, approval checks, high-impact action classification. | Over-scoped tools and missing approvals are detected before action. |
| AGENTIC-03 | Limited delegation modelling. | Agent identity, trust boundary, handoff policy, call graph. | Unsafe delegation and confused-deputy paths are flagged. |
| AGENTIC-04 | LLM03 provenance concepts. | Tool manifest, owner, version, description poisoning, connector drift. | Unknown or poisoned tools are detected before invocation. |
| AGENTIC-05 | LLM04/LLM08 source trust. | Memory integrity, plan tampering, state diff, rollback. | Poisoned memory/state is detected and routed to review. |
| AGENTIC-06 | LLM02/LLM06 leakage and tool actions. | Data-flow across tool calls, credential scope, artifact leakage. | Restricted data crossing a tool boundary is flagged. |
| AGENTIC-07 | LLM10 resource budgets. | Iteration, retry, fan-out, cost, timeout, loop controls. | Runaway agent behaviour is bounded and evidenced. |
| AGENTIC-08 | Approval evidence exists. | Approval checkpoints for high-impact actions. | Missing/expired approvals block high-impact simulated action. |
| AGENTIC-09 | Audit logging exists at platform level. | Agent action trace completeness and non-repudiation evidence. | Findings include request/tool/memory/approval trace completeness. |
| AGENTIC-10 | LLM09/LLM10 risk signals. | Goal-plan-policy conflict and unsafe plan classification. | Unsafe or conflicting plans are routed to manual review. |

## Immediate backlog

1. Extract official ASI category names and descriptions from the OWASP PDFs.
2. Create `benchmarks/fixtures/agentic/` manifests.
3. Add simulated safe agent tools and traces.
4. Add `core/agentic_evaluators.py`.
5. Extend evidence schema for plan/tool/memory/delegation/action traces.
6. Add agentic dashboard coverage table.
7. Add report guidance blocks for agentic findings.
8. Add machine-readable ASI/Agentic-to-ATLAS mapping.
9. Add CI gates for agentic manifests and report fields.
10. Update `ASSESSMENT_ASSURANCE.md` after the first agentic evaluator batch lands.

## Claim rule

Do not describe Agentic Application coverage as official OWASP ASI coverage until the PDF categories are extracted and confirmed. Do not mark a category `Working` until fixtures, evaluators, evidence, reports, and CI gates exist.