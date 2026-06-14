NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4512-db-snapshot-launcher-in-root
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-8[1m]
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4512
target_paths: ["scripts/install_db_snapshot_task.ps1", "platform_tests/scripts/test_db_snapshot_launcher_in_root.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4512: Move the GTKB-DbSnapshot task launcher out of %TEMP% to a durable in-root home

## Summary

WI-4512 (P3, `git-tooling`, origin=improvement): `scripts/install_db_snapshot_task.ps1` writes the scheduled-task launcher to `$env:TEMP` (`:45` `$tempScript = Join-Path $env:TEMP "gtkb_db_snapshot_task.py"`; `:46` `Set-Content -Path $tempScript ...`; `:50` the scheduled task's `-Argument` points at `$tempScript`). Temp-cleaning utilities can delete that launcher, silently breaking the daily MemBase snapshot until the installer is re-run.

**Cycle-8 triage (this session) confirms WI-4512 is genuinely OPEN** — the installer still targets `$env:TEMP` verbatim. The fix moves the launcher to a durable in-root location, updates the installer (and the scheduled task's argument), and adds a test asserting the launcher path is in-root.

This is also a **project-root-boundary** correction: the launcher is an out-of-root *active dependency* (the scheduled task executes it daily), which the root-boundary rule disallows. Note the existing DB-snapshot exception covers snapshot *output* to `%LOCALAPPDATA%` only — NOT the launcher script — so moving the launcher in-root is fully consistent with that exception.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4512 is the backlog authority for this fix (P3 git-tooling durability defect).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4512; allows `source` + `test_addition`).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** + **`.claude/rules/project-root-boundary.md`** — the core spec for this fix: all active GT-KB artifacts must be in-root under `E:\GT-KB`. The `$env:TEMP` launcher is an out-of-root active dependency; moving it in-root restores compliance. The DB-snapshot **output** exception (`%LOCALAPPDATA%\gtkb-snapshots`) is distinct and unaffected — it does not cover the launcher script.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file bridge (the always-applicable bridge-governance trigger); it is a git-tooling fix that does not modify `bridge/INDEX.md` or any bridge workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps the acceptance criterion to an executed test.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked fix to an installer surface with explicit test coverage.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4512 + the fab-03 Residual Risk it was identified from), cycle-8 triage confirmed it open, the bounded PAUTH authorizes the `source` + `test_addition` work, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / the project-root-boundary rule defines the in-root target. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4512 (and 7 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-BATCH-2`.
- **`bridge/gtkb-fab-03-membase-backup` (VERIFIED; Residual Risk in -010)** — the MemBase-backup work that installed the GTKB-DbSnapshot task and recorded this `$env:TEMP` launcher fragility as residual risk. This proposal closes that residual.
- **`.claude/rules/project-root-boundary.md` — "DB-Snapshot Output Exception"** — confirms the exception is scoped to snapshot *output*; the launcher script is not covered, so it must be in-root. Cited to avoid mis-applying the exception to the launcher.
- _Live semantic deliberation search was not run during authoring (the session's standing `gt deliberations search` hang/freshness caution); prior-decision context gathered from the installer source + the root-boundary rule instead._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4512 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`; forbids formal-artifact mutation). This fix stays within that scope: it edits one PowerShell installer (source) + adds one test. No formal-artifact or KB mutation.

## Design

In `scripts/install_db_snapshot_task.ps1`:

1. Replace the `$env:TEMP` launcher path (`:45`) with a durable in-root location, e.g. `$launcher = Join-Path $ProjectRoot ".gtkb-state\db-snapshot\gtkb_db_snapshot_task.py"` (resolve `$ProjectRoot` from the script location / repo root). `.gtkb-state/` is in-root and persists across Temp cleaning; the launcher is generated runtime content, so a non-tracked in-root runtime dir is the natural home (the implementer MAY choose `scripts/` instead if a tracked launcher is preferred — the acceptance is "in-root + durable, not `$env:TEMP`").
2. Ensure the parent directory exists before `Set-Content` (e.g. `New-Item -ItemType Directory -Force` on the parent).
3. Point the scheduled task's `-Argument` (`:50`) and the `Write-Host "Script: ..."` (`:77`) at the new in-root path.
4. Idempotent re-install: writing to the durable path overwrites the prior launcher (same as today), and the scheduled task is re-registered against the stable in-root path.

No change to the snapshot OUTPUT path (`%LOCALAPPDATA%\gtkb-snapshots`, governed by the existing exception), to the snapshot schedule, or to `groundtruth.db`.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_db_snapshot_launcher_in_root.py`) | Method |
|---|---|---|
| Installer writes the launcher to an in-root durable path, not `%TEMP%` (WI-4512; ADR-ISOLATION-APPLICATION-PLACEMENT-001) | `test_launcher_path_is_in_root_not_temp` | read `scripts/install_db_snapshot_task.ps1`; assert it does NOT use `$env:TEMP` for the launcher and DOES target an in-root path (e.g. under `.gtkb-state/` or `scripts/`) |
| Scheduled-task argument references the in-root launcher | `test_scheduled_task_argument_is_in_root` | assert the `-Argument` / launcher reference points at the in-root path, not `$env:TEMP` |
| Parent directory is ensured before write (no install-time failure) | `test_installer_ensures_launcher_dir` | assert the installer creates the launcher's parent dir (New-Item -Force or equivalent) before `Set-Content` |

Pre-file code-quality gates: the changed file is PowerShell (`.ps1`), so `ruff` does not apply; the `.githooks/pre-commit` PowerShell-parse gate (`pre-commit-ps1-parse.ps1`) validates the edited `.ps1` syntax. Run `python -m pytest platform_tests/scripts/test_db_snapshot_launcher_in_root.py -q --tb=short` for the new test.

## Risk / Rollback

- **Risk: low.** One PowerShell installer edit (launcher path `$env:TEMP` → in-root) + one new static-assertion test. No change to the snapshot output, schedule, DB, or any other harness/tool. The scheduled task is re-registered against a stable in-root path on next install (more durable than today, not less).
- **Operational note:** existing installs still point at the old `%TEMP%` launcher until re-run; the installer is the supported re-registration path (unchanged operationally). Worth a one-line note in the install docs, but not required for this slice.
- **Rollback:** revert the installer edit + delete the test. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs broken/fragile behavior (the daily snapshot silently breaks when Temp is cleaned) and restores project-root-boundary compliance; no new capability surface. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
