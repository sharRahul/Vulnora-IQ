# MITRE ATLAS Matrix for AI

This document is the VulnoraIQ planning matrix for MITRE ATLAS AI techniques. It is designed to help add ATLAS techniques into VulnoraIQ modules, payloads, fixtures, reports, and dashboards over time.

> **Current status:** planning and traceability document. The techniques below are not all implemented as active checks. Treat them as a roadmap and coverage register.

## Source alignment

The current local mapping source is defined in `config/mitre_atlas_mapping.yaml`:

- Source name: MITRE ATLAS
- Data repository: Straitcode/mitre-atlas-data
- ATLAS version: 5.6.0
- Data file: `dist/ATLAS.yaml`
- Validation date: 2026-06-22

## How to use this matrix

1. Add or refresh techniques in `config/mitre_atlas_mapping.yaml`.
2. Ensure every technique appears in this document.
3. Map each technique to one or more VulnoraIQ modules.
4. Add safe fixtures and deterministic evaluators.
5. Add report fields and dashboard coverage views.
6. Add CI tests before marking a technique as implemented.

## Matrix columns

| Column | Meaning |
| --- | --- |
| ATLAS technique | AML technique ID and name. |
| VulnoraIQ coverage area | Where the technique should eventually be implemented. |
| Current mapped module(s) | Current module names that reference the technique. |
| Implementation status | Current implementation state inside VulnoraIQ. |
| Next implementation work | What must be added before the technique can be treated as active coverage. |

## AI Supply Chain and Data Integrity

| ATLAS technique | VulnoraIQ coverage area | Current mapped module(s) | Implementation status | Next implementation work |
| --- | --- | --- | --- | --- |
| AML.T0010 — AI Supply Chain Compromise | Supply chain, model provenance, dataset provenance | `owasp_llm03_supply_chain` | Planned mapped coverage | Add model, dataset, package, and connector provenance fixtures. |
| AML.T0010.001 — AI Software | AI software package and runtime dependency provenance | `owasp_llm03_supply_chain` | Planned mapped coverage | Add safe dependency metadata fixture and package provenance evaluator. |
| AML.T0010.002 — Data | Training, fine-tuning, and retrieval data provenance | `owasp_llm03_supply_chain` | Planned mapped coverage | Add source approval, data owner, and lineage checks. |
| AML.T0019 — Publish Poisoned Datasets | Dataset supply-chain and corpus intake | `owasp_llm04_data_and_model_poisoning`, `corpus_validation` | Planned mapped coverage | Add safe poisoned-dataset metadata fixture and detection oracle. |
| AML.T0020 — Poison Training Data | Training-data integrity | `owasp_llm04_data_and_model_poisoning`, `corpus_validation` | Planned mapped coverage | Add local training-data manifest fixture and integrity evaluator. |
| AML.T0031 — Erode AI Model Integrity | Model integrity and drift | Unmapped planning backlog | Backlog | Add model-regression, drift, and confidence degradation test plan. |
| AML.T0058 — Publish Poisoned Models | Model artifact supply chain | `owasp_llm03_supply_chain` | Planned mapped coverage | Add local model-card provenance fixture and model artifact approval checks. |
| AML.T0059 — Erode Dataset Integrity | Dataset integrity and corpus trust | `owasp_llm04_data_and_model_poisoning`, `corpus_validation` | Planned mapped coverage | Add dataset delta, hash, freshness, and review checks. |

## Prompt, Instruction, and System Context Manipulation

| ATLAS technique | VulnoraIQ coverage area | Current mapped module(s) | Implementation status | Next implementation work |
| --- | --- | --- | --- | --- |
| AML.T0051 — LLM Prompt Injection | Prompt boundary testing | `owasp_llm01_prompt_injection`, `agent_chain_attack` | Starter oracle coverage | Add deeper safe direct and indirect prompt-boundary fixtures. |
| AML.T0051.000 — Direct | Direct prompt-boundary attempts | `owasp_llm01_prompt_injection` | Starter oracle coverage | Add direct user-channel fixture and evaluator-specific report fields. |
| AML.T0051.001 — Indirect | Indirect prompt-boundary attempts through retrieved or external content | `owasp_llm01_prompt_injection` | Starter oracle coverage | Add safe retrieved-content fixture and RAG interaction trace evidence. |
| AML.T0054 — LLM Jailbreak | Policy-boundary robustness | `owasp_llm06_excessive_agency`, `agent_chain_attack`, `multi_agent_abuse` | Planned mapped coverage | Add safe policy-boundary fixture and refusal-quality evaluator. |
| AML.T0056 — Extract LLM System Prompt | Protected instruction disclosure | `owasp_llm02_sensitive_information_disclosure`, `owasp_llm07_system_prompt_leakage` | Starter oracle coverage | Add protected-placeholder fixtures and artifact redaction checks. |
| AML.T0065 — LLM Prompt Crafting | Prompt attack preparation and prompt robustness | `owasp_llm01_prompt_injection` | Planned mapped coverage | Add prompt-variant corpus and evaluator confidence scoring. |
| AML.T0068 — LLM Prompt Obfuscation | Obfuscated prompt-boundary testing | `owasp_llm01_prompt_injection` | Planned mapped coverage | Add safe obfuscation fixtures without operational bypass content. |
| AML.T0069 — Discover LLM System Information | System information exposure | `owasp_llm02_sensitive_information_disclosure`, `owasp_llm07_system_prompt_leakage` | Planned mapped coverage | Add system-info placeholder fixture and disclosure evaluator. |
| AML.T0069.002 — System Prompt | System prompt discovery | `owasp_llm02_sensitive_information_disclosure`, `owasp_llm07_system_prompt_leakage` | Starter oracle coverage | Add system-prompt placeholder checks and report redaction proof. |

## RAG and Retrieval Manipulation

| ATLAS technique | VulnoraIQ coverage area | Current mapped module(s) | Implementation status | Next implementation work |
| --- | --- | --- | --- | --- |
| AML.T0064 — Gather RAG-Indexed Targets | RAG discovery and source exposure | `owasp_llm08_vector_embedding_weaknesses`, `rag_poisoning`, `retrieval_manipulation` | Working starter | Add retrieval-source inventory and access-boundary report fields. |
| AML.T0066 — Retrieval Content Crafting | RAG retrieval influence | `owasp_llm08_vector_embedding_weaknesses`, `rag_poisoning`, `retrieval_manipulation` | Working starter | Add crafted benign/misleading document fixtures and source trust thresholds. |
| AML.T0070 — RAG Poisoning | RAG corpus poisoning | `owasp_llm04_data_and_model_poisoning`, `owasp_llm08_vector_embedding_weaknesses`, `rag_poisoning`, `corpus_validation` | Working starter | Add poisoned-source metadata fixture and strict trust-score regression tests. |
| AML.T0071 — False RAG Entry Injection | False RAG entry handling | `owasp_llm08_vector_embedding_weaknesses`, `rag_poisoning` | Planned mapped coverage | Add false-entry fixture and provenance/citation evaluator. |

## Agent, Tool, and Multi-Agent Abuse

| ATLAS technique | VulnoraIQ coverage area | Current mapped module(s) | Implementation status | Next implementation work |
| --- | --- | --- | --- | --- |
| AML.T0053 — AI Agent Tool Invocation | Agent tool governance | `owasp_llm06_excessive_agency`, `agent_chain_attack`, `tool_execution_monitor`, `memory_tampering`, `multi_agent_abuse` | Working starter | Add per-tool approval, scope, and audit evidence fields. |
| AML.T0048 — External Harms | High-impact external action prevention | `owasp_llm05_improper_output_handling`, `multi_agent_abuse` | Planned mapped coverage | Add safe high-impact simulated handoff fixture and review gate. |

## Information Disclosure and Trust Manipulation

| ATLAS technique | VulnoraIQ coverage area | Current mapped module(s) | Implementation status | Next implementation work |
| --- | --- | --- | --- | --- |
| AML.T0057 — LLM Data Leakage | Sensitive information disclosure | `owasp_llm02_sensitive_information_disclosure`, `memory_tampering` | Starter oracle coverage | Add restricted-placeholder fixture and report artifact scanning. |
| AML.T0067 — LLM Trusted Output Components Manipulation | Output trust, citations, and presentation controls | `owasp_llm05_improper_output_handling`, `owasp_llm09_misinformation`, `retrieval_manipulation` | Planned mapped coverage | Add output component integrity evidence and citation quality checks. |
| AML.T0067.000 — Citations | Citation and source-trust controls | `owasp_llm05_improper_output_handling` | Planned mapped coverage | Add citation validator and source-to-claim traceability evidence. |

## Misinformation and Hallucination Operations

| ATLAS technique | VulnoraIQ coverage area | Current mapped module(s) | Implementation status | Next implementation work |
| --- | --- | --- | --- | --- |
| AML.T0060 — Publish Hallucinated Entities | Hallucinated entity abuse | `owasp_llm09_misinformation` | Planned mapped coverage | Add benign hallucinated-entity fixture and unsupported-claim evaluator. |
| AML.T0062 — Discover LLM Hallucinations | Hallucination discovery and exploitation planning | `owasp_llm09_misinformation` | Planned mapped coverage | Add unsupported-reference fixture and evidence-quality scoring. |

## Availability, Cost, and Resource Abuse

| ATLAS technique | VulnoraIQ coverage area | Current mapped module(s) | Implementation status | Next implementation work |
| --- | --- | --- | --- | --- |
| AML.T0029 — Denial of AI Service | Availability, timeouts, resource limits | `owasp_llm10_unbounded_consumption` | Planned mapped coverage | Add safe simulated resource-limit fixture; do not run load tests against real targets. |
| AML.T0034 — Cost Harvesting | Cost controls and budget limits | `owasp_llm10_unbounded_consumption` | Planned mapped coverage | Add token/cost budget evidence and alerting thresholds. |
| AML.T0046 — Spamming AI System with Chaff Data | Review fatigue and excessive event handling | `owasp_llm10_unbounded_consumption` | Planned mapped coverage | Add simulated event-volume fixture and queue/backpressure evaluator. |

## Current module-to-technique map

| VulnoraIQ module | ATLAS techniques |
| --- | --- |
| `owasp_llm01_prompt_injection` | AML.T0051, AML.T0051.000, AML.T0051.001, AML.T0065, AML.T0068 |
| `owasp_llm02_sensitive_information_disclosure` | AML.T0057, AML.T0056, AML.T0069, AML.T0069.002 |
| `owasp_llm03_supply_chain` | AML.T0010, AML.T0010.001, AML.T0010.002, AML.T0058 |
| `owasp_llm04_data_and_model_poisoning` | AML.T0019, AML.T0020, AML.T0059, AML.T0070 |
| `owasp_llm05_improper_output_handling` | AML.T0067, AML.T0067.000, AML.T0048 |
| `owasp_llm06_excessive_agency` | AML.T0053, AML.T0054 |
| `owasp_llm07_system_prompt_leakage` | AML.T0056, AML.T0069, AML.T0069.002 |
| `owasp_llm08_vector_embedding_weaknesses` | AML.T0064, AML.T0066, AML.T0070, AML.T0071 |
| `owasp_llm09_misinformation` | AML.T0060, AML.T0062, AML.T0067 |
| `owasp_llm10_unbounded_consumption` | AML.T0029, AML.T0034, AML.T0046 |
| `rag_poisoning` | AML.T0064, AML.T0066, AML.T0070, AML.T0071 |
| `retrieval_manipulation` | AML.T0064, AML.T0066, AML.T0067 |
| `corpus_validation` | AML.T0019, AML.T0020, AML.T0059, AML.T0070 |
| `agent_chain_attack` | AML.T0051, AML.T0053, AML.T0054 |
| `tool_execution_monitor` | AML.T0053 |
| `memory_tampering` | AML.T0053, AML.T0057 |
| `multi_agent_abuse` | AML.T0053, AML.T0054, AML.T0048 |

## Implementation checklist for adding techniques later

For each new technique added from a refreshed ATLAS source:

- Add the technique ID, name, and rationale in `config/mitre_atlas_mapping.yaml`.
- Add the technique to the correct section in this matrix.
- Map it to at least one VulnoraIQ module or explicitly mark it as backlog.
- Add safe fixture coverage where possible.
- Add deterministic evaluator rules.
- Add report fields for evidence quality and confidence.
- Add CI tests so the technique cannot silently disappear from the matrix.

## Status labels

| Label | Meaning |
| --- | --- |
| Backlog | Technique is documented but not mapped to a module yet. |
| Planned mapped coverage | Technique is mapped to a module but no dedicated evaluator/fixture exists yet. |
| Starter oracle coverage | Technique is covered by the current safe starter oracle layer. |
| Working starter | Technique has structured local validation but is not production-validated. |
| Production validated | Reserved for future use after authorised real-world validation and stronger evidence review. |
