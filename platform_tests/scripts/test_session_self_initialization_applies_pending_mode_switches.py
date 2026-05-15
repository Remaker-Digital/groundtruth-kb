"""Test that scripts/session_self_initialization.py drains pending
mode-switch transactions before topology derivation, per Slice 1 of
gtkb-operating-mode-transaction-001.

Source-inspection test verifying the integration is wired correctly. The
runtime behavior of apply_pending is exercised by
test_mode_switch_pending.py.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "session_self_initialization.py"
)


def test_session_self_initialization_imports_apply_pending() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "from groundtruth_kb.mode_switch.pending import apply_pending" in text


def test_session_self_initialization_apply_pending_in_main() -> None:
    """apply_pending must be called inside main(), after project_root resolution."""
    text = SCRIPT.read_text(encoding="utf-8")
    main_pos = text.find("def main(")
    assert main_pos > -1, "main() not found"
    project_root_pos = text.find("project_root = args.project_root.resolve()", main_pos)
    apply_pos = text.find("_apply_pending(project_root)", main_pos)
    assert project_root_pos > -1, "project_root assignment not found in main()"
    assert apply_pos > -1, "apply_pending call not found in main()"
    assert apply_pos > project_root_pos, (
        "apply_pending must be called after project_root is resolved"
    )
