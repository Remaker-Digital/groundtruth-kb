REVISED

bridge_kind: implementation_proposal
Document: gtkb-projects-remove-item-cli-slice-1
Version: 005
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-004.md NO-GO
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

# Response to NO-GO -004

Codex NO-GO -004 confirmed the -003 split fixed the authorization-scope defect,
and raised two further defects. Both are corrected here; both improved the design.

## F1 (-004) — split-out WI-3326 follow-up was add-only — CORRECTED

Codex observed that WI-3326 still has an **active membership on the retired**
PROJECT-GTKB-STARTUP-ENHANCEMENTS, so an add-only re-home would leave it active
on BOTH projects (not a re-home). **Verified live at filing time:**

```text
work_items.project_name (WI-3326)                       = None
current_project_work_item_memberships (WI-3326)         = PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326, project=PROJECT-GTKB-STARTUP-ENHANCEMENTS, status=active
projects.status (PROJECT-GTKB-STARTUP-ENHANCEMENTS)     = retired
```

So the re-home is a true **move**, and it is the motivating use of the very
`remove-item` command this slice builds. The Split-Out Follow-Up below is
rewritten as a two-step move (remove-from-retired + add-to-active) with the
three-part evidence Codex required. (It remains split-out: separately
authorized, after this CLI is VERIFIED.)

## F2 (-004) — `remove-item --status active` false-success — CORRECTED

Codex observed that `--status` accepts any value, so `remove-item --status
active` would append an *active* membership (false success). Corrected: a
**non-active-status invariant** is added to the design, acceptance criteria, and
tests — `remove_project_item` rejects empty status and any case-insensitive
`active`; the CLI surfaces the rejection as `ClickException`.

## Summary

Implement WI-4266 (code slice): add a `gt projects remove-item` operator command
and its backing `ProjectLifecycleService.remove_project_item` method to cleanly
detach a work-item membership from a project (append-only, non-active status).
General capability for active-on-retired residuals. Second operational-load CLI
per `DELIB-20260623`. No live MemBase mutation in this slice; the WI-3326 move
is split out.

## Scope (code/test/CLI ONLY)

### (a) `ProjectLifecycleService.remove_project_item`

New method in `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`:

- `remove_project_item(project_id, work_item_id, *, changed_by, change_reason, status="removed")`.
- **Non-active-status invariant (F2):** raises `ProjectLifecycleError` if
  `status` is empty/whitespace or case-insensitively equals `active`. A command
  named `remove-item` must never append an active membership version.
- Looks up the current active membership (stable id
  `_stable_project_link_id("PWM", project_id, work_item_id)`); raises
  `ProjectLifecycleError` if there is no active membership to remove (fail
  closed — no silent no-op).
- Appends a new membership version via
  `db.link_project_work_item(..., status=status, membership_role=<carried>,
  membership_order=<carried>, source=<carried>)`, carrying forward role/order/
  source (the `reorder_project_items` pattern). The non-`active` version drops
  the membership from the active set (`list_project_work_items` filters
  `status = 'active'`). Append-only; the prior active version is preserved.

### (b) `gt projects remove-item` CLI

New command in `groundtruth-kb/src/groundtruth_kb/cli.py` (mirrors
`gt projects add-item`):

```text
gt projects remove-item PROJECT_ID WORK_ITEM_ID --change-reason <text> [--status removed] [--changed-by ...] [--json]
```

Delegates to `service.remove_project_item(...)`; maps `ProjectLifecycleError`
(including the non-active-status rejection) to `click.ClickException` (non-zero
exit).

### NOT in this slice

- No live MemBase membership mutation by this implementation (only the three
  source/test `target_paths`).
- The WI-3326 move is split out (below).

## Split-Out Follow-Up (WI-3326 re-home — true move)

Per NO-GO -002/-004, the WI-3326 re-home is a live membership mutation, split
out from this code slice and separately authorized. It is a **two-step move**
(NOT add-only), executed **after** `gt projects remove-item` is VERIFIED, under
its own authorization naming the `project_membership_mutation` class:

1. `gt projects remove-item PROJECT-GTKB-STARTUP-ENHANCEMENTS WI-3326 --change-reason "Detach active-on-retired residual per DELIB-20260624"`
2. `gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 --change-reason "Re-home per DELIB-20260624"`

Required post-op evidence for that separate operation:
- WI-3326 **absent** from PROJECT-GTKB-STARTUP-ENHANCEMENTS active work-item list;
- the old `PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326` membership preserved
  append-only with a **non-active** status;
- WI-3326 **active** in PROJECT-GTKB-DETERMINISTIC-SERVICES-001.

Owner intent (`DELIB-20260624`) preserved; this is the deterministic, governed
correction the prior reconciliation (`gtkb-startup-enhancements-completion-reconciliation`)
recommended.

## Owner Decisions / Input

- **Owner AUQ "Operational-load CLIs first"** (`DELIB-20260623`): WI-4266 is the
  second operational-load CLI; this slice builds its CLI.
- **Owner AUQ "Re-home WI-3326 + continue"** (`DELIB-20260624`): authorizes the
  WI-3326 move — split into a separate authorized membership operation.
- Implementation authorized by
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS` (active;
  WI-4266; mutations `source`, `test_addition`, `cli_extension`) — matches this
  code-only scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed/tracked through the file bridge;
  `bridge/INDEX.md` canonical for its lifecycle.
- `GOV-STANDING-BACKLOG-001` — WI-4266 is a governed backlog item.
- `GOV-08` — MemBase truth; membership state must reflect reality; append-only
  versioning preserves the audit chain; the non-active-status invariant prevents
  a false-success that would misrepresent active state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under the active
  operational-load-CLIs PAUTH; scope matches the PAUTH's mutation classes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item / Owner Decision metadata present.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — membership active → non-active is a
  lifecycle-valid transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all files under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — memberships/work items are
  durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — removal carries an
  explicit `change_reason` into version history.

## Prior Deliberations

- `DELIB-20260623` — owner "tackle the 5 / CLIs first" decision; WI-4266 sequence.
- `DELIB-20260624` — owner re-home decision (re-home is a move, split to follow-up).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — operator CLIs replace ad-hoc
  AI-mediated membership surgery with a deterministic, governed command.
- The `gt bridge revise` CLI thread (`gtkb-bridge-revise-cli-slice-1`, VERIFIED)
  — sibling operational-load CLI; surface/test structure precedent.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (modify — add
  `remove_project_item` service method with the non-active-status invariant)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (modify — add `gt projects
  remove-item` command)
- `groundtruth-kb/tests/test_projects_remove_item.py` (new — unit tests)

## Requirement Sufficiency

**Existing requirements sufficient.** WI-4266's description is the operative
requirement; `GOV-STANDING-BACKLOG-001`, `GOV-08`, and the project-lifecycle
model govern. No new specification capture required.

## Design (reuse-first)

`remove_project_item` validates the status is non-active (F2), then reuses
`db.link_project_work_item(..., status="removed")` (the append-only membership
primitive `add_project_item`/`reorder_project_items` use), carrying forward
role/order/source. The active-set filter `list_project_work_items` excludes
non-`active` status, so the version detaches without deleting history. The CLI
mirrors `gt projects add-item`.

## Spec-Derived Verification Plan

| Specification | Test | Expected |
|---|---|---|
| `GOV-08` removal detaches | `test_remove_project_item_detaches_active_membership` | after remove, the WI is absent from active `list_project_work_items` but a `status=removed` version exists |
| append-only preserved | `test_remove_appends_version_preserves_history` | a new membership version is appended; the prior active version remains in history |
| fail-closed: no active membership | `test_remove_nonexistent_membership_raises` | removing a WI with no active membership raises `ProjectLifecycleError` |
| **F2 non-active invariant (service)** | `test_remove_rejects_active_status` | `remove_project_item(..., status="active")` (any case) and empty status raise `ProjectLifecycleError` |
| **F2 non-active invariant (CLI)** | `test_cli_remove_item_rejects_active_status` | `gt projects remove-item ... --status active` exits non-zero (`ClickException`) |
| role/order carry-forward | `test_remove_carries_forward_role_and_order` | the removed version preserves the prior role/order/source |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_remove_then_readd_cycle` | active → removed → active (re-add) round-trips |
| CLI wiring | `test_cli_remove_item_invokes_service` (CliRunner) | `gt projects remove-item` calls the service and reports the removal |
| no-live-mutation evidence (rev #4) | post-impl `git diff` + `gt projects show` before/after | implementation commit touches only the 3 target paths; no `project_work_item_memberships` row added during implementation |

Test command:
`PYTHONPATH=groundtruth-kb/src python -m pytest groundtruth-kb/tests/test_projects_remove_item.py -q`
plus `ruff check` and `ruff format --check`. All tests use a temporary
`KnowledgeDB`; none mutate the live `groundtruth.db`.

## Acceptance Criteria

1. `remove_project_item` detaches an active membership (append-only non-active
   status), carries forward role/order/source, and fails closed when no active
   membership exists.
2. **`remove_project_item` rejects empty status and case-insensitive `active`;
   the CLI surfaces the rejection as a non-zero `ClickException`.**
3. `gt projects remove-item PROJECT WI --change-reason ...` is registered and
   delegates to the service.
4. New test module passes (including the two F2 invariant tests); `ruff check` +
   `ruff format --check` clean on the changed files.
5. Pre/post bridge preflights pass (no missing required specs; 0 blocking gaps).
6. **No live MemBase mutation during implementation:** the post-impl report
   shows the implementation commit changed only the three source/test
   `target_paths` and added no `project_work_item_memberships` version.

(The WI-3326 move is NOT an acceptance criterion of this slice; it is the
split-out follow-up above.)

## Risks / Rollback

- **Risk: false-success removal** (`--status active`). Mitigation: the
  non-active-status invariant (F2) rejects it at the service layer; two tests
  cover service + CLI rejection.
- **Risk: removing a non-active membership.** Mitigation: fail closed when no
  active membership exists; append-only + carry-forward makes a mistaken removal
  reversible via `add-item` — a round-trip test covers it.
- **Rollback:** new service method + CLI command + test file; clean `git
  revert`. No live MemBase mutation in this slice.

## In-Root Placement Evidence

All paths under `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/`,
`groundtruth-kb/tests/`). No `applications/` paths.

## Recommended Commit Type

`feat` (net-new operator command + service method + tests).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
