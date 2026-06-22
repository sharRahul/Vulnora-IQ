# MITRE ATLAS Matrix for AI Systems

This file is the VulnoraIQ implementation planning register for MITRE ATLAS tactics, techniques, and sub-techniques.

> **Generated snapshot:** this checked-in snapshot is generated from the official MITRE ATLAS v6 source path used by VulnoraIQ: `https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml`.

> **Third-party notice:** MITRE ATLAS data is copyright 2021-2026 MITRE and licensed under the Apache License, Version 2.0. VulnoraIQ's use of MITRE ATLAS data does not imply endorsement by MITRE. See `THIRD_PARTY_NOTICES.md`.

> **Mapping rule:** if a tactic or technique cannot be confidently mapped to OWASP or a VulnoraIQ coverage area, it is still listed and marked `Unmapped / map later`. No ATLAS item should disappear just because it is not mapped yet.

## Official source alignment

- Site: `https://atlas.mitre.org`
- Data repository: `https://github.com/mitre-atlas/atlas-data`
- Source file: `dist/v6/ATLAS-2026.05.yaml`
- Collection version: `2026.05`
- Modified date: `2026-05-27`
- Tactic count in this snapshot: `16`
- Technique and sub-technique count in this snapshot: `170`

## Regeneration command

```bash
vulnoraiq-generate-atlas-matrix \
  --source https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml \
  --output docs/MITRE_ATLAS_AI_MATRIX.md
```

Check for drift:

```bash
vulnoraiq-generate-atlas-matrix \
  --source https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml \
  --output docs/MITRE_ATLAS_AI_MATRIX.md \
  --check
```
