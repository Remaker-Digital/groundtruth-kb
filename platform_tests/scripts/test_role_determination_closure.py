"""Executable closure proof for WI-7311 / TEST-12296."""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "groundtruth.db"
OPERATING_ROLE = ROOT / ".harness-baseline-configuration" / "rules" / "operating-role.md"
CLAUDE_MD = ROOT / "CLAUDE.md"

CONTRADICTING_SPEC_IDS = {
    "GOV-HARNESS-ROLE-PORTABILITY-001",
    "GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001",
    "REQ-HARNESS-REGISTRY-001",
}


def _current_specs() -> dict[str, tuple[int, str]]:
    uri = f"file:{DB_PATH.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        rows = connection.execute(
            "SELECT id, version, status FROM current_specifications "
            f"WHERE id IN ({','.join('?' for _ in CONTRADICTING_SPEC_IDS)})",
            tuple(sorted(CONTRADICTING_SPEC_IDS)),
        ).fetchall()
    return {spec_id: (version, status) for spec_id, version, status in rows}


def test_contradicting_formal_records_are_no_longer_active() -> None:
    current = _current_specs()
    assert set(current) == CONTRADICTING_SPEC_IDS
    assert all(status in {"retired", "superseded"} for _, status in current.values()), current


def test_canonical_operating_role_rule_has_one_session_context_authority() -> None:
    text = OPERATING_ROLE.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "::init gtkb <pb|lo>" in text
    assert "immutable for the lifetime of that context" in lowered

    forbidden = (
        "harness-state",
        "harness-registry",
        "dispatcher/default",
        "set-role",
        "gt harness roles",
        ".gtkb-state",
        "active_role:",
    )
    assert not {token for token in forbidden if token in lowered}


def test_root_guidance_has_no_retired_role_authority_or_lookup_route() -> None:
    text = CLAUDE_MD.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "::init gtkb <pb|lo>" in text
    forbidden = (
        "roles attach to harnesses",
        "registered harness may hold this role",
        "dispatcher/default role",
        "gt harness roles",
        "gov-session-role-authority-001",
        "adr-role-authority-interactive-persistence-001",
        "dcl-interactive-session-role-persistence-001",
        "gov-harness-role-portability-001",
        "gov-gtkb-multi-harness-role-config-001",
    )
    assert not {token for token in forbidden if token in lowered}
