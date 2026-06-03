REVISED

bridge_kind: implementation_proposal
Document: gtkb-projects-remove-item-cli-slice-1
Version: 008
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-007.md NO-GO
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

# Response to NO-GO -007

NO-GO -007 (Codex) responded to -005 (concurrently with the -006 GO, which it
supersedes per INDEX-latest-wins) and closed the prior F1/F2 except for one
verification gap: the CLI test plan named only `--status active`, not the
empty/whitespace `--status` case. Both findings narrow to a single trivial
addition.

## F1 (-007) — CLI empty/whitespace status rejection coverage — CORRECTED

The service-layer invariant already rejects empty/whitespace and case-insensitive
`active` (the `test_remove_rejects_active_status` service test is parametrized
over `active`/`Active`/`ACTIVE`/`  active  `/``/`   `). This REVISED adds an
explicit **CLI-level** empty/whitespace test, `test_cli_remove_item_rejects_empty_status`,
so the public command behavior is verified for the empty case as well as the
active case. No service/CLI code change is required beyond what -005 specified —
the invariant already covers empty/whitespace; only the CLI test coverage is
added.

All other -005 content (true two-step WI-3326 split-out move; non-active-status
invariant; code-only scope matching the PAUTH) is carried forward unchanged.

## Summary

Implement WI-4266 (code slice): `ProjectLifecycleService.remove_project_item` +
`gt projects remove-item` CLI to detach a work-item membership (append-only,
non-active status). General capability for active-on-retired residuals. No live
MemBase mutation in this slice; the WI-3326 move is split out. Second
operational-load CLI per `DELIB-20260623`.

## Scope (code/test/CLI ONLY)

### (a) `ProjectLifecycleService.remove_project_item`

- `remove_project_item(project_id, work_item_id, *, changed_by, change_reason, status="removed")`.
- **Non-active-status invariant:** raises `ProjectLifecycleError` if `status` is
  empty/whitespace or case-insensitively `active`.
- Fails closed when no active membership exists; carries forward role/order/
  source; appends a non-active membership version via
  `db.link_project_work_item(..., status=status)`. Append-only.

### (b) `gt projects remove-item` CLI

`gt projects remove-item PROJECT_ID WORK_ITEM_ID --change-reason <text> [--status removed] [--changed-by ...] [--json]`,
mapping `ProjectLifecycleError` (including the non-active-status rejection) to a
non-zero `click.ClickException`.

### NOT in this slice

No live MemBase membership mutation by this implementation. The WI-3326 move is
the split-out follow-up below.

## Split-Out Follow-Up (WI-3326 re-home — true move)

Unchanged from -005. After this CLI is VERIFIED, a separately-authorized
two-step move (under a `project_membership_mutation` authorization):

1. `gt projects remove-item PROJECT-GTKB-STARTUP-ENHANCEMENTS WI-3326 --change-reason "Detach active-on-retired residual per DELIB-20260624"`
2. `gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 --change-reason "Re-home per DELIB-20260624"`

Evidence: WI-3326 absent from the retired project's active list; the old
membership preserved append-only with a non-active status; WI-3326 active in
deterministic-services. (Verified live: WI-3326 has `project_name=None` but an
active `PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326` membership on the retired
project.)

## Owner Decisions / Input

- **Owner AUQ "Operational-load CLIs first"** (`DELIB-20260623`): WI-4266 second CLI.
- **Owner AUQ "Re-home WI-3326 + continue"** (`DELIB-20260624`): the WI-3326 move
  (split out as a separate authorized operation).
- Authorized by `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS`
  (active; WI-4266; `source`/`test_addition`/`cli_extension`) — matches this
  code-only scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed/tracked through the file bridge.
- `GOV-STANDING-BACKLOG-001` — WI-4266 governed backlog item.
- `GOV-08` — membership state must reflect reality; the non-active-status
  invariant prevents a false-success that would misrepresent active state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under the
  operational-load-CLIs PAUTH; scope matches its mutation classes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item / Owner Decision metadata present.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — membership active → non-active transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all files under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).

## Prior Deliberations

- `DELIB-20260623` — owner "tackle the 5 / CLIs first"; WI-4266 sequence.
- `DELIB-20260624` — owner re-home decision (WI-3326 move; split-out follow-up).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic operator CLIs.
- The `gt bridge revise` CLI thread (`gtkb-bridge-revise-cli-slice-1`, VERIFIED)
  — sibling operational-load CLI; surface/test precedent.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_projects_remove_item.py`

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-STANDING-BACKLOG-001`, `GOV-08`, and
the project-lifecycle model govern. No new specification capture required.

## Design (reuse-first)

`remove_project_item` validates non-active status (rejects empty/whitespace and
`active`), then reuses `db.link_project_work_item(..., status="removed")`,
carrying forward role/order/source. The CLI mirrors `gt projects add-item` and
surfaces rejections as `ClickException`.

## Spec-Derived Verification Plan

| Specification | Test | Expected |
|---|---|---|
| `GOV-08` removal detaches | `test_remove_project_item_detaches_active_membership` | WI absent from active list; `status=removed` version exists |
| append-only preserved | `test_remove_appends_version_preserves_history` | new version appended; prior active version remains |
| fail-closed: no active membership | `test_remove_nonexistent_membership_raises` | raises `ProjectLifecycleError` |
| F2 invariant (service) | `test_remove_rejects_active_status` (params: active/Active/ACTIVE/padded/empty/whitespace) | each raises `ProjectLifecycleError`; active membership untouched |
| F2 invariant (CLI, active) | `test_cli_remove_item_rejects_active_status` | `--status active` exits non-zero |
| **F1 -007 (CLI, empty/whitespace)** | `test_cli_remove_item_rejects_empty_status` | `--status ""` (and whitespace) exits non-zero; active membership untouched |
| role/order/source carry-forward | `test_remove_carries_forward_role_and_order` | removed version preserves prior role/order/source |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_remove_then_readd_cycle` | active → removed → active round-trips |
| CLI wiring | `test_cli_remove_item_invokes_service` | command calls the service and reports the removal |
| no-live-mutation (rev #4) | post-impl `git diff` + temp-DB tests | commit touches only the 3 target paths; no live membership row added |

Test command:
`PYTHONPATH=groundtruth-kb/src python -m pytest groundtruth-kb/tests/test_projects_remove_item.py -q`
plus `ruff check` and `ruff format --check`. All tests use a temporary
`KnowledgeDB`.

## Acceptance Criteria

1. `remove_project_item` detaches an active membership (append-only non-active
   status), carries forward role/order/source, fails closed when none exists.
2. `remove_project_item` rejects empty/whitespace and case-insensitive `active`;
   the CLI surfaces the rejection as a non-zero `ClickException`.
3. **CLI verification covers BOTH the `--status active` case and the
   empty/whitespace `--status` case.**
4. `gt projects remove-item` is registered and delegates to the service.
5. New test module passes; `ruff check` + `ruff format --check` clean.
6. Pre/post bridge preflights pass (no missing required specs; 0 blocking gaps).
7. No live MemBase mutation during implementation: the commit changes only the
   three target paths and adds no `project_work_item_memberships` version.

(The WI-3326 move is NOT an acceptance criterion of this slice; it is the
split-out follow-up.)

## Risks / Rollback

- **Risk: false-success removal** (`--status active`/empty). Mitigation: the
  non-active-status invariant rejects both; service + CLI tests cover active AND
  empty/whitespace.
- **Risk: removing a non-active membership.** Mitigation: fail closed; append-only
  + carry-forward makes a mistaken removal reversible via `add-item`.
- **Rollback:** new service method + CLI command + test file; clean `git revert`.
  No live MemBase mutation in this slice.

## In-Root Placement Evidence

All paths under `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/`,
`groundtruth-kb/tests/`). No `applications/` paths.

## Recommended Commit Type

`feat` (net-new operator command + service method + tests).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
