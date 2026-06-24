"""Launches VulnoraIQ via Docker Compose — no local Python venv required."""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "docker-compose.yml"
WEBUI_URL = "http://127.0.0.1:8787"
HEALTH_URL = f"{WEBUI_URL}/healthz"
POLL_TIMEOUT = 30.0


def _run_compose(args: list[str]) -> None:
    cmd = ["docker", "compose", *args]
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def _wait_for_webui(timeout: float = POLL_TIMEOUT) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(HEALTH_URL, timeout=2.0) as resp:
                if resp.status == 200:
                    return True
        except (OSError, URLError):
            pass
        time.sleep(0.5)
    return False


def main() -> None:
    try:
        subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=True,
            cwd=ROOT,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(
            "Docker engine is not running.\n\n"
            "VulnoraIQ requires Docker Desktop or a compatible Docker engine.\n"
            "Install / start Docker, then re-launch.\n"
        )
        sys.exit(1)

    if not COMPOSE_FILE.exists():
        print(f"docker-compose.yml not found at {COMPOSE_FILE}")
        sys.exit(1)

    _run_compose(["build"])
    _run_compose(["up", "-d"])
    _run_compose(["ps"])

    print(f"\nWaiting for VulnoraIQ to become ready at {WEBUI_URL} ...", flush=True)
    if _wait_for_webui():
        print("VulnoraIQ WebUI is ready.")
        webbrowser.open(WEBUI_URL)
    else:
        print(
            f"VulnoraIQ did not become ready within {POLL_TIMEOUT:.0f}s.\n"
            f"Check `docker compose logs` for errors.\n"
            f"Once fixed, open {WEBUI_URL} manually."
        )


if __name__ == "__main__":
    main()
