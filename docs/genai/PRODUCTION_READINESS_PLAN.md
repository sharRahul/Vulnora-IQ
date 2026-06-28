# GenAI Security production readiness plan

Plan status: Completed for `0.3.0` self-hosted internal deployment.

This active document preserves the validated GenAI readiness documentation path. The full historical plan text is staged for maintainer review in [`../ready-to-remove/GENAI_PRODUCTION_READINESS_PLAN.md`](../ready-to-remove/GENAI_PRODUCTION_READINESS_PLAN.md).

## Current source of truth

- Current implementation status: [`../IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md)
- Production readiness scorecard: [`../PRODUCTION_READINESS_SCORECARD.md`](../PRODUCTION_READINESS_SCORECARD.md)
- Assurance boundary: [`../ASSESSMENT_ASSURANCE.md`](../ASSESSMENT_ASSURANCE.md)
- Scenario manifest: [`../../benchmarks/fixtures/genai/scenarios.yaml`](../../benchmarks/fixtures/genai/scenarios.yaml)

## Current validated scope

This is the controlled internal enterprise deployment gate for the self-hosted laptop/server application model.

VulnoraIQ keeps a production-grade scenario harness for controlled internal GenAI Security validation. The maintained scope tracks `DSGAI01–DSGAI21`, expands them into **84 concrete scenario cases**, and validates the `genai-production-v2` evidence contract through `scripts/validate_genai_readiness.py`.

This is **not independent real-world detection assurance**. The harness validates scenario structure, evidence fields, evaluator contracts, confidence floors, manual-review routing, and report wording for controlled internal validation. Findings remain framework evidence requiring human review.

## Maintainer note

Keep this lightweight active stub until the validator is intentionally changed. Delete or archive the full historical copy in `docs/ready-to-remove/` only after maintainer review.
