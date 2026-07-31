NEW

# Defect-Fix Proposal - Prevent modernization semantic false-green by executing clause-exactness coverage

bridge_kind: prime_proposal
Document: gtkb-wi5260-modernization-clause-exact-semantics
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5260

target_paths: ["scripts/check_modernization_scope_semantics.py", "platform_tests/scripts/test_modernization_scope_semantics.py"]

## Claim

The frozen modernization semantic checker currently reports PASS while 33 of the 56 clause-exact acceptance cases fail. Bind each affected frozen handle to its exact pytest evidence and evaluate all exact selections in one deterministic, fail-closed subprocess without changing the frozen manifest or manufacturing receipts.

This proposal is filed as the next append-only numbered bridge file, `bridge/gtkb-wi5260-modernization-clause-exact-semantics-001.md`. No prior versioned bridge file is deleted, rewritten, or treated as replaceable state.

## Defect / Reproduction

At HEAD `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f` in the authoritative concurrent worktree:

- `python scripts/check_modernization_scope_semantics.py validate` reports `MODERNIZATION SCOPE SEMANTICS: PASS`.
- `python -m pytest platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py --runxfail -q --tb=short` collects 56 cases and reports `33 failed, 23 passed in 111.00s`.
- None of the clause-exact nodes is currently represented by an exact proof type in `PROOFS`.

The mismatch permits a frozen acceptance handle to remain green because an older broad test passes even when the objective's exact behavior fails.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`:

- `scripts/check_modernization_scope_semantics.py`
- `platform_tests/scripts/test_modernization_scope_semantics.py`

Both paths are presently untracked candidate files. Their pre-implementation bytes are foreign content. WI-5260 may add only independently reviewed changes and must not claim, stage, commit, remove, or replace those foreign bytes.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - Named modernization objectives must be enforced by executable, fail-closed evidence rather than broad family proxies.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected implementation requires this proposal, an independent GO, matching claim, and implementation-start authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The observed false-green is preserved as WI-5260 and a reviewable implementation artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal links the exact implementation scope and tests to governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent VERIFIED requires rerunning every mapped specification-derived test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work item, and target paths are explicit above.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner authorization is durably captured as `DELIB-202666274`; no additional owner question is inferred.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation and runtime test output remain under the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - WI-5260 is the durable backlog authority for this defect.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex filing uses the governed helper and audit path because native Write-hook parity is unavailable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The checker, mapping, regression tests, and independent verdict form the durable change packet.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Implementation and verification advance only after their required lifecycle evidence exists.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Existing proofs, the frozen digest, root containment, and evidence validity remain unchanged.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Exact pytest outcomes become deterministic machine-evaluable evidence and fail closed on absent or invalid results.

## Requirement Sufficiency

Existing requirements sufficient.

The frozen modernization acceptance contract and the specifications linked above already require objective-exact, machine-evaluable, fail-closed evidence. WI-5260 corrects the checker implementation so it enforces those requirements; it does not introduce a new normative behavior or require a specification amendment.

## Prior Deliberations

- `DELIB-202666274` - Owner authorization for all required project-level modernization blocker repairs while preserving bridge, independent review, implementation-start, and mechanical-operation gates.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the Assurance project at project scope. It does not bypass bridge GO, claim/start, independent VERIFIED, Git, release, routing, harness, or deployment gates.

## Proposed Scope

1. Add a scoped `pytest-exact:` proof selector while preserving every existing broad proof and the frozen manifest digest.
2. Add the validated mapping for 47 affected handles using 52 unique proof selections that collect all 56 concrete clause-exact cases. HP03 through HP06 use distinct parameterized node IDs; the unparameterized MOD-AD04 selection aggregates all five parameter cases.
3. Execute all exact selections in one batched pytest subprocess with `--runxfail` and built-in JUnit XML under an owned temporary directory inside `.gtkb-state`.
4. Parse JUnit deterministically. An exact parameterized reference matches one case; an unparameterized base reference aggregates every matching parameter case.
5. Fail closed when pytest fails, XML is missing or malformed, a requested case is absent, or any matching case fails, errors, or skips.
6. Add focused regressions for prefix validation, unchanged broad pytest behavior, one-subprocess execution, parameter and base-node aggregation, missing/skipped/error handling, mapping uniqueness, and 47-handle/52-selection/56-case collection coverage.
7. Do not modify the frozen release-candidate manifest, its digest, receipt schemas, receipt data, or any unrelated target.
8. Treat target pre-start bytes as foreign. If a committed baseline is still absent at verification, finalization must fail closed and route baseline ownership rather than commit unrelated bytes.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_modernization_scope_semantics.py run --phase clean-suite",
  "before_behavior": "Older broad pytest proofs can pass while the objective's clause-exact case fails, producing a semantic false-green.",
  "after_behavior": "Each affected handle consumes exact JUnit case outcomes from one deterministic batched pytest run and fails closed on any incomplete or non-passing result.",
  "self_descriptive_naming": "The pytest-exact prefix distinguishes objective-exact evidence from retained broad pytest compatibility proofs.",
  "obsolete_guidance_disposition": "No existing proof is removed; broad proofs remain visible but cannot substitute for newly mapped clause-exact evidence.",
  "history_preservation": "The frozen manifest, scope digest, existing PROOFS entries, and prior observed evidence remain unchanged and queryable.",
  "baseline": {
    "scope_digest_sha256": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240",
    "semantic_checker": "PASS",
    "clause_exact_cases": 56,
    "clause_exact_passed": 23,
    "clause_exact_failed": 33,
    "runtime_seconds": 111.0
  },
  "expected_result": {
    "exact_handles": 47,
    "exact_selections": 52,
    "collected_cases": 56,
    "subprocesses": 1,
    "semantic_checker_while_exact_failures_exist": "FAIL"
  },
  "rollback": {
    "instructions": "Remove only the independently reviewed WI-5260 exact proof type, map, runner, and focused tests; preserve every foreign pre-start byte and all existing broad proof behavior.",
    "test": "python -m pytest platform_tests/scripts/test_modernization_scope_semantics.py -q --tb=short"
  },
  "hard_invariants": [
    "frozen scope digest remains unchanged",
    "no receipt is created or rewritten",
    "all exact selections execute in one subprocess",
    "temporary paths remain root-contained",
    "foreign untracked baseline bytes are not claimed or finalized"
  ],
  "fail_closed_conditions": [
    "pytest nonzero exit",
    "missing or malformed JUnit XML",
    "missing requested node",
    "failed case",
    "errored case",
    "skipped case",
    "duplicate or uncovered mapping"
  ],
  "essential_context_preservation": "All 94 frozen handles, existing broad proofs, receipt validators, phase behavior, and root-containment rules remain present."
}
```

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Run the focused scope-semantics tests and prove 47 handles map to 52 unique exact selections covering 56 cases. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Prove the frozen digest and every existing broad proof are unchanged; run focused non-regression tests. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Exercise passing, failing, errored, skipped, missing, and malformed JUnit outcomes and require deterministic fail-closed results. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run proposal applicability and clause preflights against this complete content. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns the focused suite and the complete 56-case `--runxfail` command before VERIFIED. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all temporary JUnit and pytest basetemp paths resolve under `E:\GT-KB\.gtkb-state`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify active GO, matching claim, and implementation-start authority before either target is edited. |

## Acceptance Criteria

1. The 47 affected handles map to 52 unique exact proof selections that collect all 56 concrete clause-exact cases with zero duplication or omission.
2. The checker preserves all existing broad proofs and frozen digest `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`.
3. One batched exact run reports each handle from JUnit outcomes and fails closed for failures, errors, skips, missing XML, malformed XML, or missing cases.
4. Focused regression tests pass under the repository default timeout.
5. The current 33 exact failures can no longer coexist with `MODERNIZATION SCOPE SEMANTICS: PASS`.
6. No foreign pre-start target bytes, receipts, frozen manifest data, Git state, bridge configuration, TAFE state beyond governed publication, harness state, or external systems are mutated by implementation.

## Risks / Rollback

- Exact evaluation adds approximately 111 seconds to AT-SCOPE-SEMANTICS. One batched subprocess keeps this far below the 2400-second acceptance timeout.
- JUnit node reconstruction can mishandle parameters. Tests cover exact parameter references and unparameterized base aggregation.
- Pytest or XML failures could otherwise be mistaken for missing evidence. Every such state fails closed with machine-readable detail.
- Both target files are untracked foreign candidates. The implementation report must identify only WI-5260 additions. If no committed baseline exists, VERIFIED finalization is prohibited until the owning baseline is governed or the target boundary is separated.
- Rollback removes only WI-5260 additions through an independently reviewed patch and reruns the focused suite; it must not restore, replace, stage, or delete foreign bytes.

## Files Expected To Change

- `scripts/check_modernization_scope_semantics.py`
- `platform_tests/scripts/test_modernization_scope_semantics.py`

## Recommended Commit Type

`fix`
