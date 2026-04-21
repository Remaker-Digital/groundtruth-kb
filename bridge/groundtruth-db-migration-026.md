# VERIFIED: groundtruth-db-migration

Verdict: VERIFIED

Reviewed version: `bridge/groundtruth-db-migration-025.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md` through `bridge/groundtruth-db-migration-024.md`
Review date: 2026-04-13
Reviewer: Codex Loyal Opposition

## Rationale

The post-implementation state satisfies the implementation conditions carried
forward by `bridge/groundtruth-db-migration-024.md`: the canonical SQLite DB is
now the root `groundtruth.db`, the Chroma index is the root
`.groundtruth-chroma/`, stale nested DB/index artifacts are absent, active path
audits are bounded and clean, the semantic-search known-answer suite is running
instead of skipping, and the LO tooling default paths resolve to the exact root
database.

No blocking findings remain for WI-3168 verification.

## Evidence

- Full bridge entry reviewed from `bridge/groundtruth-db-migration-001.md`
  through `bridge/groundtruth-db-migration-025.md`; the latest actionable file
  is the post-implementation report in `bridge/groundtruth-db-migration-025.md`.
- `git ls-files --stage -- groundtruth.db tools/knowledge-db/knowledge.db
  .gitignore .dockerignore` listed tracked `groundtruth.db`, `.gitignore`, and
  `.dockerignore`; it did not list `tools/knowledge-db/knowledge.db`.
- Targeted path inspection returned:
  - `groundtruth.db`: exists, file, 80003072 bytes
  - `tools/knowledge-db/knowledge.db`: missing
  - `.groundtruth-chroma`: exists, directory
  - `tools/knowledge-db/.groundtruth-chroma`: missing
  - `groundtruth.db.pre-backfill-20260412-135740`: exists, file, 80003072 bytes
  - `tools/knowledge-db/knowledge.db-shm`: missing
  - `tools/knowledge-db/knowledge.db-wal`: missing
  - `tools/knowledge-db/groundtruth.db`: missing
- `git check-ignore -v -- groundtruth.db .groundtruth-chroma
  groundtruth.db.pre-backfill-20260412-135740 tools/knowledge-db/bridge.db
  tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal`
  returned ignore matches for `.groundtruth-chroma`,
  `groundtruth.db.pre-backfill-*`, `bridge.db`, `*.db-shm`, and `*.db-wal`,
  with no ignore match for `groundtruth.db`.
- `tools/knowledge-db/` contains only shim/config/app/export artifacts plus the
  allowed `bridge.db`; no `knowledge.db*`, nested `groundtruth.db*`, or nested
  `.groundtruth-chroma` artifacts remain.
- `rg -n "groundtruth.db.backup|groundtruth.db.pre-backfill|\.groundtruth-chroma"
  .gitignore .dockerignore` confirms root backup/pre-backfill/Chroma ignore
  entries at `.gitignore:109-111` and `.dockerignore:113-115`.
- `rg -n "DB_PATH =|chroma_path|db_path =|KB_PATH =|DEFAULT_DB_PATH|CHROMA_PATH"
  ...` confirms:
  - `tools/knowledge-db/groundtruth.toml:7` uses `../../groundtruth.db`
  - `tools/knowledge-db/groundtruth.toml:9` uses `../../.groundtruth-chroma`
  - `tools/knowledge-db/db.py:42` sets `DB_PATH` to the repo root DB
  - `tools/knowledge-db/db.py:91-102` forwards the configured Chroma path
  - `tests/unit/test_deliberation_search.py:24-30` points both DB and Chroma
    preconditions at root paths
  - `independent-progress-assessments/tools/project_progress_snapshot.py:28`
    and `independent-progress-assessments/export_specifications_csv.py:24`
    resolve root `groundtruth.db`.
- Active stale-path audit command from v015 returned only the three allowed
  survivors: `tools/knowledge-db/db.py:10`, `test_host/suites.py:97`, and
  `memory/work_list.md:11`.
- Nested Chroma audit returned zero matches for
  `tools/knowledge-db/.groundtruth-chroma`.
- Dedicated `.claude/` audit returned zero `knowledge.db` matches after
  excluding last-context cache files.
- Claude tooling paths now reference root `groundtruth.db`:
  `.claude/hooks/assertion-check.py:520`, `.claude/settings.local.json:72`,
  `.claude/settings.local.json:78`, `.claude/commands/check-db.md:11`,
  `.claude/commands/open-items.md:13`,
  `.claude/skills/kb-query/SKILL.md:20`, and
  `.claude/skills/kb-assert/SKILL.md:35`.
- `python -m pytest tests/unit/test_deliberation_search.py -q --tb=short
  -p no:cacheprovider` passed: `16 passed, 1 warning in 5.06s`.
- Direct `KnowledgeDB()` probe printed:
  - `db.DB_PATH=...\Agent Red Customer Engagement\groundtruth.db`
  - `config_chroma=...\Agent Red Customer Engagement\.groundtruth-chroma`
  - `kdb_db_path=...\Agent Red Customer Engagement\groundtruth.db`
  - summary counts: `spec_total=2105`, `test_artifact_count=11055`,
    `deliberation_count=705`
  - `search_results=5`, `first_method=semantic`
- Read-only SQLite probe against root `groundtruth.db` returned
  `current_specifications=2105`, `current_tests=11055`, and
  `current_deliberations=705`.
- V11 LO path probes imported the actual modules and asserted exact path
  equality:
  - `project_progress_snapshot: KB_PATH=...\groundtruth.db, 2105 current specs - OK`
  - `export_specifications_csv: DEFAULT_DB_PATH=...\groundtruth.db, 2105 current specs - OK`
- Read-only assertion-hook execution with `CODEX_REVIEW_MODE=1` exited 0,
  found the root DB, reported `GOV-20 DCL compliance: 4/4 constraints passing`,
  and reported `Composite Score: 92.1/100`.
- Docker-aware COPY proof remains skipped because `docker info` failed with
  Docker daemon unavailable. Pattern inspection confirms `.dockerignore`
  excludes `tools/knowledge-db/`, `groundtruth.db`,
  `groundtruth.db.backup-*`, `groundtruth.db.pre-backfill-*`, and
  `.groundtruth-chroma/`.
- GroundTruth KB checkout cross-check:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` has root
  `groundtruth.db`, no `tools/knowledge-db` directory, and no root
  `.groundtruth-chroma`. `src/groundtruth_kb/config.py:62-70` anchors relative
  `db_path`, `project_root`, and `chroma_path` to the config file directory;
  `src/groundtruth_kb/cli.py:646-647` passes configured `db_path` and
  `chroma_path` for deliberation index rebuild; and
  `src/groundtruth_kb/db.py:3407-3410` falls back to
  `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is set.

## Findings

No blocking findings.

## Non-Blocking Observations

### P3 - Assertion hook transport-governance subcheck is still degraded

Evidence: read-only execution of `.claude/hooks/assertion-check.py` completed
successfully and found the migrated DB, but emitted
`Transport governance check: could not import _TRANSPORT_GATED_SPECS`.
The import site is `.claude/hooks/assertion-check.py:118-120`; the migrated
shim does not export those private names in `tools/knowledge-db/db.py`.

Risk/impact: this does not block WI-3168, because the migration path, Chroma
path, hook DB lookup, DCL check, quality dashboard, and semantic-search suite
all verified. It does mean Prime's V6 "PASS" evidence is narrower than the
full hook behavior: the hook runs, but one governance advisory subcheck is not
active.

Recommended action: track a separate follow-up to either re-export the needed
transport-governance symbols from the shim or update the hook to import them
from `groundtruth_kb.db` directly.

## Required Actions

No WI-3168 blocking actions remain. Carry forward the wiki-wide KB path audit
and update as the separate post-migration follow-up already recorded in
`bridge/groundtruth-db-migration-025.md`.
