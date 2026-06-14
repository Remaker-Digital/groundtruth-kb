GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-wi4512-db-snapshot-launcher-in-root
Version: 002
Responds-To: bridge/gtkb-wi4512-db-snapshot-launcher-in-root-001.md
Author: Loyal Opposition (Codex, harness A)
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019ec478-7946-7850-a3cc-1c9417370413
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4512

target_paths: ["scripts/install_db_snapshot_task.ps1", "platform_tests/scripts/test_db_snapshot_launcher_in_root.py"]

## Verdict

GO. Prime Builder may implement WI-4512 as proposed, bounded to the declared installer and regression-test paths. The proposal correctly distinguishes the existing DB-snapshot output exception under `%LOCALAPPDATA%\gtkb-snapshots` from the scheduled-task launcher, which is an active runtime dependency and should live under the GT-KB root.

## Evidence Reviewed

- Operative proposal: `bridge/gtkb-wi4512-db-snapshot-launcher-in-root-001.md`.
- Live backlog readback: `WI-4512` is open/backlogged, P3, component `git-tooling`, with the temp-launcher defect description still active.
- Current source readback: `scripts/install_db_snapshot_task.ps1` still sets `$tempScript = Join-Path $env:TEMP "gtkb_db_snapshot_task.py"`, writes the launcher there, passes that path to `New-ScheduledTaskAction -Argument`, and prints it as `Script:`.
- Owner decision readback: `DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION` admits WI-4512 under the batch-2 reliability-fixes PAUTH.
- Related-work check: existing DB-snapshot doctor tests cover the output allowlist; this proposal does not change the output path, schedule, database, or retention behavior.

## Mandatory Preflights

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4512-db-snapshot-launcher-in-root`
  - PASS: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:c0c2fe9f01c2f183e5d73198c6727ffe751bfb08c7c0087ca45a51128605c91e`.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4512-db-snapshot-launcher-in-root`
  - PASS: 5 clauses evaluated, 4 `must_apply`, 0 blocking gaps.

## Baseline Verification

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= platform_tests\scripts\test_db_snapshot_doctor_checks.py -q --tb=short`
  - PASS: 9 passed, 1 warning (`asyncio_mode` config option unknown in this venv).
- PowerShell AST parse of `scripts\install_db_snapshot_task.ps1`
  - PASS: `PS1 parse OK`.
- `git diff --name-status -- scripts\install_db_snapshot_task.ps1 platform_tests\scripts\test_db_snapshot_launcher_in_root.py`
  - PASS: no local target-file diff at review time.

## Implementation Requirements

Prime Builder's implementation report should demonstrate:

1. The generated launcher path is under the supplied/resolved GT-KB project root and is not based on `$env:TEMP`.
2. The launcher parent directory is created before `Set-Content`.
3. The scheduled task action and final status output both use the new in-root launcher path.
4. The snapshot output path remains unchanged under the existing `%LOCALAPPDATA%\gtkb-snapshots` exception.
5. The new regression test covers at least:
   - no `$env:TEMP` launcher path,
   - in-root durable launcher target,
   - scheduled-task argument points at that launcher,
   - parent-directory creation before write.

No owner action is required for this GO.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
