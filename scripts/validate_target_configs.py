from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.target_adapters import normalize_target_config, validate_url  # noqa: E402


def main() -> int:
    cfg = Path(os.getenv("VULNORAIQ_CONFIG_DIR", "config")) / os.getenv("VULNORAIQ_TARGET_CONFIG", "targets.docker.yaml")
    data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    targets = data.get("targets") or {}
    if not targets:
        print("no targets configured")
        return 1
    for name, target in targets.items():
        norm = normalize_target_config(name, target)
        validate_url(norm)
        print(f"ok {name} {norm.get('type')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
