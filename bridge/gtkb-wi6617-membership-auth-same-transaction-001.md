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
Document: gtkb-wi6617-membership-auth-same-transaction
Version: 001
Date: 2026-08-17 UTC

Project: PROJECT-GTKB-AUTHORIZATION-MODEL-CORRECTION
Project Authorization: none
Owner Decision: DELIB-20260816201237
Work Item: WI-6617 v1
Related Work Items: WI-6618, WI-6619, WI-6453, WI-6540, WI-6557
Blocks: WI-6618 MUST NOT start until this work-product commit exists

target_paths: []
target_specifications: ["GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001", "ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001", "DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
repository_metadata_mutation_in_scope: false

# NEW — Exact P0: membership mutation is the authorization transaction (WI-6617)

## Decision Requested

Approve this exact slice. This message performs no source, test, Git, packet,
or specification mutation. A later separately selected Prime Builder may
implement only after independent GO, and only against paths that are not
foreign-dirty at implementation time.

This session does not implement a GO item. After this file is written, this
session's involvement in WI-6617 is over except that WI-6618 is filed next
as a blocked sibling that MUST NOT land first.

## Sequencing (owner, this turn)

WI-6617 MUST land before WI-6618. Collapsing the population while the writer
can still mint per-item or surplus current rows would let the drift reappear.
DCL C1/C2 stay report-only until the WI-6618 supersession pass.

## Fresh Authority Reads

- Owner decision `DELIB-20260816201237` (outcome `owner_decision`): model
  first; membership mutation and re-authorization are the same transaction;
  exactly one current authorization per project; envelope does not enumerate
  work-item IDs; supersede per-item PAUTHs into one per project (that last
  clause is WI-6618, not this slice).
- `ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001` v1 `active`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 `active` (supersedes v2).
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 `active` — this slice
  implements C2 (creation reject), C3 (transaction atomicity), and C4
  (envelope purity). C1/C2 fail-closed waits for WI-6618.
- Work item WI-6617 v1, P0. Active member of
  `PROJECT-GTKB-AUTHORIZATION-MODEL-CORRECTION`. That project has **zero**
  current project-authorization rows (bootstrap). It is not a member of
  `PAUTH-GET-HEALTHY-PHASE-3-20260815` v35 (522-id include list). Under GOV
  v3 that include list is not coverage authority. Do not add these WIs to
  PHASE 3 membership (that would be a membership event on an already
  authorized project and would require a new current PHASE 3 version).
- Git HEAD `bf084f171`. This session holds no work-intent claim.
- Dirty (do not combine): `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`,
  `platform_tests/scripts/test_project_authorization.py`,
  `scripts/implementation_authorization.py`. Live NEW WI-6453 already
  claims `db.py` for a same-id `status=superseded` lock. This slice is
  targetless so it does not pile onto those files.

## Measured HEAD Behavior To Lock

- `ProjectLifecycleService.add_project_item` (lifecycle.py:297) and
  `remove_project_item` (lifecycle.py:736) call only
  `link_project_work_item`. Zero references to authorization. C3 violation
  shape is the current production path.
- `authorize_project` still accepts `included_work_item_ids` /
  `excluded_work_item_ids` and writes them (C4).
- `amend_authorization` (lifecycle.py:1104) is an include-list delta writer
  (WI-6505). GOV v3: amendment is not an authorization path.
- `insert_project_authorization` does not reject a PAUTH id or scope that
  names a single work item (C2).

## Exact Disposition Postimage

After independent GO, a later Prime Builder may do only this slice:

1. **C3.** `add_project_item` / `remove_project_item` (and any other
   membership writer) MUST, in the **same SQLite transaction** as the
   membership append:
   - if the project **joined** already has a current authorization, append
     a new current authorization version for that project;
   - if the project **left** already has a current authorization, append a
     new current authorization version for that project;
   - if that append cannot be performed, the membership mutation MUST fail
     and roll back.
   A project with **no** current authorization (this bootstrap project) MUST
   NOT mint an authorization as a side effect of membership-only change.
2. **C2 creation reject.** `insert_project_authorization` / `authorize_project`
   MUST reject before insert when the authorization id or declared scope
   resolves to an individual work item (including `PAUTH-WI-*` identity
   shapes). Do not activate such a row.
3. **C4.** Reject at creation any envelope that enumerates included or
   excluded work-item IDs (non-empty lists fail closed). Operation-time
   coverage MUST read **current project membership**, not those columns.
   Stop writing the lists from `authorize_project`. CLI `--include-work-item`
   is out of this slice while `cli.py` is dirty; the store/lifecycle reject
   is sufficient to fail closed.
4. **Retire `amend_authorization` as an authorization path.** The callable
   MUST fail closed with a reason that scope change requires a new current
   version under direct owner approval of the complete proposed envelope.
   Do not use include-list deltas. Do not delete historical rows.
5. **C1/C2 fail-closed is out of this slice.** Audit-time reporting MAY be
   added; fail-closed on the pre-cutover 938-row population is WI-6618.
6. Tests in a **new** module (do not edit dirty
   `test_project_authorization.py`):
   - add-item to an already-authorized project increments that project's
     current PAUTH version in the same transaction; a forced auth-append
     failure rolls back membership;
   - move from authorized A to authorized B appends both;
   - add-item to an unauthorized project does not create a PAUTH;
   - insert with `included_work_item_ids=['WI-1']` raises;
   - insert with id `PAUTH-WI-3396-...` raises;
   - `amend_authorization` raises and leaves version unchanged.
7. Do not run the 585-row supersession (WI-6618). Do not purge "program"
   language (WI-6619). Do not edit projections. Do not implement this GO
   in the reviewing session.

## Requirement Sufficiency

`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3, the ADR, and the DCL
already record the required behavior. No new specification is created.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 `active` — event
  transaction; envelope MUST NOT enumerate work-item IDs; amendment is not
  an authorization path.
- `ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001` v1 `active` — applied as a
  functional test. Violation is FAIL.
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 `active` — C2, C3, C4.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` v2 — intrinsic envelope; work-item
  ID lists are no longer coverage fields under GOV v3 C4.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v5 — this carrier is ephemeral.
- `GOV-10` v2.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v2.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v6.

All current ADR heads are independent tests of this disposition. Violation of
an applicable ADR or specification is FAIL.

## Spec-Derived Verification Plan (spec-to-test mapping)

```text
python -m pytest platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py -q --tb=short
```

The implementer may name a different new test module. This review does not
add tests.

Loyal Opposition must confirm HEAD `add_project_item` / `remove_project_item`
still contain no authorization writer, and that this slice does not collapse
the 938-row population.

## Independent Review Plan

Re-read WI-6617 v1, DCL C2–C4, GOV v3 Authorization As An Event, and HEAD
lifecycle membership methods. Return GO only for the writer-transaction
postimage. GO is not implementation in the reviewing session.

## Subsequent Implementation Boundary

After independent GO, another Prime Builder may edit then-clean lifecycle /
db / evaluator / new-test paths. No bridge message enters a work-product
commit. The commit metadata MUST name `(WI-6617)` before any WI-6618
implementation starts.

## Filing-Tool Defects

Filed as `bridge/gtkb-wi6617-membership-auth-same-transaction-001.md`.

1. Marker-first header written without `normalize_bridge_envelope_head`
   (WI-6538 / WI-6541 / WI-5814).
2. Applicability preflight may deny this file for missing PHASE 3 include-list
   coverage. That evaluator consults `included_work_item_ids` (DCL C4
   violation shape). Bypass recorded against WI-6617 / GOV v3 C4 /
   WI-5814 / WI-6541. Independent LO review is not bypassed.
3. Legacy TAFE/dispatcher commands were not used.
4. Direct Write of this numbered file is the contention WI-6564 / WI-6384
   name.

## Prior Deliberations

- `DELIB-20260816201237` — owner model, sequencing, supersede-not-delete.
- WI-6617 v1 is step 4 of the accepted corrective sequence.
- WI-6453 (this session, live NEW) locks same-id version supersession in
  `db.py`; it is not C3 and MUST NOT absorb this slice.
- WI-6540 (live NEW) is include-list amend behavior; C4 retires that field
  as coverage. Do not combine.

## Owner Action Required

None.

## Files Expected To Change

None in this session.

## Recommended Commit Type

None.

## Risk / Rollback

Risk is starting WI-6618's data collapse first, or editing dirty
`lifecycle.py` while foreign hunks are present. This filing forbids both.
Rollback is deletion of this ephemeral message.

---
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
