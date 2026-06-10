# Implementation Proposal: Reliability fast-lane for small defect fixes

Status: NEW
Document: gtkb-reliability-fast-lane
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-14
Session: S351
bridge_kind: governance_advisory

## Motivation

In S351 a ~10-line performance/reliability defect (eager `import chromadb`
imposing ~7s latency on PreToolUse hooks) required, before any code could be
written: an investigation, a NEW bridge proposal, a Codex NO-GO, three owner
AskUserQuestion rounds, and the creation of a deliberation record, a work
item, a project authorization, and a formal-artifact-approval packet — then a
REVISED proposal and a second Codex review.

Codex's review was fast and valuable and is not the cost being addressed.
The disproportion was the per-fix **project -> work-item -> project-
authorization -> approval-packet** chain (Codex NO-GO `-002` finding F2). The
governance model assumes implementation work descends from a planned project;
an incidentally-discovered defect has no such parent, so a bespoke project
authorization is manufactured per fix.

The owner approved building a lighter-weight path via AskUserQuestion (S351):
option "Build the standing fast-lane."

## Proposed governance change

Create one durable, once-approved governance structure so that future small
defect/reliability fixes skip the per-fix authorization ceremony while keeping
the bridge review, the work item, and all safety gates intact.

### Artifact 1 - Project `PROJECT-GTKB-RELIABILITY-FIXES`

A standing project: the permanent home for small, incidentally-discovered
defect and reliability fixes that do not belong to a planned workstream.

### Artifact 2 - Standing project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`

| Field | Value |
|---|---|
| project_id | `PROJECT-GTKB-RELIABILITY-FIXES` |
| status | active |
| authorization_name | Reliability fast-lane standing authorization |
| scope_summary | Standing authorization for small defect/reliability fixes meeting the GOV-RELIABILITY-FAST-LANE-001 eligibility criteria. |
| allowed_mutation_classes | `["source", "test_addition", "hook_upgrade", "cli_extension"]` |
| forbidden_operations | `["deploy", "git_push_force", "spec_deletion"]` |
| included_work_item_ids | `null` (covers-by-membership) |
| owner_decision_deliberation_id | `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` |
| expires_at | none |

The `included_work_item_ids = null` choice is the mechanism: the bridge-
compliance-gate's `_wi_project_membership_gap` rejects a work item only when
`included` is *non-empty and* missing it. A null/empty `included` list means
"every work item with active membership in this project is covered." New
fast-lane work items are therefore auto-covered simply by being created under
`PROJECT-GTKB-RELIABILITY-FIXES`. **No hook change is required** — this works
with the gate logic exactly as it stands today.

### Artifact 3 - Governance specification `GOV-RELIABILITY-FAST-LANE-001`

Draft content (presented for owner formal-artifact approval on GO):

> **GOV-RELIABILITY-FAST-LANE-001 - Reliability fast-lane for small defect fixes**
>
> A work item is *fast-lane eligible* when ALL of the following hold:
> 1. `origin` is `defect` or `regression` (never `new`).
> 2. The change introduces no new public API, CLI surface, or behavior
>    beyond removing the defect.
> 3. The change requires no new or revised requirement or specification.
> 4. The change is small and single-concern — as a guide, ~3 source files
>    and ~150 net lines or fewer. Larger changes use the standard project
>    path.
>
> A fast-lane eligible work item is created under `PROJECT-GTKB-RELIABILITY-
> FIXES` and is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
> through active project membership. Such a fix does NOT require a per-fix
> deliberation record, a per-fix project authorization, or a per-fix formal-
> artifact-approval packet.
>
> A fast-lane fix DOES still require, unchanged: a bridge proposal carrying
> the standard `Project Authorization` / `Project` / `Work Item` metadata
> lines (citing the standing artifacts); Codex GO before implementation;
> the implementation-start authorization packet derived from that GO; a
> post-implementation report; and Codex VERIFIED. All root-boundary,
> credential-scan, hook-parity, and formal-artifact gates remain in force.
>
> Loyal Opposition issues NO-GO on any fast-lane proposal whose work item
> fails an eligibility criterion, directing it to refile under the standard
> project path.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — the fast-lane preserves the file-bridge authority model; fast-lane fixes still flow NEW -> GO -> implement -> report -> VERIFIED.
- GOV-ARTIFACT-APPROVAL-001 — the new GOV spec and the standing authorization are formal artifacts and will be presented for explicit owner approval with packets before canonical insertion.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — fast-lane proposals still carry the three project-linkage metadata lines; they cite the standing project and authorization rather than per-fix ones.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — the standing authorization is a project-scoped implementation authorization; this proposal uses that mechanism as designed, with a once-approved standing envelope.
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 — the standing authorization conforms to the project-authorization envelope schema.
- GOV-STANDING-BACKLOG-001 — fast-lane work items remain first-class backlog work items in MemBase; the fast-lane changes the authorization path, not backlog membership.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — repetitive AI ceremony whose marginal information value is low is itself a defect; the fast-lane removes per-fix authorization plumbing in that spirit.
- `.claude/rules/codex-review-gate.md` — the mandatory pre-implementation review gate, fully preserved by the fast-lane.
- `.claude/rules/file-bridge-protocol.md` — the bridge protocol governing this proposal.

## Prior Deliberations

- `DELIB-S351-HOOK-IMPORT-LATENCY-AUTHORIZATION` — the S351 owner decision and the per-fix authorization chain whose disproportion for a small fix motivated this proposal.
- The owner approved building the standing fast-lane via AskUserQuestion (S351); that decision will be archived as `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` during implementation and is the `owner_decision_deliberation_id` for the standing authorization.
- A `search_deliberations` scan for "reliability fast lane", "lightweight defect fix process", and "project authorization ceremony" returned no prior deliberation proposing a lighter authorization path.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal references "standing backlog", "work item", and "backlog" while
describing the fast-lane policy. It is NOT a bulk operation: it creates three
named artifacts (one project, one authorization, one GOV spec) under explicit
owner formal-artifact approval and per-artifact inventory. No work items are
batch-promoted, retired, or mutated. `GOV-STANDING-BACKLOG-001` bulk-operation
clauses do not apply; evidence patterns are per-artifact inventory and
formal-artifact-approval packets.

## What is preserved (deliberately unchanged)

- The bridge proposal and Codex GO / NO-GO / VERIFIED cycle.
- A first-class MemBase work item for every fix.
- The implementation-start authorization packet derived from the GO.
- Root-boundary, credential-scan, hook-parity, and formal-artifact gates.
- The post-implementation report and verification.

The fast-lane removes per-fix *authorization ceremony*, not *review*.

## Verification Plan

This is a governance change; verification is artifact-existence and
behavioral, derived from the linked specifications:

- Confirm `GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`,
  and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` exist in MemBase with
  the fields above, each backed by an owner formal-artifact-approval packet.
- Confirm `PAUTH-...-STANDING` has `included_work_item_ids = null` and
  `status = active`.
- Behavioral check: create a throwaway work item with active membership in
  `PROJECT-GTKB-RELIABILITY-FIXES`, draft a stub bridge proposal citing the
  standing `Project Authorization` / `Project` / `Work Item` lines, and
  confirm the bridge-compliance-gate `_wi_project_membership_gap` check
  returns no gap (the standing authorization covers it by membership).
- Confirm the existing bridge-compliance-gate and `_wi_project_membership_gap`
  tests still pass — the fast-lane requires no hook change, so no regression
  is expected.

## Acceptance Criteria

1. The three artifacts exist in MemBase with the specified fields and
   owner-approval packets.
2. A work item created under `PROJECT-GTKB-RELIABILITY-FIXES` is accepted by
   the bridge-compliance-gate project-linkage check without a per-fix
   authorization.
3. No bridge-compliance-gate hook change is made; existing hook tests pass.
4. `GOV-RELIABILITY-FAST-LANE-001` states the eligibility criteria and the
   preserved-vs-dropped governance steps unambiguously enough for Codex to
   enforce eligibility at review time.

## Risk and Rollback

- **Risk: the standing authorization is a broader blast radius than per-fix
  authorizations.** Mitigated by: tight eligibility criteria in
  GOV-RELIABILITY-FAST-LANE-001; `forbidden_operations` unchanged from every
  other PAUTH; Codex review still mandatory and empowered to NO-GO ineligible
  work; `allowed_mutation_classes` scoped to source/test/hook/cli.
- **Risk: scope creep — features dressed as defect fixes.** Mitigated by the
  `origin in {defect, regression}` and no-new-API / no-new-requirement
  criteria, enforced by Codex at review.
- **Rollback:** set `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` status to
  a terminal state and supersede `GOV-RELIABILITY-FAST-LANE-001`; in-flight
  fast-lane fixes revert to the standard project path. No code is changed by
  this proposal, so there is no source rollback.

## Recommended Commit Type

`feat:` — this adds a new governed capability (the fast-lane), realized as
MemBase artifacts. (Confirmed in the implementation report.)

## Owner Decisions / Input

- The owner approved building the standing fast-lane via AskUserQuestion
  (S351), selecting the option "Build the standing fast-lane" over the
  bridge-exempt alternative, the defer-to-backlog option, and keeping the
  current uniform process.
- On Codex GO, the GOV spec `GOV-RELIABILITY-FAST-LANE-001` and the standing
  authorization will each be presented to the owner in native review format
  for explicit formal-artifact approval (per GOV-ARTIFACT-APPROVAL-001)
  before canonical MemBase insertion. The directional approval recorded here
  authorizes the bridge thread, not the final artifact text.
