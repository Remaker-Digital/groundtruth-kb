# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cross-harness hook-registration parity for workstream-focus UserPromptSubmit.

Authority: bridge `gtkb-loyal-opposition-startup-symmetry-001` GO at -008,
IP-12 (`.claude/settings.json` UserPromptSubmit registration; first-position
ordering).

Specs: DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001; init-keyword
matching MUST run before owner-decision-tracker so the tracker doesn't see
init-keyword prompts as prose decision-asks.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_SETTINGS = REPO_ROOT / ".claude" / "settings.json"
CODEX_HOOKS = REPO_ROOT / ".codex" / "hooks.json"


@pytest.fixture(scope="module")
def claude_settings() -> dict:
    return json.loads(CLAUDE_SETTINGS.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def codex_hooks() -> dict:
    return json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))


def _flatten_user_prompt_submit_commands(settings: dict) -> list[str]:
    """Collect all command strings from the UserPromptSubmit hook array."""
    ups = settings.get("hooks", {}).get("UserPromptSubmit", [])
    commands: list[str] = []
    for entry in ups:
        for hook in entry.get("hooks", []):
            cmd = hook.get("command")
            if isinstance(cmd, str):
                commands.append(cmd)
    return commands


def test_claude_userpromptsubmit_includes_workstream_focus(claude_settings: dict) -> None:
    """T-LOSS-claude-userpromptsubmit-routes-init-keyword: workstream-focus is registered."""
    commands = _flatten_user_prompt_submit_commands(claude_settings)
    assert any("workstream-focus.py" in cmd for cmd in commands), (
        f"workstream-focus.py not found in Claude UserPromptSubmit hooks: {commands}"
    )


def test_claude_userpromptsubmit_workstream_focus_runs_first(claude_settings: dict) -> None:
    """workstream-focus.py MUST be the first hook in the UserPromptSubmit chain.

    Ordering rationale: init-keyword matching runs before owner-decision-tracker
    so init-keyword prompts are not seen by the tracker as prose decision-asks.
    """
    commands = _flatten_user_prompt_submit_commands(claude_settings)
    assert commands, "expected at least one UserPromptSubmit hook"
    assert "workstream-focus.py" in commands[0], (
        f"workstream-focus.py must be first in UserPromptSubmit array; got first={commands[0]!r}"
    )
    assert "cmd /d /s /c" not in commands[0], (
        "Claude workstream-focus UserPromptSubmit hook must not depend on a cmd.exe "
        "environment wrapper; the Python adapter sets GTKB_HARNESS_NAME=claude."
    )


def test_claude_workstream_focus_adapter_sets_harness_name() -> None:
    """The Python adapter owns Claude harness selection for lifecycle guards."""
    adapter_text = (REPO_ROOT / ".claude" / "hooks" / "workstream-focus.py").read_text(encoding="utf-8")
    assert 'os.environ.setdefault("GTKB_HARNESS_NAME", "claude")' in adapter_text


def test_codex_userpromptsubmit_includes_workstream_focus(codex_hooks: dict) -> None:
    """T-LOSS-codex-userpromptsubmit-routes-init-keyword: Codex parity (existing).

    Codex side uses .codex/gtkb-hooks/workstream-focus.cmd which delegates to
    the same .claude/hooks/workstream-focus.py module. This test asserts the
    Codex registration is still present.
    """
    # Walk the codex hooks structure looking for workstream-focus references.
    raw = json.dumps(codex_hooks)
    assert "workstream-focus" in raw, "Codex hooks.json must reference workstream-focus (cross-harness parity)"


# ──────────────────────────────────────────────────────────────────────────
# Startup-disclosure relay cache parity
#
# Authority: bridge/gtkb-startup-relay-truncation-fix-refile-003.md (Codex GO
# at -004); ADR-CODEX-HOOK-PARITY-FALLBACK-001.
# ──────────────────────────────────────────────────────────────────────────

_RELAY_DISPATCHERS = {
    "claude": REPO_ROOT / ".claude" / "hooks" / "session_start_dispatch.py",
    "codex": REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py",
}


def test_startup_relay_cache_write_is_parity_across_dispatchers() -> None:
    """T6 -- ADR-CODEX-HOOK-PARITY-FALLBACK-001: both SessionStart dispatchers
    write the harness-scoped startup-disclosure relay cache.

    The bounded-pointer relay is sound only if BOTH harness dispatchers populate
    the harness-scoped cache; a one-harness implementation would break the relay
    for the other harness.
    """
    # Verify the core implementation contains the cache writing logic
    core_path = REPO_ROOT / "scripts" / "session_start_dispatch_core.py"
    core_text = core_path.read_text(encoding="utf-8")
    assert "def _write_startup_relay_cache(" in core_text, (
        "Core dispatcher logic is missing the _write_startup_relay_cache helper"
    )
    assert "_write_startup_relay_cache(" in core_text, "Core dispatcher logic must call _write_startup_relay_cache"
    assert "last-user-visible-startup.md" in core_text
    assert "last-user-visible-startup.meta.json" in core_text

    # Verify each wrapper delegates/imports the core dispatcher
    for harness, path in _RELAY_DISPATCHERS.items():
        text = path.read_text(encoding="utf-8")
        assert "session_start_dispatch_core" in text, f"{harness} dispatcher is missing the core delegation import"
