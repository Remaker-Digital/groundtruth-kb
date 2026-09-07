"""The project authorization field is named for what it holds (WI-7706).

``projects.activation_status`` always carried authorization values -- ``authorized`` and
``not authorized`` -- under a name describing activation. Canon section 1 holds the two concepts
distinct: activation is the mechanical consequence of the project commit; authorization is the
owner's prior approval to proceed. ``GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`` v5 names this
field as the authorization record.

The mismatch was not cosmetic. It produced a live misreading during the session that filed this
work: a check searching ``PRAGMA table_info(projects)`` for a column whose *name* contained
``authoriz`` reported the field absent while it was present and populated across 617 projects.

Bound to TEST-12597.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.db import _VALID_AUTHORIZATION_VALUES, KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def project_columns(tmp_path_factory: pytest.TempPathFactory) -> set[str]:
    db = KnowledgeDB(tmp_path_factory.mktemp("authz") / "probe.db")
    conn = db._get_conn()
    return {row[1] for row in conn.execute("PRAGMA table_info(projects)").fetchall()}


def test_authorization_column_named_authorization_and_agent_red_untouched(project_columns: set[str]) -> None:
    """The canonical name is ``authorization``; the retired name is gone from the schema."""
    assert "authorization" in project_columns, "the project row must carry an 'authorization' column"
    assert "activation_status" not in project_columns, "the retired name must not survive alongside the new one"


def test_the_field_still_holds_only_the_two_canonical_values(project_columns: set[str]) -> None:
    """Renaming must not widen the contract.

    The rename is a naming correction. If it also admitted a third state it would be a semantic
    change wearing a rename's clothes.
    """
    assert {"authorized", "not authorized"} == _VALID_AUTHORIZATION_VALUES


def test_a_fresh_project_defaults_to_authorized(tmp_path: Path) -> None:
    """Canon section 3: new projects are created ``authorized``."""
    conn = KnowledgeDB(tmp_path / "default.db")._get_conn()
    conn.execute(
        "INSERT INTO projects (id, version, name, changed_by, changed_at, change_reason) "
        "VALUES ('PROJECT-AUTHZ-DEFAULT', 1, 'probe', 'test', '2026-09-04', 'probe')"
    )
    value = conn.execute("SELECT authorization FROM projects WHERE id = 'PROJECT-AUTHZ-DEFAULT'").fetchone()[0]
    assert value == "authorized"


def test_the_adopter_keeps_its_own_unrelated_field() -> None:
    """Agent Red's ``activation_status`` is tenant activation, not project authorization.

    Renaming it would break the reference adopter, so the platform rename stops at that boundary.
    Asserted rather than left to convention, because a future repository-wide rename is exactly the
    change that would cross it by accident.
    """
    adopter = REPO_ROOT / "applications" / "Agent_Red"
    if not adopter.is_dir():
        pytest.skip("adopter subtree not present in this checkout")
    preserved = [
        p for p in adopter.rglob("*.py") if "activation_status" in p.read_text(encoding="utf-8", errors="replace")
    ]
    assert preserved, "Agent Red's tenant activation_status must not have been renamed by platform work"
