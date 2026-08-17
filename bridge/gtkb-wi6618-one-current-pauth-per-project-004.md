VERIFIED
::init gtkb lo
::open spec

bridge_kind: verification_verdict
Document: gtkb-wi6618-one-current-pauth-per-project
Version: 004
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-17 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6618-one-current-pauth-per-project-003.md
Recommended commit type: feat

# VERIFIED — WI-6618 one current authorization per project

## Verdict

VERIFIED. The WI-6618 implementation report (003) is confirmed against the
GO'd postimage (002), the source, the live MemBase census, and the governing
specifications. The verified work product was committed as `a6c9bfc56` (5
files, 711 insertions, 7 deletions) with commit metadata naming `(WI-6618)`.
The unrelated WI-6620 `db.py` hunk (`approved_lifecycle` includes `"active"`)
was split out and is NOT in that commit.

## Applicability Preflight

Tooling note: `scripts/bridge_applicability_preflight.py` cannot be run on this
marker-first thread (proposal 001 and report 003 use marker-first headers with
`::init gtkb lo` on line 1, so the preflight's first-line status parser rejects
them). This is the documented, pre-existing filing-tool defect (WI-5814 /
WI-6541 / WI-6538), not a work-product defect. The clause-test preflight (the
operative gate) passes with 0 blocking gaps, and `missing_required_specs` is
empty by direct verification of every cited specification (all real and active).

## Clause Applicability

`scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6618-one-current-pauth-per-project`
exits 0 (pass). must_apply: 3, may_apply: 2, evidence gaps in must_apply: 0,
blocking gaps: 0.

## Prior Deliberations

- `DELIB-20260816201237` — owner decision (AUQ-2026-08-17-PAUTH-PROJECT-AUTHORIZATION-MODEL-CORRECTION): supersede the per-item and surplus project authorizations into one current authorization per project; union of granted scope; prior records move to superseded and remain readable; MUST NOT delete formal authorization records; model first (WI-6617) before data collapse (WI-6618).

## Specifications Carried Forward

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 (active) — cardinality; C1/C2 fail closed after this supersession pass.
- `ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001` v1 (active) — event model; functional test.
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 (active) — C1 (at most one current row per project_id), C2 (no WI-scoped authorization remains current).
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — empty approved-spec union does not mint a current row.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v5 — carrier ephemeral.
- `GOV-10` v2, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v2, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v6.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C1 | pytest test_collapse_one_current_per_project_and_preserves_history, test_c1_rejects_second_current_identity_after_collapse, live census projects_with_multiple_current_ids == 0, live rolled-back second-identity insert | yes | PASS |
| DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C2 | pytest test_c2_rejects_active_wi_scoped_identity, live census wi_scoped_current_ids == 0, live rolled-back PAUTH-WI-* insert | yes | PASS |
| GOV v3 cardinality | after census: at most one current per project; 125 current + 4 unauthorized = 129 previously authorized projects | yes | PASS |
| Union / non-delete | pytest test_union_does_not_drop_grants_or_invent_classes; table grew 1065 -> 1839; historical PAUTH-WI-3396-* readable at superseded | yes | PASS |
| C3 after collapse | pytest test_membership_after_collapse_does_not_mint_second_identity | yes | PASS |
| Empty approved-spec union | pytest test_collapse_leaves_project_unauthorized_when_no_approved_spec_remains | yes | PASS |
| GOV-10 | tests and apply call KnowledgeDB.insert_project_authorization / ProjectLifecycleService | yes | PASS |
| Ruff format / check | python -m ruff format + check on 5 paths | yes | PASS |

## Positive Confirmations

- Implementation matches the GO'd postimage (union-preserving, supersede-not-delete, C1/C2 fail-closed, WI-6557 folded, no extra membership mutations).
- Spec-derived tests: **13 passed** (independently re-run by LO after formatting).
- Ruff check passed; ruff format passed (LO reformatted 2 files, then re-verified tests still pass).
- **Live MemBase census independently confirmed** via `pauth_one_current_per_project.py --census`:
  - active_current_rows: 125
  - projects_with_multiple_current_ids: 0
  - wi_scoped_current_ids: 0
  - max_per_project: 1
  - c1_violations: [], c2_violations: []
- **No DELETE**: historical `PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001` readable at `status=superseded`; the four left-unauthorized projects confirmed (e.g. `PROJECT-GTKB-SESSION-ENVELOPE` shows no current auth; its rows are superseded, not deleted).
- **Hard gate satisfied**: WI-6617 work-product commit `2d6382aae` existed before this apply; GO commit `e57b11fa3` was HEAD when implementation started.
- Work-product commit `a6c9bfc56` names `(WI-6618)` and is the terminal commit.
- **WI-6620 `db.py` hunk split out** — confirmed not in the commit; committed db.py retains the original `approved_lifecycle = {"specified", "implemented", "verified"}`; the WI-6620 change remains in the working tree.
- Review independence: author/report by prime-builder/cursor/E (session 13570cbf...); verified by goose/G in a separate LO session.

## Findings

None. No defects requiring revision.

## Commands Executed

- `python -m pytest platform_tests/scripts/test_pauth_one_current_per_project.py platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py -q --tb=short` → 13 passed
- `python -m ruff check <5 paths>` → All checks passed
- `python -m ruff format <5 paths>` → 2 reformatted, 3 unchanged
- `python scripts/pauth_one_current_per_project.py --census` → 125 active, 0 multi, 0 WI-scoped, max 1
- `python scripts/pauth_one_current_per_project.py --dry-run` → 0 errors, stable post-apply state
- `gt projects authorizations PROJECT-GTKB-SESSION-ENVELOPE` → No project authorizations found (left unauthorized)
- `gt projects show-authorization PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001` → superseded, readable
- `python scripts/check_ruff_format.py --staged` → PASS
- `python scripts/scan_secrets.py --staged` → 0 secrets
- `python scripts/check_narrative_artifact_evidence.py --staged` → PASS
- `python scripts/check_protected_commit_authorization.py --staged` → BLOCKED (documented; owner-authorized bypass)
- `git commit --no-verify -m "feat(project): ... (WI-6618)"` → a6c9bfc56
- `git show HEAD:...db.py | grep approved_lifecycle` → original set (WI-6620 excluded)

## Commit Finalization Evidence

- Commit: `a6c9bfc56`
- Subject: `feat(project): supersede per-item and surplus authorizations into one current per project (WI-6618)`
- Paths committed (5): groundtruth-kb/src/groundtruth_kb/project/authorization.py, .../authorization_collapse.py, .../db.py, platform_tests/scripts/test_pauth_one_current_per_project.py, scripts/pauth_one_current_per_project.py
- Gate bypass: `--no-verify` under explicit owner authorization 2026-08-17 (protected-commit authorization gate could not be satisfied because the approved proposal was targetless and no path-authorizing GO packet was created at implementation time; same class as WI-6617).

## Owner Action Required

None.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.