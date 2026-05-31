"""Tests for the standing-backlog health doctor check."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.doctor import check_standing_backlog_health


def _write_bridge_index(
    root: Path, document: str = "clean-thread", status: str = "VERIFIED", date: str = "2026-05-19"
) -> None:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    version_path = bridge_dir / f"{document}-001.md"
    version_path.write_text(f"{status}\n\n# {document}\n\nDate: {date} UTC\n", encoding="utf-8")
    (bridge_dir / "INDEX.md").write_text(
        f"# Bridge Index\n\nDocument: {document}\n{status}: bridge/{document}-001.md\n",
        encoding="utf-8",
    )


def _insert_open_work_item(root: Path, work_item_id: str = "WI-ORPHAN") -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_work_item(
            work_item_id,
            f"Work item {work_item_id}",
            "hygiene",
            "backlog",
            "open",
            "test",
            "seed",
        )
    finally:
        db.close()


def _insert_authorized_open_work_item(root: Path, work_item_id: str = "WI-COVERED") -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-AUTH-SEED",
            "owner_conversation",
            "Owner approved authorization",
            "Owner approved PROJECT-X authorization.",
            "{}",
            "test",
            "seed",
            outcome="owner_decision",
        )
        db.insert_project("Project X", "test", "seed", id="PROJECT-X", status="active")
        db.insert_spec(
            id="SPEC-SEED",
            title="Seed spec",
            status="verified",
            changed_by="test",
            change_reason="seed",
        )
        db.insert_work_item(
            work_item_id,
            f"Work item {work_item_id}",
            "hygiene",
            "backlog",
            "open",
            "test",
            "seed",
        )
        db.link_project_work_item("PROJECT-X", work_item_id, "test", "seed")
        db.insert_project_authorization(
            "PROJECT-X",
            "Primary authorization",
            "DELIB-AUTH-SEED",
            "Bounded scope.",
            "test",
            "seed",
            id="PAUTH-X",
            status="active",
            included_work_item_ids=[work_item_id],
            included_spec_ids=["SPEC-SEED"],
        )
    finally:
        db.close()


def test_doctor_finds_orphaned_wis(tmp_path: Path) -> None:
    _write_bridge_index(tmp_path)
    _insert_open_work_item(tmp_path)

    payload = check_standing_backlog_health(tmp_path)

    assert payload["status"] == "warning"
    assert payload["summary"]["orphaned_wi_count"] == 1
    finding = payload["findings"][0]
    assert finding["kind"] == "orphaned-WI"
    assert finding["severity"] == "WARN"
    assert finding["work_item_id"] == "WI-ORPHAN"


def test_doctor_detects_stale_no_go(tmp_path: Path) -> None:
    KnowledgeDB(db_path=tmp_path / "groundtruth.db").close()
    _write_bridge_index(tmp_path, document="stale-thread", status="NO-GO", date="2026-05-01")

    payload = check_standing_backlog_health(
        tmp_path,
        stale_no_go_days=7,
        now=datetime(2026, 5, 20, tzinfo=UTC),
    )

    assert payload["status"] == "warning"
    assert payload["summary"]["stale_no_go_count"] == 1
    finding = payload["findings"][0]
    assert finding["kind"] == "stale-NO-GO"
    assert finding["severity"] == "WARN"
    assert finding["document"] == "stale-thread"
    assert finding["age_days"] == 19


def test_doctor_severity_classification(tmp_path: Path) -> None:
    _insert_open_work_item(tmp_path)

    payload = check_standing_backlog_health(tmp_path)

    severities_by_kind = {finding["kind"]: finding["severity"] for finding in payload["findings"]}
    assert severities_by_kind["orphaned-WI"] == "WARN"
    assert severities_by_kind["missing-evidence"] == "FAIL"
    assert payload["status"] == "fail"


def test_clean_state_no_findings(tmp_path: Path) -> None:
    _write_bridge_index(tmp_path)
    _insert_authorized_open_work_item(tmp_path)

    payload = check_standing_backlog_health(tmp_path)

    assert payload["status"] == "pass"
    assert payload["summary"]["finding_count"] == 0
    assert payload["findings"] == []


def test_json_output_schema(tmp_path: Path) -> None:
    _write_bridge_index(tmp_path)
    _insert_open_work_item(tmp_path)

    payload = check_standing_backlog_health(tmp_path)

    assert {
        "schema_version",
        "check",
        "status",
        "threshold_days",
        "summary",
        "findings",
    } <= set(payload)
    assert {
        "finding_count",
        "fail_count",
        "warn_count",
        "orphaned_wi_count",
        "stale_no_go_count",
        "missing_evidence_count",
    } <= set(payload["summary"])
