REVISED

# Implementation Proposal - Retirement Disposition for Bridge Poller WIs + Claude Axis-2 Thread WI

bridge_kind: implementation_proposal
Document: gtkb-bridge-poller-wi-retirement-disposition
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-POLLER-001

target_paths: ["groundtruth.db"]

This REVISED proposal dispositions 4 work items that no longer warrant implementation: 3 bridge-poller-* WIs (poller retired 2026-05-09 per Slice 4) and WI-3256 (Claude axis-2 thread automation; superseded and withdrawn). The WI-3256 disposition is corrected in `-005` to use a mechanically-terminal `resolution_status` so the closure actually removes the row from the active backlog.

## Revision Notes

This `-005` revision addresses the single finding in the `-004` NO-GO verdict. The `-002` round-1 findings (F1 unsupported `wont_fix` rationale, F2 single `Work Item:` header for a four-WI mutation) were resolved in `-003` and are carried forward unchanged. The `-004` finding and its resolution:

- **`-004` F1 (P1 — `resolution_status='superseded'` would not close WI-3256 in the live backlog):**
  Resolved. Codex verified that the live MemBase code defines terminal
  work-item statuses as exactly `verified`, `resolved`, `retired`, `wont_fix`,
  `not_a_defect` (`groundtruth-kb/src/groundtruth_kb/db.py:99-105`,
  `WORK_ITEM_TERMINAL_RESOLUTION_STATUSES`), and that `get_open_work_items()`
  returns every current work item whose `resolution_status` is NOT in that
  tuple (`groundtruth-kb/src/groundtruth_kb/db.py:3594-3607`). `superseded` is
  not in that tuple, so the `-003`/`-004` proposed post-state would have left
  WI-3256 in the active backlog.

  `-005` adopts Codex's recommended Option 1 (the narrowest fix; no scope
  expansion). WI-3256's proposed post-state is changed from
  `resolution_status='superseded'` to the terminal live status
  `resolution_status='resolved'` with `stage='resolved'`. The supersession
  fact is preserved without relying on a non-terminal status:
  - `superseded_by` is set to the verified successor thread
    `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` (the schema
    has a `superseded_by` field — `groundtruth-kb/src/groundtruth_kb/db.py:94`).
  - `status_detail` records `superseded/subsumed into single-harness dispatcher`.
  - `change_reason` records the full supersession evidence (the `WITHDRAWN`
    notice, the owner AUQ decision, the verified successor) and the explicit
    residual multi-harness Axis-2 gap statement.
  Because `resolved` IS in `WORK_ITEM_TERMINAL_RESOLUTION_STATUSES`, the
  closure is mechanically terminal: `get_open_work_items()` will exclude
  WI-3256 after the mutation. `-005` does NOT take Codex's Option 2 (adding
  `superseded` as a first-class terminal `resolution_status`): that would
  require broadening `target_paths` into MemBase code and tests, which is a
  larger scope this single disposition proposal deliberately avoids.

  The `-003` corrected evidence is preserved: no `wont_fix`, no
  indefinite-deferral claim, and an explicit statement that multi-harness
  Axis-2 parity remains a separate open gap.

The `-005` change is confined to the WI-3256 row's proposed post-state
(`resolution_status`, `stage`, `superseded_by`, `status_detail`). The three
poller WIs are unchanged (`retired`, already terminal). No `target_paths`
change: the mutation set is still `groundtruth.db` only.

## Claim

Apply retirement / resolution dispositions to:
1. GTKB-BRIDGE-POLLER-001 - poller umbrella; superseded by cross-harness event-driven trigger.
2. GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR - trigger-conditional refactor no longer applicable.
3. GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT - smart-poller-specific gap; not applicable post-retirement.
4. WI-3256 - Claude-side axis-2 thread automation; subsumed by the single-harness bridge dispatcher per the owner "pause; subsume" decision and the `WITHDRAWN` supersession notice. Closed with the terminal status `resolved` (`stage='resolved'`), with the supersession recorded in `superseded_by` / `status_detail` / `change_reason`. Multi-harness Axis-2 parity remains a separate open gap and is NOT closed by this disposition.

## In-Root Placement Evidence

Target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - backlog hygiene; a terminal `resolution_status` is required for `get_open_work_items()` to exclude the disposed rows.
- `GOV-ARTIFACT-APPROVAL-001` - WI mutation evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; poller retirement supersedes these WIs.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the canonical dispatch substrate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project / work-item metadata so bridge proposals are machine-checkable; the Affected Work Item Inventory satisfies the full-mutation-set audit requirement raised in `-002` F2.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the affected WIs and their dispositions form the artifact graph for this cleanup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the poller retirement and the WITHDRAWN supersession trigger the lifecycle disposition of these four work items.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this disposition is captured as governed work with a bridge artifact and a spec-derived verification plan.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - poller retirement decision.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - Slice 4 retirement that superseded the 3 poller WIs.
- `DELIB-1893` - VERIFIED bridge thread for the smart-poller retirement slice (surfaced by Codex `-002` and `-004` deliberation searches; supports retiring the obsolete smart-poller direction).
- `DELIB-1517` - earlier NO-GO for Claude Code bridge-status thread automation (surfaced by Codex `-002` deliberation search; relevant to the WI-3256 history).
- `DELIB-1544` / `DELIB-1549` / `DELIB-1550` - bridge-poller retirement reviews surfaced by the Codex `-004` deliberation search; no contrary owner decision blocking the corrected disposition.
- `DELIB-1497` / `DELIB-1566` - event-driven replacement / trigger verification context surfaced by the Codex `-004` deliberation search.

No prior deliberation directs WI-3256 to a `wont_fix` indefinite-deferral
disposition; the live evidence directs it to a `resolved` (subsumed)
disposition, which this revision adopts with the supersession recorded in
`superseded_by` / `status_detail` / `change_reason`.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-BRIDGE-PROTOCOL-RELIABILITY authorization (`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH`); this proposal cleans the inventory of superseded WIs.
- Owner AUQ answer, 2026-05-09: "Pause; subsume into single-harness dispatcher" — recorded in `memory/pending-owner-decisions.md` and cited by the `WITHDRAWN` supersession notice `bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md`. This is the owner decision that directs the corrected WI-3256 disposition (closed as `resolved`/subsumed, not `wont_fix`).

## Requirement Sufficiency

Existing requirements sufficient. This proposal applies backlog-data
dispositions consistent with already-recorded owner decisions and the retired
poller / withdrawn-thread evidence. No new or revised requirement or
specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This is a 4-WI disposition cleanup, member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. It performs no batch resolve/promote/retire across the backlog; the inventory is a fixed, explicitly enumerated set of four work items (see `## Affected Work Item Inventory`). The applicable evidence pattern is a bounded per-WI disposition with formal-artifact-approval discipline preserved unchanged.

## Bridge INDEX Update Evidence

`-005` REVISED line prepended above the `-004` NO-GO line under the `Document: gtkb-bridge-poller-wi-retirement-disposition` block in `bridge/INDEX.md`; prior `-001`/`-002`/`-003`/`-004` versions preserved unchanged per the append-only bridge audit trail. `bridge/INDEX.md` remains the canonical bridge workflow state.

## Affected Work Item Inventory

This proposal mutates exactly the following four `work_items` rows in
`groundtruth.db`. This inventory is the implementation-authorization evidence
for the full mutation set (`-002` F2). All four rows are within the cited
project authorization's included-work-item list per the `-002` Positive
Confirmations. The implementation report must verify each row's pre-state,
post-state, and `change_reason`.

| Work Item | Pre-state (resolution_status) | Proposed post-state | change_reason summary |
|---|---|---|---|
| `GTKB-BRIDGE-POLLER-001` | open / unresolved | `retired` | Smart poller retired 2026-05-09 (Slice 4); superseded by the cross-harness event-driven trigger. Cites `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` and this proposal. |
| `GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR` | open / unresolved | `retired` | Trigger-conditional poller refactor no longer applicable after smart-poller retirement. Cites `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` and this proposal. |
| `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` | open / unresolved | `retired` | Smart-poller-specific Prime-classification refinement; not applicable post-retirement. Cites `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` and this proposal. |
| `WI-3256` | open / unresolved | `resolved` (`stage='resolved'`); `superseded_by='bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md'`; `status_detail='superseded/subsumed into single-harness dispatcher'` | Claude-side Axis-2 thread automation subsumed into the single-harness bridge dispatcher per the owner "pause; subsume" decision (2026-05-09 AUQ). Cites the `WITHDRAWN` supersession notice `bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md` and the verified successor `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` (VERIFIED). The `change_reason` explicitly states that multi-harness Axis-2 parity remains an open gap not closed by this disposition. Closed with the terminal status `resolved` so `get_open_work_items()` excludes the row; `superseded`/`wont_fix` are deliberately not used. |

## Proposed Scope

### IP-1: Retire 3 poller WIs

Update each WI to `resolution_status='retired'` with `change_reason` citing
`DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` and this proposal
(`bridge/gtkb-bridge-poller-wi-retirement-disposition-005.md`):

- GTKB-BRIDGE-POLLER-001
- GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR
- GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT

`retired` is already in `WORK_ITEM_TERMINAL_RESOLUTION_STATUSES`, so these three closures are mechanically terminal and `get_open_work_items()` excludes them after the mutation.

### IP-2: Disposition WI-3256 (corrected per `-004` F1)

Update WI-3256 to the terminal live status `resolution_status='resolved'` with `stage='resolved'`. Record the supersession fact in dedicated fields rather than in a non-terminal status:

1. Set `superseded_by='bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md'` (the verified successor; the schema field `superseded_by` exists at `groundtruth-kb/src/groundtruth_kb/db.py:94`).
2. Set `status_detail='superseded/subsumed into single-harness dispatcher'`.
3. The `change_reason` MUST:
   a. Cite the live `WITHDRAWN` supersession notice `bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md`.
   b. Cite the owner AUQ decision of 2026-05-09: "Pause; subsume into single-harness dispatcher" (recorded in `memory/pending-owner-decisions.md`).
   c. Cite the verified successor thread `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md` (VERIFIED) — the single-harness use case is covered by that dispatcher.
   d. State explicitly that this disposition closes the obsolete Claude-side Axis-2 thread-automation mechanism only; multi-harness Axis-2 parity remains an open gap and is NOT resolved by this disposition.

The `change_reason` MUST NOT claim an "indefinite owner deferral" and MUST NOT
use `wont_fix`. The disposition uses the terminal status `resolved` (NOT the
non-terminal `superseded`) so `get_open_work_items()` excludes WI-3256 after the
mutation; this corrects the `-003`/`-004` F1 non-terminal-status defect.

If a residual multi-harness Axis-2 parity gap should be tracked as active work,
that is out of scope for this disposition proposal; a separate work item for
that gap may be created under normal backlog process. This proposal does not
delete or suppress any such tracking.

### IP-3: No spec changes, no MemBase code changes

No spec promotions or new specs. No change to `WORK_ITEM_TERMINAL_RESOLUTION_STATUSES` or any other MemBase code (Codex's Option 2 is deliberately not taken; `target_paths` stays `groundtruth.db` only).

## Specification-Derived Verification Plan

| Linked specification / behavior | Verification |
|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — disposition is verified against observable MemBase state | Each of the four rows below is read post-mutation and compared to the Affected Work Item Inventory. |
| 3 poller WIs marked retired and excluded from the active backlog (`GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) | `db.get_work_item('GTKB-BRIDGE-POLLER-001').resolution_status == 'retired'` (and the two sibling rows); none of the three appears in `db.get_open_work_items()`. |
| WI-3256 closed with a terminal status and excluded from the active backlog (`-004` F1; `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) | `db.get_work_item('WI-3256').resolution_status == 'resolved'` and `'WI-3256' not in {wi['id'] for wi in db.get_open_work_items()}`. This is the spec-derived check that the closure is mechanically terminal. |
| WI-3256 supersession recorded in dedicated fields, not a non-terminal status (`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) | `db.get_work_item('WI-3256').superseded_by` references `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md`; `status_detail` contains `superseded`. |
| Each change_reason cites superseding evidence (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-ARTIFACT-APPROVAL-001`) | Per-WI `change_reason` references this proposal and the superseding DELIB / WITHDRAWN notice as enumerated in the Affected Work Item Inventory. |
| WI-3256 change_reason does not claim indefinite deferral, does not use `wont_fix`, and does not erase the multi-harness gap (`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) | WI-3256 `change_reason` text contains the `WITHDRAWN`-notice citation and an explicit residual-gap statement; it contains neither `wont_fix` nor "defer indefinitely". |
| No code regressions | Not applicable; no code mutations. `target_paths` is `groundtruth.db` only; `WORK_ITEM_TERMINAL_RESOLUTION_STATUSES` is unchanged. |

This is a backlog-data triage proposal; verification is observable MemBase
state inspection rather than automated pytest. The verification commands above
are the spec-derived checks mapping each linked specification to an observable
post-state assertion. The `WI-3256 not in get_open_work_items()` check is the
direct spec-derived verification of the `-004` F1 fix.

## Acceptance Criteria

- IP-1 and IP-2 dispositions applied exactly as the Affected Work Item Inventory specifies.
- The three poller WIs read `resolution_status='retired'` and none appears in `get_open_work_items()`.
- WI-3256 reads `resolution_status='resolved'` with `stage='resolved'` (NOT `superseded`, NOT `wont_fix`), and `'WI-3256' not in get_open_work_items()`.
- WI-3256's `superseded_by` references the verified successor dispatcher thread and `status_detail` records the supersession.
- Per-WI `change_reason` cites this proposal plus the superseding DELIB / WITHDRAWN notice.
- The WI-3256 `change_reason` cites the WITHDRAWN supersession notice and the verified successor dispatcher, and contains an explicit residual multi-harness Axis-2 gap statement.
- Both preflights PASS on the `-005` operative file.

## Risks / Rollback

- Risk: an unrecorded owner intent may exist for one of the poller WIs that has not been surfaced. Mitigation: Deliberation Archive searches were run for poller-specific decisions (see Prior Deliberations); no contradicting decision surfaced.
- Risk (addressed by `-002` F1): encoding the wrong owner decision for WI-3256. Mitigation: the corrected disposition cites the live `WITHDRAWN` notice and the verified successor dispatcher, and explicitly preserves the multi-harness Axis-2 residual gap.
- Risk (addressed by `-004` F1): a non-terminal `resolution_status` would leave WI-3256 in the active backlog. Mitigation: `-005` uses the terminal status `resolved`; the verification plan asserts `'WI-3256' not in get_open_work_items()`.
- Rollback: revert each WI's `resolution_status` (and WI-3256's `stage`, `superseded_by`, `status_detail`) and restore the prior `change_reason` for all four rows.

## Recommended Commit Type

`chore` - backlog data hygiene. No code change.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-005` operative file
after filing the INDEX entry. Outputs are embedded in the `## Applicability
Preflight` and `## Clause Applicability` sections below.

## Applicability Preflight

- packet_hash: `sha256:79255a3d17d98ba60e137d9707e5f2c645db19679ae861e4e212dccddb346df1`
- bridge_document_name: `gtkb-bridge-poller-wi-retirement-disposition`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-wi-retirement-disposition-005.md`
- operative_file: `bridge/gtkb-bridge-poller-wi-retirement-disposition-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-poller-wi-retirement-disposition`
- Operative file: `bridge\gtkb-bridge-poller-wi-retirement-disposition-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Clause preflight exit code: 0 (pass; zero blocking gaps).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
