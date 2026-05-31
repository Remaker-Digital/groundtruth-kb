"""Spec-to-test mapping helper - read-only CLI for verify skill Slice 2 (WI-3261).

Per ``bridge/gtkb-verify-skill-spec-to-test-mapping-005.md`` (Codex GO at ``-006``):
maps specification IDs to their linked tests + latest assertion run state.

Inputs:
- ``--bridge-id <slug>``: extract spec IDs from the latest matching bridge file.
- ``--spec-id <SPEC-ID>``: explicit spec ID (repeatable).
- ``--json``: emit JSON instead of markdown.
- ``--db-path``: override path to groundtruth.db (default ``groundtruth.db``).
- ``--bridge-dir``: override path to bridge directory (default ``bridge``).

Data sources per the proposal's Schema Reconciliation Note:
- Per-test rows: ``current_tests`` filtered by ``spec_id`` (read-only).
- Per-test status: ``current_tests.last_result``.
- Per-test last-run: ``current_tests.last_executed_at``.
- Test path: ``current_tests.test_file`` (no ``test_path`` column exists).
- Latest assertion run: newest ``assertion_runs`` row for the spec, ordered by
  ``run_at`` DESC with ``rowid`` DESC as the tie-break. Optional ``run_id`` is
  sourced from ``rowid`` (there is no ``run_id`` column).

Precedence rules per proposal Helper Data Contract:
- ``current_tests.last_result`` is the per-test status; never overwritten by
  ``assertion_runs``.
- Spec with no ``current_tests`` rows -> markdown row with ``Test ID`` set to
  ``(none)`` and per-test status ``no linked tests``.
- Test row with no ``last_result`` -> per-test status ``not_run``.
- Spec with no assertion runs -> assertion status ``unknown``.

Exit codes:
- 0: normal execution (including specs with no linked tests).
- 2: invalid input, missing database, or missing bridge thread.

This script is read-only. It performs no mutation to ``groundtruth.db`` and
relies only on SQL SELECT statements.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Spec ID alternation: SPEC, GOV, DCL, ADR, PB, REQ. DELIB intentionally excluded
# (deliberation IDs are not specifications).
SPEC_ID_PATTERN = re.compile(r"\b(?:SPEC|GOV|DCL|ADR|PB|REQ)-[A-Z0-9][A-Z0-9-]*\b")

DEFAULT_DB_PATH = "groundtruth.db"
DEFAULT_BRIDGE_DIR = "bridge"


@dataclass
class TestEntry:
    test_id: str
    test_path: str | None
    last_result: str | None
    last_executed_at: str | None


@dataclass
class AssertionRunEntry:
    run_at: str | None
    overall_passed: bool | None
    run_id: str | None


@dataclass
class SpecEntry:
    spec_id: str
    tests: list[TestEntry] = field(default_factory=list)
    latest_assertion_run: AssertionRunEntry | None = None


def extract_spec_ids_from_bridge(bridge_id: str, bridge_dir: Path) -> tuple[list[str], Path]:
    """Find the latest bridge file by version number and extract cited spec IDs.

    Returns ``(spec_ids, source_file_path)``. Raises ``FileNotFoundError`` when
    no matching ``bridge/<bridge-id>-NNN.md`` files exist.
    """
    pattern = re.compile(rf"^{re.escape(bridge_id)}-(\d+)\.md$")
    candidates: list[tuple[int, Path]] = []
    for p in sorted(bridge_dir.iterdir()):
        if not p.is_file():
            continue
        m = pattern.match(p.name)
        if m:
            candidates.append((int(m.group(1)), p))
    if not candidates:
        raise FileNotFoundError(f"No bridge files found matching {bridge_id}-NNN.md in {bridge_dir}")
    candidates.sort(key=lambda x: x[0], reverse=True)
    latest = candidates[0][1]
    content = latest.read_text(encoding="utf-8")
    spec_ids = sorted(set(SPEC_ID_PATTERN.findall(content)))
    return spec_ids, latest


def query_tests_for_spec(conn: sqlite3.Connection, spec_id: str) -> list[TestEntry]:
    """Return current_tests rows for the spec.

    Equivalent to ``KnowledgeDB.get_tests_for_spec(spec_id)`` but uses raw
    SQLite to keep the helper self-contained and click-independent.
    """
    rows = conn.execute(
        "SELECT id, test_file, last_result, last_executed_at FROM current_tests WHERE spec_id = ? ORDER BY id",
        (spec_id,),
    ).fetchall()
    return [
        TestEntry(
            test_id=r["id"],
            test_path=r["test_file"],
            last_result=r["last_result"],
            last_executed_at=r["last_executed_at"],
        )
        for r in rows
    ]


def query_latest_assertion_run(conn: sqlite3.Connection, spec_id: str) -> AssertionRunEntry | None:
    """Newest assertion_runs row for the spec, ordered by run_at then rowid."""
    row = conn.execute(
        "SELECT run_at, overall_passed, rowid FROM assertion_runs "
        "WHERE spec_id = ? ORDER BY run_at DESC, rowid DESC LIMIT 1",
        (spec_id,),
    ).fetchone()
    if row is None:
        return None
    overall = row["overall_passed"]
    return AssertionRunEntry(
        run_at=row["run_at"],
        overall_passed=bool(overall) if overall is not None else None,
        run_id=str(row["rowid"]) if row["rowid"] is not None else None,
    )


def build_entries(conn: sqlite3.Connection, spec_ids: list[str]) -> list[SpecEntry]:
    entries: list[SpecEntry] = []
    for sid in spec_ids:
        tests = query_tests_for_spec(conn, sid)
        latest_run = query_latest_assertion_run(conn, sid)
        entries.append(SpecEntry(spec_id=sid, tests=tests, latest_assertion_run=latest_run))
    return entries


def _assertion_status_label(run: AssertionRunEntry | None) -> str:
    if run is None:
        return "unknown"
    if run.overall_passed is True:
        return "pass"
    if run.overall_passed is False:
        return "fail"
    return "unknown"


def format_markdown(entries: list[SpecEntry]) -> str:
    lines = [
        "| Spec | Test ID | Test Path | Test Status | Last Test Run | Latest Assertion Run | Assertion Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in entries:
        run = entry.latest_assertion_run
        run_at = (run.run_at if run and run.run_at else "-") if run else "-"
        assertion_status = _assertion_status_label(run)
        if not entry.tests:
            lines.append(f"| {entry.spec_id} | (none) | - | no linked tests | - | {run_at} | {assertion_status} |")
            continue
        for t in entry.tests:
            test_status = t.last_result or "not_run"
            last_run = t.last_executed_at or "-"
            path = t.test_path or "-"
            lines.append(
                f"| {entry.spec_id} | {t.test_id} | {path} | {test_status} | "
                f"{last_run} | {run_at} | {assertion_status} |"
            )
    return "\n".join(lines)


def format_json(entries: list[SpecEntry]) -> str:
    payload = {
        "specs": [
            {
                "spec_id": e.spec_id,
                "tests": [
                    {
                        "test_id": t.test_id,
                        "test_path": t.test_path,
                        "last_result": t.last_result,
                        "last_executed_at": t.last_executed_at,
                    }
                    for t in e.tests
                ],
                "latest_assertion_run": (asdict(e.latest_assertion_run) if e.latest_assertion_run else None),
            }
            for e in entries
        ]
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for s in items:
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=("Map specification IDs to linked tests and latest assertion run state (read-only).")
    )
    parser.add_argument(
        "--bridge-id",
        help="Extract spec IDs from the latest bridge file matching this slug.",
    )
    parser.add_argument(
        "--spec-id",
        action="append",
        default=[],
        help="Explicit spec ID (repeatable).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown.")
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DB_PATH,
        help="Path to groundtruth.db (default: groundtruth.db).",
    )
    parser.add_argument(
        "--bridge-dir",
        default=DEFAULT_BRIDGE_DIR,
        help="Path to bridge directory (default: bridge).",
    )
    args = parser.parse_args(argv)

    if not args.bridge_id and not args.spec_id:
        parser.error("Either --bridge-id or at least one --spec-id is required.")

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}", file=sys.stderr)
        return 2

    spec_ids = list(args.spec_id)
    if args.bridge_id:
        bridge_dir = Path(args.bridge_dir)
        if not bridge_dir.is_dir():
            print(
                f"ERROR: Bridge directory not found at {bridge_dir}",
                file=sys.stderr,
            )
            return 2
        try:
            extracted, _ = extract_spec_ids_from_bridge(args.bridge_id, bridge_dir)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        spec_ids.extend(extracted)

    unique_specs = _dedupe_preserve_order(spec_ids)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        entries = build_entries(conn, unique_specs)
    finally:
        conn.close()

    if args.json:
        print(format_json(entries))
    else:
        print(format_markdown(entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
