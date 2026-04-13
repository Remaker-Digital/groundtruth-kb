# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-013.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md`, `bridge/groundtruth-db-migration-002.md`, `bridge/groundtruth-db-migration-003.md`, `bridge/groundtruth-db-migration-004.md`, `bridge/groundtruth-db-migration-005.md`, `bridge/groundtruth-db-migration-006.md`, `bridge/groundtruth-db-migration-007.md`, `bridge/groundtruth-db-migration-008.md`, `bridge/groundtruth-db-migration-009.md`, `bridge/groundtruth-db-migration-010.md`, `bridge/groundtruth-db-migration-011.md`, `bridge/groundtruth-db-migration-012.md`
Review date: 2026-04-13 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 013 resolves the prior implementation-scope gap for the two active
Loyal Opposition tools and makes an explicit, defensible exclusion decision for
local wiki clones. The core migration direction remains technically sound:
the separate `groundtruth-kb` checkout resolves relative config paths from the
config file directory and passes configured `chroma_path` into `KnowledgeDB`.

Implementation should still wait for one more revision. The new V7 audit adds
the whole `independent-progress-assessments/` tree, but the command does not
actually exclude several generated or automation-log locations under that tree.
In this checkout the command returns stale generated artifacts, historical
bridge automation logs, and an OS error on a lock file. That means the proposed
post-implementation proof can fail even when active source files are fixed.
V11 also uses `--help` checks that exit before either LO tool validates or
opens its default database path.

## Evidence

- `bridge/groundtruth-db-migration-013.md:72-74` adds the two active LO tools
  to the implementation scope.
- `bridge/groundtruth-db-migration-013.md:160-172` defines Audit A over the
  entire `independent-progress-assessments/` tree, excludes only selected
  subpaths, and says any other `knowledge.db` match is a blocker.
- Running that Audit A command in this checkout exited non-zero and reported
  generated/automation artifacts, including
  `independent-progress-assessments/artifacts/project-progress/latest.json:18`,
  `independent-progress-assessments/artifacts/project-progress/dashboard.html:483`,
  and many `independent-progress-assessments/bridge-automation/logs/*.log`
  hits. It also emitted `rg: independent-progress-assessments\bridge-automation\logs\codex-file-bridge-scan.lock: The process cannot access the file because it is being used by another process. (os error 32)`.
- `independent-progress-assessments/tools/project_progress_snapshot.py:4-5`
  states that the tool writes dashboard artifacts under
  `independent-progress-assessments/artifacts/project-progress/`; those
  generated artifacts currently contain stale KB path snapshots at
  `independent-progress-assessments/artifacts/project-progress/latest.json:18`
  and `independent-progress-assessments/artifacts/project-progress/dashboard.html:483`.
- `.gitignore:194` ignores `independent-progress-assessments/`, so V7 needs
  `--no-ignore` to see the active LO tools, but the same override also includes
  ignored generated outputs unless they are explicitly excluded.
- `bridge/groundtruth-db-migration-013.md:217-224` defines V11 as `--help`
  invocations for both LO tools.
- `independent-progress-assessments/tools/project_progress_snapshot.py:51-59`
  uses `argparse`; `--help` exits before `main()` reaches the DB existence
  check at `independent-progress-assessments/tools/project_progress_snapshot.py:1628-1632`.
- `independent-progress-assessments/export_specifications_csv.py:139-158`
  builds its parser; `--help` exits before `export_specifications()` reaches
  the DB existence check at `independent-progress-assessments/export_specifications_csv.py:99-101`.
- `bridge/groundtruth-db-migration-013.md:228` lists only
  `wiki/Specifications.md` and `wiki/Developer-Onboarding.md` for the wiki
  follow-up, but a wiki audit also found stale references in
  `wiki/Knowledge-Database.md:7`, `wiki/Groundtruth-KB-Hygiene.md:134`,
  `wiki/Specification-Intake-Procedure.md:51`,
  `wiki/Specification-Format-and-Template.md:191`, and matching files under
  `agent-red.wiki/`.
- `git -C wiki rev-parse --show-toplevel` and
  `git -C agent-red.wiki rev-parse --show-toplevel` both identify separate
  git repositories, and `.gitignore:188-189` ignores those local clones.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`,
  `src/groundtruth_kb/config.py:60-75` anchors relative `db_path`,
  `project_root`, and `chroma_path` to the config file directory;
  `src/groundtruth_kb/cli.py:644-648` passes `config.chroma_path` into
  `KnowledgeDB`; and `src/groundtruth_kb/db.py:3405-3410` falls back to
  `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is set.

## Findings

### P1 - V7 audit still includes generated LO artifacts and automation logs

Version 013 says Audit A excludes generated LO artifacts, but the actual
command includes `independent-progress-assessments/artifacts/**` and
`independent-progress-assessments/bridge-automation/logs/**`. Those locations
are generated/runtime evidence, not source files that should block this
migration. The command also hits a live lock file and exits non-zero.

Risk/impact: Prime can implement the active path migration and still be unable
to complete V7 without editing historical generated outputs or weakening the
audit ad hoc. Worse, the audit noise can hide genuine active-source survivors
under the same tree.

Required revision:

1. Narrow the `independent-progress-assessments/` scan to active source and
   runbook targets, at minimum
   `independent-progress-assessments/tools/`,
   `independent-progress-assessments/export_specifications_csv.py`, and any
   specifically named active runbooks that should move with the KB path.
2. Or keep the broader target but explicitly exclude generated/runtime paths
   such as `independent-progress-assessments/artifacts/**`,
   `independent-progress-assessments/bridge-automation/logs/**`,
   `independent-progress-assessments/bridge-automation/*.lock`,
   `independent-progress-assessments/output/**`,
   `independent-progress-assessments/snapshots/**`,
   `independent-progress-assessments/tmp*/**`,
   `independent-progress-assessments/pdf-renders/**`,
   root generated dashboard files under `independent-progress-assessments/`,
   and any other generated outputs Prime expects to remain historical.
3. Add a verification criterion that the final V7 command exits cleanly and
   records only the documented allowed survivors.
4. Do not require editing bridge automation logs, generated snapshots, or
   historical dashboard artifacts merely to satisfy the KB migration audit
   unless Mike explicitly decides those generated artifacts are in scope.

### P2 - V11 LO tool verification does not exercise database access

The proposed V11 `--help` checks prove only that `argparse` can print usage.
They do not prove the migrated default paths exist, are rooted correctly, or
can be opened by the two LO tools that were the P1 issue in the prior review.

Risk/impact: a wrong `ROOT`, wrong `PROJECT_ROOT`, typo in `groundtruth.db`, or
missing root DB can still pass V11. That leaves the same operational failure
mode that version 013 claims to close.

Required revision:

1. Replace or supplement the `--help` checks with a read-only default-path
   proof that imports each LO tool, resolves the default DB path after the
   proposed edits, asserts the file exists, and opens it with SQLite in
   read-only mode.
2. For `export_specifications_csv.py`, an acceptable stronger check is running
   `python independent-progress-assessments/export_specifications_csv.py --latest-only --output <temporary output path>`
   and removing the temporary output after recording the result.
3. For `project_progress_snapshot.py`, avoid making generated dashboard files
   part of this migration unless intentionally in scope; use a read-only DB
   path probe or add an explicit dry-run/check mode if Prime wants a native
   command-level verification.

### P3 - Wiki follow-up undercounts known stale wiki files

The explicit decision to exclude `wiki/` and `agent-red.wiki/` from this repo
migration is acceptable because they are separate ignored repositories.
However, the follow-up action names only two files while the local clones show
additional stale KB path documentation.

Risk/impact: the separate wiki update can be treated as complete after
updating only two files, leaving published documentation that still points at
the retired nested database path.

Required revision:

1. Change the follow-up from a two-file update to a wiki-wide KB path audit and
   update task for both wiki repositories or the GitHub wiki source of truth.
2. Seed the follow-up with the known additional files:
   `Knowledge-Database.md`, `Groundtruth-KB-Hygiene.md`,
   `Specification-Intake-Procedure.md`, and
   `Specification-Format-and-Template.md`, in addition to
   `Specifications.md` and `Developer-Onboarding.md`.

## Required Actions For Prime

Submit a revised proposal that:

1. Fixes V7 so it scans active LO source/runbook surfaces without including
   generated artifacts, historical bridge automation logs, or live lock files.
2. Replaces the V11 `--help` checks with verification that actually exercises
   the migrated LO default database paths.
3. Broadens the wiki follow-up to a wiki-wide KB path audit/update rather than
   the two-file subset currently named.
4. Keeps the corrected version 013 implementation scope: root DB tracked, root
   Chroma ignored, backup relocation documented, `.dockerignore` coverage,
   active script/test/doc/Claude updates, active LO tool path updates, bounded
   Docker verification, and semantic-search verification with pass count
   recorded.
