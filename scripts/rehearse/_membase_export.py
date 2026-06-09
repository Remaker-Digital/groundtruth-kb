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

Type-Specific Override Decisions (per Codex ``-008`` Finding 1)
---------------------------------------------------------------
The classification cascade for each versioned-artifact row is:

1. **Type-specific signal** (table-specific override):
   - ``tests``: classify by ``test_file`` path. Mixed-scope test
     filenames first; ``tests/groundtruth_kb/`` → framework;
     ``tests/transport/``, ``tests/scripts/test_admin_*``,
     ``tests/scripts/test_provider_*`` → adopter (named); any other
     ``tests/`` path → adopter (this lane runs against the *adopter*
     project's KB; framework tests live upstream).
   - ``deliberations``: classify by ``origin_project``. Markers like
     ``groundtruth-kb`` → framework; ``agent-red`` / ``agent_red`` →
     adopter. NULL or unrecognized → fall through.

2. **ID prefix + generic content scan** (fallback for rows without a
   type-specific signal): existing ``_classify_artifact_id`` logic.

Tables with **no override** (explicit decision per Codex ``-008``
required-action option):
   - ``operational_procedures``: ``type`` column is workflow type, not
     scope; no clean adopter/framework discriminator.
   - ``documents``: ``category`` is content-type ("assessment",
     "architecture"), not scope; ``source_path`` is sparsely populated.
   - ``work_items``: ``component`` is functional area, not scope.
   - ``specifications``: ``type`` is artifact subtype; ``tags`` are
     mostly non-scope ("phase-2", "owner_directive").
   - ``test_plans``, ``test_plan_phases``, ``test_procedures``,
     ``testable_elements``, ``backlog_snapshots``, ``environment_config``:
     limited adopter/framework signal beyond ID prefix + content scan.

These tables fall through to ID-prefix + content scan unconditionally.

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
        "projects",
        "project_work_item_memberships",
        "project_dependencies",
        "project_artifact_links",
        "project_authorizations",
        "harnesses",
        "sot_artifacts",
        "canonical_terms",
        "dispatch_events",
    }
)

# Relationship tables: no id+version; classification flows from parent.
_RELATIONSHIP_TABLES: frozenset[str] = frozenset(
    {
        "deliberation_specs",
        "deliberation_work_items",
        "specification_deliberation_sources",
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
    "work_intent_claims": {
        "reason": "transient_coordination_data",
        "cutover_policy": "discard_post_migration",
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
    "name",
    "purpose",
    "target_outcome",
    "scope_note",
    "notes",
    "authorization_name",
    "scope_summary",
    "canonical_term",
    "definition",
    "usage_examples",
    "harness_name",
)

# Per-table additional columns queried for the type-specific classifier
# (separate from generic content scan). Per Codex `-008` Finding 1: the
# original Slice 8 proposal called for type-specific overrides per
# versioned-table type. REVISED-1 implements them for the two tables with
# strong, distinct signal columns; explicitly documents no-override for
# the others (see "Type-specific override decisions" in the module
# docstring).
_TABLE_SPECIFIC_TYPE_COLUMNS: dict[str, tuple[str, ...]] = {
    # Per Codex `-008`: tests classify by file path FIRST, falling back to
    # ID prefix + content scan for tests with NULL ``test_file``.
    "tests": ("test_file", "test_class", "test_function"),
    # Highest-leverage signal in this KB: ``deliberations.origin_project``
    # is populated for ~96% of rows (1,264 / 1,318 in the live schema)
    # and explicitly identifies the originating project.
    "deliberations": ("origin_project", "origin_repo"),
    # Explicitly empty (no override) for these tables; their type-columns
    # are functional categories, not adopter/framework discriminators:
    #   - operational_procedures.type: workflow type, not scope
    #   - documents.category: content-type ("assessment", "architecture"),
    #     not scope; ``source_path`` is sparsely populated
    #   - work_items.component: functional area ("infrastructure_automation",
    #     "customer_interface"), not scope
    #   - specifications.type: artifact subtype ("architecture_decision",
    #     "governance"), not scope; ``tags`` are mostly non-scope
    #     ("phase-2", "owner_directive")
    # These tables fall through to ID-prefix + content scan for every row.
}

# Test-path classification patterns (per Codex `-008` Finding 1 and the
# principled "this is the adopter KB" default rule). Order is
# significant: mixed-scope check runs FIRST so a path like
# ``test_release_candidate_gate.py`` (which lives under a typically-adopter
# directory) is correctly classified as mixed.
_TEST_PATH_MIXED_SCOPE_MARKERS: tuple[str, ...] = (
    "test_release_candidate_gate",
    "test_groundtruth_governance_adoption",
)

_TEST_PATH_FRAMEWORK_PREFIXES: tuple[str, ...] = ("tests/groundtruth_kb/",)

_TEST_PATH_ADOPTER_NAMED_PREFIXES: tuple[str, ...] = (
    "tests/transport/",
    "tests/scripts/test_admin_",
    "tests/scripts/test_provider_",
)

# Default fallback: any path under ``tests/`` that didn't match a
# mixed-scope marker, framework prefix, or adopter-named prefix is treated
# as adopter product test. Justification: this Slice-8 lane runs against
# the *adopter* project's KB. Framework tests live in the upstream
# `groundtruth-kb` repo's KB, not here. Tests in this DB that reference
# product-area paths (`tests/widget/`, `tests/multi_tenant/`,
# `tests/integration/`, etc.) are adopter content by construction. A
# future framework-side import of test artifacts into this KB would still
# be caught: an explicit ``tests/groundtruth_kb/`` prefix overrides this
# default.
_TEST_PATH_DEFAULT_ADOPTER_PREFIX: str = "tests/"

# Deliberation origin classification markers.
_DELIBERATION_ORIGIN_FRAMEWORK_MARKERS: tuple[str, ...] = (
    "groundtruth",
    "gt-kb",
)
_DELIBERATION_ORIGIN_ADOPTER_MARKERS: tuple[str, ...] = (
    "agent-red",
    "agent_red",
    "agent red",
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
                "has_id": "id" in columns or "event_id" in columns,
                "has_version": "version" in columns,
                "has_id_version": ("id" in columns or "event_id" in columns) and "version" in columns,
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


def _classify_test_path(test_file: str | None) -> tuple[str, str] | None:
    """Path-based classifier for the ``tests`` table.

    Per Codex ``-008`` Finding 1. Returns ``(classification, signal)`` if
    ``test_file`` carries a recognized scope signal; ``None`` if NULL,
    empty, or unrecognized (caller falls through to ID-prefix + content
    scan).

    Order is significant: mixed-scope check runs first so a known mixed
    file isn't shadowed by a directory-prefix match.
    """
    if not test_file:
        return None
    p = test_file.replace("\\", "/").lower()
    for marker in _TEST_PATH_MIXED_SCOPE_MARKERS:
        if marker in p:
            return ("unclassified", "mixed_scope_test")
    for prefix in _TEST_PATH_FRAMEWORK_PREFIXES:
        if p.startswith(prefix):
            return ("framework", "test_path_framework_groundtruth_kb")
    for prefix in _TEST_PATH_ADOPTER_NAMED_PREFIXES:
        if p.startswith(prefix):
            return ("adopter", "test_path_adopter_named")
    if p.startswith(_TEST_PATH_DEFAULT_ADOPTER_PREFIX):
        return ("adopter", "test_path_adopter_product")
    return None


def _classify_deliberation_origin(origin_project: str | None) -> tuple[str, str] | None:
    """Origin-project classifier for the ``deliberations`` table.

    Returns ``(classification, signal)`` if ``origin_project`` carries a
    recognized scope marker; ``None`` if NULL or unrecognized (caller
    falls through to ID-prefix + content scan).
    """
    if not origin_project:
        return None
    p = origin_project.lower().strip()
    if any(marker in p for marker in _DELIBERATION_ORIGIN_FRAMEWORK_MARKERS):
        return ("framework", "deliberation_origin_project_framework")
    if any(marker in p for marker in _DELIBERATION_ORIGIN_ADOPTER_MARKERS):
        return ("adopter", "deliberation_origin_project_agent_red")
    return None


def _classify_by_type_specific_signal(table_name: str, type_columns: dict[str, str | None]) -> tuple[str, str] | None:
    """Dispatch to per-table type-specific classifier.

    Returns ``(classification, signal)`` if the table has a strong
    type-specific signal; ``None`` if no signal applies (caller falls
    through to ID-prefix + content scan).

    Per Codex ``-008`` Finding 1: the originally promised type-specific
    override layer. Implemented for ``tests`` (path-based) and
    ``deliberations`` (origin_project-based). Explicitly absent for
    other versioned tables — see module docstring "Type-Specific
    Override Decisions".
    """
    if table_name == "tests":
        return _classify_test_path(type_columns.get("test_file"))
    if table_name == "deliberations":
        return _classify_deliberation_origin(type_columns.get("origin_project"))
    return None


def _enumerate_versioned_table(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    """Enumerate ``(id, versions[], classification)`` for a versioned table.

    One entry per unique ``id``; ``versions`` is the sorted list of
    ``version`` values that exist for that id.

    Classification cascade per Codex ``-008`` Finding 1:
      1. Type-specific signal (table-specific column scan; e.g.,
         ``tests.test_file`` path or ``deliberations.origin_project``).
      2. Fall through: ID prefix + generic content scan across
         ``_CONTENT_BEARING_COLUMNS``.

    For type-specific columns, a per-id representative value is taken
    as the first non-null value across version rows (typically all
    versions of the same id share these values).
    """
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info("{table_name}")')
    columns = [c[1] for c in cur.fetchall()]
    content_cols = [c for c in _CONTENT_BEARING_COLUMNS if c in columns]
    type_cols = [c for c in _TABLE_SPECIFIC_TYPE_COLUMNS.get(table_name, ()) if c in columns]
    id_col = "event_id" if "event_id" in columns else "id"
    select_cols = [id_col, "version", *content_cols, *type_cols]
    select_list = ", ".join(select_cols)
    cur.execute(f'SELECT {select_list} FROM "{table_name}" ORDER BY {id_col}, version')
    rows = cur.fetchall()

    n_content = len(content_cols)

    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_id = row[0]
        version = row[1]
        content_values = row[2 : 2 + n_content]
        type_values = row[2 + n_content : 2 + n_content + len(type_cols)]
        content_blob = " ".join(str(v) for v in content_values if v is not None)
        if row_id not in by_id:
            by_id[row_id] = {
                "id": row_id,
                "versions": [],
                "content_blob": [],
                # Per-id type-column representative: first non-null value
                # observed across version rows.
                "type_columns": {col: None for col in type_cols},
            }
        by_id[row_id]["versions"].append(version)
        by_id[row_id]["content_blob"].append(content_blob)
        for col_name, value in zip(type_cols, type_values, strict=False):
            if value is not None and by_id[row_id]["type_columns"].get(col_name) is None:
                by_id[row_id]["type_columns"][col_name] = value

    entries: list[dict[str, Any]] = []
    for row_id, data in by_id.items():
        # Tier 1 — type-specific signal.
        type_specific = _classify_by_type_specific_signal(table_name, data["type_columns"])
        if type_specific is not None:
            classification, signal = type_specific
        else:
            # Tier 2 — ID prefix + content scan fallback.
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
