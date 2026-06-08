from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cross_harness_bridge_trigger as cht  # noqa: E402


def test_poll_dispatch_verdict_returns_path_and_latency_on_existing_file(tmp_path: Path) -> None:
    bridge_id = "test-doc"
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (tmp_path / "groundtruth.toml").write_text("[project]\n", encoding="utf-8")

    dispatch_ts = time.time()
    time.sleep(0.05)

    verdict_file = bridge_dir / f"gtkb-{bridge_id}-002.md"
    verdict_file.write_text("verdict", encoding="utf-8")

    # Touch file to ensure its mtime is definitely >= dispatch_ts
    verdict_file.touch()

    path, latency = cht._poll_dispatch_verdict(
        dispatch_ts=dispatch_ts,
        bridge_id=bridge_id,
        project_root=tmp_path,
        timeout=2.0,
        poll_interval=0.05,
    )

    assert path == f"bridge/{verdict_file.name}"
    assert latency is not None
    assert latency >= 0.0


def test_poll_dispatch_verdict_returns_none_on_timeout(tmp_path: Path) -> None:
    bridge_id = "test-doc"
    (tmp_path / "groundtruth.toml").write_text("[project]\n", encoding="utf-8")
    (tmp_path / "bridge").mkdir()

    dispatch_ts = time.time()

    path, latency = cht._poll_dispatch_verdict(
        dispatch_ts=dispatch_ts,
        bridge_id=bridge_id,
        project_root=tmp_path,
        timeout=0.1,
        poll_interval=0.05,
    )

    assert path is None
    assert latency is None


def test_post_dispatch_poll_thread_is_daemon(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import threading

    created_threads = []
    orig_thread = threading.Thread

    def spy_thread(*args, **kwargs):
        t = orig_thread(*args, **kwargs)
        created_threads.append(t)
        return t

    monkeypatch.setattr(threading, "Thread", spy_thread)

    cht._post_dispatch_poll(
        dispatch_id="d1",
        bridge_id="b1",
        dispatch_ts=time.time(),
        project_root=tmp_path,
        state_dir=tmp_path / "state",
    )

    assert len(created_threads) == 1
    assert created_threads[0].daemon is True


def test_post_dispatch_poll_writes_to_dedicated_jsonl(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    monkeypatch.setattr(cht, "_poll_dispatch_verdict", lambda *a, **kw: ("bridge/gtkb-b1-002.md", 1.5))

    cht._poll_and_log_verdict(
        dispatch_id="d1",
        bridge_id="b1",
        dispatch_ts=time.time(),
        project_root=tmp_path,
        state_dir=state_dir,
    )

    log_file = state_dir / "dispatch-diagnostic-post.jsonl"
    assert log_file.is_file()
    records = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]

    assert len(records) == 1
    assert records[0]["dispatch_id"] == "d1"
    assert records[0]["bridge_id"] == "b1"
    assert records[0]["verdict_path"] == "bridge/gtkb-b1-002.md"
    assert records[0]["verdict_latency_seconds"] == 1.5
    assert "dispatch_timestamp" in records[0]
    assert "timestamp" in records[0]


def test_diagnostic_record_schema_extension_is_additive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Verifies that trigger-diagnostic.jsonl is kept isolated and is not polluted
    # by background polling logs.
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    monkeypatch.setattr(cht, "_poll_dispatch_verdict", lambda *a, **kw: ("bridge/gtkb-b1-002.md", 1.5))

    cht._poll_and_log_verdict(
        dispatch_id="d1",
        bridge_id="b1",
        dispatch_ts=time.time(),
        project_root=tmp_path,
        state_dir=state_dir,
    )

    # Assert that trigger-diagnostic.jsonl does not exist or is empty
    diag_file = state_dir / "trigger-diagnostic.jsonl"
    assert not diag_file.exists()
