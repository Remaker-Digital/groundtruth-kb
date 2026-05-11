# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Active-session suppression tests for scripts/cross_harness_bridge_trigger.py.

Per ``bridge/gtkb-cross-harness-trigger-active-session-suppression-001-005.md``
GO at ``-006`` (REVISED-2):

These tests cover the suppression gate added to the trigger:
- ``check_counterpart_active(recipient, state_dir)``: returns True when the
  counterpart's lock file is present and within sanity TTL.
- ``run_trigger()`` three-way state-machine:
  - counterpart_active → record ``last_suppressed_signature``; do NOT dispatch.
  - prior_dispatched == current → ``unchanged``; do NOT dispatch.
  - else → dispatch; record ``last_dispatched_signature``; clear suppressed.

Tests use ``--dry-run`` to avoid spawning real harness subprocesses.

Filed in a new file rather than weaving into ``test_cross_harness_bridge_trigger.py``
to avoid merge conflicts with concurrent revisions; tracked as a minor
deviation from the GO'd proposal (which expected updates to the existing
file). Test coverage is equivalent.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from unittest import mock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py"


@pytest.fixture(scope="module")
def trigger_module():
    assert _SCRIPT_PATH.is_file(), f"Missing {_SCRIPT_PATH}"
    spec = importlib.util.spec_from_file_location(
        "cross_harness_bridge_trigger_for_suppression_tests", _SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["cross_harness_bridge_trigger_for_suppression_tests"] = module
    spec.loader.exec_module(module)
    return module


def _write_lock(state_dir: Path, role: str, mtime_offset_seconds: float = 0.0) -> Path:
    """Create a heartbeat lock file. Optionally backdate its mtime."""
    state_dir.mkdir(parents=True, exist_ok=True)
    lock = state_dir / f"active-{role}-session.lock"
    lock.write_text(json.dumps({"opened_at": "x", "last_refreshed": "x"}))
    if mtime_offset_seconds:
        atime = time.time() + mtime_offset_seconds
        os.utime(lock, (atime, atime))
    return lock


def _make_minimal_index(tmp_path: Path) -> Path:
    """Create a minimal project root with bridge/INDEX.md + groundtruth.toml.

    The trigger needs both to resolve project_root and produce actionable
    pending entries. We point at the real GT-KB INDEX by symlink-equivalent
    via copying a minimal valid INDEX with one Prime-actionable entry.
    """
    project_root = tmp_path / "project"
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(parents=True)
    (project_root / "groundtruth.toml").write_text("# minimal\n")
    # Minimal bridge/INDEX.md with one Prime-actionable GO entry.
    (bridge_dir / "INDEX.md").write_text(
        "Document: test-suppression-fixture\n"
        "GO: bridge/test-suppression-fixture-002.md\n"
        "NEW: bridge/test-suppression-fixture-001.md\n"
    )
    # Bridge files referenced by INDEX.md must exist for the parser.
    (bridge_dir / "test-suppression-fixture-002.md").write_text("GO\nFixture content.\n")
    (bridge_dir / "test-suppression-fixture-001.md").write_text("NEW\nFixture content.\n")
    return project_root


# ---------------------------------------------------------------------------
# check_counterpart_active() — direct unit tests
# ---------------------------------------------------------------------------


def test_check_counterpart_active_lock_absent_returns_false(trigger_module, tmp_path: Path) -> None:
    """T-SUPPRESS-counterpart-absent-dispatches (predicate level)."""
    assert trigger_module.check_counterpart_active("prime", tmp_path) is False
    assert trigger_module.check_counterpart_active("codex", tmp_path) is False


def test_check_counterpart_active_lock_present_fresh_returns_true(trigger_module, tmp_path: Path) -> None:
    """T-SUPPRESS-counterpart-active-suppresses (predicate level): lock present + fresh mtime."""
    # recipient="prime" looks for active-claude-session.lock (the harness behind Prime).
    _write_lock(tmp_path, "claude")
    assert trigger_module.check_counterpart_active("prime", tmp_path) is True


def test_check_counterpart_active_lock_stale_returns_false(trigger_module, tmp_path: Path) -> None:
    """T-SUPPRESS-counterpart-stale-overrides-via-sanity-ttl: lock older than 120s is treated as orphaned."""
    _write_lock(tmp_path, "claude", mtime_offset_seconds=-500)  # 500s old
    assert trigger_module.check_counterpart_active("prime", tmp_path) is False


def test_check_counterpart_active_sanity_ttl_default_is_120s(trigger_module, tmp_path: Path, monkeypatch) -> None:
    """T-SUPPRESS-sanity-ttl-default-is-120s: env var unset → 120s default."""
    monkeypatch.delenv("GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS", raising=False)
    # Lock 119s old (within 120s default): active.
    _write_lock(tmp_path, "claude", mtime_offset_seconds=-119)
    assert trigger_module.check_counterpart_active("prime", tmp_path) is True


def test_check_counterpart_active_sanity_ttl_env_var_overrides(trigger_module, tmp_path: Path, monkeypatch) -> None:
    """Operators can override the 120s default for tuning."""
    monkeypatch.setenv("GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS", "30")
    _write_lock(tmp_path, "claude", mtime_offset_seconds=-60)  # 60s old, > 30s ttl
    assert trigger_module.check_counterpart_active("prime", tmp_path) is False


def test_check_counterpart_active_recipient_codex_checks_codex_lock(trigger_module, tmp_path: Path) -> None:
    """recipient='codex' looks for active-codex-session.lock, not active-claude-session.lock."""
    _write_lock(tmp_path, "codex")
    assert trigger_module.check_counterpart_active("codex", tmp_path) is True
    # Without a Claude lock, prime check returns False.
    assert trigger_module.check_counterpart_active("prime", tmp_path) is False


def test_check_counterpart_active_unknown_recipient_returns_false(trigger_module, tmp_path: Path) -> None:
    """An unknown recipient name should NOT cause silent suppression of every dispatch."""
    _write_lock(tmp_path, "claude")
    _write_lock(tmp_path, "codex")
    assert trigger_module.check_counterpart_active("unknown", tmp_path) is False


# ---------------------------------------------------------------------------
# run_trigger() — state-machine integration tests
#
# These tests run the trigger in --dry-run mode against a minimal project
# root. We monkeypatch _spawn_harness so we can observe whether dispatch
# was attempted without spawning real subprocesses.
# ---------------------------------------------------------------------------


def _run_trigger_dry(trigger_module, project_root: Path, state_dir: Path) -> dict:
    """Run trigger in dry-run mode; return the result dict."""
    return trigger_module.run_trigger(
        project_root=project_root, state_dir=state_dir, dry_run=True
    )


def test_run_trigger_counterpart_active_records_suppressed_not_dispatched(
    trigger_module, tmp_path: Path
) -> None:
    """T-SUPPRESS-suppressed-signature-stored-not-as-dispatched (F1 fix critical).

    When the counterpart is active, the current signature is recorded in
    last_suppressed_signature; last_dispatched_signature stays at its prior
    value; legacy `signature` field is not updated.
    """
    project_root = _make_minimal_index(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    # Plant a counterpart active-claude-session lock so Prime dispatch
    # is suppressed (recipient=prime, counterpart=claude).
    _write_lock(state_dir, "claude")

    result = _run_trigger_dry(trigger_module, project_root, state_dir)

    prime_state = result["dispatch_state"]["recipients"]["prime"]
    assert prime_state["last_result"] == "counterpart_active_session_present"
    assert prime_state["last_suppressed_signature"] is not None
    # last_dispatched_signature was not set on this fire (None or absent).
    assert prime_state.get("last_dispatched_signature") in (None,), (
        f"expected None, got {prime_state.get('last_dispatched_signature')!r}"
    )
    # Legacy `signature` field should NOT be updated to the suppressed signature.
    assert prime_state.get("signature") in (None,), (
        f"expected None or unchanged, got {prime_state.get('signature')!r}"
    )


def test_run_trigger_retry_after_counterpart_exits(trigger_module, tmp_path: Path) -> None:
    """T-SUPPRESS-retry-after-counterpart-exits (F1 fix critical).

    Step A: counterpart active → suppress; record last_suppressed_signature.
    Step B: counterpart exits (lock removed); same signature; trigger fires
    again → dispatch branch is entered (because last_dispatched_signature
    was never set to the suppressed signature).
    """
    project_root = _make_minimal_index(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    # Step A: counterpart active.
    claude_lock = _write_lock(state_dir, "claude")
    result_a = _run_trigger_dry(trigger_module, project_root, state_dir)
    prime_state_a = result_a["dispatch_state"]["recipients"]["prime"]
    assert prime_state_a["last_result"] == "counterpart_active_session_present"
    suppressed_sig = prime_state_a["last_suppressed_signature"]
    assert suppressed_sig is not None

    # Step B: counterpart exits.
    claude_lock.unlink()
    # Same INDEX content → same signature.
    result_b = _run_trigger_dry(trigger_module, project_root, state_dir)
    prime_state_b = result_b["dispatch_state"]["recipients"]["prime"]
    # Dispatch branch entered. In dry_run, _spawn_harness returns
    # {"launched": False, "reason": "dry_run"}, and last_result becomes
    # "launch_failed" because launched is False. The critical assertion is
    # that we did NOT enter the "unchanged" or "counterpart_active" branches.
    assert prime_state_b["last_result"] not in (
        "unchanged",
        "counterpart_active_session_present",
    ), (
        f"expected dispatch branch entry, got last_result={prime_state_b['last_result']!r}"
    )
    # last_dispatched_signature is set to the current signature post-dispatch attempt.
    assert prime_state_b["last_dispatched_signature"] == suppressed_sig
    # last_suppressed_signature is cleared.
    assert prime_state_b["last_suppressed_signature"] is None


def test_run_trigger_dedup_still_works_after_real_dispatch(trigger_module, tmp_path: Path) -> None:
    """T-SUPPRESS-dedup-still-works-after-real-dispatch (Slice 2 invariant).

    After a dispatch, last_dispatched_signature is set. Same signature next
    fire returns "unchanged".
    """
    project_root = _make_minimal_index(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    # No counterpart lock → dispatch branch.
    result_a = _run_trigger_dry(trigger_module, project_root, state_dir)
    prime_state_a = result_a["dispatch_state"]["recipients"]["prime"]
    dispatched_sig = prime_state_a["last_dispatched_signature"]
    assert dispatched_sig is not None

    # Same INDEX content → same signature → "unchanged".
    result_b = _run_trigger_dry(trigger_module, project_root, state_dir)
    prime_state_b = result_b["dispatch_state"]["recipients"]["prime"]
    assert prime_state_b["last_result"] == "unchanged"
    # last_dispatched_signature unchanged.
    assert prime_state_b["last_dispatched_signature"] == dispatched_sig


def test_run_trigger_suppressed_cleared_after_dispatch(trigger_module, tmp_path: Path) -> None:
    """T-SUPPRESS-suppressed-cleared-after-dispatch (state hygiene).

    When dispatch fires for a previously-suppressed signature, the
    last_suppressed_signature field is cleared (set to None).
    Already covered by test_run_trigger_retry_after_counterpart_exits, but
    asserted explicitly here to pin the contract.
    """
    project_root = _make_minimal_index(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    claude_lock = _write_lock(state_dir, "claude")
    _run_trigger_dry(trigger_module, project_root, state_dir)

    claude_lock.unlink()
    result = _run_trigger_dry(trigger_module, project_root, state_dir)
    prime_state = result["dispatch_state"]["recipients"]["prime"]
    assert prime_state["last_suppressed_signature"] is None


def test_run_trigger_legacy_signature_field_preserved_during_suppression(
    trigger_module, tmp_path: Path
) -> None:
    """Legacy `signature` field is NOT updated on suppression (back-compat).

    Slice 2 readers (e.g., dashboards) key off `signature`; updating it on
    suppression would mislead them into treating the work as dispatched.
    """
    project_root = _make_minimal_index(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    # First dispatch (no counterpart) sets legacy signature.
    _run_trigger_dry(trigger_module, project_root, state_dir)
    state_first = json.loads((state_dir / "dispatch-state.json").read_text())
    legacy_sig_first = state_first["recipients"]["prime"]["signature"]
    assert legacy_sig_first is not None

    # Now plant counterpart lock; subsequent fires should suppress without
    # touching legacy signature. Modify INDEX so the signature would CHANGE
    # if the suppression branch wrote to legacy_sig (proving the test).
    bridge_index = project_root / "bridge" / "INDEX.md"
    bridge_index.write_text(
        bridge_index.read_text()
        + "\nDocument: another-fixture\nGO: bridge/another-fixture-001.md\n"
    )
    (project_root / "bridge" / "another-fixture-001.md").write_text("GO\n")
    _write_lock(state_dir, "claude")

    _run_trigger_dry(trigger_module, project_root, state_dir)
    state_second = json.loads((state_dir / "dispatch-state.json").read_text())
    legacy_sig_second = state_second["recipients"]["prime"]["signature"]
    # Legacy signature should be UNCHANGED because suppression must not touch it.
    assert legacy_sig_second == legacy_sig_first


# ---------------------------------------------------------------------------
# T-SUPPRESS-heartbeat-trigger-shared-lock-dir — config integration test
#
# Parses both .claude/settings.json and .codex/hooks.json, extracts the
# --state-dir argument from every heartbeat command and every trigger
# command, asserts they all resolve to the same path within each harness
# side. Failure here indicates the silent-suppression bug from -001-004 F1.
# ---------------------------------------------------------------------------


def _extract_state_dir_from_command(command: str) -> str | None:
    """Best-effort extraction of `--state-dir <value>` from a hook command line."""
    parts = command.split("--state-dir", 1)
    if len(parts) != 2:
        return None
    tail = parts[1].strip()
    # Drop a leading quote if present.
    if tail.startswith('"'):
        end = tail.find('"', 1)
        if end > 0:
            return tail[1:end]
    # Otherwise take the first whitespace-delimited token.
    token = tail.split()[0] if tail.split() else None
    return token


def _gather_heartbeat_and_trigger_state_dirs(config: dict) -> dict:
    """Return mapping {hook_name: list_of_(script_kind, state_dir)} for inspection."""
    out: dict = {}
    for event_name, groups in config.get("hooks", {}).items():
        out[event_name] = []
        for group in groups:
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                state_dir = _extract_state_dir_from_command(cmd)
                if "active_session_heartbeat.py" in cmd:
                    out[event_name].append(("heartbeat", state_dir))
                elif "cross_harness_bridge_trigger.py" in cmd:
                    out[event_name].append(("trigger", state_dir))
    return out


def test_heartbeat_trigger_shared_lock_dir_claude(tmp_path: Path) -> None:
    """T-SUPPRESS-heartbeat-trigger-shared-lock-dir (Claude side).

    All heartbeat commands and all trigger commands in .claude/settings.json
    must use the SAME --state-dir value within each harness side.
    """
    settings = json.loads((_REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    by_event = _gather_heartbeat_and_trigger_state_dirs(settings)

    all_state_dirs = []
    for event, entries in by_event.items():
        for kind, state_dir in entries:
            assert state_dir is not None, (
                f"Claude {event} hook missing --state-dir: kind={kind}"
            )
            all_state_dirs.append((event, kind, state_dir))

    # Every (heartbeat or trigger) command must resolve to the same state_dir.
    state_dir_values = {state_dir for _, _, state_dir in all_state_dirs}
    assert len(state_dir_values) == 1, (
        f"Claude heartbeat and trigger commands have inconsistent --state-dir: {all_state_dirs!r}"
    )
    # Must contain the expected fragment.
    only_state_dir = next(iter(state_dir_values))
    assert ".gtkb-state/bridge-poller" in only_state_dir or ".gtkb-state\\bridge-poller" in only_state_dir


def test_heartbeat_trigger_shared_lock_dir_codex(tmp_path: Path) -> None:
    """T-SUPPRESS-heartbeat-trigger-shared-lock-dir (Codex side)."""
    hooks = json.loads((_REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    by_event = _gather_heartbeat_and_trigger_state_dirs(hooks)

    all_state_dirs = []
    for event, entries in by_event.items():
        for kind, state_dir in entries:
            assert state_dir is not None, (
                f"Codex {event} hook missing --state-dir: kind={kind}"
            )
            all_state_dirs.append((event, kind, state_dir))

    state_dir_values = {state_dir for _, _, state_dir in all_state_dirs}
    assert len(state_dir_values) == 1, (
        f"Codex heartbeat and trigger commands have inconsistent --state-dir: {all_state_dirs!r}"
    )
    only_state_dir = next(iter(state_dir_values))
    assert ".gtkb-state/bridge-poller" in only_state_dir or ".gtkb-state\\bridge-poller" in only_state_dir
