REVISED

bridge_kind: implementation_report
Document: gtkb-fab-03-membase-backup
Version: 010
Responds-To: bridge/gtkb-fab-03-membase-backup-009.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4415
Project Authorization: PAUTH-FAB03-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, /loop FAB program

# Post-Implementation Report: FAB-03 MemBase Backup (REVISED v010)

## Revision Scope

Addresses both findings in `bridge/gtkb-fab-03-membase-backup-009.md` (NO-GO):

**F1 (scheduled task not registered) — RESOLVED.** The installer
`scripts/install_db_snapshot_task.ps1` was executed in this session. The
`GTKB-DbSnapshot` task is now registered, State `Ready`, daily trigger 03:00,
next run 2026-06-13 03:00. An on-demand end-to-end run was triggered via
`Start-ScheduledTask` and completed with `LastTaskResult: 0`.

**F2 (no live snapshot / freshness warning) — RESOLVED.** The on-demand task
run produced a validated snapshot in the real (unvirtualized)
`%LOCALAPPDATA%\gtkb-snapshots\GT-KB` directory:
`groundtruth-20260612T223315Z.db` (187,383,808 bytes, `method: vacuum`,
`integrity_check_result: ok`, `schema_version: 151`, manifest alongside). The
live `_check_db_snapshot_freshness` doctor check now passes.

## Root Cause of the v008 Evidence Discrepancy (MSIX virtualization)

The v006/v008 freshness "pass" claims were real but observed from inside the
AI-harness sandbox. The Claude desktop harness runs under MSIX file-system
virtualization: Python `%LOCALAPPDATA%` writes from harness-spawned processes
were redirected to the package cache
(`...\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\gtkb-snapshots\GT-KB`).
Snapshots created interactively from the harness were therefore invisible to
the unvirtualized LO verification context, which correctly reported the real
directory absent.

The remediation evidence in this revision is deliberately produced in the
**real** context: the scheduled task executes under the Task Scheduler service
(no MSIX redirection), and its manifest records the unredirected
`final_path: C:\...\AppData\Local\gtkb-snapshots\GT-KB\groundtruth-20260612T223315Z.db`.
Cross-check performed: the task-created snapshot appears in the merged
filesystem view but NOT in the harness package cache, proving physical
placement in the real `%LOCALAPPDATA%`. The steady-state daily 03:00 posture
runs entirely in the real context and is unaffected by harness virtualization.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority; bridge/INDEX.md
  updated with this REVISED entry at the top of the
  gtkb-fab-03-membase-backup document block.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs
  cited and carried forward from the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — 9 spec-derived platform
  tests executed (all PASS) plus live operational read-back evidence.
- `GOV-STANDING-BACKLOG-001` — WI-4415 is the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation artifacts are
  in-root under `E:\GT-KB`. The snapshot output directory is the off-root
  `%LOCALAPPDATA%\gtkb-snapshots`, authorized by the DB-Snapshot Output Exception
  added to `project-root-boundary.md` (owner-decision evidence:
  `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611`).

## Spec-to-Test Mapping

| Specification | Test(s) / Verification | Result |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / DB-Snapshot Output Exception | `test_allowlist_regex_matches_localappdata_pattern`, `test_allowlist_regex_rejects_non_localappdata`, `test_allowlist_check_pass_on_localappdata`, `test_allowlist_check_fail_on_synced_dir` | PASS |
| Rule-text-vs-source parity (project-root-boundary.md ↔ doctor.py) | `test_rule_text_cites_allowlist_constant`, `test_rule_text_cites_doctor_check_name` | PASS |
| Doctor freshness check | `test_freshness_check_warning_when_no_dir` + live read-back (pass, 0h old) | PASS |
| Install script existence + syntax | `test_install_script_exists`, `test_install_script_syntax` | PASS |
| Scheduled snapshot operationalization (GO acceptance criterion 1) | `Get-ScheduledTask` / `schtasks` read-back; `Start-ScheduledTask` end-to-end run `LastTaskResult: 0`; real-context snapshot + manifest | PASS |

## Verification Commands (fresh, this revision)

```
powershell -ExecutionPolicy Bypass -File scripts/install_db_snapshot_task.ps1
# Result: Scheduled task 'GTKB-DbSnapshot' registered: daily at 03:00.

Get-ScheduledTask -TaskName GTKB-DbSnapshot
# Result: TaskName GTKB-DbSnapshot, State Ready; trigger StartBoundary 03:00 daily, Enabled True

schtasks /Query /TN GTKB-DbSnapshot /FO LIST
# Result: Status Ready, Next Run Time: 6/13/2026 3:00:00 AM

Start-ScheduledTask -TaskName GTKB-DbSnapshot; Get-ScheduledTaskInfo -TaskName GTKB-DbSnapshot
# Result: LastRunTime 06/12/2026 15:33:06 (local), LastTaskResult: 0, NextRunTime 06/13/2026 03:00:00

# Task-run snapshot manifest (real context, no MSIX redirect):
#   final_path: %LOCALAPPDATA%\gtkb-snapshots\GT-KB\groundtruth-20260612T223315Z.db
#   integrity_check_result: ok | method: vacuum | schema_version: 151 | snapshot_size: 187383808

python -m pytest platform_tests/scripts/test_db_snapshot_doctor_checks.py -q --tb=short
# Result: 9 passed in 0.77s

python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_db_snapshot_doctor_checks.py
# Result: All checks passed!

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_db_snapshot_doctor_checks.py
# Result: 2 files already formatted

# Live doctor read-back (post task-run):
#   freshness: pass - Newest snapshot groundtruth-20260612T223315Z.db is 0h old
#   allowlist: pass - Snapshot output ...\AppData\Local\gtkb-snapshots\GT-KB matches allowlist
```

## Files Changed

No file changes in this revision relative to v008. The v010 delta is
operational state only: scheduled-task registration plus the first real-context
validated snapshot. Implementation files carried forward from v006/v008 (all
already committed at `c5481033d` and `2b976b694`):

| File | Action | Purpose |
|---|---|---|
| `.claude/rules/project-root-boundary.md` | MODIFIED (v006) | DB-Snapshot Output Exception section |
| `.groundtruth/formal-artifact-approvals/2026-06-12-project-root-boundary-db-snapshot-exception.json` | CREATED (v006) | Narrative-approval packet (SHA256 `d69e11d8...`) |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | MODIFIED (v006) | `_DB_SNAPSHOT_OUTPUT_ALLOWLIST`, freshness + allowlist checks, registered in `run_doctor()` |
| `scripts/install_db_snapshot_task.ps1` | CREATED (v006); EXECUTED (v010) | Idempotent installer; task now registered |
| `groundtruth.toml` | MODIFIED (v006) | `[backup]` retention config |
| `groundtruth-kb/docs/gt-db-snapshot.md` | MODIFIED (v006) | Scheduling, SyncBackSE repoint, config table |
| `platform_tests/scripts/test_db_snapshot_doctor_checks.py` | CREATED (v006) | 9 platform tests |

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

1. **Daily automated snapshot** — `GTKB-DbSnapshot` task REGISTERED (State
   Ready, daily 03:00, next run 2026-06-13); on-demand run `LastTaskResult: 0`
   produced a validated real-context snapshot. ✓
2. **Root-boundary exception** — `.claude/rules/project-root-boundary.md`
   § DB-Snapshot Output Exception documents the 3-condition allowlist. ✓
3. **Doctor enforcement** — `_check_db_snapshot_output_allowlist` FAIL on
   non-allowlisted paths; `_check_db_snapshot_freshness` live PASS post
   task-run. Both registered in `run_doctor()`. ✓
4. **Retention config** — `groundtruth.toml` `[backup]` keys
   `retain_recent=7`, `retain_daily_days=30`. ✓
5. **SyncBackSE repoint guidance** — `groundtruth-kb/docs/gt-db-snapshot.md`
   § Repointing SyncBack / SyncBackSE. ✓
6. **Platform tests** — 9 tests, all PASS (re-run this revision). ✓
7. **Narrative-approval packet** — packet exists with matching SHA256
   (confirmed by LO at `-009` Positive Confirmations). ✓

## Residual Risk

- The task launcher lives at `%TEMP%\gtkb_db_snapshot_task.py` (real Temp,
  verified physically present outside the harness package cache). Temp
  cleaning utilities could remove it; re-running the idempotent installer
  restores it. A durable in-root launcher home (e.g., `.gtkb-state/`) is a
  reasonable hardening follow-up, captured as a backlog candidate rather than
  expanding this thread's scope.
- Harness-created snapshots (from MSIX-virtualized interactive sessions) land
  in the package cache, not the real output directory. This affects only
  ad-hoc in-harness invocations; the scheduled daily run and any owner-shell
  invocation write to the real path.

## Recommended Commit Type

`feat:` — carried forward from v008; the implementation files are net-new
infrastructure (already committed). This revision itself is report + 
operational-state only.

## Requirement Sufficiency

Existing requirements sufficient. The implementation is scoped to
`DELIB-FAB03-REMEDIATION-20260610` (staged backup posture) and
`DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611` (off-root exception). No new
requirements needed.
