# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the dispatcher black-box config/state PreToolUse gate (WI-4788 slice 1).

Spec linkage: ADR-DISPATCHER-ARCHITECTURE-001 (isolation invariants 1-3 -- dispatcher config
and runtime state are GT-KB-owned; harnesses must not directly mutate them) +
GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (mutations flow through the governed CLI so the projection
stays write-through-consistent -- the WI-4820 false-green-drift class) +
DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (harness-registry.json is a generated projection).
"""

from __future__ import annotations

import io
import json

import pytest

from scripts import dispatch_blackbox_gate as gate

PROTECTED_WRITES = [
    ("config/dispatcher/rules.toml", "dispatcher_config"),
    ("harness-state/harness-registry.json", "harness_registry"),
    (".gtkb-state/bridge-poller/dispatch-state.json", "dispatcher_runtime_state"),
    (".gtkb-state/bridge-poller/dispatch-runs/2026-06-26-x.exit_code", "dispatcher_runtime_state"),
    (".gtkb-state/cross-harness-trigger/signature.json", "dispatcher_runtime_state"),
    (".gtkb-state/dispatcher-daemon/heartbeat.json", "dispatcher_runtime_state"),
]


@pytest.mark.parametrize(("rel_path", "expected_class"), PROTECTED_WRITES)
def test_classify_protected_path(rel_path: str, expected_class: str) -> None:
    """DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 / ADR invariants: each protected surface
    classifies to its dispatcher class."""
    assert gate.classify_protected_path(rel_path) == expected_class


@pytest.mark.parametrize(("rel_path", "expected_class"), PROTECTED_WRITES)
def test_gate_blocks_dispatcher_config_and_state_writes(rel_path: str, expected_class: str) -> None:
    """ADR-DISPATCHER-ARCHITECTURE-001 invariants 1-3: a direct Write to a protected dispatcher
    config/state surface is blocked with a reason that names the governed CLI."""
    decision = gate.gate_decision("Write", rel_path)
    assert decision.block is True
    assert decision.protected_class == expected_class
    assert decision.reason is not None
    assert "WI-4788" in decision.reason
    assert "gt " in decision.reason  # redirected to a governed gt CLI


def test_edit_and_notebookedit_also_blocked() -> None:
    """All mutating tools (Write/Edit/NotebookEdit) are gated, not just Write."""
    for tool in ("Edit", "NotebookEdit"):
        assert gate.gate_decision(tool, "config/dispatcher/rules.toml").block is True


def test_gate_allows_non_protected_and_non_write_tools() -> None:
    """ADR (CLI bypass asymmetry): non-protected paths and non-mutating tools pass."""
    # Non-protected path passes for a mutating tool.
    assert gate.gate_decision("Write", "scripts/foo.py").block is False
    assert gate.classify_protected_path("scripts/foo.py") is None
    # Non-mutating tools pass even on a protected path.
    for tool in ("Read", "Grep", "Glob", "Bash"):
        assert gate.gate_decision(tool, "config/dispatcher/rules.toml").block is False
    # A .gtkb-state path outside the protected dispatcher dirs passes.
    assert gate.gate_decision("Write", ".gtkb-state/work-intent/some-slug.json").block is False
    assert gate.classify_protected_path(".gtkb-state/work-intent/some-slug.json") is None


def test_owner_bypass_allows_with_audit() -> None:
    """GOV-SOURCE-OF-TRUTH-FRESHNESS-001: the owner bypass is explicit and audited; without it
    the same protected write blocks."""
    blocked = gate.gate_decision("Write", "config/dispatcher/rules.toml")
    assert blocked.block is True
    assert blocked.bypass_audited is False

    bypassed = gate.gate_decision("Write", "config/dispatcher/rules.toml", bypass=True)
    assert bypassed.block is False
    assert bypassed.bypass_audited is True
    assert bypassed.protected_class == "dispatcher_config"


def test_main_blocks_protected_write_via_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    """The PreToolUse entry point emits a deny decision and records the denial."""
    denials = tmp_path / "denials.jsonl"
    payload = {"tool_name": "Write", "tool_input": {"file_path": "config/dispatcher/rules.toml"}}
    monkeypatch.setattr(gate.sys, "stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setattr(gate.sys, "argv", ["dispatch_blackbox_gate.py"])
    monkeypatch.setenv("GTKB_GATE_DENIALS_PATH", str(denials))
    monkeypatch.delenv("GTKB_DISPATCH_BLACKBOX_BYPASS", raising=False)

    rc = gate.main()
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "WI-4788" in out["hookSpecificOutput"]["permissionDecisionReason"]
    assert denials.exists()


def test_main_allows_non_protected_via_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A non-protected target passes through as an empty allow object."""
    payload = {"tool_name": "Write", "tool_input": {"file_path": "scripts/foo.py"}}
    monkeypatch.setattr(gate.sys, "stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setattr(gate.sys, "argv", ["dispatch_blackbox_gate.py"])

    rc = gate.main()
    assert rc == 0
    assert capsys.readouterr().out.strip() == "{}"
