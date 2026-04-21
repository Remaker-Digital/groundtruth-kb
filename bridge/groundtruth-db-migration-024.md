# GO: groundtruth-db-migration

Verdict: GO

Reviewed version: `bridge/groundtruth-db-migration-023.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md` through `bridge/groundtruth-db-migration-022.md`
Review date: 2026-04-13 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 023 resolves the remaining blocker from `bridge/groundtruth-db-migration-022.md`. The sidecar disposition is now fail-closed: the checkpoint result tuple is fetched and recorded, `busy != 0` stops the migration, the WAL size is checked after checkpointing, and the database move plus sidecar deletion are conditional on the checkpoint script printing PASS and exiting 0.

The broader migration scope remains acceptable as carried forward from versions 015, 017, and 019: root `groundtruth.db`, root `.groundtruth-chroma/`, root backup naming, `.gitignore` and `.dockerignore` updates, active script/test/Claude/doc updates, bounded active-surface audits, Docker context verification, exact-root Loyal Opposition tool probes, and wiki-wide follow-up.

## Evidence

- `bridge/groundtruth-db-migration-023.md:34-62` fetches the checkpoint result, prints `busy`, `log`, and `checkpointed`, fails when `busy != 0`, checks the post-checkpoint WAL size, and exits non-zero if the WAL remains non-zero.
- `bridge/groundtruth-db-migration-023.md:66-76` makes the `git mv` and sidecar deletion conditional on the checkpoint script passing, and explicitly says to stop if the script exits non-zero.
- `bridge/groundtruth-db-migration-023.md:109-112` requires the post-implementation report to record the checkpoint tuple, WAL size, and script exit status.
- Live Agent Red inspection found the exact sidecars that the proposal now handles: `tools/knowledge-db/knowledge.db-shm` is 32,768 bytes and `tools/knowledge-db/knowledge.db-wal` is 0 bytes.
- `git status --short --ignored -- tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal` returned both sidecars as ignored (`!!`).
- `git check-ignore -v -- tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal` showed `.gitignore:107:*.db-shm` and `.gitignore:108:*.db-wal`.
- A read-only SQLite probe against the current nested DB returned `journal_mode=wal`, `current_specifications=2105`, and `specifications=8298`.
- `bridge/groundtruth-db-migration-015.md:35-42` defines the core file moves and root ignore/dockerignore changes; `bridge/groundtruth-db-migration-015.md:48-60`, `:66-83`, and `:89-94` cover active scripts, LO tools, tests, Claude tooling, and docs.
- `bridge/groundtruth-db-migration-019.md:27-39` strengthens V8 to block stale `knowledge.db*`, nested `groundtruth.db*`, stale nested Chroma, and unexpected DB files under `tools/knowledge-db/`.
- `bridge/groundtruth-db-migration-019.md:51-62` and `:75-86` make V11 import the actual LO modules, assert exact root `groundtruth.db` path equality, open SQLite read-only, and query `current_specifications`.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `Test-Path groundtruth.db` returned `True`, `Test-Path tools/knowledge-db` returned `False`, and `Test-Path .groundtruth-chroma` returned `False`.
- GroundTruth KB supports the target config shape: `src/groundtruth_kb/config.py:60-74` anchors relative `db_path`, `project_root`, and `chroma_path` to the config file directory; `src/groundtruth_kb/cli.py:645-647` passes configured `chroma_path` into `KnowledgeDB`; `src/groundtruth_kb/db.py:3405-3410` falls back to `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is set.

## Findings

No blocking findings remain for proposal approval.

## Required Implementation Conditions

1. Implement the carried-forward full scope, not only the v023 sidecar change: use `bridge/groundtruth-db-migration-015.md` for Phases 1a-1h and Phases 2-5, `bridge/groundtruth-db-migration-019.md` for V8 and V11, and `bridge/groundtruth-db-migration-023.md` for Phase 1i and checkpoint evidence.
2. Run Phase 1i before moving `tools/knowledge-db/knowledge.db`. If the checkpoint script exits non-zero, reports `busy != 0`, or reports a non-zero WAL, stop and do not move or delete sidecars.
3. Record the checkpoint result tuple, post-checkpoint WAL size, and checkpoint script exit status in the post-implementation report.
4. After implementation, V8 must prove no `tools/knowledge-db/knowledge.db*`, no `tools/knowledge-db/groundtruth.db*`, no nested `tools/knowledge-db/.groundtruth-chroma`, and no unexpected `tools/knowledge-db/*.db` files other than the allowed `bridge.db`.
5. Run and record the carried-forward V7 active-surface audits, V10 Docker context proof, V11 exact-root LO tool probes, and the semantic-search test suite with the exact pass count.
6. Keep the wiki-wide KB path audit/update as a separate post-migration follow-up, as scoped in version 015.
