# VulnoraIQ

**VulnoraIQ** is an early-stage AI security assessment and VAPT platform for **LLM applications, RAG pipelines, AI agents, and orchestration layers**.

> **Current maturity:** version `0.0.1.2` is an early development build. It is useful for local demos, UI workflow validation, report-pipeline development, and safe framework testing. It is **not ready for real-world VAPT testing or production assessment use** yet.

> **Important limitation:** OWASP LLM 2025 coverage now has safe starter oracle coverage for all 10 categories, but the checks are not production-validated. Treat all scan output as framework-development evidence, not validated security assurance.

> **Responsible use only:** run this platform only against systems you own or are explicitly authorised to assess. The default demo target is safe and local. Configured non-demo targets require an explicit authorisation flag.

## Why this exists

AI application security needs more than prompt-level checks. VulnoraIQ provides a practical structure for assessing model endpoints, retrieval layers, tools, memory, orchestration, governance controls, and reporting.

The current implementation provides:

- Modern hosted Web UI with realtime progress, role-aware auth hooks, persistent JSON job storage, executive dashboards, scan history, and artifact download
- OWASP LLM 2025 safe starter oracle coverage for all 10 categories
- Structured evidence records and oracle results for module interactions
- MITRE ATLAS mapping catalog with AML technique IDs, local source fixture, and scheduled refresh validation workflow
- Safe demo target with no external API keys
- Local demo HTTP target and control-gap fixture examples
- Baseline, RAG, agent, and full profile definitions
- Module protocol, starter modules, and registry-based module lookup
- Safe YAML payload libraries mapped to module names
- Scanner, scoring, result model, policy evaluation, scoped policy exceptions, and approval evidence validation
- RAG corpus manifest validation and RAG retrieval scenario validation with source-trust scoring
- Agent runtime governance and simulated execution validation for tools, memory, approvals, and rollback planning
- Configured target adapter contracts for HTTP JSON, chat-completions-compatible, Ollama-style generate, and webhook JSON endpoint shapes
- Markdown, JSON, SARIF-style, Markdown dashboard, HTML dashboard, trend, diff, and branded HTML export outputs
- Benchmark regression suite and OWASP starter fixture corpus
- Safe release-package builder for demo outputs and non-sensitive examples
- Package metadata release gate
- Explicit non-demo authorisation gate
- Python CI across supported versions with tests, metadata gates, target contract validation, benchmark fixture validation, scan smoke tests, trends, exports, and release artifacts

The next phase should focus on the OWASP documentation and check-depth plan before any claim of real-world VAPT readiness.

## OWASP LLM 2025 coverage

| OWASP ID | Risk | Module status |
|---|---|---|
| LLM01:2025 | Prompt Injection | Safe starter oracle with ATLAS mapping |
| LLM02:2025 | Sensitive Information Disclosure | Safe starter oracle with ATLAS mapping |
| LLM03:2025 | Supply Chain | Safe starter oracle with ATLAS mapping |
| LLM04:2025 | Data and Model Poisoning | Safe starter oracle with ATLAS mapping |
| LLM05:2025 | Improper Output Handling | Safe starter oracle with ATLAS mapping |
| LLM06:2025 | Excessive Agency | Safe starter oracle with ATLAS mapping |
| LLM07:2025 | System Prompt Leakage | Safe starter oracle with ATLAS mapping |
| LLM08:2025 | Vector and Embedding Weaknesses | Safe starter oracle with ATLAS mapping |
| LLM09:2025 | Misinformation | Safe starter oracle with ATLAS mapping |
| LLM10:2025 | Unbounded Consumption | Safe starter oracle with ATLAS mapping |

## Architecture

```text
Operator Browser: Hosted Web UI | CLI | CI
        ↓
Auth / Role Layer: local token config | viewer | analyst | admin
        ↓
Target AI Systems: demo echo target | local demo app | configured HTTP/Chat/Ollama/Webhook targets
        ↓
Integration Layer: DemoEchoClient | HttpJsonTargetClient | ChatCompletionsTargetClient | OllamaGenerateTargetClient | WebhookJsonTargetClient | TargetContractValidator
        ↓
Core Engine: Scanner | Test Runner | Results Engine | Risk Scoring | Policy Engine | OWASP Oracle Registry
        ↓
Module Layer: AssessmentModule protocol | ModuleRegistry | starter modules | structured evidence model
        ↓
Payload Layer: safe YAML payload libraries
        ↓
Governance Layer: policy rules | exceptions | approval evidence | RAG manifest | RAG retrieval scenarios | agent runtime manifest | agent execution scenarios | ATLAS mapping
        ↓
Assessment Profiles: baseline | rag | agent | full
        ↓
Outputs: Web dashboard | Markdown | JSON | SARIF-style | dashboards | report diff | trends | benchmarks | HTML export | release package
```

## Repository structure

```text
vulnoraiq/
├── .github/workflows/       # Python CI and ATLAS refresh validation
├── benchmarks/              # Regression benchmark suite, fixtures, and runner
├── config/                  # Targets, profiles, policies, manifests, mappings, scenarios, auth, branding
├── core/                    # Scanner, runner, scoring, policy, exceptions, approvals, mapping, evidence, results model
├── examples/                # Safe local demo targets and fixtures
├── integrations/            # Demo, HTTP JSON, chat, Ollama-style, webhook adapters, and contract validation
├── modules/                 # Module protocol, registry, and starter modules
├── rag_testing/             # RAG corpus and retrieval validation
├── agent_testing/           # Agent runtime and execution validation
├── payloads/                # Safe payload schema and libraries
├── reports/                 # Markdown, JSON, SARIF-style, diff, policy-trend, and HTML export generation
├── dashboards/              # Markdown, HTML, and diff-trend dashboard generation
├── webui/                   # Hosted Web UI server, auth, persistent jobs, and static frontend
├── tests/                   # Unit tests
├── scripts/                 # CLI entry points, package validation, release package builder, ATLAS refresh
└── docs/                    # Architecture, status, mapping, governance docs
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
vulnoraiq --target demo --profile baseline
```

The demo target uses an in-memory echo client, so the platform can be explored without external API keys.

## Web UI command

Run the hosted Web UI:

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Open:

```text
http://127.0.0.1:8787
```

The Web UI supports scan launch, realtime progress via Server-Sent Events, completed dashboard views, persistent scan history, role-aware auth hooks, and downloadable Markdown/JSON/SARIF/dashboard artifacts. See [`docs/web-ui.md`](docs/web-ui.md).

## Run tests

```bash
pytest -q
```

## Example demo command

```bash
vulnoraiq \
  --target demo \
  --profile baseline \
  --output reports/output/demo-report.md \
  --json-output reports/output/demo-report.json \
  --sarif-output reports/output/demo-report.sarif \
  --dashboard-output reports/output/demo-dashboard.md \
  --html-dashboard-output reports/output/demo-dashboard.html
```

## Configured target command

Only use this for systems you own or are explicitly authorised to assess:

```bash
vulnoraiq \
  --target custom_http_agent \
  --profile baseline \
  --authorised \
  --output reports/output/authorised-target-report.md \
  --json-output reports/output/authorised-target-report.json \
  --sarif-output reports/output/authorised-target-report.sarif \
  --dashboard-output reports/output/authorised-target-dashboard.md \
  --html-dashboard-output reports/output/authorised-target-dashboard.html
```

Before running against a configured target, replace the placeholder endpoint in `config/targets.yaml`, validate the target contract, and set any required token environment variable.

## Report, trend, benchmark, and export commands

```bash
vulnoraiq-diff --baseline reports/output/baseline.json --current reports/output/current.json
vulnoraiq-policy-trend --input-dir reports/output
vulnoraiq-diff-trend --input-dir reports/output
vulnoraiq-benchmark --manifest benchmarks/benchmark_suite.yaml --fail-on-regression
vulnoraiq-html-export --input-dir reports/output
vulnoraiq-validate-package
```

## ATLAS refresh command

Use local fixture mode in CI and review generated mappings before committing refreshed data:

```bash
vulnoraiq-refresh-atlas --source config/mitre_atlas_source_fixture.yaml --output reports/output/mitre_atlas_mapping.refresh-check.yaml
```

## Release package command

Build a ZIP package with safe demo outputs and non-sensitive examples after generating demo reports:

```bash
vulnoraiq-package --manifest config/release_package.yaml
```

The package path defaults to `dist/vulnoraiq-example-package.zip`.

## Dashboard command

Generate a Markdown dashboard from an existing JSON report:

```bash
vulnoraiq-dashboard \
  --report reports/output/scan-report.json \
  --output reports/output/dashboard.md
```

The standard scan command also writes an HTML dashboard.

## Module and payload authoring

Read [`docs/module-authoring.md`](docs/module-authoring.md) before adding modules or payload libraries.

## Configuration

- `config/default.yaml`: engine defaults and paths for reports, Web UI, approvals, RAG, agent, ATLAS, benchmarks, and release packaging
- `config/targets.yaml`: target definitions and adapter examples
- `config/target_contracts.yaml`: target adapter contract definitions
- `config/web_users.yaml`: local Web UI auth and role configuration
- `config/report_branding.yaml`: report/export branding
- `config/attack_profiles.yaml`: selective module execution
- `config/policies.yaml`: governance thresholds and blocking conditions
- `config/policy_exceptions.yaml`: scoped exception register
- `config/approval_evidence.yaml`: signed approval evidence register
- `config/owasp_oracles.yaml`: safe OWASP starter oracle definitions
- `config/owasp_llm_2025_mapping.yaml`: audit-friendly OWASP mapping
- `config/mitre_atlas_mapping.yaml`: MITRE ATLAS mapping catalog
- `config/atlas_refresh.yaml`: ATLAS refresh settings
- `config/mitre_atlas_source_fixture.yaml`: local ATLAS refresh fixture
- `config/rag_corpus_manifest.yaml`: RAG corpus metadata manifest
- `config/rag_retrieval_scenarios.yaml`: RAG retrieval scenario manifest
- `config/agent_runtime.yaml`: agent tool, memory, and orchestration governance manifest
- `config/agent_execution_scenarios.yaml`: agent execution scenario manifest
- `config/release_package.yaml`: release package manifest
- `benchmarks/benchmark_suite.yaml`: regression benchmark suite
- `benchmarks/fixtures/owasp_starter_fixture.yaml`: OWASP starter fixture corpus
- `payloads/schema.yaml`: payload library schema and safety rules

## Design principles

1. Audit-friendly by default.
2. Safe local demo first.
3. Explicit authorisation for configured targets.
4. System-level starter coverage across LLM, RAG, tool, memory, and orchestration layers.
5. CI/CD-ready direction for prompt, corpus, agent, release-gate, and regression checks.

## License

MIT. See `LICENSE`.
