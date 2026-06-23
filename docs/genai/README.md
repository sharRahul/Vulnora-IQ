# GenAI Security Implementation Plan

This folder defines VulnoraIQ's GenAI data-security and governance testing plan beyond the existing OWASP LLM 2025 category files.

> **Status:** Production-grade scenario harness for controlled internal enterprise validation.  
> **Scope:** OWASP GenAI Data Security Risks and Mitigations 2026, OWASP GenAI COMPASS operating model, safe synthetic scenario matrix, deterministic GenAI evaluators, and VulnoraIQ evidence/reporting guardrails.  
> **Boundary:** GenAI findings are framework evidence requiring human review. The harness is production-grade for controlled internal validation, but the results are **not certified assurance** and are not independent real-world detection assurance.

## Source documents reviewed

- `docs/owasp-documents/OWASP-GenAI-COMPASS-RunBook-1.0.pdf` — reviewed for COMPASS/OODA workflow and framework alignment.
- `docs/owasp-documents/OWASP-GenAI-Data-Security-Risks-and-Mitigations-2026-v1.0.pdf` — confirms GenAI data-security categories `DSGAI01` through `DSGAI21` in the visible table of contents.
- existing VulnoraIQ `docs/owasp/` LLM implementation specs
- `docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`

## Source note

The GenAI Data Security document's narrative text references a `DSGAI01–DSGAI25` taxonomy, while the accessible table of contents confirms `DSGAI01–DSGAI21`. VulnoraIQ tracks `DSGAI01–DSGAI21` as source-confirmed and keeps `DSGAI22–DSGAI25` open in `benchmarks/fixtures/genai/scenarios.yaml` until a complete extracted source list is available.

## Implemented GenAI readiness assets

| Asset | Status | Purpose |
| --- | --- | --- |
| [`PRODUCTION_READINESS_PLAN.md`](PRODUCTION_READINESS_PLAN.md) | Complete | Phase-by-phase GenAI Security readiness plan and completion decision. |
| `benchmarks/fixtures/genai/scenarios.yaml` | Production-grade scenario harness | v2 matrix generating 84 concrete scenario cases across `DSGAI01–DSGAI21` and secure/vulnerable/ambiguous/edge-case fixtures. |
| `core/genai_evaluators.py` | Production harness evaluators | Deterministic evaluator primitives, confidence-floor checks, acceptance criteria checks, and aggregate result handling. |
| `scripts/validate_genai_readiness.py` | Controlled-internal release gate | Validates GenAI source coverage, fixture matrix, evidence contract, confidence floors, source discrepancy tracking, docs status, and MITRE ATLAS tactic format. |
| `tests/test_genai_readiness_validation.py` | CI gate | Regression tests for the production-grade scenario harness validator and evaluator behaviour. |

## Production-grade scenario harness

The GenAI harness now requires:

- `21` source-confirmed GenAI categories.
- `4` required fixture types per category: `secure`, `vulnerable`, `ambiguous`, and `edge_case`.
- `84 concrete scenario cases` generated from the category × fixture matrix.
- `genai-production-v2` evidence contract.
- confidence floors for scenario evaluation.
- high/critical severity requirement for vulnerable production cases.
- required manual review for every GenAI result.
- safe synthetic fixture enforcement for CI.
- explicit real-world validation requirement so the repo cannot overclaim independent assurance.

## Confirmed GenAI data-security coverage areas

| OWASP ID | GenAI data-security risk | Current status | Primary evidence surfaces |
| --- | --- | --- | --- |
| DSGAI01 | Sensitive Data Leakage | Production harness | prompt |
| DSGAI02 | Agent Identity & Credential Exposure | Production harness | tool trace |
| DSGAI03 | Shadow AI & Unsanctioned Data Flows | Production harness | provider metadata |
| DSGAI04 | Data, Model & Artifact Poisoning | Production harness | retrieval |
| DSGAI05 | Data Integrity & Validation Failures | Production harness | report |
| DSGAI06 | Tool, Plugin & Agent Data Exchange Risks | Production harness | tool trace |
| DSGAI07 | Data Governance, Lifecycle & Classification for AI Systems | Production harness | provider metadata |
| DSGAI08 | Non-Compliance & Regulatory Violations | Production harness | provider metadata |
| DSGAI09 | Multimodal Capture & Cross-Channel Data Leakage | Production harness | multimodal input |
| DSGAI10 | Synthetic Data, Anonymization & Transformation Pitfalls | Production harness | report |
| DSGAI11 | Cross-Context & Multi-User Conversation Bleed | Production harness | memory |
| DSGAI12 | Unsafe Natural-Language Data Gateways (LLM-to-SQL/Graph) | Production harness | tool trace |
| DSGAI13 | Vector Store Platform Data Security | Production harness | vector store |
| DSGAI14 | Excessive Telemetry & Monitoring Leakage | Production harness | log |
| DSGAI15 | Over-Broad Context Windows & Prompt Over-Sharing | Production harness | prompt |
| DSGAI16 | Endpoint & Browser Assistant Overreach | Production harness | tool trace |
| DSGAI17 | Data Availability & Resilience Failures in AI Pipelines | Production harness | report |
| DSGAI18 | Inference & Data Reconstruction | Production harness | model artifact |
| DSGAI19 | Human-in-the-Loop & Labeler Overexposure | Production harness | provider metadata |
| DSGAI20 | Model Exfiltration & IP Replication | Production harness | model artifact |
| DSGAI21 | Disinformation & Integrity Attacks via Data Poisoning | Production harness | retrieval |

## Validation

```bash
python scripts/validate_genai_readiness.py
pytest tests/test_genai_readiness_validation.py -q
python scripts/validate_package_metadata.py
```

## Files

- [`PRODUCTION_READINESS_PLAN.md`](PRODUCTION_READINESS_PLAN.md) — completed phased implementation plan
- `benchmarks/fixtures/genai/scenarios.yaml` — production-grade controlled-internal scenario harness
- `core/genai_evaluators.py` — deterministic GenAI evaluator suite
- `scripts/validate_genai_readiness.py` — CI/release validator
- [`../owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`](../owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md) — OWASP/GenAI/Agentic to MITRE ATLAS mapping

## Remaining future work

The scenario harness is production-grade for controlled internal validation. Future work should validate it against authorised real environments, integrate report/dashboard GenAI widgets, add provider inventory connectors, add SIEM/SOAR mappings, and obtain independent assurance before external claims.
