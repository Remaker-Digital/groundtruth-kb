GO
::init gtkb lo
::open spec

bridge_kind: proposal_verdict
Document: gtkb-wi6617-membership-auth-same-transaction
Version: 002
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-17 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6617-membership-auth-same-transaction-001.md

# GO — WI-6617 membership mutation is the authorization transaction

## Verdict

GO. The proposed design-disposition postimage for WI-6617 is approved for a
later, separately selected Prime Builder to implement, subject to the
boundaries in this verdict and in the proposal.

## Applicability Preflight

Tooling note: `scripts/bridge_applicability_preflight.py` rejects the source
proposal because it uses a marker-first header (`::init gtkb lo` on line 1,
`NEW` on line 3). This is the documented, pre-existing filing-tool defect
(WI-5814 / WI-6541 / WI-6538), acknowledged by the author in the proposal's
"Filing-Tool Defects" section, not a proposal-content defect. The clause-test
preflight (the operative gate) passes with 0 blocking gaps and
`missing_required_specs` empty by direct verification. Independent verification
of each cited specification confirmed all are real, active, and directly
support the postimage; none is fabricated, and none is missing from the
proposal's Specification Links.

## Clause Applicability

`scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6617-membership-auth-same-transaction`
exits 0 (pass). must_apply: 2, may_apply: 3, evidence gaps in must_apply: 0,
blocking gaps: 0.

## Prior Deliberations

- `DELIB-20260816201237` — owner decision (AUQ-2026-08-17-PAUTH-PROJECT-AUTHORIZATION-MODEL-CORRECTION): membership mutation and re-authorization are the same transaction; exactly one current authorization per project; envelope does not enumerate work-item IDs; supersede per-item PAUTHs into one per project; model first, sweep continues read-only.

## Specifications Carried Forward

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 (active) — C3/C4; amendment not an authorization path.
- `ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001` v1 (active) — event model; functional test.
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 (active) — C2, C3, C4.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` v2 — intrinsic envelope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v5 — carrier ephemeral.
- `GOV-10` v2, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v2, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v6.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 v3 (C3/C4) | Source inspection of lifecycle.add_project_item / remove_project_item / authorize_project / amend_authorization | yes | PASS — add/remove call only link_project_work_item (no auth writer); authorize_project writes included/excluded lists; amend is include-list delta writer |
| ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001 v1 | Spec existence + active-status check via gt spec show | yes | PASS — v1 active |
| DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 v1 (C2/C3/C4) | gt spec show + clause preflight | yes | PASS — C2/C3/C4 requirements confirmed in spec text; clause preflight 0 gaps |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v6 | Fresh reads at review time | yes | PASS |

## Positive Confirmations

- Proposal faithfully implements owner decision DELIB-20260816201237 (C2 creation-reject, C3 same-transaction append, C4 envelope purity, amend retirement).
- All measured HEAD behavior claims verified against source (lifecycle.py lines 297, 736, 1034-1071, 1104+).
- Proposal is targetless (no protected mutation) — requires_review true, requires_verification true, no source/test/git mutation in this slice.
- Sequencing: WI-6617 before WI-6618; WI-6618 hard-blocked until WI-6617 work-product commit.
- Correctly scopes OUT WI-6453, WI-6540, WI-5717, WI-6088, WI-5292, WI-5784, WI-6619.
- Clause preflight passes (0 blocking gaps).

## Findings

None. No defects requiring revision.

## Required Revisions

None. This is a GO.

## Commands Executed

- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6617-membership-auth-same-transaction` → exit 0, 0 blocking gaps
- `gt spec show GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` → v3 active
- `gt spec show DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` → v1 active
- Source inspection: lifecycle.py lines 297-322, 736-760, 1034-1071, 1104-1140
- `gt backlog show WI-6617` → P0, open
- DELIB-20260816201237 read from formal-artifact-approvals

## Owner Action Required

None.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
