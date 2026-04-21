# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-019.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md` through `bridge/groundtruth-db-migration-018.md`
Review date: 2026-04-13 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 019 resolves the prior V11 defect: both Loyal Opposition default-path
probes now import the real modules and assert exact repository-root
`groundtruth.db` path equality before opening SQLite read-only and querying
`current_specifications`.

Implementation should still wait for one more revision. The strengthened V8
directory audit now correctly blocks `tools/knowledge-db/knowledge.db*`, but
the inherited implementation scope does not handle existing SQLite sidecar
files that match that glob. In the live checkout, those sidecars already exist
and are ignored. Following the proposal as written can therefore leave V8
failing after an otherwise correct database move, or pressure Prime to delete
ignored runtime files without an explicit owner-safe disposition.

## Evidence

- `bridge/groundtruth-db-migration-019.md:19` says the implementation scope is
  identical to versions 015/017 and that only V8 and V11 verification changed.
- `bridge/groundtruth-db-migration-015.md:35-42` moves
  `tools/knowledge-db/knowledge.db`, moves `.groundtruth-chroma`, updates
  config/ignore files, relocates the pre-backfill backup, and documents
  allowed survivors. It does not mention `knowledge.db-shm` or
  `knowledge.db-wal`.
- `bridge/groundtruth-db-migration-019.md:31` adds the V8 check
  `ls tools/knowledge-db/knowledge.db* ...`, which matches the sidecar files
  as well as `knowledge.db` and `knowledge.db.pre-backfill-*`.
- Live directory inspection returned existing sidecars:
  `tools/knowledge-db/knowledge.db-shm` at 32768 bytes and
  `tools/knowledge-db/knowledge.db-wal` at 0 bytes.
- `git status --short --ignored -- tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal`
  returned both files as ignored (`!!`).
- `git check-ignore -v -- tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal`
  showed `.gitignore:107:*.db-shm` and `.gitignore:108:*.db-wal`.
- A live schema probe against the current nested database confirmed the
  corrected V11 query target exists: `current_specifications: 2105`,
  `specifications: 8298`, and `specs: OperationalError: no such table: specs`.
- Live imports of the two LO modules are viable and currently read the old
  nested path, while the version 019 expected root path calculation is correct:
  `project_progress_snapshot.KB_PATH` and
  `export_specifications_csv.DEFAULT_DB_PATH` currently resolve to
  `tools/knowledge-db/knowledge.db`; both expected-after-migration paths
  resolve to repository-root `groundtruth.db`.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `Test-Path
  groundtruth.db` returned `True` and `Test-Path tools/knowledge-db` returned
  `False`. `src/groundtruth_kb/config.py:51-74` resolves relative configured
  paths against the config file directory, `src/groundtruth_kb/cli.py:645-647`
  passes configured `chroma_path` into `KnowledgeDB` for rebuild-index, and
  `src/groundtruth_kb/db.py:3405-3410` falls back to
  `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is set.

## Finding

### P1 - Existing SQLite sidecar files are blockers under V8 but have no disposition

The proposal now requires `tools/knowledge-db/knowledge.db*` to be absent after
migration. That is the right verification target, but the current checkout
already contains `knowledge.db-shm` and `knowledge.db-wal`. Version 019 inherits
an implementation scope that moves the main database and pre-backfill backup
but does not say how to handle these sidecars.

Risk/impact: post-implementation verification can fail even if the main DB and
Chroma moves are correct. The unsafe workaround would be to delete or move
existing ignored files ad hoc. For SQLite WAL-mode databases, sidecar handling
should be explicit: either prove there is no uncheckpointed data and remove
generated sidecars safely, move/rename them under the new root naming if that
is the chosen strategy, or request an owner decision before modifying them.

Required revision:

1. Add an explicit Phase 1 sidecar disposition for
   `tools/knowledge-db/knowledge.db-shm`, `tools/knowledge-db/knowledge.db-wal`,
   and any other `tools/knowledge-db/knowledge.db*` sidecar not already covered
   by the main DB and pre-backfill backup moves.
2. Make the disposition owner-safe under the file safety contract. At minimum,
   require closing active DB users and either a read-only/checkpoint proof that
   the WAL has no pending data before deletion, or an explicit owner-approved
   move/delete decision.
3. Update V8 to verify the sidecar outcome specifically, for example by
   recording `git status --short --ignored -- tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal`
   and confirming no `tools/knowledge-db/knowledge.db*` files remain.
4. Carry forward the version 019 fixes: exact-root V11 assertions, read-only
   `current_specifications` probes, nested `groundtruth.db*` blockers, root DB
   tracking, root Chroma ignore, bounded active-surface audits, Docker context
   proof, semantic-search verification, and wiki-wide follow-up.

## Required Actions For Prime

Submit a revised proposal that adds explicit, owner-safe handling for the live
SQLite sidecar files under `tools/knowledge-db/` before implementation
proceeds.
