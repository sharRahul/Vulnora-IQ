from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHERS = [
    ROOT / "launch-vulnoraiq-webui.bat",
    ROOT / "launch-vulnoraiq-webui.command",
    ROOT / "launch-vulnoraiq-webui.sh",
]


def test_platform_launchers_run_docker_startup_flow() -> None:
    for launcher in LAUNCHERS:
        text = launcher.read_text(encoding="utf-8")
        assert "VulnoraIQ" in text
        assert "docker info" in text
        assert "docker compose build" in text
        assert "docker compose up -d" in text
        assert "docker compose ps" in text
        assert "vulnoraiq-web" in text
        assert "127.0.0.1:8787" in text
        assert "bootstrap_launch.py" not in text


def test_bootstrap_remains_available_for_python_launcher_flow() -> None:
    bootstrap = (ROOT / "scripts" / "bootstrap_launch.py").read_text(encoding="utf-8")

    assert "docker" in bootstrap
    assert "compose" in bootstrap
    assert "docker-compose.yml" in bootstrap
    assert "http://127.0.0.1:8787" in bootstrap
    assert "webbrowser.open" in bootstrap
    assert "docker compose logs vulnoraiq-web" in bootstrap


def test_readme_documents_double_click_launcher_flow() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "launch-vulnoraiq-webui.bat" in readme
    assert "launch-vulnoraiq-webui.command" in readme
    assert "launch-vulnoraiq-webui.sh" in readme
    assert "browser GUI" in readme
    assert "No host Python install is required" in readme
    assert "docker compose build" in readme
    assert "docker compose up -d" in readme
