> Moved to `docs/ready-to-remove/` during the documentation cleanup on 2026-06-28. Review and delete if the active AITG integration/status docs cover everything still needed.

# OWASP AI Testing Guide implementation plan

## Current status

VulnoraIQ currently implements an **OWASP AI Testing Guide foundation path**: safe methodology profiles, payloads, target adapters, Docker mock-agent targets, WebUI/CLI execution, reports, and readiness documentation.

The full OWASP AI Testing Guide implementation remains a roadmap item. This plan tracks the work needed to move from current foundation coverage to runnable, evidence-producing coverage for the full AITG test case set.

## Purpose

Turn the OWASP AI Testing Guide into first-class VulnoraIQ coverage that can test authorised live AI applications, Docker-hosted agents, model-facing endpoints, RAG systems, tool-using agents, AI infrastructure controls, and AI data controls.

## Source basis

Reviewed source observations:

- The guide provides a structured methodology for AI system testing across reliability, security, and ethical alignment.
- It consolidates sources including OWASP GenAI Red Teaming Guide, CSA Agentic AI Red Teaming Guide, OWASP AI Exchange, OWASP AI Security and Privacy Guide, OWASP Top 10 for LLM, OWASP AI VSS, and NIST AI 100-2 E2025.
- The framework is organised under four pillars:
  - AI Application Testing
  - AI Model Testing
  - AI Infrastructure Testing
  - AI Data Testing
- The roadmap baseline tracks 32 test cases:
  - `AITG-APP-01` through `AITG-APP-14`
  - `AITG-MOD-01` through `AITG-MOD-07`
  - `AITG-INF-01` through `AITG-INF-06`
  - `AITG-DAT-01` through `AITG-DAT-05`
- Better assurance often requires grey-box or white-box evidence such as logs, prompts, architecture, source code, third-party service configuration, guardrail configuration, token/cost thresholds, and model/service administration information.

## Already implemented

| Capability | Status |
| --- | --- |
| `ai_testing_guide_foundation` profile | Complete for current methodology-harness scope. |
| Safe AI Testing Guide payload library | Complete for current scope. |
| Local/Docker target adapter execution | Complete for current local/internal scope. |
| Docker mock-agent contracts | Complete for deterministic local lab use. |
| WebUI profile selection | Complete through React console catalogue/target workflow. |
| CLI execution | Complete through `vulnoraiq scan ...`. |
| Documentation | Current integration docs and roadmap maintained. |

## Full implementation roadmap

| Phase | Outcome | Status |
| --- | --- | --- |
| AITG-1 | Normalised 32-test manifest with IDs, pillar, required evidence, target type, and expected output contract. | Planned |
| AITG-2 | Runtime modules for `APP`, `MOD`, `INF`, and `DAT` suites. | Planned |
| AITG-3 | Evidence schema for black-box, grey-box, and white-box modes. | Planned |
| AITG-4 | Docker fixtures and approved local mock targets for representative AITG tests. | Planned |
| AITG-5 | WebUI suite grouping, single-test selection, and report enrichment. | Planned |
| AITG-6 | CI validator for manifest completeness and docs alignment. | Planned |
| AITG-7 | Approved-environment validation and assurance calibration. | Future maturity |

## Required evidence fields

Each full AITG test should define:

- test ID and pillar;
- target type;
- required authorisation statement;
- input payload contract;
- required target/evidence context;
- expected safe/vulnerable/ambiguous result patterns;
- evaluator/oracle used;
- false-positive/false-negative notes;
- manual-review requirement;
- report wording and assurance boundary.

## WebUI requirements

The React console should expose:

- pillar filters;
- suite-level and single-test execution;
- target compatibility warnings;
- required evidence checklist;
- clear black-box/grey-box/white-box distinction;
- report language that avoids overclaiming.

## Safety boundary

Full AITG coverage must remain authorised-use only. Tests must not request destructive behaviour, credential exposure, unauthorised access, or external third-party assessment. Where a test requires privileged evidence, the UI and CLI must require the assessor to provide that evidence explicitly.

## Completion definition

This plan is complete only when all 32 test IDs have manifest entries, runnable modules or explicit non-runnable/manual status, tests, report integration, WebUI visibility, documentation, and CI validation.

## Implementation update

The canonical 32-test AITG manifest, `owasp-aitg-full` profile, scanner execution path, report evidence fields, and `scripts/validate_aitg_full_coverage.py` validator are implemented. Entries use original summary wording and safe fixtures rather than copying OWASP source text.
