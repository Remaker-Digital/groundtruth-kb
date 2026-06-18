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
from datetime import UTC
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"

# WI-3344: invocation_surfaces headless argv templates. {{PROMPT}} and
# {{PROJECT_ROOT}} are the placeholder tokens _harness_command substitutes as
# individual argv elements. Shared by the synthetic fixture and the FR8 tests.
_CODEX_INVOCATION_SURFACES = {"headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}}
_CLAUDE_INVOCATION_SURFACES = {
    "headless": {"argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]}
}


def _allowed_tool_set(raw: str) -> set[str]:
    return {part.strip() for part in raw.split() if part.strip()}


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


def _frozen_selected_items_for_prompt(items: list[object], max_items: int) -> list[object]:
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
                        "event_driven_hooks": True,
                        "role": ["loyal-opposition"],
                        "invocation_surfaces": _CODEX_INVOCATION_SURFACES,
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "event_driven_hooks": True,
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
    stripped = body.lstrip()
    if stripped and not stripped.startswith(("NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "WITHDRAWN")):
        if name.endswith("-001.md"):
            body = "NEW\n\n" + body
        elif name.endswith("-002.md"):
            body = "GO\n\n" + body
        stripped = body.lstrip()
    if "author_session_context_id:" not in body and not stripped.startswith(("GO", "NO-GO", "VERIFIED")):
        body = body.rstrip() + "\nauthor_session_context_id: fixture-author-session\n"
    (root / "bridge" / name).write_text(body, encoding="utf-8")


def _write_authorized_go_thread(root: Path, doc: str, target_paths: list[str] | None = None) -> str:
    if target_paths is None:
        target_paths = ["scripts/cross_harness_bridge_trigger.py"]
    proposal = "\n".join(
        [
            "NEW",
            "",
            f"# Fixture proposal {doc}",
            "",
            f"target_paths: {json.dumps(target_paths)}",
            "",
            "## Specification Links",
            "",
            "- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge authority.",
            "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - spec linkage.",
            "",
            "## Requirement Sufficiency",
            "",
            "Existing requirements are sufficient.",
            "",
            "## Verification Plan",
            "",
            "Run focused dispatch packet tests.",
            "",
        ]
    )
    _write_bridge_file(root, f"{doc}.md", proposal)
    _write_bridge_file(root, f"{doc}-002.md", "GO\n\nFixture GO.\n")
    return f"# bridge index\n\nDocument: {doc}\nGO: bridge/{doc}-002.md\nNEW: bridge/{doc}.md\n"


def _index_with_one_new(root: Path, doc: str = "example-thread") -> str:
    """Build an INDEX with one NEW entry and create the referenced file."""
    _write_bridge_file(root, f"{doc}-001.md", "bridge_kind: implementation_proposal\n")
    return f"# bridge index\n\nDocument: {doc}\nNEW: bridge/{doc}-001.md\n"


def _index_with_new_threads(root: Path, docs: list[str]) -> str:
    """Build a newest-first INDEX with multiple NEW entries."""
    lines = ["# bridge index", ""]
    for doc in docs:
        _write_bridge_file(root, f"{doc}-001.md")
        lines.extend([f"Document: {doc}", f"NEW: bridge/{doc}-001.md", ""])
    return "\n".join(lines)


def _index_with_one_go(root: Path, doc: str = "example-thread") -> str:
    """Build an INDEX whose top status is GO (Prime-actionable)."""
    _write_bridge_file(root, f"{doc}-001.md", "bridge_kind: implementation_proposal\n")
    _write_bridge_file(root, f"{doc}-002.md", "bridge_kind: implementation_proposal\n")
    return f"# bridge index\n\nDocument: {doc}\nGO: bridge/{doc}-002.md\nNEW: bridge/{doc}-001.md\n"


# ──────────────────────────────────────────────────────────────────────────
# T-2-signature-computation
# ──────────────────────────────────────────────────────────────────────────


def test_fab10_work_intent_claim_contract_uses_child_dispatch_id() -> None:
    trigger = _load_trigger()
    dispatch_id = "2026-06-12T22-10-00Z-prime-builder-A-abc123"

    assert trigger.WORK_INTENT_TRIGGER_TTL_SECONDS >= 600
    assert trigger._work_intent_session_id(dispatch_id) == dispatch_id
    assert ":" not in trigger._new_dispatch_id("prime-builder:A")


def test_fab10_dispatch_retry_knobs_prefer_gtkb_names(monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.setenv("GTKB_DISPATCH_MAX_RETRIES", "7")
    monkeypatch.setenv("OLLAMA_MAX_RETRIES", "2")
    monkeypatch.setenv("GTKB_DISPATCH_RETRY_DELAY_SECONDS", "11")
    monkeypatch.setenv("OLLAMA_RETRY_DELAY_SECONDS", "22")

    assert trigger._dispatch_max_retries() == 7
    assert trigger._dispatch_retry_delay_seconds() == 11

    monkeypatch.delenv("GTKB_DISPATCH_MAX_RETRIES")
    monkeypatch.delenv("GTKB_DISPATCH_RETRY_DELAY_SECONDS")

    assert trigger._dispatch_max_retries() == 2
    assert trigger._dispatch_retry_delay_seconds() == 22


def test_fab10_circuit_breaker_half_open_after_retry_window() -> None:
    from datetime import datetime, timedelta

    trigger = _load_trigger()
    old = {"circuit_breaker_tripped_at": (datetime.now(UTC) - timedelta(seconds=601)).isoformat()}
    recent = {"circuit_breaker_tripped_at": (datetime.now(UTC) - timedelta(seconds=10)).isoformat()}

    assert trigger._circuit_breaker_half_open_allowed(old, 600) is True
    assert trigger._circuit_breaker_half_open_allowed(recent, 600) is False


def test_fab10_prime_work_intent_held_logging_dedupes_per_holder_and_slug(tmp_path: Path) -> None:
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    item = SimpleNamespace(document_name="fixture-thread", top_status="GO", top_file="bridge/fixture-thread-002.md")
    holder = {"session_id": "dispatch-1", "ttl_expires_at": "2026-06-12T22:30:00+00:00"}

    for _ in range(2):
        trigger._record_prime_work_intent_held(
            state_dir=state_dir,
            recipient="prime-builder:B",
            dispatch_id="dispatch-2",
            item=item,
            holder=holder,
        )

    # WI-4396: work_intent_already_held is an expected lease/contention
    # suppression. It is routed to dispatch-suppressions.jsonl, NOT the
    # actionable dispatch-failures.jsonl. The per-holder/per-slug dedupe still
    # collapses the two identical calls to a single record.
    records = _suppression_records(state_dir)
    assert len(records) == 1
    assert records[0]["reason"] == "work_intent_already_held"
    assert records[0]["holder_session_id"] == "dispatch-1"
    assert _failure_records(state_dir) == []

    trigger._record_prime_work_intent_held(
        state_dir=state_dir,
        recipient="prime-builder:B",
        dispatch_id="dispatch-3",
        item=item,
        holder={"session_id": "dispatch-3"},
    )
    assert len(_suppression_records(state_dir)) == 2
    assert _failure_records(state_dir) == []


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

    summary_a = trigger.run_trigger(project_root=root, state_dir=state_dir_a, dry_run=True)
    summary_b = trigger.run_trigger(project_root=root, state_dir=state_dir_b, dry_run=True)

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
    summary_empty = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert summary_empty["results"]["loyal-opposition"]["reason"] == "no_pending"

    # Add a NEW entry (uncommitted edit) → dispatch fires.
    _write_index(root, _index_with_one_new(root))
    summary_new = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
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


def test_previous_fatal_worker_output_retries_same_signature(tmp_path: Path) -> None:
    """A failed prior worker must not permanently dedupe the same selected batch."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["loyal-opposition"]["reason"] == "dry_run"

    stderr_path = state_dir / "dispatch-runs" / "failed-worker.stderr.log"
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.write_text("ollama_harness: max-turn exhaustion before final assistant text\n", encoding="utf-8")

    state_path = state_dir / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    lo_state = state["recipients"]["loyal-opposition"]
    lo_state["last_launch"] = {
        "dispatch_id": "prior-dispatch",
        "launched_at": "2026-06-07T03:56:00+00:00",
        "stderr_path": str(stderr_path),
    }
    state_path.write_text(json.dumps(state), encoding="utf-8")

    retried = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    assert retried["results"]["loyal-opposition"]["reason"] == "dry_run"
    retried_state = retried["dispatch_state"]["recipients"]["loyal-opposition"]
    assert retried_state["last_result"] == "launch_failed"
    assert retried_state["previous_launch_failed"]["reason"] == "previous_launch_failed"
    assert retried_state["previous_launch_failed"]["matched_markers"][0]["label"] == "max_turn_exhaustion"

    failures = _failure_records(state_dir)
    assert any(record["reason"] == "previous_launch_failed" for record in failures)


def test_retry_delay_clears_after_launch_window_elapses(tmp_path: Path) -> None:
    """WI-4459: a retry-pending recipient whose last LAUNCH predates the
    retry-delay window must dispatch, even when ``updated_at`` is recent.

    Regression guard for the retry-delay livelock. The backoff window must be
    measured from ``last_launch.launched_at`` (written only on a real launch,
    stable across delay-only evaluations), not from ``updated_at`` (rewritten
    on every evaluation). With the pre-fix code reading ``updated_at``, a recent
    ``updated_at`` perpetually re-armed the delay and the recipient was wedged
    forever (``failure_count`` frozen, circuit breaker unreachable). This test
    FAILS against the pre-fix code and PASSES against the fix.
    """
    from datetime import datetime, timedelta

    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["loyal-opposition"]["reason"] == "dry_run"

    now = datetime.now(UTC)
    state_path = state_dir / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    # The trigger resolves the loyal-opposition target to a harness-specific
    # recipient key; set the retry state on both the role and role:harness keys.
    for key in ("loyal-opposition", "loyal-opposition:A"):
        lo_state = state["recipients"][key]
        lo_state["failure_count"] = 1
        lo_state["circuit_breaker_tripped"] = False
        # Stale prior dispatched signature => the current actionable signature is
        # treated as "changed" (reaches the dispatch branch + retry-delay gate).
        lo_state["last_dispatched_signature"] = "stale-signature-forces-dispatch-branch"
        lo_state["signature"] = "stale-signature-forces-dispatch-branch"
        # Last LAUNCH is well outside the retry-delay window (default 300s);
        # exit_code_processed=True so the prior failure is not reprocessed
        # (failure_count stays 1, i.e., is_retry_pending).
        lo_state["last_launch"] = {
            "dispatch_id": "prior-old-launch",
            "launched": True,
            "exit_code": 1,
            "exit_code_processed": True,
            "launched_at": (now - timedelta(seconds=3600)).isoformat(),
        }
        # updated_at is recent (pre-fix code would re-arm the delay here).
        lo_state["updated_at"] = (now - timedelta(seconds=5)).isoformat()
    state_path.write_text(json.dumps(state), encoding="utf-8")

    retried = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    reason = retried["results"]["loyal-opposition"]["reason"]
    assert reason != "retry_delay_enforced", (
        f"retry-delay must clear when the last launch predates the window; got {reason!r} (livelock regression)"
    )
    assert reason == "dry_run"


def test_retry_delay_enforced_within_launch_window(tmp_path: Path) -> None:
    """WI-4459: a retry-pending recipient whose last LAUNCH is within the
    retry-delay window must still be delayed. Guards against the fix disabling
    backoff entirely.
    """
    from datetime import datetime, timedelta

    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["loyal-opposition"]["reason"] == "dry_run"

    now = datetime.now(UTC)
    state_path = state_dir / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    for key in ("loyal-opposition", "loyal-opposition:A"):
        lo_state = state["recipients"][key]
        lo_state["failure_count"] = 1
        lo_state["circuit_breaker_tripped"] = False
        lo_state["last_dispatched_signature"] = "stale-signature-forces-dispatch-branch"
        lo_state["signature"] = "stale-signature-forces-dispatch-branch"
        # Last LAUNCH is recent (within the 300s window) => delay enforced.
        lo_state["last_launch"] = {
            "dispatch_id": "prior-recent-launch",
            "launched": True,
            "exit_code": 1,
            "exit_code_processed": True,
            "launched_at": (now - timedelta(seconds=10)).isoformat(),
        }
        lo_state["updated_at"] = (now - timedelta(seconds=5)).isoformat()
    state_path.write_text(json.dumps(state), encoding="utf-8")

    retried = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    assert retried["results"]["loyal-opposition"]["reason"] == "retry_delay_enforced"


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
    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
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
    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

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
    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=2, dry_run=True)

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
        "trigger must sign the selected dispatch batch (post-cap, post-reverse), not the full filtered list"
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


def test_ollama_lo_dispatch_caps_selected_batch_to_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ollama LO dispatch keeps the global cap unchanged but selects one item."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {
                    "headless": {
                        "argv": ["ollama-harness", "{{PROMPT}}"],
                        "max_items": 1,
                    }
                },
            ),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_three_new(root))

    trigger = _load_trigger()
    monkeypatch.setattr(trigger, "_evaluate_ollama_dispatch_readiness", lambda _root: {"ready": True})

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=2, dry_run=True)

    assert trigger.DEFAULT_MAX_ITEMS == 2
    rec = summary["dispatch_state"]["recipients"]["loyal-opposition"]
    assert rec["pending_count"] == 3
    assert rec["selected_count"] == 1
    command_head = summary["results"]["loyal-opposition"]["command_head"]
    assert command_head[0] == "ollama-harness"
    assert command_head[1].startswith("::init gtkb lo\n")


def test_spawn_gate_skips_unlaunchable_harness_with_distinct_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4525: a dispatch target whose argv head does not resolve to a
    launchable executable is skipped BEFORE spawn, recorded with a distinct
    ``target_unlaunchable`` reason, and does NOT consume circuit-breaker
    retries -- the masking failure mode of the 2026-06-13 hollow-venv jam."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {
                    "headless": {
                        "argv": ["gtkb-nonexistent-interpreter-xyz123.exe", "{{PROMPT}}"],
                        "max_items": 1,
                    }
                },
            ),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_one_new(root))

    trigger = _load_trigger()
    # Clear the ambient loop-prevention var so the gate is exercised regardless
    # of whether the test runs inside a dispatch-aware harness session (which
    # sets GTKB_NO_CROSS_HARNESS_TRIGGER=1) or in CI (where it is unset).
    monkeypatch.delenv("GTKB_NO_CROSS_HARNESS_TRIGGER", raising=False)
    monkeypatch.setattr(trigger, "_evaluate_ollama_dispatch_readiness", lambda _root: {"ready": True})

    spawn_calls: list[object] = []

    def _fake_spawn(**kwargs: object) -> dict[str, object]:
        spawn_calls.append(kwargs.get("target"))
        return {"launched": True, "reason": "fake_spawn", "dispatch_id": "fake"}

    monkeypatch.setattr(trigger, "_spawn_harness", _fake_spawn)

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=False)

    # (a) the unlaunchable target was NOT spawned.
    assert spawn_calls == []

    rec = summary["dispatch_state"]["recipients"]["loyal-opposition"]
    # (d) the distinct unlaunchable state is recorded.
    assert rec["last_result"] == "target_unlaunchable"
    # (c) the circuit-breaker failure counter was NOT consumed.
    assert int(rec.get("failure_count", 0)) == 0
    assert not rec.get("circuit_breaker_tripped")

    # (b) a distinct dispatch-failure record was written with launched=False.
    unlaunchable = [r for r in _failure_records(state_dir) if r.get("reason") == "target_unlaunchable"]
    assert unlaunchable, "expected a target_unlaunchable dispatch-failure record"
    assert unlaunchable[0]["launched"] is False
    # dispatch_state_key carries the durable role label plus harness id suffix.
    assert unlaunchable[0]["recipient"].startswith("loyal-opposition")


# ──────────────────────────────────────────────────────────────────────────
# T-2-reciprocal-dispatch — per Codex F2 on -008
# ──────────────────────────────────────────────────────────────────────────


def test_dispatched_child_env_does_not_inherit_disable_var(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    assert child_env["GTKB_INHERITED_SESSION_ID"] == meta["dispatch_id"], (
        "GTKB_INHERITED_SESSION_ID must mirror dispatch_id for compatibility work-intent surfaces"
    )
    assert "GTKB_IMPLEMENTATION_AUTH_BRIDGE_IDS" not in child_env


def test_prime_spawn_creates_dispatch_authorization_packet_and_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_synthetic_project(tmp_path)
    doc = "prime-implementation"
    _write_index(root, _write_authorized_go_thread(root, doc))
    state_dir = tmp_path / "state"
    trigger = _load_trigger()
    captured_envs: list[dict[str, str]] = []

    class _FakeProcess:
        pid = 12345

    def _fake_popen(*_args, **kwargs):
        captured_envs.append(kwargs.get("env", {}))
        return _FakeProcess()

    import subprocess as _subprocess

    monkeypatch.setattr(_subprocess, "Popen", _fake_popen)

    fake_item = type(
        "FakeItem",
        (),
        {
            "document_name": doc,
            "top_status": "GO",
            "top_file": f"bridge/{doc}-002.md",
            "dispatchable": True,
        },
    )()
    prime_target = trigger.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="B",
        command_handle="claude",
        canonical_mode="pb",
        invocation_surfaces=_CLAUDE_INVOCATION_SURFACES,
    )

    meta = trigger._spawn_harness(
        target=prime_target,
        items=[fake_item],
        project_root=root,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
        dispatch_id="dispatch-prime",
    )

    assert meta["launched"] is True
    current = json.loads(
        (root / ".gtkb-state" / "implementation-authorizations" / "current.json").read_text(encoding="utf-8")
    )
    assert current["bridge_id"] == doc
    assert current["target_path_globs"] == ["scripts/cross_harness_bridge_trigger.py"]
    assert (root / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{doc}.json").is_file()
    child_env = captured_envs[0]
    assert child_env["GTKB_IMPLEMENTATION_AUTH_DISPATCH_ID"] == "dispatch-prime"
    assert child_env["GTKB_INHERITED_SESSION_ID"] == "dispatch-prime"
    assert child_env["GTKB_IMPLEMENTATION_AUTH_BRIDGE_IDS"] == doc
    assert child_env["GTKB_IMPLEMENTATION_AUTH_CURRENT_BRIDGE_ID"] == doc
    assert child_env["GTKB_IMPLEMENTATION_AUTH_PACKET_HASHES"] == current["packet_hash"]


def test_prime_spawn_fails_closed_when_dispatch_authorization_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_synthetic_project(tmp_path)
    doc = "malformed-implementation"
    _write_bridge_file(root, f"{doc}.md", "# Missing implementation packet metadata\n")
    _write_bridge_file(root, f"{doc}-002.md", "GO\n\nFixture GO.\n")
    _write_index(root, f"# bridge index\n\nDocument: {doc}\nGO: bridge/{doc}-002.md\nNEW: bridge/{doc}.md\n")
    state_dir = tmp_path / "state"
    trigger = _load_trigger()
    popen_calls: list[object] = []

    def _fail_popen(*args, **kwargs):
        popen_calls.append((args, kwargs))
        raise AssertionError("subprocess.Popen must not be called after packet failure")

    import subprocess as _subprocess

    monkeypatch.setattr(_subprocess, "Popen", _fail_popen)

    fake_item = type(
        "FakeItem",
        (),
        {
            "document_name": doc,
            "top_status": "GO",
            "top_file": f"bridge/{doc}-002.md",
            "dispatchable": True,
        },
    )()
    prime_target = trigger.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="B",
        command_handle="claude",
        canonical_mode="pb",
        invocation_surfaces=_CLAUDE_INVOCATION_SURFACES,
    )

    meta = trigger._spawn_harness(
        target=prime_target,
        items=[fake_item],
        project_root=root,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
        dispatch_id="dispatch-prime",
    )

    assert meta["launched"] is False
    assert meta["reason"] == "implementation_authorization_packet_failed"
    assert popen_calls == []
    failures = [
        json.loads(line) for line in (state_dir / "dispatch-failures.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert failures[-1]["document_name"] == doc
    assert failures[-1]["reason"] == "implementation_authorization_packet_failed"


# ──────────────────────────────────────────────────────────────────────────
# WI-4358: cross-harness trigger filter NO-GO items before authorization
#
# The bug: _issue_dispatch_authorization_for_selected built bridge_ids from
# ALL selected items regardless of top_status, so an all-NO-GO selected batch
# (revision tasks) tripped create_authorization_packet's GO-only guard and
# raised AuthorizationError pre-spawn. The 621 confirmed silent dispatch
# failures in .gtkb-state/bridge-poller/dispatch-failures.jsonl trace back
# here.
#
# The fix: filter selected to GO-only before building bridge_ids; return
# ok=True with empty context when no GO items remain (NO-GO items are still
# visible in the dispatch prompt text via Prime's prompt-context render).
# ──────────────────────────────────────────────────────────────────────────


def _no_go_fake_item(doc: str, status: str) -> object:
    """Build a minimal FakeItem fixture with document_name + top_status (WI-4358)."""
    return type(
        "FakeItem",
        (),
        {
            "document_name": doc,
            "top_status": status,
            "top_file": f"bridge/{doc}-002.md",
            "dispatchable": True,
        },
    )()


def test_issue_dispatch_auth_skips_no_go_items(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-4358: all-NO-GO selected batch returns ok=True with empty context
    and never calls issue_dispatch_authorization_packets.
    """
    root = _make_synthetic_project(tmp_path)
    trigger = _load_trigger()

    def _fake_issue(*_args, **_kwargs):
        raise AssertionError("issue_dispatch_authorization_packets must not be called for all-NO-GO batch")

    monkeypatch.setattr(trigger, "issue_dispatch_authorization_packets", _fake_issue)

    result = trigger._issue_dispatch_authorization_for_selected(
        [
            _no_go_fake_item("revise-thread-a", "NO-GO"),
            _no_go_fake_item("revise-thread-b", "NO-GO"),
        ],
        project_root=root,
        state_dir=tmp_path / "state",
        recipient="prime-builder",
        dispatch_id="dispatch-no-go-only",
    )

    assert result == {"ok": True, "reason": None, "context": {}}


def test_issue_dispatch_auth_uses_go_items_from_mixed_list(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-4358: mixed GO+NO-GO selected batch produces an issue call with only
    the GO items' document_name(s).
    """
    root = _make_synthetic_project(tmp_path)
    trigger = _load_trigger()
    captured_bridge_ids: list[list[str]] = []

    def _fake_issue(_root, bridge_ids, *, dispatch_id):  # noqa: ARG001 (signature mirrors prod)
        captured_bridge_ids.append(list(bridge_ids))
        return {"go-thread": {"some": "context"}}

    monkeypatch.setattr(trigger, "issue_dispatch_authorization_packets", _fake_issue)

    result = trigger._issue_dispatch_authorization_for_selected(
        [
            _no_go_fake_item("go-thread", "GO"),
            _no_go_fake_item("revise-thread", "NO-GO"),
        ],
        project_root=root,
        state_dir=tmp_path / "state",
        recipient="prime-builder",
        dispatch_id="dispatch-mixed",
    )

    assert result["ok"] is True
    assert captured_bridge_ids == [["go-thread"]], (
        "Only the GO item's document_name should reach issue_dispatch_authorization_packets"
    )


def test_spawn_harness_dispatches_no_go_only_batch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-4358 spawn-level regression: _spawn_harness must launch Prime Builder
    even when the entire selected batch is NO-GO (revision tasks).

    Asserts:
    - subprocess.Popen is called exactly once (harness launch proceeds);
    - the dispatch prompt text passed to the child includes the NO-GO item's
      document name (revision task is visible to the spawned session);
    - no implementation-authorization packet file is created;
    - no GTKB_IMPLEMENTATION_AUTH_* env vars are set in the child environment.
    """
    root = _make_synthetic_project(tmp_path)
    doc = "revise-no-go-thread"
    _write_bridge_file(root, f"{doc}-001.md", "bridge_kind: implementation_proposal\n")
    _write_bridge_file(root, f"{doc}-002.md", "NO-GO\n\nFixture NO-GO.\n")
    _write_index(
        root,
        f"# bridge index\n\nDocument: {doc}\nNO-GO: bridge/{doc}-002.md\nNEW: bridge/{doc}-001.md\n",
    )

    state_dir = tmp_path / "state"
    trigger = _load_trigger()
    captured_envs: list[dict[str, str]] = []
    captured_argv: list[list[str]] = []

    class _FakeProcess:
        pid = 99999

    def _fake_popen(args, *_args, env=None, **_kwargs):
        captured_argv.append(list(args))
        captured_envs.append(dict(env) if env is not None else {})
        return _FakeProcess()

    import subprocess as _subprocess

    monkeypatch.setattr(_subprocess, "Popen", _fake_popen)

    no_go_item = _no_go_fake_item(doc, "NO-GO")
    prime_target = trigger.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="B",
        command_handle="claude",
        canonical_mode="pb",
        invocation_surfaces=_CLAUDE_INVOCATION_SURFACES,
    )

    meta = trigger._spawn_harness(
        target=prime_target,
        items=[no_go_item],
        project_root=root,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
        dispatch_id="dispatch-no-go-only",
    )

    assert meta["launched"] is True, (
        "Spawn must succeed for all-NO-GO selected batch (revision tasks still need a worker)"
    )
    assert len(captured_argv) == 1, "Popen must be called exactly once"

    # The NO-GO document name MUST appear in the dispatch prompt text so the
    # spawned worker can act on the revision task.
    prompt_text = " ".join(captured_argv[0])
    assert doc in prompt_text, f"Dispatch prompt must include NO-GO thread {doc}"

    # No implementation-authorization packet file should exist for an all-NO-GO
    # batch (no GO items means no packet creation occurred).
    auth_current = root / ".gtkb-state" / "implementation-authorizations" / "current.json"
    assert not auth_current.exists(), "No impl-auth packet should be created for all-NO-GO batch"

    # The proposal -005 explicitly admits two env-contract options for the
    # empty-GO branch: (a) no GTKB_IMPLEMENTATION_AUTH_* env vars at all, or
    # (b) the env contract is documented and asserted. The current spawn code
    # implements option (b): DISPATCH_ID echoes the dispatch_id; BRIDGE_IDS,
    # CURRENT_BRIDGE_ID, and PACKET_HASHES are present but empty. The empty
    # values are the load-bearing guarantee: a spawned worker cannot believe
    # it holds a real impl-auth packet because there is no bridge id to cite
    # and no packet hash to validate against.
    child_env = captured_envs[0]
    assert child_env.get("GTKB_IMPLEMENTATION_AUTH_BRIDGE_IDS", None) == "", (
        "BRIDGE_IDS must be empty for all-NO-GO batch (no fake bridge id leaks to worker)"
    )
    assert child_env.get("GTKB_IMPLEMENTATION_AUTH_CURRENT_BRIDGE_ID", None) == "", (
        "CURRENT_BRIDGE_ID must be empty for all-NO-GO batch"
    )
    assert child_env.get("GTKB_IMPLEMENTATION_AUTH_PACKET_HASHES", None) == "", (
        "PACKET_HASHES must be empty for all-NO-GO batch"
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
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "-c",
        "commit.gpgsign=false",
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


def test_stop_hook_emits_exactly_braces_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
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
    assert captured.out == "{}\n", f"Expected stdout exactly '{{}}\\n' for --stop-hook; got: {captured.out!r}"
    # Stdout MUST parse as a JSON object.
    parsed = json.loads(captured.out)
    assert parsed == {}, "Stop-hook stdout must parse to an empty dict"


def test_stop_hook_overrides_verbose(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
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
    sig_before = json.loads(state_path.read_text(encoding="utf-8"))["recipients"]["loyal-opposition"]["signature"]

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
    assert rec["last_result"] != "unchanged", "Stop hook must detect changed signature even when PostToolUse missed it"
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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _real_stop_hook_commands(relative_config_path: str) -> list[str]:
    config = json.loads((_repo_root() / relative_config_path).read_text(encoding="utf-8"))
    commands: list[str] = []
    for group in config["hooks"]["Stop"]:
        for hook in group.get("hooks", []):
            command = hook.get("command")
            if isinstance(command, str):
                commands.append(command)
    return commands


def _command_indices(commands: list[str], *needles: str) -> list[int]:
    return [index for index, command in enumerate(commands) if all(needle in command for needle in needles)]


def _single_command_index(commands: list[str], *needles: str) -> int:
    matches = _command_indices(commands, *needles)
    assert len(matches) == 1, f"expected exactly one command matching {needles!r}; found {matches!r}"
    return matches[0]


def test_stop_hook_order_clears_codex_lock_before_bridge_reconciliation() -> None:
    commands = _real_stop_hook_commands(".codex/hooks.json")

    session_stop_index = _single_command_index(
        commands,
        "active_session_heartbeat.py",
        "--mode session-stop",
        "--role codex",
    )
    bridge_stop_index = _single_command_index(commands, "cross_harness_bridge_trigger.py", "--stop-hook")

    assert session_stop_index == bridge_stop_index - 1
    assert _command_indices(commands[bridge_stop_index + 1 :], "--mode session-stop", "--role codex") == []


def test_stop_hook_order_clears_claude_lock_before_bridge_reconciliation() -> None:
    commands = _real_stop_hook_commands(".claude/settings.json")

    owner_stop_index = _single_command_index(commands, "owner-decision-tracker.py", "--mode stop")
    session_stop_index = _single_command_index(
        commands,
        "active_session_heartbeat.py",
        "--mode session-stop",
        "--role claude",
    )
    bridge_stop_index = _single_command_index(commands, "cross_harness_bridge_trigger.py", "--stop-hook")

    assert owner_stop_index < bridge_stop_index
    assert session_stop_index == bridge_stop_index - 1
    assert _command_indices(commands[bridge_stop_index + 1 :], "--mode session-stop", "--role claude") == []


def test_stop_reconciliation_after_session_stop_sees_inactive_lock(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    trigger = _load_trigger()
    target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="codex",
        canonical_mode="lo",
        invocation_surfaces=_CODEX_INVOCATION_SURFACES,
    )

    lock_path = state_dir / target.active_session_lock_name
    lock_path.write_text(json.dumps({"role": "codex"}), encoding="utf-8")
    assert trigger.check_counterpart_active(target, state_dir) is True

    lock_path.unlink()
    assert trigger.check_counterpart_active(target, state_dir) is False


def test_stop_reconciliation_preserves_existing_output_contract(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))

    rc = _load_trigger().main(["--project-root", str(root), "--state-dir", str(state_dir), "--stop-hook", "--dry-run"])
    assert rc == 0
    assert json.loads(capsys.readouterr().out) == {}


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
    # WI-3342 IP-4: the trigger's topology check (_is_single_harness_topology
    # via _read_role_assignments) resolves the role map from the DB-backed
    # registry projection harness-state/harness-registry.json, whose
    # ``harnesses`` field is a LIST of unified records. Single-harness topology
    # is one harness ID with a multi-element role-set.
    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "MemBase harnesses table (groundtruth.db)",
                "harnesses": [
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["prime-builder", "loyal-opposition"],
                    }
                ],
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
    lines = [line for line in failures_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = [json.loads(line) for line in lines]
    assert len(records) == 2, f"expected 2 audit entries, got {len(records)}: {records}"
    by_role = {rec["recipient"]: rec for rec in records}
    assert "prime-builder" in by_role and "loyal-opposition" in by_role
    for rec in by_role.values():
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


def test_diagnose_reports_current_role_recipient_keys_and_single_harness_as_inert(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Diagnose must read current role-label state keys, not legacy prime/codex keys."""
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "recipients": {
            "prime-builder": {
                "last_result": "single_harness_topology_not_applicable",
                "pending_count": 0,
                "selected_count": 0,
                "updated_at": "2026-05-19T21:00:00+00:00",
            },
            "loyal-opposition": {
                "last_result": "single_harness_topology_not_applicable",
                "pending_count": 0,
                "selected_count": 0,
                "updated_at": "2026-05-19T21:00:00+00:00",
            },
        },
        "schema_version": 1,
        "updated_at": "2026-05-19T21:00:00+00:00",
    }
    (state_dir / "dispatch-state.json").write_text(json.dumps(state), encoding="utf-8")

    trigger = _load_trigger()
    monkeypatch.setattr(
        trigger,
        "_read_role_assignments",
        lambda *a, **k: {
            "harnesses": {
                "C": {"status": "active", "role": ["prime-builder"]},
                "D": {"status": "active", "role": ["loyal-opposition"]},
            }
        },
    )
    output = trigger._emit_diagnose_summary(state_dir)

    assert "- prime-builder: last_result=single_harness_topology_not_applicable" in output
    assert "- loyal-opposition: last_result=single_harness_topology_not_applicable" in output
    assert "- prime: (no state recorded)" not in output
    assert "- codex: (no state recorded)" not in output
    assert "single-harness topology; cross-harness dispatch not applicable" in output
    assert "HEALTHY" in output
    assert "DEGRADED" not in output


def test_diagnose_migrates_legacy_recipient_keys_before_liveness(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Legacy dispatch-state keys are translated before diagnose renders liveness."""
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "recipients": {
            "prime": {
                "last_result": "no_pending",
                "pending_count": 0,
                "selected_count": 0,
                "updated_at": "2026-05-19T21:00:00+00:00",
            },
            "codex": {
                "last_result": "target_active_session_present",
                "pending_count": 2,
                "selected_count": 2,
                "updated_at": "2026-05-19T21:00:00+00:00",
            },
        },
        "schema_version": 1,
        "updated_at": "2026-05-19T21:00:00+00:00",
    }
    (state_dir / "dispatch-state.json").write_text(json.dumps(state), encoding="utf-8")

    trigger = _load_trigger()
    monkeypatch.setattr(
        trigger,
        "_read_role_assignments",
        lambda *a, **k: {
            "harnesses": {
                "C": {"status": "active", "role": ["prime-builder"]},
                "D": {"status": "active", "role": ["loyal-opposition"]},
            }
        },
    )
    output = trigger._emit_diagnose_summary(state_dir)

    assert "- prime-builder: last_result=no_pending" in output
    assert "- loyal-opposition: last_result=target_active_session_present" in output
    assert "- prime: last_result=" not in output
    assert "- codex: last_result=" not in output
    assert "HEALTHY" in output
    assert "DEGRADED" not in output


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
    """WI-3265 IP-2: a held target lease drives the
    loyal-opposition recipient to the `active_session_suppressed` class.
    """
    from bridge_lease_registry import acquire_lease

    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    _write_index(root, _index_with_one_new(root))

    # Acquire a lease on example-thread (loyal-opposition recipient)
    handle = acquire_lease("example-thread", action="test-harness", state_dir=state_dir)
    assert handle is not None

    trigger = _load_trigger()
    trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    lo = [r for r in _read_diagnostics(state_dir) if r["recipient"] == "loyal-opposition"]
    assert len(lo) == 1
    assert lo[0]["last_result"] == "target_active_session_present"
    assert lo[0]["classification"] == "active_session_suppressed"


def test_stop_reconciliation_retries_after_suppressed_lease_is_released(tmp_path: Path) -> None:
    """Slice 4 D3: a Stop reconciliation suppressed by active worker ownership
    remains retryable once the worker lease is gone.
    """
    from bridge_lease_registry import acquire_lease, release_lease

    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    _write_index(root, _index_with_one_new(root))

    handle = acquire_lease("example-thread", action="test-worker", state_dir=state_dir)
    assert handle is not None

    trigger = _load_trigger()
    held = trigger.run_trigger(
        project_root=root,
        state_dir=state_dir,
        dry_run=True,
        invocation_source="Stop",
    )
    assert held["results"]["loyal-opposition"]["reason"] == "target_active_session_present"
    state = json.loads((state_dir / "dispatch-state.json").read_text(encoding="utf-8"))
    suppressed_signature = state["recipients"]["loyal-opposition"]["last_suppressed_signature"]
    assert suppressed_signature
    assert state["recipients"]["loyal-opposition"].get("last_dispatched_signature") is None

    release_lease(handle)
    retried = trigger.run_trigger(
        project_root=root,
        state_dir=state_dir,
        dry_run=True,
        invocation_source="Stop",
    )

    assert retried["results"]["loyal-opposition"]["reason"] == "dry_run"
    state = json.loads((state_dir / "dispatch-state.json").read_text(encoding="utf-8"))
    rec = state["recipients"]["loyal-opposition"]
    assert rec["last_launch"]["reason"] == "dry_run"
    assert rec["last_dispatched_signature"] == suppressed_signature
    assert rec["last_suppressed_signature"] is None


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
        "timestamp",
        "invocation_source",
        "pid",
        "session_id",
        "index_mtime",
        "index_signature_pre",
        "index_signature_post",
        "dispatch_state_mtime_pre",
        "dispatch_state_mtime_post",
        "classification",
        "last_dispatched_signature",
        "last_suppressed_signature",
        "elapsed_ms",
        "recipient",
        "last_result",
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


def test_unchanged_signature_preserves_last_launch_metadata(tmp_path: Path) -> None:
    """A deduped unchanged run keeps prior launch log paths available."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()

    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["loyal-opposition"]["reason"] == "dry_run"
    state = json.loads((state_dir / "dispatch-state.json").read_text(encoding="utf-8"))
    first_launch = state["recipients"]["loyal-opposition"]["last_launch"]

    second = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert second["results"]["loyal-opposition"]["reason"] == "unchanged"
    state = json.loads((state_dir / "dispatch-state.json").read_text(encoding="utf-8"))

    assert state["recipients"]["loyal-opposition"]["last_launch"] == first_launch


def test_unchanged_signature_with_previous_fatal_worker_log_retries(tmp_path: Path) -> None:
    """A prior fatal worker marker makes the same signature retryable."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()

    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["loyal-opposition"]["reason"] == "dry_run"

    runs_dir = state_dir / "dispatch-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = runs_dir / "prior.stdout.log"
    stderr_path = runs_dir / "prior.stderr.log"
    stdout_path.write_text("", encoding="utf-8")
    stderr_path.write_text(
        "ollama_harness: max-turn exhaustion before final assistant text\n",
        encoding="utf-8",
    )

    state_path = state_dir / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    rec = state["recipients"]["loyal-opposition"]
    rec["last_result"] = "launched"
    rec["last_launch"] = {
        "dispatch_id": "prior-dispatch",
        "recipient": "loyal-opposition",
        "launched": True,
        "launched_at": "2026-06-07T06:00:00+00:00",
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    retried = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert retried["results"]["loyal-opposition"]["reason"] == "dry_run"

    previous_failures = [rec for rec in _failure_records(state_dir) if rec.get("reason") == "previous_launch_failed"]
    assert previous_failures
    assert previous_failures[-1]["prior_dispatch_id"] == "prior-dispatch"
    assert previous_failures[-1]["matched_markers"][0]["label"] == "max_turn_exhaustion"


# ──────────────────────────────────────────────────────────────────────────
# WI-3344 — data-driven _harness_command() from invocation_surfaces (FR8)
# Per bridge/gtkb-harness-data-driven-dispatch-003.md (Codex GO at -004).
# ──────────────────────────────────────────────────────────────────────────


def test_harness_command_builds_argv_from_invocation_surfaces(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-3344 FR8 / DELIB-2079 Q9: _harness_command builds the dispatch argv
    solely from a harness record's invocation_surfaces.headless template,
    substituting {{PROMPT}} and {{PROJECT_ROOT}} as individual argv elements —
    for the codex, claude, and a non-claude/codex harness record alike.
    """
    trigger = _load_trigger()
    # FAB-01: this test exercises template substitution, not argv-head
    # resolution. Neutralize _normalize_argv_head (HYG-001) so command[0] is the
    # literal template head regardless of whether codex/claude/gemini happen to
    # be on the test host's PATH; normalization has its own coverage in
    # test_fab01_dispatch_substrate_revival.py.
    monkeypatch.setattr(trigger, "_normalize_argv_head", lambda head, project_root: head)
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
    assert claude_cmd == [
        "claude",
        "-p",
        prompt,
        "--add-dir",
        str(root),
        "--output-format",
        "json",
        "--permission-mode",
        "acceptEdits",
        "--allowed-tools",
        trigger.CLAUDE_WORKER_ALLOWED_TOOLS,
    ]

    third_surfaces = {"headless": {"argv": ["gemini", "-p", "{{PROMPT}}", "--root", "{{PROJECT_ROOT}}"]}}
    third_cmd = trigger._harness_command(_target("gemini", third_surfaces), prompt, root)
    assert third_cmd == ["gemini", "-p", prompt, "--root", str(root)]


def test_claude_worker_command_uses_accept_edits_and_authoring_allowlist(tmp_path: Path) -> None:
    """Slice 4 D6b: auto-dispatched Claude Prime workers must be able to
    write approved files without an interactive permission prompt.
    """
    trigger = _load_trigger()
    target = trigger.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="B",
        command_handle="claude",
        canonical_mode="pb",
        invocation_surfaces=_CLAUDE_INVOCATION_SURFACES,
    )

    command = trigger._harness_command(target, "::init gtkb pb\nwork", tmp_path)

    assert command is not None
    assert command[command.index("--permission-mode") + 1] == "acceptEdits"
    allowed = _allowed_tool_set(command[command.index("--allowed-tools") + 1])
    assert {"Read", "Edit", "Write", "Glob", "Grep", "Bash", "TodoWrite", "NotebookEdit"} <= allowed
    assert "AskUserQuestion" not in allowed
    assert "WebFetch" not in allowed
    assert "WebSearch" not in allowed
    assert all(not tool.startswith("mcp__") for tool in allowed)


def test_non_claude_worker_command_does_not_receive_claude_permission_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Slice 4 D6b is Claude-specific; Codex argv remains the registry template."""
    trigger = _load_trigger()
    # FAB-01: neutralize argv-head normalization (HYG-001) so this test stays
    # focused on the absence of Claude permission flags, host-PATH-independent.
    monkeypatch.setattr(trigger, "_normalize_argv_head", lambda head, project_root: head)
    target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="codex",
        canonical_mode="lo",
        invocation_surfaces=_CODEX_INVOCATION_SURFACES,
    )

    command = trigger._harness_command(target, "::init gtkb lo\nwork", tmp_path)

    assert command == ["codex", "exec", "::init gtkb lo\nwork", "--cd", str(tmp_path)]
    assert "--permission-mode" not in command
    assert "--allowed-tools" not in command


def test_dispatch_prompt_warns_worker_to_record_owner_decision_blockers() -> None:
    """Slice 4 D2: worker prompts must not invite unattended workers to ask
    the owner interactively.
    """
    trigger = _load_trigger()
    target = trigger.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="B",
        command_handle="claude",
        canonical_mode="pb",
        invocation_surfaces=_CLAUDE_INVOCATION_SURFACES,
    )
    item = type(
        "FakeItem",
        (),
        {
            "document_name": "gtkb-prime-worker-delivery-regression-slice-4",
            "top_status": "GO",
            "top_file": "bridge/gtkb-prime-worker-delivery-regression-slice-4-006.md",
        },
    )()

    prompt = trigger._dispatch_prompt(target, [item], max_items=1)

    assert prompt.splitlines()[0] == "::init gtkb pb"
    assert "cannot interactively ask the owner for input" in prompt
    assert "record the blocker in the bridge artifact" in prompt
    assert "asking in prose" in prompt
    assert "harness-state/harness-identities.json" in prompt
    assert "harness-state/harness-registry.json" in prompt
    assert "groundtruth_kb.harness_projection" in prompt
    assert ".claude/rules/operating-role.md" not in prompt
    assert "harness-state/{harness}/operating-role.md" not in prompt
    assert "bridge_applicability_preflight.py --bridge-id <document-name>" in prompt
    assert "adr_dcl_clause_preflight.py --bridge-id <document-name>" in prompt
    assert "clean Applicability Preflight section" in prompt
    assert "GO gtkb-prime-worker-delivery-regression-slice-4" in prompt


def test_lo_dispatch_prompt_requires_preflights_before_verdicts() -> None:
    """LO workers need explicit preflight instructions before GO/VERIFIED writes."""
    trigger = _load_trigger()
    target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="ollama",
        canonical_mode="lo",
        invocation_surfaces={"headless": {"argv": ["ollama-harness", "{{PROMPT}}"]}},
    )
    item = type(
        "FakeItem",
        (),
        {
            "document_name": "gtkb-ollama-dispatch-stall-retry-cap",
            "top_status": "NEW",
            "top_file": "bridge/gtkb-ollama-dispatch-stall-retry-cap-001.md",
        },
    )()

    prompt = trigger._dispatch_prompt(target, [item], max_items=1)

    assert prompt.splitlines()[0] == "::init gtkb lo"
    assert "Loyal Opposition verdict requirement" in prompt
    assert "bridge_applicability_preflight.py --bridge-id <document-name>" in prompt
    assert "adr_dcl_clause_preflight.py --bridge-id <document-name>" in prompt
    assert "clean Applicability Preflight section" in prompt
    assert "NEW gtkb-ollama-dispatch-stall-retry-cap" in prompt


def test_harness_command_preserves_dispatch_prompt_as_single_argv_element(tmp_path: Path) -> None:
    """The canonical init keyword must remain the first line of the argv prompt."""
    trigger = _load_trigger()
    target = trigger.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="B",
        command_handle="claude",
        canonical_mode="pb",
        invocation_surfaces=_CLAUDE_INVOCATION_SURFACES,
    )
    prompt = "::init gtkb pb\nBridge auto-dispatch notification."

    command = trigger._harness_command(target, prompt, tmp_path)

    assert command is not None
    assert command[2] == prompt
    assert command[2].splitlines()[0] == "::init gtkb pb"


def test_spawn_records_dispatch_failure_when_worker_command_cannot_be_built(tmp_path: Path) -> None:
    """Slice 4 D4: spawn failures are durable diagnosis records, not silent drops."""
    trigger = _load_trigger()
    target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="codex",
        canonical_mode="lo",
        invocation_surfaces=None,
    )
    item = type(
        "FakeItem",
        (),
        {
            "document_name": "example-thread",
            "top_status": "NEW",
            "top_file": "bridge/example-thread-001.md",
        },
    )()
    state_dir = tmp_path / "state"

    meta = trigger._spawn_harness(
        target=target,
        items=[item],
        project_root=tmp_path,
        state_dir=state_dir,
        max_items=1,
        dry_run=False,
        dispatch_id="dispatch-missing-surfaces",
    )

    assert meta["launched"] is False
    assert meta["reason"] == "unknown_recipient"
    records = _failure_records(state_dir)
    assert records[-1]["dispatch_id"] == "dispatch-missing-surfaces"
    assert records[-1]["reason"] == "unknown_recipient"


def test_harness_command_fails_closed_for_missing_or_malformed_surfaces(tmp_path: Path) -> None:
    """WI-3344 FR8 / DELIB-2079 Q9: _harness_command returns None
    ("unknown_recipient") for NULL, no-headless, or malformed invocation_surfaces
    — uniformly, INCLUDING for a claude or codex command_handle, proving no
    hard-coded per-harness fallback survives for the existing harnesses.
    """
    trigger = _load_trigger()
    malformed_cases = [
        None,  # NULL invocation_surfaces
        {},  # no headless entry
        {"headless": {}},  # headless without argv
        {"headless": {"argv": []}},  # empty argv
        {"headless": {"argv": "codex exec"}},  # argv is not a list
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-3344 FR8: _resolve_dispatch_target reads harness-state/harness-registry.json
    and attaches the selected harness record's invocation_surfaces onto the
    returned DispatchTarget — exercising the resolve-then-attach projection
    wiring, not _harness_command in isolation.
    """
    root = _make_synthetic_project(tmp_path)
    trigger = _load_trigger()
    # FAB-01: neutralize argv-head normalization (HYG-001) so the end-to-end
    # assertion checks the resolve-then-attach template, host-PATH-independent.
    monkeypatch.setattr(trigger, "_normalize_argv_head", lambda head, project_root: head)

    target = trigger._resolve_dispatch_target("loyal-opposition", root)
    assert target.harness_id == "A"
    assert target.invocation_surfaces == _CODEX_INVOCATION_SURFACES

    # End-to-end: the resolved target's surfaces drive _harness_command.
    cmd = trigger._harness_command(target, "the-prompt", root)
    assert cmd == ["codex", "exec", "the-prompt", "--cd", str(root)]


# ──────────────────────────────────────────────────────────────────────────
# Slice 2: status-aware dispatch resolver + single-harness topology gate.
# WI-4578 role/dispatchability orthogonality plus legacy status-gate coverage.
# bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver (GO at -002).
# ──────────────────────────────────────────────────────────────────────────

_NO_STATUS = object()
_NO_EVENT_CAPABILITY = object()


def _write_registry(root: Path, records: list[dict]) -> None:
    """Write a harness-state/harness-registry.json projection from records.

    Both _read_role_assignments and _read_harness_identities resolve from this
    projection (WI-3342 IP-4), so a single registry file fully drives
    _resolve_dispatch_target and _is_single_harness_topology.
    """
    harness_state = root / "harness-state"
    harness_state.mkdir(parents=True, exist_ok=True)
    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "MemBase harnesses table (groundtruth.db)",
                "harnesses": records,
            }
        ),
        encoding="utf-8",
    )


def _rec(
    harness_id: str,
    harness_name: str,
    role: list[str],
    status=_NO_STATUS,
    surfaces=None,
    event_driven_hooks=True,
    can_receive_dispatch=None,
    can_fire_events=None,
    reviewer_precedence=None,
) -> dict:
    """Build one registry record. status=_NO_STATUS omits the status key
    (assertion 5: absent status). Pass status=None / "" / "bogus" for the other
    inactive cases."""
    record: dict = {
        "id": harness_id,
        "harness_name": harness_name,
        "harness_type": harness_name,
        "role": role,
        "invocation_surfaces": surfaces or {"headless": {"argv": [harness_name, "-p", "{{PROMPT}}"]}},
    }
    if status is not _NO_STATUS:
        record["status"] = status
    if event_driven_hooks is not _NO_EVENT_CAPABILITY:
        record["event_driven_hooks"] = event_driven_hooks
    if can_receive_dispatch is not None:
        record["can_receive_dispatch"] = can_receive_dispatch
    if can_fire_events is not None:
        record["can_fire_events"] = can_fire_events
    if reviewer_precedence is not None:
        record["reviewer_precedence"] = reviewer_precedence
    return record


def _failure_records(state_dir: Path) -> list[dict]:
    path = state_dir / "dispatch-failures.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _suppression_records(state_dir: Path) -> list[dict]:
    # WI-4396: expected lease/contention suppressions are routed to the sibling
    # dispatch-suppressions.jsonl audit log, NOT dispatch-failures.jsonl.
    path = state_dir / "dispatch-suppressions.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_ollama_loyal_opposition_dispatch_caps_selected_batch_to_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ollama Loyal Opposition dispatch uses a one-item cap without changing the global default."""
    root = _make_synthetic_project(tmp_path)
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {
                    "headless": {
                        "argv": ["ollama-harness", "-p", "{{PROMPT}}"],
                        "max_items": 1,
                    }
                },
                event_driven_hooks=True,
            ),
            _rec("B", "claude", ["prime-builder"], "inactive", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_new_threads(root, ["newest-thread", "middle-thread", "oldest-thread"]))
    state_dir = tmp_path / "state"
    trigger = _load_trigger()
    monkeypatch.setattr(trigger, "_evaluate_ollama_dispatch_readiness", lambda project_root: {"ready": True})

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    assert trigger.DEFAULT_MAX_ITEMS == 2
    assert summary["results"]["loyal-opposition"]["reason"] == "dry_run"
    state = json.loads((state_dir / "dispatch-state.json").read_text(encoding="utf-8"))
    rec = state["recipients"]["loyal-opposition"]
    assert rec["pending_count"] == 3
    assert rec["selected_count"] == 1


def test_lo_provider_failure_backoff_falls_back_after_max_turn_marker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4556: a same-signature Ollama max-turn failure backs off D and selects F."""
    from datetime import datetime, timedelta

    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["ollama-harness", "{{PROMPT}}"], "max_items": 1}},
                reviewer_precedence=10,
            ),
            _rec(
                "F",
                "openrouter",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["openrouter-harness", "{{PROMPT}}"]}},
                reviewer_precedence=20,
            ),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()
    monkeypatch.setattr(trigger, "_evaluate_harness_dispatch_readiness", lambda _kind, _root: {"ready": True})

    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["loyal-opposition"]["selected_candidate"]["harness_id"] == "D"

    runs_dir = state_dir / "dispatch-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    stderr_path = runs_dir / "prior-ollama.stderr.log"
    stderr_path.write_text("ollama_harness: max-turn exhaustion before final assistant text\n", encoding="utf-8")
    stdout_path = runs_dir / "prior-ollama.stdout.log"
    stdout_path.write_text("", encoding="utf-8")

    state_path = state_dir / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    d_state = state["recipients"]["loyal-opposition:D"]
    signature = d_state["last_dispatched_signature"]
    launch = {
        "dispatch_id": "prior-ollama",
        "recipient": "loyal-opposition:D",
        "launched": True,
        "launched_at": (datetime.now(UTC) - timedelta(seconds=5)).isoformat(),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "signature": signature,
        "needed_role_label": "loyal-opposition",
        "selected_documents": ["example-thread"],
        "primary_bridge_id": "example-thread",
        "exit_code": 1,
        "exit_code_processed": True,
    }
    for key in ("loyal-opposition:D", "loyal-opposition"):
        state["recipients"][key]["failure_count"] = 1
        state["recipients"][key]["last_result"] = "launched"
        state["recipients"][key]["last_launch"] = dict(launch)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    fallback = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    result = fallback["results"]["loyal-opposition"]
    assert result["reason"] == "dry_run"
    assert result["selected_candidate"]["harness_id"] == "F"
    assert result["fallback_skipped_candidates"] == [
        {
            "recipient": "loyal-opposition:D",
            "needed_role_label": "loyal-opposition",
            "harness_id": "D",
            "command_handle": "ollama",
            "reviewer_precedence": 10,
            "reason": "provider_failure_backoff_active",
            "failure_class": "max_turn_exhaustion",
        }
    ]
    assert fallback["dispatch_state"]["recipients"]["loyal-opposition:D"]["last_result"] == (
        "provider_failure_backoff_active"
    )
    failures = _failure_records(state_dir)
    assert any(
        record.get("reason") == "previous_launch_failed"
        and record.get("matched_markers", [{}])[0].get("label") == "max_turn_exhaustion"
        for record in failures
    )


def test_lo_exit_zero_without_verdict_backs_off_and_falls_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4556: exit-0 worker completion without a bridge verdict is a failure."""
    from datetime import datetime, timedelta

    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["ollama-harness", "{{PROMPT}}"], "max_items": 1}},
                reviewer_precedence=10,
            ),
            _rec(
                "F",
                "openrouter",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["openrouter-harness", "{{PROMPT}}"]}},
                reviewer_precedence=20,
            ),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()
    monkeypatch.setattr(trigger, "_evaluate_harness_dispatch_readiness", lambda _kind, _root: {"ready": True})

    first = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["loyal-opposition"]["selected_candidate"]["harness_id"] == "D"

    runs_dir = state_dir / "dispatch-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    dispatch_id = "prior-no-verdict"
    (runs_dir / f"{dispatch_id}.exit_code").write_text("0", encoding="utf-8")
    stdout_path = runs_dir / f"{dispatch_id}.stdout.log"
    stderr_path = runs_dir / f"{dispatch_id}.stderr.log"
    stdout_path.write_text("final prose without bridge verdict\n", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")

    state_path = state_dir / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    d_state = state["recipients"]["loyal-opposition:D"]
    signature = d_state["last_dispatched_signature"]
    launch = {
        "dispatch_id": dispatch_id,
        "recipient": "loyal-opposition:D",
        "launched": True,
        "pid": 12345,
        "launched_at": (datetime.now(UTC) + timedelta(seconds=5)).isoformat(),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "signature": signature,
        "needed_role_label": "loyal-opposition",
        "selected_documents": ["example-thread"],
        "primary_bridge_id": "example-thread",
    }
    for key in ("loyal-opposition:D", "loyal-opposition"):
        state["recipients"][key]["last_result"] = "launched"
        state["recipients"][key]["last_launch"] = dict(launch)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    fallback = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    result = fallback["results"]["loyal-opposition"]
    assert result["reason"] == "dry_run"
    assert result["selected_candidate"]["harness_id"] == "F"
    assert result["fallback_skipped_candidates"] == [
        {
            "recipient": "loyal-opposition:D",
            "needed_role_label": "loyal-opposition",
            "harness_id": "D",
            "command_handle": "ollama",
            "reviewer_precedence": 10,
            "reason": "provider_failure_backoff_active",
            "failure_class": "no_verdict_produced",
        }
    ]
    failures = _failure_records(state_dir)
    assert any(record.get("reason") == "no_verdict_produced" for record in failures)


def test_lo_ordered_fallback_prefers_lowest_precedence_ready_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4484: preferred ready LO candidate wins and later candidates are not dispatched."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["ollama-harness", "{{PROMPT}}"]}},
                reviewer_precedence=10,
            ),
            _rec("A", "codex", ["loyal-opposition"], "active", _CODEX_INVOCATION_SURFACES, reviewer_precedence=20),
            _rec(
                "F",
                "openrouter",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["openrouter-harness", "{{PROMPT}}"]}},
                reviewer_precedence=30,
            ),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()
    monkeypatch.setattr(trigger, "_evaluate_harness_dispatch_readiness", lambda _kind, _root: {"ready": True})

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    result = summary["results"]["loyal-opposition"]
    assert result["reason"] == "dry_run"
    assert result["selected_candidate"]["harness_id"] == "D"
    assert result["selected_candidate"]["reviewer_precedence"] == 10
    assert "loyal-opposition:A" not in summary["results"]
    assert "loyal-opposition:F" not in summary["results"]


def test_lo_ordered_fallback_skips_not_ready_preferred_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4484: preferred not-ready LO candidate records skip evidence and falls through."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["ollama-harness", "{{PROMPT}}"]}},
                reviewer_precedence=10,
            ),
            _rec("A", "codex", ["loyal-opposition"], "active", _CODEX_INVOCATION_SURFACES, reviewer_precedence=20),
            _rec(
                "F",
                "openrouter",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["openrouter-harness", "{{PROMPT}}"]}},
                reviewer_precedence=30,
            ),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()

    def _readiness(kind: str, _project_root: Path) -> dict[str, object]:
        return {"ready": kind != "ollama"}

    monkeypatch.setattr(trigger, "_evaluate_harness_dispatch_readiness", _readiness)

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    result = summary["results"]["loyal-opposition"]
    assert result["reason"] == "dry_run"
    assert result["selected_candidate"]["harness_id"] == "A"
    assert result["fallback_skipped_candidates"] == [
        {
            "recipient": "loyal-opposition:D",
            "needed_role_label": "loyal-opposition",
            "harness_id": "D",
            "command_handle": "ollama",
            "reviewer_precedence": 10,
            "reason": "ollama_dispatch_not_ready",
        }
    ]
    state = summary["dispatch_state"]["recipients"]
    assert state["loyal-opposition"]["selected_candidate"]["harness_id"] == "A"
    assert state["loyal-opposition:D"]["last_result"] == "ollama_dispatch_not_ready"
    assert "loyal-opposition:F" not in summary["results"]


def test_lo_ordered_fallback_allows_same_harness_author_different_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Same-harness authorship is not self-review when session context differs."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["ollama-harness", "{{PROMPT}}"]}},
                reviewer_precedence=10,
            ),
            _rec("A", "codex", ["loyal-opposition"], "active", _CODEX_INVOCATION_SURFACES, reviewer_precedence=20),
            _rec(
                "F",
                "openrouter",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["openrouter-harness", "{{PROMPT}}"]}},
                reviewer_precedence=30,
            ),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_one_new(root))
    _write_bridge_file(
        root,
        "example-thread-001.md",
        "NEW\n\nauthor_harness_id: A\nauthor_session_context_id: author-session\n",
    )
    trigger = _load_trigger()

    def _readiness(kind: str, _project_root: Path) -> dict[str, object]:
        return {"ready": kind != "ollama"}

    monkeypatch.setattr(trigger, "_evaluate_harness_dispatch_readiness", _readiness)

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    result = summary["results"]["loyal-opposition"]
    assert result["reason"] == "dry_run"
    assert result["selected_candidate"]["harness_id"] == "A"
    assert result["fallback_skipped_candidates"] == [
        {
            "recipient": "loyal-opposition:D",
            "needed_role_label": "loyal-opposition",
            "harness_id": "D",
            "command_handle": "ollama",
            "reviewer_precedence": 10,
            "reason": "ollama_dispatch_not_ready",
        },
    ]
    state = summary["dispatch_state"]["recipients"]
    assert state["loyal-opposition"]["selected_candidate"]["harness_id"] == "A"
    assert state["loyal-opposition:D"]["last_result"] == "ollama_dispatch_not_ready"


def test_lo_ordered_fallback_all_candidates_unavailable_records_no_ready(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4484: exhausted LO candidate set produces a deterministic no-ready result."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "D",
                "ollama",
                ["loyal-opposition"],
                "active",
                {"headless": {"argv": ["ollama-harness", "{{PROMPT}}"]}},
                reviewer_precedence=10,
            ),
            _rec("A", "codex", ["loyal-opposition"], "active", _CODEX_INVOCATION_SURFACES, reviewer_precedence=20),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    _write_index(root, _index_with_one_new(root))
    trigger = _load_trigger()
    monkeypatch.setattr(trigger, "_evaluate_harness_dispatch_readiness", lambda _kind, _root: {"ready": False})

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    result = summary["results"]["loyal-opposition"]
    assert result["reason"] == "no_ready_target_for_role"
    assert [candidate["harness_id"] for candidate in result["fallback_skipped_candidates"]] == ["D", "A"]
    assert [candidate["reason"] for candidate in result["fallback_skipped_candidates"]] == [
        "ollama_dispatch_not_ready",
        "codex_dispatch_not_ready",
    ]
    state = summary["dispatch_state"]["recipients"]
    assert state["loyal-opposition"]["last_result"] == "no_ready_target_for_role"
    assert state["loyal-opposition:D"]["last_result"] == "ollama_dispatch_not_ready"
    assert state["loyal-opposition:A"]["last_result"] == "codex_dispatch_not_ready"


def test_prime_builder_multi_active_selects_dispatchable_candidate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-4578: multiple active PBs are valid; dispatchability selects the target."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_registry(
        root,
        [
            _rec(
                "B",
                "claude",
                ["prime-builder"],
                "active",
                _CLAUDE_INVOCATION_SURFACES,
                can_receive_dispatch=False,
                can_fire_events=True,
            ),
            _rec(
                "A",
                "codex",
                ["prime-builder", "loyal-opposition"],
                "active",
                _CODEX_INVOCATION_SURFACES,
                can_receive_dispatch=True,
                can_fire_events=True,
            ),
        ],
    )
    _write_index(root, _index_with_one_go(root))
    trigger = _load_trigger()
    monkeypatch.setattr(trigger, "_evaluate_harness_dispatch_readiness", lambda _kind, _root: {"ready": True})

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    result = summary["results"]["prime-builder"]
    assert result["reason"] == "dry_run"
    assert result["selected_candidate"]["harness_id"] == "A"
    assert _failure_records(state_dir) == []


def test_resolve_exactly_one_active_dispatches(tmp_path: Path) -> None:
    """Assertion 4: exactly one ACTIVE match -> DispatchTarget for that harness."""
    trigger = _load_trigger()
    _write_registry(
        tmp_path,
        [
            _rec("A", "codex", ["loyal-opposition"], "active", _CODEX_INVOCATION_SURFACES),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    pb = trigger._resolve_dispatch_target("prime-builder", tmp_path, tmp_path / "state")
    assert pb is not None
    assert pb.harness_id == "B"
    assert pb.command_handle == "claude"
    assert pb.canonical_mode == "pb"
    assert pb.invocation_surfaces == _CLAUDE_INVOCATION_SURFACES
    lo = trigger._resolve_dispatch_target("loyal-opposition", tmp_path, tmp_path / "state")
    assert lo is not None and lo.harness_id == "A" and lo.canonical_mode == "lo"


def test_resolve_filters_by_active_status(tmp_path: Path) -> None:
    """Assertion 1: an inactive same-role harness is never selected."""
    trigger = _load_trigger()
    _write_registry(
        tmp_path,
        [
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
            _rec("C", "antigravity", ["prime-builder"], "inactive"),
        ],
    )
    pb = trigger._resolve_dispatch_target("prime-builder", tmp_path, tmp_path / "state")
    assert pb is not None and pb.harness_id == "B", "inactive C must not be selected"


def test_resolve_filters_by_dispatchability(tmp_path: Path) -> None:
    """WI-4578: an active same-role harness that cannot receive dispatch is never selected."""
    trigger = _load_trigger()
    _write_registry(
        tmp_path,
        [
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
            _rec("C", "antigravity", ["prime-builder"], "active", can_receive_dispatch=False),
        ],
    )
    pb = trigger._resolve_dispatch_target("prime-builder", tmp_path, tmp_path / "state")
    assert pb is not None and pb.harness_id == "B", "non-dispatchable C must not be selected"


def test_resolve_missing_dispatchability_treated_as_not_capable(tmp_path: Path) -> None:
    """WI-4213 compatibility: missing dispatchability alias is fail-closed."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    _write_registry(
        tmp_path,
        [_rec("C", "antigravity", ["prime-builder"], "active", event_driven_hooks=_NO_EVENT_CAPABILITY)],
    )
    assert trigger._resolve_dispatch_target("prime-builder", tmp_path, state_dir) is None
    records = _failure_records(state_dir)
    assert records[0]["reason"] == "no_active_target_for_role"
    assert "none active and receive-dispatch-capable" in records[0]["error_message"]


def test_resolve_zero_active_returns_sentinel_and_audits(tmp_path: Path) -> None:
    """Assertion 2: zero ACTIVE -> None sentinel + one no_active_target_for_role audit."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    _write_registry(tmp_path, [_rec("B", "claude", ["prime-builder"], "inactive")])
    target = trigger._resolve_dispatch_target("prime-builder", tmp_path, state_dir)
    assert target is None
    records = _failure_records(state_dir)
    assert len(records) == 1
    rec = records[0]
    assert rec["reason"] == "no_active_target_for_role"
    assert rec["recipient"] == "prime-builder"
    assert rec["launched"] is False
    assert "prime-builder" in rec["error_message"]


def test_resolve_zero_active_no_statedir_still_sentinels(tmp_path: Path) -> None:
    """Assertion 2 (no state_dir): zero ACTIVE still returns the sentinel; the
    audit emission is simply skipped when no state dir is provided (preserves
    the 2-arg call form used by other tests)."""
    trigger = _load_trigger()
    _write_registry(tmp_path, [_rec("B", "claude", ["prime-builder"], "inactive")])
    assert trigger._resolve_dispatch_target("prime-builder", tmp_path) is None


def test_resolve_multi_active_returns_top_ranked_target(tmp_path: Path) -> None:
    """WI-4578: 2+ ACTIVE role holders are valid; resolver returns the top-ranked target."""
    trigger = _load_trigger()
    _write_registry(
        tmp_path,
        [
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES, reviewer_precedence=20),
            _rec("C", "antigravity", ["prime-builder"], "active", reviewer_precedence=10),
        ],
    )
    target = trigger._resolve_dispatch_target("prime-builder", tmp_path, tmp_path / "state")

    assert target is not None
    assert target.harness_id == "C"


def test_resolve_missing_status_treated_as_inactive(tmp_path: Path) -> None:
    """Assertion 5: a record with no status key is inactive (fail-closed)."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    _write_registry(tmp_path, [_rec("B", "claude", ["prime-builder"])])  # status omitted
    assert trigger._resolve_dispatch_target("prime-builder", tmp_path, state_dir) is None
    assert _failure_records(state_dir)[0]["reason"] == "no_active_target_for_role"


def test_resolve_empty_and_null_status_treated_as_inactive(tmp_path: Path) -> None:
    """Assertion 5: empty-string and null status are inactive (fail-closed)."""
    trigger = _load_trigger()
    for bad_status in ("", None):
        _write_registry(tmp_path, [_rec("B", "claude", ["prime-builder"], bad_status)])
        assert trigger._resolve_dispatch_target("prime-builder", tmp_path, tmp_path / "state") is None


def test_resolve_unknown_status_treated_as_inactive(tmp_path: Path) -> None:
    """Assertion 6 (resolver half): an unrecognized status is inactive.

    The doctor FAIL on unknown status is Slice 6; here the resolver's only job
    is to refuse to dispatch to it.
    """
    trigger = _load_trigger()
    _write_registry(tmp_path, [_rec("B", "claude", ["prime-builder"], "bogus")])
    assert trigger._resolve_dispatch_target("prime-builder", tmp_path, tmp_path / "state") is None


def test_is_single_harness_topology_requires_active(tmp_path: Path) -> None:
    """Assertion 7: single-harness topology requires the harness status==active."""
    trigger = _load_trigger()
    _write_registry(tmp_path, [_rec("B", "claude", ["prime-builder", "loyal-opposition"], "active")])
    assert trigger._is_single_harness_topology(tmp_path) is True
    _write_registry(tmp_path, [_rec("B", "claude", ["prime-builder", "loyal-opposition"], "inactive")])
    assert trigger._is_single_harness_topology(tmp_path) is False
    _write_registry(tmp_path, [_rec("B", "claude", ["prime-builder", "loyal-opposition"])])  # no status
    assert trigger._is_single_harness_topology(tmp_path) is False
    _write_registry(
        tmp_path,
        [_rec("C", "antigravity", ["prime-builder", "loyal-opposition"], "active", event_driven_hooks=False)],
    )
    assert trigger._is_single_harness_topology(tmp_path) is False


def test_resolve_acting_prime_builder_matches_prime(tmp_path: Path) -> None:
    """Assertion 11: legacy acting-prime-builder token matches prime-builder."""
    trigger = _load_trigger()
    _write_registry(
        tmp_path,
        [
            _rec("A", "codex", ["loyal-opposition"], "active", _CODEX_INVOCATION_SURFACES),
            _rec("B", "claude", ["acting-prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    pb = trigger._resolve_dispatch_target("prime-builder", tmp_path, tmp_path / "state")
    assert pb is not None and pb.harness_id == "B" and pb.canonical_mode == "pb"


def test_resolve_ignores_session_stated_role_marker(tmp_path: Path) -> None:
    """Assertion 10: the resolver does NOT consult the ephemeral session-stated
    role marker; headless dispatch keys off durable role + status only."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    _write_registry(
        tmp_path,
        [
            _rec("A", "codex", ["loyal-opposition"], "active", _CODEX_INVOCATION_SURFACES),
            _rec("B", "claude", ["prime-builder"], "active", _CLAUDE_INVOCATION_SURFACES),
        ],
    )
    # A marker that, if (wrongly) consulted, would flip claude to loyal-opposition.
    session_dir = tmp_path / ".claude" / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "active-session-role.json").write_text(
        json.dumps({"session_stated_role": "loyal-opposition", "harness_name": "claude"}),
        encoding="utf-8",
    )
    pb = trigger._resolve_dispatch_target("prime-builder", tmp_path, state_dir)
    lo = trigger._resolve_dispatch_target("loyal-opposition", tmp_path, state_dir)
    assert pb is not None and pb.harness_id == "B", "durable PB resolution must ignore the marker"
    assert lo is not None and lo.harness_id == "A", "durable LO resolution must ignore the marker"


# WI-4658 — _acquire_prime_work_intent_batch quarantine-and-continue tests.
# bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md (GO at -002).
#
# Cover the behavior change: when acquire_work_intent raises
# MalformedBridgeStatusError (permanent per-file parse error), the batch
# quarantines that slug and continues with the remaining selected slugs
# instead of head-of-line-blocking the entire dispatch lane.


def _quarantine_item(slug: str) -> SimpleNamespace:
    return SimpleNamespace(
        document_name=slug,
        top_status="GO",
        top_file=f"bridge/{slug}-002.md",
    )


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def test_wi4658_batch_quarantines_malformed_and_acquires_remaining(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A batch containing one malformed slug quarantines that slug, records a
    structured finding, and still acquires the remaining valid slugs."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    def fake_acquire(slug, _session_id, *, ttl_seconds, project_root):
        if slug == "bad-slug":
            raise trigger.MalformedBridgeStatusError(
                "Bridge file has unrecognized status line: bridge/bad-slug-002.md: 'GO test'",
                path=tmp_path / "bridge" / "bad-slug-002.md",
                offending_line="GO test",
            )
        return True

    acquired_released: list[str] = []

    def fake_release(slugs, *, project_root, session_id):
        acquired_released.extend(slugs)

    monkeypatch.setattr(trigger, "acquire_work_intent", fake_acquire)
    monkeypatch.setattr(trigger, "_release_prime_work_intents", fake_release)

    selected = [_quarantine_item("good-1"), _quarantine_item("bad-slug"), _quarantine_item("good-2")]
    result = trigger._acquire_prime_work_intent_batch(
        selected,
        project_root=tmp_path,
        state_dir=state_dir,
        recipient="prime-builder:A",
        dispatch_id="dispatch-xyz",
        session_id="session-xyz",
    )

    assert result["ok"] is True
    assert result["reason"] is None
    assert result["acquired_slugs"] == ["good-1", "good-2"]
    assert len(result["quarantined_slugs"]) == 1
    q = result["quarantined_slugs"][0]
    assert q["slug"] == "bad-slug"
    assert q["offending_line"] == "GO test"
    assert "bad-slug-002.md" in q["path"]
    # No release of acquired slugs on quarantine (continue, not fail).
    assert acquired_released == []

    failures = _read_jsonl(state_dir / trigger.DISPATCH_FAILURES_FILENAME)
    quarantine_records = [f for f in failures if f.get("reason") == "bridge_file_malformed_status_quarantined"]
    assert len(quarantine_records) == 1
    rec = quarantine_records[0]
    assert rec["document_name"] == "bad-slug"
    assert rec["error_type"] == "MalformedBridgeStatusError"
    assert rec["offending_line"] == "GO test"


def test_wi4658_batch_returns_all_slugs_quarantined_when_only_malformed_remain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When every selected slug is malformed, the batch returns ok: False with
    reason ``all_slugs_quarantined`` so the caller does not spawn an empty
    dispatch."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    def fake_acquire(slug, _session_id, *, ttl_seconds, project_root):
        raise trigger.MalformedBridgeStatusError(
            f"Bridge file has unrecognized status line: bridge/{slug}-002.md: 'GO test'",
            path=tmp_path / "bridge" / f"{slug}-002.md",
            offending_line="GO test",
        )

    monkeypatch.setattr(trigger, "acquire_work_intent", fake_acquire)
    monkeypatch.setattr(trigger, "_release_prime_work_intents", lambda *args, **kwargs: None)

    selected = [_quarantine_item("bad-1"), _quarantine_item("bad-2")]
    result = trigger._acquire_prime_work_intent_batch(
        selected,
        project_root=tmp_path,
        state_dir=state_dir,
        recipient="prime-builder:A",
        dispatch_id="dispatch-xyz",
        session_id="session-xyz",
    )

    assert result["ok"] is False
    assert result["reason"] == "all_slugs_quarantined"
    assert result["acquired_slugs"] == []
    assert {q["slug"] for q in result["quarantined_slugs"]} == {"bad-1", "bad-2"}


def test_wi4658_batch_preserves_all_or_nothing_for_transient_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Non-malformed WorkIntentRegistryError (DB error, contention) retains
    prior all-or-nothing semantics: the batch fails fast and previously-acquired
    slugs are released."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    def fake_acquire(slug, _session_id, *, ttl_seconds, project_root):
        if slug == "transient":
            raise trigger.WorkIntentRegistryError("Database error during acquire: locked")
        return True

    released: list[str] = []
    monkeypatch.setattr(trigger, "acquire_work_intent", fake_acquire)
    monkeypatch.setattr(
        trigger,
        "_release_prime_work_intents",
        lambda slugs, *, project_root, session_id: released.extend(slugs),
    )

    selected = [_quarantine_item("good-1"), _quarantine_item("transient"), _quarantine_item("good-2")]
    result = trigger._acquire_prime_work_intent_batch(
        selected,
        project_root=tmp_path,
        state_dir=state_dir,
        recipient="prime-builder:A",
        dispatch_id="dispatch-xyz",
        session_id="session-xyz",
    )

    assert result["ok"] is False
    assert result["reason"] == "work_intent_acquire_failed"
    assert result["failed_slug"] == "transient"
    assert result["acquired_slugs"] == ["good-1"]
    # All-or-nothing: previously-acquired slugs were released.
    assert released == ["good-1"]

    failures = _read_jsonl(state_dir / trigger.DISPATCH_FAILURES_FILENAME)
    quarantine_records = [f for f in failures if f.get("reason") == "bridge_file_malformed_status_quarantined"]
    acquire_failure_records = [f for f in failures if f.get("reason") == "work_intent_acquire_failed"]
    assert quarantine_records == []
    assert len(acquire_failure_records) == 1


def test_wi4658_batch_quarantine_then_transient_releases_acquired_skips_quarantined(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A quarantined slug followed by a transient failure: the transient
    failure still releases acquired slugs but the quarantined slug is recorded
    in the return value for caller persistence."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    def fake_acquire(slug, _session_id, *, ttl_seconds, project_root):
        if slug == "malformed":
            raise trigger.MalformedBridgeStatusError(
                "Bridge file is empty: bridge/malformed-002.md",
                path=tmp_path / "bridge" / "malformed-002.md",
                offending_line=None,
            )
        if slug == "transient":
            raise trigger.WorkIntentRegistryError("Database error during acquire: locked")
        return True

    monkeypatch.setattr(trigger, "acquire_work_intent", fake_acquire)
    monkeypatch.setattr(trigger, "_release_prime_work_intents", lambda *args, **kwargs: None)

    selected = [_quarantine_item("good-1"), _quarantine_item("malformed"), _quarantine_item("transient")]
    result = trigger._acquire_prime_work_intent_batch(
        selected,
        project_root=tmp_path,
        state_dir=state_dir,
        recipient="prime-builder:A",
        dispatch_id="dispatch-xyz",
        session_id="session-xyz",
    )

    assert result["ok"] is False
    assert result["reason"] == "work_intent_acquire_failed"
    assert result["failed_slug"] == "transient"
    assert result["acquired_slugs"] == ["good-1"]
    # Quarantined slug is preserved in the result for caller-side persistence.
    assert len(result["quarantined_slugs"]) == 1
    assert result["quarantined_slugs"][0]["slug"] == "malformed"
