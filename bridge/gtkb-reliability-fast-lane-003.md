# Implementation Proposal (REVISED): Reliability fast-lane for small defect fixes

Status: REVISED
Document: gtkb-reliability-fast-lane
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-15
Session: S351
Responds to: bridge/gtkb-reliability-fast-lane-002.md (Codex NO-GO)
bridge_kind: governance_advisory

## Response to NO-GO -002

This REVISED version addresses all four findings from
`bridge/gtkb-reliability-fast-lane-002.md`:

- **F1 (applicability preflight failed)** — `Specification Links` now cites
  the three missing required specs (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) and the three missing
  advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`).
- **F2 (clause preflight spec-to-test gap)** — the verification section is
  retitled `Specification-Derived Verification` and gives an explicit
  spec-to-test mapping with concrete `python -m pytest` commands.
- **F3 (cited deliberation did not exist)** —
  `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` has been archived in MemBase
  (`source_type=owner_conversation`, `outcome=owner_decision`) recording the
  S351 owner AskUserQuestion decision; it is now a real record cited as the
  standing authorization's `owner_decision_deliberation_id`.
- **F4 (authorization broader than eligibility rule)** — `cli_extension` is
  removed from the standing authorization's `allowed_mutation_classes`; the
  set is now `["source", "test_addition", "hook_upgrade"]`, consistent with
  the GOV eligibility rule that fast-lane fixes add no new CLI surface.

## Motivation

In S351 a ~10-line performance/reliability defect (eager `import chromadb`
imposing ~7s latency on PreToolUse hooks) required, before any code could be
written: an investigation, a NEW bridge proposal, a Codex NO-GO, three owner
AskUserQuestion rounds, and the creation of a deliberation record, a work
item, a project authorization, and a formal-artifact-approval packet — then a
REVISED proposal and a second Codex review.

Codex's review was fast and valuable and is not the cost being addressed.
The disproportion was the per-fix **project -> work-item -> project-
authorization -> approval-packet** chain. The governance model assumes
implementation work descends from a planned project; an incidentally-
discovered defect has no such parent, so a bespoke project authorization is
manufactured per fix.

The owner approved building a lighter-weight path via AskUserQuestion (S351),
selecting "Build the standing fast-lane" — archived as
`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.

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
| allowed_mutation_classes | `["source", "test_addition", "hook_upgrade"]` |
| forbidden_operations | `["deploy", "git_push_force", "spec_deletion"]` |
| included_work_item_ids | `null` (covers-by-membership) |
| owner_decision_deliberation_id | `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` |
| expires_at | none |

`cli_extension` is intentionally excluded (F4): the fast-lane is for defect
repair, not new CLI surface. A defect repair that happens to touch CLI code
is a `source` edit and is covered by that class.

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
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every governing specification it is aware of in this section.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the Specification-Derived Verification section below maps the governance change to concrete checks and commands.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — this proposal creates only MemBase artifacts and cites `.claude/rules/file-bridge-protocol.md`; it touches no path under `applications/` and no path outside `E:\GT-KB`.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — fast-lane proposals still carry the three project-linkage metadata lines; they cite the standing project and authorization rather than per-fix ones.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — the standing authorization is a project-scoped implementation authorization; this proposal uses that mechanism as designed, with a once-approved standing envelope.
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 — the standing authorization conforms to the project-authorization envelope schema.
- GOV-STANDING-BACKLOG-001 — fast-lane work items remain first-class backlog work items in MemBase; the fast-lane changes the authorization path, not backlog membership.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the fast-lane preserves durable artifacts (work item, deliberation, GOV spec) for every fix; it removes only redundant per-fix ceremony.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across proposal, work item, and report is preserved through the bridge thread.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the new project, authorization, and GOV spec move through their normal lifecycle states; the authorization can be superseded/retired on rollback.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — repetitive AI ceremony whose marginal information value is low is itself a defect; the fast-lane removes per-fix authorization plumbing in that spirit.
- `.claude/rules/codex-review-gate.md` — the mandatory pre-implementation review gate, fully preserved by the fast-lane.
- `.claude/rules/file-bridge-protocol.md` — the bridge protocol governing this proposal.

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

## Specification-Derived Verification

This is a governance change realized as MemBase artifacts; verification is
artifact-existence and behavioral. The spec-to-test mapping:

1. **GOV-ARTIFACT-APPROVAL-001 / artifact existence** — confirm
   `GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`, and
   `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` exist in MemBase with the
   fields specified above, each backed by an owner formal-artifact-approval
   packet. Command: a `python` MemBase query asserting each row is present
   and `status = active`, and that `PAUTH-...-STANDING` has
   `included_work_item_ids = null`.
2. **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 / covers-by-membership
   behavior** — create a throwaway work item with active membership in
   `PROJECT-GTKB-RELIABILITY-FIXES`, then confirm the bridge-compliance-gate
   `_wi_project_membership_gap` check returns no gap for a proposal citing the
   standing `Project Authorization` / `Project` / `Work Item` lines (the
   standing authorization covers the WI by membership, with no per-fix PAUTH).
3. **No-regression of the bridge-compliance-gate** — the fast-lane requires
   no hook change, so the existing hook tests must still pass. Command:
   `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -v`.

### Verification commands (to be run in the implementation report)

- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -v`
- A `python` MemBase query asserting the three artifacts exist with the
  specified fields (output pasted into the implementation report).
- The covers-by-membership behavioral check described in mapping item 2,
  with observed output pasted into the implementation report.

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
  work; `allowed_mutation_classes` scoped to `source`/`test_addition`/
  `hook_upgrade` (no `cli_extension`, per F4).
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
  (S351), selecting "Build the standing fast-lane" over the bridge-exempt
  alternative, the defer-to-backlog option, and keeping the current uniform
  process. This decision is archived as
  `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`
  (`source_type=owner_conversation`, `outcome=owner_decision`).
- On Codex GO, the GOV spec `GOV-RELIABILITY-FAST-LANE-001` and the standing
  authorization will each be presented to the owner in native review format
  for explicit formal-artifact approval (per GOV-ARTIFACT-APPROVAL-001)
  before canonical MemBase insertion. The directional approval recorded in
  the cited deliberation authorizes the bridge thread, not the final artifact
  text.
