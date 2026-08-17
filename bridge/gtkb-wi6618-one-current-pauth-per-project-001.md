::init gtkb lo
::open spec
NEW

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 13570cbf-e2d1-408a-9c3d-be4ff5a582f4
author_model: grok-4.6
author_model_version: grok-4.6
author_model_configuration: Cursor IDE interactive; Prime Builder role fixed by owner `::init gtkb pb`

bridge_kind: implementation_proposal
Document: gtkb-wi6618-one-current-pauth-per-project
Version: 001
Date: 2026-08-17 UTC

Project: PROJECT-GTKB-AUTHORIZATION-MODEL-CORRECTION
Project Authorization: none
Owner Decision: DELIB-20260816201237
Work Item: WI-6618 v1
Related Work Items: WI-6617, WI-6619, WI-6557, WI-6453
Depends on: WI-6617 work-product commit MUST exist first

target_paths: []
target_specifications: ["GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001", "ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001", "DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
formal_artifact_mutation_in_scope: false
repository_metadata_mutation_in_scope: false

# NEW — Exact P0: one current authorization per project (WI-6618) — blocked on WI-6617

## Decision Requested

Approve this exact slice **as the successor to WI-6617 only**. This message
performs no source, test, Git, packet, MemBase, or specification mutation.
A later separately selected Prime Builder may implement only after
independent GO **and** after the WI-6617 work-product commit that names
`(WI-6617)` exists.

This session does not implement a GO item. After this file is written, this
session's involvement in WI-6618 is over.

## Hard sequencing (owner, this turn)

WI-6617 MUST land before WI-6618. If a session is selected to implement this
thread while `git log` does not contain a work-product commit identifying
WI-6617, it MUST refuse and leave this item untouched. Collapsing first
would let the still-open writer recreate per-item current rows.

## Fresh Authority Reads

- Owner decision `DELIB-20260816201237`: supersede the 585 per-item and
  surplus project authorizations into **one current authorization per
  project**; union of granted scope; prior records move to `superseded` and
  remain readable; MUST NOT delete formal authorization records.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 — cardinality; C1/C2
  fail closed only after this supersession pass.
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 — C1 (at most one
  current row per `project_id`); C2 (no WI-scoped authorization remains
  current). Until this pass, those checks **report** the pre-cutover
  population and do not fail closed.
- WI-6618 v1, P0. Active member of
  `PROJECT-GTKB-AUTHORIZATION-MODEL-CORRECTION` (zero current PAUTHs, by
  design). Not in PHASE 3 include list v35; that list is not coverage
  under GOV v3 C4.
- ADR measured population at drafting: 938 active authorization rows, 161
  projects, ~5.8 concurrent actives per project; 585 names an individual
  work item in the identifier (example
  `PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001`).
- Controlling writer proposal:
  `bridge/gtkb-wi6617-membership-auth-same-transaction-001.md` (NEW, this
  session). Do not start this collapse until that writer has a named
  work-product commit.
- Git HEAD `bf084f171`. This session holds no work-intent claim.
- WI-6557 sweep is read-only until this pass; fold backlog-triage
  retirements and membership corrections into this single re-authorization
  per project so they cost no extra auth events.
- Dirty lifecycle / authorization tests / implementation_authorization.py:
  do not combine. This filing is targetless.

## Measured HEAD Behavior To Lock

Multiple current `status=active` authorization rows share a `project_id`.
Identifiers of the form `PAUTH-WI-*` are current. `current_project_authorizations`
is `MAX(version)` **per authorization id**, not per project, so a project can
have many current ids at once. That is C1's violation shape.

## Exact Disposition Postimage

After independent GO **and** the WI-6617 commit, a later Prime Builder may
do only this slice:

1. For every project that currently has one or more active authorization
   rows, append **exactly one** new current authorization whose granted
   mutation classes, forbidden operations, spec includes/excludes, path
   bounds, and external-effect bounds are the **union** of what those live
   rows actually granted. Do not invent broader scope. Do not drop a
   granted operation or class that any live row allowed.
2. Every prior live row for that project MUST become `status=superseded`
   (append-only lifecycle marking; payload columns other than lifecycle
   remain historical). MUST NOT DELETE project-authorization records.
3. After the pass: at most one current, non-superseded, non-revoked
   authorization per `project_id`. No current row whose identity or scope
   designates an individual work item.
4. Work already performed under superseded records remains valid. The new
   per-project current row carries that grant forward.
5. Fold WI-6557 read-only sweep retirements/membership corrections into
   this same per-project re-authorization event. Do not run extra
   membership mutations that would each mint another current version after
   WI-6617 lands.
6. Verification MUST include a before-and-after census: active count falls
   to at most one per project; no project loses granted scope (union
   check); superseded count matches the retired surplus; C1 and C2 then
   **fail closed** on any remaining violation.
7. Tests in a new module on fixture databases plus a read-only census
   script for live MemBase. Do not overwrite live `groundtruth.db` except
   through the governed append-only writer in this pass.
8. Do not implement WI-6617 in this slice. Do not purge "program" language
   (WI-6619). Do not delete superseded/retired formal records.

## Requirement Sufficiency

GOV v3, the ADR, the DCL, and `DELIB-20260816201237` already record the
required behavior. No new specification is created.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 `active`.
- `ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001` v1 `active` — functional test.
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 `active` — C1, C2
  fail-closed after this pass.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v5 — this carrier is ephemeral.
- `GOV-10` v2.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v2.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v6.

All current ADR heads are independent tests of this disposition. Violation of
an applicable ADR or specification is FAIL.

## Spec-Derived Verification Plan (spec-to-test mapping)

```text
python -m pytest platform_tests/scripts/test_pauth_one_current_per_project.py -q --tb=short
```

Plus the before/after census named in postimage item 6. This review does
not add tests.

Loyal Opposition must confirm this proposal cannot be implemented before
the WI-6617 commit, and that the pass supersedes rather than deletes.

## Independent Review Plan

Re-read WI-6618 v1, DELIB-20260816201237 question 2, DCL C1/C2 enforcement
timing, and `bridge/gtkb-wi6617-membership-auth-same-transaction-001.md`.
Return GO only if the collapse is union-preserving, non-deleting, and
hard-blocked on WI-6617. GO is not implementation in the reviewing session.

## Subsequent Implementation Boundary

Implementers MUST refuse this item until `git log` shows a work-product
commit identifying WI-6617. Then they may append superseding PAUTH versions
on then-clean writers. No bridge message enters a work-product commit. The
collapse commit metadata MUST name `(WI-6618)` and MUST NOT include a
`VERIFIED` file.

## Filing-Tool Defects

Filed as `bridge/gtkb-wi6618-one-current-pauth-per-project-001.md` **after**
`bridge/gtkb-wi6617-membership-auth-same-transaction-001.md`.

1. Marker-first header written without `normalize_bridge_envelope_head`
   (WI-6538 / WI-6541 / WI-5814).
2. Include-list PAUTH coverage preflight is a C4 defect; bypass recorded
   against WI-6617 / GOV v3 C4 / WI-5814 / WI-6541. Independent LO review
   is not bypassed.
3. Legacy TAFE/dispatcher commands were not used.

## Prior Deliberations

- `DELIB-20260816201237` — owner chose supersede-into-one-per-project.
- WI-6618 v1 is step 5 of the accepted sequence; step 4 is WI-6617.
- WI-6557 remains read-only until this pass.

## Owner Action Required

None.

## Files Expected To Change

None in this session.

## Recommended Commit Type

None.

## Risk / Rollback

Risk is implementing this collapse while `add_project_item` still writes
membership without a PAUTH append. The hard WI-6617-commit gate is the
mitigation. Rollback is deletion of this ephemeral message.

---
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
