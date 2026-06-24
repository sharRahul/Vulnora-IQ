# Agentic Applications Security implementation plan

This folder documents VulnoraIQ's OWASP Top 10 for Agentic Applications planning and readiness alignment.

> **Status:** Complete for source-confirmed planning and current self-hosted readiness scope.  
> **Current deployment model:** Docker-first local AI-agent lab plus self-hosted internal server mode.  
> **Boundary:** `ASI01–ASI10` categories are source-confirmed and mapped for planning/readiness. VulnoraIQ does not claim independent production-validated agentic assurance for every category.

## Source documents reviewed

- `docs/owasp-documents/OWASP-Top-10-for-Agentic-Applications-2026-12.6.pdf` — confirms the OWASP Agentic Top 10 `ASI01–ASI10` category names.
- `docs/owasp-documents/OWASP-Top10-for-Agentic-Applications_AIUC-1-Crosswalk-May26.pdf` — confirms AIUC-1 crosswalk methodology, Primary/Secondary relevance, and strategic gaps.
- `docs/owasp-documents/State-of-Agentic-AI-Security-and-Governance-v2.01.pdf` — confirms governance context, adoption-tier prioritisation, agent identity/NHI, AI SBOM/provenance, runtime governance, and incident evidence.
- existing VulnoraIQ `docs/owasp/LLM06_EXCESSIVE_AGENCY.md`.
- existing VulnoraIQ `agent_testing/` manifests and scenarios.
- `docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`.

## Confirmed OWASP Agentic categories

| OWASP ID | Agentic risk | Current status | Related OWASP LLM categories | Primary evidence surfaces |
| --- | --- | --- | --- | --- |
| ASI01 | Agent Goal Hijack | Complete for planning scope | LLM01, LLM06, LLM07 | goal, prompt, retrieved context, tool description, plan trace |
| ASI02 | Tool Misuse and Exploitation | Complete for planning scope | LLM05, LLM06, LLM10 | tool manifest, tool call, argument trace, policy decision |
| ASI03 | Identity and Privilege Abuse | Complete for planning scope | LLM02, LLM06 | agent identity, credential scope, delegation trace, auth context |
| ASI04 | Agentic Supply Chain Vulnerabilities | Complete for planning scope | LLM03, LLM06 | tool/framework/provider manifest, version/provenance, prompt/template source |
| ASI05 | Unexpected Code Execution | Complete for planning scope | LLM05, LLM06 | code/tool trace, sandbox status, process-control evidence |
| ASI06 | Memory & Context Poisoning | Complete for planning scope | LLM01, LLM04, LLM06, LLM08 | memory trace, context diff, state store, source metadata |
| ASI07 | Insecure Inter-Agent Communication | Complete for planning scope | LLM02, LLM06 | agent identity, message metadata, trust boundary, protocol metadata |
| ASI08 | Cascading Failures | Complete for planning scope | LLM06, LLM10 | propagation trace, dependency graph, circuit breaker, blast-radius control |
| ASI09 | Human-Agent Trust Exploitation | Complete for planning scope | LLM05, LLM06, LLM09 | human approval, user-facing output, high-risk action flag, review evidence |
| ASI10 | Rogue Agents | Complete for planning scope | LLM03, LLM06, LLM10 | agent registry, behaviour drift, safety control, containment evidence |

## Current implemented support

The repo now includes Docker-first AI-agent lab support and current-scope agentic assessment paths:

- `ai_agent_foundation` and agent-oriented profiles;
- Docker `local_agent_tool_loop` mock target;
- host-native `agent_tool_loop` template;
- target validation and explicit authorisation;
- WebUI target-management readiness checks;
- reports/evidence requiring human review.

## Relationship to existing LLM tests

Existing VulnoraIQ LLM tests cover current-scope forms of prompt injection, sensitive information disclosure, supply chain, data/model integrity, output handling, agency, prompt leakage, vector/embedding weaknesses, misinformation, and resource limits.

The Agentic plan extends this into planning, identity, memory, delegation, inter-agent communication, traceability, bounded autonomy, and runtime governance themes.

## AIUC-1 and governance implication

The AIUC-1 crosswalk states that mappings identify relevance, not sufficiency. VulnoraIQ uses the same rule: an ASI mapping does not mean the check fully mitigates the risk.

## Completion rule

The current document is complete for source-confirmed planning, mapping, and readiness alignment. Stronger assurance requires safe local fixtures, approved-environment validation, richer runtime evidence, calibrated evaluator thresholds, and independent review.
