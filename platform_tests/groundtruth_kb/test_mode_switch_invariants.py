"""Tests for groundtruth_kb.mode_switch.invariants.

Spec-derived tests for the REQ-HARNESS-REGISTRY-001 FR9 role-partition
postcondition: ``prime_builder_ids`` and ``verify_role_partition``. A valid
FR9 active dispatch partition holds exactly one active prime-builder and
exactly one active loyal-opposition. Non-active harness role metadata is
retained but ignored by the active partition.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.mode_switch.invariants import (
    RolePartitionViolation,
    prime_builder_ids,
    verify_role_document_partition,
    verify_role_partition,
)


def _write_role_map(root: Path, harnesses: dict) -> None:
    """Seed the harness registry projection (WI-3342 IP-5).

    ``verify_role_partition`` reads the DB-backed registry projection
    ``harness-state/harness-registry.json``, whose ``harnesses`` field is a
    LIST of unified records (each carrying ``id`` + ``role``), not the retired
    ``harness-state/role-assignments.json`` ``{harness_id: record}`` dict. This
    helper accepts the legacy dict-keyed-by-id input and writes the equivalent
    projection LIST so each test's verification intent is preserved.
    """
    path = root / "harness-state" / "harness-registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for harness_id, record in harnesses.items():
        rec = {"id": harness_id, **record}
        if "status" not in rec:
            rec["status"] = "active"
        records.append(rec)
    path.write_text(json.dumps({"harnesses": records}), encoding="utf-8")


def test_prime_builder_ids_single() -> None:
    doc = {
        "harnesses": {
            "A": {"role": ["loyal-opposition"], "status": "active"},
            "B": {"role": ["prime-builder"], "status": "active"},
        }
    }
    assert prime_builder_ids(doc) == ["B"]


def test_prime_builder_ids_handles_legacy_scalar_role() -> None:
    """A legacy scalar role wire form (``"role": "prime-builder"``) is counted."""
    doc = {
        "harnesses": {
            "A": {"role": "prime-builder", "status": "active"},
            "B": {"role": "loyal-opposition", "status": "active"},
        }
    }
    assert prime_builder_ids(doc) == ["A"]


def test_verify_role_partition_accepts_valid_partition(tmp_path: Path) -> None:
    _write_role_map(
        tmp_path,
        {
            "A": {"role": ["prime-builder"], "status": "active"},
            "B": {"role": ["loyal-opposition"], "status": "active"},
            "C": {"role": [], "status": "suspended"},
        },
    )
    assert verify_role_partition(tmp_path) == "A"


def test_verify_role_partition_allows_non_active_role_retention(tmp_path: Path) -> None:
    """WI-4213: non-active harnesses may retain roles but do not count in the active partition."""
    _write_role_map(
        tmp_path,
        {
            "A": {"role": ["prime-builder"], "status": "active"},
            "B": {"role": ["loyal-opposition"], "status": "active"},
            "C": {"role": ["prime-builder"], "status": "registered", "event_driven_hooks": False},
        },
    )
    assert verify_role_partition(tmp_path) == "A"


def test_verify_role_document_partition_accepts_candidate_document() -> None:
    summary = verify_role_document_partition(
        {
            "harnesses": {
                "A": {"role": ["prime-builder"], "status": "active"},
                "B": {"role": ["loyal-opposition"], "status": "active"},
                "C": {"role": ["prime-builder"], "status": "registered"},
            }
        }
    )
    assert summary.prime_builder_id == "A"
    assert summary.loyal_opposition_id == "B"
    assert summary.active_harness_ids == ("A", "B")


def test_verify_role_document_partition_rejects_invalid_candidate_document() -> None:
    candidate = {
        "harnesses": {
            "A": {"role": ["prime-builder"], "status": "active"},
            "B": {"role": ["prime-builder"], "status": "active"},
            "C": {"role": ["loyal-opposition"], "status": "registered"},
        }
    }
    with pytest.raises(RolePartitionViolation, match="exactly one prime-builder"):
        verify_role_document_partition(candidate)


def test_verify_role_partition_rejects_zero_prime_builder(tmp_path: Path) -> None:
    _write_role_map(
        tmp_path,
        {
            "A": {"role": ["loyal-opposition"]},
            "B": {"role": ["loyal-opposition"]},
        },
    )
    with pytest.raises(RolePartitionViolation):
        verify_role_partition(tmp_path)


def test_verify_role_partition_rejects_multiple_prime_builder(tmp_path: Path) -> None:
    _write_role_map(
        tmp_path,
        {
            "A": {"role": ["prime-builder"]},
            "B": {"role": ["prime-builder"]},
        },
    )
    with pytest.raises(RolePartitionViolation) as exc:
        verify_role_partition(tmp_path)
    message = str(exc.value)
    assert "A" in message and "B" in message


def test_verify_role_partition_rejects_non_target_without_loyal_opposition(
    tmp_path: Path,
) -> None:
    """Exactly one prime-builder, but a non-target has an empty role set — the
    -006 F1 gap a prime-count-only check missed."""
    _write_role_map(
        tmp_path,
        {
            "A": {"role": ["prime-builder"]},
            "B": {"role": ["loyal-opposition"]},
            "C": {"role": []},
        },
    )
    with pytest.raises(RolePartitionViolation) as exc:
        verify_role_partition(tmp_path)
    assert "C" in str(exc.value)
