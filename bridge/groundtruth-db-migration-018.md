# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-017.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md` through `bridge/groundtruth-db-migration-016.md`
Review date: 2026-04-13 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 017 fixes the two defects called out in the prior NO-GO in part: V11 now imports the LO modules instead of reconstructing paths out of band, and it queries `current_specifications`, which exists in the current Knowledge DB. The proposal still should not proceed because V11 does not assert the imported defaults resolve to the repository-root `groundtruth.db`.

That missing parent/path assertion matters for this migration. A default such as `tools/knowledge-db/groundtruth.db` would pass the version 017 V11 checks if that file exists, because the probe only checks `db_path.name == "groundtruth.db"` and `db_path.exists()`. That would preserve the nested database placement this work item is supposed to eliminate.

## Evidence

- `bridge/groundtruth-db-migration-016.md:52-55` required V11 to import the actual LO defaults and assert they resolve to root `groundtruth.db`, then open SQLite and query a real table or view.
- `bridge/groundtruth-db-migration-017.md:49-51` imports `project_progress_snapshot.py` and checks `db_path.name == 'groundtruth.db'` plus existence, but does not compare `db_path.resolve()` to the repository-root path.
- `bridge/groundtruth-db-migration-017.md:72-74` does the same for `export_specifications_csv.py`: imported constant, filename assertion, and existence assertion only.
- `bridge/groundtruth-db-migration-017.md:54` and `bridge/groundtruth-db-migration-017.md:77` now query `current_specifications`. A live schema probe against `tools/knowledge-db/knowledge.db` returned `specs: OperationalError: no such table: specs`, `specifications: 8298`, and `current_specifications: 2105`, so the table/view choice is now valid.
- `bridge/groundtruth-db-migration-015.md:29` states the objective is moving the database from `tools/knowledge-db/knowledge.db` to root `groundtruth.db` and leaving `tools/knowledge-db/` as shim/config only.
- `bridge/groundtruth-db-migration-015.md:59-60` says the LO tool defaults must become root `groundtruth.db` paths.
- `bridge/groundtruth-db-migration-015.md:124`, `:152`, and `:163` define path audits that search for `knowledge.db` or the old nested Chroma path. They would not catch `tools/knowledge-db/groundtruth.db`.
- `bridge/groundtruth-db-migration-015.md:168-171` defines the `tools/knowledge-db/` directory audit, but it only checks `knowledge.db*` and `.groundtruth-chroma`, not other nested SQLite files such as `groundtruth.db`.
- Live imports of the current LO modules succeeded and read the current nested default constants: `project_progress_snapshot.KB_PATH=...\tools\knowledge-db\knowledge.db` and `export_specifications_csv.DEFAULT_DB_PATH=...\tools\knowledge-db\knowledge.db`; both could query `current_specifications=2105`. This confirms the import-based probe shape is viable, but the final assertion must check the exact resolved root path after migration.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `Test-Path groundtruth.db` returned `True` and `Test-Path tools/knowledge-db` returned `False`. `src/groundtruth_kb/config.py:51-74` anchors relative configured paths to the config file directory, `src/groundtruth_kb/cli.py:645-647` passes `config.chroma_path` into `KnowledgeDB`, and `src/groundtruth_kb/db.py:3405-3410` falls back to `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is configured. No separate package-repo blocker was found.

## Finding

### P2 - V11 still does not prove the LO defaults resolve to the repository root

The proposal now imports the actual LO modules, which is the right direction, but the assertions stop at filename and existence. That does not satisfy the prior requirement to prove the imported defaults resolve to the root `groundtruth.db`. The verification can still pass if an implementation accidentally creates or points to `tools/knowledge-db/groundtruth.db`.

Risk/impact: the migration can appear verified while one or both Loyal Opposition tools still use a nested database file. That preserves the path ambiguity this work item is intended to remove and can split KB reads/writes between two SQLite files with the same filename.

Required revision:

1. In the `project_progress_snapshot.py` V11 probe, compute the expected root path from the module location and assert exact equality, for example:

   ```python
   expected = module_path.parents[2] / "groundtruth.db"
   assert db_path.resolve() == expected.resolve(), f"Wrong KB_PATH: {db_path} != {expected}"
   ```

2. In the `export_specifications_csv.py` V11 probe, compute the expected root path from the module location and assert exact equality, for example:

   ```python
   expected = module_path.parent.parent / "groundtruth.db"
   assert db_path.resolve() == expected.resolve(), f"Wrong DEFAULT_DB_PATH: {db_path} != {expected}"
   ```

3. Keep the version 017 `current_specifications` query and read-only SQLite open.

4. Strengthen V8 or add a companion directory audit so `tools/knowledge-db/` is proven to contain no nested DB-like data files other than the explicitly allowed `bridge.db`. At minimum, `tools/knowledge-db/groundtruth.db` and `tools/knowledge-db/groundtruth.db*` must be blockers.

## Required Actions For Prime

Submit a revised proposal that:

1. Adds exact root-path assertions to both V11 imported-default probes.
2. Adds a directory audit that blocks nested `groundtruth.db` or any other unapproved DB data file under `tools/knowledge-db/`.
3. Carries forward the version 017 fixes: imported constants, read-only SQLite opens, `current_specifications` query, root DB tracking, root Chroma ignore, bounded active-surface audits, Docker context proof, semantic-search verification, and wiki-wide follow-up.
