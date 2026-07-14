# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Restore fleet-goal MemBase carrier rows from the WI-5138 recovery snapshot.

This is intentionally narrow: WI-5139 authorizes restoring only the missing
work-item, test, project-membership, and PAUTH carrier rows needed to unblock
the fleet-goal bridge metadata after the WI-5138 rollback.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIVE_DB = PROJECT_ROOT / "groundtruth.db"
DEFAULT_SNAPSHOT_DB = (
    PROJECT_ROOT / ".gtkb-state" / "antigravity-wi5138-recovery-001" / "pre-finalization-groundtruth.db"
)

WORK_ITEM_IDS = (
    "WI-5211",
    "WI-5216",
    "WI-5222",
    "WI-5223",
    "WI-5224",
    "WI-5225",
    "WI-5226",
    "WI-5227",
    "WI-5228",
)
TEST_IDS = (
    "TEST-11370",
    "TEST-11376",
    "TEST-11377",
    "TEST-11379",
    "TEST-11380",
    "TEST-11381",
    "TEST-11382",
)
PAUTH_IDS = (
    "PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5211-DF-VERDICT-PARITY-20260712",
    "PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712",
    "PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5222-60M-GENEROUS-ALLOWANCE-20260713",
    "PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5223-ELIGIBILITY-PRECEDENCE-20260713",
    "PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5224-VERDICT-COMPLETION-CONTRACT-20260713",
)


@dataclass(frozen=True)
class RestoreSpec:
    table: str
    where_sql: str
    params: tuple[Any, ...]
    key_columns: tuple[str, ...] = ("id", "version")


def _in_clause(values: Sequence[str]) -> str:
    return ", ".join("?" for _ in values)


RESTORE_SPECS = (
    RestoreSpec(
        "work_items",
        f"id in ({_in_clause(WORK_ITEM_IDS)})",
        WORK_ITEM_IDS,
    ),
    RestoreSpec(
        "tests",
        f"id in ({_in_clause(TEST_IDS)})",
        TEST_IDS,
    ),
    RestoreSpec(
        "project_work_item_memberships",
        f"work_item_id in ({_in_clause(WORK_ITEM_IDS)})",
        WORK_ITEM_IDS,
    ),
    RestoreSpec(
        "project_authorizations",
        f"id in ({_in_clause(PAUTH_IDS)})",
        PAUTH_IDS,
    ),
)


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"pragma table_info({table})").fetchall()
    columns = [row["name"] for row in rows if row["name"] != "rowid"]
    if not columns:
        raise ValueError(f"Table not found or has no columns: {table}")
    return columns


def _snapshot_rows(conn: sqlite3.Connection, spec: RestoreSpec) -> list[sqlite3.Row]:
    return conn.execute(
        f"select * from {spec.table} where {spec.where_sql} order by id, version",
        spec.params,
    ).fetchall()


def _row_key(row: sqlite3.Row, key_columns: Sequence[str]) -> tuple[Any, ...]:
    return tuple(row[column] for column in key_columns)


def _key_payload(row: sqlite3.Row, key_columns: Sequence[str]) -> str:
    values = _row_key(row, key_columns)
    return ":".join(str(value) for value in values)


def _exists(conn: sqlite3.Connection, spec: RestoreSpec, row: sqlite3.Row) -> bool:
    predicates = " and ".join(f"{column} = ?" for column in spec.key_columns)
    result = conn.execute(
        f"select 1 from {spec.table} where {predicates} limit 1",
        _row_key(row, spec.key_columns),
    ).fetchone()
    return result is not None


def _insert_row(
    conn: sqlite3.Connection,
    table: str,
    columns: Sequence[str],
    row: sqlite3.Row,
) -> None:
    column_sql = ", ".join(columns)
    value_sql = ", ".join("?" for _ in columns)
    conn.execute(
        f"insert into {table} ({column_sql}) values ({value_sql})",
        tuple(row[column] for column in columns),
    )


def _json_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid JSON list payload: {raw!r}") from exc
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError(f"Expected JSON string list, got: {raw!r}")
    return parsed


def _validate_authorization_scope(rows: Sequence[sqlite3.Row]) -> None:
    allowed = set(WORK_ITEM_IDS)
    for row in rows:
        included = set(_json_list(row["included_work_item_ids"]))
        if not included:
            raise ValueError(f"PAUTH {row['id']} v{row['version']} has no included work items")
        outside_scope = sorted(included - allowed)
        if outside_scope:
            raise ValueError(
                f"PAUTH {row['id']} v{row['version']} includes out-of-scope work items: {', '.join(outside_scope)}"
            )


def restore_carriers(
    *,
    live_db: Path = DEFAULT_LIVE_DB,
    snapshot_db: Path = DEFAULT_SNAPSHOT_DB,
    dry_run: bool = False,
) -> dict[str, Any]:
    if not live_db.exists():
        raise FileNotFoundError(f"Live DB not found: {live_db}")
    if not snapshot_db.exists():
        raise FileNotFoundError(f"Snapshot DB not found: {snapshot_db}")

    summary: dict[str, Any] = {
        "dry_run": dry_run,
        "live_db": str(live_db),
        "snapshot_db": str(snapshot_db),
        "tables": {},
    }
    with _connect(live_db) as live_conn, _connect(snapshot_db) as snapshot_conn:
        live_conn.execute("begin")
        try:
            for spec in RESTORE_SPECS:
                live_columns = _columns(live_conn, spec.table)
                snapshot_columns = _columns(snapshot_conn, spec.table)
                if live_columns != snapshot_columns:
                    raise ValueError(f"Column mismatch for {spec.table}")

                rows = _snapshot_rows(snapshot_conn, spec)
                if spec.table == "project_authorizations":
                    _validate_authorization_scope(rows)

                table_summary = {
                    "candidate_rows": len(rows),
                    "inserted": 0,
                    "inserted_keys": [],
                    "skipped_existing": 0,
                    "skipped_keys": [],
                }
                for row in rows:
                    key = _key_payload(row, spec.key_columns)
                    if _exists(live_conn, spec, row):
                        table_summary["skipped_existing"] += 1
                        table_summary["skipped_keys"].append(key)
                        continue
                    table_summary["inserted"] += 1
                    table_summary["inserted_keys"].append(key)
                    if not dry_run:
                        _insert_row(live_conn, spec.table, live_columns, row)
                summary["tables"][spec.table] = table_summary

            if dry_run:
                live_conn.rollback()
            else:
                live_conn.commit()
        except Exception:
            live_conn.rollback()
            raise
    summary["total_inserted"] = sum(table["inserted"] for table in summary["tables"].values())
    summary["total_skipped_existing"] = sum(table["skipped_existing"] for table in summary["tables"].values())
    return summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--snapshot-db", type=Path, default=DEFAULT_SNAPSHOT_DB)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    summary = restore_carriers(
        live_db=args.live_db,
        snapshot_db=args.snapshot_db,
        dry_run=args.dry_run,
    )
    if args.as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"Inserted {summary['total_inserted']} carrier rows")
        print(f"Skipped {summary['total_skipped_existing']} existing carrier rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
