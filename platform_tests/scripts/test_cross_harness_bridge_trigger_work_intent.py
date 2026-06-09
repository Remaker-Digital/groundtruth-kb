# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for Prime work-intent batching in cross-harness trigger."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = str(_REPO_ROOT / "scripts")
_TESTS_DIR = str(_REPO_ROOT / "platform_tests" / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from bridge_work_intent_registry import acquire, current_holder  # noqa: E402
from test_cross_harness_bridge_trigger import (  # noqa: E402
    _load_trigger,
    _make_synthetic_project,
    _write_bridge_file,
    _write_index,
)

_BRIDGE_KIND_BODY = (
    "bridge_kind: implementation_proposal\n"
    'target_paths: ["scripts/cross_harness_bridge_trigger.py"]\n'
    "\n"
    "## Specification Links\n"
    "\n"
    "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    "\n"
    "## Requirement Sufficiency\n"
    "\n"
    "Existing requirements are sufficient.\n"
    "\n"
    "## Spec-derived verification plan\n"
    "\n"
    "Run focused dispatch tests.\n"
)


class _FakeProcess:
    pid = 4242


def _fake_popen(*_args, **_kwargs) -> _FakeProcess:
    return _FakeProcess()


def _index_with_go_documents(root: Path, *slugs: str) -> str:
    chunks = ["# bridge index\n"]
    for slug in slugs:
        _write_bridge_file(root, f"{slug}-001.md", _BRIDGE_KIND_BODY)
        _write_bridge_file(root, f"{slug}-002.md", _BRIDGE_KIND_BODY)
        chunks.append(f"\nDocument: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}-001.md\n")
    return "".join(chunks)


def _prime_selected(trigger, root: Path, max_items: int = 2) -> list[object]:
    index_text = (root / "bridge" / "INDEX.md").read_text(encoding="utf-8")
    prime_items, _ = trigger._compute_actionable(index_text, root)
    filtered = [item for item in prime_items if getattr(item, "dispatchable", True)]
    return trigger._selected_oldest_first(filtered, max_items)


def _failure_records(state_dir: Path) -> list[dict[str, object]]:
    path = state_dir / "dispatch-failures.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_prime_dispatch_filters_held_work_intent_and_signs_unheld_batch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_go_documents(root, "held-thread", "free-thread"))
    assert acquire("held-thread", "foreground-session", ttl_seconds=120, project_root=root)

    trigger = _load_trigger()
    monkeypatch.setattr(trigger.subprocess, "Popen", _fake_popen)

    selected = _prime_selected(trigger, root, max_items=2)
    expected_unheld = [item for item in selected if item.document_name == "free-thread"]
    expected_signature = trigger._signature(expected_unheld)

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

    result = summary["results"]["prime-builder"]
    assert result["launched"] is True
    rec = summary["dispatch_state"]["recipients"]["prime-builder"]
    assert rec["signature"] == expected_signature
    assert rec["last_dispatched_signature"] == expected_signature
    assert rec["selected_count"] == 1
    assert rec["work_intent_held_filtered_count"] == 1

    held = current_holder("held-thread", project_root=root)
    free = current_holder("free-thread", project_root=root)
    assert held is not None and held["session_id"] == "foreground-session"
    assert free is not None
    assert free["session_id"].startswith("trigger-dispatched-")

    failures = _failure_records(state_dir)
    assert any(
        record.get("reason") == "work_intent_already_held"
        and record.get("document_name") == "held-thread"
        and record.get("holder_session_id") == "foreground-session"
        for record in failures
    )


def test_prime_acquire_failure_releases_batch_and_preserves_signature(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_go_documents(root, "first-thread", "second-thread"))
    state_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at": "2026-06-01T00:00:00+00:00",
                "recipients": {
                    "prime-builder": {
                        "signature": "prior-signature",
                        "last_dispatched_signature": "prior-signature",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    trigger = _load_trigger()
    popen_calls: list[object] = []

    def _unexpected_popen(*args, **kwargs):
        popen_calls.append((args, kwargs))
        return _FakeProcess()

    real_acquire = trigger.acquire_work_intent

    def _fail_second(slug: str, session_id: str, ttl_seconds: int = 30, *, project_root: Path | None = None) -> bool:
        if slug == "second-thread":
            return False
        return real_acquire(slug, session_id, ttl_seconds=ttl_seconds, project_root=project_root)

    monkeypatch.setattr(trigger.subprocess, "Popen", _unexpected_popen)
    monkeypatch.setattr(trigger, "acquire_work_intent", _fail_second)

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

    assert popen_calls == []
    result = summary["results"]["prime-builder"]
    assert result["launched"] is False
    assert result["reason"] == "work_intent_acquire_failed"
    rec = summary["dispatch_state"]["recipients"]["prime-builder"]
    assert rec["last_dispatched_signature"] == "prior-signature"
    assert rec["signature"] == "prior-signature"
    assert current_holder("first-thread", project_root=root) is None
    assert current_holder("second-thread", project_root=root) is None
    assert any(
        record.get("reason") == "work_intent_acquire_failed" and record.get("document_name") == "second-thread"
        for record in _failure_records(state_dir)
    )


def test_prime_spawn_failure_releases_claims_and_preserves_signature(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_go_documents(root, "spawn-fail-thread"))
    state_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at": "2026-06-01T00:00:00+00:00",
                "recipients": {
                    "prime-builder": {
                        "signature": "prior-signature",
                        "last_dispatched_signature": "prior-signature",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    trigger = _load_trigger()

    def _fail_spawn(*_args, **_kwargs):
        raise OSError("simulated prime spawn failure")

    monkeypatch.setattr(trigger.subprocess, "Popen", _fail_spawn)

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

    result = summary["results"]["prime-builder"]
    assert result["launched"] is False
    assert result["error_message"] == "simulated prime spawn failure"
    rec = summary["dispatch_state"]["recipients"]["prime-builder"]
    assert rec["last_dispatched_signature"] == "prior-signature"
    assert rec["signature"] == "prior-signature"
    assert current_holder("spawn-fail-thread", project_root=root) is None


def test_loyal_opposition_dispatch_ignores_work_intent_holders(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_bridge_file(root, "review-thread-001.md", _BRIDGE_KIND_BODY)
    _write_index(root, "# bridge index\n\nDocument: review-thread\nNEW: bridge/review-thread-001.md\n")
    assert acquire("review-thread", "foreground-session", ttl_seconds=120, project_root=root)

    trigger = _load_trigger()
    monkeypatch.setattr(trigger.subprocess, "Popen", _fake_popen)

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

    assert summary["results"]["loyal-opposition"]["launched"] is True
    assert current_holder("review-thread", project_root=root)["session_id"] == "foreground-session"
    assert not any(record.get("reason") == "work_intent_already_held" for record in _failure_records(state_dir))
