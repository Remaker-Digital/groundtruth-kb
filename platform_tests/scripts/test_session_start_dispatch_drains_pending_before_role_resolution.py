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

ROOT = Path(__file__).resolve().parents[2]
# Slice D of GTKB-STARTUP-REFRACTOR-001: main() and the pending-transaction
# drain moved into the shared core; the thin wrappers delegate. The drain
# ordering is therefore a single-source property of the core module.
CORE = ROOT / "scripts" / "session_start_dispatch_core.py"


def test_session_start_dispatch_imports_apply_pending() -> None:
    """The shared core must import apply_pending from groundtruth_kb.mode_switch.pending."""
    text = CORE.read_text(encoding="utf-8")
    assert "from groundtruth_kb.mode_switch.pending import apply_pending" in text, (
        f"{CORE} missing apply_pending import"
    )


def test_session_start_dispatch_apply_pending_precedes_role_resolution() -> None:
    """apply_pending() call must appear before _bridge_dispatch_keyword_check() in main()."""
    text = CORE.read_text(encoding="utf-8")
    main_pos = text.find("def main()")
    assert main_pos > -1, f"{CORE}: main() not found"
    main_apply_pos = text.find("apply_pending", main_pos)
    main_resolution_pos = text.find("_bridge_dispatch_keyword_check()", main_pos)
    assert main_apply_pos > -1, f"{CORE}: apply_pending call not found in main()"
    assert main_resolution_pos > -1, f"{CORE}: role-resolution call not found in main()"
    assert main_apply_pos < main_resolution_pos, f"{CORE}: apply_pending must precede role-resolution in main()"
