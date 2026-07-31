# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for Prime work-intent batching in dispatcher daemon."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = str(_REPO_ROOT / "scripts")
_TESTS_DIR = str(_REPO_ROOT / "platform_tests" / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from bridge_work_intent_registry import acquire, current_holder  # noqa: E402
from test_dispatcher_runtime import (  # noqa: E402
    _CODEX_INVOCATION_SURFACES,
    _make_synthetic_project,
    _rec,
    _write_bridge_file,
    _write_registry,
)
from test_dispatcher_runtime import (  # noqa: E402
    _load_trigger as _load_base_trigger,
)


def _write_index(project_root: Path, content: str) -> None:
    (project_root / "bridge").mkdir(parents=True, exist_ok=True)
    (project_root / "bridge" / "INDEX.md").write_text(content, encoding="utf-8")


_BRIDGE_KIND_BODY = (
    "bridge_kind: implementation_proposal\n"
    'target_paths: ["scripts/dispatcher_runtime.py"]\n'
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


def _bridge_kind_body(target_paths: list[str] | None = None) -> str:
    if target_paths is None:
        return _BRIDGE_KIND_BODY
    return _BRIDGE_KIND_BODY.replace(
        'target_paths: ["scripts/dispatcher_runtime.py"]',
        f"target_paths: {json.dumps(target_paths)}",
    )


class _FakeProcess:
    pid = 4242


def _fake_popen(*_args, **_kwargs) -> _FakeProcess:
    return _FakeProcess()


@pytest.fixture(autouse=True)
def _select_fixture_worker_documents(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GTKB_HARNESS_NAME", "fixture")
    work_intents = sys.modules["bridge_work_intent_registry"]
    real_acquire = work_intents.acquire

    def _acquire_with_worker_document(
        slug: str,
        session_id: str,
        ttl_seconds: int = 30,
        *,
        project_root: Path | None = None,
    ) -> bool:
        if project_root is not None:
            _write_prime_worker_session(project_root, session_id)
        return real_acquire(slug, session_id, ttl_seconds=ttl_seconds, project_root=project_root)

    monkeypatch.setattr(work_intents, "acquire", _acquire_with_worker_document)


def _write_prime_worker_session(root: Path, session_id: str) -> None:
    document = {
        "status": "open",
        "session_id": session_id,
        "harness_id": "T",
        "harness_name": "fixture",
        "worker_role_provenance": {
            "schema_version": 1,
            "session_id": session_id,
            "harness_id": "T",
            "harness_name": "fixture",
            "role": "prime-builder",
            "role_resolution_source": "test-fixture",
            "issued_at": "2026-07-11T00:00:00Z",
            "dispatch_run_id": None,
        },
    }
    path = root / "harness-state" / "fixture" / "session-envelopes" / f"{session_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def _load_trigger():
    trigger = _load_base_trigger()
    # Keep launcher Popen fakes local to this dispatcher module instance.
    trigger.subprocess = SimpleNamespace(**vars(trigger.subprocess))
    return trigger


def _index_with_go_documents(
    root: Path,
    *slugs: str,
    target_paths_by_slug: dict[str, list[str]] | None = None,
) -> str:
    chunks = ["# bridge index\n"]
    for slug in slugs:
        target_paths = target_paths_by_slug.get(slug) if target_paths_by_slug else None
        _write_bridge_file(
            root,
            f"{slug}-001.md",
            "NEW\n\nauthor_session_context_id: fixture-author-session\n\n" + _bridge_kind_body(target_paths),
        )
        _write_bridge_file(
            root,
            f"{slug}-002.md",
            "GO\n\nauthor_session_context_id: fixture-go-session\n\n" + _bridge_kind_body(target_paths),
        )
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


def _suppression_records(state_dir: Path) -> list[dict[str, object]]:
    path = state_dir / "dispatch-suppressions.jsonl"
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
    _write_prime_worker_session(root, "foreground-session")
    assert acquire("held-thread", "foreground-session", ttl_seconds=120, project_root=root)

    trigger = _load_trigger()
    monkeypatch.setattr(trigger.subprocess, "Popen", _fake_popen)

    selected = _prime_selected(trigger, root, max_items=2)
    expected_unheld = [item for item in selected if item.document_name == "free-thread"]
    expected_signature = trigger._signature(expected_unheld)

    summary = trigger.run_dispatch_cycle(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

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
    assert result["work_intent_session_id"] == result["dispatch_id"]
    assert free["session_id"] == result["work_intent_session_id"]

    suppressions = _suppression_records(state_dir)
    assert any(
        record.get("reason") == "work_intent_already_held"
        and record.get("document_name") == "held-thread"
        and record.get("holder_session_id") == "foreground-session"
        for record in suppressions
    )


def test_prime_dispatch_suppresses_same_batch_target_path_overlap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4996: overlapping GO items in one batch launch only the oldest eligible one."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    shared_target = "scripts/shared.py"
    _write_index(
        root,
        _index_with_go_documents(
            root,
            "first-thread",
            "second-thread",
            target_paths_by_slug={
                "first-thread": [shared_target],
                "second-thread": [shared_target],
            },
        ),
    )
    trigger = _load_trigger()
    monkeypatch.setattr(trigger.subprocess, "Popen", _fake_popen)
    selected = _prime_selected(trigger, root, max_items=2)
    assert len(selected) == 2
    launched_doc = selected[0].document_name
    suppressed_doc = selected[1].document_name

    summary = trigger.run_dispatch_cycle(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

    result = summary["results"]["prime-builder"]
    assert result["launched"] is True
    rec = summary["dispatch_state"]["recipients"]["prime-builder"]
    assert rec["selected_count"] == 1
    assert rec["target_path_overlap_filtered_count"] == 1
    assert current_holder(launched_doc, project_root=root) is not None
    assert current_holder(suppressed_doc, project_root=root) is None
    assert any(
        record.get("reason") == "target_path_overlap_selected"
        and record.get("document_name") == suppressed_doc
        and record.get("overlap_with_document_name") == launched_doc
        and shared_target in record.get("overlapping_targets", [])
        for record in _suppression_records(state_dir)
    )


def test_prime_dispatch_keeps_disjoint_go_items_fanning_out_to_cap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4996: target serialization preserves normal fan-out for disjoint paths."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(
        root,
        _index_with_go_documents(
            root,
            "first-thread",
            "second-thread",
            target_paths_by_slug={
                "first-thread": ["scripts/first.py"],
                "second-thread": ["platform_tests/scripts/test_second.py"],
            },
        ),
    )
    trigger = _load_trigger()
    monkeypatch.setattr(trigger.subprocess, "Popen", _fake_popen)

    summary = trigger.run_dispatch_cycle(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

    result = summary["results"]["prime-builder"]
    assert result["launched"] is True
    rec = summary["dispatch_state"]["recipients"]["prime-builder"]
    assert rec["selected_count"] == 2
    assert rec["target_path_overlap_filtered_count"] == 0
    assert current_holder("first-thread", project_root=root) is not None
    assert current_holder("second-thread", project_root=root) is not None
    assert not any(
        record.get("reason") in {"target_path_overlap_selected", "target_path_overlap_inflight"}
        for record in _suppression_records(state_dir)
    )


def test_prime_dispatch_suppresses_later_tick_inflight_target_path_overlap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4996: a later GO item is suppressed when an in-flight packet reserves its path."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    shared_target = "scripts/shared.py"
    _write_index(
        root,
        _index_with_go_documents(
            root,
            "inflight-thread",
            target_paths_by_slug={"inflight-thread": [shared_target]},
        ),
    )
    trigger = _load_trigger()
    packet = trigger.create_authorization_packet(root, "inflight-thread")
    trigger.write_named_packet(root, packet, "inflight-thread")
    _write_prime_worker_session(root, "foreground-session")
    assert acquire("inflight-thread", "foreground-session", ttl_seconds=120, project_root=root)
    _write_index(
        root,
        _index_with_go_documents(
            root,
            "later-thread",
            target_paths_by_slug={"later-thread": [shared_target]},
        ),
    )
    popen_calls: list[object] = []

    def _unexpected_popen(*args, **kwargs):
        popen_calls.append((args, kwargs))
        return _FakeProcess()

    monkeypatch.setattr(trigger.subprocess, "Popen", _unexpected_popen)

    summary = trigger.run_dispatch_cycle(project_root=root, state_dir=state_dir, max_items=1, dry_run=False)

    assert popen_calls == []
    result = summary["results"]["prime-builder"]
    assert result["launched"] is False
    assert result["reason"] == "target_path_overlap_inflight"
    rec = summary["dispatch_state"]["recipients"]["prime-builder"]
    assert rec["selected_count"] == 0
    assert rec["target_path_overlap_filtered_count"] == 1
    assert current_holder("later-thread", project_root=root) is None
    assert any(
        record.get("reason") == "target_path_overlap_inflight"
        and record.get("document_name") == "later-thread"
        and "inflight-thread" in str(record.get("collision_reason", ""))
        for record in _suppression_records(state_dir)
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

    summary = trigger.run_dispatch_cycle(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

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

    summary = trigger.run_dispatch_cycle(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

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

    summary = trigger.run_dispatch_cycle(project_root=root, state_dir=state_dir, max_items=2, dry_run=False)

    assert summary["results"]["loyal-opposition"]["launched"] is True
    assert current_holder("review-thread", project_root=root)["session_id"] == "foreground-session"
    assert not any(record.get("reason") == "work_intent_already_held" for record in _failure_records(state_dir))


def test_dispatcher_mediated_codex_exec_composition_remains_launchable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4988: dispatcher-owned Popen is outside the interactive shell guard."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(root, [_rec("A", "codex", ["prime-builder"], "active", _CODEX_INVOCATION_SURFACES)])
    _write_index(root, _index_with_go_documents(root, "codex-dispatch-thread"))
    trigger = _load_trigger()
    popen_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def _capture_popen(*args, **kwargs) -> _FakeProcess:
        popen_calls.append((args, kwargs))
        return _FakeProcess()

    monkeypatch.setattr(trigger.subprocess, "Popen", _capture_popen)

    summary = trigger.run_dispatch_cycle(project_root=root, state_dir=state_dir, max_items=1, dry_run=False)

    result = summary["results"]["prime-builder"]
    assert result["launched"] is True
    assert result["recipient"] == "prime-builder:A"
    assert popen_calls
    wrapped_command = None
    for _args, kwargs in popen_calls:
        env = kwargs.get("env") or {}
        if trigger.RUN_WITH_STATUS_CONFIG_ENV_VAR in env:
            import base64
            import json

            raw = base64.b64decode(env[trigger.RUN_WITH_STATUS_CONFIG_ENV_VAR])
            config = json.loads(raw.decode("utf-8"))
            cmd_args = config.get("cmd_args")
            if cmd_args and any(
                str(part).replace("\\", "/").rsplit("/", 1)[-1].lower().startswith("codex") for part in cmd_args
            ):
                wrapped_command = cmd_args
                break
    assert wrapped_command is not None
    codex_index = next(
        index
        for index, part in enumerate(wrapped_command)
        if str(part).replace("\\", "/").rsplit("/", 1)[-1].lower().startswith("codex")
    )
    assert wrapped_command[codex_index + 1] == "exec"
    assert "--cd" in wrapped_command
