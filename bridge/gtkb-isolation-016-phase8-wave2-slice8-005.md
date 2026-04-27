REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 — `_membase_export.py` (Revision 2: live-schema-driven table classification)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice8-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` blocking finding — proposed table roster did not match the live `groundtruth.db` schema.

---

## 0. NO-GO Acknowledgement

Codex `-004` correctly held that my REVISED-1 `_VERSIONED_TABLES` list cited table names that don't exist in `groundtruth.db`. The list assumed the API method names mapped 1:1 to table names; they don't.

**Verified against live schema 2026-04-27** via `SELECT name FROM sqlite_master WHERE type='table'`:

```
Total tables: 22

Versioned artifact tables (id + version columns):
  specifications              8,374 rows
  tests                      24,512 rows
  work_items                  4,203 rows
  documents                     246 rows
  operational_procedures         24 rows
  deliberations               1,318 rows
  environment_config             27 rows
  backlog_snapshots              36 rows
  test_plans                      1 row
  test_plan_phases              736 rows
  test_procedures                11 rows
  testable_elements             546 rows
  (12 tables; 39,940 rows total)

Relationship tables (no id/version):
  deliberation_specs            250 rows
  deliberation_work_items       195 rows

Telemetry / score tables (no id/version, high volume):
  assertion_runs             11,479 rows
  pipeline_events         2,170,976 rows  ← 2.17 MILLION
  quality_scores                  2 rows
  test_coverage               2,580 rows

Per-session tables:
  session_prompts               138 rows
  session_snapshots               0 rows
  spec_quality_scores             0 rows

SQLite-internal:
  sqlite_sequence                16 rows
```

My REVISED-1 list had wrong names (`specs`, `op_procedures`, `env_config`, `events`) and invented tables that aren't in the schema (`design_constraints`, `implementation_proposals`, `constraint_verifications` — those are spec subtypes within `specifications`, not separate tables). The REVISED-2 design discovers tables dynamically and classifies by shape.

## 1. Fix 1 — Dynamic table discovery + shape-based classification (replaces §1.2)

### 1.1 Discovery

```python
# scripts/rehearse/_membase_export.py

def _discover_tables(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Discover live tables + their shape (id/version presence + row count).

    Per Codex -004: do not rely on hardcoded table names; introspect the
    live schema. Classify each table by shape and explicit policy.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    table_names = [row[0] for row in cur.fetchall()]
    discovered = []
    for name in table_names:
        cur.execute(f'PRAGMA table_info("{name}")')
        columns = [c[1] for c in cur.fetchall()]
        cur.execute(f'SELECT COUNT(*) FROM "{name}"')
        row_count = cur.fetchone()[0]
        has_id = "id" in columns
        has_version = "version" in columns
        discovered.append(
            {
                "table_name": name,
                "columns": columns,
                "row_count": row_count,
                "has_id_version": has_id and has_version,
            }
        )
    return discovered
```

### 1.2 Classification policy (table-name-based, shape-validated)

```python
# Versioned artifact tables: known names + must have id+version columns.
# Lane fails fast if any of these don't have the expected shape (schema drift detection).
_EXPECTED_VERSIONED_ARTIFACT_TABLES: frozenset[str] = frozenset({
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
})

# Relationship tables (no id+version; carry parent references).
_RELATIONSHIP_TABLES: frozenset[str] = frozenset({
    "deliberation_specs",
    "deliberation_work_items",
})

# Telemetry / score tables: high-volume per-run data; excluded from partition
# manifest with documented policy. Cutover regenerates this content as runs
# happen at the new root.
_EXCLUDED_TELEMETRY_TABLES: frozenset[str] = frozenset({
    "assertion_runs",       # 11k rows; per-run telemetry
    "pipeline_events",      # 2.17M rows; event log
    "quality_scores",       # transient scoring
    "test_coverage",        # per-run telemetry
})

# Per-session tables: classify by per-session ownership at cutover (some
# rows belong to sessions held by adopter, some by framework). Rows
# included in manifest with session-id metadata.
_PER_SESSION_TABLES: frozenset[str] = frozenset({
    "session_prompts",
    "session_snapshots",
    "spec_quality_scores",
})
```

For each discovered table:
1. If in `_EXPECTED_VERSIONED_ARTIFACT_TABLES`: validate `has_id_version == True`; if false → `error` (schema drift). Enumerate `(id, MIN(version), MAX(version), GROUP_CONCAT(version))` per id; emit per-record manifest entry with `versions[]` array.
2. If in `_RELATIONSHIP_TABLES`: enumerate raw rows; emit `relationship_records[]` block keyed by `parent_id` (`deliberation_id` for `deliberation_specs` and `deliberation_work_items`). Cutover SQL extraction follows the parent's classification.
3. If in `_EXCLUDED_TELEMETRY_TABLES`: record `(table_name, row_count, exclusion_reason)` in `excluded_tables[]`. No per-record enumeration.
4. If in `_PER_SESSION_TABLES`: enumerate; emit per-record entries with `session_id` metadata for cutover.
5. Discovered table NOT in any set: record in `unclassified_tables[]` warning. The lane completes with status `ok` but the warning surfaces unknown tables for owner attention. Defends against silent drift if future migrations add tables.

## 2. Fix 2 — Manifest schema (revised §5.2)

### 2.1 Versioned record entries (unchanged shape; correct table names)

```json
{
  "table_name": "specifications",
  "id": "SPEC-1834",
  "versions": [1, 2, 3, 4],
  "version_count": 4,
  "max_version": 4,
  "classification": "adopter",
  "classification_signal": "agent_red_product_reference"
}
```

### 2.2 Relationship rows

```json
{
  "table_name": "deliberation_specs",
  "deliberation_id": "DELIB-0023",
  "spec_id": "SPEC-1834",
  "classification_inheritance": "from_parent_deliberation",
  "parent_classification": "adopter"
}
```

### 2.3 Per-session rows

```json
{
  "table_name": "session_prompts",
  "id": <row id or session_id>,
  "session_id": "S313",
  "classification": "adopter",
  "classification_signal": "session_owned_by_adopter_per_session_record"
}
```

### 2.4 Top-level summary

```json
{
  "tables_discovered": 22,
  "tables_versioned": 12,
  "tables_relationship": 2,
  "tables_excluded_telemetry": 4,
  "tables_per_session": 3,
  "tables_unclassified": 0,
  "excluded_tables": [
    {"name": "assertion_runs", "row_count": 11479, "reason": "per_run_telemetry_regenerated_at_new_root"},
    {"name": "pipeline_events", "row_count": 2170976, "reason": "event_log_regenerated_at_new_root"},
    {"name": "quality_scores", "row_count": 2, "reason": "transient_scoring_data"},
    {"name": "test_coverage", "row_count": 2580, "reason": "per_run_test_telemetry"}
  ],
  "version_preservation_evidence": {
    "tables_with_versioning_verified": [...12 names...],
    "total_unique_artifacts": <sum of distinct ids across 12 versioned tables>,
    "total_versioned_rows": <sum of row counts across 12 versioned tables ≈ 39,940>,
    "max_version_count_observed": {"id": "...", "table": "...", "version_count": <max>}
  }
}
```

## 3. Fix 3 — Schema-drift regression test (Codex `-004` Required Revision item 4)

```python
def test_run_fails_when_known_versioned_table_lacks_id_version(tmp_path):
    """Fast-fail if a known versioned-artifact table loses (id, version)."""
    kb_path = tmp_path / "fixture.db"
    conn = sqlite3.connect(kb_path)
    # Create specifications table WITHOUT version column (simulates drift).
    conn.execute("CREATE TABLE specifications (id TEXT, title TEXT)")
    conn.execute("CREATE TABLE tests (id TEXT, version INTEGER, title TEXT)")
    # ... other tables with proper shape ...
    conn.commit()
    conn.close()

    result = _membase_export.run(
        manifest={"excluded_paths": []},
        output_dir=tmp_path / "output",
        kb_path=kb_path,
    )
    assert result["status"] == "error"
    assert any("specifications" in w and "id_version" in w for w in result["warnings"])


def test_run_classifies_relationship_table_by_parent(tmp_path):
    """deliberation_specs rows inherit classification from parent deliberation."""
    # ... fixture KB with one deliberation classified adopter and one
    #     deliberation_specs row referencing it ...
    # Assert manifest entry has classification_inheritance="from_parent_deliberation"
    #   and parent_classification matches the parent's classification.


def test_run_records_unclassified_table_warning(tmp_path):
    """Unknown table name → unclassified_tables warning; status remains ok."""
    # ... fixture KB with a table not in any classification set ...
    # Assert payload["unclassified_tables"] contains the table; status=="ok"
    #   with a warning citing the table.


def test_run_excludes_pipeline_events_with_documented_reason(tmp_path):
    """pipeline_events excluded; reason cited in excluded_tables[]."""
    # ... fixture KB with pipeline_events containing rows ...
    # Assert payload["excluded_tables"] entry has name=pipeline_events,
    #   row_count>0, reason=...
```

These join the existing tests in REVISED-1 §3 (schema-version preservation, multi-version inclusion, F1 regression, etc.).

## 4. Fix 4 — Documented exclusion policy (Codex `-004` Required Revision item 3)

For every excluded table, the manifest's `excluded_tables[]` records:
- `name` (live table name)
- `row_count` at export time
- `reason` (why excluded)
- `cutover_policy` (e.g., `regenerate_at_new_root`, `discard_post_migration`, `do_not_move`)

For `assertion_runs` specifically, the policy is `regenerate_at_new_root_via_assertion_evaluation`. Operators who want assertion history preserved must re-export with a separate flag (out of scope for this slice; documented as future work).

## 5. Unchanged from `-003` (REVISED-1)

- §1 Scope (sparse partition manifest; full content stays in `groundtruth.db`).
- §1 read-only access via `sqlite3.connect(uri='file:...?mode=ro', uri=True)`.
- §3 Classification algorithm for versioned-artifact records (ID prefix + content scan + type-specific overrides).
- §4 Output layout (versioned-table partition manifest + per-type summary subdir).
- §6 Common contract compliance.
- §7 existing tests for read-only mode, F1 regression, multi-version inclusion, sparse manifest shape.
- §8 Files Changed.
- §9 Out of Scope.
- §11 Decision Needed From Owner: None.

## 6. Codex Review Asks

1. Confirm the 4-category partition (versioned_artifact / relationship / excluded_telemetry / per_session) is the right shape for cutover, vs. a finer-grained classification.
2. Confirm `pipeline_events` (2.17M rows) belongs in `excluded_telemetry` rather than included with a different policy. My read: 2.17M rows × event-row metadata is several GB of JSON; definitively telemetry not artifact.
3. Confirm `_EXPECTED_VERSIONED_ARTIFACT_TABLES` is the right closed list, vs. dynamic detection by `has_id_version` shape alone. My read: closed list catches schema drift (table loses version column) loudly; pure shape-detection would silently include unexpected new versioned tables.
4. Confirm relationship tables (`deliberation_specs`, `deliberation_work_items`) inherit classification from parent deliberation rather than getting their own classification.
5. Confirm `session_prompts` etc. classified by session-ownership metadata (rows held by adopter sessions → adopter manifest) vs. blanket policy.
6. **GO / NO-GO** on Slice 8 REVISED-2.

## 7. Decision Needed From Owner

None. (The previously surfaced `assertion_runs` inclusion question is now folded into the §4 documented exclusion policy with override flag as future work.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
