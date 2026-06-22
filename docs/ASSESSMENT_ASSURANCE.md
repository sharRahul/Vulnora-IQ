# Assessment Assurance

This document separates scanner/evaluator assurance from platform production readiness. It clarifies what VulnoraIQ findings represent today, what evidence is collected, what limitations apply, and what is required before external VAPT-grade claims can be made.

---

## 1. What VulnoraIQ Findings Mean Today

- **Findings are framework-development evidence**, not validated security assurance. They indicate that a configured check triggered on observed interaction data under local or authorised target conditions.
- **No third-party penetration test has been performed** on any target through this framework. No external VAPT firm has reviewed the check logic, evaluator thresholds, or output claims.
- **OWASP LLM 2025 coverage** has implementation specs, safe starter oracle coverage, and local good/bad fixtures for all 10 categories. This is sufficient for development regression testing and internal exploration but is **not VAPT-grade** detection.
- Results should be treated as **experimental indicators** that require human review before any risk conclusion is drawn.

---

## 2. OWASP LLM Categories and Current Coverage

| OWASP ID | Risk | Check type | Heuristic vs Deterministic | Requires human review |
|---|---|---|---|---|
| LLM01:2025 | Prompt Injection | Oracle + evaluator | Deterministic (local fixtures), heuristic (production oracle) | Yes — ambiguous injection boundaries |
| LLM02:2025 | Sensitive Information Disclosure | Pattern matching + oracle | Deterministic (known patterns), heuristic (context leakage) | Yes — false-positive prone on benign content |
| LLM03:2025 | Supply Chain | Inventory scan + oracle | Deterministic (dependency lists), heuristic (provenance) | Yes — provenance claims require manual verification |
| LLM04:2025 | Data and Model Poisoning | Integrity check + oracle | Heuristic | Yes — no single deterministic signal |
| LLM05:2025 | Improper Output Handling | Output schema check + oracle | Deterministic (schema violations), heuristic (downstream risk) | Yes — business context needed |
| LLM06:2025 | Excessive Agency | Tool permission analysis + oracle | Deterministic (allowlist violations), heuristic (autonomy risk) | Yes — agency risk is context-dependent |
| LLM07:2025 | System Prompt Leakage | Prompt segment scan + oracle | Deterministic (known markers), heuristic (inferred leakage) | Yes — leakage requires confirmation |
| LLM08:2025 | Vector and Embedding Weaknesses | Retrieval analysis + oracle | Heuristic | Yes — retrieval manipulation is hard to detect automatically |
| LLM09:2025 | Misinformation | Citation check + oracle | Heuristic | Yes — factuality requires subject-matter review |
| LLM10:2025 | Unbounded Consumption | Resource limit check + oracle | Deterministic (threshold violations), heuristic (resource exhaustion risk) | Yes — thresholds are application-specific |

### Coverage notes

- All 10 categories have **safe starter oracle coverage** in `config/owasp_oracles.yaml`.
- All 10 categories have **implementation specs** in `docs/owasp/`.
- All 10 categories have **local good/bad fixture targets** in `examples/local_demo_targets/owasp_fixture_targets.py`.
- CI validates that oracles, docs, and fixtures are present, but does not validate detection depth against real-world attack surfaces.

---

## 3. Evidence Collected

### Collected

- **InteractionEvidence** records — per-request/response observations from target interactions.
- **OracleResult** evaluations — output of oracle checks applied to interaction evidence.
- **Policy engine decisions** — policy evaluation results that produce findings and scores.
- **Scan metadata** — profile, module, detector, and confidence data attached to each finding.
- **Dashboard and report artifacts** — Markdown, JSON, SARIF, and HTML export bundles.

### NOT collected

- Full request/response bodies are not persisted beyond the scan context except as structured evidence fields.
- Secrets, tokens, API keys, or credentials are never written to evidence or report output.
- Personally identifiable information (PII) present in target responses is not explicitly collected, but no automated redaction is performed — human review of raw evidence is required before sharing.
- System-level access logs, network captures, or host telemetry are outside the framework's scope.

---

## 4. Limitations of Local Fixtures

- **Synthetic targets** — the local good/bad fixtures model controlled behaviours and are not real AI applications. They are designed to exercise oracle and evaluator logic, not to reflect real-world deployment complexity.
- **May not reflect real-world attack surfaces** — a fixture that passes local checks may still miss vectors present in production LLM stacks (RAG pipelines, plugin ecosystems, agent tool chains, authentication layers).
- **Useful for development and regression testing** — fixtures ensure that oracles and evaluators behave as expected during development and CI. Passing local fixture tests does **not** imply production-grade detection.

---

## 5. False Positive / False Negative Expectations

- **Starter-level checks may produce false positives.** Heuristic oracles and simple pattern matchers will flag benign content as suspicious in some cases.
- **Not all attack paths are covered.** The current check set is limited to the scenarios defined in the OWASP implementation specs. Real-world attackers will use techniques not represented in those scenarios.
- **False negatives are expected** for sub-techniques that lack oracle rules, evaluator support, or scenario coverage.
- **Human review is required** before treating any finding as a confirmed vulnerability or risk. Findings are starting points for investigation, not conclusions.

---

## 6. Requirements Before External VAPT-Grade Claims

Before VulnoraIQ output can be represented as VAPT-grade security assurance, the following must be addressed:

1. **Deeper check logic per OWASP category** — category-specific evaluator composition, multi-signal detection, and coverage of ambiguous and edge-case scenarios as defined in each `docs/owasp/LLM*` spec.
2. **Third-party penetration testing** — an independent VAPT firm must review the framework's detection capability against real targets and confirm that findings map to genuine security risk.
3. **Calibrated evaluator thresholds** — confidence, severity, and risk-score thresholds must be benchmarked against known-good and known-vulnerable targets to minimise false positives and false negatives.
4. **Real-world fixture validation** — fixture targets must include ambiguous, adversarial, and production-mimicking scenarios beyond the current local good/bad pair.
5. **Report language maturity review** — finding descriptions, remediation guidance, and limitation statements must be reviewed by security communications professionals to ensure they do not overstate assurance or understate risk.

---

## 7. Mapping Between OWASP/MITRE and Implemented Checks

### OWASP reference

- Full OWASP LLM 2025 implementation specs are in [`docs/owasp/`](owasp/README.md).
- Each `LLM*` document defines scope, payload strategy, expected behaviour, evidence fields, evaluator rules, severity rationale, and false-positive/false-negative notes.
- Oracle definitions reside in `config/owasp_oracles.yaml`.

### MITRE ATLAS reference

- The MITRE ATLAS AI technique planning matrix is in [`docs/MITRE_ATLAS_AI_MATRIX.md`](MITRE_ATLAS_AI_MATRIX.md).
- An initial OWASP-to-MITRE mapping is documented in [`docs/mitre-atlas-mapping.md`](mitre-atlas-mapping.md).

### Detection coverage status

| ATLAS tactic area | OWASP mapping | Detection vs Planning |
|---|---|---|
| Reconnaissance / discovery | LLM02, LLM08 | Planning — candidate mapping, no active oracle |
| Resource development / supply chain | LLM03 | Active — starter oracle, dependency inventory |
| Initial access / prompt injection | LLM01, LLM07 | Active — starter oracle, direct/indirect probe support |
| Execution / output handling, agency | LLM05, LLM06 | Active — schema and permission checks (starter) |
| Persistence / poisoning | LLM04, LLM06 | Planning — integrity check oracle exists, no active poisoning detection |
| Defense evasion / prompt leakage | LLM01, LLM07 | Active — prompt segment scan (starter) |
| Collection / sensitive disclosure | LLM02, LLM08 | Active — pattern-based leakage check (starter) |
| Exfiltration | LLM02, LLM06 | Planning — no active exfiltration detection |
| Impact / misinformation, consumption | LLM05, LLM09, LLM10 | Active — citation and resource-limit checks (starter) |
| Privilege escalation / credential access | LLM06, LLM02 | Planning — no active escalation detection |
| Command and control / lateral movement | LLM06 | Planning — no active C2 or movement detection |

> **Note:** "Planning" entries in the table above indicate that the MITRE technique is mapped to an OWASP category in documentation but does not yet have an active oracle rule or evaluator check. Active detection is at starter level and has not been validated against real attack scenarios.
