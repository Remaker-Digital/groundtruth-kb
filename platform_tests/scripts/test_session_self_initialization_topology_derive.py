"""Test that scripts/workstream_focus.save_state derives topology_mode from
the live role map per Slice 1 of gtkb-operating-mode-transaction-001.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.mode_switch.derive import topology_from_role_map


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return tmp_path


def test_topology_derives_multi_harness_for_two_singleton_role_sets() -> None:
    role_map = {
        "harnesses": {
            "A": {"role": ["loyal-opposition"]},
            "B": {"role": ["prime-builder"]},
        }
    }
    assert topology_from_role_map(role_map) == "multi_harness"


def test_topology_derives_single_harness_for_one_multi_role_set() -> None:
    role_map = {
        "harnesses": {
            "A": {"role": ["prime-builder", "loyal-opposition"]},
        }
    }
    assert topology_from_role_map(role_map) == "single_harness"


def test_topology_multi_harness_for_empty_map() -> None:
    assert topology_from_role_map({}) == "multi_harness"
    assert topology_from_role_map({"harnesses": {}}) == "multi_harness"


def test_topology_handles_legacy_scalar_role() -> None:
    role_map = {"harnesses": {"A": {"role": "prime-builder"}}}
    # Single harness with only one role token -> multi_harness (needs BOTH).
    assert topology_from_role_map(role_map) == "multi_harness"


def test_topology_handles_acting_prime_builder_as_prime() -> None:
    """GOV-ACTING-PRIME-BUILDER-001 READ-accepts the legacy value as prime."""
    role_map = {
        "harnesses": {
            "A": {"role": ["acting-prime-builder", "loyal-opposition"]},
        }
    }
    assert topology_from_role_map(role_map) == "single_harness"


def test_operating_role_md_documents_gt_mode_set_role() -> None:
    """SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 criterion #4: agent
    instructions direct agents to use the transaction component, not
    ad-hoc edits.

    Verifies that `.claude/rules/operating-role.md` documents the
    `gt mode set-role` CLI surface and the `--defer-to-next-session`
    flag as the canonical write path for role/topology changes.
    """
    rule_path = Path(__file__).resolve().parents[2] / ".claude" / "rules" / "operating-role.md"
    text = rule_path.read_text(encoding="utf-8")
    # Section heading exists.
    assert "Mode-Switch Transaction Component" in text, (
        "operating-role.md missing the Mode-Switch Transaction Component section"
    )
    # CLI surface documented.
    assert "gt mode set-role" in text, "operating-role.md missing gt mode set-role CLI reference"
    # Defer flag documented.
    assert "--defer-to-next-session" in text, "operating-role.md missing --defer-to-next-session reference"
    # Anti-ad-hoc-edit guidance present.
    assert "rather than ad-hoc direct edits" in text or "not ad-hoc" in text.lower(), (
        "operating-role.md missing anti-ad-hoc-edit guidance"
    )


def test_workstream_focus_save_state_writes_derived_topology(project_root: Path) -> None:
    """When save_state runs, topology_mode is overridden with the derived value."""
    import importlib
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    try:
        wf = importlib.import_module("workstream_focus")
    finally:
        sys.path.pop(0)

    _write(
        project_root / "harness-state" / "role-assignments.json",
        json.dumps(
            {
                "harnesses": {
                    "A": {"role": ["prime-builder", "loyal-opposition"]},
                }
            }
        ),
    )

    state = wf.save_state(
        wf.DEFAULT_FOCUS,
        project_root,
        updated_by="reset",
    )
    assert state["topology_mode"] == "single_harness"
