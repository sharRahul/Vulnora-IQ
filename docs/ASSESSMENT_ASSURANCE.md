# Assessment Assurance

This document separates scanner/evaluator assurance from application production readiness. It clarifies what VulnoraIQ findings represent today, what evidence is collected, what limitations apply, and what is required before external VAPT-grade claims can be made.

---

## 1. What VulnoraIQ findings mean today

- **Findings are framework-development and internal assessment evidence**, not independently validated security assurance.
- **No third-party penetration test has validated the full framework output** against real targets.
- **OWASP LLM 2025 coverage** is complete for the current safe local/internal scope, with implementation specs, safe oracle coverage, and local good/bad fixtures for all 10 categories.
- **GenAI Security coverage** is complete for the current `DSGAI01–DSGAI21` controlled-internal scenario-harness scope, backed by safe synthetic scenario manifests, deterministic evaluator primitives, required evidence fields, tests, and CI validation.
- **Agentic Applications readiness** is complete for the self-hosted internal application gates, but not certified assurance.
- Results should be treated as **structured internal evidence** that requires human review before any risk conclusion is drawn.

---

## 2. OWASP LLM categories and current coverage

| OWASP ID | Risk | Check type | Heuristic vs deterministic | Requires human review |
|---|---|---|---|---|
| LLM01:2025 | Prompt Injection | Oracle + evaluator | Deterministic local fixtures, heuristic production oracle | Yes |
| LLM02:2025 | Sensitive Information Disclosure | Pattern matching + oracle | Deterministic known patterns, heuristic context leakage | Yes |
| LLM03:2025 | Supply Chain | Inventory scan + oracle | Deterministic dependency lists, heuristic provenance | Yes |
| LLM04:2025 | Data and Model Poisoning | Integrity check + oracle | Heuristic | Yes |
| LLM05:2025 | Improper Output Handling | Output schema check + oracle | Deterministic schema violations, heuristic downstream risk | Yes |
| LLM06:2025 | Excessive Agency | Tool permission analysis + oracle | Deterministic allowlist violations, heuristic autonomy risk | Yes |
| LLM07:2025 | System Prompt Leakage | Prompt segment scan + oracle | Deterministic known markers, heuristic inferred leakage | Yes |
| LLM08:2025 | Vector and Embedding Weaknesses | Retrieval analysis + oracle | Heuristic | Yes |
| LLM09:2025 | Misinformation | Citation check + oracle | Heuristic | Yes |
| LLM10:2025 | Unbounded Consumption | Resource limit check + oracle | Deterministic threshold violations, heuristic resource risk | Yes |

### OWASP coverage notes

- All 10 categories have **complete safe oracle coverage** in `config/owasp_oracles.yaml` for the current local/internal scope.
- All 10 categories have **implementation specs** in `docs/owasp/`.
- All 10 categories have **local good/bad fixture targets** in `examples/local_demo_targets/owasp_fixture_targets.py`.
- CI validates that oracles, docs, fixtures, and mapping metadata are present, but does not validate detection depth against real-world environments.

---

## 3. GenAI Security categories and current coverage

| OWASP GenAI ID | Coverage status | Evidence basis | Requires human review |
| --- | --- | --- | --- |
| `DSGAI01–DSGAI21` | Complete for current scope | `benchmarks/fixtures/genai/scenarios.yaml`, `core/genai_evaluators.py`, `scripts/validate_genai_readiness.py`, `tests/test_genai_readiness_validation.py` | Yes |
| `DSGAI22–DSGAI25` | Source discrepancy / map later | Preserved in scenario manifest metadata | Yes |

### GenAI coverage notes

- GenAI coverage uses **safe synthetic scenario manifests**, not real sensitive data.
- The GenAI readiness validator checks scenario metadata, source-confirmed ID coverage, fixture coverage, required evidence fields, MITRE ATLAS tactic format, and documentation alignment.
- The evaluator suite detects synthetic restricted markers and validates evidence structure; it does not replace organisation-specific data discovery, DLP, legal review, privacy assessment, or independent testing.
- GenAI findings must state the assessed data surface and whether the result is based on synthetic markers or real evidence.

---

## 4. Evidence collected

### Collected

- **InteractionEvidence** records — per-request/response observations from target interactions.
- **OracleResult** evaluations — output of oracle checks applied to interaction evidence.
- **Policy engine decisions** — policy evaluation results that produce findings and scores.
- **Scan metadata** — profile, module, detector, and confidence data attached to each finding.
- **GenAI evidence metadata** — expected fields such as `genai_id`, `genai_risk_area`, `data_classification`, `data_surface`, `redaction_status`, `manual_review_reason`, and `mitre_atlas_tactics`.
- **Dashboard and report artifacts** — Markdown, JSON, SARIF, and HTML export bundles.

### NOT collected or not guaranteed

- Full request/response bodies are not intended to be persisted beyond controlled evidence fields.
- Secrets, tokens, API keys, or credentials must not be written to evidence or report output.
- Personally identifiable information present in target responses is not automatically safe to share; human review is required before sharing reports.
- System-level access logs, network captures, host telemetry, provider logs, and enterprise data-catalogue records are outside the default framework scope unless explicitly integrated.

---

## 5. Limitations of local and synthetic fixtures

- **Synthetic targets and manifests** exercise evaluator and validator logic; they are not real AI applications.
- **Safe GenAI fixtures** demonstrate expected evidence shape and control-gap signalling but may miss environment-specific provider, vector-store, telemetry, and governance failures.
- Passing local fixture tests does **not** imply production-grade detection.
- Passing GenAI readiness validation means the coverage manifest and docs are consistent; it does **not** prove every real GenAI data-security risk is detectable.

---

## 6. False positive / false negative expectations

- Current-scope checks may produce false positives.
- Not all attack or failure paths are covered.
- False negatives are expected for scenarios that lack oracle rules, evaluator support, real-world fixtures, or organisation-specific telemetry.
- Human review is required before treating any finding as a confirmed vulnerability or risk.

---

## 7. Requirements before external VAPT-grade claims

Before VulnoraIQ output can be represented as VAPT-grade or independently validated assurance, the following must be addressed:

1. **Deeper check logic per OWASP and GenAI category** — multi-signal detection, ambiguous/edge-case handling, and realistic scenario coverage.
2. **Third-party testing** — independent review of the framework, evaluator thresholds, and report language.
3. **Calibrated evaluator thresholds** — confidence, severity, and risk-score thresholds benchmarked against known-good and known-vulnerable targets.
4. **Approved environment validation** — authorised targets, provider configurations, RAG/vector stores, logs, and data-governance workflows.
5. **Report language maturity review** — finding descriptions, remediation guidance, and limitation statements must not overstate assurance.
6. **GenAI governance validation** — provider inventory, data classification, retention, privacy/legal review, and human-review workflows must be organisation-specific.

---

## 8. Mapping between OWASP/MITRE and implemented checks

### OWASP and GenAI references

- Full OWASP LLM 2025 implementation specs are in [`docs/owasp/`](owasp/README.md).
- GenAI Security readiness docs are in [`docs/genai/`](genai/README.md).
- Oracle definitions reside in `config/owasp_oracles.yaml`.
- GenAI scenario definitions reside in `benchmarks/fixtures/genai/scenarios.yaml`.

### MITRE ATLAS reference

- The MITRE ATLAS AI technique planning matrix is in [`docs/MITRE_ATLAS_AI_MATRIX.md`](MITRE_ATLAS_AI_MATRIX.md).
- An OWASP/GenAI/Agentic-to-MITRE mapping is documented in [`docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`](owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md).

### Detection coverage status

| Area | Detection vs planning |
|---|---|
| OWASP LLM safe local checks | Complete for current scope |
| OWASP/ATLAS mapping metadata | Complete CI governance check |
| GenAI `DSGAI01–DSGAI21` scenario coverage | Complete current-scope manifest and validator coverage |
| GenAI `DSGAI22–DSGAI25` | Source discrepancy / map later |
| Independent assurance | Future maturity item |

> **Note:** Current-scope coverage has not been independently validated against real-world targets. Use findings as structured evidence for internal review, not as final assurance conclusions.
