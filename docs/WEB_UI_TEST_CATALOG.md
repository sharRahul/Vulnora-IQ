# Web UI Categorized Test Catalog

The self-hosted VulnoraIQ Web UI exposes runnable assessment options as a categorized catalog.

## User workflow

1. Choose a target.
2. Choose a test option from the dropdown or category cards.
3. Review the selected option details.
4. Confirm authorisation for configured non-demo targets.
5. Start the selected assessment.
6. Review progress, findings, policy status, and report artifacts.

## Categories

The dashboard groups runnable profiles into:

- `Assessment suites` — baseline, RAG, agent, and full assessment suites.
- `OWASP LLM Top 10 single tests` — one-click focused checks for each OWASP LLM module.
- `RAG and vector store tests` — focused retrieval, corpus, and vector-store checks.
- `Agentic and tool-use tests` — focused agent orchestration, tool execution, memory, and multi-agent checks.

## Implementation

The catalog is driven by `config/attack_profiles.yaml`. Each visible option must include:

- `category`
- `display_name`
- `description`
- `modules`

Single-test profiles use a single module in `modules`, allowing users to run one focused test from the Web UI without changing backend scanner behaviour.

## Validation

```bash
pytest tests/test_webui_test_catalog.py -q
```

The test ensures every registered starter module has at least one runnable single-test profile and that each catalog option includes display metadata.
