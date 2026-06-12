"""FAB-13 runtime evidence retention tests."""

from __future__ import annotations

import importlib.util
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

from groundtruth_kb.session import envelope

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_DECISION_TRACKER = REPO_ROOT / ".claude" / "hooks" / "owner-decision-tracker.py"
TRIGGER = REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py"


def _load_module(path: Path, name: str) -> ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_owner_tracker() -> ModuleType:
    return _load_module(OWNER_DECISION_TRACKER, "fab13_owner_decision_tracker")


def _load_trigger() -> ModuleType:
    return _load_module(TRIGGER, "fab13_cross_harness_bridge_trigger")


def _write_retention_config(project_root: Path) -> None:
    config_dir = project_root / "config" / "governance"
    config_dir.mkdir(parents=True)
    (config_dir / "runtime-evidence-retention.toml").write_text(
        "[owner_decision_ledger]\narchive_resolved_after_days = 30\n",
        encoding="utf-8",
    )


def test_owner_decision_retention_archives_after_da_harvest(tmp_path: Path, monkeypatch) -> None:
    tracker = _load_owner_tracker()
    monkeypatch.setattr(tracker, "PROJECT_ROOT", tmp_path)
    _write_retention_config(tmp_path)

    call_order: list[str] = []

    def fake_archive(entry) -> bool:  # type: ignore[no-untyped-def]
        assert not (tmp_path / "memory" / "archive").exists(), "sidecar write must happen after DA harvest"
        call_order.append(entry.id)
        return True

    monkeypatch.setattr(tracker, "_archive_decision_for_retention", fake_archive)

    old = tracker.DecisionEntry(
        id="DECISION-0001",
        asked_at="2026-05-01T00:00:00Z",
        question="Old question?",
        status="resolved",
        resolved_at="2026-05-02T00:00:00Z",
        answer="Old answer",
    )
    recent = tracker.DecisionEntry(
        id="DECISION-0002",
        asked_at="2026-06-10T00:00:00Z",
        question="Recent question?",
        status="resolved",
        resolved_at="2026-06-10T00:00:00Z",
        answer="Recent answer",
    )
    historical = tracker.DecisionEntry(
        id="DECISION-0003",
        asked_at="2026-04-01T00:00:00Z",
        question="Historical question?",
        status="resolved",
        resolved_at="2026-04-02T00:00:00Z",
        answer="Historical answer",
    )
    sections = {"pending": [], "resolved": [old, recent], "history": [historical]}

    mutated = tracker._rotate_resolved_decisions_for_retention(
        sections,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert mutated is True
    assert sections["resolved"] == [recent]
    assert sections["history"] == []
    assert call_order == ["DECISION-0001", "DECISION-0003"]

    archive_202605 = (tmp_path / "memory" / "archive" / "pending-owner-decisions-202605.md").read_text(encoding="utf-8")
    archive_202604 = (tmp_path / "memory" / "archive" / "pending-owner-decisions-202604.md").read_text(encoding="utf-8")
    assert "DECISION-0001" in archive_202605
    assert "Old question?" in archive_202605
    assert "DECISION-0003" in archive_202604
    assert "Historical question?" in archive_202604


def test_owner_decision_retention_keeps_entry_live_when_da_harvest_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    tracker = _load_owner_tracker()
    monkeypatch.setattr(tracker, "PROJECT_ROOT", tmp_path)
    _write_retention_config(tmp_path)
    monkeypatch.setattr(tracker, "_archive_decision_for_retention", lambda _entry: False)

    old = tracker.DecisionEntry(
        id="DECISION-0004",
        asked_at="2026-05-01T00:00:00Z",
        question="Blocked archive?",
        status="resolved",
        resolved_at="2026-05-02T00:00:00Z",
        answer="Keep me live",
    )
    sections = {"pending": [], "resolved": [old], "history": []}

    mutated = tracker._rotate_resolved_decisions_for_retention(
        sections,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert mutated is False
    assert sections["resolved"] == [old]
    assert not (tmp_path / "memory" / "archive").exists()


def test_jsonl_rotation_keeps_five_rollovers(tmp_path: Path) -> None:
    trigger = _load_trigger()
    target = tmp_path / "dispatch-failures.jsonl"

    for index in range(7):
        target.write_text(f"segment {index}\n" + ("x" * 20), encoding="utf-8")
        trigger._rotate_jsonl_if_needed(target, max_bytes=10, max_rollovers=5)

    assert not target.exists()
    for index in range(1, 6):
        assert (tmp_path / f"dispatch-failures.jsonl.{index}").is_file()
    assert not (tmp_path / "dispatch-failures.jsonl.6").exists()
    assert "segment 6" in (tmp_path / "dispatch-failures.jsonl.1").read_text(encoding="utf-8")


def test_dispatch_runs_prune_preserves_live_pid_artifacts(tmp_path: Path) -> None:
    trigger = _load_trigger()
    runs_dir = tmp_path / "dispatch-runs"
    runs_dir.mkdir()
    now = time.time()

    old = runs_dir / "old.stdout.log"
    old.write_text("old", encoding="utf-8")
    os.utime(old, (now - 20 * 86400, now - 20 * 86400))

    recent_a = runs_dir / "a.stdout.log"
    recent_a.write_text("a" * 12, encoding="utf-8")
    os.utime(recent_a, (now - 100, now - 100))
    recent_b = runs_dir / "b.stdout.log"
    recent_b.write_text("b" * 12, encoding="utf-8")
    os.utime(recent_b, (now - 50, now - 50))

    live_pid = runs_dir / "live.pid"
    live_log = runs_dir / "live.stdout.log"
    live_pid.write_text(str(os.getpid()), encoding="utf-8")
    live_log.write_text("live" * 10, encoding="utf-8")
    os.utime(live_pid, (now - 1000, now - 1000))
    os.utime(live_log, (now - 1000, now - 1000))

    result = trigger._prune_dispatch_runs(
        runs_dir,
        max_age_days=14,
        max_total_bytes=16,
        now_epoch=now,
    )

    assert result["deleted_count"] >= 2
    assert not old.exists()
    assert not recent_a.exists()
    assert recent_b.exists()
    assert live_pid.exists()
    assert live_log.exists()


def test_session_envelope_git_status_is_bounded(monkeypatch, tmp_path: Path) -> None:
    class Result:
        returncode = 0
        stdout = "\n".join(f" M file_{index}.py" for index in range(5))

    monkeypatch.setattr(envelope, "GIT_STATUS_SHORT_LINE_LIMIT", 3)
    monkeypatch.setattr(envelope.subprocess, "run", lambda *args, **kwargs: Result())

    status = envelope._git_status(tmp_path)

    assert status["dirty"] is True
    assert status["short_line_count"] == 5
    assert status["short_line_limit"] == 3
    assert status["short_truncated"] is True
    assert status["short"].splitlines() == [" M file_0.py", " M file_1.py", " M file_2.py"]
