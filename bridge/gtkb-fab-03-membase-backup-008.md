REVISED

bridge_kind: implementation_report
Document: gtkb-fab-03-membase-backup
Version: 008
Author: prime-builder (Antigravity, harness C) — interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4415
Project Authorization: PAUTH-FAB03-20260610

author_identity: prime-builder
author_harness_id: C
author_session_context_id: antigravity-pb-20260612-fab03-revision
author_model: gemini-pro
author_model_version: 1.5
author_model_configuration: Antigravity desktop, Prime Builder bridge queue processing

---

# Post-Implementation Report: FAB-03 MemBase Backup (REVISED)

## Summary

Implemented all 7 steps of the FAB-03 MemBase backup operationalization per the
GO at `-004`. The implementation adds a daily automated snapshot posture using
the existing `create_snapshot()` API, a root-boundary exception with
deterministic doctor enforcement, and supporting documentation/tests.

This revision (v008) responds to the NO-GO finding in `bridge/gtkb-fab-03-membase-backup-007.md`
by providing the explicit machine-recognizable owner waiver for the off-root snapshot output path.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority; bridge/INDEX.md
  updated with this post-implementation REVISED entry at the top of the
  gtkb-fab-03-membase-backup document block.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs
  cited and carried forward from the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — 9 spec-derived platform
  tests created and executed (all PASS).
- `GOV-STANDING-BACKLOG-001` — WI-4415 is the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation artifacts are
  in-root under `E:\GT-KB`. The snapshot output directory is the off-root
  `%LOCALAPPDATA%\gtkb-snapshots`, authorized by the DB-Snapshot Output Exception
  added to `project-root-boundary.md` (owner-decision evidence:
  `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611`).

## Spec-to-Test Mapping

| Specification | Test(s) | Result |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / DB-Snapshot Output Exception | `test_allowlist_regex_matches_localappdata_pattern`, `test_allowlist_regex_rejects_non_localappdata`, `test_allowlist_check_pass_on_localappdata`, `test_allowlist_check_fail_on_synced_dir` | PASS |
| Rule-text-vs-source parity (project-root-boundary.md ↔ doctor.py) | `test_rule_text_cites_allowlist_constant`, `test_rule_text_cites_doctor_check_name` | PASS |
| Doctor freshness check | `test_freshness_check_warning_when_no_dir` | PASS |
| Install script existence + syntax | `test_install_script_exists`, `test_install_script_syntax` | PASS |

## Verification Commands

```
python -m pytest platform_tests/scripts/test_db_snapshot_doctor_checks.py -v --tb=short
# Result: 9 passed in 0.56s

python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_db_snapshot_doctor_checks.py
# Result: All checks passed!

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_db_snapshot_doctor_checks.py
# Result: 2 files already formatted

# Live doctor check verification:
python -c "from pathlib import Path; from groundtruth_kb.project.doctor import _check_db_snapshot_freshness, _check_db_snapshot_output_allowlist; t = Path('E:/GT-KB'); r1 = _check_db_snapshot_freshness(t); r2 = _check_db_snapshot_output_allowlist(t); print(f'freshness: {r1.status} - {r1.message}'); print(f'allowlist: {r2.status} - {r2.message}')"
# Result: freshness: pass - Newest snapshot groundtruth-20260612T214444Z.db is 0h old
#         allowlist: pass - Snapshot output C:\Users\micha\AppData\Local\gtkb-snapshots\GT-KB matches allowlist
```

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `.claude/rules/project-root-boundary.md` | MODIFIED | Added DB-Snapshot Output Exception section (lines 68-95) |
| `.groundtruth/formal-artifact-approvals/2026-06-12-project-root-boundary-db-snapshot-exception.json` | CREATED | Narrative-approval packet for the rule amendment (SHA256 `d69e11d8...`) |
| groundtruth-kb/src/groundtruth_kb/project/doctor.py | MODIFIED | Added `_DB_SNAPSHOT_OUTPUT_ALLOWLIST` regex, `_check_db_snapshot_freshness()`, `_check_db_snapshot_output_allowlist()`, registered in `run_doctor()` |
| `scripts/install_db_snapshot_task.ps1` | CREATED | Idempotent Windows scheduled task installer (`GTKB-DbSnapshot`, daily 03:00, S4U logon) |
| `groundtruth.toml` | MODIFIED | Added `[backup]` section with `retain_recent=7`, `retain_daily_days=30` |
| `groundtruth-kb/docs/gt-db-snapshot.md` | MODIFIED | Added scheduling, SyncBackSE repoint guidance, configuration table, root boundary exception note |
| `platform_tests/scripts/test_db_snapshot_doctor_checks.py` | CREATED | 9 platform tests covering allowlist regex, rule-text parity, doctor checks, installer |

## Owner Decisions / Input

- `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611` — owner chose
  `%LOCALAPPDATA%\gtkb-snapshots` as the off-root output directory and
  authorized a formal DB-Snapshot Output Exception in
  `project-root-boundary.md`.
- `DELIB-FAB03-REMEDIATION-20260610` — owner approved staged backup posture:
  Slice 1 scheduled `gt db snapshot` + doctor checks + retention config +
  SyncBackSE repoint guidance.
- Auto-approve-inline authorization: owner authorized inline formal/narrative
  approval packets for this 2026-06-12 session.

Owner waiver: ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT - DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611 - owner-authorized DB snapshot output exception for %LOCALAPPDATA%\gtkb-snapshots

## Acceptance Criteria Check

1. **Daily automated snapshot** — `scripts/install_db_snapshot_task.ps1` creates
   the `GTKB-DbSnapshot` scheduled task (daily 03:00); calls `create_snapshot()`
   directly. ✓
2. **Root-boundary exception** — `.claude/rules/project-root-boundary.md`
   § DB-Snapshot Output Exception documents the 3-condition allowlist. ✓
3. **Doctor enforcement** — `_check_db_snapshot_output_allowlist` FAIL on
   non-allowlisted paths; `_check_db_snapshot_freshness` WARN on stale/missing
   snapshots. Both registered in `run_doctor()`. ✓
4. **Retention config** — `groundtruth.toml` `[backup]` keys
   `retain_recent=7`, `retain_daily_days=30`. ✓
5. **SyncBackSE repoint guidance** — `groundtruth-kb/docs/gt-db-snapshot.md`
   § Repointing SyncBack / SyncBackSE. ✓
6. **Platform tests** — 9 tests in
   `platform_tests/scripts/test_db_snapshot_doctor_checks.py`, all PASS. ✓
7. **Narrative-approval packet** — `.groundtruth/formal-artifact-approvals/
   2026-06-12-project-root-boundary-db-snapshot-exception.json` with matching
   SHA256. ✓

## Recommended Commit Type

`feat:` — Net-new capability: doctor checks, scheduled task installer, retention
config, root-boundary exception enforcement, platform tests. Not a fix or
refactor; this is new infrastructure.

## Requirement Sufficiency

Existing requirements sufficient. The implementation is scoped to
`DELIB-FAB03-REMEDIATION-20260610` (staged backup posture) and
`DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611` (off-root exception). No new
requirements needed.
