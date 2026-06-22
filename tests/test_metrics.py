from __future__ import annotations

from webui.hosted_server import _get_metrics_snapshot, _inc_metric


def test_metrics_counters_increment() -> None:
    _inc_metric("test_counter")
    snapshot = _get_metrics_snapshot()
    assert snapshot.get("test_counter", 0) >= 1


def test_metrics_contains_expected_keys() -> None:
    snapshot = _get_metrics_snapshot()
    expected = ["active_scans"]
    for key in expected:
        assert key in snapshot


def test_metrics_active_scans_non_negative() -> None:
    snapshot = _get_metrics_snapshot()
    assert snapshot.get("active_scans", 0) >= 0


def test_metrics_thread_safe() -> None:
    import threading
    errors: list[Exception] = []

    def increment() -> None:
        try:
            for _ in range(100):
                _inc_metric("thread_test")
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
    snapshot = _get_metrics_snapshot()
    assert snapshot.get("thread_test", 0) >= 900  # some might not finish
