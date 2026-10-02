"""c123 (batch design WP5, G35; WI-7358): the terminal work-item reopen primitive is gone.

``KnowledgeDB.reopen_terminal_work_item`` was a legacy SQLite write path that outlived the cutover to the native
authority; only tests called it, and its gates cited retired approval concepts. It is deleted with no replacement. The
native authority has no reopen path (amend, move and retire refuse an item that is not open; covered by
test_native_work_item_amendments.py and test_native_work_item_retirement.py), and a resolved SQLite work item cannot
be moved back to an earlier stage through ``update_work_item``.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB


def test_knowledge_db_offers_no_terminal_reopen() -> None:
    assert callable(getattr(KnowledgeDB, "update_work_item", None)), "control: the ordinary work-item writer exists"
    assert not hasattr(KnowledgeDB, "reopen_terminal_work_item")
    assert not [name for name in dir(KnowledgeDB) if "reopen" in name.lower()]


@pytest.mark.parametrize("earlier_stage", ["created", "tested", "backlogged", "implementing"])
def test_a_resolved_work_item_cannot_move_back_through_update(tmp_path: Path, earlier_stage: str) -> None:
    db = KnowledgeDB(db_path=tmp_path / "kb.db")
    try:
        db.insert_work_item(
            id="WI-RESOLVED-1",
            title="Resolved",
            origin="new",
            component="core",
            resolution_status="resolved",
            changed_by="test",
            change_reason="create",
            stage="resolved",
        )
        history = db.get_work_item_history("WI-RESOLVED-1")

        with pytest.raises(ValueError, match="Invalid stage transition"):
            db.update_work_item("WI-RESOLVED-1", "test", "move back", stage=earlier_stage)

        assert db.get_work_item_history("WI-RESOLVED-1") == history
        assert db.get_work_item("WI-RESOLVED-1")["stage"] == "resolved"
    finally:
        db.close()
