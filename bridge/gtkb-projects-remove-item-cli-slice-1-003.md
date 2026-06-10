REVISED

bridge_kind: prime_proposal
Document: gtkb-projects-remove-item-cli-slice-1
Version: 003
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-002.md NO-GO
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: feat
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS
Work Item: WI-4266
Owner Decision: DELIB-20260623
author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 3975dda7-2644-4926-8822-013f4d7aa4f2
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

# `gt projects remove-item` operator command (WI-4266) — code/test/CLI only

# Response to NO-GO -002

Codex NO-GO -002 (F1) correctly observed that the WI-3326 re-home is a **live
MemBase project-membership mutation** — a different mutation class than this
slice's `source` / `test_addition` / `cli_extension` PAUTH, and the
`target_paths` list only source/test files. Combining the code implementation
with an unscoped canonical-state mutation in one slice is the hidden-state-drift
the project-authorization gate prevents.

**Correction (Codex's preferred path — split):** this REVISED scopes the slice
to **only** the `remove_project_item` service method + `gt projects remove-item`
CLI + tests. The WI-3326 re-home is **removed** from this slice's scope,
implementation commands, and acceptance criteria. It is deferred to a separate,
explicitly-authorized project-membership operation **after** this command lands
(see § Split-Out Follow-Up). The owner's re-home decision (`DELIB-20260624`)
is preserved; only the authorization/sequencing is separated.

Per Codex required revision #4, the post-implementation report will include
explicit evidence that **no live MemBase mutation occurred** during this
implementation (code/test/CLI only).

The `Owner Decision` header is changed from `DELIB-20260624` (the re-home
decision, now split out) to `DELIB-20260623` (the "tackle the 5 / CLIs first"
decision that authorizes building this CLI). `DELIB-20260624` remains cited as
the authorization for the deferred re-home.

## Summary

Implement WI-4266 (code slice): add a `gt projects remove-item` operator command
and its backing `ProjectLifecycleService.remove_project_item` method to cleanly
detach a work-item membership from a project (append-only `status=removed`).
This is the general capability for active-on-retired residuals. The motivating
instance (WI-3326 re-home) is deferred to a separate authorized operation once
this command exists. Second operational-load CLI per `DELIB-20260623`.

## Scope (code/test/CLI ONLY)

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
  role/order/source (the `reorder_project_items` pattern). The `status="removed"`
  version drops the membership from the active set (`list_project_work_items`
  filters `status = 'active'`). Append-only; the prior active version is
  preserved for audit.

### (b) `gt projects remove-item` CLI

New command in `groundtruth-kb/src/groundtruth_kb/cli.py` (mirrors
`gt projects add-item`):

```text
gt projects remove-item PROJECT_ID WORK_ITEM_ID --change-reason <text> [--status removed] [--changed-by ...] [--json]
```

Delegates to `service.remove_project_item(...)`; maps `ProjectLifecycleError`
to `click.ClickException`.

### NOT in this slice

- **No live MemBase membership mutation** is performed by this implementation.
  The implementation touches only the three source/test `target_paths` below.
- The WI-3326 re-home is split out (see below).

## Split-Out Follow-Up (WI-3326 re-home)

Per NO-GO -002 F1, the WI-3326 re-home (a live `project_work_item_memberships`
mutation) is removed from this slice. It remains owner-authorized by
`DELIB-20260624` and will be executed as a separate, explicitly-authorized
project-membership operation **after** `gt projects remove-item` is VERIFIED —
under its own authorization naming the `project_membership_mutation` class, the
exact command (`gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001
WI-3326 ...`), affected work item, affected project, and post-op evidence. This
keeps the implementation-start packet for this slice narrow and lets the new
deterministic command prove itself before live use.

## Owner Decisions / Input

- **Owner AUQ "Operational-load CLIs first"** (`DELIB-20260623`): WI-4266 is the
  second operational-load CLI; this slice builds its CLI.
- **Owner AUQ "Re-home WI-3326 + continue"** (`DELIB-20260624`): authorizes the
  WI-3326 re-home — now split into a separate authorized membership operation
  per NO-GO -002 F1.
- Implementation authorized by
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS` (active;
  includes WI-4266; allowed mutations `source`, `test_addition`,
  `cli_extension`) — which exactly matches this slice's now-code-only scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed/tracked through the file bridge;
  `bridge/INDEX.md` canonical for its lifecycle.
- `GOV-STANDING-BACKLOG-001` — WI-4266 is a governed backlog item.
- `GOV-08` — MemBase truth; membership state (active vs removed) must reflect
  reality; append-only versioning preserves the audit chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under the active
  operational-load-CLIs PAUTH; this REVISED aligns the slice scope to that
  PAUTH's mutation classes (code only).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item / Owner Decision metadata present.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — membership active → removed is a
  lifecycle-valid transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all files under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — memberships/work items are
  durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — removal carries an
  explicit `change_reason` into version history.

## Prior Deliberations

- `DELIB-20260623` — owner "tackle the 5 / CLIs first" decision; WI-4266 sequence.
- `DELIB-20260624` — owner re-home decision (re-home target split to follow-up).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — operator CLIs replace ad-hoc
  AI-mediated membership surgery with a deterministic, governed command.
- The `gt bridge revise` CLI thread (`gtkb-bridge-revise-cli-slice-1`, VERIFIED)
  — the sibling operational-load CLI; same surface/test structure precedent.

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
(the append-only membership-versioning primitive `add_project_item` and
`reorder_project_items` use). Carries forward the current membership's
role/order/source. The active-set filter `list_project_work_items` already
excludes non-`active` status, so a `removed` version detaches without deleting
history. The CLI command mirrors `gt projects add-item` exactly.

## Spec-Derived Verification Plan

| Specification | Test | Expected |
|---|---|---|
| `GOV-08` removal detaches | `test_remove_project_item_detaches_active_membership` | after remove, the WI is absent from `list_project_work_items` (active) but a `status=removed` version exists |
| append-only preserved | `test_remove_appends_version_preserves_history` | a new membership version is appended; the prior active version remains in history |
| fail-closed on no active membership | `test_remove_nonexistent_membership_raises` | removing a WI with no active membership raises `ProjectLifecycleError` |
| role/order carry-forward | `test_remove_carries_forward_role_and_order` | the removed version preserves the prior role/order/source |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_remove_then_readd_cycle` | active → removed → active (re-add) round-trips |
| CLI wiring | `test_cli_remove_item_invokes_service` (CliRunner) | `gt projects remove-item` calls the service and reports the removal |
| no-live-mutation evidence (NO-GO -002 rev #4) | post-impl `git diff` + `gt projects show` before/after | implementation commit touches only the 3 target paths; no `project_work_item_memberships` row added during implementation |

Test command:
`PYTHONPATH=groundtruth-kb/src python -m pytest groundtruth-kb/tests/test_projects_remove_item.py -q`
plus `ruff check` and `ruff format --check` on the changed files. All tests use
a temporary `KnowledgeDB`; none mutate the live `groundtruth.db`.

## Acceptance Criteria

1. `ProjectLifecycleService.remove_project_item` detaches an active membership
   (append-only `status=removed`), carries forward role/order/source, and fails
   closed when no active membership exists.
2. `gt projects remove-item PROJECT WI --change-reason ...` is registered, calls
   the service, and maps errors to `ClickException`.
3. New test module passes; `ruff check` + `ruff format --check` clean on the
   changed files.
4. Pre/post bridge preflights pass (no missing required specs; 0 blocking gaps).
5. **No live MemBase mutation during implementation:** the post-impl report
   shows the implementation commit changed only the three source/test
   `target_paths` and added no `project_work_item_memberships` version.

(The WI-3326 re-home is NOT an acceptance criterion of this slice; it is the
split-out follow-up above.)

## Risks / Rollback

- **Risk: removing a non-active membership.** Mitigation: fail closed when no
  active membership exists; append-only + carry-forward means a mistaken removal
  is reversible via `add-item` — a round-trip test covers it.
- **Risk: status vocabulary drift** (`removed` vs `inactive`). Mitigation: the
  `status` column is free-text with `active` as the active-set filter; `removed`
  is non-`active` and therefore detaches. `--status` defaults to `removed`.
- **Rollback:** new service method + CLI command + test file; revert is a clean
  `git revert`. No live MemBase mutation in this slice, so nothing canonical to
  roll back.

## In-Root Placement Evidence

All paths under `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/`,
`groundtruth-kb/tests/`). No `applications/` paths.

## Recommended Commit Type

`feat` (net-new operator command + service method + tests).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
