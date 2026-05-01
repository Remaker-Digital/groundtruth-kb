"""Wave 3 lane (Stage D cross-cutting consumer): manifest-driven DB filter dry-run.

Per ``bridge/gtkb-isolation-016-phase8-wave3-execution-007.md`` (REVISED-3,
GO at ``-008``) and predecessor ``-005`` (REVISED-2). Implements the
``db-filter-dryrun`` lane that consumes Slice 8's partition manifest and
emits a filtered preview DB containing only adopter-classified rows.

The lane is a deterministic consumer: zero classification logic of its
own. All framework/adopter/unclassified decisions flow from the partition
manifest produced by ``_membase_export.py``.

Owner decisions encoded:
  - ``DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE`` (manifest_driven_filter)
  - ``DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE`` (leave_behind_with_warning)

Outputs (under ``{output_dir}/db-filter-dryrun/``):
  - ``groundtruth-filtered-preview.db`` — schema copy of legacy with only
    adopter rows; telemetry tables empty (regenerable per Slice 8).
  - ``db-filter-summary.json`` — per-table row counts and integrity check.
  - ``db-filter-warnings.txt`` — one line per unclassified or orphan row.
  - ``db-filter-rejects.txt`` — one line per framework row excluded.
  - ``result.json`` — standard sub-script envelope.

Disposition handling:
  - ``leave_behind_with_warning`` (current default): unclassified rows are
    skipped and recorded as warnings.
  - ``carry_forward_to_adopter``, ``manual_review_gate``: validator accepts
    these for forward compatibility, but this lane raises NotImplementedError.

Read-only on legacy: legacy DB is opened with ``mode=ro`` URI; no writes to
``E:/GT-KB/groundtruth.db``.

Slice 8 partition manifest schema consumed (per actual output of
``_membase_export.py``):

  - ``versioned_records``: list of {table_name, id, versions, classification}
  - ``relationship_records``: list of {table_name, <natural_key_cols>, classification}
  - ``per_session_records``: list of {table_name, session_id, row_id, classification}
  - ``summary.excluded_tables``: list of {name, row_count, reason, cutover_policy}
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import emit_result

_LANE_NAME = "db-filter-dryrun"
_LANE_SUBDIR = "db-filter-dryrun"
_MEMBASE_SUBDIR = "membase_export"
_PARTITION_MANIFEST_FILENAME = "membase-partition-manifest.json"
_OUTPUT_DB_FILENAME = "groundtruth-filtered-preview.db"

# Natural-key column tuples per relationship table. Slice 8 emits these
# columns directly on each relationship_records entry.
_RELATIONSHIP_KEY_COLUMNS: dict[str, tuple[str, ...]] = {
    "deliberation_specs": ("deliberation_id", "spec_id"),
    "deliberation_work_items": ("deliberation_id", "work_item_id"),
}


def _open_legacy_readonly(db_path: Path) -> sqlite3.Connection:
    """Open the legacy DB read-only via SQLite URI (``mode=ro``)."""
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _copy_schema(src: sqlite3.Connection, dst: sqlite3.Connection) -> list[str]:
    """Copy CREATE TABLE statements from src to dst. Returns table names."""
    cur = src.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables: list[str] = []
    for name, sql in cur.fetchall():
        if sql:
            dst.execute(sql)
            tables.append(name)
    dst.commit()
    return tables


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def _build_versioned_index(
    partition_manifest: dict[str, Any],
) -> dict[str, dict[tuple[str, int], str]]:
    """Build {table: {(id, version): classification}} from versioned_records."""
    out: dict[str, dict[tuple[str, int], str]] = {}
    for entry in partition_manifest.get("versioned_records", []):
        table = entry.get("table_name")
        artifact_id = entry.get("id")
        classification = entry.get("classification") or "unclassified"
        versions = entry.get("versions") or []
        if not isinstance(table, str) or not isinstance(artifact_id, str):
            continue
        bucket = out.setdefault(table, {})
        for v in versions:
            try:
                bucket[(artifact_id, int(v))] = classification
            except (TypeError, ValueError):
                continue
    return out


def _build_relationship_index(
    partition_manifest: dict[str, Any],
) -> dict[str, dict[tuple[str, ...], str]]:
    """Build {table: {(key_col_values...): classification}} from relationship_records."""
    out: dict[str, dict[tuple[str, ...], str]] = {}
    for entry in partition_manifest.get("relationship_records", []):
        table = entry.get("table_name")
        classification = entry.get("classification") or "unclassified"
        if not isinstance(table, str):
            continue
        key_cols = _RELATIONSHIP_KEY_COLUMNS.get(table)
        if key_cols is None:
            continue
        try:
            key_tuple = tuple(str(entry.get(c)) for c in key_cols)
        except (TypeError, ValueError):
            continue
        out.setdefault(table, {})[key_tuple] = classification
    return out


def _build_per_session_index(
    partition_manifest: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Build {table: {session_id: classification}} from per_session_records.

    Slice 8 classifies per (table, session_id), not per row; row_id is
    informational. We collapse to {table: {session_id: classification}}.
    """
    out: dict[str, dict[str, str]] = {}
    for entry in partition_manifest.get("per_session_records", []):
        table = entry.get("table_name")
        session_id = entry.get("session_id")
        classification = entry.get("classification") or "unclassified"
        if not isinstance(table, str) or session_id is None:
            continue
        out.setdefault(table, {})[str(session_id)] = classification
    return out


def _excluded_telemetry_table_names(partition_manifest: dict[str, Any]) -> set[str]:
    summary = partition_manifest.get("summary") or {}
    out: set[str] = set()
    for entry in summary.get("excluded_tables", []) or []:
        name = entry.get("name")
        if isinstance(name, str):
            out.add(name)
    return out


def _filter_versioned_table(
    legacy: sqlite3.Connection,
    target: sqlite3.Connection,
    table: str,
    classify_map: dict[tuple[str, int], str],
    *,
    disposition: str,
    warnings_lines: list[str],
    rejects_lines: list[str],
    counters: dict[str, int],
) -> int:
    """Copy adopter-classified rows; skip framework; warn-and-skip unclassified.

    Returns count of rows inserted into target.
    """
    cols = _table_columns(legacy, table)
    if not cols or "id" not in cols or "version" not in cols:
        return 0
    placeholders = ",".join(["?"] * len(cols))
    col_list = ",".join(cols)
    insert_sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
    cur = legacy.cursor()
    cur.execute(f"SELECT {col_list} FROM {table}")
    id_idx = cols.index("id")
    ver_idx = cols.index("version")
    inserted = 0
    for row in cur.fetchall():
        row_id = row[id_idx]
        row_ver = row[ver_idx]
        try:
            ver_int = int(row_ver) if row_ver is not None else 0
        except (TypeError, ValueError):
            ver_int = 0
        classification = classify_map.get((str(row_id), ver_int), "unclassified")
        if classification == "adopter":
            target.execute(insert_sql, row)
            inserted += 1
            counters["adopter_inserted"] = counters.get("adopter_inserted", 0) + 1
        elif classification == "framework":
            rejects_lines.append(f"{table} | id={row_id} | version={row_ver}")
            counters["framework_excluded"] = counters.get("framework_excluded", 0) + 1
        else:
            if disposition == "leave_behind_with_warning":
                warnings_lines.append(f"unclassified: {table} | id={row_id} | version={row_ver}")
                counters["unclassified_warned"] = counters.get("unclassified_warned", 0) + 1
            else:
                raise NotImplementedError(
                    f"unclassified_disposition={disposition!r} not implemented in this Wave 3 commit; "
                    f"only 'leave_behind_with_warning' is supported."
                )
    return inserted


def _filter_relationship_table(
    legacy: sqlite3.Connection,
    target: sqlite3.Connection,
    table: str,
    classify_map: dict[tuple[str, ...], str],
    *,
    warnings_lines: list[str],
    counters: dict[str, int],
) -> int:
    """Copy relationship rows whose classification (per Slice 8) is adopter."""
    cols = _table_columns(legacy, table)
    key_cols = _RELATIONSHIP_KEY_COLUMNS.get(table)
    if not cols or key_cols is None or not all(c in cols for c in key_cols):
        return 0
    placeholders = ",".join(["?"] * len(cols))
    col_list = ",".join(cols)
    insert_sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
    cur = legacy.cursor()
    cur.execute(f"SELECT {col_list} FROM {table}")
    key_idxs = [cols.index(c) for c in key_cols]
    inserted = 0
    for row in cur.fetchall():
        key_tuple = tuple(str(row[i]) if row[i] is not None else "None" for i in key_idxs)
        classification = classify_map.get(key_tuple, "unclassified")
        if classification == "adopter":
            target.execute(insert_sql, row)
            inserted += 1
        elif classification == "framework":
            counters["framework_excluded"] = counters.get("framework_excluded", 0) + 1
        else:
            warnings_lines.append(
                f"orphan_relationship: {table} | "
                + " | ".join(f"{c}={k}" for c, k in zip(key_cols, key_tuple, strict=False))
            )
            counters["orphan_relationship_warned"] = counters.get("orphan_relationship_warned", 0) + 1
    return inserted


def _filter_per_session_table(
    legacy: sqlite3.Connection,
    target: sqlite3.Connection,
    table: str,
    session_classify_map: dict[str, str],
    *,
    counters: dict[str, int],
) -> int:
    """Copy per-session rows whose session_id is classified adopter by Slice 8."""
    cols = _table_columns(legacy, table)
    if not cols or "session_id" not in cols:
        return 0
    placeholders = ",".join(["?"] * len(cols))
    col_list = ",".join(cols)
    insert_sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
    cur = legacy.cursor()
    cur.execute(f"SELECT {col_list} FROM {table}")
    sid_idx = cols.index("session_id")
    inserted = 0
    for row in cur.fetchall():
        sid = str(row[sid_idx]) if row[sid_idx] is not None else ""
        classification = session_classify_map.get(sid, "unclassified")
        if classification == "adopter":
            target.execute(insert_sql, row)
            inserted += 1
            counters["adopter_inserted"] = counters.get("adopter_inserted", 0) + 1
    return inserted


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    project_root: Path | None = None,
    kb_path: Path | None = None,
) -> dict[str, Any]:
    """Wave 3 db-filter-dryrun lane entry point.

    Reads Slice 8 partition manifest at ``{output_dir}/membase_export/...``,
    emits filtered preview DB at ``{output_dir}/db-filter-dryrun/...``.
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    started = time.time()
    root = project_root if project_root is not None else LEGACY_ROOT
    db_path = kb_path if kb_path is not None else (root / "groundtruth.db")
    lane_dir = output_dir / _LANE_SUBDIR
    lane_dir.mkdir(parents=True, exist_ok=True)

    partition_manifest_path = output_dir / _MEMBASE_SUBDIR / _PARTITION_MANIFEST_FILENAME
    if not partition_manifest_path.exists():
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"partition_manifest_missing: {partition_manifest_path}"],
            },
        )

    try:
        partition_manifest = json.loads(partition_manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"partition_manifest_unreadable: {exc}"],
            },
        )

    if partition_manifest.get("status") == "error":
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"partition_manifest_status_error: {partition_manifest.get('warnings', [])}"],
            },
        )

    disposition = manifest.get("unclassified_disposition", "leave_behind_with_warning")

    if not db_path.exists():
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"kb_path_not_found: {db_path}"],
            },
        )

    output_db_path = lane_dir / _OUTPUT_DB_FILENAME
    if output_db_path.exists():
        output_db_path.unlink()

    legacy = _open_legacy_readonly(db_path)
    target = sqlite3.connect(str(output_db_path))

    warnings_lines: list[str] = []
    rejects_lines: list[str] = []
    counters: dict[str, int] = {}
    table_counts: dict[str, dict[str, int]] = {}

    try:
        copied_tables = _copy_schema(legacy, target)
        versioned_index = _build_versioned_index(partition_manifest)
        relationship_index = _build_relationship_index(partition_manifest)
        per_session_index = _build_per_session_index(partition_manifest)
        excluded_telemetry_names = _excluded_telemetry_table_names(partition_manifest)

        for table in copied_tables:
            if table in excluded_telemetry_names:
                table_counts[table] = {"category": "excluded_telemetry", "rows_inserted": 0}
                counters["telemetry_skipped"] = counters.get("telemetry_skipped", 0) + 1
                continue
            if table in versioned_index:
                inserted = _filter_versioned_table(
                    legacy,
                    target,
                    table,
                    versioned_index[table],
                    disposition=disposition,
                    warnings_lines=warnings_lines,
                    rejects_lines=rejects_lines,
                    counters=counters,
                )
                table_counts[table] = {"category": "versioned_artifact", "rows_inserted": inserted}
                continue
            if table in relationship_index:
                inserted = _filter_relationship_table(
                    legacy,
                    target,
                    table,
                    relationship_index[table],
                    warnings_lines=warnings_lines,
                    counters=counters,
                )
                table_counts[table] = {"category": "relationship", "rows_inserted": inserted}
                continue
            if table in per_session_index:
                inserted = _filter_per_session_table(
                    legacy,
                    target,
                    table,
                    per_session_index[table],
                    counters=counters,
                )
                table_counts[table] = {"category": "per_session", "rows_inserted": inserted}
                continue
            table_counts[table] = {"category": "unhandled", "rows_inserted": 0}

        target.commit()
        integrity_cur = target.cursor()
        integrity_cur.execute("PRAGMA integrity_check")
        integrity_result = integrity_cur.fetchone()
        integrity_ok = integrity_result is not None and integrity_result[0] == "ok"

    finally:
        legacy.close()
        target.close()

    summary = {
        "lane": _LANE_NAME,
        "manifest_input_path": str(partition_manifest_path),
        "legacy_db_path": str(db_path),
        "output_db_path": str(output_db_path),
        "unclassified_disposition": disposition,
        "row_counts": {
            "adopter_inserted": counters.get("adopter_inserted", 0),
            "framework_excluded": counters.get("framework_excluded", 0),
            "unclassified_warned": counters.get("unclassified_warned", 0),
            "telemetry_skipped": counters.get("telemetry_skipped", 0),
            "orphan_relationship_warned": counters.get("orphan_relationship_warned", 0),
        },
        "tables": table_counts,
        "integrity_check": "ok" if integrity_ok else (integrity_result[0] if integrity_result else "unknown"),
        "elapsed_seconds": round(time.time() - started, 3),
    }

    summary_path = lane_dir / "db-filter-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    warnings_path = lane_dir / "db-filter-warnings.txt"
    warnings_path.write_text("\n".join(warnings_lines) + ("\n" if warnings_lines else ""), encoding="utf-8")

    rejects_path = lane_dir / "db-filter-rejects.txt"
    rejects_path.write_text("\n".join(rejects_lines) + ("\n" if rejects_lines else ""), encoding="utf-8")

    output_files = [str(output_db_path), str(summary_path), str(warnings_path), str(rejects_path)]

    if not integrity_ok:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": output_files,
                "metrics": summary["row_counts"],
                "warnings": [f"integrity_check_failed: {summary['integrity_check']}"],
            },
        )

    return emit_result(
        lane_dir,
        {
            "status": "ok",
            "output_files": output_files,
            "metrics": summary["row_counts"],
            "warnings": warnings_lines[:10],
        },
    )
