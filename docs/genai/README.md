# GenAI Security Implementation Plan

This folder defines VulnoraIQ's implementation plan for GenAI security testing beyond the existing OWASP LLM 2025 category files.

> **Status:** planning.  
> **Scope:** GenAI application/data-security risks, governance runbook requirements, and data handling controls.  
> **Boundary:** not yet active production-validated detection coverage.

## Source documents to review

- `docs/owasp-documents/OWASP-GenAI-COMPASS-RunBook-1.0.pdf`
- `docs/owasp-documents/OWASP-GenAI-Data-Security-Risks-and-Mitigations-2026-v1.0.pdf`
- existing VulnoraIQ `docs/owasp/` LLM implementation specs
- `docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`

## Planned GenAI coverage areas

| Planning ID | GenAI risk/control area | Current status | Related OWASP LLM categories | Primary evidence surfaces |
| --- | --- | --- | --- | --- |
| GENAI-DATA-01 | Sensitive data in prompts and uploaded context | Planning | LLM02, LLM07 | prompt, upload metadata, request trace |
| GENAI-DATA-02 | Sensitive data in model responses | Planning | LLM02, LLM05, LLM09 | response, output artifact, report artifact |
| GENAI-DATA-03 | RAG/vector-store data leakage | Planning | LLM02, LLM08 | retrieval trace, document metadata, citation map |
| GENAI-DATA-04 | Training/fine-tuning data exposure | Planning | LLM02, LLM03, LLM04 | dataset metadata, model metadata, provider policy |
| GENAI-DATA-05 | Data provenance and source integrity | Planning | LLM03, LLM04, LLM08 | source manifest, hash/signature, owner/review metadata |
| GENAI-DATA-06 | Logs, telemetry, and report artifact leakage | Planning | LLM02, LLM05, LLM07 | logs, audit events, reports, SARIF, dashboard exports |
| GENAI-DATA-07 | Third-party provider and data residency exposure | Planning | LLM02, LLM03 | provider inventory, contract metadata, region/retention flags |
| GENAI-DATA-08 | Tool/connector access to restricted data | Planning | LLM02, LLM06 | tool trace, connector manifest, credential scope |
| GENAI-GOV-01 | Governance ownership and approval workflow | Planning | LLM03, LLM04, LLM06 | approval evidence, risk owner, exception metadata |
| GENAI-GOV-02 | Risk register and control mapping | Planning | all LLM categories | policy mapping, control status, residual risk |

## Relationship to existing LLM tests

The existing LLM test plan focuses on model, RAG, agent, output, and resource-risk categories. The GenAI plan adds organisation-level and data-security controls:

- data classification
- data minimisation
- retention and deletion
- provider handling
- governance sign-off
- logging/report artifact hygiene
- data provenance and lineage
- privacy/security control mapping

## Maturity rule

A GenAI control area remains `Planning` until:

1. source category wording is confirmed from the OWASP PDFs,
2. a safe local fixture exists,
3. an evaluator or validator exists,
4. reports include structured evidence,
5. docs explain what the result proves and does not prove,
6. CI validates the behaviour.

A GenAI area can move to `Working starter` when it has secure, vulnerable, ambiguous, and edge-case scenarios plus report evidence and false-positive/false-negative guidance.

## Files

- [`PRODUCTION_READINESS_PLAN.md`](PRODUCTION_READINESS_PLAN.md) — phased implementation plan

## Next steps

1. Extract exact headings and category IDs from the GenAI OWASP PDFs.
2. Convert planning IDs into confirmed source IDs where available.
3. Add scenario manifests under `benchmarks/fixtures/genai/`.
4. Add GenAI evaluator composition in `core/genai_evaluators.py` or an equivalent module.
5. Add machine-readable mapping in `config/owasp_mitre_atlas_crosswalk.yaml`.
6. Add report and dashboard coverage for GenAI data-security controls.