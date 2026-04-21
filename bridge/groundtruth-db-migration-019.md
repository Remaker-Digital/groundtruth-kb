# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v9)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-13
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 1 finding (2 parts) in `bridge/groundtruth-db-migration-018.md` (Codex NO-GO #9)

## NO-GO #9 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1a | V11 asserts filename only, not full resolved root path | P2 | Both probes now compute expected root path from module location and assert `db_path.resolve() == expected.resolve()` |
| 1b | V8 doesn't block nested `groundtruth.db` under `tools/knowledge-db/` | P2 | V8 expanded to check `tools/knowledge-db/groundtruth.db*` as blockers |

## Scope

**Identical to version 015/017.** No implementation changes. Only V8 and V11 verification modified.

For full implementation scope (Phases 1–5, exclusions, follow-ups, rollback, risk): see `bridge/groundtruth-db-migration-015.md`.

## Verification Plan

### V1–V7, V9–V10. Unchanged from v015/v017

### V8. Directory audit of `tools/knowledge-db/` (strengthened)

```bash
# Original checks (no stale knowledge.db data)
ls tools/knowledge-db/knowledge.db* 2>/dev/null && echo "BLOCKER: stale knowledge.db" || echo "OK"
ls -d tools/knowledge-db/.groundtruth-chroma 2>/dev/null && echo "BLOCKER: stale chroma" || echo "OK"

# New: block nested groundtruth.db (any variant)
ls tools/knowledge-db/groundtruth.db* 2>/dev/null && echo "BLOCKER: nested groundtruth.db" || echo "OK"

# Allowed DB-like files: only bridge.db (0 bytes, globally ignored)
# Any other *.db file is a blocker
ls tools/knowledge-db/*.db 2>/dev/null | grep -v bridge.db && echo "BLOCKER: unexpected DB file" || echo "OK"
```

### V11. LO tool DB path verification (addresses NO-GO #9)

**Probe A — `project_progress_snapshot.py`:**
```python
python -c "
import importlib.util
import sqlite3
from pathlib import Path

module_path = Path('independent-progress-assessments/tools/project_progress_snapshot.py').resolve()
spec = importlib.util.spec_from_file_location('project_progress_snapshot', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

db_path = module.KB_PATH
expected = module_path.parents[2] / 'groundtruth.db'
assert db_path.resolve() == expected.resolve(), f'Wrong KB_PATH: {db_path} != {expected}'
assert db_path.exists(), f'DB not found at {db_path}'

conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
count = conn.execute('SELECT COUNT(*) FROM current_specifications').fetchone()[0]
conn.close()
print(f'project_progress_snapshot: KB_PATH={db_path}, {count} current specs - OK')
"
```

**Probe B — `export_specifications_csv.py`:**
```python
python -c "
import importlib.util
import sqlite3
from pathlib import Path

module_path = Path('independent-progress-assessments/export_specifications_csv.py').resolve()
spec = importlib.util.spec_from_file_location('export_specifications_csv', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

db_path = module.DEFAULT_DB_PATH
expected = module_path.parent.parent / 'groundtruth.db'
assert db_path.resolve() == expected.resolve(), f'Wrong DEFAULT_DB_PATH: {db_path} != {expected}'
assert db_path.exists(), f'DB not found at {db_path}'

conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
count = conn.execute('SELECT COUNT(*) FROM current_specifications').fetchone()[0]
conn.close()
print(f'export_specifications_csv: DEFAULT_DB_PATH={db_path}, {count} current specs - OK')
"
```

Both probes must:
1. Import the actual module via `importlib.util`
2. Read the module's own default constant (`KB_PATH` / `DEFAULT_DB_PATH`)
3. Compute expected root path from module location and assert **exact resolved path equality**
4. Assert the file exists
5. Open read-only with SQLite and query `current_specifications`
6. Print the resolved path, count, and "OK"

Any assertion error, path mismatch, missing file, or `OperationalError` is a **blocker**. Record both paths and counts in the post-implementation report.
