# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-003.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md`, `bridge/groundtruth-db-migration-002.md`
Review date: 2026-04-12 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

The revision resolves the three findings from `bridge/groundtruth-db-migration-002.md` on the proposal surface: it removes the root `groundtruth.db` ignore, explicitly migrates `CHROMA_PATH`, and changes the path audit to use `rg --hidden`.

It still needs one more revision before implementation because the live repository has an existing untracked nested DB backup that the proposal does not account for, and the revised audit can still return a false zero while active `knowledge.db` references survive.

## Evidence

- `bridge/groundtruth-db-migration-003.md` Phase 1e removes only `groundtruth.db` and `tools/knowledge-db/knowledge.db.backup-*`, then adds `groundtruth.db.backup-*` and `.groundtruth-chroma/`.
- `Get-ChildItem -Force tools/knowledge-db` shows `knowledge.db` and `knowledge.db.pre-backfill-20260412-135740`, both 80,003,072 bytes, plus `.groundtruth-chroma`.
- `git status --short -- tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740 tools/knowledge-db/knowledge.db tools/knowledge-db/.groundtruth-chroma groundtruth.db .groundtruth-chroma .gitignore` returned:
  - `M tools/knowledge-db/knowledge.db`
  - `?? tools/knowledge-db/.groundtruth-chroma/`
  - `?? tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740`
- `git check-ignore -v -- tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740 tools/knowledge-db/knowledge.db tools/knowledge-db/.groundtruth-chroma groundtruth.db .groundtruth-chroma` returned only `.gitignore:109:groundtruth.db groundtruth.db`; the pre-backfill DB backup is not ignored.
- `tools/knowledge-db/groundtruth.toml:4-9` confirms current config paths are anchored to `tools/knowledge-db/`, so the proposed `../../groundtruth.db` and `../../.groundtruth-chroma` direction is consistent with the local comment.
- In the GroundTruth checkout, `src/groundtruth_kb/config.py:60-75` resolves relative path settings against the directory containing `groundtruth.toml`; `tests/test_config.py:82-93` asserts this behavior.
- In the GroundTruth checkout, `src/groundtruth_kb/cli.py:644-648` passes `config.chroma_path` into `KnowledgeDB` for `gt deliberations rebuild-index`; `src/groundtruth_kb/db.py:3405-3408` falls back to `db_path.parent / ".groundtruth-chroma"` when no explicit Chroma path is configured.
- `rg --hidden -n "tools/knowledge-db/knowledge\.db|tools/knowledge-db/\.groundtruth-chroma" ...` catches exact literal nested paths, but it does not catch path-constructed or standalone `knowledge.db` references such as:
  - `tools/knowledge-db/seed.py:587`: `Path(__file__).parent / "knowledge.db"`
  - `.claude/hooks/assertion-check.py:520`: `KB_DIR / "knowledge.db"`
  - `scripts/deliberation_health.py:31`: `REPO_ROOT / "tools" / "knowledge-db" / "knowledge.db"`
  - `scripts/harvest_session_deliberations.py:509`: `help="Path to knowledge.db"`
  - `.claude/settings.local.json:78`: `Bash(sqlite3 knowledge.db ...`
- `scripts/harvest_session_deliberations.py:24` and `scripts/harvest_session_deliberations.py:509` are not both named in the revised Phase 2 table, which only lists line 48 for that file.

## Findings

### P1 - Existing nested DB backup is outside the migration plan

The proposal's objective says `tools/knowledge-db/` becomes a pure shim/config directory and V8 says `tools/knowledge-db/` must not contain `knowledge.db` or `.groundtruth-chroma/`. The live directory also contains `tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740`, an 80 MB SQLite-shaped data backup. It is untracked and not ignored.

Risk/impact: following the proposal as written can leave a second stale KB data file under the retired nested location. That preserves the exact source-of-truth ambiguity the migration is meant to remove, and it gives future scripts or operators a plausible old DB to read accidentally. Because this is an existing file, deletion or relocation also needs an explicit owner decision under the file-safety contract.

Required revision:

1. Add an explicit disposition for `tools/knowledge-db/knowledge.db.pre-backfill-*` files: owner-approved delete, move to an approved archive location, rename/move beside `groundtruth.db` with a root backup pattern, or keep as a documented allowed survivor.
2. Update `.gitignore` if the chosen disposition creates or preserves backup files.
3. Update verification to prove no undeclared `tools/knowledge-db/knowledge.db*` data artifacts remain, for example `Get-ChildItem -Force tools/knowledge-db | Where-Object Name -like 'knowledge.db*'` plus `git status --short -- tools/knowledge-db`.

### P2 - The hidden-aware audit is still too narrow

The revised audit fixes the earlier hidden-directory problem, but it only searches exact literal `tools/knowledge-db/knowledge.db` and `tools/knowledge-db/.groundtruth-chroma` strings. Active code has several path-composed `knowledge.db` references that would not be caught if implementation misses them. It also misses standalone user-facing strings such as `scripts/harvest_session_deliberations.py:509`.

Risk/impact: Prime can record a zero-match audit while stale active references remain. The most important cases are hook/script paths because they can silently open the retired DB name after migration, or skip/avoid the migrated DB.

Required revision:

1. Broaden V7 to catch standalone and path-composed DB references, for example a hidden-aware audit over `knowledge\.db|tools[/\\]knowledge-db[/\\]\.groundtruth-chroma|\.groundtruth-chroma`, with explicit exclusions and allowed survivors.
2. Add `scripts/harvest_session_deliberations.py:24` and `scripts/harvest_session_deliberations.py:509` to the update list, not only line 48.
3. Explicitly decide whether `.claude/settings.local.json:78` remains an allowed permission pattern or should move to `groundtruth.db`.
4. Treat any remaining active script, hook, skill, command, test, or user-facing doc match as a blocker unless it is specifically documented as historical or intentional.

## Required Actions For Prime

Submit a revised proposal that:

1. Handles existing `tools/knowledge-db/knowledge.db.pre-backfill-*` artifacts with an owner-safe disposition.
2. Strengthens the hidden-aware audit so it cannot miss path-composed `knowledge.db` references.
3. Completes the `harvest_session_deliberations.py` update scope and documents the `.claude/settings.local.json:78` decision.
4. Keeps the prior fixes from version 003: root `groundtruth.db` unignored/tracked, root `.groundtruth-chroma/` ignored, `CHROMA_PATH` migrated, and `test_deliberation_search.py` run with the pass count recorded.
