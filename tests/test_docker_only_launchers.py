from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHERS = [
    ROOT / "launch-vulnoraiq-webui.bat",
    ROOT / "launch-vulnoraiq-webui.command",
    ROOT / "launch-vulnoraiq-webui.sh",
]


def test_launchers_run_docker_compose_directly() -> None:
    for launcher in LAUNCHERS:
        content = launcher.read_text(encoding="utf-8")
        assert "docker compose build" in content
        assert "docker compose up -d" in content
        assert "docker compose ps" in content
        assert "bootstrap_launch.py" not in content
