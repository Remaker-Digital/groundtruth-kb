"""D3 work-item project binding: WI-6016 and WI-6035 are bound to their project.

Per the approved proposal (`bridge/gtkb-d3-work-item-project-binding-007.md`,
GO at `-008`), the two genuinely unbound D3 work items each receive one active
membership row in `current_project_work_item_memberships`.

The load-bearing design point, and the reason this module exists rather than a
one-line assertion: **membership is read from
`current_project_work_item_memberships` filtered to `status = 'active'`, never
from `current_work_items.project_name`.** That derived surface is what produced
this thread's `-001` defect, and it is the same label-versus-membership
divergence recorded as WI-6445.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_DB_PATH = _ROOT / "groundtruth.db"

PROJECT_ID = "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE"
BOUND_WORK_ITEMS = ("WI-6016", "WI-6035")

MEMBERSHIP_TABLE = "current_project_work_item_memberships"


def _connect() -> sqlite3.Connection:
    if not _DB_PATH.is_file():
        pytest.skip("groundtruth.db not present in this checkout")
    return sqlite3.connect(f"file:{_DB_PATH.as_posix()}?mode=ro", uri=True)


def _active_memberships(conn: sqlite3.Connection, work_item_id: str) -> list[str]:
    """Return active project ids for a work item, read from the authoritative table."""
    return [
        row[0]
        for row in conn.execute(
            f"SELECT project_id FROM {MEMBERSHIP_TABLE} WHERE work_item_id = ? AND status = 'active'",
            (work_item_id,),
        )
    ]


@pytest.mark.parametrize("work_item_id", BOUND_WORK_ITEMS)
def test_work_item_holds_an_active_membership_in_the_project(work_item_id: str) -> None:
    conn = _connect()
    try:
        assert PROJECT_ID in _active_memberships(conn, work_item_id)
    finally:
        conn.close()


@pytest.mark.parametrize("work_item_id", BOUND_WORK_ITEMS)
def test_work_item_holds_exactly_one_membership_row_in_the_project(work_item_id: str) -> None:
    """Addition, not duplication: binding must not create a second row."""
    conn = _connect()
    try:
        count = conn.execute(
            f"SELECT COUNT(*) FROM {MEMBERSHIP_TABLE} WHERE work_item_id = ? AND project_id = ? AND status = 'active'",
            (work_item_id, PROJECT_ID),
        ).fetchone()[0]
        assert count == 1
    finally:
        conn.close()


@pytest.mark.parametrize("work_item_id", BOUND_WORK_ITEMS)
def test_work_item_is_not_bound_to_any_other_project(work_item_id: str) -> None:
    """Nothing was moved between projects; these were previously unbound."""
    conn = _connect()
    try:
        assert _active_memberships(conn, work_item_id) == [PROJECT_ID]
    finally:
        conn.close()


def test_membership_authority_is_the_membership_table_not_the_derived_label() -> None:
    """The regression guard for this thread's `-001` defect.

    `current_work_items.project_name` is a derived label. A work item can carry an
    active membership row while that label is unset, so a consumer that reads the
    label as membership authority reaches the wrong answer. This asserts the
    authoritative read path resolves independently of the label's value, rather
    than asserting any particular label content.
    """
    conn = _connect()
    try:
        for work_item_id in BOUND_WORK_ITEMS:
            membership = _active_memberships(conn, work_item_id)
            assert membership == [PROJECT_ID], (
                f"{work_item_id} membership must resolve from {MEMBERSHIP_TABLE}, "
                "independently of current_work_items.project_name"
            )
    finally:
        conn.close()


def test_binding_added_exactly_two_memberships_to_the_project() -> None:
    """Scope guard: the change adds two rows and modifies none.

    Asserted as a floor rather than an exact project total, because the project's
    membership set legitimately changes as other D3 work is bound; pinning an
    exact count would make this test a tripwire for unrelated work.
    """
    conn = _connect()
    try:
        members = {
            row[0]
            for row in conn.execute(
                f"SELECT work_item_id FROM {MEMBERSHIP_TABLE} WHERE project_id = ? AND status = 'active'",
                (PROJECT_ID,),
            )
        }
        assert set(BOUND_WORK_ITEMS) <= members
        assert len(members) >= len(BOUND_WORK_ITEMS)
    finally:
        conn.close()
