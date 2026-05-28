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
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import (  # noqa: E402
    generate_harness_projection,
)

from scripts.harness_roles import (  # noqa: E402
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

# ---------------------------------------------------------------------------
# WI-3342 IP-6 — registry-backed reader/writer fixtures.
#
# scripts/harness_roles.py was migrated off the legacy
# harness-state/role-assignments.json. load_role_assignments reads the
# DB-backed registry projection (harness-state/harness-registry.json); the
# writers mutate the DB ``harnesses`` table and regenerate the projection.
# _mirror_role_assignments_to_registry skips harnesses with no current DB row,
# so writer tests must seed a real DB first.
# ---------------------------------------------------------------------------


def _seed_registry(root: Path, harnesses: dict[str, tuple[str, list[str]]]) -> None:
    """Seed a groundtruth.db ``harnesses`` table + generated projection.

    ``harnesses`` maps each durable harness id to ``(harness_name, role_set)``.
    """
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    for harness_id, (harness_name, role_set) in harnesses.items():
        db.insert_harness(
            id=harness_id,
            harness_name=harness_name,
            harness_type=harness_name,
            role=list(role_set),
            changed_by="test",
            change_reason="WI-3342 IP-6 role_set_schema fixture",
            status="active",
        )
    generate_harness_projection(db, root)


def _write_projection_directly(root: Path, harnesses: list[dict]) -> None:
    """Write the registry projection file directly with the given records.

    Used by the legacy-scalar READ-tolerance tests: the projection reader and
    ``_normalize_role_field`` must accept a legacy scalar ``role`` wire form in
    a projection record even though the DB writer always emits list form.
    """
    registry = root / "harness-state" / "harness-registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "MemBase harnesses table (groundtruth.db)",
                "harnesses": harnesses,
            }
        ),
        encoding="utf-8",
    )


def _projection_role(root: Path, harness_id: str) -> object:
    """Return the raw ``role`` field for ``harness_id`` in the registry projection."""
    projection = json.loads(
        (root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8")
    )
    for record in projection.get("harnesses", []):
        if isinstance(record, dict) and record.get("id") == harness_id:
            return record.get("role")
    raise KeyError(harness_id)


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


def test_set_harness_role_writes_list_form(tmp_path: Path) -> None:
    # WI-3342 IP-6: the write path persists to the DB ``harnesses`` table and
    # regenerates the registry projection; the harness must exist in the DB.
    _seed_registry(tmp_path, {"A": ("codex", [ROLE_LOYAL_OPPOSITION])})
    set_harness_role(
        tmp_path,
        ROLE_PRIME_BUILDER,
        harness_id="A",
        harness_name="codex",
    )
    role = _projection_role(tmp_path, "A")
    assert isinstance(role, list)
    assert role == [ROLE_PRIME_BUILDER]


def test_role_for_harness_writes_list_form_on_self_correction(tmp_path: Path) -> None:
    # WI-3342 IP-6: self-correction writes to the DB + projection; seed harness
    # B so the corrective role write lands (the mirror skips DB-less harnesses).
    _seed_registry(tmp_path, {"B": ("claude", [])})
    role_for_harness(
        tmp_path,
        harness_id="B",
        harness_name="claude",
        ensure_prime_on_startup=True,
    )
    assert isinstance(_projection_role(tmp_path, "B"), list)


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-legacy-scalar-read + writeback (IP-9b + IP-10)
# ──────────────────────────────────────────────────────────────────────────


def test_legacy_scalar_role_reads_as_singleton_set(tmp_path: Path) -> None:
    # WI-3342 IP-3: load_role_assignments reads the registry projection. The
    # legacy scalar role wire form is still READ-accepted: a projection record
    # carrying a scalar ``role`` normalizes to a singleton list via
    # _normalize_role_field. Seed the projection file directly to exercise
    # legacy-scalar READ tolerance (the DB writer itself always emits lists).
    _write_projection_directly(
        tmp_path,
        [
            {"id": "A", "harness_name": "codex", "role": "loyal-opposition"},
            {"id": "B", "harness_name": "claude", "role": "prime-builder"},
        ],
    )

    document = load_role_assignments(tmp_path)
    # Loader normalizes legacy scalar values into list form.
    assert document["harnesses"]["A"]["role"] == ["loyal-opposition"]
    assert document["harnesses"]["B"]["role"] == ["prime-builder"]


def test_legacy_scalar_upgrades_to_list_on_first_write(tmp_path: Path) -> None:
    """IP-10 backward-compat: every WRITE path emits list form, never scalar.

    WI-3342 IP-5/IP-6: the role-map write surface is the DB ``harnesses`` table
    (which is list-native) + the regenerated registry projection; the retired
    role-assignments.json file-writer is gone. This test pins the write-path
    list-emission contract: after a ``set_harness_role`` write, every role
    record in the regenerated projection is list form (no scalar leaks).
    """
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )

    # Trigger a write via set_harness_role.
    set_harness_role(
        tmp_path,
        ROLE_LOYAL_OPPOSITION,
        harness_id="B",
        harness_name="claude",
    )

    # B's role set is list form; A is demoted-or-carried as list form too —
    # the write path normalizes every role record to the list wire form.
    assert _projection_role(tmp_path, "B") == [ROLE_LOYAL_OPPOSITION]
    assert isinstance(_projection_role(tmp_path, "A"), list)


def test_load_role_assignments_normalizes_legacy_scalar_projection_record(
    tmp_path: Path,
) -> None:
    """IP-10 backward-compat: a legacy scalar role wire form is normalized.

    The role-set-schema migration accepts legacy scalar role values on READ
    and normalizes them to singleton lists in process. After WI-3342 the role
    map is the registry projection; this confirms a projection record carrying
    a legacy scalar ``role`` is normalized by ``load_role_assignments``.
    """
    _write_projection_directly(
        tmp_path,
        [{"id": "A", "harness_name": "codex", "role": "prime-builder"}],
    )
    document = load_role_assignments(tmp_path)
    assert document["harnesses"]["A"]["role"] == [ROLE_PRIME_BUILDER]


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-multi-element-set-single-harness-mode (single-harness topology)
# ──────────────────────────────────────────────────────────────────────────


def test_multi_element_role_set_persists_through_load(tmp_path: Path) -> None:
    """Single-harness mode: multi-element role set survives load + normalize.

    WI-3342 IP-3: load_role_assignments reads the registry projection; the
    multi-element role-set wire form (single-harness topology) must survive the
    load + normalize round-trip.
    """
    _seed_registry(
        tmp_path,
        {"B": ("claude", ["prime-builder", "loyal-opposition"])},
    )

    document = load_role_assignments(tmp_path)
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
    assert {
        ROLE_PRIME_BUILDER,
        ROLE_LOYAL_OPPOSITION,
        ROLE_ACTING_PRIME_BUILDER,
    } == VALID_ROLES_FOR_READ
    assert {ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION} == VALID_ROLES_FOR_WRITE
    assert VALID_ROLES_FOR_WRITE.issubset(VALID_ROLES_FOR_READ)
    assert ROLE_ACTING_PRIME_BUILDER in VALID_ROLES_FOR_READ
    assert ROLE_ACTING_PRIME_BUILDER not in VALID_ROLES_FOR_WRITE
