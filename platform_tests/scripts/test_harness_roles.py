from __future__ import annotations

import json
from pathlib import Path

from scripts.harness_roles import (
    ROLE_LOYAL_OPPOSITION,
    ROLE_PRIME_BUILDER,
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
