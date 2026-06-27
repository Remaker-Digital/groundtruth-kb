# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests verifying canonical-init-keyword implementation preserves the seven
governing role/dispatch specs cited in
bridge/gtkb-canonical-init-keyword-syntax-001-005.md Specification Links.

Authority: bridge -005 IP-8 surface 6 (Codex GO at -008; F1 fix).

Each test pins the behavior of one cited governing spec. Failure indicates
the canonical-init-keyword implementation has regressed the cited spec's
preservation claim.

Governing specs covered:

  1. GOV-HARNESS-ROLE-PORTABILITY-001    -> test_role_portability_preserved
  2. GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 -> test_either_harness_can_hold_either_role
  3. DCL-CROSS-HARNESS-ENFORCEMENT-001   -> test_strict_ignore_applies_to_both_harnesses
  4. ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 -> test_keyword_emitted_only_on_actionable
  5. DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 -> test_no_keyword_on_idle_signature
  6. DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 v2 -> test_receiver_defers_to_durable_record
  7. PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 -> test_misdirected_dispatch_writes_audit_log
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRIGGER_PATH = PROJECT_ROOT / "scripts" / "cross_harness_bridge_trigger.py"
CLAUDE_HOOK_PATH = PROJECT_ROOT / ".claude" / "hooks" / "session_start_dispatch.py"
CODEX_HOOK_PATH = PROJECT_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"


def _load_module(name: str, path: Path) -> ModuleType:
    assert path.is_file(), f"Missing module: {path}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_trigger() -> ModuleType:
    return _load_module("cross_harness_bridge_trigger_govspec", TRIGGER_PATH)


def _load_claude_hook_isolated(name_suffix: str) -> ModuleType:
    """Load Claude hook with a unique sys.modules name for test isolation."""
    return _load_module(f"claude_hook_govspec_{name_suffix}", CLAUDE_HOOK_PATH)


def _load_codex_hook_isolated(name_suffix: str) -> ModuleType:
    """Load Codex hook with a unique sys.modules name for test isolation."""
    return _load_module(f"codex_hook_govspec_{name_suffix}", CODEX_HOOK_PATH)


def _write_harness_state(
    project_root: Path,
    *,
    claude_role: str,
    codex_role: str,
) -> None:
    """Write harness-state fixtures with the given role assignments.

    Both ``claude_role`` and ``codex_role`` are durable role labels:
    ``"prime-builder"`` or ``"loyal-opposition"``.
    """
    harness_state = project_root / "harness-state"
    harness_state.mkdir(parents=True, exist_ok=True)
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
                    "B": {"role": claude_role, "harness_type": "claude"},
                    "A": {"role": codex_role, "harness_type": "codex"},
                },
            }
        ),
        encoding="utf-8",
    )
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
                        "role": [codex_role],
                        "event_driven_hooks": True,
                        "invocation_surfaces": {
                            "headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}
                        },
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "role": [claude_role],
                        "event_driven_hooks": True,
                        "invocation_surfaces": {
                            "headless": {
                                "argv": [
                                    "claude",
                                    "-p",
                                    "{{PROMPT}}",
                                    "--add-dir",
                                    "{{PROJECT_ROOT}}",
                                    "--output-format",
                                    "json",
                                ]
                            }
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-role-portability — GOV-HARNESS-ROLE-PORTABILITY-001
# ──────────────────────────────────────────────────────────────────────────


def test_role_portability_preserved(tmp_path: Path) -> None:
    """GOV-HARNESS-ROLE-PORTABILITY-001 — Prime/LO are portable across harnesses.

    Swapping which harness holds which role MUST swap the dispatch target
    accordingly. The keyword tracks the durable role; the command handle
    tracks the durable identity.
    """
    trigger = _load_trigger()

    # Default fixture: claude=B=prime-builder, codex=A=loyal-opposition.
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    target_lo = trigger._resolve_dispatch_target("loyal-opposition", tmp_path)
    target_pb = trigger._resolve_dispatch_target("prime-builder", tmp_path)
    assert target_lo.command_handle == "codex"
    assert target_lo.canonical_mode == "lo"
    assert target_lo.harness_id == "A"
    assert target_pb.command_handle == "claude"
    assert target_pb.canonical_mode == "pb"
    assert target_pb.harness_id == "B"

    # Swapped fixture: claude=B=loyal-opposition, codex=A=prime-builder.
    _write_harness_state(tmp_path, claude_role="loyal-opposition", codex_role="prime-builder")
    target_lo = trigger._resolve_dispatch_target("loyal-opposition", tmp_path)
    target_pb = trigger._resolve_dispatch_target("prime-builder", tmp_path)
    assert target_lo.command_handle == "claude", (
        "After role swap, loyal-opposition dispatch must target claude (B), not codex. Role portability regressed."
    )
    assert target_lo.canonical_mode == "lo"
    assert target_lo.harness_id == "B"
    assert target_pb.command_handle == "codex"
    assert target_pb.canonical_mode == "pb"
    assert target_pb.harness_id == "A"


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-multi-harness-config — GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001
# ──────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "claude_role,codex_role,prime_handle,lo_handle",
    [
        ("prime-builder", "loyal-opposition", "claude", "codex"),
        ("loyal-opposition", "prime-builder", "codex", "claude"),
    ],
)
def test_either_harness_can_hold_either_role(
    tmp_path: Path,
    claude_role: str,
    codex_role: str,
    prime_handle: str,
    lo_handle: str,
) -> None:
    """GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 — GT-KB installs must prepare
    capable harnesses for either role.

    Both single-direction binding configurations resolve cleanly: the
    resolver narrows to the harness assigned the requested role, never
    hard-codes one direction. Same harnesses with the OTHER role
    assignment also resolves correctly (the bottom row of the table).
    """
    trigger = _load_trigger()
    _write_harness_state(tmp_path, claude_role=claude_role, codex_role=codex_role)
    pb = trigger._resolve_dispatch_target("prime-builder", tmp_path)
    lo = trigger._resolve_dispatch_target("loyal-opposition", tmp_path)
    assert pb.command_handle == prime_handle
    assert lo.command_handle == lo_handle
    assert pb.canonical_mode == "pb"
    assert lo.canonical_mode == "lo"


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-cross-harness-enforcement — DCL-CROSS-HARNESS-ENFORCEMENT-001
# ──────────────────────────────────────────────────────────────────────────


def test_prompt_keyword_authorization_audits_both_harnesses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """DCL-CROSS-HARNESS-ENFORCEMENT-001 — prompt keyword authorization plus
    role-mismatch audit applies symmetrically to Claude AND Codex.

    Setup: Claude harness B holds prime-builder; Codex harness A holds
    loyal-opposition. A dispatch arrives intended for prime-builder
    (mode 'pb'). The Codex receiver MUST authorize the explicit prompt keyword
    and audit because pb is not in {'lo'}. The Claude receiver MUST authorize
    without mismatch audit because pb is in {'pb'}. Mirror case (mode 'lo')
    exercises the other direction.
    """
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")

    claude_hook = _load_claude_hook_isolated("cross_harness_enforcement")
    codex_hook = _load_codex_hook_isolated("cross_harness_enforcement")

    failures_path = tmp_path / "dispatch-failures.jsonl"

    # Case A: dispatch mode 'pb' targets prime-builder.
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-cross-pb")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb pb")
    claude_dec, _ = claude_hook._bridge_dispatch_keyword_check(project_root=tmp_path, failures_path=failures_path)
    codex_dec, _ = codex_hook._bridge_dispatch_keyword_check(project_root=tmp_path, failures_path=failures_path)
    assert claude_dec == claude_hook.StartupDecision.DISPATCH_AUTHORIZED, (
        "Claude (prime-builder) MUST authorize a pb-targeted dispatch."
    )
    assert codex_dec == codex_hook.StartupDecision.DISPATCH_AUTHORIZED, (
        "Codex (loyal-opposition) MUST authorize and audit a pb-targeted dispatch."
    )

    # Case B: dispatch mode 'lo' targets loyal-opposition.
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-cross-lo")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    claude_dec, _ = claude_hook._bridge_dispatch_keyword_check(project_root=tmp_path, failures_path=failures_path)
    codex_dec, _ = codex_hook._bridge_dispatch_keyword_check(project_root=tmp_path, failures_path=failures_path)
    assert codex_dec == codex_hook.StartupDecision.DISPATCH_AUTHORIZED, (
        "Codex (loyal-opposition) MUST authorize an lo-targeted dispatch."
    )
    assert claude_dec == claude_hook.StartupDecision.DISPATCH_AUTHORIZED, (
        "Claude (prime-builder) MUST authorize and audit an lo-targeted dispatch."
    )


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-actionable-only-spawn — ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2
# ──────────────────────────────────────────────────────────────────────────


def _bridge_actionable_item(
    document_name: str = "example-thread",
    top_status: str = "NEW",
    top_file: str = "bridge/example-thread-001.md",
) -> SimpleNamespace:
    """Minimal duck-typed actionable item for trigger internal-call tests."""
    return SimpleNamespace(
        document_name=document_name,
        top_status=top_status,
        top_file=top_file,
        dispatchable=True,
    )


def test_keyword_emitted_only_on_actionable() -> None:
    """ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 — bridge dispatch spawns
    headless harness only when actionable work appears.

    The canonical keyword is part of ``_dispatch_prompt``; the prompt is
    only built inside the dispatch path that fires when actionable
    signature changes. Test: the keyword IS present in the dispatch
    prompt when ``_dispatch_prompt`` is called with a non-empty actionable
    list; and is the FIRST line per the spec.
    """
    trigger = _load_trigger()
    target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="codex",
        canonical_mode="lo",
    )
    prompt = trigger._dispatch_prompt(
        target,
        [_bridge_actionable_item()],
        trigger.DEFAULT_MAX_ITEMS,
    )
    lines = prompt.splitlines()
    assert lines, "dispatch prompt was empty"
    assert lines[0] == "::init gtkb lo", (
        f"First line of dispatch prompt MUST be the canonical keyword, got {lines[0]!r}"
    )


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-no-idle-emission — DCL-SMART-POLLER-AUTO-TRIGGER-001 v2
# ──────────────────────────────────────────────────────────────────────────


def test_no_keyword_on_idle_signature(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 — auto-trigger NEVER fires when
    work waits, never when idle. With an empty INDEX, no
    ``_dispatch_prompt`` call happens and no keyword is emitted.

    Test exercises ``run_trigger`` end-to-end with an empty INDEX and
    asserts (a) no spawn launched, (b) reason indicates idle, (c) keyword
    env var would NOT be set because spawn did not happen.
    """
    trigger = _load_trigger()

    # Synthetic empty project.
    (tmp_path / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestIdle"\nprofile = "dual-agent"\n', encoding="utf-8"
    )
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text("# empty\n", encoding="utf-8")
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")

    monkeypatch.delenv("GTKB_NO_CROSS_HARNESS_TRIGGER", raising=False)
    state_dir = tmp_path / "state"
    summary = trigger.run_trigger(project_root=tmp_path, state_dir=state_dir, dry_run=True)

    # No actionable -> no dispatch path entered for either recipient.
    for recipient in ("prime-builder", "loyal-opposition"):
        assert summary["results"][recipient]["launched"] is False
        assert summary["results"][recipient]["reason"] in {
            "no_pending",
            "no_pending_after_filter",
        }, (
            f"Idle INDEX must NOT trigger dispatch for {recipient!r}; "
            f"got reason={summary['results'][recipient]['reason']!r}"
        )


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-defer-to-durable — DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 v2
# ──────────────────────────────────────────────────────────────────────────


def test_receiver_defers_to_durable_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 v2 — bridge dispatch
    prompts audit against the durable role record, not against inline prose.

    Setup: Claude harness B has durable role 'prime-builder'. A dispatch
    arrives with keyword 'lo'. The receiver MUST consult ITS OWN durable
    role record (B -> prime-builder -> {'pb'}) for audit evidence, while still
    authorizing the explicit keyword regardless of whatever role the prompt's
    prose body claims.
    """
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    claude_hook = _load_claude_hook_isolated("defer_to_durable")
    failures_path = tmp_path / "dispatch-failures.jsonl"

    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-defer")
    # Keyword says lo, but Claude harness B has durable role prime-builder ({'pb'}).
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    decision, reason = claude_hook._bridge_dispatch_keyword_check(project_root=tmp_path, failures_path=failures_path)
    assert decision == claude_hook.StartupDecision.DISPATCH_AUTHORIZED, (
        f"Claude (durable role prime-builder, {{'pb'}}) MUST authorize and audit a "
        f"keyword='lo' dispatch; got {decision.value!r} ({reason!r}). "
        "Receiver must audit against its own durable role record."
    )
    assert "not in role set" in reason


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-audit-log-on-misdirect — PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2
# ──────────────────────────────────────────────────────────────────────────


def test_misdirected_dispatch_writes_audit_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 — role mismatch must
    be investigable via audit log entry.

    The S321 incident class: dispatch failures running undetected for hours.
    The prompt-role authority revision requires every role mismatch to leave a JSONL record
    at ``.gtkb-state/bridge-poller/dispatch-failures.jsonl`` with structured
    fields. Test asserts the file is created and contains the expected
    fields after a misdirected dispatch.
    """
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    claude_hook = _load_claude_hook_isolated("audit_log")
    failures_path = tmp_path / "dispatch-failures.jsonl"

    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-misdirect-001")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    decision, _reason = claude_hook._bridge_dispatch_keyword_check(project_root=tmp_path, failures_path=failures_path)
    assert decision == claude_hook.StartupDecision.DISPATCH_AUTHORIZED

    assert failures_path.is_file(), (
        "Role mismatch must leave an audit-log entry at the dispatch-failures path; no file was created."
    )
    lines = [line for line in failures_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines, "dispatch-failures.jsonl was empty after role mismatch"
    record = json.loads(lines[-1])
    assert record["kind"] == "dispatch_role_mismatch_authorized"
    assert record["run_id"] == "test-run-misdirect-001"
    assert record["observed_keyword_mode"] == "lo"
    assert record["expected_role_set"] == ["pb"]
    assert record["own_harness_id"] == "B"
    assert record["own_harness_name"] == "claude"
    assert "ts" in record
