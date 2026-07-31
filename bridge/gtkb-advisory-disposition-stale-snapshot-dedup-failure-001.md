NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; delegated read-only evidence audit; dispatcher deliberately disabled
author_metadata_source: x-codex-turn-metadata

bridge_kind: governance_review
Document: gtkb-advisory-disposition-stale-snapshot-dedup-failure
Version: 001
Date: 2026-07-30 UTC
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Related Work Items: WI-5784, WI-5795
Work Item Candidate: not yet created
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Report — Advisory Disposition Can Create Duplicate Work Items From A Stale Observation

## Summary

The reviewed work-intent release-lock Advisory was already consolidated into
WI-5784 before a later Loyal Opposition/Claude disposition created WI-5795 for
the same work. This is an observed stale/concurrent disposition failure, not a
source-only race hypothesis. The advisory workflow requires a duplicate search,
but no commit-time currentness check prevented a delayed worker from appending
a second active project member after the canonical carrier changed.

## Claim

Advisory disposition lacks an atomic boundary that observes current carriers,
chooses or creates one, and commits only if that observation remains current.
Procedural duplicate searching alone cannot prevent duplicate work items under
concurrent or delayed workers.

## Exact Evidence

1. `bridge/gtkb-advisory-work-intent-release-db-lock-concurrency-001.md`
   records the release-lock incident; independent GO is version 002.
2. WI-5784 v2, MemBase row 11646 at `2026-07-30T13:02:06Z`, expanded the
   existing acquire-lock carrier to cover both acquire and release. Its change
   reason explicitly routes the reviewed release Advisory into the existing
   nonduplicate carrier.
3. WI-5784 v4, row 11665 at `2026-07-30T14:01:35Z`, completed the
   consolidation and cites release source/GO receipt rows 387/391 and acquire
   recurrence rows 422/423.
4. WI-5795 v1 was nevertheless appended at row 11675 at
   `2026-07-30T15:15:11Z`, 73 minutes 36 seconds after row 11665.
   `changed_by=loyal-opposition/claude`; its description calls itself a
   companion to WI-5784 and owns the release half already included in
   WI-5784's acquire-and-release contract.
5. Both rows remain open active members of
   `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729`.
6. `.claude/skills/gtkb-advisory-disposition/SKILL.md` requires duplicate work
   to route to no-op or an update of the existing artifact, not a second record,
   and requires searching backlog/spec/bridge records before disposition.
7. GOV-15 correctly blocked Prime Builder's attempted automatic resolution of
   WI-5795 because no exact owner terminal-resolution approval exists. Current
   WI-5784 v6, row 11690, corrects the transient success wording and leaves
   WI-5795 open.
8. The transient reconciliation itself demonstrates a second ordering hazard:
   WI-5784 v5 row 11689 stated that WI-5795 was resolved even though the target
   transition failed. WI-5784 v6 superseded that false statement 13 seconds
   later. Terminal-success wording must not be appended before the target
   transition succeeds.
9. `scripts/hygiene/advisory_candidate_promote.py` validates staged candidate
   state before allocating and inserting a work item, but no final live carrier
   check is performed inside the insertion boundary. This is not evidence that
   the service created WI-5795; it demonstrates that the same stale-observation
   class is not mechanically excluded from the promotion path.

## Impact

- Two active project members can invite two proposals and concurrent
  implementations for one defect.
- Project counts, priorities, dependency closure, and authorization exposure
  become inflated or ambiguous.
- Cleanup consumes owner attention because GOV-15 correctly prevents silent
  termination of a duplicate defect row.
- Append-only MemBase permanently retains the duplicate and transient false
  reconciliation statement, increasing SoT size and future read cost.
- Append-only storage prevents overwrite loss but does not by itself provide
  semantic uniqueness under stale workers.

## Duplicate Search And Corrective Carrier

No existing item exactly owns commit-time semantic deduplication of advisory
disposition:

- WI-5757 owns slug-plus-version router intake and starvation visibility.
- WI-5796 owns concurrent append safety for the candidate JSONL store.
- WI-5675 owns concurrent WI-ID allocation and broader MemBase contention.
- WI-4573 and WI-3274 concern duplicate bridge proposals, not duplicate
  MemBase advisory carriers.

Recommended route after independent review: create one active child under
`PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729` for live-deduplicated,
idempotent advisory disposition at MemBase insertion. Link, but do not broaden,
WI-5757, WI-5796, and WI-5675.

## Recommended Acceptance Contract

1. Manual, skill, router, and batch paths use one governed disposition service;
   direct work-item insertion cannot bypass its final duplicate check.
2. The service records a first-class advisory-source identity and canonical
   carrier relation. A broader carrier such as WI-5784 is recognized as already
   dispositioned through exact source linkage.
3. The final duplicate check and conditional insert occur in one short
   transaction or generation-bound lease.
4. A stale observation returns `already_dispositioned` with the canonical WI
   and appends no new work item.
5. Two concurrent workers disposing the same Advisory produce exactly one work
   item and receive the same canonical-carrier receipt.
6. A deterministic test reproduces this incident: worker A observes no carrier;
   worker B updates WI-5784; worker A resumes; create is rejected as stale and
   returns WI-5784.
7. The receipt preserves observation revision, advisory identity, candidates
   considered, selected carrier, outcome, and elapsed time.
8. Candidate-store promotion and MemBase insertion are crash-idempotent.
9. Duplicate detection does not auto-resolve an existing defect. It emits one
   owner-disposition question and GOV-15 remains fail closed.
10. Append-only history is preserved; owner-approved cleanup appends a terminal
    successor naming WI-5784 as canonical rather than deleting either row.
11. No dispatcher or TAFE activation or mutation is introduced.

## Immediate Disposition

WI-5784 remains the intended canonical implementation carrier. WI-5795 stays
open until the owner explicitly approves one terminal disposition, such as
resolution as a duplicate/superseded record into WI-5784. Project PAUTH does
not substitute for GOV-15 terminal-resolution approval.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Requirement Sufficiency

**Existing requirements sufficient.** This report adds operational evidence and
a corrective acceptance outline to the existing deterministic, append-only,
project-authorized artifact lifecycle. No new GOV, ADR, or DCL is required
before the finding can be dispositioned into a project-member work item.

## Specification-Derived Verification Outline

| Requirement | Future behavioral evidence | Required result |
| --- | --- | --- |
| Live duplicate exclusion | Two workers dispose the same source with one delayed after observation | Exactly one WI; both receipts return the same canonical carrier. |
| Broader-carrier recognition | Link the source Advisory to a pre-existing multi-finding carrier | No second WI; result identifies the existing carrier. |
| Crash idempotence | Interrupt between candidate promotion and MemBase acknowledgement, then retry | Retry appends no duplicate and returns the same disposition receipt. |
| GOV-15 preservation | Detect an already-created duplicate without owner terminal approval | Duplicate stays open and one owner-decision packet is emitted. |
| Append-only integrity | Audit all disposition and correction rows | No history rewrite; currentness and supersession remain queryable. |

## Prior Deliberations

- `DELIB-202667531` authorizes advisory stress-observation capture and governed
  processing without granting implementation.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` establishes
  project-only implementation authority; it does not waive GOV-15 resolution.
- The release and acquire Advisory v001/v002 chains are the reviewed source
  evidence consolidated into WI-5784.

## Non-Approval

This Advisory Report preserves an observed concurrency defect and recommends a
future artifact route. It is not implementation approval, a bridge GO, a work-
item resolution, an implementation-start packet, or authority to resolve
WI-5795.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
