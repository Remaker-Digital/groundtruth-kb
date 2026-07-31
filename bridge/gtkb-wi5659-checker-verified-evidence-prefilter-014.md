NO-GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex-automation
author_harness_id: A
author_session_context_id: A-2026-07-24T00-27-25Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=not-provided; thread_source=automation

bridge_kind: lo_verdict
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 014
Date: 2026-07-24 UTC
Reviewer: Loyal Opposition (Codex)
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-013.md

## Summary

This revision correctly accepts the ordering finding from version 012 and provides a complete independent-GO proposal. Its preflights, project linkage, declared paths, and test plan are otherwise sound. However, it declares existing requirements sufficient while implementing and testing a material divergence from the owner decision for mechanism 3: the decision requires every index entry to remain represented in the snapshot ledger, while the proposal and live code deliberately keep oversized blobs out of that ledger in a separate `exempted` map. PAUTH v4 repeats the separate-map approach, creating a durable requirement conflict rather than resolving it. A `GO` cannot choose between those two security contracts by inference.

## Findings

### P1 — Mechanism 3's authoritative accounting contract is internally inconsistent

- **Claim:** The proposal cannot truthfully state that existing requirements are sufficient because the owner decision and the proposed implementation specify incompatible representations for oversized blobs.
- **Evidence:** `DELIB-202667186` requires that "Every index entry remains represented in the snapshot ledger with its mode, object id, and declared size." In contrast, version 013 says oversized blobs are deliberately not placed in `ledger`, and instead records them in `_BridgeSnapshot.exempted`. The live implementation at `scripts/check_protected_commit_authorization.py` lines 141-150 and 769-798 implements that separate map; the focused tests explicitly assert `"authority.txt" not in bridge_snapshot.ledger` and `"big.txt" not in ledger` in `platform_tests/scripts/test_check_protected_commit_authorization.py` lines 1569-1571 and 2335-2338. PAUTH v4's scope summary also describes a separate `exempted` map, but does not supersede or amend the owner-decision contract.
- **Impact:** The `ledger` is the structure `_verify_snapshot_ledger` uses for file-set, identity, and content-hash integrity. Treating a separate mutable map as equivalent without an owner decision or requirement amendment weakens the review's ability to prove that the authorized security contract—not merely a fast implementation—was selected.
- **Recommended action:** Obtain a focused owner clarification through the governed deliberation path: either (a) require oversized entries to remain in a verifier-recognized ledger representation and revise the implementation/test plan accordingly, or (b) explicitly amend `DELIB-202667186` to permit the separate `exempted` map and define the integrity checks it must satisfy. Then file a REVISED proposal that cites the resolved contract. Do not infer that PAUTH v4 silently supersedes the owner decision.

## Positive Confirmations

- The operative author session context `a94000f7-fde3-4a4e-8d8e-f7b09e51fffb` differs from this review session `A-2026-07-24T00-27-25Z`; metadata is present, so review independence is satisfied.
- The applicability preflight passed with no missing required or advisory specifications, and the mandatory clause preflight reported four must-apply clauses with zero evidence or blocking gaps.
- The declared source and test paths are in root and match active PAUTH v4 / WI-5659 scope. The backlog check found no duplicate work; WI-5660 remains a separate bridge-helper defect.
- Independent checks passed: 113 focused pytest tests; Ruff lint; and Ruff format check.
- The revision explicitly preserves the version-012 rule that a future `GO` is not retroactive authorization for the already-disclosed earlier change.

## Prior Deliberations

- `DELIB-202667184` establishes the independent bridge `GO` / `VERIFIED` sequence for WI-5659.
- `DELIB-202667185` authorizes the batch materialization scope and preserves its fail-closed constraints.
- `DELIB-202667186` authorizes mechanism 3 but contains the unresolved snapshot-ledger requirement cited above.
- `DELIB-202667187` authorizes mechanism 4's ledger-verification scope.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-012.md` correctly rejected the prior out-of-order implementation report and required this proposal.

## Applicability Preflight

- packet_hash: `sha256:931cb51e2c101e00030d3333f9c0767ce57cdaf6e827d3c57e1994250a9d7b5b`
- bridge_document_name: `gtkb-wi5659-checker-verified-evidence-prefilter`
- declared_target_paths: ["platform_tests/scripts/test_check_protected_commit_authorization.py", "scripts/check_protected_commit_authorization.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-013.md`
- operative_file: `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-013.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:da21f7d6a0c9dcfa4ae65fe3cd716f54e05929d437d80f213f838de4642f08a1`

| Spec | Severity | Cited |
|---|---|---|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes |

## Clause Applicability

- Bridge id: `gtkb-wi5659-checker-verified-evidence-prefilter`
- Operative file: `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-013.md`
- Clauses evaluated: 5; must_apply: 4; may_apply: 1; not_applicable: 0.
- Evidence gaps in must-apply clauses: 0; blocking gaps: 0; mandatory preflight exited 0.

| Clause | Applicability | Evidence |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — |

## Review Method

- Read the full fourteen-version bridge chain, including the version-012 ordering finding and this version-013 revision.
- Inspected the live target implementation and the mechanism-3 / mechanism-4 test cases.
- Ran the mandatory applicability and ADR/DCL clause preflights against version 013.
- Searched the Deliberation Archive for WI-5659 and mechanisms 3/4; reviewed `DELIB-202667184` through `DELIB-202667187` and active PAUTH v4.
- Ran `python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` (113 passed), `python -m ruff check ...` (passed), `python -m ruff format --check ...` (2 files already formatted), and `git diff --check` (passed).

## Verdict

**NO-GO** — resolve the owner-level snapshot-ledger versus separate-exemption-map contract before this proposal can receive an independent `GO`. The revision is otherwise well-scoped and its validation evidence should be preserved for the next review.
