#!/usr/bin/env python
"""FAB-11 pytest evidence contract migration.

This tool performs the GOV-12/GOV-13 amendment and MemBase test-evidence
scoping approved by ``gtkb-fab-11-regression-signal-revival``. It is intentionally
idempotent: repeated ``--apply`` runs keep the same semantic state.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GTKB_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(GTKB_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.governance.approval_packet import (  # noqa: E402
    construct_approval_packet,
    validate_packet,
)

BRIDGE_ID = "gtkb-fab-11-regression-signal-revival"
SOURCE_REF = "bridge/gtkb-fab-11-regression-signal-revival-003.md"
OWNER_DECISION = "DELIB-FAB11-REMEDIATION-20260610B / PAUTH-FAB11-20260610"
CHANGED_BY = "prime-builder/codex"
HISTORICAL_RESULT = "historical_agent_red"
HISTORICAL_CUTOFF = "2026-05-01T00:00:00+00:00"
TARGET_SPECS = ("GOV-12", "GOV-13")

LIVE_TEST_EVIDENCE_VIEW_SQL = """
CREATE VIEW kpi_spec_test_mapping AS
WITH live_test_evidence AS (
    SELECT DISTINCT spec_id FROM test_coverage
    UNION
    SELECT DISTINCT spec_id FROM current_tests
    WHERE test_file IS NOT NULL
      AND TRIM(test_file) != ''
      AND COALESCE(last_result, '') NOT IN ('stale', 'historical_agent_red')
)
SELECT
    COUNT(DISTINCT s.id) AS total_specifications,
    SUM(CASE WHEN t.spec_id IS NOT NULL THEN 1 ELSE 0 END) AS mapped_specifications,
    SUM(CASE WHEN t.spec_id IS NULL THEN 1 ELSE 0 END) AS unmapped_specifications,
    (SUM(CASE WHEN t.spec_id IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT s.id)) AS spec_test_mapping_percentage
FROM current_specifications s
LEFT JOIN live_test_evidence t ON s.id = t.spec_id
WHERE s.status != 'retired'
"""


@dataclass(frozen=True)
class SpecAmendment:
    spec_id: str
    packet_path: str
    new_description: str


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _now_date() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _append_amendment(description: str | None, spec_id: str) -> str:
    marker = "FAB-11 pytest evidence amendment"
    base = (description or "").rstrip()
    if marker in base:
        return base
    if spec_id == "GOV-12":
        addition = (
            "FAB-11 pytest evidence amendment (2026-06-12): work-item creation still "
            "initiates test planning, but current repository-native pytest files and "
            "their execution output are governed verification evidence. Historical "
            "MemBase `tests` rows imported from Agent Red before application isolation "
            "are app-scoped history and must not be counted as live pass evidence unless "
            "refreshed by a current execution record."
        )
    else:
        addition = (
            "FAB-11 pytest evidence amendment (2026-06-12): phase assignment remains "
            "required for governed test artifacts, and repository-native pytest coverage "
            "mappings may satisfy live spec-to-test visibility. Historical Agent Red "
            "MemBase `tests` rows are retained for provenance but are excluded from live "
            "KPI pass-evidence counts."
        )
    return f"{base}\n\n{addition}".strip()


def _packet_path(spec_id: str, date_text: str) -> Path:
    safe_id = spec_id.lower().replace("-", "-")
    return PROJECT_ROOT / ".groundtruth" / "formal-artifact-approvals" / (
        f"{date_text}-fab11-{safe_id}-pytest-evidence.json"
    )


def plan_spec_amendments(db: KnowledgeDB, date_text: str) -> list[SpecAmendment]:
    amendments: list[SpecAmendment] = []
    for spec_id in TARGET_SPECS:
        spec = db.get_spec(spec_id)
        if spec is None:
            raise RuntimeError(f"{spec_id} not found")
        new_description = _append_amendment(spec.get("description"), spec_id)
        packet_path = _packet_path(spec_id, date_text)
        amendments.append(
            SpecAmendment(
                spec_id=spec_id,
                packet_path=packet_path.relative_to(PROJECT_ROOT).as_posix(),
                new_description=new_description,
            )
        )
    return amendments


def write_packet(spec: dict[str, Any], amendment: SpecAmendment, packet_path: Path) -> dict[str, object]:
    packet = construct_approval_packet(
        artifact_type=spec["type"],
        artifact_id=amendment.spec_id,
        action="update",
        source_ref=SOURCE_REF,
        full_content=amendment.new_description,
        approval_mode="approve",
        presented_to_user=True,
        transcript_captured=True,
        explicit_change_request=(
            f"{OWNER_DECISION}: amend {amendment.spec_id} to recognize pytest execution "
            "and pytest coverage mappings as current governed verification evidence."
        ),
        changed_by=CHANGED_BY,
        change_reason=f"{BRIDGE_ID}: pytest evidence contract amendment",
        approved_by="owner",
    )
    validation = validate_packet(packet)
    if not validation.is_valid:
        raise RuntimeError("; ".join(validation.errors))
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return packet


def _historical_test_rows(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """SELECT id FROM current_tests
           WHERE last_result IN ('pass', 'fail')
           AND changed_at < ?
           ORDER BY id""",
        (HISTORICAL_CUTOFF,),
    ).fetchall()
    return [row["id"] for row in rows]


def _apply_historical_test_scope(db: KnowledgeDB, test_ids: list[str], *, max_tests: int | None) -> int:
    applied = 0
    for test_id in test_ids:
        if max_tests is not None and applied >= max_tests:
            break
        current = db.get_test(test_id)
        if current is None or current.get("last_result") == HISTORICAL_RESULT:
            continue
        description = (current.get("description") or "").rstrip()
        note = (
            "FAB-11: retained as historical Agent Red MemBase test evidence; "
            "not counted as live pytest pass evidence."
        )
        if note not in description:
            description = f"{description}\n\n{note}".strip()
        db.update_test(
            test_id,
            changed_by=CHANGED_BY,
            change_reason=f"{BRIDGE_ID}: scope pre-isolation tests table row to Agent Red history",
            last_result=HISTORICAL_RESULT,
            description=description,
        )
        applied += 1
    return applied


def _migrate_view(conn: sqlite3.Connection) -> None:
    conn.execute("DROP VIEW IF EXISTS kpi_spec_test_mapping")
    conn.execute(LIVE_TEST_EVIDENCE_VIEW_SQL)
    conn.commit()


def apply(db_path: Path, *, date_text: str, max_tests: int | None = None) -> dict[str, Any]:
    db = KnowledgeDB(db_path=db_path)
    try:
        amendments = plan_spec_amendments(db, date_text)
        packets: list[str] = []
        amended_specs = 0
        for amendment in amendments:
            spec = db.get_spec(amendment.spec_id)
            if spec is None:
                raise RuntimeError(f"{amendment.spec_id} not found")
            packet_path = PROJECT_ROOT / amendment.packet_path
            write_packet(spec, amendment, packet_path)
            packets.append(amendment.packet_path)
            if spec.get("description") != amendment.new_description:
                db.update_spec(
                    amendment.spec_id,
                    changed_by=CHANGED_BY,
                    change_reason=(
                        f"{BRIDGE_ID}: pytest evidence contract amendment; "
                        f"approval packet {amendment.packet_path}"
                    ),
                    description=amendment.new_description,
                    validate_assertions=False,
                )
                amended_specs += 1

        conn = _connect(db_path)
        try:
            test_ids = _historical_test_rows(conn)
            _migrate_view(conn)
        finally:
            conn.close()
        historical_tests_applied = _apply_historical_test_scope(db, test_ids, max_tests=max_tests)
    finally:
        db.close()

    return {
        "bridge_id": BRIDGE_ID,
        "applied": True,
        "amended_specs": amended_specs,
        "approval_packets": packets,
        "historical_tests_planned": len(test_ids),
        "historical_tests_applied": historical_tests_applied,
        "max_tests": max_tests,
        "view_migrated": True,
    }


def dry_run(db_path: Path, *, date_text: str) -> dict[str, Any]:
    db = KnowledgeDB(db_path=db_path)
    try:
        amendments = plan_spec_amendments(db, date_text)
        conn = _connect(db_path)
        try:
            test_ids = _historical_test_rows(conn)
            current_view = conn.execute("SELECT * FROM kpi_spec_test_mapping").fetchone()
        finally:
            conn.close()
    finally:
        db.close()
    return {
        "bridge_id": BRIDGE_ID,
        "applied": False,
        "spec_amendments": [amendment.__dict__ for amendment in amendments],
        "historical_tests_planned": len(test_ids),
        "current_kpi_spec_test_mapping": dict(current_view) if current_view else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=PROJECT_ROOT / "groundtruth.db")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--date", default=_now_date())
    parser.add_argument("--max-tests", type=int)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()

    result = apply(args.db, date_text=args.date, max_tests=args.max_tests) if args.apply else dry_run(args.db, date_text=args.date)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
