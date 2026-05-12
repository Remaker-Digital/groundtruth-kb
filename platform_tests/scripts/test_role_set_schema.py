# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the role-set schema introduced by IP-8 of
bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (Codex GO at -014).

Specs:
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 (Path 2 atomic migration)
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 (behavior contract)
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 (wake substrate)
- DCL-CROSS-HARNESS-ENFORCEMENT-001 (preserved)
- GOV-HARNESS-ROLE-PORTABILITY-001 (preserved)

Covers IP-7 (role-set schema test surface), IP-9 (runtime migration
regression — write-always-list + legacy-scalar reads), and IP-9b
(acting-prime-builder READ acceptance + SET rejection).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.harness_roles import (
    ROLE_ACTING_PRIME_BUILDER,
    ROLE_LOYAL_OPPOSITION,
    ROLE_PRIME_BUILDER,
    VALID_ROLES_FOR_READ,
    VALID_ROLES_FOR_WRITE,
    _normalize_role_field,
    _role_set_to_json,
    is_loyal_opposition,
    is_prime_builder,
    load_role_assignments,
    primary_role,
    role_for_harness,
    set_harness_role,
)


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-role-set-schema-valid: helpers accept scalar + list forms
# ──────────────────────────────────────────────────────────────────────────


def test_normalize_role_field_accepts_legacy_scalar() -> None:
    assert _normalize_role_field("prime-builder") == frozenset({ROLE_PRIME_BUILDER})
    assert _normalize_role_field("loyal-opposition") == frozenset({ROLE_LOYAL_OPPOSITION})
    assert _normalize_role_field("acting-prime-builder") == frozenset({ROLE_ACTING_PRIME_BUILDER})
    # Mixed case is normalized to lowercase.
    assert _normalize_role_field("Prime-Builder") == frozenset({ROLE_PRIME_BUILDER})


def test_normalize_role_field_accepts_singleton_list() -> None:
    assert _normalize_role_field(["prime-builder"]) == frozenset({ROLE_PRIME_BUILDER})
    assert _normalize_role_field(["loyal-opposition"]) == frozenset({ROLE_LOYAL_OPPOSITION})


def test_normalize_role_field_accepts_multi_element_list() -> None:
    assert _normalize_role_field(["prime-builder", "loyal-opposition"]) == frozenset(
        {ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION}
    )
    # Order-insensitive.
    assert _normalize_role_field(["loyal-opposition", "prime-builder"]) == frozenset(
        {ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION}
    )


def test_normalize_role_field_drops_unknown_tokens() -> None:
    assert _normalize_role_field(["prime-builder", "bogus-role"]) == frozenset({ROLE_PRIME_BUILDER})
    assert _normalize_role_field("not-a-real-role") == frozenset()


def test_normalize_role_field_handles_empty_and_none() -> None:
    assert _normalize_role_field(None) == frozenset()
    assert _normalize_role_field("") == frozenset()
    assert _normalize_role_field([]) == frozenset()
    assert _normalize_role_field(123) == frozenset()  # unsupported type


def test_role_set_to_json_sorts_canonically() -> None:
    assert _role_set_to_json({ROLE_PRIME_BUILDER}) == ["prime-builder"]
    assert _role_set_to_json({ROLE_LOYAL_OPPOSITION, ROLE_PRIME_BUILDER}) == [
        "loyal-opposition",
        "prime-builder",
    ]
    # Tuples and frozensets are equivalent inputs.
    assert _role_set_to_json(frozenset({"prime-builder", "loyal-opposition"})) == [
        "loyal-opposition",
        "prime-builder",
    ]


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-attribution-prime-first: multi-element sets attribute as Prime
# ──────────────────────────────────────────────────────────────────────────


def test_is_prime_builder_singleton_set() -> None:
    assert is_prime_builder({"role": ["prime-builder"]}) is True
    assert is_prime_builder({"role": ["loyal-opposition"]}) is False


def test_is_prime_builder_multi_element_set() -> None:
    """Single-harness mode role set contains BOTH roles; Prime attribution wins."""
    assert is_prime_builder({"role": ["prime-builder", "loyal-opposition"]}) is True


def test_is_prime_builder_legacy_acting_prime() -> None:
    """Acting-Prime Compatibility Contract: acting-prime-builder reads as Prime-equivalent."""
    assert is_prime_builder({"role": "acting-prime-builder"}) is True
    assert is_prime_builder({"role": ["acting-prime-builder"]}) is True


def test_is_loyal_opposition_membership() -> None:
    assert is_loyal_opposition({"role": ["loyal-opposition"]}) is True
    assert is_loyal_opposition({"role": ["prime-builder"]}) is False
    # Multi-element set containing LO returns True.
    assert is_loyal_opposition({"role": ["prime-builder", "loyal-opposition"]}) is True


def test_primary_role_prime_first() -> None:
    assert primary_role({"role": ["prime-builder", "loyal-opposition"]}) == ROLE_PRIME_BUILDER
    assert primary_role({"role": ["loyal-opposition"]}) == ROLE_LOYAL_OPPOSITION
    # Acting-Prime resolves to Prime for primary-role display.
    assert primary_role({"role": "acting-prime-builder"}) == ROLE_PRIME_BUILDER


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-write-always-list: every WRITE path emits JSON list, never scalar
# ──────────────────────────────────────────────────────────────────────────


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_set_harness_role_writes_list_form(tmp_path: Path) -> None:
    role_path = tmp_path / "harness-state" / "role-assignments.json"
    set_harness_role(
        tmp_path,
        ROLE_PRIME_BUILDER,
        harness_id="A",
        harness_name="codex",
        assignment_path=role_path,
    )
    data = _read(role_path)
    assert isinstance(data["harnesses"]["A"]["role"], list)
    assert data["harnesses"]["A"]["role"] == [ROLE_PRIME_BUILDER]


def test_role_for_harness_writes_list_form_on_self_correction(tmp_path: Path) -> None:
    role_path = tmp_path / "harness-state" / "role-assignments.json"
    role_for_harness(
        tmp_path,
        harness_id="B",
        harness_name="claude",
        assignment_path=role_path,
        ensure_prime_on_startup=True,
    )
    data = _read(role_path)
    assert isinstance(data["harnesses"]["B"]["role"], list)


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-legacy-scalar-read + writeback (IP-9b + IP-10)
# ──────────────────────────────────────────────────────────────────────────


def test_legacy_scalar_role_reads_as_singleton_set(tmp_path: Path) -> None:
    role_path = tmp_path / "harness-state" / "role-assignments.json"
    role_path.parent.mkdir(parents=True, exist_ok=True)
    role_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "A": {"harness_type": "codex", "role": "loyal-opposition"},
                    "B": {"harness_type": "claude", "role": "prime-builder"},
                },
            }
        ),
        encoding="utf-8",
    )

    document = load_role_assignments(tmp_path, assignment_path=role_path)
    # Loader normalizes legacy scalar values into list form.
    assert document["harnesses"]["A"]["role"] == ["loyal-opposition"]
    assert document["harnesses"]["B"]["role"] == ["prime-builder"]


def test_legacy_scalar_upgrades_to_list_on_first_write(tmp_path: Path) -> None:
    """IP-10 backward-compat one-shot smoke test."""
    role_path = tmp_path / "harness-state" / "role-assignments.json"
    role_path.parent.mkdir(parents=True, exist_ok=True)
    role_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "A": {"harness_type": "codex", "role": "loyal-opposition"},
                    "B": {"harness_type": "claude", "role": "prime-builder"},
                },
            }
        ),
        encoding="utf-8",
    )

    # Trigger a write via set_harness_role.
    set_harness_role(
        tmp_path,
        ROLE_LOYAL_OPPOSITION,
        harness_id="B",
        harness_name="claude",
        assignment_path=role_path,
    )

    data = _read(role_path)
    # B's role set should now be list form.
    assert data["harnesses"]["B"]["role"] == ["loyal-opposition"]
    # A's role set was carried through the normalize/write cycle and is also list form now.
    assert data["harnesses"]["A"]["role"] == ["loyal-opposition"]


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-multi-element-set-single-harness-mode (single-harness topology)
# ──────────────────────────────────────────────────────────────────────────


def test_multi_element_role_set_persists_through_load(tmp_path: Path) -> None:
    """Single-harness mode: multi-element role set survives load + normalize."""
    role_path = tmp_path / "harness-state" / "role-assignments.json"
    role_path.parent.mkdir(parents=True, exist_ok=True)
    role_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "B": {
                        "harness_type": "claude",
                        "role": ["prime-builder", "loyal-opposition"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    document = load_role_assignments(tmp_path, assignment_path=role_path)
    assert sorted(document["harnesses"]["B"]["role"]) == [
        "loyal-opposition",
        "prime-builder",
    ]


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-acting-prime-legacy-read-compat (IP-9b explicit)
# ──────────────────────────────────────────────────────────────────────────


def test_legacy_acting_prime_scalar_read_via_normalize() -> None:
    role_set = _normalize_role_field("acting-prime-builder")
    assert role_set == frozenset({ROLE_ACTING_PRIME_BUILDER})
    assert is_prime_builder({"role": "acting-prime-builder"}) is True


def test_legacy_acting_prime_list_read_via_normalize() -> None:
    role_set = _normalize_role_field(["acting-prime-builder"])
    assert role_set == frozenset({ROLE_ACTING_PRIME_BUILDER})


def test_legacy_acting_prime_mixed_set_read() -> None:
    role_set = _normalize_role_field(["acting-prime-builder", "loyal-opposition"])
    assert role_set == frozenset({ROLE_ACTING_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION})
    assert is_prime_builder({"role": ["acting-prime-builder", "loyal-opposition"]}) is True
    assert is_loyal_opposition({"role": ["acting-prime-builder", "loyal-opposition"]}) is True


def test_set_role_rejects_acting_prime(tmp_path: Path) -> None:
    role_path = tmp_path / "harness-state" / "role-assignments.json"
    with pytest.raises(ValueError, match="acting-prime-builder is a READ-only"):
        set_harness_role(
            tmp_path,
            ROLE_ACTING_PRIME_BUILDER,
            harness_id="A",
            harness_name="codex",
            assignment_path=role_path,
        )


def test_read_write_vocabulary_separation() -> None:
    """VALID_ROLES_FOR_READ is strict superset of VALID_ROLES_FOR_WRITE.

    READ accepts the legacy compatibility/provenance value
    `acting-prime-builder`; WRITE does not.
    """
    assert VALID_ROLES_FOR_READ == {
        ROLE_PRIME_BUILDER,
        ROLE_LOYAL_OPPOSITION,
        ROLE_ACTING_PRIME_BUILDER,
    }
    assert VALID_ROLES_FOR_WRITE == {ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION}
    assert VALID_ROLES_FOR_WRITE.issubset(VALID_ROLES_FOR_READ)
    assert ROLE_ACTING_PRIME_BUILDER in VALID_ROLES_FOR_READ
    assert ROLE_ACTING_PRIME_BUILDER not in VALID_ROLES_FOR_WRITE
