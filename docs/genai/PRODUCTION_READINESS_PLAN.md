# GenAI Security Production Readiness Plan

**Plan status:** Completed for `0.2.0` controlled internal enterprise deployment.

**Scope:** GenAI data-security and governance assessment readiness for authorised internal LLM, RAG, vector-store, provider, tool, telemetry, multimodal, and model-artifact assessments.

**Readiness claim:** VulnoraIQ has a **working-starter GenAI Security production-readiness gate** for controlled internal assessment use. This means source-confirmed DSGAI coverage is represented by safe synthetic scenario manifests, deterministic evaluator composition, documented evidence requirements, and CI validation. It does **not** mean production-validated detection assurance, public internet readiness, multi-tenant SaaS readiness, or certified VAPT-grade assurance.

**Production boundary:** public internet / SaaS hardening remains deferred. Use GenAI results as framework evidence requiring human review.

## Source-confirmed baseline

VulnoraIQ tracks the OWASP GenAI Data Security categories `DSGAI01–DSGAI21` from the reviewed source material.

> **Source discrepancy:** the GenAI document narrative references `DSGAI01–DSGAI25`, while the accessible table of contents confirms `DSGAI01–DSGAI21`. `DSGAI22–DSGAI25` remain explicitly preserved as unresolved source discrepancy / map-later items in `benchmarks/fixtures/genai/scenarios.yaml`.

## Phase status

| Phase | Area | Status | Release gate |
| --- | --- | --- | --- |
| GENAI-0 | Boundary and source confirmation | Complete | Docs preserve the `DSGAI01–DSGAI21` source-confirmed range and the `DSGAI22–DSGAI25` discrepancy. |
| GENAI-1 | Scenario manifests | Complete | `benchmarks/fixtures/genai/scenarios.yaml` covers `DSGAI01–DSGAI21` with secure, vulnerable, ambiguous, and edge-case fixture coverage. |
| GENAI-2 | Evaluator composition | Complete | `core/genai_evaluators.py` provides deterministic safe-fixture evaluators for restricted markers, evidence fields, data classification, data surfaces, context windows, and scenario expectations. |
| GENAI-3 | Evidence schema contract | Complete | GenAI scenarios require `genai_id`, `genai_risk_area`, `data_classification`, `data_surface`, `redaction_status`, `manual_review_reason`, and `mitre_atlas_tactics`. |
| GENAI-4 | Reports and dashboard language | Complete | The plan and README define what findings prove, do not prove, and when human review is required. |
| GENAI-5 | COMPASS workflow integration | Complete | Observe, Orient, Decide, Act workflow is mapped to VulnoraIQ inventory, mapping, prioritisation, and report/retest actions. |
| GENAI-6 | CI and release gates | Complete | `scripts/validate_genai_readiness.py`, tests, and both CI workflows validate GenAI scenario/docs readiness. |
| GENAI-7 | Public/SaaS hardening | Deferred | Requires tenant isolation, external assurance, SIEM/SOAR integration, SLOs, public ingress protection, and stronger identity/governance integrations. |

## Category coverage

| OWASP ID | Category | Working-starter focus |
| --- | --- | --- |
| DSGAI01 | Sensitive Data Leakage | Synthetic marker leakage across prompt, response, log, and report surfaces. |
| DSGAI02 | Agent Identity & Credential Exposure | Scoped vs over-scoped agent credential evidence and credential-bearing traces. |
| DSGAI03 | Shadow AI & Unsanctioned Data Flows | Sanctioned provider evidence, unknown provider routing, and unsanctioned upload/data-flow indicators. |
| DSGAI04 | Data, Model & Artifact Poisoning | Source, corpus, model, and artifact integrity indicators. |
| DSGAI05 | Data Integrity & Validation Failures | Schema, freshness, provenance, and transformation-review indicators. |
| DSGAI06 | Tool, Plugin & Agent Data Exchange Risks | Connector/tool trace boundaries and data-flow evidence. |
| DSGAI07 | Data Governance, Lifecycle & Classification for AI Systems | Classification, lineage, retention, deletion, and approval evidence. |
| DSGAI08 | Non-Compliance & Regulatory Violations | Residency, legal-basis, retention, and regulated-data review routing. |
| DSGAI09 | Multimodal Capture & Cross-Channel Data Leakage | Synthetic multimodal privacy and cross-channel leakage indicators. |
| DSGAI10 | Synthetic Data, Anonymization & Transformation Pitfalls | Transformation, re-identification, and membership-risk review signals. |
| DSGAI11 | Cross-Context & Multi-User Conversation Bleed | Session, memory, tenant/user boundary, and cache-bleed indicators. |
| DSGAI12 | Unsafe Natural-Language Data Gateways (LLM-to-SQL/Graph) | Generated query, schema allowlist, and excessive access indicators. |
| DSGAI13 | Vector Store Platform Data Security | Vector ACL, scope, import, poisoning, and embedding leakage indicators. |
| DSGAI14 | Excessive Telemetry & Monitoring Leakage | Audit/log/trace/report leakage indicators. |
| DSGAI15 | Over-Broad Context Windows & Prompt Over-Sharing | Context minimisation and trust-domain separation indicators. |
| DSGAI16 | Endpoint & Browser Assistant Overreach | Endpoint/browser permission and local context exposure indicators. |
| DSGAI17 | Data Availability & Resilience Failures in AI Pipelines | Stale index, failed restore, corrupt pipeline, and availability indicators. |
| DSGAI18 | Inference & Data Reconstruction | Reconstruction and membership-inference-safe probes requiring review. |
| DSGAI19 | Human-in-the-Loop & Labeler Overexposure | Label queue masking, reviewer minimisation, and overexposure indicators. |
| DSGAI20 | Model Exfiltration & IP Replication | Model artifact, access log, and extraction-probe indicators. |
| DSGAI21 | Disinformation & Integrity Attacks via Data Poisoning | Poisoned corpus and unsupported high-impact claim indicators. |

## Phase GENAI-1: Scenario manifests

Implemented controls:

- `benchmarks/fixtures/genai/scenarios.yaml` provides machine-readable GenAI coverage.
- Every source-confirmed `DSGAI01–DSGAI21` category is represented.
- Every category records coverage for secure, vulnerable, ambiguous, and edge-case fixtures.
- Every scenario records data classification, data surface, required evidence fields, MITRE ATLAS tactic mapping, and manual-review requirement.
- `DSGAI22–DSGAI25` remain preserved as source-discrepancy items, not silently dropped.

Gate:

```bash
python scripts/validate_genai_readiness.py --manifest benchmarks/fixtures/genai/scenarios.yaml
```

## Phase GENAI-2: Evaluator composition

Implemented controls:

- `core/genai_evaluators.py` includes deterministic evaluator primitives for:
  - synthetic restricted-marker leakage,
  - data-classification metadata,
  - data-surface metadata,
  - required evidence fields,
  - context-window minimisation,
  - fixture expectation handling.
- Evaluator output includes status, confidence, reason, evidence fields, false-positive notes, and manual-review flag.

Gate:

```bash
pytest tests/test_genai_readiness_validation.py -q
```

## Phase GENAI-3: Evidence schema contract

Required GenAI evidence fields:

- `genai_id`
- `genai_risk_area`
- `data_classification`
- `data_surface`
- `redaction_status`
- `manual_review_reason`
- `mitre_atlas_tactics`

The validator fails if scenario coverage omits these fields.

## Phase GENAI-4: Reports and dashboards

GenAI findings must be described as framework evidence. Reports and dashboards must state:

- what data surface was assessed,
- whether only a synthetic marker was observed,
- whether real sensitive data was observed or not assessed,
- which evidence fields support the finding,
- why human review is required,
- what the result does not prove.

## Phase GENAI-5: COMPASS workflow integration

| COMPASS phase | VulnoraIQ implementation |
| --- | --- |
| Observe | Inventory providers, prompts, data stores, vector stores, tools, logs, reports, and model artifacts. |
| Orient | Map observed surfaces to OWASP LLM, DSGAI, Agentic ASI, MITRE ATLAS, and known control gaps. |
| Decide | Select safe synthetic GenAI scenario suites and prioritise remediation or retest actions. |
| Act | Generate report evidence, create backlog items, retest after mitigation, and preserve manual-review notes. |

## Phase GENAI-6: CI and release gates

Implemented gates:

- `scripts/validate_genai_readiness.py`
- `tests/test_genai_readiness_validation.py`
- `vulnoraiq-validate-genai-readiness` console entry point
- CI workflow step in `.github/workflows/ci.yml`
- CI workflow step in `.github/workflows/python-ci.yml`
- release checklist command and acceptance criteria

Release candidate gate:

```bash
python -m pip install -e .[dev]
ruff check .
mypy .
pytest -q
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py
```

## Deferred Phase GENAI-7: Public/SaaS hardening

Required before public/SaaS claims:

- tenant isolation for GenAI data stores, vector indexes, reports, and reviewer queues,
- OIDC/SSO or equivalent enterprise identity integration,
- SIEM/SOAR integration and alert rules,
- shared rate/session/CSRF state for multi-instance deployment,
- public ingress/WAF/CDN/DDoS reference architecture,
- performance and resilience testing for GenAI data pipelines,
- independent security assessment or penetration test,
- approved assurance wording for external reports.

## Completion decision

**Completed for `0.2.0` controlled internal enterprise GenAI Security readiness.** Phases GENAI-0 through GENAI-6 are implemented, documented, and backed by repository checks or CI gates. Public internet / SaaS hardening remains deferred and out of scope.
