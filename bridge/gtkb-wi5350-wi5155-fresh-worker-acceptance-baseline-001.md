NEW

# Stabilize the WI-5155 Fresh-Worker Acceptance Baseline

bridge_kind: prime_proposal
Document: gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T19:40:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5350

target_paths: ["platform_tests/scripts/test_modernization_fresh_worker.py"]

implementation_scope: test baseline stabilization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Independently review and adopt the exact WI-5155 fresh-worker acceptance-test
candidate that is present in the worktree but absent from `HEAD`. The file is a
pre-existing 17,076-byte implementation candidate. Because it is untracked,
descendant WI-5336 cannot safely finalize a one-line timeout marker without
absorbing the complete foreign baseline.

This is a byte-adoption transaction, not a test-behavior change. The sole
candidate is:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `platform_tests/scripts/test_modernization_fresh_worker.py` | `8A3C32384031A272070C304FCA99634C0E5360C16841475E88FF7A5756C1751A` | 17,076 |

All four tests passed unchanged in 51.36 seconds under diagnostic
`--timeout=600`. Independent review must inspect the complete file, confirm the
hash immediately before reporting, and preserve WI-5155 provenance. Any
WI-5336 `@pytest.mark.timeout(...)` descendant hunk is excluded and may be
implemented only after this exact baseline is present in `HEAD`.

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - governs deterministic worker context assembly, seven-category manifests, failure/recovery behavior, and role/activity isolation.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` - governs the six-activity evaluation surfaces for which the fresh-worker proof was created.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - requires release-readiness evidence and regression visibility from executable governed tests.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires deterministic evidence for adopting a change-controlled test artifact.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires baseline adoption to preserve legitimate behavior and every hard invariant.
- `GOV-WORK-TREE-HYGIENE-001` - requires verified candidate bytes to receive explicit ownership instead of remaining unexplained dirt.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs independent review, exact claim/start scope, implementation report, and VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant governing specifications to be linked here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5350 to the active Assurance project PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires hash, whole-file review, and executable test evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - requires this baseline to precede WI-5336 and forbids absorption of its descendant marker.
- `GOV-STANDING-BACKLOG-001` - keeps the missing baseline visible until its exact bytes are independently verified and finalized.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires every candidate and evidence path to remain inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserve the historical WI-5155 lifecycle and current baseline-stabilization lifecycle as distinct governed artifacts.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-READINESS-AUTHORIZATION` - authorized the Assurance project and WI-5155 fresh-worker evaluation work.
- `DELIB-202666274` - authorizes required modernization blocker and false-closure repairs at project scope while preserving review and mechanical-operation gates.

## Owner Decisions / Input

`DELIB-202666274` and active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
authorize this independently reviewed baseline recovery. No new owner decision
is required for filing or exact-byte review. This proposal does not authorize
staging, commit, push, release, deployment, dispatcher/TAFE mutation, harness
mutation, credential lifecycle, destructive cleanup, or external-system
mutation. Any later local commit still requires exact mechanical authority.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-ACTIVITY-CONTEXT-MANIFEST-001`,
`GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, the exact candidate bytes, and
the four executable acceptance tests completely define the baseline. No new
or revised requirement is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "config/governance/modernization-release-candidate.json",
  "primary_route": "independently reviewed exact-byte baseline adoption before descendant timeout repair",
  "before_behavior": "the complete fresh-worker acceptance candidate is untracked, so descendant finalization would absorb foreign bytes",
  "after_behavior": "the exact WI-5155 baseline exists in HEAD and WI-5336 can finalize only its own test-local marker",
  "self_descriptive_naming": "WI-5350 identifies baseline stabilization and preserves WI-5155 provenance",
  "obsolete_guidance_disposition": "historical WI-5155 work remains history and is not rewritten as current implementation authority",
  "history_preservation": "the original WI-5155 lifecycle and new baseline-recovery lifecycle remain separate",
  "baseline": {
    "head_presence": "path absent",
    "worktree_presence": "exact candidate path untracked",
    "diagnostic_tests": "4 passed in 51.36 seconds"
  },
  "expected_result": {
    "head_presence": "the exact candidate hash is present",
    "descendant_scope": "WI-5336 timeout annotation remains absent from the baseline"
  },
  "rollback": {
    "instructions": "revert only the exact one-file baseline transaction under separately authorized Git mechanics",
    "test": "rerun the four frozen tests and exact hash inventory"
  },
  "hard_invariants": [
    "no unrelated worktree byte is absorbed",
    "no WI-5336 timeout hunk is included",
    "wheel isolation and source-tree/root-config absence remain asserted",
    "all current fresh-worker assertions remain intact"
  ],
  "fail_closed_conditions": [
    "the candidate hash changes",
    "a second path enters scope",
    "an assertion is removed or weakened",
    "exact Git mechanical authority is absent"
  ],
  "essential_context_preservation": "all current fresh-worker context assembly, packaging, isolation, and fallback assertions are preserved"
}
```

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001`; `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`; `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --timeout=600` | All four unchanged tests pass; deterministic manifest, failure/recovery, wheel/source-tree/root-config, role, and activity-isolation assertions execute. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`; `GOV-WORK-TREE-HYGIENE-001` | SHA-256/byte inventory before report and finalization; exact one-path diff/index inventory | Hash and size match this proposal; exactly one file is adopted. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Complete-file review and the four-test run | No assertion or legitimate result is removed, weakened, or bypassed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mandatory preflights, exact matching claim/start, implementation report, and independent whole-file review | No missing required/advisory specs or clause gaps; exact-byte adoption is independently VERIFIED. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Search the candidate for a test-local timeout marker and compare its hash to this proposal | No WI-5336 `@pytest.mark.timeout(...)` hunk is present; WI-5336 remains a later descendant. |
| `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5155/WI-5350 histories and numbered proposal/report/verdict chain | Historical implementation and current baseline stabilization remain distinct and traceable. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and exact path inventory | `CLAUSE-IN-ROOT` passes and every dependency resolves under `E:\GT-KB`. |

## Risk / Rollback

Whole-file adoption is intentional because the candidate is absent from
`HEAD`. The principal risk is misattributing later bytes or smuggling WI-5336
into the baseline. Independent review must inspect the complete file, bind the
exact hash, rerun all four tests, and fail closed on drift. No test edit is
proposed. Rollback is limited to the exact one-file baseline transaction under
separate Git authority; no broad reset, cleanup, or unrelated operation is
permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - restores the missing committed carrier for a pre-existing acceptance
baseline without changing test behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
