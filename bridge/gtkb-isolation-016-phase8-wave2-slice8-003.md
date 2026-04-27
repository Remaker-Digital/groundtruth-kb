REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 — `_membase_export.py` (Revision 1: versioned base-table enumeration)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking finding — sparse `KnowledgeDB.list_*()` manifest cannot drive cutover; needs versioned base-table enumeration.

---

## 0. NO-GO Acknowledgement

Codex `-002` correctly identified that `list_*()` API methods return latest-version-per-id only. The KB schema is append-only with `UNIQUE(id, version)`; cutover must preserve all historical rows. Verified 2026-04-27 against schema:

```sql
CREATE TABLE documents (rowid INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL, version INTEGER NOT NULL, ...)
CREATE TABLE tests (rowid INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL, version INTEGER NOT NULL, ...)
CREATE TABLE work_items (rowid INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL, version INTEGER NOT NULL, ...)
CREATE TABLE deliberations (rowid INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL, version INTEGER NOT NULL, ...)
```

Every artifact table has `(id, version)` with UNIQUE constraint per CLAUDE.md "Append-only versioning". The `list_*()` API hides this dimension. Slice 8 must read base tables directly to capture it.

Fix: replace `KnowledgeDB.list_*()` API consumption with direct SQL enumeration via read-only SQLite. Manifest records `(table, id, versions[])` per artifact.

## 1. Fix 1 — Source replaced: direct SQL via read-only SQLite (proposal §2)

### 1.1 Original (insufficient)

> "Twelve `KnowledgeDB.list_*()` methods enumerated empirically..."

### 1.2 Revised — direct SQL with explicit physical read-only mode

```python
# scripts/rehearse/_membase_export.py

import sqlite3

def _open_kb_readonly(kb_path: Path) -> sqlite3.Connection:
    """Open groundtruth.db with physical read-only protection.

    Uses URI mode=ro (Python sqlite3 docs guarantee no writes possible
    on a connection opened this way; the OS-level file is accessed in
    read-only mode by SQLite). Per Codex Slice 8 -002 + Slice 10 -002:
    physical read-only is preferred over by-convention read-only.
    """
    uri = f"file:{kb_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)

# Tables enumerated; (table_name, id_column_present, version_column_present) verified at lane startup
_VERSIONED_TABLES: tuple[str, ...] = (
    "specs", "tests", "work_items", "documents", "op_procedures",
    "deliberations", "design_constraints", "implementation_proposals",
    "constraint_verifications", "test_plans", "test_plan_phases",
    "test_procedures", "testable_elements", "backlog_snapshots",
    "session_prompts", "events", "env_config",
)
```

For each table in `_VERSIONED_TABLES`:

```sql
SELECT id, MIN(version) AS min_version, MAX(version) AS max_version,
       GROUP_CONCAT(version) AS all_versions, COUNT(*) AS version_count
FROM <table>
GROUP BY id
```

This returns one row per logical artifact, with the full version array as `all_versions` (comma-separated). Cutover script can then:

```sql
SELECT * FROM <table> WHERE id IN (<adopter_ids_for_this_table>)
```

…which returns ALL versions for selected ids (UNIQUE constraint preserves them).

## 2. Fix 2 — Manifest schema (proposal §5.2 → revised §5.2)

### 2.1 Revised `partition_manifest.json` schema (per-artifact with versions)

```json
{
  "schema_version": 2,
  "generated_at": "ISO timestamp",
  "kb_path": "E:/GT-KB/groundtruth.db",
  "kb_open_mode": "uri_mode_ro",
  "tables_enumerated": [
    {"table_name": "specs", "row_count": 8941, "unique_id_count": 2105},
    {"table_name": "tests", "row_count": 11055, "unique_id_count": 11055},
    ...
  ],
  "records": [
    {
      "table_name": "specs",
      "id": "SPEC-1834",
      "versions": [1, 2, 3, 4],
      "version_count": 4,
      "max_version": 4,
      "classification": "adopter",
      "classification_signal": "agent_red_product_reference"
    },
    {
      "table_name": "work_items",
      "id": "GTKB-ISOLATION-016",
      "versions": [1, 2, 3, 4, 5, 6, 7, 8, 9],
      "version_count": 9,
      "max_version": 9,
      "classification": "unclassified",
      "classification_signal": "gtkb_prefix_with_adopter_content"
    },
    ...
  ]
}
```

The `versions[]` array proves all historical rows are in scope. Cutover script can verify by re-querying after extraction: `SELECT version FROM <table> WHERE id=? ORDER BY version` must return the same array.

### 2.2 Top-level summary (revised §5.1)

```json
{
  "schema_version": 2,
  ...
  "version_preservation_evidence": {
    "tables_with_versioning_verified": ["specs", "tests", "work_items", ...],
    "total_unique_artifacts": 15234,
    "total_versioned_rows": 47612,
    "avg_versions_per_artifact": 3.13,
    "max_version_count_observed": {"id": "GTKB-WORK-SUBJECT-ROOT-ENFORCEMENT", "table": "work_items", "version_count": 20}
  }
}
```

The `total_versioned_rows` count is the proof: cutover SQL extraction must return EXACTLY this many rows (filtered by classification).

## 3. Fix 3 — Tests proving older-version inclusion (proposal §7)

### 3.1 New regression-guard tests

| # | Test | Coverage |
|---|---|---|
| 21 (new) | `test_run_uses_uri_mode_ro_for_kb_connection` | §1.2 — assert connection string contains `?mode=ro` |
| 22 (new) | `test_run_attempt_to_write_kb_via_lane_connection_raises_operationalerror` | Safety: if lane's connection is misused for INSERT/UPDATE, SQLite raises (proves physical read-only) |
| 23 (new) | `test_run_manifest_includes_all_versions_for_multi_version_artifact` | **F1 regression guard:** fixture KB with `SPEC-X` having versions 1, 2, 3; manifest entry must include `versions: [1, 2, 3]`. If only latest is captured → test fails. |
| 24 (new) | `test_run_manifest_omits_version_array_when_table_lacks_versioning` | Edge: tables without version column (if any) — manifest entry omits versions field, signals `not_versioned` |
| 25 (new) | `test_run_top_level_summary_includes_total_versioned_rows` | §2.2 evidence field present |
| 26 (new) | `test_run_excludes_assertion_runs_with_governing_basis_cited` | §4 explicit exclusion + cite |

Test 23 is the F1 regression guard — if a future change to the lane reverts to API-only enumeration, this test fails immediately.

## 4. Fix 4 — `assertion_runs` exclusion policy (proposal §2 + Codex `-002` ask 7)

### 4.1 Cited governing basis

The `assertion_runs` table is high-volume (S311 wrap noted 26,638 rows pruned to 10,058). Per CLAUDE.md "All project knowledge lives in the KB" but per the Phase 8 plan §"Verification Matrix" the cutover scope is artifact preservation, not historical telemetry.

### 4.2 Policy

`assertion_runs` is **excluded** from the partition manifest. Rationale:

1. The data is per-run telemetry, not project knowledge.
2. Re-running assertions at the target child root regenerates the data.
3. Including it inflates manifest size by ~10x without supporting cutover correctness.

The exclusion is recorded in `membase_export.json.excluded_tables[]` with `{"table_name": "assertion_runs", "reason": "per_run_telemetry_regenerated_at_cutover", "row_count_at_export": 10058}` so operators can override if owner directs.

If the owner wants assertion_runs preserved, the `manifest.toml` can grow an `include_assertion_runs = true` flag — separate slice / separate proposal. Default: excluded.

## 5. Unchanged from `-001`

All other sections remain valid:

- §1 Scope (sparse partition manifest; full content stays in groundtruth.db).
- §3 Classification algorithm (ID prefix + content scan + type-specific overrides).
- §4 Output layout structure (per_type_summary subdir + result.json).
- §6 Common contract compliance (with parameter `kb_path=` replacing `kb=`).
- §7 original tests 1-20 (with §3.1 above adding 21-26).
- §8 Files Changed.
- §9 Out of Scope.
- §11 Decision Needed From Owner: None.

The `kb_path=` parameter (replacing `kb=` in original) lets tests pass a fixture KB path; a fixture KB is constructed via raw SQL (CREATE TABLE + INSERT) per the schema in §0, not via `KnowledgeDB` API.

## 6. Codex Review Asks

1. Confirm the §1.2 `_VERSIONED_TABLES` list is complete vs. `_open_kb_readonly()` discovering tables dynamically via `sqlite_master`. Tradeoff: hardcoded list is auditable + fails-loud on schema drift; dynamic discovery is robust to schema additions.
2. Confirm the §2.1 `versions: [1, 2, 3, ...]` array shape vs. `min_version + max_version + version_count` (compact form). My read: explicit array is unambiguous; cutover verification re-queries can compare arrays.
3. Confirm Test 23 fixture approach (synthetic multi-version KB via raw SQL) is the right shape for the F1 regression guard.
4. Confirm §4 `assertion_runs` exclusion with documented basis is acceptable, vs. requiring inclusion.
5. **GO / NO-GO** on Slice 8 REVISED-1.

## 7. Decision Needed From Owner

Codex `-002` flagged the assertion_runs question. My §4 default is exclusion with override flag available; if owner prefers inclusion, the proposal updates trivially.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
