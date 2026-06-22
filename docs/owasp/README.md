# OWASP LLM 2025 Implementation Plan

This folder is the bridge from **working starter** to **working** for VulnoraIQ.

Each OWASP file defines:

- assessment scope
- safe local payload strategy
- secure expected behaviour
- vulnerable expected behaviour
- evidence fields
- evaluator rules
- severity rationale
- false-positive and false-negative notes
- criteria before the category can be marked `Working`

## Production-readiness planning document

Use `PRODUCTION_READINESS_PLAN.md` as the controlling implementation plan for moving OWASP coverage from starter documentation to production-ready candidate capability.

That plan defines:

- maturity ladder from `Working-alpha starter` to `Production-ready`
- cross-category implementation phases
- scenario manifest requirements
- evaluator expansion requirements
- structured evidence expansion
- category benchmark gates
- report language and operator workflow requirements
- production-safety gates
- immediate implementation backlog

## Current baseline pulled from repo implementation

Current starter implementation exists in:

| Area | Repo path | Current purpose |
| --- | --- | --- |
| OWASP oracle definitions | `config/owasp_oracles.yaml` | Safe starter signals and required evidence fields. |
| Local evaluator primitives | `core/evaluators.py` | Deterministic checks for local fixtures and CI. |
| Local good/bad fixture target | `examples/local_demo_targets/owasp_fixture_targets.py` | Safe local fixture behaviour for all 10 categories. |
| Scanner/report path | `core/`, `reports/`, `dashboards/` | Structured findings, oracle evidence, reports, and dashboards. |
| Release gate | `scripts/validate_package_metadata.py` | Checks docs, package metadata, fixtures, evaluator suite, matrix docs, and notices. |

## Maturity rule

A category remains `Working-alpha starter` until all of the following are true:

1. Safe secure and vulnerable fixtures exist.
2. Evaluators detect the vulnerable fixture and do not flag the secure fixture.
3. Findings include structured evidence and confidence.
4. CI validates the behaviour.
5. Operator documentation explains how to interpret output.

A category should not be marked `Working` until it also has:

1. secure, vulnerable, ambiguous, and edge-case scenario coverage
2. category-specific evaluator composition
3. benchmark regression thresholds
4. false-positive and false-negative examples
5. report language suitable for VAPT evidence review
6. explicit limitations and manual-review guidance
7. target contract requirements for any required trace evidence

## Category files

| OWASP ID | File | Current status | Next documentation/action focus |
| --- | --- | --- | --- |
| LLM01:2025 | `LLM01_PROMPT_INJECTION.md` | Working-alpha spec | Add multi-surface prompt boundary scenarios and direct/indirect/triggered classification. |
| LLM02:2025 | `LLM02_SENSITIVE_INFORMATION_DISCLOSURE.md` | Working-alpha spec | Add report artifact scanning, redaction policy, and evidence minimisation. |
| LLM03:2025 | `LLM03_SUPPLY_CHAIN.md` | Working-alpha spec | Add component inventory manifests and provenance validation rules. |
| LLM04:2025 | `LLM04_DATA_AND_MODEL_POISONING.md` | Working-alpha spec | Add corpus/model integrity drift and source trust scenarios. |
| LLM05:2025 | `LLM05_IMPROPER_OUTPUT_HANDLING.md` | Working-alpha spec | Add schema/handoff policies and downstream consumer simulation. |
| LLM06:2025 | `LLM06_EXCESSIVE_AGENCY.md` | Working-alpha spec | Add tool, memory, approval, rollback, and audit evidence plans. |
| LLM07:2025 | `LLM07_SYSTEM_PROMPT_LEAKAGE.md` | Working-alpha spec | Add prompt segment classification and protected marker artifact scanning. |
| LLM08:2025 | `LLM08_VECTOR_AND_EMBEDDING_WEAKNESSES.md` | Working-alpha spec | Add retrieval scenario manifests, source trust scoring, and metadata filters. |
| LLM09:2025 | `LLM09_MISINFORMATION.md` | Working-alpha spec | Add claim-level support mapping and unsupported claim confidence rules. |
| LLM10:2025 | `LLM10_UNBOUNDED_CONSUMPTION.md` | Working-alpha spec | Add token, timeout, retry, iteration, cost, fan-out, and agent-loop budgets. |

## Implementation order recommendation

1. **Evidence and schema foundation:** expand result/report fields before adding more checks.
2. **Scenario manifests:** add category manifests with secure, vulnerable, ambiguous, and edge-case rows.
3. **Evaluator composition:** build category-specific evaluator decisions from existing primitives.
4. **Report language:** add operator-facing meaning, limitation, and remediation text.
5. **Benchmark and CI gates:** fail on missed vulnerable fixtures, noisy secure fixtures, and missing evidence.
6. **Adapter contracts:** require model, retrieval, tool, memory, and artifact traces where relevant.
7. **Production-candidate review:** only after repeated authorised validation and maintainer review.

## Next planning pass

After this documentation pass, use `PRODUCTION_READINESS_PLAN.md` and the 10 category docs to select the first implementation batch for production-readiness work. The safest first batch is:

1. report/evidence schema expansion
2. OWASP scenario manifest loader
3. category evaluator composition
4. artifact scanning for restricted/protected placeholders
5. HTML dashboard OWASP coverage view
