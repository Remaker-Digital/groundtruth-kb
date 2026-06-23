"""Tests for groundtruth_kb.mode_switch.transaction.apply_role_switch.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criteria #1
(deterministic component), #2 (validation before write), and #3 (audit
evidence).

WI-3342 IP-6: ``apply_role_switch`` was migrated to read the harness role map
from the DB-backed registry projection ``harness-state/harness-registry.json``
and to persist the post-switch role map through the DB ``harnesses`` table +
projection regeneration (the transitional ``role-assignments.json`` write was
removed). The fixtures here therefore seed a real ``groundtruth.db`` with the
test harnesses and generate the projection from it; post-write assertions read
the regenerated projection rather than the retired role-assignments.json.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import (  # noqa: E402
    generate_harness_projection,
)
from groundtruth_kb.mode_switch.transaction import (  # noqa: E402
    TransactionValidationError,
    apply_role_switch,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


HarnessSeed = tuple[str, list[str]] | tuple[str, list[str], str]

# Default harnesses for a seeded workspace: harness A (codex) loyal-opposition,
# harness B (claude) prime-builder. Each entry is (harness_name, role-set)
# or (harness_name, role-set, status).
_DEFAULT_HARNESSES: dict[str, HarnessSeed] = {
    "A": ("codex", ["loyal-opposition"]),
    "B": ("claude", ["prime-builder"]),
}


def _seed_workspace(
    root: Path,
    *,
    harnesses: dict[str, HarnessSeed] | None = None,
    index_text: str | None = None,
) -> None:
    """Seed a real ``groundtruth.db`` registry + generated projection + INDEX.

    ``harnesses`` maps each durable harness id to ``(harness_name, role_set)``.
    A real DB is required because ``apply_role_switch`` persists the post-switch
    role map through the DB ``harnesses`` table (``_mirror_role_map_to_registry``
    skips any harness with no current DB row) and then regenerates the
    projection — the surface every post-write assertion reads.
    """
    if harnesses is None:
        harnesses = _DEFAULT_HARNESSES
    if index_text is None:
        index_text = "Document: foo\nVERIFIED: bridge/foo-002.md\nNEW: bridge/foo-001.md\n"
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    for harness_id, seed in harnesses.items():
        harness_name, role_set = seed[0], seed[1]
        status = seed[2] if len(seed) > 2 else "active"
        db.insert_harness(
            id=harness_id,
            harness_name=harness_name,
            harness_type=harness_name,
            role=list(role_set),
            changed_by="test",
            change_reason="WI-3342 IP-6 mode-switch transaction fixture",
            status=status,
        )
    generate_harness_projection(db, root)
    _write(root / "bridge" / "INDEX.md", index_text)
    _write(root / "bridge" / "foo-001.md", "NEW\n")


def _read_role_map(root: Path) -> dict[str, Any]:
    """Return ``{harness_id: role_set}`` from the regenerated registry projection.

    WI-3342 IP-6: the authoritative post-switch role surface is the DB-backed
    registry projection (``harness-state/harness-registry.json``), not the
    retired ``harness-state/role-assignments.json``.
    """
    projection = json.loads((root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    return {
        str(record["id"]): record.get("role")
        for record in projection.get("harnesses", [])
        if isinstance(record, dict) and record.get("id")
    }


def _audit_records(root: Path) -> list[Path]:
    return sorted((root / ".gtkb-state" / "mode-switches").glob("*.json"))


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return tmp_path


def test_apply_role_switch_returns_transaction_result(project_root: Path) -> None:
    _seed_workspace(project_root)
    # WI-3342 IP-6: target the harness by its durable id. apply_role_switch
    # reads the registry projection, whose records carry ``harness_name`` (not
    # the legacy ``name`` key), so harness-id targeting is the migration-stable
    # path; harness B is the claude harness.
    result = apply_role_switch(project_root, "B", "prime-builder", change_reason="test")
    assert result.harness_id == "B"
    assert result.new_role_set == ("prime-builder",)
    assert result.audit_record_path.exists()


def test_apply_role_switch_rejects_unknown_role(project_root: Path) -> None:
    _seed_workspace(project_root)
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "claude", "fake-role", change_reason="test")


def test_apply_role_switch_rejects_acting_prime_builder(project_root: Path) -> None:
    """GOV-ACTING-PRIME-BUILDER-001: SET-rejects the legacy compat value."""
    _seed_workspace(project_root)
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "claude", "acting-prime-builder", change_reason="test")


def test_apply_role_switch_rejects_unknown_harness(project_root: Path) -> None:
    _seed_workspace(project_root)
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "no-such-harness", "prime-builder", change_reason="t")


def test_apply_role_switch_refuses_when_bridge_index_missing(project_root: Path) -> None:
    """F2: validators run BEFORE any state mutation.

    WI-3342 IP-6: a valid registry projection is seeded so the role-artifact
    validator passes and the bridge-artifact validator (missing INDEX) is the
    failure under test.
    """
    db = KnowledgeDB(db_path=project_root / "groundtruth.db")
    db.insert_harness(
        id="A",
        harness_name="codex",
        harness_type="codex",
        role=["prime-builder"],
        changed_by="test",
        change_reason="fixture",
        status="active",
    )
    generate_harness_projection(db, project_root)
    # No bridge/INDEX.md
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "A", "loyal-opposition", change_reason="t")


def test_apply_role_switch_refuses_when_bridge_index_unparseable(project_root: Path) -> None:
    """F2: bridge artifact with unknown status token fails closed.

    WI-3342 IP-6: a valid registry projection is seeded so the bridge-artifact
    validator (unknown status token) is the failure under test.
    """
    db = KnowledgeDB(db_path=project_root / "groundtruth.db")
    db.insert_harness(
        id="A",
        harness_name="codex",
        harness_type="codex",
        role=["prime-builder"],
        changed_by="test",
        change_reason="fixture",
        status="active",
    )
    generate_harness_projection(db, project_root)
    _write(
        project_root / "bridge" / "INDEX.md",
        "Document: foo\nFROBNICATED: bridge/foo-001.md\n",
    )
    with pytest.raises(TransactionValidationError):
        apply_role_switch(project_root, "A", "loyal-opposition", change_reason="t")


def test_apply_role_switch_rejects_invalid_active_candidate_without_reassignment(project_root: Path) -> None:
    """Changing only B to prime-builder would leave two active Prime Builders."""
    _seed_workspace(
        project_root,
        harnesses={
            "A": ("codex", ["prime-builder"]),
            "B": ("claude", ["loyal-opposition"]),
        },
    )
    with pytest.raises(TransactionValidationError, match="at least one loyal-opposition"):
        apply_role_switch(project_root, "B", "prime-builder", change_reason="t")
    updated = _read_role_map(project_root)
    assert updated["A"] == ["prime-builder"]
    assert updated["B"] == ["loyal-opposition"]
    assert _audit_records(project_root) == []


def test_audit_record_contains_required_fields(project_root: Path) -> None:
    """Acceptance criterion #3: who/what/when/effective-when evidence."""
    _seed_workspace(project_root)
    # WI-3342 IP-6: target harness B (claude) by its durable id.
    result = apply_role_switch(project_root, "B", "prime-builder", change_reason="audit fields test")
    record = json.loads(result.audit_record_path.read_text(encoding="utf-8"))
    assert record["harness_id"] == "B"
    assert record["requested_role"] == "prime-builder"
    assert record["new_role_set"] == ["prime-builder"]
    assert record["change_reason"] == "audit fields test"
    assert "requested_at" in record
    assert "effective_at" in record
    assert record["deferred"] is False


def test_apply_role_switch_allows_multiple_prime_builders(
    project_root: Path,
) -> None:
    """Active candidates can have multiple prime-builders and loyal-oppositions."""
    _seed_workspace(
        project_root,
        harnesses={
            "A": ("codex", ["prime-builder"]),
            "B": ("claude", ["loyal-opposition"]),
            "C": ("antigravity", ["loyal-opposition"]),
        },
    )
    apply_role_switch(project_root, "B", "prime-builder", change_reason="t")
    updated = _read_role_map(project_root)
    assert updated["A"] == ["prime-builder"]
    assert updated["B"] == ["prime-builder"]
    assert updated["C"] == ["loyal-opposition"]


def test_apply_role_switch_preserves_non_active_retained_roles(project_root: Path) -> None:
    """WI-4213: role membership is not erased merely because a harness is non-active."""
    _seed_workspace(
        project_root,
        harnesses={
            "A": ("codex", ["loyal-opposition"]),
            "B": ("claude", ["prime-builder"]),
            "C": ("antigravity", ["prime-builder"], "registered"),
        },
    )
    apply_role_switch(project_root, "C", "loyal-opposition", change_reason="preserve non-active role")
    updated = _read_role_map(project_root)
    assert updated["A"] == ["loyal-opposition"]
    assert updated["B"] == ["prime-builder"]
    assert updated["C"] == ["loyal-opposition"]
