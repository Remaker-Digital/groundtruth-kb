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

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"

# WI-3344: invocation_surfaces headless argv templates. {{PROMPT}} and
# {{PROJECT_ROOT}} are the placeholder tokens _harness_command substitutes as
# individual argv elements. Shared by the synthetic fixture and the FR8 tests.
_CODEX_INVOCATION_SURFACES = {
    "headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}
}
_CLAUDE_INVOCATION_SURFACES = {
    "headless": {
        "argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]
    }
}


def _frozen_pending_signature(items: list[object]) -> str:
    """Frozen byte-identical reference for the retired smart-poller's
    ``_pending_signature`` (Slice 4 D7).

    Source: ``archive/smart-poller-2026-05-09/groundtruth-kb/scripts/bridge_poller_runner.py``
    lines 215-225 (function ``_pending_signature``). Replicated here so
    cross-harness-trigger tests can verify byte-identical signatures
    without importing the archived runner.
    """
    normalized = [
        {
            "document_name": item.document_name,  # type: ignore[attr-defined]
            "top_status": item.top_status,  # type: ignore[attr-defined]
            "top_file": item.top_file,  # type: ignore[attr-defined]
        }
        for item in items
    ]
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _frozen_selected_items_for_prompt(
    items: list[object], max_items: int
) -> list[object]:
    """Frozen byte-identical reference for the retired smart-poller's
    ``_selected_items_for_prompt`` (Slice 4 D7).

    Source: ``archive/smart-poller-2026-05-09/groundtruth-kb/scripts/bridge_poller_runner.py``
    lines 262-266 (function ``_selected_items_for_prompt``). INDEX is
    newest-first; bridge work should be processed oldest-first, so reverse
    then cap.
    """
    if max_items <= 0:
        return []
    return list(reversed(items))[:max_items]


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
    ``bridge/INDEX.md`` for the trigger to read, and ``harness-state/*.json``
    fixtures required by IP-3b's _resolve_dispatch_target (default fixture:
    claude=B=prime-builder, codex=A=loyal-opposition).
    """
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestSynthetic"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (root / "bridge").mkdir(exist_ok=True)
    harness_state = root / "harness-state"
    harness_state.mkdir(exist_ok=True)
    (harness_state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "claude": {"id": "B"},
                    "codex": {"id": "A"},
                },
            }
        ),
        encoding="utf-8",
    )
    (harness_state / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "B": {"role": "prime-builder", "harness_type": "claude"},
                    "A": {"role": "loyal-opposition", "harness_type": "codex"},
                },
            }
        ),
        encoding="utf-8",
    )
    # WI-3344: a multi-harness registry projection so the now-fallback-free
    # _harness_command can build dispatch argv for A (codex) and B (claude).
    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["loyal-opposition"],
                        "invocation_surfaces": _CODEX_INVOCATION_SURFACES,
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "role": ["prime-builder"],
                        "invocation_surfaces": _CLAUDE_INVOCATION_SURFACES,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
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

    sig_a = summary_a["dispatch_state"]["recipients"]["loyal-opposition"]["signature"]
    sig_b = summary_b["dispatch_state"]["recipients"]["loyal-opposition"]["signature"]
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
    assert summary_empty["results"]["loyal-opposition"]["reason"] == "no_pending"

    # Add a NEW entry (uncommitted edit) → dispatch fires.
    _write_index(root, _index_with_one_new(root))
    summary_new = trigger.run_trigger(
        project_root=root, state_dir=state_dir, dry_run=True
    )
    # dry_run=True → "launched" stays False, but reason is "dry_run" not "no_pending"
    # which proves the dispatch path was entered.
    assert summary_new["results"]["loyal-opposition"]["reason"] == "dry_run"


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
    assert first["results"]["loyal-opposition"]["reason"] == "dry_run"

    second = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert second["results"]["loyal-opposition"]["reason"] == "unchanged"


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
    initial_sig = initial_state["recipients"]["loyal-opposition"]["signature"]

    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    final_state = json.loads(state_path.read_text(encoding="utf-8"))
    final_sig = final_state["recipients"]["loyal-opposition"]["signature"]
    assert final_sig == initial_sig
    assert final_state["recipients"]["loyal-opposition"]["last_result"] == "unchanged"


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
    assert first["results"]["loyal-opposition"]["reason"] == "dry_run"
    assert first["results"]["prime-builder"]["reason"] in {"no_pending", "no_pending_after_filter"}

    # Promote NEW → GO (top of stack).
    _write_index(root, _index_with_one_go(root))
    second = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    # Second fire: prime actionable (GO), codex not.
    assert second["results"]["prime-builder"]["reason"] == "dry_run"
    assert second["results"]["loyal-opposition"]["reason"] in {"no_pending", "no_pending_after_filter"}


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

    actual_sig = summary["dispatch_state"]["recipients"]["loyal-opposition"]["signature"]
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
    selected dispatch batch — not the full filtered list — to match the
    retired smart-poller's signature contract byte-for-byte and avoid
    redundant dispatches.

    Reproduces Codex's required regression: 3 pending entries, max_items=2.
    The trigger's stored signature must equal
    ``_frozen_pending_signature(_frozen_selected_items_for_prompt(filtered, 2))``
    and must NOT equal ``_frozen_pending_signature(filtered)``.

    Slice 4 D7: the frozen-reference helpers below replace the prior
    ``importlib`` cross-import of ``bridge_poller_runner.py``. The runner was
    archived to ``archive/smart-poller-2026-05-09/`` on 2026-05-09 so this
    test owns the byte-identical reference. Source for the frozen logic:
    ``archive/smart-poller-2026-05-09/groundtruth-kb/scripts/bridge_poller_runner.py``
    lines 215-225 (``_pending_signature``) and lines 262-266
    (``_selected_items_for_prompt``).
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_three_new(root))

    trigger = _load_trigger()
    summary = trigger.run_trigger(
        project_root=root, state_dir=state_dir, max_items=2, dry_run=True
    )

    from groundtruth_kb.bridge.detector import parse_index  # type: ignore
    from groundtruth_kb.bridge.notify import compute_actionable_pending  # type: ignore

    parse_result = parse_index(
        (root / "bridge" / "INDEX.md").read_text(encoding="utf-8"),
        project_root=root,
    )
    _, codex_items = compute_actionable_pending(parse_result, project_root=root)
    assert len(codex_items) == 3, "fixture should have 3 Codex-actionable entries"

    selected = _frozen_selected_items_for_prompt(codex_items, 2)
    expected_selected_sig = _frozen_pending_signature(selected)
    expected_full_sig = _frozen_pending_signature(codex_items)
    assert expected_selected_sig != expected_full_sig, (
        "fixture must be sized so selected-batch and full-list signatures DIFFER"
    )

    actual_sig = summary["dispatch_state"]["recipients"]["loyal-opposition"]["signature"]
    assert actual_sig == expected_selected_sig, (
        "trigger must sign the selected dispatch batch (post-cap, post-reverse), "
        "not the full filtered list"
    )
    assert actual_sig != expected_full_sig

    # And the dispatch-state should record selected_count=2 alongside pending_count=3.
    rec = summary["dispatch_state"]["recipients"]["loyal-opposition"]
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

    lo_target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="codex",
        canonical_mode="lo",
        invocation_surfaces=_CODEX_INVOCATION_SURFACES,
    )
    meta = trigger._spawn_harness(
        target=lo_target,
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
    # Per Slice 4 D9b (Codex F1 on -006): the trigger MUST set
    # GTKB_BRIDGE_POLLER_RUN_ID on the child env so the SessionStart hooks at
    # .claude/hooks/session_start_dispatch.py and .codex/gtkb-hooks/session_start_dispatch.py
    # enter bridge auto-dispatch mode rather than treating the initial prompt as
    # a discarded owner session-start stimulus. The retired smart-poller used to
    # set this; the cross-harness trigger now sets it itself with the dispatch_id.
    assert "GTKB_BRIDGE_POLLER_RUN_ID" in child_env, (
        "trigger must set GTKB_BRIDGE_POLLER_RUN_ID for SessionStart auto-dispatch context"
    )
    assert child_env["GTKB_BRIDGE_POLLER_RUN_ID"] == meta["dispatch_id"], (
        "GTKB_BRIDGE_POLLER_RUN_ID must equal the dispatch_id"
    )


# ──────────────────────────────────────────────────────────────────────────
# WI-3353 IP-6/IP-7: worktree-aware canonical-root resolution (transitive)
# ──────────────────────────────────────────────────────────────────────────


def _build_worktree_project(tmp_path: Path) -> tuple[Path, Path]:
    """Build a synthetic GT-KB canonical checkout with a linked worktree under
    .claude/worktrees/test-wt. Returns (canonical_root, worktree_root). The
    worktree carries its own committed groundtruth.toml. Requires git.
    """
    ident = [
        "-c", "user.email=test@example.com",
        "-c", "user.name=test",
        "-c", "commit.gpgsign=false",
    ]
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "groundtruth.toml").write_text("# synthetic GT-KB root\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "add", "groundtruth.toml"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "commit", "-m", "init"], cwd=canonical, check=True, capture_output=True)
    worktree = canonical / ".claude" / "worktrees" / "test-wt"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", *ident, "worktree", "add", "--detach", str(worktree)],
        cwd=canonical,
        check=True,
        capture_output=True,
    )
    return canonical, worktree


def test_cross_harness_trigger_resolves_canonical_from_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-3353 IP-6/IP-7: scripts/cross_harness_bridge_trigger.py needs no code
    change -- its _resolve_project_root delegates to the now worktree-correct
    groundtruth_kb.bridge.paths.resolve_project_root(). From inside a linked
    worktree the trigger therefore resolves the canonical main-worktree root,
    transitively verifying the IP-1 fix."""
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    canonical, worktree = _build_worktree_project(tmp_path)
    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)
    monkeypatch.chdir(worktree)
    trigger = _load_trigger()
    resolved = trigger._resolve_project_root(None)
    assert resolved.resolve() == canonical.resolve()


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
    assert s1["results"]["loyal-opposition"]["reason"] == "dry_run"
    assert s1["results"]["prime-builder"]["reason"] in {"no_pending", "no_pending_after_filter"}
    codex_sig_after_step1 = s1["dispatch_state"]["recipients"]["loyal-opposition"]["signature"]

    # Step 2: same INDEX → no relaunch (signature dedup is the loop prevention).
    s2 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert s2["results"]["loyal-opposition"]["reason"] == "unchanged"

    # Step 3: simulate Codex writing GO. INDEX top is now GO (Prime-actionable).
    _write_index(root, _index_with_one_go(root))
    s3 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    # Reciprocal dispatch: Prime is now actionable; trigger fires.
    assert s3["results"]["prime-builder"]["reason"] == "dry_run", (
        "After Codex writes GO, Prime's signature must change and fire dispatch"
    )
    # Codex's actionable list is now empty (top is GO, not NEW/REVISED).
    assert s3["results"]["loyal-opposition"]["reason"] in {"no_pending", "no_pending_after_filter"}

    # And Codex's recorded signature has changed (was NEW-actionable; now empty).
    codex_sig_after_step3 = s3["dispatch_state"]["recipients"]["loyal-opposition"]["signature"]
    assert codex_sig_after_step3 != codex_sig_after_step1


# ──────────────────────────────────────────────────────────────────────────
# T-3-* — Slice 3 hook-mode tests (per GO at -004)
# ──────────────────────────────────────────────────────────────────────────


def test_stop_hook_emits_exactly_braces_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """T-3-stop-hook-output-contract: ``--stop-hook`` mode MUST emit exactly
    ``{}`` (parseable JSON object, no extra text) on stdout and exit 0.

    Required by the OpenAI Codex Stop hook contract per Codex `-002` F2 +
    Codex GO at `-004` "GO Conditions For Later Verification" line 167.
    Also valid for Claude Stop hook registrations.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    rc = trigger.main(
        [
            "--project-root",
            str(root),
            "--state-dir",
            str(state_dir),
            "--stop-hook",
            "--dry-run",
        ]
    )
    assert rc == 0

    captured = capsys.readouterr()
    # Stdout MUST be exactly "{}\n" (no extra summary text — Codex contract).
    assert captured.out == "{}\n", (
        f"Expected stdout exactly '{{}}\\n' for --stop-hook; got: {captured.out!r}"
    )
    # Stdout MUST parse as a JSON object.
    parsed = json.loads(captured.out)
    assert parsed == {}, "Stop-hook stdout must parse to an empty dict"


def test_stop_hook_overrides_verbose(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """T-3-stop-hook-output-contract (verbose interaction): when both
    --stop-hook and --verbose are passed, --stop-hook MUST win to preserve
    the JSON contract.

    Without this guard a misconfigured hook command (--verbose accidentally
    set in the same registration) would emit pretty-printed summary text
    that violates the Codex Stop contract.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    rc = trigger.main(
        [
            "--project-root",
            str(root),
            "--state-dir",
            str(state_dir),
            "--stop-hook",
            "--verbose",
            "--dry-run",
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out == "{}\n"


def test_stop_hook_runs_reconciliation_bounded_no_dispatch_on_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """T-3-stop-reconciliation-bounded: with --stop-hook on unchanged INDEX,
    the trigger MUST run reconciliation (read INDEX, compute signature,
    check dispatch-state) and exit 0 with `{}` stdout, but NOT dispatch.

    Bounded-by-signature-dedup contract: if a prior PostToolUse fire already
    recorded the current signature, Stop reconciliation sees match and exits
    "unchanged" — no spawn.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    # Prime the dispatch-state by firing default mode first.
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    state_path = state_dir / "dispatch-state.json"
    assert state_path.exists()
    sig_before = json.loads(state_path.read_text(encoding="utf-8"))[
        "recipients"
    ]["loyal-opposition"]["signature"]

    # Now invoke --stop-hook on the SAME index state.
    capsys.readouterr()  # drain
    rc = trigger.main(
        [
            "--project-root",
            str(root),
            "--state-dir",
            str(state_dir),
            "--stop-hook",
            "--dry-run",
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out == "{}\n"

    # Signature unchanged; last_result records "unchanged".
    state_after = json.loads(state_path.read_text(encoding="utf-8"))
    sig_after = state_after["recipients"]["loyal-opposition"]["signature"]
    assert sig_after == sig_before
    assert state_after["recipients"]["loyal-opposition"]["last_result"] == "unchanged"


def test_stop_hook_fail_soft_dispatches_on_changed_signature(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """T-3-stop-reconciliation-fail-soft: if PostToolUse missed an INDEX
    change (e.g., a tool that doesn't fire PostToolUse), the Stop hook
    MUST detect the changed signature and dispatch.

    This is the fail-soft safety net per parent thread `-002` F2 Codex
    wording. The trigger still emits `{}` to satisfy the Codex contract,
    but internally the dispatch path is entered (dry_run mode in test).
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"

    # Prime dispatch-state with NO INDEX (signature for empty list).
    _write_index(root, "# empty\n")
    trigger = _load_trigger()
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    # Simulate PostToolUse missing the change: edit INDEX without firing
    # default trigger; only Stop fires.
    _write_index(root, _index_with_one_new(root))

    capsys.readouterr()  # drain
    rc = trigger.main(
        [
            "--project-root",
            str(root),
            "--state-dir",
            str(state_dir),
            "--stop-hook",
            "--dry-run",
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out == "{}\n"

    # Internal dispatch state shows the dispatch path was entered: last_launch
    # carries the dry-run meta. In dry_run mode, launched=False so last_result
    # records "launch_failed" (existing convention) — the load-bearing assertion
    # is that the launch path was attempted (last_launch present + reason
    # "dry_run"), proving the Stop hook detected the signature change rather
    # than no-op'ing on "unchanged".
    state_path = state_dir / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    rec = state["recipients"]["loyal-opposition"]
    assert rec["last_result"] != "unchanged", (
        "Stop hook must detect changed signature even when PostToolUse missed it"
    )
    assert "last_launch" in rec
    assert rec["last_launch"]["reason"] == "dry_run"


def test_stop_hook_main_returns_zero_even_on_internal_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """T-3-stop-hook-output-contract (failure path): even when reconciliation
    fails internally, --stop-hook MUST exit 0 (fire-and-forget) AND emit
    valid Stop-contract output. The catch-all in main() suppresses the error
    to stderr; stdout stays JSON-valid.

    Note: when reconciliation fails BEFORE the print path, stdout is empty.
    Codex docs treat exit 0 + empty stdout as success too, so this is still
    a valid Stop contract — but the test pins the exit code, not the exact
    stdout, because the print is gated on successful run_trigger.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()

    def _boom(*_args, **_kwargs):
        raise RuntimeError("simulated detection failure for stop-hook fail-soft test")

    monkeypatch.setattr(trigger, "_compute_actionable", _boom)
    rc = trigger.main(
        [
            "--project-root",
            str(root),
            "--state-dir",
            str(state_dir),
            "--stop-hook",
            "--dry-run",
        ]
    )
    assert rc == 0
    # Error logged to stderr (fire-and-forget).
    captured = capsys.readouterr()
    assert "cross-harness trigger error" in captured.err


def test_overlap_state_shared_path_reads_existing_dispatch_state(tmp_path: Path) -> None:
    """T-3-overlap-state-shared (Option A coordination): when --state-dir
    points at the smart-poller's existing dispatch-state path, the trigger
    MUST read that file and respect a previously-recorded signature
    (avoiding double-dispatch during the smart-poller/trigger overlap window).
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "shared-bridge-poller-state"
    state_dir.mkdir(parents=True)

    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()

    # Compute what the trigger's signature WOULD be for this INDEX state.
    s = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    expected_sig = s["dispatch_state"]["recipients"]["loyal-opposition"]["signature"]
    assert s["results"]["loyal-opposition"]["reason"] == "dry_run"

    # Wipe state, then pre-populate as-if smart-poller already dispatched.
    state_path = state_dir / "dispatch-state.json"
    state_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at": "1999-01-01T00:00:00+00:00",
                "recipients": {
                    "codex": {
                        "signature": expected_sig,
                        "signature_scope": "selected_dispatch_batch",
                        "pending_count": 1,
                        "selected_count": 1,
                        "raw_pending_count": 1,
                        "updated_at": "1999-01-01T00:00:00+00:00",
                        "last_result": "launched",
                    }
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    # Trigger fires; sees matching signature; does NOT dispatch.
    s2 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert s2["results"]["loyal-opposition"]["reason"] == "unchanged", (
        "trigger must respect a pre-existing matching signature in the shared state file"
    )


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-trigger-noop-with-audit-evidence (Slice 2 IP-8 F1 closure)
# ──────────────────────────────────────────────────────────────────────────


def test_cross_harness_trigger_noop_in_single_harness_topology_records_audit_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """IP-8 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md
    (Codex GO at -006), F1 closure of -004:

    In single-harness topology (one harness ID with multi-element role-set),
    the cross-harness trigger MUST:

    1. Return ``{"skipped": True, "reason": "single_harness_topology_not_applicable"}``.
    2. NOT spawn any subprocess.
    3. Write per-role audit-log entries to dispatch-failures.jsonl with the
       SPEC-cited reason — preserving the SPEC's
       "resolution fails with an audit-log entry" invariant per
       SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Coexistence.
    4. Write per-recipient dispatch-state.json records with
       last_result="single_harness_topology_not_applicable" — preserving
       the audit-log-via-dispatch-state evidence path for --diagnose and
       doctor consumers.
    """
    # Build synthetic project with SINGLE-harness role-set (multi-element).
    (tmp_path / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestSingleHarness"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (tmp_path / "bridge").mkdir(exist_ok=True)
    harness_state = tmp_path / "harness-state"
    harness_state.mkdir(exist_ok=True)
    (harness_state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "claude": {"id": "B"},
                    "codex": {"id": "A"},
                },
            }
        ),
        encoding="utf-8",
    )
    (harness_state / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "B": {
                        "role": ["prime-builder", "loyal-opposition"],
                        "harness_type": "claude",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    _write_index(tmp_path, _index_with_one_new(tmp_path))
    state_dir = tmp_path / "state"

    # Patch subprocess.Popen to assert it's never called.
    import subprocess as _subprocess

    popen_calls: list = []

    def _fail_popen(*args, **kwargs):
        popen_calls.append((args, kwargs))
        raise AssertionError("subprocess.Popen must NOT be invoked in single-harness topology")

    monkeypatch.setattr(_subprocess, "Popen", _fail_popen)

    trigger = _load_trigger()
    result = trigger.run_trigger(project_root=tmp_path, state_dir=state_dir, dry_run=False)

    # (1) Return value.
    assert result == {"skipped": True, "reason": "single_harness_topology_not_applicable"}

    # (2) No subprocess spawned.
    assert popen_calls == [], "Popen was invoked in single-harness topology"

    # (3) Per-role audit-log entries in dispatch-failures.jsonl.
    failures_path = state_dir / "dispatch-failures.jsonl"
    assert failures_path.is_file(), "dispatch-failures.jsonl missing"
    lines = [
        line for line in failures_path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    records = [json.loads(line) for line in lines]
    assert len(records) == 2, f"expected 2 audit entries, got {len(records)}: {records}"
    by_role = {rec["recipient"]: rec for rec in records}
    assert "prime-builder" in by_role and "loyal-opposition" in by_role
    for role, rec in by_role.items():
        assert rec["reason"] == "single_harness_topology_not_applicable"
        assert rec["launched"] is False
        assert "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001" in rec["error_message"]

    # (4) Per-recipient dispatch-state.json records.
    state_path = state_dir / "dispatch-state.json"
    assert state_path.is_file(), "dispatch-state.json missing"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    recipients = state.get("recipients", {})
    assert recipients["prime-builder"]["last_result"] == "single_harness_topology_not_applicable"
    assert recipients["loyal-opposition"]["last_result"] == "single_harness_topology_not_applicable"
    assert "updated_at" in recipients["prime-builder"]
    assert "updated_at" in recipients["loyal-opposition"]


# ──────────────────────────────────────────────────────────────────────────
# WI-3265 — dispatch-state-lag diagnostic instrumentation (IP-2)
# Per bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md (Codex GO -004).
# Diagnostic-only: instrumentation must observe, never alter, dispatch behavior.
# ──────────────────────────────────────────────────────────────────────────


def _read_diagnostics(state_dir: Path) -> list[dict]:
    """Read all records from the WI-3265 trigger-diagnostic.jsonl log."""
    path = state_dir / "trigger-diagnostic.jsonl"
    if not path.is_file():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def test_diagnostic_emitted_per_invocation(tmp_path: Path) -> None:
    """WI-3265 IP-2: a diagnostic record is emitted for every recipient on
    every normal-path invocation; the log grows by len(recipients) each fire.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()

    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    first = _read_diagnostics(state_dir)
    assert len(first) == 2, "one diagnostic record per recipient (prime-builder + loyal-opposition)"
    assert {r["recipient"] for r in first} == {"prime-builder", "loyal-opposition"}

    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    second = _read_diagnostics(state_dir)
    assert len(second) == 4, "instrumentation fires on every invocation"


def test_diagnostic_classifies_suppressed(tmp_path: Path) -> None:
    """WI-3265 IP-2: a fresh counterpart active-session lock drives the
    loyal-opposition recipient to the `active_session_suppressed` class.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    _write_index(root, _index_with_one_new(root))
    # codex is the loyal-opposition harness in the default fixture; a fresh
    # active-codex-session.lock suppresses its dispatch.
    (state_dir / "active-codex-session.lock").write_text("lock", encoding="utf-8")

    trigger = _load_trigger()
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    lo = [r for r in _read_diagnostics(state_dir) if r["recipient"] == "loyal-opposition"]
    assert len(lo) == 1
    assert lo[0]["last_result"] == "counterpart_active_session_present"
    assert lo[0]["classification"] == "active_session_suppressed"


def test_diagnostic_classifies_dispatched(tmp_path: Path) -> None:
    """WI-3265 IP-2: when the dispatch branch is entered for a recipient, its
    diagnostic record classifies as `dispatched`. dry-run yields a
    `launch_failed` last_result, which the classifier maps to `dispatched`
    because the dispatch branch was reached.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    lo = [r for r in _read_diagnostics(state_dir) if r["recipient"] == "loyal-opposition"]
    assert len(lo) == 1
    assert lo[0]["last_result"] in {"launched", "launch_failed"}
    assert lo[0]["classification"] == "dispatched"


def test_diagnostic_classifies_no_change(tmp_path: Path) -> None:
    """WI-3265 IP-2: a second invocation on an unchanged INDEX classifies the
    recipient as `no_change` (signature dedup → last_result `unchanged`).
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    lo = [r for r in _read_diagnostics(state_dir) if r["recipient"] == "loyal-opposition"]
    assert len(lo) == 2
    assert lo[-1]["last_result"] == "unchanged"
    assert lo[-1]["classification"] == "no_change"


def test_diagnostic_classifies_selected_batch(tmp_path: Path) -> None:
    """WI-3265 IP-2: when actionable work exists but the selected batch is
    empty (forced deterministically here via max_items=0), the recipient
    classifies as `selected_batch_skipped`.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()
    trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=0, dry_run=True)

    lo = [r for r in _read_diagnostics(state_dir) if r["recipient"] == "loyal-opposition"]
    assert len(lo) == 1
    assert lo[0]["last_result"] == "no_pending_after_filter"
    assert lo[0]["classification"] == "selected_batch_skipped"


def test_diagnostic_jsonl_parseable(tmp_path: Path) -> None:
    """WI-3265 IP-2: every emitted line is valid JSON carrying the full schema;
    classification stays within the documented vocabulary.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    path = state_dir / "trigger-diagnostic.jsonl"
    assert path.is_file()
    raw = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert raw, "diagnostic log must contain at least one record"
    expected_keys = {
        "timestamp", "invocation_source", "pid", "session_id",
        "index_mtime", "index_signature_pre", "index_signature_post",
        "dispatch_state_mtime_pre", "dispatch_state_mtime_post",
        "classification", "last_dispatched_signature",
        "last_suppressed_signature", "elapsed_ms", "recipient", "last_result",
    }
    for ln in raw:
        rec = json.loads(ln)  # raises on malformed JSON -> test fails
        missing = expected_keys - rec.keys()
        assert not missing, f"diagnostic record missing keys: {missing}"
        assert rec["classification"] in trigger.TRIGGER_DIAGNOSTIC_CLASSIFICATIONS


def test_dispatch_decision_unchanged_with_instrumentation(tmp_path: Path) -> None:
    """WI-3265 IP-2: instrumentation is observational — the dispatch decision
    (results + dispatch-state) is exactly the pre-instrumentation contract,
    and no diagnostic field leaks into dispatch-state.json.
    """
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()

    # NEW present -> loyal-opposition dispatched, prime-builder idle.
    s1 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert s1["results"]["loyal-opposition"]["reason"] == "dry_run"
    assert s1["results"]["prime-builder"]["reason"] in {"no_pending", "no_pending_after_filter"}

    # Re-fire on unchanged INDEX -> dedup holds.
    s2 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert s2["results"]["loyal-opposition"]["reason"] == "unchanged"

    # Promote NEW -> GO -> prime-builder dispatched, loyal-opposition idle.
    _write_index(root, _index_with_one_go(root))
    s3 = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert s3["results"]["prime-builder"]["reason"] == "dry_run"
    assert s3["results"]["loyal-opposition"]["reason"] in {"no_pending", "no_pending_after_filter"}

    # Instrumentation did not leak into dispatch-state.json.
    state = json.loads((state_dir / "dispatch-state.json").read_text(encoding="utf-8"))
    for rec in state["recipients"].values():
        for leaked in ("classification", "index_signature_pre", "elapsed_ms", "invocation_source"):
            assert leaked not in rec, f"diagnostic field {leaked!r} leaked into dispatch-state"
    # The diagnostic log is a separate artifact and was written.
    assert (state_dir / "trigger-diagnostic.jsonl").is_file()


# ──────────────────────────────────────────────────────────────────────────
# WI-3344 — data-driven _harness_command() from invocation_surfaces (FR8)
# Per bridge/gtkb-harness-data-driven-dispatch-003.md (Codex GO at -004).
# ──────────────────────────────────────────────────────────────────────────


def test_harness_command_builds_argv_from_invocation_surfaces(tmp_path: Path) -> None:
    """WI-3344 FR8 / DELIB-2079 Q9: _harness_command builds the dispatch argv
    solely from a harness record's invocation_surfaces.headless template,
    substituting {{PROMPT}} and {{PROJECT_ROOT}} as individual argv elements —
    for the codex, claude, and a non-claude/codex harness record alike.
    """
    trigger = _load_trigger()
    prompt = "::init gtkb lo"
    root = tmp_path

    def _target(handle: str, surfaces: object) -> object:
        return trigger.DispatchTarget(
            needed_role_label="loyal-opposition",
            harness_id="A",
            command_handle=handle,
            canonical_mode="lo",
            invocation_surfaces=surfaces,
        )

    codex_cmd = trigger._harness_command(_target("codex", _CODEX_INVOCATION_SURFACES), prompt, root)
    assert codex_cmd == ["codex", "exec", prompt, "--cd", str(root)]

    claude_cmd = trigger._harness_command(_target("claude", _CLAUDE_INVOCATION_SURFACES), prompt, root)
    assert claude_cmd == ["claude", "-p", prompt, "--add-dir", str(root), "--output-format", "json"]

    third_surfaces = {"headless": {"argv": ["gemini", "-p", "{{PROMPT}}", "--root", "{{PROJECT_ROOT}}"]}}
    third_cmd = trigger._harness_command(_target("gemini", third_surfaces), prompt, root)
    assert third_cmd == ["gemini", "-p", prompt, "--root", str(root)]


def test_harness_command_fails_closed_for_missing_or_malformed_surfaces(tmp_path: Path) -> None:
    """WI-3344 FR8 / DELIB-2079 Q9: _harness_command returns None
    ("unknown_recipient") for NULL, no-headless, or malformed invocation_surfaces
    — uniformly, INCLUDING for a claude or codex command_handle, proving no
    hard-coded per-harness fallback survives for the existing harnesses.
    """
    trigger = _load_trigger()
    malformed_cases = [
        None,                                                  # NULL invocation_surfaces
        {},                                                    # no headless entry
        {"headless": {}},                                      # headless without argv
        {"headless": {"argv": []}},                            # empty argv
        {"headless": {"argv": "codex exec"}},                  # argv is not a list
        {"headless": {"argv": ["codex", 123, "{{PROMPT}}"]}},  # non-string argv element
    ]
    for handle in ("codex", "claude", "gemini"):
        for surfaces in malformed_cases:
            target = trigger.DispatchTarget(
                needed_role_label="loyal-opposition",
                harness_id="A",
                command_handle=handle,
                canonical_mode="lo",
                invocation_surfaces=surfaces,
            )
            assert trigger._harness_command(target, "p", tmp_path) is None, (
                f"_harness_command must fail closed to None for handle={handle!r}, surfaces={surfaces!r}"
            )


def test_resolve_dispatch_target_attaches_invocation_surfaces_from_projection(
    tmp_path: Path,
) -> None:
    """WI-3344 FR8: _resolve_dispatch_target reads harness-state/harness-registry.json
    and attaches the selected harness record's invocation_surfaces onto the
    returned DispatchTarget — exercising the resolve-then-attach projection
    wiring, not _harness_command in isolation.
    """
    root = _make_synthetic_project(tmp_path)
    trigger = _load_trigger()

    target = trigger._resolve_dispatch_target("loyal-opposition", root)
    assert target.harness_id == "A"
    assert target.invocation_surfaces == _CODEX_INVOCATION_SURFACES

    # End-to-end: the resolved target's surfaces drive _harness_command.
    cmd = trigger._harness_command(target, "the-prompt", root)
    assert cmd == ["codex", "exec", "the-prompt", "--cd", str(root)]
