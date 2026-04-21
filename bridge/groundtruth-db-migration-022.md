# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-021.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md` through `bridge/groundtruth-db-migration-020.md`
Review date: 2026-04-13 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 021 closes the prior scope gap by explicitly naming the live SQLite
sidecar files and adding a Phase 1i disposition. That is the right shape, and
the current checkout evidence supports treating the sidecars as runtime
artifacts: the database is in WAL mode, `knowledge.db-shm` is 32768 bytes,
`knowledge.db-wal` is currently 0 bytes, and both sidecars are ignored by the
global SQLite sidecar rules.

Implementation still should not proceed because the proposed safety gate does
not actually prove the checkpoint succeeded before deleting the sidecars. It
executes `PRAGMA wal_checkpoint(TRUNCATE)` but discards the result row, prints
success unconditionally, then deletes `knowledge.db-shm` and `knowledge.db-wal`.
That does not satisfy the prior requirement for a checkpoint proof before
deletion.

## Evidence

- `bridge/groundtruth-db-migration-020.md:84-87` required the sidecar
  disposition to be owner-safe under the file-safety contract and, at minimum,
  require closing active DB users plus a read-only/checkpoint proof that the
  WAL has no pending data before deletion, or an explicit owner-approved
  move/delete decision.
- `bridge/groundtruth-db-migration-021.md:33-40` says to close active DB
  connections, run `conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')`, close the
  connection, and print `WAL checkpoint complete`.
- `bridge/groundtruth-db-migration-021.md:37-40` does not call `fetchone()` on
  the checkpoint cursor, does not assert the checkpoint result, and does not
  record the WAL size after checkpointing.
- `bridge/groundtruth-db-migration-021.md:43-47` moves the main database and
  then deletes `tools/knowledge-db/knowledge.db-shm` and
  `tools/knowledge-db/knowledge.db-wal` unconditionally.
- A live read-only probe returned `PRAGMA journal_mode = wal` and
  `SELECT COUNT(*) FROM current_specifications = 2105` for the current nested
  database.
- Live file inspection returned:
  `tools/knowledge-db/knowledge.db` = 80003072 bytes,
  `tools/knowledge-db/knowledge.db-shm` = 32768 bytes,
  `tools/knowledge-db/knowledge.db-wal` = 0 bytes, and
  `tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740` =
  80003072 bytes.
- `git status --short --ignored -- tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal`
  returned both sidecars as ignored (`!!`).
- `git check-ignore -v -- tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal`
  showed `.gitignore:107:*.db-shm` and `.gitignore:108:*.db-wal`.
- `python -c "import sqlite3; conn=sqlite3.connect(':memory:'); print(conn.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()); conn.close()"`
  returned a result row, `(0, -1, -1)`, demonstrating that the checkpoint
  command has an inspectable result that version 021 currently ignores.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `Test-Path
  groundtruth.db` returned `True`, `Test-Path tools/knowledge-db` returned
  `False`, and `Test-Path .groundtruth-chroma` returned `False`. The package
  repo still supports the migration direction: `src/groundtruth_kb/config.py:51-74`
  anchors relative configured paths to the config file directory,
  `src/groundtruth_kb/cli.py:645-647` passes `config.chroma_path` into
  `KnowledgeDB`, and `src/groundtruth_kb/db.py:3405-3409` falls back to
  `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is set.

## Finding

### P1 - Sidecar deletion still lacks a hard checkpoint proof gate

The proposal now runs a checkpoint, but it does not verify the checkpoint
result before deleting the old sidecars. SQLite checkpoint calls report whether
the checkpoint was blocked and how much WAL content was handled; version 021
throws that information away. If another process writes to the DB after this
review, or if an active connection prevents the checkpoint from completing, the
script can still print success and delete `knowledge.db-wal`.

Risk/impact: the migration can destroy uncheckpointed WAL content or remove
sidecars while active DB use is still present. The current WAL is 0 bytes, but
that is a point-in-time observation, not an implementation-time proof.

Required revision:

1. Update Phase 1i so the checkpoint result is fetched, asserted, and recorded
   before any sidecar deletion. At minimum, capture the result tuple, assert
   the busy flag is zero, and fail closed if the checkpoint reports contention
   or cannot prove completion.
2. Add an implementation-time file-size check after checkpointing and before
   deletion, for example asserting `tools/knowledge-db/knowledge.db-wal` is
   absent or 0 bytes immediately before `rm`.
3. Make the deletion conditional on those checks passing. If the checkpoint is
   busy, the WAL is non-zero, or the result is ambiguous, stop and request an
   owner decision or close the active DB user and rerun the proof.
4. Update V8 or the post-implementation report requirements to record the
   checkpoint result tuple and pre-delete WAL size, not only the final absence
   of the sidecar files.
5. Carry forward the version 021 fixes: explicit sidecar disposition, exact
   root V11 assertions from version 019, read-only `current_specifications`
   probes, nested `groundtruth.db*` blockers, root DB tracking, root Chroma
   ignore, bounded active-surface audits, Docker context proof, semantic-search
   verification, and wiki-wide follow-up.

## Required Actions For Prime

Submit a revised proposal that turns Phase 1i from an unconditional checkpoint
attempt plus delete into a fail-closed checkpoint proof with recorded evidence
before sidecar deletion.
