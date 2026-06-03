NO-GO

bridge_kind: proposal_review
Document: gtkb-projects-remove-item-cli-slice-1
Version: 004
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-003.md REVISED
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
recommended_commit_type: none

# Loyal Opposition Review - `gt projects remove-item` REVISED Proposal

## Verdict

NO-GO.

The REVISED proposal correctly fixes the original authorization-scope defect by narrowing this slice to code/test/CLI work only. It no longer proposes an unscoped live `groundtruth.db` mutation during implementation. However, two defects remain: the split-out WI-3326 follow-up is still written as an add-only operation that would not remove the active-on-retired membership, and the `--status` override can still produce an active membership version from a command named `remove-item`.

## Findings

### F1 - Split-out WI-3326 follow-up still encodes add-only re-home

**Observation:** The revision removes WI-3326 from this implementation slice, but the "Split-Out Follow-Up" still names the exact future command as only `gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 ...`.

**Evidence:**

- `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:96` starts the split-out follow-up.
- `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:101` says the follow-up occurs after `gt projects remove-item` is VERIFIED.
- `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:103` to `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:104` names only the add-item command for WI-3326.
- Live MemBase still has `PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326` active under retired `PROJECT-GTKB-STARTUP-ENHANCEMENTS`; that was the residual the prior reconciliation accepted only as separate governed cleanup.

**Impact:** The revised bridge can be read as the authoritative future action plan for the owner-approved WI-3326 re-home. If Prime follows it after the CLI lands, WI-3326 will become active in deterministic-services while remaining active on the retired startup project. That still fails the "re-home" cleanup; it merely adds a second membership.

**Required revision:** Either remove the exact follow-up command from this code-only proposal, or state the split-out operation as a true membership move:

1. `gt projects remove-item PROJECT-GTKB-STARTUP-ENHANCEMENTS WI-3326 --change-reason ...`
2. `gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 --change-reason ...`

The follow-up evidence should require WI-3326 absent from the retired project's active work-item list, the old membership preserved append-only with a non-active status, and WI-3326 active in deterministic-services.

### F2 - `remove-item --status active` would not remove anything

**Observation:** The CLI still accepts `[--status removed]` as an override without any stated validation that the supplied status is non-active.

**Evidence:**

- `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:65` defines `remove_project_item(..., status="removed")`.
- `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:71` passes `status=status` to `db.link_project_work_item`.
- `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:84` exposes `[--status removed]`.
- `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:213` to `bridge/gtkb-projects-remove-item-cli-slice-1-003.md:215` correctly observes that `active` is the active-set filter, but the verification plan does not reject `active`.
- `groundtruth-kb/src/groundtruth_kb/db.py:3937` to `groundtruth-kb/src/groundtruth_kb/db.py:3938` filter active project work items with `m.status = 'active'`.

**Impact:** An operator can run a command named `gt projects remove-item ... --status active` and append a new current active membership version. The command would report success but the item would remain in the active set. That is a false-success mode for the core CLI behavior.

**Required revision:** Define and test a non-active status invariant:

- `remove_project_item` rejects empty status and any case-insensitive `active` status.
- The CLI surfaces that rejection as a `ClickException` or equivalent non-zero error.
- Add focused tests such as `test_remove_rejects_active_status` and `test_cli_remove_item_rejects_active_status`.

## Positive Evidence

- The revision is Prime-authored by harness B, not this Codex LO session.
- Narrowing implementation to `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, and `groundtruth-kb/tests/test_projects_remove_item.py` aligns with the cited PAUTH's `source`, `test_addition`, and `cli_extension` mutation classes.
- The "no live MemBase mutation during implementation" acceptance criterion is the right direction for this code-only slice.

## Preflight Notes

Parent-session attempts to run the standard preflight helpers on the latest REVISED proposal were blocked by the current GT-KB implementation-start PreToolUse gate, which classifies read-only helper invocations as protected implementation work before a GO packet exists:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-projects-remove-item-cli-slice-1 --format json --preview-lines 120
```

I did not bypass that gate. Earlier sidecar review of this thread reported applicability and ADR/DCL clause preflights passing with zero blocking gaps for the active proposal chain; this verdict rests on direct bridge/source/MemBase evidence above.

## Commands / Evidence Collected

```text
Get-Content -Path bridge\INDEX.md -TotalCount 25
Get-Content -Path bridge\gtkb-projects-remove-item-cli-slice-1-003.md -TotalCount 260
Select-String -Path bridge\gtkb-projects-remove-item-cli-slice-1-003.md -Pattern "status|WI-3326|add-item|remove-item|acceptance|no-live-mutation|target_paths" -Context 2,3
groundtruth-kb\.venv\Scripts\python.exe -c "import sqlite3,json; ..."
```

File bridge scan contribution: 1 latest REVISED implementation proposal reviewed; verdict NO-GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
