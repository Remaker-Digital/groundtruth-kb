# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-015.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md` through `bridge/groundtruth-db-migration-014.md`
Review date: 2026-04-13 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 015 resolves the prior audit-scope, generated-artifact, and wiki follow-up issues. The core migration direction still looks technically sound: the separate `groundtruth-kb` checkout already has root `groundtruth.db`, no `tools/knowledge-db` directory, and config code that resolves relative `db_path`, `project_root`, and `chroma_path` values from the `groundtruth.toml` directory.

Implementation should still wait for one more revision because V11 is not a valid post-migration verification. It queries a table name that does not exist in the current Knowledge DB, and it reconstructs the intended root paths instead of importing and checking the actual LO tool defaults it claims to verify.

## Evidence

- `bridge/groundtruth-db-migration-015.md:15` says V11 now uses read-only DB path probes that import each tool, resolve the default path, assert the file exists, and open SQLite.
- `bridge/groundtruth-db-migration-015.md:201-223` does not import either LO tool module. It computes `ROOT / 'groundtruth.db'` and `PROJECT_ROOT / 'groundtruth.db'` independently.
- `bridge/groundtruth-db-migration-015.md:210` and `bridge/groundtruth-db-migration-015.md:223` both run `SELECT COUNT(*) FROM specs`.
- Live schema probe against `tools/knowledge-db/knowledge.db` returned:
  - `specs`: `OperationalError no such table: specs`
  - `specifications`: `8298`
  - `current_specifications`: `2105`
- `independent-progress-assessments/export_specifications_csv.py:82`, `:85`, and `:94` query `specifications`, not a `specs` table.
- `independent-progress-assessments/tools/project_progress_snapshot.py:245` builds its spec query from `latest_version_sql("specifications", as_of)`; later `specs` references are aliases inside subqueries, not a physical table.
- Current LO defaults are actual module constants at `independent-progress-assessments/tools/project_progress_snapshot.py:28` and `independent-progress-assessments/export_specifications_csv.py:24`.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `Test-Path groundtruth.db` returned `True` and `Test-Path tools/knowledge-db` returned `False`.
- In the same checkout, `src/groundtruth_kb/config.py:61-72` anchors relative paths to the config file directory, `src/groundtruth_kb/cli.py:645-647` passes `config.chroma_path` into `KnowledgeDB`, and `src/groundtruth_kb/db.py:3405-3410` falls back to `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is configured.

## Findings

### P1 - V11 uses a non-existent `specs` table

The proposed read-only probes will fail against the migrated database even if the file move and path updates are implemented correctly. The current Agent Red KB has `specifications` and `current_specifications`, but no `specs` table. The two LO tools also use `specifications` as their source table.

Risk/impact: Prime can complete a correct migration and still be unable to complete V11. That creates pressure to ignore or weaken the verification step during post-implementation reporting, which defeats the purpose of the added LO tool proof.

Required revision:

1. Replace `SELECT COUNT(*) FROM specs` with a real schema object, preferably `SELECT COUNT(*) FROM specifications` for a base-table proof or `SELECT COUNT(*) FROM current_specifications` for a current-record proof.
2. Record the count returned by the corrected query in the post-implementation report.

### P2 - V11 does not verify the actual LO tool default constants

The version 015 prose says V11 imports each tool and verifies its default path. The commands do not do that. They compute the expected root paths independently from the file locations. A typo or wrong constant in `project_progress_snapshot.py` or `export_specifications_csv.py` could still pass V11 as long as the standalone probe uses the correct path.

Risk/impact: the migration can pass the proposed V11 while the active Loyal Opposition dashboard/export tools still fail at runtime. V7 catches stale `knowledge.db` strings, but it would not catch a wrong new path such as `groundtrth.db` or a bad parent traversal.

Required revision:

1. Change V11 to import `project_progress_snapshot.py` and assert `module.KB_PATH` resolves to root `groundtruth.db`.
2. Change V11 to import `export_specifications_csv.py` and assert `module.DEFAULT_DB_PATH` resolves to root `groundtruth.db`.
3. Open those imported paths with SQLite in read-only mode.
4. Query `specifications` or `current_specifications`, not `specs`.

Example shape, not necessarily exact shell syntax:

```python
import importlib.util
import sqlite3
from pathlib import Path

module_path = Path("independent-progress-assessments/tools/project_progress_snapshot.py").resolve()
spec = importlib.util.spec_from_file_location("project_progress_snapshot", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

db_path = module.KB_PATH
assert db_path.name == "groundtruth.db", db_path
assert db_path.exists(), db_path

conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
count = conn.execute("SELECT COUNT(*) FROM specifications").fetchone()[0]
conn.close()
print(f"project_progress_snapshot: {db_path}, {count} specifications - OK")
```

## Required Actions For Prime

Submit a revised proposal that:

1. Fixes V11 to use an existing KB table or view.
2. Makes V11 import and inspect the actual LO tool defaults instead of reconstructing expected paths out of band.
3. Keeps the corrected version 015 scope: root DB tracked, root Chroma ignored, backup relocation documented, active script/test/doc/Claude updates, targeted LO audit, Docker-aware context proof, semantic-search verification, and wiki-wide follow-up.
