NEW

# Implementation Proposal - Make change-controlled artifact evaluation fail closed

bridge_kind: prime_proposal
Document: gtkb-wi5153-fail-closed-artifact-evaluability
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5153

target_paths: ["groundtruth-kb/src/groundtruth_kb/assertions.py", "groundtruth-kb/tests/test_assertions.py", "scripts/check_artifact_evaluability.py", "platform_tests/scripts/test_check_artifact_evaluability.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make unsupported, skipped, partial, contradictory, stale, and zero-executable
change-controlled evidence fail closed instead of contributing to a passing
assertion aggregate. Add a read-only evaluator that binds each result to the
carrier version/hash, evaluator version/hash, evaluation time, selected scope,
currentness state, and invalidation conditions.

The authoritative worktree already contains a candidate for this scope. Those
bytes are review evidence, not assumed approval: after independent GO the Prime
Builder must reconcile the candidate to the approved outcomes, rerun the full
verification plan, and report only the exact WI-5153 hunks. The two untracked
targets remain foreign until WI-5359 establishes their exact committed baseline.

Current candidate inventory:

| Path | Current SHA-256 | Disposition |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/assertions.py` | `7BFB40A6A21D419E2B747A28ABA519A8EBBDAA6A1D03C2D3D1D4DAF829806158` | Review only the fail-closed status/aggregate hunks against HEAD. |
| `groundtruth-kb/tests/test_assertions.py` | `F1211CA8B9BC624789778668CE1AA3861C8351081EFB6282604E051B4D08C2F8` | Review only the matching WI-5153 regression hunks against HEAD. |
| `scripts/check_artifact_evaluability.py` | `AE6B58F5FE5B4BDE9A5501A013D0CEFD5D229BEC6AF41A7750449F9CBC686065` | Whole-file descendant only after WI-5359 baseline. |
| `platform_tests/scripts/test_check_artifact_evaluability.py` | `69E4FAC09572619DCCD6C9FA526FBC14BA795AE1225949691E4574B612F15B67` | Whole-file descendant only after WI-5359 baseline. |

## Specification Links

- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Required evidence must be machine-evaluable, current, complete, and fail closed on unsupported or indeterminate states.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - Cross-cutting carrier obligations cannot pass from prose, omission, or skipped execution.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - Release promotion requires complete passing governed evidence rather than a false-green aggregate.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Legitimate executable PASS/FAIL behavior and history remain intact while missing evidence becomes explicit.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected implementation requires independent GO, matching claim/start authority, implementation reporting, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The exact source/test scope is linked to every governing requirement above.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, WI, and parseable target paths are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent verification reruns core, schema, gate, evaluator, and negative-evidence tests.
- `GOV-STANDING-BACKLOG-001` - WI-5153 is the durable semantic owner; WI-5359 owns the precursor baseline.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Implementation and test output remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN` - Establishes fail-closed evaluability before hard-invariant projection.
- `DELIB-202666274` - Authorizes the modernization program while preserving bridge, independent review, and mechanical Git gates.

## Owner Decisions / Input

No new owner decision is required. The active Assurance PAUTH and the owner's
full-program authorization cover this implementation proposal. This does not
authorize Git staging/commit, database mutation, dispatcher/TAFE/harness
mutation, cleanup, release, or deployment.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
defines the required result and currentness semantics; the other linked carriers
define enforcement, non-impairment, and independent verification. No formal
carrier amendment is needed.

## Proposed Scope

1. Emit explicit `PASS`, `FAIL`, `PARTIAL`, `UNASSESSED`, and `NOT_APPLICABLE` evaluation results while retaining the compatibility `passed` boolean.
2. Treat unsupported required assertion types and skipped required children as non-passing evidence.
3. Propagate `UNASSESSED` and `PARTIAL` through `all_of` and `any_of`; do not discard skipped children before composition.
4. Treat no defined assertions as `NOT_APPLICABLE`, all unsupported/non-machine assertions as `UNASSESSED`, mixed complete/incomplete evidence as `PARTIAL`, and direct executable failure as `FAIL`.
5. Make aggregate summaries pass only when every applicable carrier passes; expose partial and unassessed counts and stable diagnostic statuses.
6. Evaluate change-controlled ADR/DCL/GOV carriers read-only and bind results to subject identity/version/hash, evaluator identity/version/hash, timestamp, selected assertion scope, evidence state, and invalidation conditions.
7. Reject duplicate/unknown scoped assertion IDs, unsupported evidence states, malformed assertion data, and multi-carrier scoped requests.
8. Keep a scoped assertion PASS from representing a full-carrier PASS while deferred assertions remain.
9. Preserve deterministic prose/stored assertion reconciliation and historical KEEP/QUARANTINE versus active-leakage classification.
10. Exclude `groundtruth-kb/src/groundtruth_kb/gates.py`, assertion schema files, `groundtruth.db`, formal carrier mutation, WI-5152 registry work, and every unrelated dirty hunk.
11. Do not finalize either untracked path until WI-5359's exact baseline is independently VERIFIED and committed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_artifact_evaluability.py --spec DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001 --json",
  "before_behavior": "Unsupported and zero-executable evidence can be skipped out of aggregation and appear passing.",
  "after_behavior": "Every applicable carrier exposes an explicit result and only complete current executable PASS evidence satisfies governed gates.",
  "self_descriptive_naming": "Evaluation result names distinguish failed, partial, unassessed, and not-applicable states directly.",
  "obsolete_guidance_disposition": "Compatibility booleans remain, but guidance that treats skipped required evidence as passing is superseded by explicit status fields.",
  "history_preservation": "Assertion definitions, recorded history, legitimate executable outcomes, and nonoperative historical evidence remain queryable.",
  "baseline": {
    "integrated_tests": 141,
    "candidate_integrated_passed": 141,
    "unsupported_required_may_pass": true,
    "zero_executable_may_pass": true
  },
  "expected_result": {
    "integrated_tests": 141,
    "integrated_passed": 141,
    "unsupported_required_result": "FAIL",
    "zero_executable_result": "UNASSESSED",
    "mixed_result": "PARTIAL"
  },
  "rollback": "Remove only independently reviewed WI-5153 hunks after a separately governed rollback review; preserve the WI-5359 baseline and all unrelated concurrent changes.",
  "hard_invariants": [
    "no unsupported required evidence passes",
    "no skipped required child is discarded",
    "no scoped pass becomes a full-carrier pass",
    "no stale or contradictory evidence satisfies a current gate",
    "no unrelated tracked hunk or database row is included"
  ],
  "fail_closed_conditions": [
    "unknown assertion type",
    "duplicate or unknown assertion id",
    "malformed assertion data",
    "noncurrent evidence state",
    "subject or evaluator version/hash change",
    "WI-5359 baseline absent for untracked descendants"
  ],
  "essential_context_preservation": "Existing assertion APIs, compatibility booleans, legitimate executable results, carrier history, and exact scoped-selection evidence remain available."
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Core fail-closed assertion semantics | `python -m pytest groundtruth-kb/tests/test_assertions.py -q --tb=short --timeout=600` | All tests pass, including unsupported, zero-executable, partial, and composite propagation cases. |
| Schema/gate non-regression | `python -m pytest groundtruth-kb/tests/test_assertion_schema.py groundtruth-kb/tests/test_gates.py -q --tb=short --timeout=600` | All existing tests pass with no modifications required in those files. |
| Evaluator semantics/currentness | `python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short --timeout=180` | 14 tests pass after WI-5359 baseline plus reviewed descendant hunks. |
| Integrated boundary | `python -m pytest groundtruth-kb/tests/test_assertions.py groundtruth-kb/tests/test_assertion_schema.py groundtruth-kb/tests/test_gates.py platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short --timeout=600` | Current candidate evidence is 141 passed; implementation remains fully green. |
| Live fail-closed census | `python scripts/check_artifact_evaluability.py --json` | Nonzero while any current change-controlled carrier is FAIL, PARTIAL, or UNASSESSED; report includes stable reason/currentness fields. |
| Scope isolation | `git diff --` limited to the four target paths plus exact hash checks | No `gates.py`, database, registry, formal-carrier, dispatcher, harness, or unrelated hunk is included. |

## Acceptance Criteria

1. Unsupported, skipped, zero-executable, partial, stale, contradictory, and malformed evidence cannot produce aggregate PASS.
2. Complete supported executable evidence preserves its legitimate PASS/FAIL result.
3. Scoped PASS remains carrier `PARTIAL` while deferred assertions exist.
4. Reports bind subject/evaluator identities, versions/hashes, evaluation time, scope, currentness, and invalidation conditions.
5. The integrated 141-test boundary passes.
6. WI-5359 establishes the untracked baseline before descendant finalization.
7. Only exact WI-5153 hunks are reported and later mechanically finalized.

## Risk / Rollback

The intended behavior change will expose many currently unevaluable carriers as
blocking; WI-5152 and later Assurance work must add real executable evidence,
not relax this evaluator. Compatibility consumers may still read `passed`, but
new status fields are authoritative for the richer result state.

Rollback removes only the independently reviewed WI-5153 hunks through a
separate governed transaction. It must preserve WI-5359, concurrent changes,
assertion history, and all append-only governance evidence.

## Bridge Filing

This proposal is filed as the next append-only numbered file for
`gtkb-wi5153-fail-closed-artifact-evaluability`. Dispatcher/TAFE state plus the
numbered file chain remain live workflow authority; this session performs no
manual routing or direct harness contact.

## Recommended Commit Type

`fix` - required assertion evidence stops failing open.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
