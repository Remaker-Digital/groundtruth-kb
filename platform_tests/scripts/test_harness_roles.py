from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.harness_roles import (
    ROLE_ACTING_PRIME_BUILDER,
    ROLE_LOYAL_OPPOSITION,
    ROLE_PRIME_BUILDER,
    load_role_assignments,
    role_for_harness,
    set_harness_role,
)


def _write_role_map(path: Path, harnesses: dict[str, tuple[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    harness_id: {"harness_type": harness_type, "role": role}
                    for harness_id, (harness_type, role) in harnesses.items()
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_missing_role_map_self_assigns_starting_harness_prime(tmp_path: Path) -> None:
    role_path = tmp_path / "harness-state" / "role-assignments.json"

    role, _document, path = role_for_harness(
        tmp_path,
        harness_id="A",
        harness_name="codex",
        assignment_path=role_path,
        ensure_prime_on_startup=True,
    )

    assert role == ROLE_PRIME_BUILDER
    assert path == role_path
    data = _read(role_path)
    assert data["harnesses"]["A"]["harness_type"] == "codex"
    assert data["harnesses"]["A"]["role"] == ROLE_PRIME_BUILDER


def test_startup_self_corrects_when_no_prime_is_recorded(tmp_path: Path) -> None:
    role_path = _write_role_map(
        tmp_path / "role-assignments.json",
        {
            "A": ("codex", ROLE_LOYAL_OPPOSITION),
            "B": ("claude", ROLE_LOYAL_OPPOSITION),
        },
    )

    role, _document, _path = role_for_harness(
        tmp_path,
        harness_id="B",
        harness_name="claude",
        assignment_path=role_path,
        ensure_prime_on_startup=True,
    )

    data = _read(role_path)
    assert role == ROLE_PRIME_BUILDER
    assert data["harnesses"]["B"]["role"] == ROLE_PRIME_BUILDER
    assert data["harnesses"]["A"]["role"] == ROLE_LOYAL_OPPOSITION


def test_setting_prime_demotes_other_recorded_harnesses(tmp_path: Path) -> None:
    role_path = _write_role_map(
        tmp_path / "role-assignments.json",
        {
            "A": ("codex", ROLE_LOYAL_OPPOSITION),
            "B": ("claude", ROLE_PRIME_BUILDER),
            "C": ("third", ROLE_LOYAL_OPPOSITION),
        },
    )

    role, _document, _path = set_harness_role(
        tmp_path,
        ROLE_PRIME_BUILDER,
        harness_id="A",
        harness_name="codex",
        assignment_path=role_path,
    )

    data = _read(role_path)
    assert role == ROLE_PRIME_BUILDER
    assert data["harnesses"]["A"]["role"] == ROLE_PRIME_BUILDER
    assert data["harnesses"]["B"]["role"] == ROLE_LOYAL_OPPOSITION
    assert data["harnesses"]["C"]["role"] == ROLE_LOYAL_OPPOSITION


def test_setting_loyal_can_leave_no_prime_until_next_startup(tmp_path: Path) -> None:
    role_path = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", ROLE_PRIME_BUILDER), "B": ("claude", ROLE_LOYAL_OPPOSITION)},
    )

    set_harness_role(
        tmp_path,
        ROLE_LOYAL_OPPOSITION,
        harness_id="A",
        harness_name="codex",
        assignment_path=role_path,
    )
    data = _read(role_path)
    assert all(record["role"] != ROLE_PRIME_BUILDER for record in data["harnesses"].values())

    role, _document, _path = role_for_harness(
        tmp_path,
        harness_id="B",
        harness_name="claude",
        assignment_path=role_path,
        ensure_prime_on_startup=True,
    )

    data = _read(role_path)
    assert role == ROLE_PRIME_BUILDER
    assert data["harnesses"]["A"]["role"] == ROLE_LOYAL_OPPOSITION
    assert data["harnesses"]["B"]["role"] == ROLE_PRIME_BUILDER


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
    be a new role-switch target.
    """
    role_path = tmp_path / "harness-state" / "role-assignments.json"

    with pytest.raises(ValueError, match="Unsupported next-session role"):
        set_harness_role(
            tmp_path,
            ROLE_ACTING_PRIME_BUILDER,
            harness_id="A",
            harness_name="codex",
            assignment_path=role_path,
        )


def test_t_compat_2_load_role_assignments_reads_existing_acting_prime_value(tmp_path: Path) -> None:
    """T-compat-2: load_role_assignments accepts an existing acting-prime-builder
    value without raising.

    Per GOV-ACTING-PRIME-BUILDER-001 (legacy compatibility framing). Pre-
    existing role-map entries with acting-prime-builder must continue to load.
    """
    role_path = _write_role_map(
        tmp_path / "harness-state" / "role-assignments.json",
        {
            "A": ("codex", ROLE_ACTING_PRIME_BUILDER),
            "B": ("claude", ROLE_PRIME_BUILDER),
        },
    )

    document = load_role_assignments(tmp_path, assignment_path=role_path)
    assert document["harnesses"]["A"]["role"] == ROLE_ACTING_PRIME_BUILDER, (
        "Existing acting-prime-builder role-map value must read without error "
        "for backward compatibility."
    )
    assert document["harnesses"]["B"]["role"] == ROLE_PRIME_BUILDER
