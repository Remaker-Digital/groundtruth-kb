#!/usr/bin/env python
"""FAB-11 pipeline_events assertion_run retention.

Operational telemetry is not a core artifact ledger. This tool prunes old
``pipeline_events`` rows for assertion runs, snapshots the DB immediately before
the destructive maintenance, and VACUUMs when configured.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GTKB_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(GTKB_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

BRIDGE_ID = "gtkb-fab-11-regression-signal-revival"
CHANGED_BY = "prime-builder/codex"
CONFIG_PATH = PROJECT_ROOT / "config" / "governance" / "pipeline-events-retention.toml"
FAB11_SNAPSHOT_PREFIX = "groundtruth.db.pre-backfill-fab11-vacuum-"


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def load_config(path: Path) -> dict[str, Any]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("pipeline retention schema_version must be 1")
    if data.get("event_type") != "assertion_run":
        raise ValueError("FAB-11 retention is scoped to event_type='assertion_run'")
    if int(data.get("retention_days", 0)) <= 0:
        raise ValueError("retention_days must be positive")
    if int(data.get("delete_batch_size", 0)) <= 0:
        raise ValueError("delete_batch_size must be positive")
    return data


def cutoff_timestamp(retention_days: int, *, now: datetime | None = None) -> str:
    baseline = now or datetime.now(UTC)
    return (baseline - timedelta(days=retention_days)).isoformat(timespec="seconds")


def _counts(conn: sqlite3.Connection, event_type: str, cutoff: str) -> dict[str, int]:
    total = conn.execute("SELECT COUNT(*) FROM pipeline_events").fetchone()[0]
    event_total = conn.execute("SELECT COUNT(*) FROM pipeline_events WHERE event_type = ?", (event_type,)).fetchone()[0]
    candidates = conn.execute(
        "SELECT COUNT(*) FROM pipeline_events WHERE event_type = ? AND timestamp < ?",
        (event_type, cutoff),
    ).fetchone()[0]
    return {"total": total, "event_type_total": event_total, "prune_candidates": candidates}


def _dead_snapshot_paths(project_root: Path, fresh_snapshot: Path | None = None) -> list[Path]:
    dead: list[Path] = []
    for pattern in ("groundtruth.db.corrupt-S311-*", "groundtruth.db.pre-backfill-*"):
        for path in project_root.glob(pattern):
            if fresh_snapshot is not None and path.resolve() == fresh_snapshot.resolve():
                continue
            if path.name.startswith(FAB11_SNAPSHOT_PREFIX):
                continue
            if path.is_file():
                dead.append(path)
    return sorted(set(dead))


def dry_run(db_path: Path, config_path: Path) -> dict[str, Any]:
    config = load_config(config_path)
    cutoff = cutoff_timestamp(int(config["retention_days"]))
    conn = _connect(db_path)
    try:
        counts = _counts(conn, str(config["event_type"]), cutoff)
    finally:
        conn.close()
    return {
        "bridge_id": BRIDGE_ID,
        "applied": False,
        "config_path": config_path.relative_to(PROJECT_ROOT).as_posix(),
        "cutoff": cutoff,
        "db_bytes": db_path.stat().st_size,
        "counts": counts,
        "dead_snapshots": [p.name for p in _dead_snapshot_paths(PROJECT_ROOT)],
    }


def _snapshot_db(db_path: Path, snapshot_prefix: str) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    snapshot = db_path.with_name(f"{snapshot_prefix}-{stamp}.bak")
    shutil.copy2(db_path, snapshot)
    return snapshot


def _delete_candidates(conn: sqlite3.Connection, event_type: str, cutoff: str, batch_size: int) -> int:
    total_deleted = 0
    while True:
        cur = conn.execute(
            """DELETE FROM pipeline_events
               WHERE rowid IN (
                   SELECT rowid FROM pipeline_events
                   WHERE event_type = ? AND timestamp < ?
                   LIMIT ?
               )""",
            (event_type, cutoff, batch_size),
        )
        deleted = cur.rowcount if cur.rowcount is not None else 0
        conn.commit()
        if deleted <= 0:
            break
        total_deleted += deleted
    return total_deleted


def apply(db_path: Path, config_path: Path, *, skip_vacuum: bool = False) -> dict[str, Any]:
    config = load_config(config_path)
    event_type = str(config["event_type"])
    cutoff = cutoff_timestamp(int(config["retention_days"]))
    before_bytes = db_path.stat().st_size
    snapshot = _snapshot_db(db_path, str(config["snapshot_prefix"]))

    conn = _connect(db_path)
    try:
        before_counts = _counts(conn, event_type, cutoff)
        deleted = _delete_candidates(conn, event_type, cutoff, int(config["delete_batch_size"]))
        after_delete_counts = _counts(conn, event_type, cutoff)
        vacuum_ran = bool(config.get("vacuum_after_delete", True)) and not skip_vacuum
        if vacuum_ran:
            conn.execute("VACUUM")
        after_vacuum_counts = _counts(conn, event_type, cutoff)
    finally:
        conn.close()

    disposed: list[str] = []
    for path in _dead_snapshot_paths(PROJECT_ROOT, fresh_snapshot=snapshot):
        path.unlink()
        disposed.append(path.name)

    db = KnowledgeDB(db_path=db_path)
    try:
        db.record_event(
            "pipeline_events_retention",
            CHANGED_BY,
            artifact_id=BRIDGE_ID,
            artifact_type="bridge_thread",
            metadata={
                "event_type": event_type,
                "cutoff": cutoff,
                "deleted": deleted,
                "before_bytes": before_bytes,
                "after_bytes": db_path.stat().st_size,
                "snapshot": snapshot.name,
                "vacuum_ran": vacuum_ran,
            },
        )
    finally:
        db.close()

    return {
        "bridge_id": BRIDGE_ID,
        "applied": True,
        "config_path": config_path.relative_to(PROJECT_ROOT).as_posix(),
        "cutoff": cutoff,
        "snapshot": snapshot.name,
        "before_bytes": before_bytes,
        "after_bytes": db_path.stat().st_size,
        "deleted": deleted,
        "before_counts": before_counts,
        "after_delete_counts": after_delete_counts,
        "after_vacuum_counts": after_vacuum_counts,
        "vacuum_ran": vacuum_ran,
        "disposed_dead_snapshots": disposed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=PROJECT_ROOT / "groundtruth.db")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--skip-vacuum", action="store_true")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()

    result = apply(args.db, args.config, skip_vacuum=args.skip_vacuum) if args.apply else dry_run(args.db, args.config)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
