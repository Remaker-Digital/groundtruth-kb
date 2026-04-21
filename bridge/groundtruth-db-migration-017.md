# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v8)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-13
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 2 findings in `bridge/groundtruth-db-migration-016.md` (Codex NO-GO #8)

## NO-GO #8 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | V11 queries non-existent `specs` table; real table is `specifications` | P1 | Fixed to `SELECT COUNT(*) FROM current_specifications` |
| 2 | V11 reconstructs paths independently instead of importing actual LO tool defaults | P2 | Fixed: uses `importlib.util` to load each LO module, reads `module.KB_PATH` / `module.DEFAULT_DB_PATH`, asserts name and existence, opens with SQLite read-only |

## Cumulative NO-GO Resolution

All 18 findings from eight NO-GO reviews addressed. Carries forward all v015 implementation scope unchanged — only V11 verification is modified.

## Prior Deliberations

NO-GO versions: -002, -004, -006, -008, -010, -012, -014, -016

## Objective, Scope (Phases 1–5), Explicitly NOT Changed, Follow-up Actions, Rollback, Risk Assessment

**Identical to version 015.** No implementation scope changes. Only V11 is revised below. For full scope reference, see `bridge/groundtruth-db-migration-015.md`.

## Verification Plan

### V1–V10. Unchanged from v015

**V1.** Git tracking. **V2.** Smoke test. **V3.** Web UI. **V4.** Semantic search. **V5.** Test suite (16 passed, record count). **V6.** Assertion hook. **V7.** Bounded path audit (targeted LO paths, `.claude/` scan). **V8.** Directory audit. **V9.** Root file state. **V10.** Docker context verification.

### V11. LO tool DB path verification (addresses NO-GO #8 findings 1+2)

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
assert db_path.name == 'groundtruth.db', f'Wrong DB name: {db_path.name}'
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
assert db_path.name == 'groundtruth.db', f'Wrong DB name: {db_path.name}'
assert db_path.exists(), f'DB not found at {db_path}'

conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
count = conn.execute('SELECT COUNT(*) FROM current_specifications').fetchone()[0]
conn.close()
print(f'export_specifications_csv: DEFAULT_DB_PATH={db_path}, {count} current specs - OK')
"
```

Both probes must:
1. Import the actual module (not reconstruct paths independently)
2. Read the module's own default constant (`KB_PATH` / `DEFAULT_DB_PATH`)
3. Assert the filename is `groundtruth.db`
4. Assert the file exists at the resolved path
5. Open it read-only and query `current_specifications`
6. Print the count and "OK"

Any assertion error, missing file, or `OperationalError` is a **blocker**. Record both counts in the post-implementation report.
