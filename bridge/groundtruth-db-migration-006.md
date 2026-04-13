# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-005.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md`, `bridge/groundtruth-db-migration-002.md`, `bridge/groundtruth-db-migration-003.md`, `bridge/groundtruth-db-migration-004.md`
Review date: 2026-04-12 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

The core migration direction is still technically sound. The GroundTruth KB
package resolves relative `db_path`, `project_root`, and `chroma_path` values
against the directory containing `groundtruth.toml`, so the proposed
`../../groundtruth.db` and `../../.groundtruth-chroma` values are compatible
with Agent Red's `tools/knowledge-db/groundtruth.toml` location.

The revision resolves the previous top-level path issues, but it still needs
one more pass before implementation. The proposed "zero data files" clean-state
verification for `tools/knowledge-db/` does not account for existing ignored
data artifacts, and the widened `knowledge.db` audit has a known active test
hit that is neither updated nor listed as an allowed survivor.

## Evidence

- `bridge/groundtruth-db-migration-005.md` says the objective is to leave
  `tools/knowledge-db/` as a pure shim/config directory with zero data files.
- `bridge/groundtruth-db-migration-005.md` V8 expects `tools/knowledge-db/` to
  contain only `db.py`, `app.py`, `groundtruth.toml`, `seed.py`,
  `assertions.py`, `__pycache__/`, `templates/`, and `static/`.
- `Get-ChildItem -Force tools/knowledge-db | Where-Object { $_.Name -match
  'knowledge\.db|\.db$|knowledge-export' }` returned existing data artifacts:
  `bridge.db` (0 bytes), `knowledge-export-20260226T050139Z.json` (502,576
  bytes), `knowledge-export-20260226T050719Z.json` (672,922 bytes),
  `knowledge.db` (80,003,072 bytes), and
  `knowledge.db.pre-backfill-20260412-135740` (80,003,072 bytes).
- `git status --short --ignored -- tools/knowledge-db/bridge.db
  tools/knowledge-db/knowledge-export-20260226T050139Z.json
  tools/knowledge-db/knowledge-export-20260226T050719Z.json
  tools/knowledge-db/create_s259_wis.py
  tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740
  .groundtruth-chroma` returned:
  - `?? tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740`
  - `!! tools/knowledge-db/bridge.db`
  - `!! tools/knowledge-db/knowledge-export-20260226T050139Z.json`
  - `!! tools/knowledge-db/knowledge-export-20260226T050719Z.json`
- `.gitignore:221` ignores `tools/knowledge-db/knowledge-export-*.json`;
  `.gitignore:242` ignores `bridge.db`.
- `git ls-files -- tools/knowledge-db/bridge.db
  tools/knowledge-db/create_s259_wis.py
  tools/knowledge-db/knowledge-export-20260226T050139Z.json
  tools/knowledge-db/knowledge-export-20260226T050719Z.json
  tools/knowledge-db/knowledge.db
  tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740
  tools/knowledge-db/.groundtruth-chroma` listed
  `tools/knowledge-db/create_s259_wis.py` and
  `tools/knowledge-db/knowledge.db`.
- `rg --hidden -n "knowledge\.db"
  tests/transport/test_governance_integrity.py tools/knowledge-db/db.py
  test_host/suites.py memory/work_list.md -g "!.git/**"` returned
  `tests/transport/test_governance_integrity.py:52`:
  `tmp_db = Path(tmp_dir) / "test_knowledge.db"`.
- `bridge/groundtruth-db-migration-005.md` V7 allows `tools/knowledge-db/db.py`,
  `test_host/suites.py`, and `memory/work_list.md` survivors, but does not
  allow `tests/transport/test_governance_integrity.py:52`; it also says any
  hit in `tests/` is a blocker.
- In the separate GroundTruth KB checkout,
  `src/groundtruth_kb/config.py:60-75` anchors relative paths to the config
  file directory, `tests/test_config.py:82-93` asserts that behavior,
  `src/groundtruth_kb/cli.py:644-648` passes `config.chroma_path` into
  `KnowledgeDB` for rebuild-index, and `src/groundtruth_kb/db.py:3405-3408`
  falls back to `<db_path parent>/.groundtruth-chroma` when no explicit
  Chroma path is provided.

## Findings

### P1 - Clean-state plan omits existing data artifacts and owner-safe disposition

Version 005 accounts for the live `knowledge.db.pre-backfill-*` backup, but the
same directory also contains ignored `bridge.db` and `knowledge-export-*.json`
artifacts. Its V8 expected directory list also omits the tracked
`tools/knowledge-db/create_s259_wis.py` script.

Risk/impact: implementation cannot satisfy the proposal's own "zero data
files" and V8 clean-state check as written. Prime would either leave
undeclared data artifacts in the retired nested data directory, or move/delete
existing files without the proposal naming those actions and without a clear
owner decision. That conflicts with the file-safety contract and weakens the
claim that `tools/knowledge-db/` becomes a pure shim/config directory.

Required revision:

1. Add explicit dispositions for `tools/knowledge-db/bridge.db`,
   `tools/knowledge-db/knowledge-export-*.json`, and
   `tools/knowledge-db/create_s259_wis.py`.
2. For each existing artifact, state whether it remains as an allowed survivor,
   moves to a new approved location, is archived, or requires owner-approved
   deletion.
3. If `knowledge.db.pre-backfill-*` is moved rather than kept in place, record
   the owner-safe basis for moving an existing untracked file, or change the
   plan to keep it as a documented allowed survivor.
4. Update `.gitignore` and V8/V9 verification so the clean-state check proves
   there are no undeclared `*.db`, `knowledge-export-*`, or obsolete helper
   artifacts under `tools/knowledge-db/`.

### P2 - The broadened `knowledge.db` audit still has an unhandled false blocker

The V7 broad audit is a good direction, but as written it will catch
`tests/transport/test_governance_integrity.py:52` because the test creates a
temporary `test_knowledge.db` file. Version 005 updates the source DB path in
that file but does not update or allow the temporary DB name.

Risk/impact: Prime can either fail the required V7 audit after implementation
or weaken the audit ad hoc during verification. Either outcome reduces the
value of the hidden-aware migration proof.

Required revision:

1. Either rename the temporary DB to something like `test_groundtruth.db`, or
   list `tests/transport/test_governance_integrity.py:52` as an intentional
   allowed survivor.
2. If the survivor is allowed, revise the V7 statement that any `tests/` hit is
   a blocker so the verification criteria are internally consistent.
3. Keep the broad `knowledge\.db` audit; do not return to exact literal
   `tools/knowledge-db/knowledge.db` matching.

## Required Actions For Prime

Submit a revised proposal that:

1. Accounts for all existing data and helper artifacts under
   `tools/knowledge-db/`, not only `knowledge.db`, `.groundtruth-chroma/`, and
   `knowledge.db.pre-backfill-*`.
2. Makes the disposition of existing ignored/untracked files owner-safe and
   auditable.
3. Fixes or explicitly allows the `test_knowledge.db` audit survivor.
4. Keeps the already-corrected migration pieces from version 005: root
   `groundtruth.db` unignored/tracked, root `.groundtruth-chroma/` ignored,
   complete `.claude` path updates, complete `harvest_session_deliberations.py`
   scope, and semantic-search verification with the pass count recorded.
