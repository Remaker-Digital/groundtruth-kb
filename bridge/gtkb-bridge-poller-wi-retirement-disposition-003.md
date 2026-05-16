REVISED

# Implementation Proposal - Retirement Disposition for Bridge Poller WIs + Claude Axis-2 Thread WI

bridge_kind: implementation_proposal
Document: gtkb-bridge-poller-wi-retirement-disposition
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-POLLER-001

target_paths: ["groundtruth.db"]

This REVISED proposal dispositions 4 work items that no longer warrant implementation: 3 bridge-poller-* WIs (poller retired 2026-05-09 per Slice 4) and WI-3256 (Claude axis-2 thread automation; superseded and withdrawn — see the corrected disposition below).

## Revision Notes

This `-003` revision addresses both findings in the `-002` NO-GO verdict:

- **F1 (P1 — WI-3256 disposition rationale contradicts live bridge evidence):**
  Resolved. The WI-3256 disposition no longer claims an "indefinite owner
  deferral" and no longer requests `wont_fix`. IP-2 below now sets WI-3256 to
  `resolution_status='superseded'` and the `change_reason` cites the live
  `WITHDRAWN` supersession notice
  (`bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md`),
  the owner AUQ answer ("Pause; subsume into single-harness dispatcher"), and
  the verified successor dispatcher
  (`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md`, VERIFIED).
  The corrected rationale explicitly preserves the distinction between an
  obsolete mechanism, the covered single-harness use case, and the still-open
  multi-harness Axis-2 parity gap (IP-2 no longer erases that gap; it records
  it as residual future work, consistent with the WITHDRAWN notice §"Disposition").
- **F2 (P2 — proposal mutates four work items but carries one machine-readable
  Work Item header):** Resolved. The new `## Affected Work Item Inventory`
  section below enumerates all four affected work items with pre-state,
  proposed post-state, and `change_reason` summary. That inventory is treated
  as the implementation-authorization evidence for the full mutation set. The
  single-`Work Item:` metadata header is retained for `implementation_authorization.py`
  parsing of the umbrella WI; the inventory section makes the complete row set
  auditable and verifiable per the F2 recommended action ("add an explicit
  affected-work-item inventory that is treated as part of the implementation
  authorization evidence").

In addition, the three advisory specs the `-002` applicability preflight
flagged as missing (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`)
are now cited in `## Specification Links` below.

No `target_paths` change: the mutation set is still `groundtruth.db` only.

## Claim

Apply retirement / supersession dispositions to:
1. GTKB-BRIDGE-POLLER-001 - poller umbrella; superseded by cross-harness event-driven trigger.
2. GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR - trigger-conditional refactor no longer applicable.
3. GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT - smart-poller-specific gap; not applicable post-retirement.
4. WI-3256 - Claude-side axis-2 thread automation; superseded by the single-harness bridge dispatcher per the owner "pause; subsume" decision and the `WITHDRAWN` supersession notice. Multi-harness Axis-2 parity remains a separate open gap and is NOT closed by this disposition.

## In-Root Placement Evidence

Target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - backlog hygiene.
- `GOV-ARTIFACT-APPROVAL-001` - WI mutation evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; poller retirement supersedes these WIs.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the canonical dispatch substrate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project / work-item metadata so bridge proposals are machine-checkable; the Affected Work Item Inventory satisfies the full-mutation-set audit requirement raised in F2.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the affected WIs and their dispositions form the artifact graph for this cleanup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the poller retirement and the WITHDRAWN supersession trigger the lifecycle disposition of these four work items.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this disposition is captured as governed work with a bridge artifact and a spec-derived verification plan.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - poller retirement decision.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - Slice 4 retirement that superseded the 3 poller WIs.
- `DELIB-1893` - VERIFIED bridge thread for the smart-poller retirement slice (surfaced by Codex `-002` deliberation search; supports retiring the obsolete smart-poller direction).
- `DELIB-1517` - earlier NO-GO for Claude Code bridge-status thread automation (surfaced by Codex `-002` deliberation search; relevant to the WI-3256 history).

No prior deliberation directs WI-3256 to a `wont_fix` indefinite-deferral
disposition; the live evidence directs it to `superseded` (subsumed into the
single-harness dispatcher), which this revision adopts.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-BRIDGE-PROTOCOL-RELIABILITY authorization (`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH`); this proposal cleans the inventory of superseded WIs.
- Owner AUQ answer, 2026-05-09: "Pause; subsume into single-harness dispatcher" — recorded in `memory/pending-owner-decisions.md` and cited by the `WITHDRAWN` supersession notice `bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md`. This is the owner decision that directs the corrected WI-3256 disposition (`superseded`, not `wont_fix`).

## Requirement Sufficiency

Existing requirements sufficient. This proposal applies backlog-data
dispositions consistent with already-recorded owner decisions and the retired
poller / withdrawn-thread evidence. No new or revised requirement or
specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This is a 4-WI disposition cleanup, member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. It performs no batch resolve/promote/retire across the backlog; the inventory is a fixed, explicitly enumerated set of four work items (see `## Affected Work Item Inventory`). The applicable evidence pattern is a bounded per-WI disposition with formal-artifact-approval discipline preserved unchanged.

## Bridge INDEX Update Evidence

`-003` REVISED line prepended above the `-002` NO-GO line under the `Document: gtkb-bridge-poller-wi-retirement-disposition` block; prior `-001`/`-002` versions preserved unchanged per the append-only bridge audit trail.

## Affected Work Item Inventory

This proposal mutates exactly the following four `work_items` rows in
`groundtruth.db`. This inventory is the implementation-authorization evidence
for the full mutation set (F2). All four rows are within the cited project
authorization's included-work-item list per the `-002` Positive Confirmations.
The implementation report must verify each row's pre-state, post-state, and
`change_reason`.

| Work Item | Pre-state (resolution_status) | Proposed post-state | change_reason summary |
|---|---|---|---|
| `GTKB-BRIDGE-POLLER-001` | open / unresolved | `retired` | Smart poller retired 2026-05-09 (Slice 4); superseded by the cross-harness event-driven trigger. Cites `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` and this proposal. |
| `GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR` | open / unresolved | `retired` | Trigger-conditional poller refactor no longer applicable after smart-poller retirement. Cites `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` and this proposal. |
| `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` | open / unresolved | `retired` | Smart-poller-specific Prime-classification refinement; not applicable post-retirement. Cites `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` and this proposal. |
| `WI-3256` | open / unresolved | `superseded` | Claude-side Axis-2 thread automation subsumed into the single-harness bridge dispatcher per the owner "pause; subsume" decision (2026-05-09 AUQ). Cites the `WITHDRAWN` supersession notice `bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md` and the verified successor `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` (VERIFIED). The `change_reason` explicitly states that multi-harness Axis-2 parity remains an open gap not closed by this disposition. |

## Proposed Scope

### IP-1: Retire 3 poller WIs

Update each WI to `resolution_status='retired'` with `change_reason` citing
`DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` and this proposal
(`bridge/gtkb-bridge-poller-wi-retirement-disposition-003.md`):

- GTKB-BRIDGE-POLLER-001
- GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR
- GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT

### IP-2: Disposition WI-3256 (corrected per F1)

Update WI-3256 to `resolution_status='superseded'`. The `change_reason` MUST:

1. Cite the live `WITHDRAWN` supersession notice
   `bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md`.
2. Cite the owner AUQ decision of 2026-05-09: "Pause; subsume into
   single-harness dispatcher" (recorded in `memory/pending-owner-decisions.md`).
3. Cite the verified successor thread
   `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` (VERIFIED) —
   the single-harness use case is covered by that dispatcher.
4. State explicitly that this disposition closes the obsolete Claude-side
   Axis-2 thread-automation mechanism only; multi-harness Axis-2 parity remains
   an open gap and is NOT resolved by this disposition.

The `change_reason` MUST NOT claim an "indefinite owner deferral" and MUST NOT
use `wont_fix`. This corrects the `-001`/`-002` F1 contradiction with the live
bridge evidence.

If a residual multi-harness Axis-2 parity gap should be tracked as active work,
that is out of scope for this disposition proposal; a separate work item for
that gap may be created under normal backlog process. This proposal does not
delete or suppress any such tracking.

### IP-3: No spec changes

No spec promotions or new specs.

## Specification-Derived Verification Plan

| Linked specification / behavior | Verification |
|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — disposition is verified against observable MemBase state | Each of the four rows below is read post-mutation and compared to the Affected Work Item Inventory. |
| 3 poller WIs marked retired (`GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) | `db.get_work_item('GTKB-BRIDGE-POLLER-001').resolution_status == 'retired'` (and the two sibling rows). |
| WI-3256 marked superseded, not wont_fix (`GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) | `db.get_work_item('WI-3256').resolution_status == 'superseded'`. |
| Each change_reason cites superseding evidence (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-ARTIFACT-APPROVAL-001`) | Per-WI `change_reason` references this proposal and the superseding DELIB / WITHDRAWN notice as enumerated in the Affected Work Item Inventory. |
| WI-3256 change_reason does not claim indefinite deferral and does not erase the multi-harness gap (`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) | WI-3256 `change_reason` text contains the `WITHDRAWN`-notice citation and an explicit residual-gap statement; it contains neither `wont_fix` nor "defer indefinitely". |
| No code regressions | Not applicable; no code mutations. `target_paths` is `groundtruth.db` only. |

This is a backlog-data triage proposal; verification is observable MemBase
state inspection rather than automated pytest. The verification commands above
are the spec-derived checks mapping each linked specification to an observable
post-state assertion.

## Acceptance Criteria

- IP-1 and IP-2 dispositions applied exactly as the Affected Work Item Inventory specifies.
- The three poller WIs read `resolution_status='retired'`.
- WI-3256 reads `resolution_status='superseded'` (NOT `wont_fix`).
- Per-WI `change_reason` cites this proposal plus the superseding DELIB / WITHDRAWN notice.
- The WI-3256 `change_reason` cites the WITHDRAWN supersession notice and the verified successor dispatcher, and contains an explicit residual multi-harness Axis-2 gap statement.
- Both preflights PASS on the `-003` operative file.

## Risks / Rollback

- Risk: an unrecorded owner intent may exist for one of the poller WIs that has not been surfaced. Mitigation: Deliberation Archive searches were run for poller-specific decisions (see Prior Deliberations); no contradicting decision surfaced.
- Risk (addressed by F1): encoding the wrong owner decision for WI-3256. Mitigation: the corrected `superseded` disposition cites the live `WITHDRAWN` notice and the verified successor dispatcher, and explicitly preserves the multi-harness Axis-2 residual gap.
- Rollback: revert each WI's `resolution_status` and restore the prior `change_reason` for all four rows.

## Recommended Commit Type

`chore` - backlog data hygiene. No code change.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` operative file
after filing the INDEX entry. Outputs are embedded in the `## Applicability
Preflight` and `## Clause Applicability` sections below.

## Applicability Preflight

```text
- packet_hash: `sha256:fda16568aab46b3cdb0fe10101281851035007e190b7a63f461202cf5fc6240b`
- bridge_document_name: `gtkb-bridge-poller-wi-retirement-disposition`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-wi-retirement-disposition-003.md`
- operative_file: `bridge/gtkb-bridge-poller-wi-retirement-disposition-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:superseded, content:verified, content:retired |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |
```

## Clause Applicability

```text
- Bridge id: `gtkb-bridge-poller-wi-retirement-disposition`
- Operative file: `bridge\gtkb-bridge-poller-wi-retirement-disposition-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | must_apply | yes | blocking | blocking |

Exit 0 = pass.
```

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
