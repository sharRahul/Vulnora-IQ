# LLM VAPT Framework

An AI security assessment framework for **LLM applications, RAG pipelines, AI agents, and orchestration layers**.

> **Current maturity:** this repository is a working starter framework, not a complete enterprise platform yet. Start with [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) to see what is implemented, partial, or planned.

> **Responsible use only:** run this framework only against systems you own or are explicitly authorised to assess. The default demo target is safe and local. Configured non-demo targets require an explicit authorisation flag.

## Why this exists

AI application security needs more than prompt-level checks. This repository provides a practical structure for assessing model endpoints, retrieval layers, tools, memory, orchestration, governance controls, and reporting.

The current implementation provides:

- OWASP LLM 2025 starter mapping
- Safe demo target with no external API keys
- Baseline, RAG, agent, and full profile definitions
- Scanner, starter check runner, scoring, and result model
- Markdown reporting with evidence details
- Explicit non-demo authorisation gate
- Minimal HTTP JSON target adapter for approved targets

The roadmap includes deeper RAG fixtures, agent harnesses, policy enforcement, MITRE ATLAS mapping, dashboards, and CI-friendly output formats.

## OWASP LLM 2025 coverage

| OWASP ID | Risk | Module path / status |
|---|---|---|
| LLM01:2025 | Prompt Injection | Starter check |
| LLM02:2025 | Sensitive Information Disclosure | Starter check |
| LLM03:2025 | Supply Chain | Starter check |
| LLM04:2025 | Data and Model Poisoning | Starter check |
| LLM05:2025 | Improper Output Handling | Starter check |
| LLM06:2025 | Excessive Agency | Starter check |
| LLM07:2025 | System Prompt Leakage | Starter check |
| LLM08:2025 | Vector and Embedding Weaknesses | Starter check |
| LLM09:2025 | Misinformation | Starter check |
| LLM10:2025 | Unbounded Consumption | Starter check |

## Architecture

```text
Target AI Systems: demo echo target | configured HTTP JSON target
        ↓
Integration Layer: DemoEchoClient | HttpJsonTargetClient
        ↓
Core Engine: Scanner | Test Runner | Results Engine | Risk Scoring
        ↓
Testing Profiles: baseline | rag | agent | full
        ↓
Reporting: Markdown report with finding evidence and recommendations
```

## Repository structure

```text
llm-vapt-framework/
├── config/                 # Targets, profiles, policies, mappings
├── core/                   # Scanner, runner, scoring, results model
├── integrations/           # Demo and HTTP JSON adapters
├── modules/                # Reserved for future pluggable module implementations
├── rag_testing/            # Reserved for RAG fixtures and harnesses
├── agent_testing/          # Reserved for agent fixtures and harnesses
├── payloads/               # Reserved for safe starter payload libraries
├── reports/                # Markdown report generation and templates
├── dashboards/             # Reserved for visualisation helpers
├── tests/                  # Unit tests
├── scripts/                # CLI and CI entry points
└── docs/                   # Architecture, roadmap, mapping, governance docs
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python scripts/run_scan.py --target demo --profile baseline
```

The demo target uses an in-memory echo client, so the framework can be explored without external API keys.

## Run tests

```bash
pytest -q
```

## Example demo command

```bash
python scripts/run_scan.py \
  --target demo \
  --profile baseline \
  --output reports/output/demo-report.md
```

## Configured target command

Only use this for systems you own or are explicitly authorised to assess:

```bash
python scripts/run_scan.py \
  --target custom_http_agent \
  --profile baseline \
  --authorised \
  --output reports/output/authorised-target-report.md
```

Before running against a configured target, replace the placeholder endpoint in `config/targets.yaml` and set any required token environment variable.

## Configuration

- `config/default.yaml`: engine defaults
- `config/targets.yaml`: target definitions
- `config/attack_profiles.yaml`: selective module execution
- `config/policies.yaml`: governance thresholds and blocking conditions
- `config/owasp_llm_2025_mapping.yaml`: audit-friendly OWASP mapping

## Design principles

1. Audit-friendly by default.
2. Safe local demo first.
3. Explicit authorisation for configured targets.
4. System-level coverage roadmap across LLM, RAG, tool, memory, and orchestration layers.
5. CI/CD-ready direction for prompt, corpus, agent, and release-gate checks.

## License

MIT. See `LICENSE`.
