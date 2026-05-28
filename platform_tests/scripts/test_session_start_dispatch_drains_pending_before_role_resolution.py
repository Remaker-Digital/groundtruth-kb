"""Test that both SessionStart dispatch hooks drain pending mode-switches
before resolving the durable role set.

Per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criterion #5/6 and
Codex review at bridge -007 F1 (and re-affirmed at -011/-013/-015): the
pending-transaction drain must run before `_bridge_dispatch_keyword_check()`
or any other role-resolution call so deferred role/topology switches take
effect for the dispatch decision.

These are source-inspection tests: invoking the hooks end-to-end requires a
full Claude/Codex SessionStart payload, which is out of scope. Tests verify
the wiring (import + call ordering by source position) rather than the
runtime behavior, which is exercised by the unit tests in
test_mode_switch_pending.py.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CODEX_HOOK = ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"
CLAUDE_HOOK = ROOT / ".claude" / "hooks" / "session_start_dispatch.py"


@pytest.mark.parametrize("hook_path", [CODEX_HOOK, CLAUDE_HOOK], ids=["codex", "claude"])
def test_session_start_dispatch_imports_apply_pending(hook_path: Path) -> None:
    """The hook must import apply_pending from groundtruth_kb.mode_switch.pending."""
    text = hook_path.read_text(encoding="utf-8")
    assert "from groundtruth_kb.mode_switch.pending import apply_pending" in text, (
        f"{hook_path} missing apply_pending import"
    )


@pytest.mark.parametrize("hook_path", [CODEX_HOOK, CLAUDE_HOOK], ids=["codex", "claude"])
def test_session_start_dispatch_apply_pending_precedes_role_resolution(hook_path: Path) -> None:
    """apply_pending() call must appear before _bridge_dispatch_keyword_check() in main()."""
    text = hook_path.read_text(encoding="utf-8")
    apply_pos = text.find("apply_pending")
    resolution_pos = text.find("_bridge_dispatch_keyword_check()")
    assert apply_pos > -1, f"{hook_path}: apply_pending not found"
    assert resolution_pos > -1, f"{hook_path}: role-resolution call not found"
    # The apply_pending import + call may appear before main(); what matters
    # is that within main() the call site comes BEFORE role resolution.
    # Locate the main() function body and check ordering.
    main_pos = text.find("def main()")
    assert main_pos > -1, f"{hook_path}: main() not found"
    # The apply_pending call in main() body:
    main_apply_pos = text.find("apply_pending", main_pos)
    main_resolution_pos = text.find("_bridge_dispatch_keyword_check()", main_pos)
    assert main_apply_pos > -1 and main_resolution_pos > -1
    assert main_apply_pos < main_resolution_pos, f"{hook_path}: apply_pending must precede role-resolution in main()"
