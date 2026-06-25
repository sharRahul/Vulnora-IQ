from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_platform_launchers_delegate_to_bootstrap() -> None:
    launchers = [
        ROOT / "launch-vulnoraiq-webui.bat",
        ROOT / "launch-vulnoraiq-webui.command",
        ROOT / "launch-vulnoraiq-webui.sh",
    ]
    for launcher in launchers:
        text = launcher.read_text(encoding="utf-8")
        assert "scripts" in text
        assert "bootstrap_launch.py" in text
        assert "VulnoraIQ" in text
        assert "docker compose down" in text or "Docker" in text


def test_bootstrap_runs_docker_browser_launcher_flow() -> None:
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
    assert "scripts/bootstrap_launch.py" in readme
