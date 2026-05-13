# Agent Testing Layer

This folder is for AI agent and orchestration-layer security tests.

Planned modules:

- `agent_chain_attack.py` - multi-step chain planning and abuse-path modelling
- `tool_execution_monitor.py` - tool-call logging, scoping, and policy checks
- `memory_tampering.py` - memory write integrity and source-trust checks
- `multi_agent_abuse.py` - inter-agent trust boundary and message abuse checks

Primary OWASP LLM 2025 alignment:

- LLM01: Prompt Injection
- LLM06: Excessive Agency
- LLM07: System Prompt Leakage
- LLM02: Sensitive Information Disclosure, where tool or memory output leaks private context
