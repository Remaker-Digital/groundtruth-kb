"""FAB-18 regression coverage for backlog dignity metric calibration."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.doctor import check_standing_backlog_health


def _write_bridge_index(root: Path) -> None:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / "clean-thread-001.md").write_text(
        "VERIFIED\n\n# clean-thread\n\nDate: 2026-06-12 UTC\n",
        encoding="utf-8",
    )
    (bridge_dir / "INDEX.md").write_text(
        "Document: clean-thread\nVERIFIED: bridge/clean-thread-001.md\n",
        encoding="utf-8",
    )


def _insert_open_work_item(root: Path, item_id: str, *, approval_state: str) -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_work_item(
            item_id,
            f"Work item {item_id}",
            "hygiene",
            "backlog",
            "open",
            "test",
            "seed",
            approval_state=approval_state,
        )
    finally:
        db.close()


def test_unapproved_future_wi_without_pauth_is_not_doctor_warn(tmp_path: Path) -> None:
    _write_bridge_index(tmp_path)
    _insert_open_work_item(tmp_path, "WI-FUTURE", approval_state="unapproved")

    payload = check_standing_backlog_health(tmp_path)

    assert payload["status"] == "pass"
    assert payload["summary"]["orphaned_wi_count"] == 0
    assert payload["summary"]["non_implementation_uncovered_count"] == 1
    assert payload["findings"] == []


def test_implementation_authorized_wi_without_pauth_still_warns(tmp_path: Path) -> None:
    _write_bridge_index(tmp_path)
    _insert_open_work_item(tmp_path, "WI-ACTIVE", approval_state="implementation_authorized")

    payload = check_standing_backlog_health(tmp_path)

    assert payload["status"] == "warning"
    assert payload["summary"]["orphaned_wi_count"] == 1
    assert payload["findings"][0]["work_item_id"] == "WI-ACTIVE"
    assert payload["findings"][0]["approval_state"] == "implementation_authorized"
