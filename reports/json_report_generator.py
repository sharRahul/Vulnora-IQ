from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.results_engine import ResultsEngine
from core.types import ScanResult


class JsonReportGenerator:
    """Generates machine-readable assessment reports for CI and dashboards."""

    def __init__(self) -> None:
        self.results_engine = ResultsEngine()

    def generate(self, result: ScanResult, output_path: str | Path) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        normalised: dict[str, Any] = self.results_engine.normalise(result)
        output.write_text(json.dumps(normalised, indent=2, sort_keys=True, default=str), encoding="utf-8")
        return output
