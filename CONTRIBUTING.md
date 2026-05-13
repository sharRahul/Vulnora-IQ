# Contributing

Thank you for helping improve the LLM VAPT Framework.

## Contribution principles

- Keep all tests focused on authorised AI security assessment.
- Do not contribute payloads that facilitate credential theft, malware delivery, uncontrolled exfiltration, or bypass of real-world safety systems outside a defensive test context.
- Map every new module to an OWASP LLM 2025 risk, MITRE ATLAS technique where relevant, and at least one remediation recommendation.
- Add unit tests for scoring, result formatting, and module behaviour.

## Development workflow

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
```

## Adding a new module

1. Create the module under `modules/`, `rag_testing/`, or `agent_testing/`.
2. Add the module key to `core/test_runner.py` or replace the starter module runner with a concrete module class.
3. Update `config/owasp_llm_2025_mapping.yaml` and relevant docs.
4. Add tests under `tests/unit/`.

## Finding requirements

Every finding should include title, description, severity, OWASP reference, evidence, recommendation, and affected component.
