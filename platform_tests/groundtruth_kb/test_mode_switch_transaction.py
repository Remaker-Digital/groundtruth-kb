"""Tests for groundtruth_kb.mode_switch.transaction.apply_role_switch.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criteria #1
(deterministic component), #2 (validation before write), and #3 (audit
evidence).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.mode_switch.transaction import (
    TransactionValidationError,
    apply_role_switch,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_workspace(
    root: Path,
    *,
    role_map: dict | None = None,
    index_text: str | None = None,
) -> None:
    if role_map is None:
        role_map = {
            "harnesses": {
                "A": {"role": ["loyal-opposition"], "name": "codex"},
                "B": {"role": ["prime-builder"], "name": "claude"},
            }
        }
    if index_text is None:
        index_text = (
            "Document: foo\n"
            "VERIFIED: bridge/foo-002.md\n"
            "NEW: bridge/foo-001.md\n"
        )
    _write(root / "harness-state" / "role-assignments.json", json.dumps(role_map))
    _write(root / "bridge" / "INDEX.md", index_text)


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return tmp_path


def test_apply_role_switch_returns_transaction_result(project_root: Path) -> None:
    _seed_workspace(project_root)
    result = apply_role_switch(
        project_root, "claude", "loyal-opposition", change_reason="test"
    )
    assert result.harness_id == "B"
    assert result.new_role_set == ("loyal-opposition",)
    assert result.audit_record_path.exists()


def test_apply_role_switch_rejects_unknown_role(project_root: Path) -> None:
    _seed_workspace(project_root)
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "claude", "fake-role", change_reason="test")


def test_apply_role_switch_rejects_acting_prime_builder(project_root: Path) -> None:
    """GOV-ACTING-PRIME-BUILDER-001: SET-rejects the legacy compat value."""
    _seed_workspace(project_root)
    with pytest.raises(TransactionValidationError):
        apply_role_switch(
            project_root, "claude", "acting-prime-builder", change_reason="test"
        )


def test_apply_role_switch_rejects_unknown_harness(project_root: Path) -> None:
    _seed_workspace(project_root)
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "no-such-harness", "prime-builder", change_reason="t")


def test_apply_role_switch_refuses_when_bridge_index_missing(project_root: Path) -> None:
    """F2: validators run BEFORE any state mutation."""
    _write(
        project_root / "harness-state" / "role-assignments.json",
        json.dumps({"harnesses": {"A": {"role": ["prime-builder"]}}}),
    )
    # No bridge/INDEX.md
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "A", "loyal-opposition", change_reason="t")


def test_apply_role_switch_refuses_when_bridge_index_unparseable(project_root: Path) -> None:
    """F2: bridge artifact with unknown status token fails closed."""
    _write(
        project_root / "harness-state" / "role-assignments.json",
        json.dumps({"harnesses": {"A": {"role": ["prime-builder"]}}}),
    )
    _write(
        project_root / "bridge" / "INDEX.md",
        "Document: foo\nFROBNICATED: bridge/foo-001.md\n",
    )
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "A", "loyal-opposition", change_reason="t")


def test_apply_role_switch_demotes_other_harness_to_opposite_role(project_root: Path) -> None:
    """When B becomes prime-builder, A must be demoted to loyal-opposition."""
    role_map = {
        "harnesses": {
            "A": {"role": ["prime-builder"], "name": "codex"},
            "B": {"role": ["loyal-opposition"], "name": "claude"},
        }
    }
    _seed_workspace(project_root, role_map=role_map)
    apply_role_switch(project_root, "B", "prime-builder", change_reason="t")
    updated = json.loads(
        (project_root / "harness-state" / "role-assignments.json").read_text(
            encoding="utf-8"
        )
    )
    assert updated["harnesses"]["B"]["role"] == ["prime-builder"]
    assert updated["harnesses"]["A"]["role"] == ["loyal-opposition"]


def test_audit_record_contains_required_fields(project_root: Path) -> None:
    """Acceptance criterion #3: who/what/when/effective-when evidence."""
    _seed_workspace(project_root)
    result = apply_role_switch(
        project_root, "claude", "loyal-opposition", change_reason="audit fields test"
    )
    record = json.loads(result.audit_record_path.read_text(encoding="utf-8"))
    assert record["harness_id"] == "B"
    assert record["requested_role"] == "loyal-opposition"
    assert record["new_role_set"] == ["loyal-opposition"]
    assert record["change_reason"] == "audit fields test"
    assert "requested_at" in record
    assert "effective_at" in record
    assert record["deferred"] is False


def test_apply_role_switch_prime_builder_demotes_all_non_targets(
    project_root: Path,
) -> None:
    """FR9 full role partition: promoting a harness to prime-builder demotes
    EVERY other harness to loyal-opposition, including a non-target whose prior
    role set was empty (the -006 F1 regression)."""
    role_map = {
        "harnesses": {
            "A": {"role": ["prime-builder"], "name": "codex"},
            "B": {"role": ["loyal-opposition"], "name": "claude"},
            "C": {"role": [], "name": "antigravity"},
        }
    }
    _seed_workspace(project_root, role_map=role_map)
    apply_role_switch(project_root, "B", "prime-builder", change_reason="t")
    updated = json.loads(
        (project_root / "harness-state" / "role-assignments.json").read_text(
            encoding="utf-8"
        )
    )
    assert updated["harnesses"]["B"]["role"] == ["prime-builder"]
    assert updated["harnesses"]["A"]["role"] == ["loyal-opposition"]
    # C's prior role set was [] — without the FR9 fix it would survive as [].
    assert updated["harnesses"]["C"]["role"] == ["loyal-opposition"]
