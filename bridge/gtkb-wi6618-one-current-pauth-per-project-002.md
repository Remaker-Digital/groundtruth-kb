GO
::init gtkb lo
::open spec

bridge_kind: proposal_verdict
Document: gtkb-wi6618-one-current-pauth-per-project
Version: 002
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-17 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6618-one-current-pauth-per-project-001.md

# GO — WI-6618 one current authorization per project

## Verdict

GO. The proposed supersession pass for WI-6618 is approved for a later,
separately selected Prime Builder to implement, subject to the boundaries in
this verdict and in the proposal.

## Hard-gate confirmation

The WI-6617 work-product commit exists: `2d6382aae` (`feat(project): fold
membership mutation into the authorization transaction (WI-6617)`). The
WI-6617 thread is VERIFIED (terminal) at `bridge/gtkb-wi6617-membership-auth-
same-transaction-004.md`. The hard sequencing gate that WI-6618 MUST NOT start
before WI-6617's work-product commit is satisfied. Any implementer MUST still
confirm `git log` shows a WI-6617-naming work-product commit before running the
collapse.

## Applicability Preflight

Tooling note: `scripts/bridge_applicability_preflight.py` cannot be run on this
marker-first thread (proposal 001 uses a marker-first header with `::init gtkb lo`
on line 1, so the preflight's first-line status parser rejects it). This is the
documented, pre-existing filing-tool defect (WI-5814 / WI-6541 / WI-6538), not a
proposal-content defect. The clause-test preflight (the operative gate) passes
with 0 blocking gaps, and `missing_required_specs` is empty by direct
verification of every cited specification (all real and active).

## Clause Applicability

`scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6618-one-current-pauth-per-project`
exits 0 (pass). must_apply: 3, may_apply: 2, evidence gaps in must_apply: 0,
blocking gaps: 0.

## Prior Deliberations

- `DELIB-20260816201237` — owner decision (AUQ-2026-08-17-PAUTH-PROJECT-AUTHORIZATION-MODEL-CORRECTION): supersede the 585 per-item and surplus project authorizations into one current authorization per project; union of granted scope; prior records move to superseded and remain readable; MUST NOT delete formal authorization records; model first (WI-6617) before data collapse (WI-6618).

## Specifications Carried Forward

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 (active) — cardinality; C1/C2 fail closed only after this supersession pass.
- `ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001` v1 (active) — event model; functional test.
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 (active) — C1 (at most one current row per project_id), C2 (no WI-scoped authorization remains current).
- `GOV-FILE-BRIDGE-AUTHORITY-001` v5 — carrier ephemeral.
- `GOV-10` v2, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v2, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v6.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 v3 (cardinality) | Proposal postimage review + DELIB-20260816201237 Q2 | yes | PASS — exactly one current non-superseded non-revoked authorization per project_id |
| DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C1 | gt spec show + clause preflight | yes | PASS — C1 fail-closed after pass |
| DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C2 | gt spec show + clause preflight | yes | PASS — no current WI-scoped authorization after pass |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v6 | Fresh reads at review time | yes | PASS |

## Positive Confirmations

- Proposal faithfully implements owner decision DELIB-20260816201237 Q2 (supersede into one per project, union-preserving, non-deleting).
- Hard-gate satisfied: WI-6617 work-product commit `2d6382aae` exists; WI-6617 VERIFIED.
- Union scope: "Do not invent broader scope. Do not drop a granted operation or class that any live row allowed." — matches owner intent.
- Non-deleting: "MUST NOT DELETE project-authorization records"; prior rows move to `superseded` — matches canon §1 and owner disposition.
- Folds WI-6557 read-only sweep retirements into the single re-authorization event (owner-chosen batching).
- C1/C2 transition from report-only to fail-closed after the pass.
- Verification plan includes before/after census (active count ≤ 1 per project; union check; superseded count).
- Clause preflight passes (0 blocking gaps).

## Findings

None. No defects requiring revision.

## Required Revisions

None. This is a GO.

## Commands Executed

- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6618-one-current-pauth-per-project` → exit 0, 0 blocking gaps
- `git log --oneline --all --grep="WI-6617"` → 2d6382aae (work-product), ee913ccd2 (bridge)
- `gt spec show GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` → v3 active
- `gt spec show DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` → v1 active
- DELIB-20260816201237 read from formal-artifact-approvals

## Owner Action Required

None.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
