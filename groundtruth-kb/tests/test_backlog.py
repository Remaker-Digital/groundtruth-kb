"""Tests for unified backlog migration helpers."""

from __future__ import annotations

from groundtruth_kb.backlog import migrate_work_list_items, parse_work_list_markdown
from groundtruth_kb.db import KnowledgeDB

SAMPLE_WORK_LIST = "\n".join(
    [
        "| # | ID | Status | Blocks / blocked by | Next step |",
        "|---|---|---|---|---|",
        (
            "| 0 | `GTKB-DASHBOARD-002` Slice 2.3 | **P0 OWNER-ELEVATED** | "
            "See `GTKB-OTHER-001`; bridge/example-001.md; DELIB-S1; GOV-TEST-001. | "
            "Review implementation. |"
        ),
        "| 1 | `GTKB-DASHBOARD-002` Slice 2.2 | blocked | Waiting on owner. | Resume later. |",
        "| 2 | `GTKB-COMMIT-TRIAGE-001` | **DONE - VERIFIED** | None. | Move to completed. |",
    ]
)


def test_parse_work_list_markdown_preserves_duplicate_project_rows() -> None:
    items = parse_work_list_markdown(SAMPLE_WORK_LIST)

    assert [item.work_item_id for item in items] == [
        "GTKB-DASHBOARD-002-SLICE-2-3",
        "GTKB-DASHBOARD-002-SLICE-2-2",
        "GTKB-COMMIT-TRIAGE-001",
    ]
    assert items[0].project_name == "GTKB-DASHBOARD-002"
    assert items[0].subproject_name == "Slice 2.3"
    assert items[0].priority == "P0"
    assert items[0].related_bridge_threads == ("bridge/example-001.md",)
    assert items[0].related_deliberation_ids == ("DELIB-S1",)
    assert items[0].related_spec_ids_at_creation == ("GOV-TEST-001",)
    assert "GTKB-OTHER-001" in items[0].depends_on_work_items
    assert items[2].resolution_status == "verified"


def test_migrate_work_list_items_inserts_missing_rows(db: KnowledgeDB) -> None:
    db.insert_work_item(
        id="GTKB-COMMIT-TRIAGE-001",
        title="Existing item",
        origin="hygiene",
        component="backlog",
        resolution_status="open",
        changed_by="test",
        change_reason="setup",
    )

    items = parse_work_list_markdown(SAMPLE_WORK_LIST)
    result = migrate_work_list_items(
        db,
        items,
        changed_by="test",
        change_reason="migrate test work list",
    )

    assert result.parsed == 3
    assert result.inserted == ("GTKB-DASHBOARD-002-SLICE-2-3", "GTKB-DASHBOARD-002-SLICE-2-2")
    assert result.updated_existing == ("GTKB-COMMIT-TRIAGE-001",)
    assert result.skipped_existing == ()

    migrated = db.get_work_item("GTKB-DASHBOARD-002-SLICE-2-3")
    assert migrated is not None
    assert migrated["project_name"] == "GTKB-DASHBOARD-002"
    assert migrated["implementation_order"] == 0
    assert migrated["status_detail"] == "P0 OWNER-ELEVATED"
    assert migrated["related_bridge_threads_parsed"] == ["bridge/example-001.md"]

    enriched = db.get_work_item("GTKB-COMMIT-TRIAGE-001")
    assert enriched is not None
    assert enriched["implementation_order"] == 2
    assert enriched["status_detail"] == "DONE - VERIFIED"
