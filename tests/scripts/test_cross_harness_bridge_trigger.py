# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/cross_harness_bridge_trigger.py.

Per ``bridge/gtkb-bridge-poller-event-driven-replacement-003.md`` Slice 2
test plan (T-2-* rows). 8 tests cover signature computation, dispatch-state
idempotence, repeated-fire on unchanged signature, dispatch on changed
signature, loop-prevention env var, fire-and-forget exit semantics,
uncommitted INDEX edit triggers dispatch, and stale latest-commit replay
does NOT trigger.

Slice 2 is non-live: tests exercise the script directly. Slice 3 lands the
hook registrations once Slice 1 is VERIFIED.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"


def _load_trigger() -> ModuleType:
    """Load scripts/cross_harness_bridge_trigger.py with sys.modules registration."""
    assert _SCRIPT_PATH.is_file(), f"Expected trigger at {_SCRIPT_PATH}"
    module_name = "cross_harness_bridge_trigger"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _make_synthetic_project(root: Path) -> Path:
    """Create a minimal in-root synthetic GT-KB project with a bridge/ dir.

    Returns ``root``. Creates ``groundtruth.toml`` so resolver is satisfied,
    and ``bridge/INDEX.md`` for the trigger to read.
    """
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestSynthetic"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (root / "bridge").mkdir(exist_ok=True)
    return root


def _write_index(root: Path, body: str) -> None:
    (root / "bridge" / "INDEX.md").write_text(body, encoding="utf-8")


def _write_bridge_file(root: Path, name: str, body: str = "# placeholder\n") -> None:
    """Create a referenced bridge file so ``compute_actionable_pending`` keeps it."""
    (root / "bridge" / name).write_text(body, encoding="utf-8")


def _index_with_one_new(root: Path, doc: str = "example-thread") -> str:
    """Build an INDEX with one NEW entry and create the referenced file."""
    _write_bridge_file(root, f"{doc}-001.md", "bridge_kind: implementation_proposal\n")
    return f"# bridge index\n\nDocument: {doc}\nNEW: bridge/{doc}-001.md\n"


def _index_with_one_go(root: Path, doc: str = "example-thread") -> str:
    """Build an INDEX whose top status is GO (Prime-actionable)."""
    _write_bridge_file(root, f"{doc}-001.md", "bridge_kind: implementation_proposal\n")
    _write_bridge_file(root, f"{doc}-002.md", "bridge_kind: implementation_proposal\n")
    return (
        f"# bridge index\n\nDocument: {doc}\n"
        f"GO: bridge/{doc}-002.md\n"
        f"NEW: bridge/{doc}-001.md\n"
    )


# ──────────────────────────────────────────────────────────────────────────
# T-2-signature-computation
# ──────────────────────────────────────────────────────────────────────────


def test_signature_computation_is_deterministic_per_recipient(tmp_path: Path) -> None:
    """T-2-signature-computation: signature deterministic per recipient
    given identical INDEX state.

    Maps to ``_signature`` byte-equivalence with smart-poller normalization.
    """
    root = _make_synthetic_project(tmp_path)
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    state_dir_a = tmp_path / "state-a"
    state_dir_b = tmp_path / "state-b"

    summary_a = trigger.run_trigger(
        project_root=root, state_dir=state_dir_a, dry_run=True
    )
    summary_b = trigger.run_trigger(
        project_root=root, state_dir=state_dir_b, dry_run=True
    )

    sig_a = summary_a["dispatch_state"]["recipients"]["codex"]["signature"]
    sig_b = summary_b["dispatch_state"]["recipients"]["codex"]["signature"]
    assert sig_a == sig_b
    # And the signature is non-empty (we have a NEW entry).
    assert sig_a != trigger._signature([])


# ──────────────────────────────────────────────────────────────────────────
# T-2-uncommitted-INDEX-triggers
# ──────────────────────────────────────────────────────────────────────────


def test_uncommitted_index_edit_triggers_dispatch(tmp_path: Path) -> None:
    """T-2-uncommitted-INDEX-triggers: live-INDEX-signature dispatch reads the
    working tree, NOT committed state.

    No git involvement: a written-but-not-committed INDEX still drives dispatch
    because the predicate is the file's bytes on disk (per Codex F1 fix on
    REVISED-1).
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"

    # Empty INDEX → no dispatch.
    _write_index(root, "# empty\n")
    trigger = _load_trigger()
    summary_empty = trigger.run_trigger(
        project_root=root, state_dir=state_dir, dry_run=True
    )
    assert summary_empty["results"]["codex"]["reason"] == "no_pending"

    # Add a NEW entry (uncommitted edit) → dispatch fires.
    _write_index(root, _index_with_one_new(root))
    summary_new = trigger.run_trigger(
        project_root=root, state_dir=state_dir, dry_run=True
    )
    # dry_run=True → "launched" stays False, but reason is "dry_run" not "no_pending"
    # which proves the dispatch path was entered.
    assert summary_new["results"]["codex"]["reason"] == "dry_run"


# ──────────────────────────────────────────────────────────────────────────
# T-2-stale-commit-no-replay
# ──────────────────────────────────────────────────────────────────────────


def test_unchanged_signature_does_not_replay(tmp_path: Path) -> None:
    """T-2-stale-commit-no-replay: when INDEX is unchanged between trigger
    fires, the second invocation MUST NOT redispatch.

    This is the core deduplication contract. With no committed-state
    dependence in the predicate, "stale latest-commit replay" reduces to
    "unchanged INDEX → unchanged signature → no dispatch".
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()

    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["codex"]["reason"] == "dry_run"

    second = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert second["results"]["codex"]["reason"] == "unchanged"


# ──────────────────────────────────────────────────────────────────────────
# T-2-dispatch-state-idempotence
# ──────────────────────────────────────────────────────────────────────────


def test_dispatch_state_idempotent_writes_on_unchanged_signature(tmp_path: Path) -> None:
    """T-2-dispatch-state-idempotence: repeated invocation with unchanged INDEX
    keeps the dispatch-state signature stable.

    Note: the file is rewritten every fire (with a fresh ``updated_at``
    timestamp) — but the signature value never changes when the INDEX is
    unchanged. Idempotence here = signature stability, not bytewise file
    stability.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    state_path = state_dir / "dispatch-state.json"
    initial_state = json.loads(state_path.read_text(encoding="utf-8"))
    initial_sig = initial_state["recipients"]["codex"]["signature"]

    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    final_state = json.loads(state_path.read_text(encoding="utf-8"))
    final_sig = final_state["recipients"]["codex"]["signature"]
    assert final_sig == initial_sig
    assert final_state["recipients"]["codex"]["last_result"] == "unchanged"


# ──────────────────────────────────────────────────────────────────────────
# T-2-dispatch-on-changed-signature
# ──────────────────────────────────────────────────────────────────────────


def test_dispatch_fires_on_signature_change(tmp_path: Path) -> None:
    """T-2-dispatch-on-changed-signature: changing the INDEX top status from
    NEW to GO must change the actionable signature for both recipients
    (Codex stops being actionable; Prime starts) and re-fire dispatch.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    # First fire: codex actionable, prime not.
    assert first["results"]["codex"]["reason"] == "dry_run"
    assert first["results"]["prime"]["reason"] in {"no_pending", "no_pending_after_filter"}

    # Promote NEW → GO (top of stack).
    _write_index(root, _index_with_one_go(root))
    second = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    # Second fire: prime actionable (GO), codex not.
    assert second["results"]["prime"]["reason"] == "dry_run"
    assert second["results"]["codex"]["reason"] in {"no_pending", "no_pending_after_filter"}


# ──────────────────────────────────────────────────────────────────────────
# T-2-loop-prevention
# ──────────────────────────────────────────────────────────────────────────


def test_manual_disable_env_var_no_ops(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """T-2-loop-prevention (revised post -008 F2): GTKB_NO_CROSS_HARNESS_TRIGGER=1
    short-circuits the trigger as an OPERATOR opt-out.

    Per Codex F2 on -008: this env var is NOT propagated to dispatched-harness
    env. Setting it on the child would suppress reciprocal dispatch (e.g.,
    Codex's GO write would not wake Prime). The actual loop prevention is
    signature-state deduplication; this env var is for manual debugging /
    emergency-stop only.

    The reciprocal-dispatch fix is exercised by
    ``test_dispatched_child_env_does_not_inherit_disable_var`` and
    ``test_reciprocal_dispatch_new_to_go_round_trip`` below.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    monkeypatch.setenv("GTKB_NO_CROSS_HARNESS_TRIGGER", "1")
    trigger = _load_trigger()
    summary = trigger.run_trigger(
        project_root=root, state_dir=state_dir, dry_run=True
    )
    assert summary == {"skipped": True, "reason": "loop_prevention_env_var"}
    # And no dispatch-state file was written.
    assert not (state_dir / "dispatch-state.json").exists()


# ──────────────────────────────────────────────────────────────────────────
# T-2-fire-and-forget
# ──────────────────────────────────────────────────────────────────────────


def test_main_returns_zero_even_on_internal_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """T-2-fire-and-forget: ``main()`` always returns 0.

    Even if the underlying detection raises, the script must not propagate
    a non-zero exit code (hooks must not stall tool use). The error is logged
    to stderr / dispatch-failures.jsonl instead.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()

    def _boom(*_args, **_kwargs):
        raise RuntimeError("simulated detection failure")

    monkeypatch.setattr(trigger, "_compute_actionable", _boom)
    rc = trigger.main(
        [
            "--project-root",
            str(root),
            "--state-dir",
            str(state_dir),
            "--dry-run",
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert "cross-harness trigger error" in captured.err


# ──────────────────────────────────────────────────────────────────────────
# T-2-codex-hook-firing-regression — schema-level guard
# ──────────────────────────────────────────────────────────────────────────


def test_dispatch_state_schema_matches_smart_poller_signature_scheme(tmp_path: Path) -> None:
    """T-2-codex-hook-firing-regression (schema half).

    The signature scheme MUST stay byte-identical to the smart-poller's
    ``_pending_signature`` so Slice 4 can retire the smart-poller without a
    signature reset. This test pins the scheme by importing the canonical
    runner's helper and asserting equality on a fixed input.

    Per Codex F1 on -008: the smart-poller signs the SELECTED dispatch batch
    (post-cap, post-reverse-for-oldest-first), NOT the full filtered list.
    This test now reproduces that behavior exactly.

    The "Codex hooks fire on Windows" empirical regression is exercised at
    a different test layer (``DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08``
    and Slice 3 hook-registration tests). Slice 2 covers the schema half.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    summary = trigger.run_trigger(
        project_root=root, state_dir=state_dir, dry_run=True
    )

    from groundtruth_kb.bridge.detector import parse_index  # type: ignore
    from groundtruth_kb.bridge.notify import compute_actionable_pending  # type: ignore

    # Reproduce the smart-poller's signature scheme for the same INDEX state.
    parse_result = parse_index(
        (root / "bridge" / "INDEX.md").read_text(encoding="utf-8"),
        project_root=root,
    )
    _, codex_items = compute_actionable_pending(parse_result, project_root=root)
    selected = trigger._selected_oldest_first(codex_items, trigger.DEFAULT_MAX_ITEMS)
    expected_sig = trigger._signature(selected)

    actual_sig = summary["dispatch_state"]["recipients"]["codex"]["signature"]
    assert actual_sig == expected_sig


# ──────────────────────────────────────────────────────────────────────────
# T-2-selected-batch-signature-parity — per Codex F1 on -008
# ──────────────────────────────────────────────────────────────────────────


def _index_with_three_new(root: Path) -> str:
    """Build an INDEX with three NEW Codex-actionable entries.

    Used to exercise the selected-batch vs full-list signature distinction
    (only meaningful when the pending list exceeds ``DEFAULT_MAX_ITEMS=2``).
    """
    docs = ["alpha-thread", "beta-thread", "gamma-thread"]
    for doc in docs:
        _write_bridge_file(root, f"{doc}-001.md", "bridge_kind: implementation_proposal\n")
    body = ["# bridge index", ""]
    for doc in docs:
        body.append(f"Document: {doc}")
        body.append(f"NEW: bridge/{doc}-001.md")
        body.append("")
    return "\n".join(body) + "\n"


def test_signature_uses_selected_batch_not_full_list_with_max_items_2(
    tmp_path: Path,
) -> None:
    """Codex F1 on -008: under backlog pressure, the trigger must sign the
    selected dispatch batch — not the full filtered list — to match
    smart-poller behavior byte-for-byte and avoid redundant dispatches.

    Reproduces Codex's required regression: 3 pending entries, max_items=2.
    The trigger's stored signature must equal
    ``bridge_poller_runner._pending_signature(_selected_items_for_prompt(
    filtered, 2))`` and must NOT equal ``_pending_signature(filtered)``.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_three_new(root))

    trigger = _load_trigger()
    summary = trigger.run_trigger(
        project_root=root, state_dir=state_dir, max_items=2, dry_run=True
    )

    # Reproduce both candidate signature scopes from the canonical smart-poller helper.
    import importlib.util as _ilu

    runner_path = (
        Path(__file__).resolve().parents[2]
        / "groundtruth-kb"
        / "scripts"
        / "bridge_poller_runner.py"
    )
    spec = _ilu.spec_from_file_location("_runner_for_parity", runner_path)
    assert spec is not None and spec.loader is not None
    runner = _ilu.module_from_spec(spec)
    spec.loader.exec_module(runner)

    from groundtruth_kb.bridge.detector import parse_index  # type: ignore
    from groundtruth_kb.bridge.notify import compute_actionable_pending  # type: ignore

    parse_result = parse_index(
        (root / "bridge" / "INDEX.md").read_text(encoding="utf-8"),
        project_root=root,
    )
    _, codex_items = compute_actionable_pending(parse_result, project_root=root)
    assert len(codex_items) == 3, "fixture should have 3 Codex-actionable entries"

    selected = runner._selected_items_for_prompt(codex_items, 2)
    expected_selected_sig = runner._pending_signature(selected)
    expected_full_sig = runner._pending_signature(codex_items)
    assert expected_selected_sig != expected_full_sig, (
        "fixture must be sized so selected-batch and full-list signatures DIFFER"
    )

    actual_sig = summary["dispatch_state"]["recipients"]["codex"]["signature"]
    assert actual_sig == expected_selected_sig, (
        "trigger must sign the selected dispatch batch (post-cap, post-reverse), "
        "not the full filtered list"
    )
    assert actual_sig != expected_full_sig

    # And the dispatch-state should record selected_count=2 alongside pending_count=3.
    rec = summary["dispatch_state"]["recipients"]["codex"]
    assert rec["pending_count"] == 3
    assert rec["selected_count"] == 2
    assert rec["signature_scope"] == "selected_dispatch_batch"


def test_default_max_items_matches_smart_poller_default_cap(tmp_path: Path) -> None:
    """Codex F1 on -008: default cap must match smart-poller's default of 2.

    Bumping the cap is scope creep — requires a separate proposal.
    """
    trigger = _load_trigger()
    assert trigger.DEFAULT_MAX_ITEMS == 2


# ──────────────────────────────────────────────────────────────────────────
# T-2-reciprocal-dispatch — per Codex F2 on -008
# ──────────────────────────────────────────────────────────────────────────


def test_dispatched_child_env_does_not_inherit_disable_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex F2 on -008: the trigger MUST NOT propagate
    GTKB_NO_CROSS_HARNESS_TRIGGER to the dispatched-harness child env.

    Setting it on the child would suppress the legitimate reciprocal
    dispatch (Codex's GO write would not wake Prime). Loop prevention lives
    in the signature-state file, not the env var.

    We patch ``subprocess.Popen`` to capture the env that would be passed
    and assert the disable var is absent — even when the parent process has
    it set (the parent's setting must not leak into the child).
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()

    # Parent has the env var set (e.g., a debug-stopped operator session) —
    # the dispatch path must STILL refuse to propagate it to the child.
    # But the parent's run_trigger short-circuits when the env var is set
    # in its own environment, so we simulate the dispatch path differently:
    # call _spawn_harness directly with monkeypatched Popen.
    captured_envs: list[dict] = []

    class _FakeProcess:
        pid = 12345

    import subprocess as _subprocess

    def _fake_popen(*_args, **kwargs):
        captured_envs.append(kwargs.get("env", {}))
        return _FakeProcess()

    monkeypatch.setattr(_subprocess, "Popen", _fake_popen)
    monkeypatch.setenv("GTKB_NO_CROSS_HARNESS_TRIGGER", "1")

    # Build a single-item synthetic actionable to exercise _spawn_harness
    # without going through run_trigger (which would short-circuit).
    from types import SimpleNamespace

    fake_item = SimpleNamespace(
        document_name="reciprocal-test",
        top_status="NEW",
        top_file="bridge/reciprocal-test-001.md",
        index_line_number=1,
        dispatchable=True,
        classification="dispatchable",
    )

    meta = trigger._spawn_harness(
        recipient="codex",
        items=[fake_item],
        project_root=root,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
    )
    assert meta["launched"] is True
    assert len(captured_envs) == 1
    child_env = captured_envs[0]
    # Parent's setting MUST NOT leak.
    assert "GTKB_NO_CROSS_HARNESS_TRIGGER" not in child_env, (
        "GTKB_NO_CROSS_HARNESS_TRIGGER must not be propagated to child harness env"
    )
    # GTKB_PROJECT_ROOT IS propagated (legitimate).
    assert child_env.get("GTKB_PROJECT_ROOT") == str(root)


def test_reciprocal_dispatch_new_to_go_round_trip(tmp_path: Path) -> None:
    """Codex F2 on -008: simulate Claude-writes-NEW → Codex-writes-GO and
    prove the reciprocal trigger fires Prime dispatch on the second changed
    signature, while a redundant fire on unchanged signature does NOT
    relaunch.

    Sequence:
      1. INDEX has one NEW (Codex-actionable). Trigger fires → Codex dispatched.
      2. Same INDEX state, trigger fires again. Codex signature unchanged → no dispatch.
         (This is the "dispatched harness's tool-use" loop-prevention path.)
      3. INDEX is updated to add GO on top (Prime-actionable; Codex no longer top).
         Trigger fires → Prime dispatched. Codex's signature is now empty/stable.

    This is the round-trip the proposal at -003 §241 requires.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()

    # Step 1: NEW present → Codex dispatched.
    s1 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert s1["results"]["codex"]["reason"] == "dry_run"
    assert s1["results"]["prime"]["reason"] in {"no_pending", "no_pending_after_filter"}
    codex_sig_after_step1 = s1["dispatch_state"]["recipients"]["codex"]["signature"]

    # Step 2: same INDEX → no relaunch (signature dedup is the loop prevention).
    s2 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert s2["results"]["codex"]["reason"] == "unchanged"

    # Step 3: simulate Codex writing GO. INDEX top is now GO (Prime-actionable).
    _write_index(root, _index_with_one_go(root))
    s3 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    # Reciprocal dispatch: Prime is now actionable; trigger fires.
    assert s3["results"]["prime"]["reason"] == "dry_run", (
        "After Codex writes GO, Prime's signature must change and fire dispatch"
    )
    # Codex's actionable list is now empty (top is GO, not NEW/REVISED).
    assert s3["results"]["codex"]["reason"] in {"no_pending", "no_pending_after_filter"}

    # And Codex's recorded signature has changed (was NEW-actionable; now empty).
    codex_sig_after_step3 = s3["dispatch_state"]["recipients"]["codex"]["signature"]
    assert codex_sig_after_step3 != codex_sig_after_step1
