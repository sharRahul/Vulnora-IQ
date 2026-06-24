# WebUI categorized test catalog

The current React WebUI exposes assessment profiles as an operator-facing catalogue. Users can choose full suites or focused single-test profiles without changing backend scanner behaviour.

## Current user workflow

1. Open the WebUI.
2. Choose or filter a target in the target-management workspace.
3. Validate target connectivity.
4. Choose a suite or focused test option.
5. Review the readiness checklist and target metadata.
6. Confirm authorisation for configured non-demo targets.
7. Launch the scan.
8. Review recent jobs, findings, policy status, and report artifacts.

## Catalogue categories

The profile catalogue is driven by `config/attack_profiles.yaml`. Current visible groupings include:

| Category | Examples |
| --- | --- |
| Assessment suites | `baseline`, `rag`, `agent`, `full`, `ai_agent_foundation`, `ai_testing_guide_foundation` |
| OWASP LLM Top 10 single tests | Focused `LLM01` through `LLM10` module profiles. |
| RAG and vector-store tests | Retrieval, context, source, and vector-store checks. |
| Agentic and tool-use tests | Tool execution, permission, memory, autonomy, and multi-agent checks. |
| OWASP AI Testing Guide profiles | Foundation and individual methodology/profile checks. |

## Metadata requirements

Each visible profile should include:

- `category`
- `display_name`
- `description`
- `modules`

Single-test profiles should reference a single module so users can run one focused check from the WebUI.

## Current WebUI implementation

The target-management workspace now combines profile selection with:

- target search/filtering;
- readiness metrics;
- target health/status indicators;
- safety checklist;
- target validation;
- scan launch controls;
- recent job list.

## Validation

```bash
pytest tests/test_webui_test_catalog.py -q
npm run test:webui:hosted
```

The Python test validates profile catalogue metadata. The hosted WebUI Playwright flow exercises the browser-level run path when Chromium is available.

## Boundary

Catalogue visibility does not mean every mapped framework item has independently validated real-world detection coverage. Treat scan output as internal assessment evidence requiring human review.
