"""Tests for groundtruth_kb.mode_switch.invariants.

Spec-derived tests for the REQ-HARNESS-REGISTRY-001 FR9 role-partition
postcondition: ``prime_builder_ids`` and ``verify_role_partition``. A valid
FR9 partition holds exactly one prime-builder and every other harness exactly
``["loyal-opposition"]``.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.mode_switch.invariants import (
    RolePartitionViolation,
    prime_builder_ids,
    verify_role_partition,
)


def _write_role_map(root: Path, harnesses: dict) -> None:
    path = root / "harness-state" / "role-assignments.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"harnesses": harnesses}), encoding="utf-8")


def test_prime_builder_ids_single() -> None:
    doc = {
        "harnesses": {
            "A": {"role": ["loyal-opposition"]},
            "B": {"role": ["prime-builder"]},
        }
    }
    assert prime_builder_ids(doc) == ["B"]


def test_prime_builder_ids_handles_legacy_scalar_role() -> None:
    """A legacy scalar role wire form (``"role": "prime-builder"``) is counted."""
    doc = {
        "harnesses": {
            "A": {"role": "prime-builder"},
            "B": {"role": "loyal-opposition"},
        }
    }
    assert prime_builder_ids(doc) == ["A"]


def test_verify_role_partition_accepts_valid_partition(tmp_path: Path) -> None:
    _write_role_map(
        tmp_path,
        {
            "A": {"role": ["prime-builder"]},
            "B": {"role": ["loyal-opposition"]},
            "C": {"role": ["loyal-opposition"]},
        },
    )
    assert verify_role_partition(tmp_path) == "A"


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
