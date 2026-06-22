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

## Maturity rule

A category remains `Working starter` until all of the following are true:

1. Safe secure and vulnerable fixtures exist.
2. Evaluators detect the vulnerable fixture and do not flag the secure fixture.
3. Findings include structured evidence and confidence.
4. CI validates the behaviour.
5. Operator documentation explains how to interpret output.

## Category files

| OWASP ID | File | Current status |
| --- | --- | --- |
| LLM01:2025 | `LLM01_PROMPT_INJECTION.md` | Working-alpha spec |
| LLM02:2025 | `LLM02_SENSITIVE_INFORMATION_DISCLOSURE.md` | Working-alpha spec |
| LLM03:2025 | `LLM03_SUPPLY_CHAIN.md` | Working-alpha spec |
| LLM04:2025 | `LLM04_DATA_AND_MODEL_POISONING.md` | Working-alpha spec |
| LLM05:2025 | `LLM05_IMPROPER_OUTPUT_HANDLING.md` | Working-alpha spec |
| LLM06:2025 | `LLM06_EXCESSIVE_AGENCY.md` | Working-alpha spec |
| LLM07:2025 | `LLM07_SYSTEM_PROMPT_LEAKAGE.md` | Working-alpha spec |
| LLM08:2025 | `LLM08_VECTOR_AND_EMBEDDING_WEAKNESSES.md` | Working-alpha spec |
| LLM09:2025 | `LLM09_MISINFORMATION.md` | Working-alpha spec |
| LLM10:2025 | `LLM10_UNBOUNDED_CONSUMPTION.md` | Working-alpha spec |

## Next planning pass

After this implementation pass, use these documents to decide the deeper OWASP-specific payloads, fixtures, evaluator thresholds, and report language needed before real-world VAPT readiness is claimed.
