# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Configuration validation tests for Slice 3 hook registrations.

Per ``bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-003.md``
GO at ``-004`` (Codex review):

- T-3-claude-registration: ``.claude/settings.json`` registers PostToolUse
  Bash, PostToolUse Write|Edit, and Stop entries that invoke
  ``scripts/cross_harness_bridge_trigger.py`` with the shared smart-poller
  state path (Option A overlap coordination); Stop entry uses ``--stop-hook``.
- T-3-codex-registration: ``.codex/hooks.json`` registers PostToolUse Bash,
  PostToolUse apply_patch, and Stop entries with the same script + state
  path; Stop entry has no matcher and uses ``--stop-hook``.

These tests validate the file shape — not the runtime behavior of the
trigger script (covered separately in `test_cross_harness_bridge_trigger.py`)
and not Codex hook firing on Windows (covered by
``DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST`` and `test_codex_hook_parity.py`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"
CODEX_HOOKS_PATH = REPO_ROOT / ".codex" / "hooks.json"

# Per Slice 3 §C1 + Codex GO -004 line 167: Slice 3 commands MUST point at
# the shared smart-poller state path during the overlap window (Option A).
SHARED_STATE_PATH_FRAGMENT_CLAUDE = ".gtkb-state/bridge-poller"
SHARED_STATE_PATH_FRAGMENT_CODEX = r".gtkb-state\bridge-poller"

TRIGGER_SCRIPT_NAME = "cross_harness_bridge_trigger.py"


@pytest.fixture(scope="module")
def claude_settings() -> dict:
    assert CLAUDE_SETTINGS_PATH.is_file(), f"Missing {CLAUDE_SETTINGS_PATH}"
    return json.loads(CLAUDE_SETTINGS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def codex_hooks() -> dict:
    assert CODEX_HOOKS_PATH.is_file(), f"Missing {CODEX_HOOKS_PATH}"
    return json.loads(CODEX_HOOKS_PATH.read_text(encoding="utf-8"))


def _all_post_tool_use_groups(config: dict) -> list[dict]:
    return list(config.get("hooks", {}).get("PostToolUse", []))


def _all_stop_groups(config: dict) -> list[dict]:
    return list(config.get("hooks", {}).get("Stop", []))


def _matcher_for(group: dict) -> str | None:
    """Normalize matcher (treat absent / empty / None as None)."""
    m = group.get("matcher")
    if not m:
        return None
    return m


def _has_trigger_invocation(
    group: dict,
    *,
    state_path_fragment: str,
    require_stop_hook_flag: bool,
) -> bool:
    """Return True if any hook in the group invokes the trigger script with
    the expected --state-dir fragment (and --stop-hook flag if required)."""
    for hook in group.get("hooks", []):
        cmd = hook.get("command", "")
        if TRIGGER_SCRIPT_NAME not in cmd:
            continue
        if state_path_fragment not in cmd:
            continue
        if require_stop_hook_flag and "--stop-hook" not in cmd:
            continue
        if not require_stop_hook_flag and "--stop-hook" in cmd:
            # PostToolUse must NOT carry --stop-hook (the JSON output would be
            # spurious for tool-event hooks).
            continue
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────
# T-3-claude-registration
# ──────────────────────────────────────────────────────────────────────────


def test_claude_post_tool_use_bash_invokes_trigger(claude_settings: dict) -> None:
    """T-3-claude-registration (Bash): PostToolUse Bash matcher MUST invoke
    cross_harness_bridge_trigger.py with --state-dir at the shared path.
    """
    groups = _all_post_tool_use_groups(claude_settings)
    bash_groups = [g for g in groups if _matcher_for(g) == "Bash"]
    assert bash_groups, "Slice 3 requires at least one PostToolUse Bash matcher"
    assert any(
        _has_trigger_invocation(
            g,
            state_path_fragment=SHARED_STATE_PATH_FRAGMENT_CLAUDE,
            require_stop_hook_flag=False,
        )
        for g in bash_groups
    ), (
        "PostToolUse Bash matcher must invoke "
        f"{TRIGGER_SCRIPT_NAME} with --state-dir pointing at the smart-poller "
        f"shared path ({SHARED_STATE_PATH_FRAGMENT_CLAUDE})"
    )


def test_claude_post_tool_use_write_edit_invokes_trigger(claude_settings: dict) -> None:
    """T-3-claude-registration (Write|Edit): PostToolUse Write|Edit matcher
    MUST invoke the trigger.

    The matcher value is the Claude regex form ``Write|Edit`` — both tools
    are covered by a single regex matcher entry per Claude hooks docs.
    """
    groups = _all_post_tool_use_groups(claude_settings)
    we_groups = [g for g in groups if _matcher_for(g) == "Write|Edit"]
    assert we_groups, (
        "Slice 3 requires a PostToolUse Write|Edit matcher (regex form covers "
        "both Write and Edit tools)"
    )
    assert any(
        _has_trigger_invocation(
            g,
            state_path_fragment=SHARED_STATE_PATH_FRAGMENT_CLAUDE,
            require_stop_hook_flag=False,
        )
        for g in we_groups
    )


def test_claude_stop_invokes_trigger_with_stop_hook_flag(claude_settings: dict) -> None:
    """T-3-claude-registration (Stop): Stop hook MUST invoke the trigger
    with --stop-hook so the JSON output contract is satisfied.
    """
    groups = _all_stop_groups(claude_settings)
    assert groups, "Slice 3 requires at least one Stop hook entry"
    assert any(
        _has_trigger_invocation(
            g,
            state_path_fragment=SHARED_STATE_PATH_FRAGMENT_CLAUDE,
            require_stop_hook_flag=True,
        )
        for g in groups
    ), (
        f"Stop hook must invoke {TRIGGER_SCRIPT_NAME} with --stop-hook AND "
        f"--state-dir pointing at {SHARED_STATE_PATH_FRAGMENT_CLAUDE}"
    )


# ──────────────────────────────────────────────────────────────────────────
# T-3-codex-registration
# ──────────────────────────────────────────────────────────────────────────


def test_codex_post_tool_use_bash_invokes_trigger(codex_hooks: dict) -> None:
    """T-3-codex-registration (Bash): PostToolUse Bash matcher MUST invoke
    the trigger with --state-dir at the shared (Windows-style) path.
    """
    groups = _all_post_tool_use_groups(codex_hooks)
    bash_groups = [g for g in groups if _matcher_for(g) == "Bash"]
    assert bash_groups, "Slice 3 requires at least one Codex PostToolUse Bash matcher"
    assert any(
        _has_trigger_invocation(
            g,
            state_path_fragment=SHARED_STATE_PATH_FRAGMENT_CODEX,
            require_stop_hook_flag=False,
        )
        for g in bash_groups
    )


def test_codex_post_tool_use_apply_patch_invokes_trigger(codex_hooks: dict) -> None:
    """T-3-codex-registration (apply_patch): Codex's editor tool is
    apply_patch; PostToolUse apply_patch matcher MUST invoke the trigger.
    """
    groups = _all_post_tool_use_groups(codex_hooks)
    ap_groups = [g for g in groups if _matcher_for(g) == "apply_patch"]
    assert ap_groups, (
        "Slice 3 requires a Codex PostToolUse apply_patch matcher"
    )
    assert any(
        _has_trigger_invocation(
            g,
            state_path_fragment=SHARED_STATE_PATH_FRAGMENT_CODEX,
            require_stop_hook_flag=False,
        )
        for g in ap_groups
    )


def test_codex_stop_has_no_matcher(codex_hooks: dict) -> None:
    """T-3-codex-registration (Stop matcher rule): Codex Stop matchers are
    NOT supported per OpenAI Codex hooks docs. The Stop entry MUST be
    matcher-less (the entire Stop event fires the hook globally).
    """
    groups = _all_stop_groups(codex_hooks)
    assert groups, "Slice 3 requires a Codex Stop hook entry"
    for g in groups:
        assert _matcher_for(g) is None, (
            "Codex Stop entries must NOT declare a matcher — Stop matchers "
            "are not supported by Codex hooks. Got: "
            f"{g.get('matcher')!r}"
        )


def test_codex_stop_invokes_trigger_with_stop_hook_flag(codex_hooks: dict) -> None:
    """T-3-codex-registration (Stop): Codex Stop hook MUST invoke the trigger
    with --stop-hook so the OpenAI Codex Stop JSON output contract is
    satisfied.
    """
    groups = _all_stop_groups(codex_hooks)
    assert any(
        _has_trigger_invocation(
            g,
            state_path_fragment=SHARED_STATE_PATH_FRAGMENT_CODEX,
            require_stop_hook_flag=True,
        )
        for g in groups
    ), (
        f"Codex Stop hook must invoke {TRIGGER_SCRIPT_NAME} with --stop-hook AND "
        f"--state-dir pointing at {SHARED_STATE_PATH_FRAGMENT_CODEX}"
    )


# ──────────────────────────────────────────────────────────────────────────
# Cross-harness assertions
# ──────────────────────────────────────────────────────────────────────────


def test_both_harnesses_share_dispatch_state_path(
    claude_settings: dict, codex_hooks: dict
) -> None:
    """Option A coordination: BOTH harnesses' trigger invocations MUST
    target the same logical dispatch-state path (the smart-poller's
    existing ``.gtkb-state/bridge-poller/``).

    This pins the contract: signature-state file is shared so whichever
    mechanism fires first records the signature; the other sees match
    and skips. Slice 4 D3 may finalize this path; until then, this test
    locks the overlap behavior.
    """
    # Claude side — UNIX-style separator due to $CLAUDE_PROJECT_DIR + /.
    claude_commands = [
        hook.get("command", "")
        for event_groups in [
            claude_settings["hooks"]["PostToolUse"],
            claude_settings["hooks"]["Stop"],
        ]
        for group in event_groups
        for hook in group.get("hooks", [])
    ]
    claude_trigger_cmds = [
        cmd for cmd in claude_commands if TRIGGER_SCRIPT_NAME in cmd
    ]
    assert claude_trigger_cmds, "expected at least one Claude trigger registration"
    for cmd in claude_trigger_cmds:
        assert SHARED_STATE_PATH_FRAGMENT_CLAUDE in cmd, (
            f"Claude trigger registration must use the shared path: {cmd}"
        )

    # Codex side — Windows-style separator due to absolute E:\GT-KB path.
    codex_commands = [
        hook.get("command", "")
        for event_groups in [
            codex_hooks["hooks"]["PostToolUse"],
            codex_hooks["hooks"]["Stop"],
        ]
        for group in event_groups
        for hook in group.get("hooks", [])
    ]
    codex_trigger_cmds = [
        cmd for cmd in codex_commands if TRIGGER_SCRIPT_NAME in cmd
    ]
    assert codex_trigger_cmds, "expected at least one Codex trigger registration"
    for cmd in codex_trigger_cmds:
        assert SHARED_STATE_PATH_FRAGMENT_CODEX in cmd, (
            f"Codex trigger registration must use the shared path: {cmd}"
        )
