# OWASP LLM Top 10 mapping implementation plan

## Current status

VulnoraIQ currently has OWASP LLM 2025 current-scope coverage, OWASP/MITRE metadata governance, and a planning roadmap for richer framework/control mapping.

This document remains a roadmap, not a completed implementation claim for every external framework mapping.

## Purpose

Define how VulnoraIQ should use framework/control mapping sources, including `emmanuelgjr/owaspllmtop10mapping`, to enrich findings, reports, dashboards, remediation guidance, and coverage traceability.

## Source basis

Reviewed source observations:

- The source repository maps OWASP Top 10 for LLM risks to multiple cybersecurity frameworks and standards.
- Listed mapping targets include NIST CSF, ISO/IEC 27001, ISO/IEC 20547-4:2020, MITRE ATT&CK, CIS Controls, CVE/CWE, FAIR, STRIDE, ENISA, ASVS, SAMM, MITRE ATLAS, BSIMM, OPENCRE, and CycloneDX ML SBOM.
- The repository is archived/read-only and should be treated as a static reference source.
- The project states MIT licensing.
- Example mappings provide useful control context but include approximations that must be adapted to VulnoraIQ's current OWASP LLM 2025 taxonomy and evidence model.

## Compatibility considerations

The source mappings may use earlier OWASP LLM category names or numbering. VulnoraIQ should not import them directly as authoritative coverage. It should normalise every entry against:

- current OWASP LLM 2025 IDs and names;
- VulnoraIQ module IDs and oracle IDs;
- MITRE ATLAS technique/tactic metadata;
- evidence surface and target type;
- confidence and provenance fields;
- manual-review requirement.

## Already implemented in VulnoraIQ

| Capability | Status |
| --- | --- |
| OWASP LLM 2025 category docs | Complete for all 10 categories in `docs/owasp/`. |
| Current-scope safe oracle coverage | Complete for local/internal assessment scope. |
| OWASP/MITRE mapping validation | Complete through `scripts/validate_owasp_atlas_mappings.py`. |
| MITRE ATLAS matrix/docs | Complete for current planning scope. |
| Report evidence model | Complete for current scanner/reporting scope. |

## Roadmap

| Phase | Outcome | Status |
| --- | --- | --- |
| MAP-1 | Create normalised mapping registry schema with source, framework, control ID, OWASP ID, VulnoraIQ module, confidence, and provenance. | Planned |
| MAP-2 | Add import/curation script for static source mappings with manual review queue. | Planned |
| MAP-3 | Add report enrichment for framework/control references. | Planned |
| MAP-4 | Add WebUI coverage and filtering by framework/control. | Planned |
| MAP-5 | Add CI validation for source provenance, stale mappings, missing confidence labels, and unsupported IDs. | Planned |
| MAP-6 | Add manual sign-off workflow before stronger assurance claims. | Future maturity |

## Registry fields

Each mapping entry should include:

- source repository/document;
- source license/provenance;
- source mapping ID or location;
- target framework;
- target framework control/technique ID;
- OWASP LLM 2025 ID;
- VulnoraIQ module/oracle/profile linkage;
- mapping confidence;
- mapping status (`active`, `candidate`, `needs_review`, `deprecated`, `map_later`);
- evidence surface;
- manual-review flag;
- notes on approximation or taxonomy mismatch.

## Safety and assurance boundary

Framework/control mappings enrich context. They do not prove that a target is secure or that every mapped control has been tested. Reports must distinguish between:

- implemented scanner checks;
- mapped control context;
- manual review requirements;
- future roadmap coverage.
