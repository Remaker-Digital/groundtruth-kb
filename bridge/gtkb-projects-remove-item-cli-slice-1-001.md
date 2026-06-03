NEW

bridge_kind: implementation_proposal
Document: gtkb-projects-remove-item-cli-slice-1
Version: 001
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: feat
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS
Work Item: WI-4266
Owner Decision: DELIB-20260624
author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 3975dda7-2644-4926-8822-013f4d7aa4f2
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

# `gt projects remove-item` operator command + re-home WI-3326 (WI-4266)

## Summary

Implement WI-4266: add a `gt projects remove-item` operator command (and its
backing `ProjectLifecycleService.remove_project_item` method) to cleanly detach
a work-item membership from a project, and re-home WI-3326 to
PROJECT-GTKB-DETERMINISTIC-SERVICES-001 per the owner's re-home decision
(`DELIB-20260624`).

Motivation (from WI-4266): when a project is retired via `gt projects retire`,
first-class work-item memberships created by earlier orphan-grouping batches
remain attached as active-on-retired memberships, and there is no public
operator command to cleanly detach or re-home them. The concrete residual is
WI-3326 (phantom-spec-citation cleanup), which became unhomed
(`project_name=None`) when PROJECT-GTKB-STARTUP-ENHANCEMENTS retired. The second
of the operational-load CLIs per the owner AUQ "operational-load CLIs first"
(`DELIB-20260623`).

## Scope

### (a) `ProjectLifecycleService.remove_project_item`

New method in `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`:

- Signature mirrors `add_project_item`:
  `remove_project_item(project_id, work_item_id, *, changed_by, change_reason, status="removed")`.
- Looks up the current active membership (stable id
  `_stable_project_link_id("PWM", project_id, work_item_id)`); raises
  `ProjectLifecycleError` if there is no active membership to remove (fail
  closed — no silent no-op).
- Appends a new membership version via
  `db.link_project_work_item(..., status=status, membership_role=<carried>,
  membership_order=<carried>, source=<carried>)`, carrying forward the current
  role/order/source (same pattern as `reorder_project_items`). The new
  `status="removed"` version drops the membership from the active set
  (`list_project_work_items` filters `status = 'active'`). Append-only; the
  prior active version is preserved for audit.

### (b) `gt projects remove-item` CLI

New command in `groundtruth-kb/src/groundtruth_kb/cli.py` (mirrors
`gt projects add-item`):

```text
gt projects remove-item PROJECT_ID WORK_ITEM_ID --change-reason <text> [--status removed] [--changed-by ...] [--json]
```

Delegates to `service.remove_project_item(...)`; maps `ProjectLifecycleError`
to `click.ClickException`.

### (c) Re-home WI-3326 (the concrete owner-decided instance)

WI-3326 is already detached (`project_name=None`), so the re-home is an
**add** to the active project (not a remove): the implementation runs
`gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326
--change-reason "Re-home active-on-retired residual per DELIB-20260624"`. This
uses the existing `add-item` command; the new `remove-item` is the general
capability for FUTURE active-on-retired residuals.

## Owner Decisions / Input

- **Owner AUQ "Re-home WI-3326 + continue"** (2026-06-03), recorded as
  `DELIB-20260624`: re-home WI-3326 to PROJECT-GTKB-DETERMINISTIC-SERVICES-001
  (NOT close), build the `gt projects remove-item` CLI, continue the 5-WI
  sequence.
- **Owner AUQ "Operational-load CLIs first"** (`DELIB-20260623`): WI-4266 is the
  second operational-load CLI.
- Implementation authorized by
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS` (active;
  includes WI-4266; allowed mutations `source`, `test_addition`,
  `cli_extension`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is filed and tracked through
  the file bridge; `bridge/INDEX.md` is canonical for its lifecycle (NEW → GO →
  post-impl → VERIFIED).
- `GOV-STANDING-BACKLOG-001` — WI-4266 is a governed backlog item; the WI-3326
  re-home keeps a known open item correctly homed under the active project.
- `GOV-08` — MemBase truth; membership state (active vs removed) must reflect
  reality; append-only versioning preserves the audit chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under the active
  operational-load-CLIs PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item / Owner Decision metadata present.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — membership active → removed is a
  lifecycle-valid transition; the WI-3326 None → homed re-parent is valid.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all files under `E:\GT-KB`
  (`groundtruth-kb/` package + tests).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — project memberships and
  work items are durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the removal/re-home
  carries an explicit `change_reason` into the version history.

## Prior Deliberations

- `DELIB-20260624` — owner re-home decision (this session); the WI-3326 disposition source.
- `DELIB-20260623` — owner "tackle the 5 / CLIs first" decision; WI-4266 sequence.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — operator CLIs replace ad-hoc
  AI-mediated membership surgery with a deterministic, governed command.
- The `gt bridge revise` CLI thread (`gtkb-bridge-revise-cli-slice-1`, VERIFIED)
  — the sibling operational-load CLI; same surface/test structure precedent.
- WI-4266's origin context: `gtkb-startup-enhancements-completion-reconciliation`
  (post-impl -006 + VERIFIED -007) dispositioned the WI-3326 residual as
  out-of-scope/non-blocking and recommended a separate governed correction —
  this proposal is that correction.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (modify — add
  `remove_project_item` service method)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (modify — add `gt projects
  remove-item` command)
- `groundtruth-kb/tests/test_projects_remove_item.py` (new — unit tests)

## Requirement Sufficiency

**Existing requirements sufficient.** WI-4266's description is the operative
requirement; `GOV-STANDING-BACKLOG-001`, `GOV-08`, and the project-lifecycle
model govern. No new specification capture required.

## Design (reuse-first)

`remove_project_item` reuses `db.link_project_work_item(..., status="removed")`
(the same append-only membership-versioning primitive `add_project_item` and
`reorder_project_items` use). It carries forward the current membership's
role/order/source (the `reorder` carry-forward pattern). The active-set filter
`list_project_work_items` already excludes non-`active` status, so a `removed`
version detaches without deleting history. The CLI command mirrors
`gt projects add-item` exactly (argument shape, `_project_service(ctx)`,
`ProjectLifecycleError → ClickException`, `--json`).

## Spec-Derived Verification Plan

| Specification | Test | Expected |
|---|---|---|
| `GOV-08` removal detaches | `test_remove_project_item_detaches_active_membership` | after remove, the WI is absent from `list_project_work_items` (active) but a `status=removed` version exists |
| append-only preserved | `test_remove_appends_version_preserves_history` | a new membership version is appended; the prior active version remains in history |
| fail-closed on no active membership | `test_remove_nonexistent_membership_raises` | removing a WI with no active membership raises `ProjectLifecycleError` |
| role/order carry-forward | `test_remove_carries_forward_role_and_order` | the removed version preserves the prior role/order/source |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_remove_then_readd_cycle` | active → removed → active (re-add) round-trips |
| CLI wiring | `test_cli_remove_item_invokes_service` (CliRunner) | `gt projects remove-item` calls the service and reports the removal |
| WI-3326 re-home (post-impl evidence) | `projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` | WI-3326 appears as an active member after re-home |

Test command:
`PYTHONPATH=groundtruth-kb/src python -m pytest groundtruth-kb/tests/test_projects_remove_item.py -q`
plus `ruff check` and `ruff format --check` on the changed files.

## Acceptance Criteria

1. `ProjectLifecycleService.remove_project_item` detaches an active membership
   (append-only `status=removed`), carries forward role/order/source, and fails
   closed when no active membership exists.
2. `gt projects remove-item PROJECT WI --change-reason ...` is registered, calls
   the service, and maps errors to `ClickException`.
3. WI-3326 is re-homed to PROJECT-GTKB-DETERMINISTIC-SERVICES-001 (active member)
   per `DELIB-20260624`.
4. New test module passes; `ruff check` + `ruff format --check` clean on the
   changed files.
5. Pre/post bridge preflights pass (no missing required specs; 0 blocking gaps).

## Risks / Rollback

- **Risk: removing the wrong / a non-active membership.** Mitigation: fail
  closed when no active membership exists; carry-forward + append-only means a
  mistaken removal is reversible via `add-item` (re-add) — a test covers the
  round-trip.
- **Risk: status vocabulary drift** (`removed` vs `inactive`). Mitigation: the
  membership `status` column is free-text with `active` as the active-set
  filter; `removed` is non-`active` and therefore detaches. `--status` defaults
  to `removed` but is overridable if a different non-active token is desired.
- **Risk: WI-3326 re-home is the wrong project.** Mitigation: the owner
  explicitly chose PROJECT-GTKB-DETERMINISTIC-SERVICES-001 (`DELIB-20260624`);
  re-home is reversible (remove-item / re-add).
- **Rollback:** new service method + CLI command + test file; revert is a clean
  `git revert`. The WI-3326 re-home is one append-only membership version,
  reversible via `remove-item`.

## In-Root Placement Evidence

All paths under `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/`,
`groundtruth-kb/tests/`). No `applications/` paths.

## Recommended Commit Type

`feat` (net-new operator command + service method + tests).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
