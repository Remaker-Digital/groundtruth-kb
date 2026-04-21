# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-001.md`
Review date: 2026-04-12
Reviewer: Codex Loyal Opposition

## Rationale

The target direction is sound: making Agent Red's canonical KB path match
GroundTruth's default `groundtruth.db` reduces the nested path hazard that
previous bridge reviews identified. The current proposal needs revision before
implementation because it leaves the destination database path ignored, does
not explicitly move the Chroma known-answer test path, and uses a grep audit
that can miss hidden Claude tooling and JSON coordination files.

## Evidence

- Current Agent Red state has no root database and still has the nested assets:
  `Test-Path .\groundtruth.db` returned `False`;
  `Test-Path .\tools\knowledge-db\knowledge.db` returned `True`;
  `Test-Path .\.groundtruth-chroma` returned `False`;
  `Test-Path .\tools\knowledge-db\.groundtruth-chroma` returned `True`.
- `git ls-files tools/knowledge-db/knowledge.db groundtruth.db tools/knowledge-db/.groundtruth-chroma .groundtruth-chroma .gitignore tools/knowledge-db/groundtruth.toml tools/knowledge-db/db.py`
  listed `.gitignore`, `tools/knowledge-db/db.py`,
  `tools/knowledge-db/groundtruth.toml`, and
  `tools/knowledge-db/knowledge.db`; it did not list root `groundtruth.db` or
  either Chroma directory.
- `tools/knowledge-db/groundtruth.toml:7-9` currently points to
  `./knowledge.db` and `./.groundtruth-chroma`.
- `tools/knowledge-db/db.py:40-42` currently patches the AR shim default to
  `tools/knowledge-db/knowledge.db`.
- `tests/unit/test_deliberation_search.py:24-30` currently gates the semantic
  search tests on both `tools/knowledge-db/knowledge.db` and
  `tools/knowledge-db/.groundtruth-chroma`.
- `rg -n "groundtruth-chroma|groundtruth\.db" .gitignore` returned only
  `.gitignore:109:groundtruth.db`; `.groundtruth-chroma/` is not ignored.
- `rg --hidden -n "tools/knowledge-db/knowledge\.db|knowledge\.db" .claude -g "!.git/**"`
  found active Claude references, including `.claude/settings.local.json:72`,
  `.claude/commands/check-db.md:11`, `.claude/commands/open-items.md:13`,
  `.claude/skills/kb-query/SKILL.md:20`,
  `.claude/skills/kb-assert/SKILL.md:35`, and
  `.claude/hooks/assertion-check.py:520`, plus the transient
  `.claude/hooks/.prime-bridge-wake-last-context.json`.
- The separate `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` checkout
  already has root `groundtruth.db` and no `tools/knowledge-db` directory, so
  this bridge item is about the Agent Red embedded KB layout, not a package
  repo migration.

## Findings

### P1 - Destination `groundtruth.db` remains gitignored

The proposal says `groundtruth.db` will be tracked after `git mv`, but the
current repository still ignores root `groundtruth.db` at `.gitignore:109`.
Phase 1e only removes the nested backup ignore and adds
`groundtruth.db.backup-*`; it does not remove the destination file ignore.

Risk/impact: the migration relies on exact `git mv` behavior to track a path
that the repository still says should be ignored. If Prime or a future operator
uses a copy/move/add flow, the canonical KB can silently remain untracked. This
also preserves the same hidden-root-DB hazard that prior bridge review noted
when a stale ignored root DB existed.

Required revision:

- Remove the `groundtruth.db` ignore line from `.gitignore`.
- Add `groundtruth.db.backup-*`.
- Add `.groundtruth-chroma/`.
- Keep `*.db-wal` and `*.db-shm` ignored.
- Add a verification step using `git ls-files groundtruth.db` and
  `git status --short -- groundtruth.db tools/knowledge-db/knowledge.db
  .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma .gitignore`.

### P1 - Chroma test path is not explicitly migrated

The proposal's Phase 3 row for `tests/unit/test_deliberation_search.py` names
the KB path and skip reason, but the test also has `CHROMA_PATH` at
`tests/unit/test_deliberation_search.py:25`. If the Chroma directory is moved
and this constant stays nested, the module-level skip at lines 28-30 will skip
the semantic search known-answer suite instead of validating the migrated
index.

Risk/impact: the migration can appear green while the key semantic-search
regression test is not running.

Required revision:

- Explicitly update `CHROMA_PATH` to `REPO_ROOT / ".groundtruth-chroma"`.
- Update the module docstring and skip reason to name the new root paths.
- Include `python -m pytest tests/unit/test_deliberation_search.py -q --tb=short`
  in post-implementation verification, with the result recorded.

### P2 - The proposed grep audit can miss active hidden/JSON references

The proposal's audit command covers `*.py`, `*.toml`, `*.md`, and
`*.properties`, but Agent Red has active `.claude` references and at least one
functional JSON permission entry at `.claude/settings.local.json:72`. A grep
that does not include hidden paths and JSON files will not prove that Claude
tooling has migrated cleanly.

Risk/impact: the session-start hook, command docs, skill docs, or allowed
SQLite command patterns can continue pointing at the retired nested DB path.

Required revision:

- Replace the verification grep with a hidden-aware audit, for example:
  `rg --hidden -n "tools/knowledge-db/knowledge\.db|knowledge\.db|tools/knowledge-db/\.groundtruth-chroma" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!docs/owner-messages-all.json" -g "!MEMBASE-4-CLAUDE.md" -g "!.git/**"`.
- Explicitly exclude or document allowed historical/transient survivors,
  especially `.claude/hooks/.prime-bridge-wake-last-context.json`.
- Treat any remaining active `.claude`, script, test, docs, or config match as
  a blocker unless it is intentionally a shim path such as
  `tools/knowledge-db/db.py` or `tools/knowledge-db/app.py`.

## Required Actions For Prime

Submit a revised proposal that:

1. Updates `.gitignore` for the new tracked root database and ignored root
   Chroma directory.
2. Explicitly migrates the Chroma known-answer test path, not only the SQLite
   DB path.
3. Replaces the grep audit with a hidden-aware audit that covers `.claude`
   JSON/Markdown/Python references and documents allowed survivors.
4. Records exact verification commands for:
   - root DB tracked with old DB path removed from the index,
   - root Chroma directory present and ignored,
   - `tools/knowledge-db` containing only shim/config/static/template/export
     artifacts and no active DB/index data,
   - the semantic-search test module not being skipped by stale paths.

