> Moved to `docs/ready-to-remove/` during the documentation cleanup on 2026-06-28. Review and delete if current OWASP status, integration, and assurance docs cover everything still needed.

# OWASP LLM 2025 Production Readiness Plan

This document converts the existing OWASP LLM 2025 starter documentation into a production-readiness implementation plan for VulnoraIQ.

> **Current status:** planning document. VulnoraIQ remains an early development build. These items define what must be implemented, tested, reviewed, and documented before any category is marked `Working` or production-ready.

## Current repo baseline pulled from OWASP docs and code

The existing `docs/owasp/` files already define starter scope, safe fixture strategy, expected secure/vulnerable behaviour, required evidence, evaluator ideas, severity rationale, and working criteria for all 10 OWASP LLM 2025 categories.

The current implementation also provides:

- safe OWASP starter oracle definitions in `config/owasp_oracles.yaml`
- deterministic evaluator primitives in `core/evaluators.py`
- local good/bad OWASP fixture behaviour in `examples/local_demo_targets/owasp_fixture_targets.py`
- structured evidence and oracle result plumbing through scanner/report output
- CI-facing package metadata and release gates

## Maturity ladder

| Level | Meaning | Required evidence |
| --- | --- | --- |
| Working-alpha starter | Safe local fixture and basic deterministic evaluator exist. | Good/bad fixture, minimal evidence, CI unit test. |
| Working starter | Category has representative local scenario set and report evidence. | Scenario manifests, evaluator result objects, report fields, negative controls, documentation. |
| Working | Category has contract-tested adapters, stable findings, repeatable benchmark cases, false-positive handling, and operator interpretation guidance. | Adapter contracts, benchmark thresholds, report confidence, reviewed false-positive/false-negative notes. |
| Production-ready candidate | Category has authorised real-target validation guidance, strong safety guardrails, configurable thresholds, and release acceptance criteria. | Validation runbook, safe-mode boundaries, approval gates, evidence-retention rules, release checklist. |
| Production-ready | Reserved for future use after repeated authorised validation, review, and release governance. | Maintainer approval, CI evidence, release evidence pack, documented limitations. |

## Cross-category implementation phases

### Phase OWASP-1 — Scenario manifests

Create a scenario manifest for each category under `benchmarks/fixtures/owasp/` or an equivalent safe fixture path.

Each scenario should define:

- `scenario_id`
- `owasp_id`
- `category`
- `fixture_type`: secure, vulnerable, ambiguous, edge_case
- `target_surface`: model, RAG, agent, tool, memory, output, report artifact
- `input_fixture`
- `expected_secure_outcome`
- `expected_vulnerable_signal`
- `required_evidence_fields`
- `severity_floor`
- `manual_review_required`

### Phase OWASP-2 — Evaluator expansion

Expand `core/evaluators.py` from generic primitives into reusable category-specific evaluator composition.

Required evaluator types:

- boundary decision evaluator
- restricted marker and redaction evaluator
- provenance completeness evaluator
- approval and integrity evaluator
- schema and handoff evaluator
- tool/action/memory governance evaluator
- protected instruction disclosure evaluator
- retrieval boundary and source-trust evaluator
- claim support and uncertainty evaluator
- resource-budget evaluator
- artifact leakage evaluator
- confidence and manual-review evaluator

### Phase OWASP-3 — Evidence model expansion

Extend structured evidence so every finding can explain:

- what was tested
- what was observed
- which evaluator passed, failed, or warned
- which OWASP category and ATLAS technique were linked
- confidence score and confidence reason
- whether evidence came from model output, tool trace, retrieval trace, metadata, report artifact, or simulated fixture
- whether the result is demo-only, starter, or production-candidate evidence

### Phase OWASP-4 — Category benchmark gates

Add benchmark gates that fail if:

- secure fixtures are flagged as high-confidence failures
- vulnerable fixtures are missed
- ambiguous fixtures are not marked for review
- required evidence fields are missing
- generated reports drop OWASP ID, ATLAS ID, severity, confidence, or recommendation
- report artifacts accidentally include restricted fixture markers outside controlled evidence fields

### Phase OWASP-5 — Report language and operator workflow

Each category must have operator-facing language for:

- what the finding means
- what the finding does not prove
- confidence explanation
- reproduction boundaries
- recommended remediation
- when to escalate to manual review
- when not to use the result as production evidence

### Phase OWASP-6 — Production-safety gates

Before any real target testing:

- require explicit authorisation
- require target contract validation
- require safe-mode defaults
- block destructive, load, exfiltration, credential-harvesting, or unauthorised actions
- keep generated evidence minimal and redacted
- store report outputs securely
- document limitations in every generated report

## Category implementation matrix

| OWASP ID | Current baseline | Next implementation focus | Working target |
| --- | --- | --- | --- |
| LLM01 | Boundary prompts and basic forbidden marker checks. | Multi-surface prompt boundary scenarios covering user, retrieved content, tool instructions, and agent chains. | Boundary decision evidence with direct/indirect/triggered classification and false-positive controls. |
| LLM02 | Placeholder disclosure and redaction checks. | Artifact scanning, source classification, restricted marker policies, and evidence minimisation. | End-to-end restricted-data control across model output, retrieval traces, report artifacts, and logs. |
| LLM03 | Provenance metadata checks. | Component inventory manifests, dependency/model/dataset/connector ownership, approval, signature/hash metadata. | Supply-chain risk evidence for every AI component used by a target profile. |
| LLM04 | Approval/integrity checks for corpus/model sources. | Corpus delta scenarios, integrity drift, unreviewed source handling, poisoning metadata signals. | Source trust, hash, owner, approval, and review status validated before trust. |
| LLM05 | Schema and handoff checks. | Output schema policies, unsafe handoff simulation, downstream consumer validation, review gates. | Model output cannot trigger simulated downstream use without validation and approval status. |
| LLM06 | Tool/action boundary checks. | Tool inventory, permission scopes, memory writes, approval points, rollback plans, and audit trails. | Every simulated agent action has allowlist, approval, memory integrity, and rollback evidence. |
| LLM07 | Protected placeholder disclosure checks. | Prompt segment classification, protected instruction markers, artifact redaction, and leakage confidence. | Protected instruction handling is separated from normal refusal text and report artifacts. |
| LLM08 | Retrieval access-boundary checks. | Retrieval scenario manifests, source trust scores, metadata filters, user/group boundaries, citation grounding. | RAG evidence proves allowed/disallowed document decisions and source-trust scoring. |
| LLM09 | Citation/uncertainty checks. | Claim-level support map, unsupported claim detection, fabricated citation detection, high-impact review routing. | Reports show claim support, source traceability, uncertainty, and manual review status. |
| LLM10 | Token/resource budget checks. | Timeout, retry, iteration, cost, fan-out, and agent-loop budget scenarios. | Resource-control evidence shows bounded execution and safe refusal of unbounded workflows. |

## Implementation acceptance checklist

A category can move from `Working-alpha starter` to `Working starter` when:

- at least one secure, vulnerable, ambiguous, and edge-case local scenario exists
- evaluator composition is category-specific, not only a generic primitive
- reports include structured category evidence
- CI validates fixture behaviour
- README and category doc explain limitations

A category can move from `Working starter` to `Working` when:

- scenario coverage includes model, RAG, agent, and report artifact surfaces where relevant
- confidence scoring is stable and documented
- false-positive and false-negative examples are documented
- benchmark thresholds exist and fail on regression
- target adapter contracts specify required traces/evidence for that category
- operator report language is suitable for a VAPT consultant to present without overstating certainty

## Immediate implementation backlog

1. Create category scenario manifests for all 10 OWASP categories.
2. Add `core/owasp_evaluators.py` to compose deterministic evaluator primitives into category-specific decisions.
3. Extend report JSON schema with `owasp_evidence`, `confidence`, `evidence_surface`, and `manual_review_reason`.
4. Add fixture regression tests for secure, vulnerable, ambiguous, and edge-case scenarios.
5. Add artifact scanning for restricted placeholders and protected instruction markers.
6. Add OWASP coverage dashboard table to HTML export.
7. Add operator guidance blocks to generated reports.
8. Add target contract requirements for model output, retrieval trace, tool trace, memory trace, and artifact trace evidence.
9. Add release gate that fails if category docs, scenario manifests, evaluator mappings, and report schema drift.
10. Revisit MITRE ATLAS matrix mappings after OWASP evaluator coverage is deeper.
