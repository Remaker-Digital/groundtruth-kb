"""Project name normalization and explicit single-parent membership.

Display labels never create projects or parent relationships, including on restart.
"""

from __future__ import annotations

import sys
from contextlib import closing
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB, _project_id_from_names  # noqa: E402


def test_bare_name_prefixed() -> None:
    assert _project_id_from_names("GTKB-X") == "PROJECT-GTKB-X"


def test_qualified_id_not_doubled() -> None:
    assert _project_id_from_names("PROJECT-GTKB-X") == "PROJECT-GTKB-X"


def test_subproject_bare() -> None:
    assert _project_id_from_names("GTKB-X", "SUB") == "PROJECT-GTKB-X-SUB"


def test_subproject_qualified_not_doubled() -> None:
    assert _project_id_from_names("PROJECT-GTKB-X", "SUB") == "PROJECT-GTKB-X-SUB"


def test_idempotent() -> None:
    for bare in ("GTKB-X", "PROJECT-GTKB-X", "GTKB-Y-Z", "PROJECT-GTKB-Y-Z"):
        once = _project_id_from_names(bare)
        twice = _project_id_from_names(once)
        assert once == twice, f"non-idempotent for input {bare!r}: once={once!r}, twice={twice!r}"


def test_display_labels_never_create_or_duplicate_membership(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    with closing(KnowledgeDB(db_path=db_path)) as db:
        db.insert_work_item(
            id="WI-9999",
            title="Explicit parent survives a conflicting display label",
            origin="improvement",
            component="backlog",
            resolution_status="open",
            changed_by="test",
            change_reason="seed",
            project_name="PROJECT-DISPLAY-LABEL",
        )
    with closing(KnowledgeDB(db_path=db_path)) as db:
        assert db.get_project("PROJECT-DISPLAY-LABEL") is None
        assert db._get_conn().execute("SELECT COUNT(*) FROM project_work_item_memberships").fetchone()[0] == 0
        db.insert_project("Actual parent", "test", "seed", id="PROJECT-PARENT")
        membership = db.link_project_work_item("PROJECT-PARENT", "WI-9999", "test", "explicit parent")
    with closing(KnowledgeDB(db_path=db_path)) as db:
        assert db.get_project("PROJECT-DISPLAY-LABEL") is None
        assert db.get_project_work_item_membership(membership["id"]) == membership
        rows = db._get_conn().execute("SELECT id FROM current_project_work_item_memberships").fetchall()
        assert [row["id"] for row in rows] == [membership["id"]]
