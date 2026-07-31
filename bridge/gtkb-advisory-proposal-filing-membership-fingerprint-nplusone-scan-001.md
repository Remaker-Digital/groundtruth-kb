NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; delegated read-only proposal-filing audit; dispatcher deliberately disabled
author_metadata_source: x-codex-turn-metadata

bridge_kind: governance_review
Document: gtkb-advisory-proposal-filing-membership-fingerprint-nplusone-scan
Version: 001
Date: 2026-07-30 UTC
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Related Work Items: WI-5458, WI-5725, WI-5790, WI-5792, WI-5798
Work Item Candidate: not yet created
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Advisory Report — Proposal Filing Emits Null Membership Invalidation Evidence Through A Mixed-Snapshot N+1 Scan

## Summary

Read-only boundary tracing for the WI-5790 implementation proposal found two
coupled defects in the staged proposal-filing implementation.

First, `_active_memberships_for_work_item` receives membership rows whose
canonical fields are aliased as `membership_id`, `membership_version`, and
`membership_status`, but `_resolve_project_state` reads `id`, `version`, and
`status`. The resulting authorization decision records all three membership
invalidation inputs as null despite relying on an active membership.

Second, the helper finds one work item's memberships by enumerating all 472
current projects and calling `list_project_work_items` once per project. One
project-state resolution therefore executes 473 SQL statements. Normal proposal
filing resolves state before preflight and again afterward, producing two full
scans. Those statements do not share one declared read transaction, so a
concurrent append-only membership transition can yield a membership set that
never existed in any single database snapshot.

One direct canonical-view query fixes both problems without introducing a
cache, mutable projection, or alternate source of truth.

## Classification

- Category: authority-evidence correctness, concurrency/currentness, and
  append-only SoT access latency.
- Severity: high for operation-time evidence; high operational cost at current
  scale.
- Affected surface:
  `groundtruth_kb.bridge.proposal_filing._active_memberships_for_work_item`.
- Observed while preparing the WI-5790 proposal; WI-5790's implementation-start
  single-flight scope is not broadened by this report.

## Exact Code And State Evidence

1. Current staged source postimage:
   `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`, SHA-256
   `0F833B14091A869883587B1C4E010C36823841E22441154FB385F2DD8FE4F45A`,
   Git blob `017b0e8816680380aa914e5d7135fb81f81a7d1a`.
2. `proposal_filing.py:149-156` loops over
   `db.list_projects(include_terminal=True)` and calls
   `db.list_project_work_items(project_id)` for every project.
3. `groundtruth-kb/src/groundtruth_kb/db.py:5486-5493` defines the returned
   fields as `membership_id`, `membership_version`, and `membership_status`.
4. `proposal_filing.py:770-772` instead reads `membership.get("id")`,
   `membership.get("version")`, and `membership.get("status")`.
5. Current canonical WI-5790 membership:
   `PWM-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI-5790` version 1,
   status `active`, project `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729`.
6. Replaying the exact returned-row shape against those consumer lookups
   produced null membership id, version, and status. Reading the documented
   aliases produced the exact values above.
7. `proposal_filing.py:1344-1350` performs the initial project-state
   resolution; `:1357-1366` repeats it for post-preflight invalidation
   comparison. At 472 projects this is two sets of one project-enumeration query
   plus 472 membership queries.
8. The current WI-5790 investigation measured 16.673 seconds warm in-process
   for this membership-resolution path. An independent exact-query-shape replay
   executed 473 statements in 8.650 seconds.
9. A direct indexed canonical-view lookup against
   `current_project_work_item_memberships`, filtered by work item and active
   status, returned the exact row in five samples ranging from 0.00305 to
   0.00776 seconds. `idx_project_memberships_work_item` already exists.
10. `groundtruth-kb/src/groundtruth_kb/cli_backlog_authorize_implementation.py:
    84-93` already demonstrates the direct canonical-view query pattern.
11. Current staged test postimage:
    `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`, SHA-256
    `3B1ED9F7A85E7209E26355C6B0A81F7B2A8E182CFA4EDED4B643AD8ADBA8BCCA`,
    Git blob `4871bcd661c1a8a049c4f8d9ad24a6ad005fb010`. Its decision-evidence test
    asserts bridge status/version but not any membership invalidation field.

## Concurrency Failure

The scan is not merely slow. Each per-project SELECT may observe a different
SQLite read snapshot. For an atomic append-only transition from active
membership A to active membership B, scanning A before the commit and B after
can return both memberships; scanning B before the commit and A after can
return neither. Either result can be impossible in every committed database
generation, causing a false multiple-membership denial, a false orphan result,
or an authorization decision assembled from mutually inconsistent evidence.

A single targeted SELECT gives each resolution one coherent statement snapshot.
The existing deliberate second resolution then provides the correct
before/after invalidation boundary.

## Authority And Audit Impact

- Decision evidence claims to bind membership invalidation inputs while
  serializing them as null.
- An active-to-active membership version change can be omitted from the stated
  fingerprint even though operation-time enforcement says every project
  membership change invalidates prior evidence.
- A selected project-membership-fallback authorization can coexist with
  evidence saying no membership identity, version, or status was bound.
- Long multi-statement scans enlarge the race window and increase lock/load
  pressure on the growing append-only MemBase.
- Normal proposal filing pays the scan twice, making this a recurring hot-path
  cost rather than a one-off diagnostic expense.

## Duplicate Search And Recommended Carrier

No existing artifact exactly owns this coupled correction. WI-5458 owns PAUTH
candidate selection but its latest v014 is NO-GO on a separate finalization
deadlock. WI-5725 owns scaffold-versus-filing selection parity. WI-5792 owns
cold imports and duplicate audits. WI-5798 owns one-observation semantics for
multi-row sweeps. WI-5790 remains the implementation-start single-flight
carrier and should not absorb a proposal-filing defect.

After independent review, create one child under
`PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729`, tentatively titled
`Make proposal-filing membership resolution single-query and bind the canonical membership fingerprint`.
Do not create separate correctness and latency work items; they would overlap
on the same helper, source, tests, and acceptance boundary.

## Recommended Correction

1. Replace `_active_memberships_for_work_item` with one parameterized query
   against `current_project_work_item_memberships`, filtered by work item and
   active status.
2. Return one documented membership representation and use it consistently.
3. Prefer a public `KnowledgeDB` query method if cross-surface reuse is
   intended; otherwise keep the bounded direct query local and test its exact
   contract.
4. Preserve deterministic ordering for the legitimate multiple-membership
   diagnostic.
5. Keep initial and post-preflight resolutions separate, but make each a
   coherent point lookup.
6. Bind exact membership id, version, status, project, and observation identity
   into the decision fingerprint.
7. Add phase/query-count telemetry sufficient to expose regressions without
   logging sensitive database contents.
8. Introduce no persistent cache, mutable shadow table, TAFE/dispatcher
   dependency, or raw base-table authority.

## Recommended Acceptance Contract

1. A seeded active membership produces exact non-null id, version, project, and
   status in `authorization_decision.invalidation_inputs`.
2. Appending a new active membership version during candidate preflight changes
   the fingerprint and denies publication.
3. Retiring or moving the membership during preflight also denies before bridge
   publication.
4. No active membership fails closed with no publication or side effects.
5. Two legitimate active memberships produce the existing deterministic
   disambiguation error.
6. A deterministic two-connection transition test observes either the complete
   pre-transition set or complete post-transition set, never a mixed set.
7. Query instrumentation proves one membership query per project-state
   resolution independent of total project count.
8. A scale fixture with at least 1,000 unrelated projects preserves constant
   query count and bounded warm latency.
9. Existing PAUTH ranking, expiry, exclusion, explicit-selector, bridge
   preimage, owner-decision, target-classification, and denial tests remain
   green.
10. Decision payload and generated proposal contain the same exact membership
    fingerprint.
11. The implementation uses the canonical current view and existing index;
    append-only history and auditability remain unchanged.
12. TAFE and dispatcher remain disabled and untouched.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Requirement Sufficiency

Existing requirements are sufficient. Operation-time enforcement explicitly
requires currentness evidence and invalidation on any project-membership
change. The freshness and deterministic-services rules supply the canonical
read and bounded-service requirements. This correction needs implementation
and regression coverage, not a new formal normative artifact.

## Specification-Derived Verification Outline

| Requirement | Future behavioral evidence | Required result |
| --- | --- | --- |
| Exact membership evidence | Dry-run with seeded active membership | Exact non-null id/version/status/project in decision and proposal. |
| Operation-time invalidation | Append membership successor during preflight | Typed stale-input denial; zero publication side effects. |
| Snapshot coherence | Concurrent atomic move between two projects | Result is wholly before or wholly after, never both/neither. |
| Constant query complexity | Repeat with 1, 472, and 1,000 unrelated projects | One membership statement per resolution; elapsed time remains bounded. |
| Existing authority behavior | Current focused PAUTH selection suite | Ranking, expiry, exclusions, explicit selection, and no-side-effect denials remain unchanged. |
| Canonical SoT use | Query trace and source inspection | Current membership view and existing index used; no cache or alternate authority. |

## Prior Deliberations

- `DELIB-202667697` requires governed Advisory Reports for concrete SoT
  access-latency and append-only growth-cost examples.
- `DELIB-202667531` prioritizes fix-class Advisory findings while retaining all
  normal proposal, review, claim, start, reporting, and verification gates.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` makes active
  parent-project membership load-bearing implementation-authority evidence.
- WI-5458 v013/v014 preserves the staged postimage and review state in which
  this defect was found.

## Non-Approval

This Advisory Report records a correctness, concurrency, and SoT-latency
finding. It does not authorize creating the proposed work item, changing its
parent project, implementation, protected mutation, PAUTH mutation, bridge GO,
claim, implementation start, Git action, TAFE/dispatcher action, release,
deployment, or external-system mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
