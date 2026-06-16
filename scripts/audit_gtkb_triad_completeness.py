#!/usr/bin/env python3
"""Audit GT-KB specification/test/implementation triad completeness.

The audit is intentionally independent of adopter application test suites. It
reads the GT-KB knowledge database and bridge files, then reports gaps that
must be backfilled from historical evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "groundtruth.db"
DEFAULT_BRIDGE_DIR = PROJECT_ROOT / "bridge"
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TERMINAL_SPEC_STATUSES = {"implemented", "verified"}
BRIDGE_TERMINAL_STATUSES = {"GO", "VERIFIED"}
SPEC_LINK_RE = re.compile(r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9_.-]*\b")
SECTION_RE_TEMPLATE = r"(?im)^##\s+{heading}\s*$"


@dataclass(frozen=True)
class Gap:
    """A single triad-completeness gap."""

    kind: str
    severity: str
    artifact_id: str
    artifact_path: str | None
    detail: str


def _json_loads(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _latest_specs(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT s.*
        FROM specifications s
        INNER JOIN (
            SELECT id, MAX(version) AS max_version
            FROM specifications
            GROUP BY id
        ) latest
        ON s.id = latest.id AND s.version = latest.max_version
        ORDER BY s.id
        """
    ).fetchall()


def _has_registered_or_coverage_test(conn: sqlite3.Connection, spec_id: str) -> bool:
    test_row = conn.execute(
        """
        SELECT 1
        FROM tests t
        INNER JOIN (
            SELECT id, MAX(version) AS max_version
            FROM tests
            GROUP BY id
        ) latest
        ON t.id = latest.id AND t.version = latest.max_version
        WHERE t.spec_id = ?
        LIMIT 1
        """,
        (spec_id,),
    ).fetchone()
    if test_row:
        return True
    coverage_row = conn.execute(
        "SELECT 1 FROM test_coverage WHERE spec_id = ? LIMIT 1",
        (spec_id,),
    ).fetchone()
    return coverage_row is not None


def _has_passing_test_result(conn: sqlite3.Connection, spec_id: str) -> bool:
    return (
        conn.execute(
            """
            SELECT 1
            FROM tests t
            INNER JOIN (
                SELECT id, MAX(version) AS max_version
                FROM tests
                GROUP BY id
            ) latest
            ON t.id = latest.id AND t.version = latest.max_version
            WHERE t.spec_id = ? AND LOWER(COALESCE(t.last_result, '')) = 'pass'
            LIMIT 1
            """,
            (spec_id,),
        ).fetchone()
        is not None
    )


def _has_implementation_evidence(row: sqlite3.Row) -> bool:
    assertions = _json_loads(row["assertions"], [])
    source_paths = _json_loads(row["source_paths"], [])
    constraints = _json_loads(row["constraints"], {})
    if assertions:
        return True
    if source_paths:
        return True
    return bool(isinstance(constraints, dict) and constraints.get("implementation_evidence"))


def audit_spec_triad(db_path: Path) -> list[Gap]:
    """Audit latest implemented/verified specs for test and implementation evidence."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    gaps: list[Gap] = []

    try:
        for row in _latest_specs(conn):
            spec_id = row["id"]
            status = row["status"]
            if status != "retired" and not _has_owner_deliberation_origin(conn, spec_id):
                gaps.append(
                    Gap(
                        kind="spec_without_owner_deliberation_origin",
                        severity=_deliberation_gap_severity(row),
                        artifact_id=spec_id,
                        artifact_path=None,
                        detail=(
                            "Spec has no linked Deliberation Archive entry with "
                            "source_type='owner_conversation'; Loyal Opposition may request "
                            "owner approval/rejection or re-authorization before treating it "
                            "as governing."
                        ),
                    )
                )

            if status not in TERMINAL_SPEC_STATUSES:
                continue

            artifact_path = None
            source_paths = _json_loads(row["source_paths"], [])
            if source_paths:
                artifact_path = ", ".join(source_paths[:3])

            if not _has_implementation_evidence(row):
                gaps.append(
                    Gap(
                        kind="terminal_spec_without_implementation_evidence",
                        severity="high",
                        artifact_id=spec_id,
                        artifact_path=artifact_path,
                        detail=f"{status} spec has no assertions, source_paths, or implementation_evidence constraint.",
                    )
                )

            if not _has_registered_or_coverage_test(conn, spec_id):
                gaps.append(
                    Gap(
                        kind="terminal_spec_without_test_mapping",
                        severity="critical",
                        artifact_id=spec_id,
                        artifact_path=artifact_path,
                        detail=f"{status} spec has no row in tests or test_coverage.",
                    )
                )
            elif not _has_passing_test_result(conn, spec_id):
                gaps.append(
                    Gap(
                        kind="terminal_spec_without_passing_test_execution",
                        severity="high",
                        artifact_id=spec_id,
                        artifact_path=artifact_path,
                        detail=(
                            f"{status} spec has test mapping but no latest tests.last_result='pass'. "
                            "Coverage-only mappings are not execution evidence."
                        ),
                    )
                )

            if _is_agent_red_candidate(row):
                gaps.append(
                    Gap(
                        kind="agent_red_scoped_spec_candidate_for_gtkb_reclassification",
                        severity="medium",
                        artifact_id=spec_id,
                        artifact_path=artifact_path,
                        detail=(
                            "Spec text references Agent Red. Confirm whether it is a GT-KB platform "
                            "behavior proven by Agent Red as adopter, or an application-only spec."
                        ),
                    )
                )
    finally:
        conn.close()

    return gaps


def _has_owner_deliberation_origin(conn: sqlite3.Connection, spec_id: str) -> bool:
    return (
        conn.execute(
            """
            SELECT 1
            FROM current_deliberations
            WHERE spec_id = ?
              AND source_type = 'owner_conversation'
              AND COALESCE(source_ref, '') != ''
            LIMIT 1
            """,
            (spec_id,),
        ).fetchone()
        is not None
    )


def _deliberation_gap_severity(row: sqlite3.Row) -> str:
    spec_type = row["type"] or "requirement"
    if spec_type in {"requirement", "specification"}:
        return "critical"
    return "high"


def _is_agent_red_candidate(row: sqlite3.Row) -> bool:
    text = " ".join(
        str(row[key] or "") for key in ("title", "description", "scope", "section", "tags", "source_paths")
    ).lower()
    if "agent red" not in text and "agent_red" not in text and "agent-red" not in text:
        return False
    return row["status"] != "retired"


def _has_markdown_section(content: str, heading: str) -> bool:
    return re.search(SECTION_RE_TEMPLATE.format(heading=re.escape(heading)), content) is not None


def _extract_bridge_entries(project_root: Path) -> list[tuple[str, str, str]]:
    """Return status-bearing numbered bridge files as ``(slug, status, rel_path)``."""
    from groundtruth_kb.bridge.versioned_files import scan_expected_documents, status_from_bridge_file

    entries: list[tuple[str, str, str]] = []
    for document in scan_expected_documents(project_root).values():
        for rel_path in document.files:
            status = status_from_bridge_file(project_root / rel_path)
            if status:
                entries.append((document.slug, status, rel_path))
    return entries


def audit_bridge_spec_links(bridge_dir: Path, project_root: Path) -> list[Gap]:
    """Audit historical GO/VERIFIED bridge files for explicit spec linkage."""
    if not bridge_dir.is_dir():
        return [
            Gap(
                kind="bridge_state_missing",
                severity="critical",
                artifact_id="bridge",
                artifact_path=str(bridge_dir),
                detail="Bridge directory is missing; cannot audit approved/verified implementation history.",
            )
        ]

    gaps: list[Gap] = []
    for document, status, rel_path in _extract_bridge_entries(project_root):
        if status not in BRIDGE_TERMINAL_STATUSES:
            continue
        bridge_file = project_root / rel_path
        if not bridge_file.exists():
            gaps.append(
                Gap(
                    kind="bridge_terminal_file_missing",
                    severity="critical",
                    artifact_id=document,
                    artifact_path=rel_path,
                    detail=f"{status} bridge entry points to a missing file.",
                )
            )
            continue
        content = bridge_file.read_text(encoding="utf-8", errors="replace")
        if not _has_markdown_section(content, "Specification Links"):
            gaps.append(
                Gap(
                    kind="bridge_terminal_without_specification_links_section",
                    severity="high",
                    artifact_id=document,
                    artifact_path=rel_path,
                    detail=f"{status} bridge file has no '## Specification Links' section.",
                )
            )
        elif not SPEC_LINK_RE.search(content):
            gaps.append(
                Gap(
                    kind="bridge_terminal_without_concrete_spec_id",
                    severity="high",
                    artifact_id=document,
                    artifact_path=rel_path,
                    detail=f"{status} bridge file has Specification Links but no concrete spec ID.",
                )
            )
    return gaps


def run_audit(db_path: Path, bridge_dir: Path, project_root: Path) -> dict[str, Any]:
    gaps = [
        *audit_spec_triad(db_path),
        *audit_bridge_spec_links(bridge_dir, project_root),
    ]
    by_kind: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    for gap in gaps:
        by_kind[gap.kind] = by_kind.get(gap.kind, 0) + 1
        by_severity[gap.severity] = by_severity.get(gap.severity, 0) + 1

    return {
        "db_path": str(db_path),
        "bridge_state": str(bridge_dir),
        "gap_count": len(gaps),
        "by_kind": dict(sorted(by_kind.items())),
        "by_severity": dict(sorted(by_severity.items())),
        "gaps": [asdict(gap) for gap in gaps],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--fail-on-gaps", action="store_true", help="Exit nonzero when gaps exist.")
    args = parser.parse_args()

    report = run_audit(args.db, args.bridge_dir, args.project_root)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("GT-KB triad completeness audit")
        print(f"DB: {report['db_path']}")
        print(f"Bridge state: {report['bridge_state']}")
        print(f"Gaps: {report['gap_count']}")
        print(f"By severity: {report['by_severity']}")
        print(f"By kind: {report['by_kind']}")
        for gap in report["gaps"][:50]:
            print(f"- [{gap['severity']}] {gap['kind']} {gap['artifact_id']}: {gap['detail']}")
        if len(report["gaps"]) > 50:
            print(f"... {len(report['gaps']) - 50} more gaps omitted from text output; use --json.")

    if args.fail_on_gaps and report["gap_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
