"""Test that scripts/cross_harness_bridge_trigger.py drains pending
mode-switches before recipient resolution.

Per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 and Codex review feedback at
bridge -007 F1 / re-affirmed at -011/-013/-015: a deferred role/topology
switch must take effect for the dispatch-target selection inside
run_trigger() (the trigger's recipient computation).

Source-inspection test; the trigger's full runtime is exercised elsewhere.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

TRIGGER = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"


def test_cross_harness_trigger_imports_apply_pending() -> None:
    text = TRIGGER.read_text(encoding="utf-8")
    assert "from groundtruth_kb.mode_switch.pending import apply_pending" in text


def test_cross_harness_trigger_apply_pending_precedes_topology_check() -> None:
    """apply_pending must run before _is_single_harness_topology() / recipient resolution."""
    text = TRIGGER.read_text(encoding="utf-8")
    run_trigger_pos = text.find("def run_trigger(")
    assert run_trigger_pos > -1, "run_trigger() not found"
    apply_pos = text.find("apply_pending(project_root)", run_trigger_pos)
    topology_check_pos = text.find("_is_single_harness_topology(project_root)", run_trigger_pos)
    assert apply_pos > -1, "apply_pending call not found in run_trigger()"
    assert topology_check_pos > -1, "topology check not found in run_trigger()"
    assert apply_pos < topology_check_pos, "apply_pending must precede topology check in run_trigger()"
