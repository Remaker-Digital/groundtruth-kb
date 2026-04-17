# NO-GO: F3 Spec Quality Gate v2 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f3-003.md  
**Prior review:** bridge/gtkb-spec-pipeline-f3-002.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The revised scoring model correctly stops rewarding non-executable assertion names and defines a per-spec persistence table. It is still not implementation-ready because the persistence contract is incomplete: the new table is not integrated into GT-KB's explicit export/import allowlists, and the API accepts a `session_id` that the proposed table does not store.

## Findings

### 1. Blocking: persisted per-spec scores would be dropped by export/import

**Claim:** F3 v2 persists scores in `spec_quality_scores` so F7 can show historical trends.

**Evidence:**
- The proposal introduces `spec_quality_scores` at bridge/gtkb-spec-pipeline-f3-003.md:59-80.
- The implementation sequence only mentions creating the table and scoring APIs at bridge/gtkb-spec-pipeline-f3-003.md:123-126; it does not mention export/import.
- Current `export_json()` uses a hard-coded table list at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2565-2585.
- Current CLI import uses a separate hard-coded `_IMPORTABLE_TABLES` allowlist at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317-334.

**Risk/impact:** Quality history would exist only in the live SQLite file. A normal GT-KB export/import would silently lose the exact trend data F3 is adding for F7.

**Required action:** Add `spec_quality_scores` to export/import scope, include import validation for `flags` JSON, and add tests proving a persisted score survives export/import.

### 2. Major: `session_id` is accepted by the API but not stored

**Claim:** `persist_quality_scores(session_id)` stores session-bound quality scoring.

**Evidence:**
- The proposed API takes `session_id` at bridge/gtkb-spec-pipeline-f3-003.md:84-104.
- The proposed table key and columns are `spec_id`, `spec_version`, `scored_at`, scores, tier, and flags, with no `session_id`, at bridge/gtkb-spec-pipeline-f3-003.md:64-78.
- Current aggregate `quality_scores` table is explicitly keyed by `session_id` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:273-286.

**Risk/impact:** Callers cannot later answer which session produced a persisted per-spec score, even though the method requires a session ID and F7 is expected to reason about session history.

**Required action:** Either add `session_id` to `spec_quality_scores` and tests, or remove the parameter and state that per-spec history is timestamp-only while F7 stores session attribution separately in snapshots.

## Verification

- `python -m pytest tests/test_db.py -q --tb=short` passed: `25 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.

## Conditions For GO

1. Define export/import behavior for `spec_quality_scores`.
2. Resolve whether per-spec quality records are session-attributed or timestamp-only.
3. Add tests for persistence roundtrip through both API retrieval and database export/import.
