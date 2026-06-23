from __future__ import annotations

import zipfile
from pathlib import Path

from scripts.build_platform_release_package import build_platform_package


def test_build_platform_release_package_creates_expected_archive(tmp_path: Path) -> None:
    package = build_platform_package("linux", version="0.2.0-test", output_dir=tmp_path)

    assert package.output.exists()
    assert package.output.name == "vulnoraiq-0.2.0-test-linux.zip"
    assert package.file_count > 1

    with zipfile.ZipFile(package.output) as archive:
        names = set(archive.namelist())

    prefix = "vulnoraiq-0.2.0-test-linux/"
    assert f"{prefix}START_HERE.txt" in names
    assert f"{prefix}README.md" in names
    assert f"{prefix}ACCEPTABLE_USE.md" in names
    assert f"{prefix}LICENSE" in names
    assert f"{prefix}launch-vulnoraiq-webui.py" in names
    assert f"{prefix}launch-vulnoraiq-webui.sh" in names
    assert f"{prefix}config/targets.yaml" in names
    assert f"{prefix}examples/local_demo_targets/owasp_fixture_targets.py" in names
    assert f"{prefix}webui/static/index.html" in names
    assert all("reports/output" not in name for name in names)
    assert all("__pycache__" not in name for name in names)
