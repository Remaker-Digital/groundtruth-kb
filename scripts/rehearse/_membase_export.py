"""Wave 2 lane 4 (Stage C leaf): MemBase / KB partition manifest.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice8-005.md`` (REVISED-2)
and ``-006`` (Codex GO with implementation constraints).

Discovers live ``groundtruth.db`` schema dynamically via ``sqlite_master``
and classifies each table into one of four categories:

- **versioned_artifact** (12 known tables with ``id`` + ``version``):
  enumerated as one entry per unique ``id`` with full ``versions`` array.
- **relationship** (``deliberation_specs``, ``deliberation_work_items``):
  rows trace classification from parent deliberation; orphan rows
  surface as warnings per Codex ``-006`` constraint 3.
- **excluded_telemetry** (``assertion_runs``, ``pipeline_events``,
  ``quality_scores``, ``test_coverage``): ``(row_count, reason,
  cutover_policy)`` per Codex ``-006`` constraint 2; not enumerated
  per-row.
- **per_session** (``session_prompts``, ``session_snapshots``,
  ``spec_quality_scores``): rows classified by ``session_id`` ownership
  signal; undeterminable ownership → ``unclassified`` per Codex
  ``-006`` constraint 4 (NOT defaulted to ``adopter``).

Discovered tables not in any classification set return ``status='error'``
per Codex ``-006`` constraint 1 (NOT silent ``ok``-with-warning). This
defends the cutover plan against silent omission of new schema
additions.

Outputs:
  - ``membase-partition-manifest.json`` (machine-readable cutover plan)
  - ``membase-partition-manifest-preview.md`` (human review)
  - ``result.json`` (standard sub-script envelope)
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import emit_result

# ---- Table classification policy --------------------------------------

# Per Codex `-006` review: closed list of known versioned-artifact tables.
# A pure shape-detection (any table with id+version) would silently
# include unexpected new tables; this closed list catches schema drift
# loudly while still validating shape.
_EXPECTED_VERSIONED_ARTIFACT_TABLES: frozenset[str] = frozenset(
    {
        "specifications",
        "tests",
        "work_items",
        "documents",
        "operational_procedures",
        "deliberations",
        "environment_config",
        "backlog_snapshots",
        "test_plans",
        "test_plan_phases",
        "test_procedures",
        "testable_elements",
    }
)

# Relationship tables: no id+version; classification flows from parent.
_RELATIONSHIP_TABLES: frozenset[str] = frozenset(
    {
        "deliberation_specs",
        "deliberation_work_items",
    }
)

# Per Codex `-006` constraint 2: each excluded telemetry table emits
# (row_count, reason, cutover_policy) exactly. Telemetry data is
# regenerated at the new root after cutover; not part of the partition
# manifest.
_EXCLUDED_TELEMETRY_POLICY: dict[str, dict[str, str]] = {
    "assertion_runs": {
        "reason": "per_run_telemetry_regenerated_at_new_root",
        "cutover_policy": "regenerate_at_new_root_via_assertion_evaluation",
    },
    "pipeline_events": {
        "reason": "event_log_regenerated_at_new_root",
        "cutover_policy": "discard_post_migration",
    },
    "quality_scores": {
        "reason": "transient_scoring_data",
        "cutover_policy": "regenerate_at_new_root",
    },
    "test_coverage": {
        "reason": "per_run_test_telemetry",
        "cutover_policy": "regenerate_at_new_root",
    },
}

# Per-session tables: rows classified by session-ownership metadata.
_PER_SESSION_TABLES: frozenset[str] = frozenset(
    {
        "session_prompts",
        "session_snapshots",
        "spec_quality_scores",
    }
)

# Adopter / framework content markers for content-based classification
# of versioned-artifact rows. Per the proposal's §3 algorithm: ID prefix
# is the primary signal, with content-scan as the secondary signal for
# non-prefixed IDs (SPEC-*, DELIB-*, WI-*, DOC-*).
_ADOPTER_CONTENT_MARKERS: tuple[str, ...] = (
    "agent red",
    "agent_red",
    "agent-red",
    "shopify",
    "stripe",
    "transport",
)

_FRAMEWORK_CONTENT_MARKERS: tuple[str, ...] = (
    "groundtruth-kb",
    "groundtruth_kb",
    "gt-kb",
)

# Columns scanned for content-based classification when present in the
# table schema. Order matters only for deterministic concatenation.
_CONTENT_BEARING_COLUMNS: tuple[str, ...] = (
    "title",
    "description",
    "content",
    "subject",
    "scope",
    "rationale",
    "summary",
)


# ---- KB access helpers -----------------------------------------------


def _open_readonly(kb_path: Path) -> sqlite3.Connection:
    """Open the KB read-only via SQLite URI (mode=ro). Per proposal §1."""
    uri = f"file:{kb_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _discover_tables(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Discover live tables and their shape (columns + row count).

    Returns one dict per non-``sqlite_%`` table with column list,
    row count, and convenience flags ``has_id`` / ``has_version`` /
    ``has_id_version`` / ``has_session_id``.
    """
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    table_names = [row[0] for row in cur.fetchall()]
    discovered: list[dict[str, Any]] = []
    for name in table_names:
        cur.execute(f'PRAGMA table_info("{name}")')
        columns = [c[1] for c in cur.fetchall()]
        cur.execute(f'SELECT COUNT(*) FROM "{name}"')
        row_count = cur.fetchone()[0]
        discovered.append(
            {
                "table_name": name,
                "columns": columns,
                "row_count": row_count,
                "has_id": "id" in columns,
                "has_version": "version" in columns,
                "has_id_version": "id" in columns and "version" in columns,
                "has_session_id": "session_id" in columns,
            }
        )
    return discovered


# ---- Classification helpers -------------------------------------------


def _classify_artifact_id(item_id: str, content_text: str = "") -> tuple[str, str]:
    """Classify a versioned-artifact row by ID prefix + content scan.

    Returns ``(classification, signal)`` where classification is one of
    ``framework`` / ``adopter`` / ``unclassified``.

    - ``AR-*`` → ``adopter``
    - ``GTKB-*`` + adopter content → ``unclassified`` (conflict signal)
    - ``GTKB-*`` + no adopter content → ``framework``
    - non-prefixed (``SPEC-*``, ``DELIB-*``, ``WI-*``, ``DOC-*``):
      classify by content scan; mixed/empty → ``unclassified``
    """
    aid = item_id or ""
    if aid.startswith("AR-"):
        return ("adopter", "ar_prefix")
    blob = content_text.lower()
    adopter_hit = any(m in blob for m in _ADOPTER_CONTENT_MARKERS)
    framework_hit = any(m in blob for m in _FRAMEWORK_CONTENT_MARKERS)
    if aid.startswith("GTKB-"):
        if adopter_hit and not framework_hit:
            return ("unclassified", "gtkb_prefix_with_adopter_content")
        return ("framework", "gtkb_prefix")
    if adopter_hit and not framework_hit:
        return ("adopter", "agent_red_product_reference")
    if framework_hit and not adopter_hit:
        return ("framework", "groundtruth_kb_reference")
    if adopter_hit and framework_hit:
        return ("unclassified", "mixed_scope_content")
    return ("unclassified", "no_classification_signal")


def _enumerate_versioned_table(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    """Enumerate ``(id, versions[], classification)`` for a versioned table.

    One entry per unique ``id``; ``versions`` is the sorted list of
    ``version`` values that exist for that id. Classification uses the
    concatenation of all version rows' content-bearing columns.
    """
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info("{table_name}")')
    columns = [c[1] for c in cur.fetchall()]
    content_cols = [c for c in _CONTENT_BEARING_COLUMNS if c in columns]
    select_list = "id, version" + (", " + ", ".join(content_cols) if content_cols else "")
    cur.execute(f'SELECT {select_list} FROM "{table_name}" ORDER BY id, version')
    rows = cur.fetchall()
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_id = row[0]
        version = row[1]
        content_blob = " ".join(str(v) for v in row[2:] if v is not None)
        if row_id not in by_id:
            by_id[row_id] = {"id": row_id, "versions": [], "content_blob": []}
        by_id[row_id]["versions"].append(version)
        by_id[row_id]["content_blob"].append(content_blob)

    entries: list[dict[str, Any]] = []
    for row_id, data in by_id.items():
        content_text = " ".join(data["content_blob"])
        classification, signal = _classify_artifact_id(row_id, content_text)
        entries.append(
            {
                "table_name": table_name,
                "id": row_id,
                "versions": sorted(data["versions"]),
                "version_count": len(data["versions"]),
                "max_version": max(data["versions"]) if data["versions"] else 0,
                "classification": classification,
                "classification_signal": signal,
            }
        )
    return entries


def _enumerate_relationship_table(
    conn: sqlite3.Connection,
    table_name: str,
    parent_classifications: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Enumerate relationship rows; trace classification from parent.

    Per Codex ``-006`` constraint 3: each row references a parent
    deliberation via ``deliberation_id``; classification inherits from
    that parent. Orphan rows (parent missing) surface as warnings and
    classify as ``unclassified``.

    Returns ``(entries, warnings)``.
    """
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info("{table_name}")')
    columns = [c[1] for c in cur.fetchall()]
    if "deliberation_id" not in columns:
        return [], [
            f"relationship_table_shape_unexpected: {table_name!r} has no deliberation_id column (columns: {columns})"
        ]

    other_cols = [c for c in columns if c != "deliberation_id"]
    select_cols = ["deliberation_id", *other_cols]
    cur.execute(f'SELECT {", ".join(select_cols)} FROM "{table_name}"')
    rows = cur.fetchall()

    entries: list[dict[str, Any]] = []
    warnings: list[str] = []
    for row in rows:
        deliberation_id = row[0]
        other_values = dict(zip(other_cols, row[1:], strict=False))
        parent = parent_classifications.get(deliberation_id)
        if parent is None:
            warnings.append(
                f"orphan_relationship_row: {table_name}.deliberation_id="
                f"{deliberation_id!r} (parent not in deliberations table)"
            )
            classification = "unclassified"
            classification_signal = "orphan_parent_deliberation_missing"
            parent_classification: str | None = None
        else:
            classification = parent["classification"]
            classification_signal = "from_parent_deliberation"
            parent_classification = parent["classification"]
        entries.append(
            {
                "table_name": table_name,
                "deliberation_id": deliberation_id,
                **other_values,
                "classification": classification,
                "classification_signal": classification_signal,
                "classification_inheritance": "from_parent_deliberation",
                "parent_classification": parent_classification,
            }
        )
    return entries, warnings


def _classify_session_id(session_id: str) -> tuple[str, str]:
    """Classify a per-session row by its session_id ownership signal.

    Per Codex ``-006`` constraint 4: undeterminable ownership →
    ``unclassified`` (NOT defaulted to ``adopter``). Agent Red sessions
    follow the ``S{N}`` convention per CLAUDE.md, which is a tracked
    classification heuristic.
    """
    sid = (session_id or "").strip()
    if sid.startswith("S") and sid[1:].isdigit():
        return ("adopter", "session_owned_by_adopter_per_s_n_convention")
    if not sid:
        return ("unclassified", "session_id_empty_ownership_undetermined")
    return ("unclassified", "session_id_format_unrecognized_ownership_undetermined")


def _enumerate_per_session_table(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    """Enumerate per-session rows; classify by session-ownership signal."""
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info("{table_name}")')
    columns = [c[1] for c in cur.fetchall()]
    cur.execute(f'SELECT * FROM "{table_name}"')
    rows = cur.fetchall()

    if "session_id" in columns:
        session_col = "session_id"
    elif "id" in columns:
        # Some per-session tables (e.g., session_snapshots) may use
        # ``id`` as the session identifier itself.
        session_col = "id"
    else:
        session_col = None

    entries: list[dict[str, Any]] = []
    for row in rows:
        row_dict = dict(zip(columns, row, strict=False))
        if session_col is not None:
            session_id = str(row_dict.get(session_col, ""))
            classification, signal = _classify_session_id(session_id)
        else:
            session_id = ""
            classification = "unclassified"
            signal = "no_session_id_column_ownership_undetermined"
        entries.append(
            {
                "table_name": table_name,
                "row_id": row_dict.get("id"),
                "session_id": session_id or None,
                "classification": classification,
                "classification_signal": signal,
            }
        )
    return entries


# ---- Output emitters --------------------------------------------------


def _build_version_preservation_evidence(
    versioned_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute version-preservation evidence per proposal §2.4."""
    if not versioned_records:
        return {
            "tables_with_versioning_verified": [],
            "total_unique_artifacts": 0,
            "total_versioned_rows": 0,
            "max_version_count_observed": None,
        }
    tables = sorted({r["table_name"] for r in versioned_records})
    total_unique = len(versioned_records)
    total_rows = sum(r["version_count"] for r in versioned_records)
    max_record = max(versioned_records, key=lambda r: r["version_count"])
    return {
        "tables_with_versioning_verified": tables,
        "total_unique_artifacts": total_unique,
        "total_versioned_rows": total_rows,
        "max_version_count_observed": {
            "id": max_record["id"],
            "table": max_record["table_name"],
            "version_count": max_record["version_count"],
        },
    }


def _emit_markdown_preview(
    path: Path,
    summary: dict[str, Any],
    versioned: list[dict[str, Any]],
    relationship: list[dict[str, Any]],
    per_session: list[dict[str, Any]],
    warnings: list[str],
) -> None:
    """Emit human-readable preview markdown."""
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lines: list[str] = [
        "# MemBase Partition Manifest\n",
        "\n",
        f"Generated: {timestamp}\n",
        "Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_membase_export.py` (Slice 8).\n",
        "\n",
        "## Summary\n",
        "\n",
        f"- Total tables discovered: {summary['tables_discovered']}\n",
        f"  - Versioned artifact tables: {summary['tables_versioned']}\n",
        f"  - Relationship tables: {summary['tables_relationship']}\n",
        f"  - Excluded telemetry tables: {summary['tables_excluded_telemetry']}\n",
        f"  - Per-session tables: {summary['tables_per_session']}\n",
        "\n",
        f"- Versioned records: {summary['versioned_records_count']:,}\n",
        f"  - framework: {summary['versioned_by_classification'].get('framework', 0):,}\n",
        f"  - adopter: {summary['versioned_by_classification'].get('adopter', 0):,}\n",
        f"  - unclassified: {summary['versioned_by_classification'].get('unclassified', 0):,}\n",
        "\n",
        f"- Relationship records: {summary['relationship_records_count']:,}\n",
        f"- Per-session records: {summary['per_session_records_count']:,}\n",
        "\n",
        "## Excluded Telemetry Tables\n",
        "\n",
    ]
    for entry in summary.get("excluded_tables", []):
        lines.append(
            f"- `{entry['name']}` ({entry['row_count']:,} rows): "
            f"{entry['reason']}; cutover policy: `{entry['cutover_policy']}`\n"
        )
    if not summary.get("excluded_tables"):
        lines.append("- (none)\n")

    lines.append("\n## Version Preservation Evidence\n\n")
    evidence = summary.get("version_preservation_evidence", {})
    lines.append(f"- Tables with versioning verified: {len(evidence.get('tables_with_versioning_verified', []))}\n")
    lines.append(f"- Total unique artifacts: {evidence.get('total_unique_artifacts', 0):,}\n")
    lines.append(f"- Total versioned rows: {evidence.get('total_versioned_rows', 0):,}\n")
    max_obs = evidence.get("max_version_count_observed")
    if max_obs:
        lines.append(
            f"- Max version count: `{max_obs['id']}` ({max_obs['table']}) — {max_obs['version_count']} versions\n"
        )

    if warnings:
        lines.append("\n## Warnings\n\n")
        for w in warnings:
            lines.append(f"- {w}\n")

    path.write_text("".join(lines), encoding="utf-8")


# ---- Entry point ------------------------------------------------------


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    project_root: Path | None = None,
    kb_path: Path | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage C leaf lane. Per common contract Wave 2 ``-003`` §4.1.

    ``project_root`` overrides ``LEGACY_ROOT`` for fixture trees.
    ``kb_path`` overrides ``{project_root}/groundtruth.db`` (defaults
    to the live KB at the resolved root).
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    root = project_root if project_root is not None else LEGACY_ROOT
    db_path = kb_path if kb_path is not None else (root / "groundtruth.db")
    lane_dir = output_dir / "membase_export"
    lane_dir.mkdir(parents=True, exist_ok=True)

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

    try:
        conn = _open_readonly(db_path)
    except sqlite3.OperationalError as exc:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"kb_open_failed: {exc}"],
            },
        )

    try:
        discovered = _discover_tables(conn)

        # Schema validation: known versioned tables must have id+version;
        # discovered tables must fall in one of the four classification
        # sets. Per Codex `-006` constraint 1: unknown tables → error.
        schema_drift_errors: list[str] = []
        unclassified_table_names: list[str] = []
        for table in discovered:
            name = table["table_name"]
            if name in _EXPECTED_VERSIONED_ARTIFACT_TABLES:
                if not table["has_id_version"]:
                    schema_drift_errors.append(
                        f"schema_drift: known versioned table {name!r} "
                        f"missing id+version columns "
                        f"(has columns: {table['columns']})"
                    )
                continue
            if name in _RELATIONSHIP_TABLES:
                continue
            if name in _EXCLUDED_TELEMETRY_POLICY:
                continue
            if name in _PER_SESSION_TABLES:
                continue
            unclassified_table_names.append(name)

        if schema_drift_errors:
            return emit_result(
                lane_dir,
                {
                    "status": "error",
                    "output_files": [],
                    "metrics": {"tables_discovered": len(discovered)},
                    "warnings": schema_drift_errors,
                },
            )
        if unclassified_table_names:
            return emit_result(
                lane_dir,
                {
                    "status": "error",
                    "output_files": [],
                    "metrics": {
                        "tables_discovered": len(discovered),
                        "unclassified_table_names": unclassified_table_names,
                    },
                    "warnings": [
                        f"unclassified_table: {name!r} not in any "
                        f"classification set "
                        f"(versioned/relationship/excluded_telemetry/per_session); "
                        f"add to policy or surface for owner decision before cutover"
                        for name in unclassified_table_names
                    ],
                },
            )

        warnings: list[str] = []

        # Pass 1 — versioned-artifact tables. Build deliberation
        # classification map for relationship-row inheritance in pass 2.
        versioned_records: list[dict[str, Any]] = []
        deliberation_classifications: dict[str, dict[str, str]] = {}
        for table in discovered:
            name = table["table_name"]
            if name not in _EXPECTED_VERSIONED_ARTIFACT_TABLES:
                continue
            entries = _enumerate_versioned_table(conn, name)
            versioned_records.extend(entries)
            if name == "deliberations":
                for entry in entries:
                    deliberation_classifications[entry["id"]] = {
                        "classification": entry["classification"],
                        "signal": entry["classification_signal"],
                    }

        # Pass 2 — relationship tables (depend on deliberation map).
        relationship_records: list[dict[str, Any]] = []
        for table in discovered:
            name = table["table_name"]
            if name not in _RELATIONSHIP_TABLES:
                continue
            entries, rel_warnings = _enumerate_relationship_table(conn, name, deliberation_classifications)
            relationship_records.extend(entries)
            warnings.extend(rel_warnings)

        # Pass 3 — per-session tables.
        per_session_records: list[dict[str, Any]] = []
        for table in discovered:
            name = table["table_name"]
            if name not in _PER_SESSION_TABLES:
                continue
            per_session_records.extend(_enumerate_per_session_table(conn, name))

        # Pass 4 — excluded-telemetry block (per Codex -006 constraint 2).
        excluded_tables: list[dict[str, Any]] = []
        for table in discovered:
            name = table["table_name"]
            if name not in _EXCLUDED_TELEMETRY_POLICY:
                continue
            policy = _EXCLUDED_TELEMETRY_POLICY[name]
            excluded_tables.append(
                {
                    "name": name,
                    "row_count": table["row_count"],
                    "reason": policy["reason"],
                    "cutover_policy": policy["cutover_policy"],
                }
            )
    finally:
        conn.close()

    # Aggregate classification counts.
    versioned_by_class: dict[str, int] = {"framework": 0, "adopter": 0, "unclassified": 0}
    for entry in versioned_records:
        versioned_by_class[entry["classification"]] = versioned_by_class.get(entry["classification"], 0) + 1
    relationship_by_class: dict[str, int] = {"framework": 0, "adopter": 0, "unclassified": 0}
    for entry in relationship_records:
        relationship_by_class[entry["classification"]] = relationship_by_class.get(entry["classification"], 0) + 1
    per_session_by_class: dict[str, int] = {"framework": 0, "adopter": 0, "unclassified": 0}
    for entry in per_session_records:
        per_session_by_class[entry["classification"]] = per_session_by_class.get(entry["classification"], 0) + 1

    summary: dict[str, Any] = {
        "tables_discovered": len(discovered),
        "tables_versioned": sum(1 for t in discovered if t["table_name"] in _EXPECTED_VERSIONED_ARTIFACT_TABLES),
        "tables_relationship": sum(1 for t in discovered if t["table_name"] in _RELATIONSHIP_TABLES),
        "tables_excluded_telemetry": sum(1 for t in discovered if t["table_name"] in _EXCLUDED_TELEMETRY_POLICY),
        "tables_per_session": sum(1 for t in discovered if t["table_name"] in _PER_SESSION_TABLES),
        "tables_unclassified": 0,
        "versioned_records_count": len(versioned_records),
        "relationship_records_count": len(relationship_records),
        "per_session_records_count": len(per_session_records),
        "versioned_by_classification": versioned_by_class,
        "relationship_by_classification": relationship_by_class,
        "per_session_by_classification": per_session_by_class,
        "excluded_tables": excluded_tables,
        "version_preservation_evidence": _build_version_preservation_evidence(versioned_records),
    }

    # Emit JSON.
    json_path = lane_dir / "membase-partition-manifest.json"
    payload = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kb_path": str(db_path),
        "summary": summary,
        "versioned_records": versioned_records,
        "relationship_records": relationship_records,
        "per_session_records": per_session_records,
        "warnings": warnings,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_files: list[Path] = [json_path]

    # Emit Markdown preview.
    md_path = lane_dir / "membase-partition-manifest-preview.md"
    _emit_markdown_preview(md_path, summary, versioned_records, relationship_records, per_session_records, warnings)
    output_files.append(md_path)

    return emit_result(
        lane_dir,
        {
            "status": "ok",
            "output_files": [str(p) for p in output_files],
            "metrics": {
                "tables_discovered": summary["tables_discovered"],
                "versioned_records_count": summary["versioned_records_count"],
                "relationship_records_count": summary["relationship_records_count"],
                "per_session_records_count": summary["per_session_records_count"],
                "excluded_tables_count": len(excluded_tables),
            },
            "warnings": warnings,
        },
    )
