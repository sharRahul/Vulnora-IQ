from __future__ import annotations

from benchmarks.run_benchmarks import run_benchmarks, write_result


def test_demo_benchmarks_pass(tmp_path) -> None:
    result = run_benchmarks(output_dir=tmp_path / "reports")

    assert result.status == "pass"
    assert result.benchmark_count == 3
    assert result.failed_count == 0


def test_benchmark_summary_written(tmp_path) -> None:
    result = run_benchmarks(output_dir=tmp_path / "reports")
    output = write_result(result, tmp_path / "summary.json")

    assert output.exists()
    assert "benchmark_count" in output.read_text(encoding="utf-8")
