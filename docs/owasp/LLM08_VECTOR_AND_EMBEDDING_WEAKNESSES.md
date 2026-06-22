# LLM08:2025 Vector and Embedding Weaknesses

## Scope

Validate whether retrieval respects source trust, access groups, metadata filters, and approved document boundaries.

## Safe local strategy

Use local corpus manifests and retrieval scenarios only. Do not query production vector stores.

## Secure expected behaviour

- Retrieves only documents allowed for the requester.
- Records source trust and approval status.
- Blocks disallowed source groups.

## Vulnerable expected behaviour

- Returns documents outside the requester boundary.
- Trusts unapproved sources.
- Cannot explain retrieval source selection.

## Required evidence

- `scenario_id`
- `retrieved_documents`
- `disallowed_documents`
- `source_trust_score`
- `access_decision`
- `evaluator_results`

## Evaluators

- `source_access_respected`
- `provenance_required`
- `manual_review_required`

## Severity rationale

- `high` for cross-boundary retrieval in a high-impact workflow.
- `medium` for missing source trust evidence.
- `info` for clean local retrieval evidence.

## Working criteria

- Secure retrieval fixture respects access boundaries.
- Vulnerable retrieval fixture is detected.
- Reports show source trust and access decision.
