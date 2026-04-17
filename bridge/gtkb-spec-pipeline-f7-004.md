# NO-GO: F7 Session Health Dashboard v2 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f7-003.md  
**Prior review:** bridge/gtkb-spec-pipeline-f7-002.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The phased dashboard design and existing-metrics baseline are sound. The proposal is still not implementation-ready because the threshold persistence example does not match the current environment-config API, and the new snapshot table has no export/import contract.

## Findings

### 1. Blocking: threshold persistence uses the existing API incorrectly

**Claim:** Thresholds can be stored in `environment_config` with `insert_env_config()` and retrieved with `get_env_config()`.

**Evidence:**
- F7 v2 proposes storing thresholds with `kdb.insert_env_config(key="health_thresholds", value=..., changed_by=..., change_reason=...)` at bridge/gtkb-spec-pipeline-f7-003.md:51-76.
- Current `insert_env_config()` requires positional `id`, `environment`, `category`, `key`, `value`, `changed_by`, and `change_reason` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1010-1022.
- Current `get_env_config()` retrieves by config ID, not key, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1077-1080.
- Direct verification of the proposal's sample call produced: `TypeError: KnowledgeDB.insert_env_config() missing 3 required positional arguments: 'id', 'environment', and 'category'`.

**Risk/impact:** The health threshold API fails as specified, or implementers create ad hoc config rows with inconsistent IDs and categories.

**Required action:** Define the exact row contract, for example `id='health-thresholds'`, `environment='shared'`, `category='health'`, `key='health_thresholds'`, and retrieve by the same `id`. Add tests for default fallback, insert, update, and retrieval.

### 2. Major: `session_snapshots` is not included in backup/restore scope

**Claim:** F7 stores snapshots for trends and `gt health trends`.

**Evidence:**
- F7 v2 adds `session_snapshots` at bridge/gtkb-spec-pipeline-f7-003.md:104-136.
- The implementation sequence adds the table and CLI but not export/import at bridge/gtkb-spec-pipeline-f7-003.md:140-151.
- Current `export_json()` uses a hard-coded table list at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2565-2585.
- Current CLI import uses a separate hard-coded `_IMPORTABLE_TABLES` allowlist at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317-334.

**Risk/impact:** Health trend history disappears on a standard GT-KB export/import, while thresholds survive through `environment_config`. That splits the dashboard state across portable and non-portable storage.

**Required action:** Add `session_snapshots` to export/import scope and add a roundtrip test, or explicitly document snapshots as disposable cache and remove durable trend claims.

## Verification

- `python -m pytest tests/test_web_pipeline.py -q --tb=short` passed: `10 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.

## Conditions For GO

1. Correct the environment-config threshold storage contract against current API signatures.
2. Define export/import behavior for `session_snapshots`.
3. Add tests for threshold persistence and snapshot backup/restore behavior.
