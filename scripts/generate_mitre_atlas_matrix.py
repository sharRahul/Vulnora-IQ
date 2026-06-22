from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import yaml

DEFAULT_SOURCE_URL = "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml"
DEFAULT_OUTPUT = Path("docs/MITRE_ATLAS_AI_MATRIX.md")


def load_atlas(source: str) -> dict[str, Any]:
    if source.startswith("http://") or source.startswith("https://"):
        with urlopen(source, timeout=60) as response:  # noqa: S310 - public MITRE ATLAS data fetch
            return yaml.safe_load(response.read().decode("utf-8")) or {}
    return yaml.safe_load(Path(source).read_text(encoding="utf-8")) or {}


def _clean(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").replace("|", "\\|")
    return " ".join(text.split())


def _technique_tactics(data: dict[str, Any]) -> dict[str, list[str]]:
    tactics = data.get("tactics", {}) or {}
    tactic_names = {tid: tactic.get("name", tid) for tid, tactic in tactics.items()}
    relationships = data.get("relationships", {}) or {}
    mapped: dict[str, list[str]] = {}
    for source_id, relation in relationships.items():
        achieves = relation.get("achieves", []) if isinstance(relation, dict) else []
        labels: list[str] = []
        for target_id in achieves:
            if target_id in tactic_names:
                labels.append(f"{target_id} — {tactic_names[target_id]}")
        if labels:
            mapped[source_id] = labels
    return mapped


def render_matrix(data: dict[str, Any], source: str) -> str:
    collection = data.get("collection", {}) or {}
    tactics = data.get("tactics", {}) or {}
    techniques = data.get("techniques", {}) or {}
    technique_tactics = _technique_tactics(data)

    lines: list[str] = []
    lines.append("# MITRE ATLAS Matrix for AI Systems")
    lines.append("")
    lines.append("This file is the VulnoraIQ implementation planning register for MITRE ATLAS tactics and techniques. It is generated from the official MITRE ATLAS data source so future VulnoraIQ configuration, payload, and documentation changes can be checked for drift.")
    lines.append("")
    lines.append("> **Current status:** source-of-truth planning register. Entries in this file are not automatically active VulnoraIQ checks. Use the implementation columns to plan payloads, fixtures, evaluators, reports, and dashboard coverage.")
    lines.append("")
    lines.append("## Source")
    lines.append("")
    lines.append(f"- Source: `{source}`")
    lines.append(f"- Collection: `{_clean(collection.get('name'))}`")
    lines.append(f"- Content version: `{_clean(collection.get('version'))}`")
    lines.append(f"- Format version: `{_clean(data.get('format-version'))}`")
    lines.append(f"- Modified date: `{_clean(collection.get('modified-date'))}`")
    lines.append(f"- Tactic count: `{len(tactics)}`")
    lines.append(f"- Technique and sub-technique count: `{len(techniques)}`")
    lines.append("")
    lines.append("## How VulnoraIQ should use this matrix")
    lines.append("")
    lines.append("1. Keep this file generated from `mitre-atlas/atlas-data`.")
    lines.append("2. Add VulnoraIQ module mappings in `config/mitre_atlas_mapping.yaml`.")
    lines.append("3. Add safe payloads and fixtures for each selected technique.")
    lines.append("4. Add deterministic evaluators and report fields.")
    lines.append("5. Mark implementation status only after CI validates the payload/evaluator path.")
    lines.append("")
    lines.append("## Tactics")
    lines.append("")
    lines.append("| Tactic ID | Tactic | ATT&CK reference | VulnoraIQ implementation status | Payload/evaluator planning notes |")
    lines.append("| --- | --- | --- | --- | --- |")
    for tactic_id in sorted(tactics):
        tactic = tactics[tactic_id]
        attack_ref = tactic.get("attack-reference") or {}
        attack = attack_ref.get("id", "")
        lines.append(f"| {tactic_id} | {_clean(tactic.get('name'))} | {_clean(attack)} | Backlog/planning | Add VulnoraIQ coverage once related techniques are selected for implementation. |")
    lines.append("")
    lines.append("## Techniques and sub-techniques")
    lines.append("")
    lines.append("| Technique ID | Technique | Tactic(s) | Maturity | Platform(s) | VulnoraIQ implementation status | Payload/evaluator planning notes |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for technique_id in sorted(techniques):
        technique = techniques[technique_id]
        tactics_text = "<br>".join(technique_tactics.get(technique_id, [])) or "Unmapped in ATLAS relationships"
        platforms = ", ".join(technique.get("platforms", []) or [])
        status = "Backlog/planning"
        notes = "Add safe payloads, local fixtures, evaluator logic, evidence fields, and report/dashboard mapping before marking active."
        lines.append(
            f"| {technique_id} | {_clean(technique.get('name'))} | {_clean(tactics_text)} | {_clean(technique.get('maturity'))} | {_clean(platforms)} | {status} | {notes} |"
        )
    lines.append("")
    lines.append("## Drift-control rule")
    lines.append("")
    lines.append("Future changes must not manually edit the generated tactic/technique tables. Update the official source version or generator, regenerate this file, then update VulnoraIQ payloads/configuration against the regenerated IDs.")
    return "\n".join(lines) + "\n"


def write_or_check(source: str, output: Path, check: bool) -> int:
    data = load_atlas(source)
    rendered = render_matrix(data, source)
    if check:
        existing = output.read_text(encoding="utf-8") if output.exists() else ""
        if existing != rendered:
            print(f"MITRE ATLAS matrix is out of date: {output}", file=sys.stderr)
            return 1
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the VulnoraIQ MITRE ATLAS AI matrix documentation from official ATLAS YAML.")
    parser.add_argument("--source", default=DEFAULT_SOURCE_URL, help="Official ATLAS YAML URL or local file path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown output path.")
    parser.add_argument("--check", action="store_true", help="Fail if the output file is not up to date.")
    args = parser.parse_args()
    raise SystemExit(write_or_check(args.source, Path(args.output), args.check))


if __name__ == "__main__":
    main()
