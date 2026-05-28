from __future__ import annotations

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

from scripts.harness_roles import (  # noqa: E402
    ROLE_ACTING_PRIME_BUILDER,
    ROLE_LOYAL_OPPOSITION,
    ROLE_PRIME_BUILDER,
    load_role_assignments,
    role_for_harness,
    set_harness_role,
)

# ---------------------------------------------------------------------------
# WI-3342 IP-6 — registry-backed reader/writer fixtures.
#
# scripts/harness_roles.py was migrated off the legacy
# harness-state/role-assignments.json: load_role_assignments reads the
# DB-backed registry projection (harness-state/harness-registry.json), and the
# writers (set_harness_role, role_for_harness self-correction) mutate the DB
# ``harnesses`` table via _mirror_role_assignments_to_registry, then regenerate
# the projection. _mirror_role_assignments_to_registry is a graceful no-op when
# no groundtruth.db is present and SKIPS any harness with no current DB row, so
# writer tests must seed a real DB with the test harnesses first.
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
            change_reason="WI-3342 IP-6 harness_roles fixture",
            status="active",
        )
    generate_harness_projection(db, root)


def _role_of(root: Path, harness_id: str) -> Any:
    """Return the role-set list recorded for ``harness_id`` in the role map.

    The role map is the registry projection per the IP-3/IP-5 migration; the
    foundational reader ``load_role_assignments`` resolves it to the
    ``{harness_id: {"role": [...]}}`` document shape.
    """
    document = load_role_assignments(root)
    return document["harnesses"][harness_id]["role"]


def test_missing_role_map_self_assigns_starting_harness_prime(tmp_path: Path) -> None:
    # No registry harnesses seeded for harness A: load_role_assignments yields
    # an empty document, role_for_harness self-corrects this harness to Prime.
    # The starting harness must be present in the DB so the corrective role
    # write lands in the registry (the mirror skips harnesses with no DB row).
    _seed_registry(tmp_path, {"A": ("codex", [])})

    role, _document, _path = role_for_harness(
        tmp_path,
        harness_id="A",
        harness_name="codex",
        ensure_prime_on_startup=True,
    )

    assert role == ROLE_PRIME_BUILDER
    # Role-set wire form per IP-8 of gtkb-single-harness-bridge-dispatcher-001:
    # WRITE always emits JSON list; singleton list represents the multi-harness
    # case. WI-3342 IP-5: the post-write role surface is the registry
    # projection, not the retired role-assignments.json.
    assert _role_of(tmp_path, "A") == [ROLE_PRIME_BUILDER]


def test_startup_self_corrects_when_no_prime_is_recorded(tmp_path: Path) -> None:
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_LOYAL_OPPOSITION]),
        },
    )

    role, _document, _path = role_for_harness(
        tmp_path,
        harness_id="B",
        harness_name="claude",
        ensure_prime_on_startup=True,
    )

    assert role == ROLE_PRIME_BUILDER
    assert _role_of(tmp_path, "B") == [ROLE_PRIME_BUILDER]
    assert _role_of(tmp_path, "A") == [ROLE_LOYAL_OPPOSITION]


def test_setting_prime_demotes_other_recorded_harnesses(tmp_path: Path) -> None:
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
            "C": ("third", [ROLE_LOYAL_OPPOSITION]),
        },
    )

    role, _document, _path = set_harness_role(
        tmp_path,
        ROLE_PRIME_BUILDER,
        harness_id="A",
        harness_name="codex",
    )

    assert role == ROLE_PRIME_BUILDER
    assert _role_of(tmp_path, "A") == [ROLE_PRIME_BUILDER]
    assert _role_of(tmp_path, "B") == [ROLE_LOYAL_OPPOSITION]
    assert _role_of(tmp_path, "C") == [ROLE_LOYAL_OPPOSITION]


def test_setting_loyal_can_leave_no_prime_until_next_startup(tmp_path: Path) -> None:
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_PRIME_BUILDER]),
            "B": ("claude", [ROLE_LOYAL_OPPOSITION]),
        },
    )

    set_harness_role(
        tmp_path,
        ROLE_LOYAL_OPPOSITION,
        harness_id="A",
        harness_name="codex",
    )
    document = load_role_assignments(tmp_path)
    # No harness's role-set contains prime-builder after the set-LO update.
    assert all(ROLE_PRIME_BUILDER not in record.get("role", []) for record in document["harnesses"].values())

    role, _document, _path = role_for_harness(
        tmp_path,
        harness_id="B",
        harness_name="claude",
        ensure_prime_on_startup=True,
    )

    assert role == ROLE_PRIME_BUILDER
    assert _role_of(tmp_path, "A") == [ROLE_LOYAL_OPPOSITION]
    assert _role_of(tmp_path, "B") == [ROLE_PRIME_BUILDER]


# ---------------------------------------------------------------------------
# Acting-Prime compatibility contract (T-compat-1, T-compat-2)
# Per bridge gtkb-role-session-lifecycle-simplification-003.md GO at -004:
#   Slice B classifies acting-prime-builder as legacy/provenance language.
#   set_harness_role must REJECT it as a SET target; load_role_assignments
#   must accept it as a READ value.
# ---------------------------------------------------------------------------


def test_t_compat_1_set_harness_role_rejects_acting_prime_builder(tmp_path: Path) -> None:
    """T-compat-1: scripts/harness_roles.py set-role rejects acting-prime-builder.

    Per GOV-HARNESS-ROLE-PORTABILITY-001 (two-role canonical set: prime-builder
    + loyal-opposition). acting-prime-builder is legacy/provenance and cannot
    be a new role-switch target. The rejection is SET-token validation that
    fires before any registry read, so no DB fixture is required.
    """
    # Per IP-8 of gtkb-single-harness-bridge-dispatcher-001 (Codex GO at -014),
    # the error message is now specific: it explicitly identifies
    # acting-prime-builder as a READ-only compatibility/provenance value rather
    # than falling through to the generic "Unsupported next-session role"
    # path. Match against the specific message so future hardening of the
    # generic error path does not silently regress this contract.
    with pytest.raises(ValueError, match="acting-prime-builder is a READ-only"):
        set_harness_role(
            tmp_path,
            ROLE_ACTING_PRIME_BUILDER,
            harness_id="A",
            harness_name="codex",
        )


def test_t_compat_2_load_role_assignments_reads_existing_acting_prime_value(tmp_path: Path) -> None:
    """T-compat-2: load_role_assignments accepts an existing acting-prime-builder
    value without raising.

    Per GOV-ACTING-PRIME-BUILDER-001 (legacy compatibility framing). Pre-
    existing role-map entries with acting-prime-builder must continue to load.
    WI-3342 IP-3: load_role_assignments reads the registry projection.
    """
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_ACTING_PRIME_BUILDER]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )

    document = load_role_assignments(tmp_path)
    # Per IP-8 of gtkb-single-harness-bridge-dispatcher-001: legacy scalar
    # values are accepted on READ and normalized into singleton lists per
    # _role_set_to_json. The compatibility/provenance value
    # acting-prime-builder remains in the READ vocabulary but normalizes to
    # a singleton list.
    assert document["harnesses"]["A"]["role"] == [ROLE_ACTING_PRIME_BUILDER], (
        "Existing acting-prime-builder role-map value must read without error "
        "for backward compatibility (now as singleton list per role-set schema)."
    )
    assert document["harnesses"]["B"]["role"] == [ROLE_PRIME_BUILDER]
