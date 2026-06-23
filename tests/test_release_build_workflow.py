from __future__ import annotations

from pathlib import Path


def test_release_build_workflow_is_not_normal_ci() -> None:
    workflow = Path(".github/workflows/release-build.yml").read_text(encoding="utf-8")

    assert "name: Build Release Artifacts" in workflow
    assert "workflow_dispatch:" in workflow
    assert "release:" in workflow
    assert "types: [published]" in workflow
    assert "  push:" not in workflow
    assert "  pull_request:" not in workflow


def test_release_build_workflow_builds_all_target_platforms() -> None:
    workflow = Path(".github/workflows/release-build.yml").read_text(encoding="utf-8")

    assert "platform: windows" in workflow
    assert "platform: linux" in workflow
    assert "platform: macos" in workflow
    assert "windows-latest" in workflow
    assert "ubuntu-latest" in workflow
    assert "macos-latest" in workflow
