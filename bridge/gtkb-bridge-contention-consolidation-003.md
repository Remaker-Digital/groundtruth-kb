REVISED

bridge_kind: governance_review
Document: gtkb-bridge-contention-consolidation
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-01 UTC
Session: 019e8466-acc1-7923-b828-0ef7ab4a7758
Recommended commit type: chore
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Items Affected: WI-3513, WI-3280, WI-3485, WI-AUTO-SPEC-INTAKE-57A736, WI-3265, WI-4213, WI-3320, WI-3334, WI-3322
Responds to: bridge/gtkb-bridge-contention-consolidation-002.md
target_paths: ["groundtruth.db", ".gtkb-state/apply-bridge-contention-consolidation.py", "bridge/gtkb-bridge-contention-consolidation-*.md", "bridge/INDEX.md"]
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e8466-acc1-7923-b828-0ef7ab4a7758
author_model: GPT-5 Codex
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop app; Prime Builder role; local workspace E:\GT-KB

# Bridge Contention Consolidation REVISED-1

## Revision Claim

This revision addresses all `-002` NO-GO findings. It keeps the consolidation
direction unchanged, but makes the MemBase mutation surface explicit, verifies
all three poller status-detail updates, and adds the missing advisory
traceability citation.

## Findings Addressed

### P1 - `target_paths` does not authorize the MemBase mutation surface

Response: accepted and corrected. The parser-readable `target_paths` line now
includes `groundtruth.db`, the helper, the bridge audit files, and
`bridge/INDEX.md`.

This revision also corrects the bridge-kind framing: the work is an
owner-authorized governance-review KB grooming mutation. It is not a source/test
implementation proposal and it does not require a project-scoped PAUTH, but it
does mutate the MemBase database and therefore names `groundtruth.db` directly.

### P2 - Poller status-detail verification checks only one of three mutated WIs

Response: accepted and corrected. The verification plan now reads back all
three poller work items:

- `GTKB-BRIDGE-POLLER-001`
- `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT`
- `GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR`

The expected result enumerates every id and requires the supersession /
reconciliation note on each row.

### P3 - Applicability preflight reports one missing advisory spec

Response: accepted and corrected. `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is now
included in Specification Links.

## Owner Decisions / Input

- 2026-06-01 UTC, S384 AUQ ("Next step"): owner selected "Consolidate
  contention work under one project view" after Prime surfaced that
  bridge-contention work was fragmented across multiple project views.
- 2026-06-01 UTC, S384 AUQ ("Harness C role") plus clarification: dual-PB is
  intended; "active" is capability-gated on bridge-event reception. This makes
  C's interactive INDEX-write contention a first-class standing condition to
  represent in the consolidation.
- 2026-06-01 current session: owner directed first-wave work to concentrate on
  bridge protocol and harness-assignment limitations that cause contention and
  conflict in highly parallel multi-harness work.

No additional owner decision is required for this revised scoping/grooming
proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; `bridge/INDEX.md`
  is canonical.
- `GOV-STANDING-BACKLOG-001` - backlog/project membership grooming authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - current-state evidence and verification
  must read live MemBase state, not cached summaries.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposed artifacts are in
  `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - advisory traceability for preserving
  contention work as durable project/work-item artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory traceability for owner
  decision and backlog grooming.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - poller WIs are retired/superseded
  lifecycle artifacts that need reconciliation notes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan
  below maps every proposed mutation to read-back evidence.

## Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - role/status model and
  active-status capability context.
- `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME` - live INDEX
  lost-update evidence motivating the L1 contention lane.
- `DELIB-2182` - owner authorization for the bridge scheduler lanes/leases
  program, including serialized INDEX writer primitives.
- `DELIB-2351` - prior Loyal Opposition review of cross-harness trigger INDEX
  edit race / quiesce-window work.
- `DELIB-2107` - VERIFIED bridge-compliance WI/project membership history.

No cited deliberation rejects additive project membership for the consolidated
contention view.

## Revised Scope

### IP-1: Create three layer sub-projects

Create these active project records under
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`:

1. `PROJECT-GTKB-BRIDGE-CONTENTION-L1-INDEX-WRITES`
2. `PROJECT-GTKB-BRIDGE-CONTENTION-L2-DISPATCH`
3. `PROJECT-GTKB-BRIDGE-CONTENTION-L3-GATE-RACES`

### IP-2: Additive work-item memberships

Keep existing home memberships and add these consolidated-view memberships:

- L1: `WI-3513`, `WI-3280`
- L2: `WI-3265`, `WI-3485`, `WI-4213`, `WI-AUTO-SPEC-INTAKE-57A736`
- L3: `WI-3320`, `WI-3334`, `WI-3322`

### IP-3: Poller reconciliation notes

Set `status_detail` only, with no lifecycle transition, on:

- `GTKB-BRIDGE-POLLER-001`
- `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT`
- `GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR`

The note should state that each is superseded by the retired-poller to
event-trigger decision and should not be treated as open bridge-contention work.

## Specification-Derived Verification Plan

This is the spec-to-test mapping for a KB grooming mutation. No `python -m
pytest` test applies because the change is an owner-authorized MemBase
read/write operation, not a source-code behavior change. Verification is
therefore read-back command evidence against `groundtruth.db`, with observed
results reported in the implementation report.

| Behavior | Verification command | Expected |
|---|---|---|
| 3 sub-projects exist with correct parent | Read `current_projects` / `db.list_projects()` for `parent_project_id='PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY'` | Lists the three `PROJECT-GTKB-BRIDGE-CONTENTION-L{1,2,3}-*` ids. |
| L1 membership | Read `db.list_project_work_items('PROJECT-GTKB-BRIDGE-CONTENTION-L1-INDEX-WRITES')` | Exactly includes `WI-3280`, `WI-3513`. |
| L2 membership | Read `db.list_project_work_items('PROJECT-GTKB-BRIDGE-CONTENTION-L2-DISPATCH')` | Includes `WI-3265`, `WI-3485`, `WI-4213`, `WI-AUTO-SPEC-INTAKE-57A736`. |
| L3 membership | Read `db.list_project_work_items('PROJECT-GTKB-BRIDGE-CONTENTION-L3-GATE-RACES')` | Exactly includes `WI-3320`, `WI-3322`, `WI-3334`. |
| All pollers flagged | Query all three poller WIs by id | Each row exists and each `status_detail` contains the supersession/reconciliation note. |
| Helper idempotent | Rerun `.gtkb-state/apply-bridge-contention-consolidation.py --dry-run` after the live run | Reports all project/membership/status-detail operations as existing/skipped. |

Implementation report must include the exact read-back command output for all
three poller rows, not a sample row.

## Clause Scope Clarification (Governance KB Grooming)

This is not a bulk backlog lifecycle action. It is a bounded owner-directed
project-view grooming change for one contention cluster, with explicit work item
ids, explicit project ids, and read-back verification for every proposed row.

- No bulk inventory artifact is required beyond this bridge packet because the
  affected ids are enumerated here.
- No review-packet or `DECISION DEFERRED` batch marker applies because no
  deferred multi-item backlog batch is being created.
- No work-item lifecycle status is changed; poller rows receive
  `status_detail` notes only.

## Acceptance Criteria

- `.gtkb-state/apply-bridge-contention-consolidation.py --dry-run` previews all
  proposed mutations.
- Live run mutates only `groundtruth.db`.
- Read-back evidence proves the three sub-projects, all nine memberships, and
  all three poller notes.
- The helper is idempotent on a second dry run.

## Pre-Filing Preflight Subsection

Candidate revision preflights must pass before filing this `REVISED` line:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-contention-consolidation --content-file .tmp/gtkb-bridge-contention-consolidation-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-contention-consolidation --content-file .tmp/gtkb-bridge-contention-consolidation-003.md
```

## Risk And Rollback

Risk: additive memberships can double-count the same WI in rollups. Mitigation:
the proposal keeps home memberships intact and frames the new projects as a
consolidated view, not a second backlog authority.

Rollback: append a new project/membership version marking the three
consolidation sub-projects retired/inactive; no destructive delete is required.
