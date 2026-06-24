from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=check)


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode())


def main() -> int:
    if not Path("/.dockerenv").exists():
        print("WARNING: smoke test is intended to run inside Docker Compose test-runner, not host")
    assert get("http://vulnoraiq-web:8787/healthz")["status"] == "ok"
    assert get("http://local-mock-agent:9090/healthz")["status"] == "ok"
    validation = run(["vulnoraiq", "targets", "validate", "--target", "local_mock_agent"]).stdout
    assert "docker mock agent ready" in validation.lower(), validation
    scan = run(["vulnoraiq", "scan", "--target", "local_mock_agent", "--profile", "ai_agent_foundation", "--authorised"]).stdout
    assert "Assessment complete" in scan, scan
    report_root = Path(os.getenv("VULNORAIQ_WEB_OUTPUT_ROOT", "/data/reports"))
    assert (report_root / "scan-report.json").exists()
    data = json.loads((report_root / "scan-report.json").read_text(encoding="utf-8"))
    assert data.get("finding_count", 0) > 0
    evidence_root = Path(os.getenv("VULNORAIQ_EVIDENCE_DIR", "/data/evidence"))
    evidence_files = list(evidence_root.rglob("*.json"))
    assert evidence_files, "no evidence files written"
    blocked = run(
        [
            "python",
            "-c",
            "from integrations.target_adapters import validate_url; validate_url({'base_url':'https://example.com','endpoint_path':'/','safety_profile':'docker_lab'})",
        ],
        check=False,
    )
    assert blocked.returncode != 0 and "blocked" in blocked.stdout.lower(), blocked.stdout
    contents = "\n".join(path.read_text(errors="ignore") for path in evidence_files[:5])
    assert "sk-live" not in contents and "password=" not in contents.lower()
    print("docker smoke test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
