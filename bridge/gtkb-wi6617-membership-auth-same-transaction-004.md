VERIFIED
::init gtkb lo
::open spec

bridge_kind: verification_verdict
Document: gtkb-wi6617-membership-auth-same-transaction
Version: 004
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-17 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6617-membership-auth-same-transaction-003.md
Recommended commit type: feat

# VERIFIED — WI-6617 membership mutation is the authorization transaction

## Verdict

VERIFIED. The WI-6617 implementation report (003) is confirmed against the
GO'd postimage (002), the source, and the governing specifications. The verified
work product was committed as `2d6382aae` (4 files, 543 insertions, 52
deletions) with commit metadata naming `(WI-6617)`. The unrelated WI-6620
`db.py` hunk (`approved_lifecycle` includes `"active"`) was split out and is NOT
in that commit.

## Applicability Preflight

Tooling note: `scripts/bridge_applicability_preflight.py` cannot be run on this
marker-first thread (the source proposal 001 and report 003 use marker-first
headers with `::init gtkb lo` on line 1, so the preflight's first-line status
parser rejects them). This is the documented, pre-existing filing-tool defect
(WI-5814 / WI-6541 / WI-6538), not a work-product defect. The clause-test
preflight (the operative gate) passes with 0 blocking gaps, and `missing_required_specs`
is empty by direct verification of every cited specification (all real and active).

## Clause Applicability

`scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6617-membership-auth-same-transaction`
exits 0 (pass). must_apply: 2, may_apply: 3, evidence gaps in must_apply: 0,
blocking gaps: 0.

## Prior Deliberations

- `DELIB-20260816201237` — owner decision (AUQ-2026-08-17-PAUTH-PROJECT-AUTHORIZATION-MODEL-CORRECTION): membership mutation and re-authorization are the same transaction; exactly one current authorization per project; envelope does not enumerate work-item IDs; supersede per-item PAUTHs into one per project; model first (WI-6617) before data collapse (WI-6618).

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
| DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C3 | pytest test_add_item_to_authorized_project_increments_pauth_version, test_auth_append_failure_rolls_back_membership, test_move_between_authorized_projects_appends_both, test_add_item_to_unauthorized_project_does_not_create_pauth | yes | PASS (7 total) |
| DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C4 | pytest test_insert_rejects_enumerated_work_item_ids | yes | PASS |
| DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C2 | pytest test_insert_rejects_work_item_scoped_identity | yes | PASS |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 v3 (amend clause) | pytest test_amend_authorization_fails_closed_and_leaves_version | yes | PASS |
| GOV-10 | tests call ProjectLifecycleService / KnowledgeDB.insert_project_authorization production interfaces | yes | PASS |
| Ruff format / check | python -m ruff format + check on 4 staged files | yes | PASS |

## Positive Confirmations

- Implementation matches the GO'd postimage exactly (C2/C3/C4, amend retirement).
- Spec-derived tests: **7 passed** (independently re-run by LO after formatting).
- Ruff check passed; ruff format passed (LO reformatted 2 files the report's check had missed, then re-verified tests still pass).
- Work-product commit `2d6382aae` names `(WI-6617)` and is the terminal commit.
- **WI-6620 `db.py` hunk split out** — confirmed not in the commit; committed db.py retains the original `approved_lifecycle = {"specified", "implemented", "verified"}`; the WI-6620 change remains in the working tree.
- WI-6618 NOT started (remains NEW/001); 938-row population NOT collapsed.
- Review independence: author/report by prime-builder/cursor/E (session 13570cbf...); verified by goose/G in a separate LO session.

## Findings

None. No defects requiring revision.

## Commands Executed

- `python -m pytest platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py -q --tb=short` → 7 passed
- `python -m ruff check <4 paths>` → All checks passed
- `python -m ruff format <4 paths>` → 2 reformatted, 2 unchanged
- `python scripts/check_ruff_format.py --staged` → PASS
- `python scripts/scan_secrets.py --staged` → 0 secrets
- `python scripts/check_narrative_artifact_evidence.py --staged` → PASS
- `python scripts/check_protected_commit_authorization.py --staged` → BLOCKED (documented; owner-authorized bypass)
- `git commit --no-verify -m "feat(project): ... (WI-6617)"` → 2d6382aae
- `git show HEAD:...db.py | grep approved_lifecycle` → original set (WI-6620 excluded)

## Commit Finalization Evidence

- Commit: `2d6382aae01cc3b4aeb85c5455c3d2f3129d320a`
- Subject: `feat(project): fold membership mutation into the authorization transaction (WI-6617)`
- Paths committed (4): groundtruth-kb/src/groundtruth_kb/db.py, .../project/authorization.py, .../project/lifecycle.py, platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py
- Gate bypass: `--no-verify` under explicit owner authorization 2026-08-17 (protected-commit authorization gate could not be satisfied because the approved proposal was targetless and no path-authorizing GO packet was created at implementation time).

## Owner Action Required

None. WI-6618 may now proceed (it is unblocked by this VERIFIED).

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
