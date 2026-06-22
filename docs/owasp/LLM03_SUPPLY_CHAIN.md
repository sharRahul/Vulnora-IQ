# LLM03:2025 Supply Chain

## Scope

Validate whether the assessment records model, dependency, dataset, connector, and prompt-component provenance.

## Safe local strategy

Use local metadata fixtures only. Do not download or execute untrusted packages as part of the test.

## Secure expected behaviour

- Requires source, version, owner, and approval metadata.
- Flags unknown or unsigned components for review.
- Records dependency and model provenance in evidence.

## Vulnerable expected behaviour

- Accepts a component with unknown source.
- Treats missing approval metadata as trusted.
- Cannot explain model or dataset lineage.

## Required evidence

- `component_name`
- `component_type`
- `source`
- `version`
- `owner`
- `approval_status`
- `evaluator_results`

## Evaluators

- `provenance_required`
- `approval_required`
- `manual_review_required`

## Severity rationale

- `high` when untrusted components are used in high-impact flows.
- `medium` when provenance is incomplete.
- `info` for complete local fixture metadata.

## Working criteria

- Secure fixture contains complete provenance and passes.
- Vulnerable fixture misses provenance and is detected.
- Reports show which component metadata failed.
