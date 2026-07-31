NEW

# Stabilize the Frozen Git-Lifecycle Acceptance Baseline

bridge_kind: prime_proposal
Document: gtkb-wi5354-git-lifecycle-acceptance-baseline
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T20:00:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5354

target_paths: ["scripts/check_modernization_git_lifecycle.py", "platform_tests/scripts/test_modernization_git_lifecycle.py"]

implementation_scope: checker and test baseline stabilization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Independently review and adopt the exact two-file frozen Git-lifecycle
acceptance baseline that is present in the worktree but absent from `HEAD`.
The checker and its black-box wrapper are both untracked, so descendant WI-5344
cannot safely repair the wrapper's nested timeout and process-tree behavior
without absorbing the complete foreign baseline.

This is an exact byte-adoption transaction, not a behavior repair. The
candidates are:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `scripts/check_modernization_git_lifecycle.py` | `FFB2ED61FA8D71496202B1A80BB7C7831233E10240C62FE7FC4EE7194ECC73C4` | 88,924 |
| `platform_tests/scripts/test_modernization_git_lifecycle.py` | `AD497F681853B0661DA2A63ECF5D4BED668129E04D43C68D84E75EA63F0A7536` | 1,029 |

The checker passed directly in 322.23 seconds with capability
`CAP-GIT-LIFECYCLE`, aggregate status `PASS`, and exactly 26/26 required
assertions passing. The wrapper's current 180-second pytest marker around a
900-second child timeout is a known WI-5344 defect and is intentionally
preserved in this baseline. Independent review must inspect both complete
files, confirm both hashes immediately before reporting, and preserve this
baseline/descendant separation.

## Specification Links

- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - governs the project/work-item Git lifecycle modeled by the checker.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - defines the production lifecycle outcomes and failure behavior that the 26 assertions exercise.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - governs branch binding, scoped commits, integration, and promotion evidence checked by the baseline.
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` - governs released-state authority and promotion boundaries exercised by the checker.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires baseline adoption to preserve every legitimate checker result and hard invariant.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact ownership for the two untracked candidates before WI-5344 changes them.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs independent review, exact claim/start scope, implementation report, and VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant governing specifications to be linked here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5354 to the active Git Lifecycle project PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires exact hash and executable checker evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - requires this baseline to precede WI-5344 and forbids absorption of descendant changes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserve the baseline and descendant lifecycles as distinct governed artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires both candidates and all evidence to remain inside `E:\GT-KB`.

## Prior Deliberations

- `INTAKE-c5792b0c` - confirmed the governed Git lifecycle and bounded dispatcher-coordination requirement implemented by this acceptance family.
- `DELIB-20260710-GTKB-MODERNIZATION-GIT-LIFECYCLE-CHARTER` - established the frozen Git Lifecycle modernization project and acceptance family.
- `DELIB-202666274` - authorizes required modernization blocker and false-closure repairs at project scope while preserving review and mechanical-operation gates.

## Owner Decisions / Input

`DELIB-202666274` and active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE`
authorize this independently reviewed baseline stabilization. No new owner
decision is required for filing or exact-byte review. This proposal does not
authorize staging, commit, branch/ref mutation, merge, push, release,
deployment, dispatcher/TAFE mutation, harness mutation, credential lifecycle,
destructive cleanup, or external-system mutation.

## Requirement Sufficiency

Existing requirements sufficient. The frozen 26-assertion contract, the two
exact candidate files, the direct 26/26 PASS result, and current Git Lifecycle
specifications completely define this baseline. No new or revised requirement
is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "config/governance/modernization-release-candidate.json",
  "primary_route": "independently reviewed exact-byte baseline adoption before WI-5344 repair",
  "before_behavior": "two complete frozen acceptance carriers are untracked and descendant repair would absorb their bytes",
  "after_behavior": "the exact baseline exists in HEAD and WI-5344 can own only its later timeout/process-tree hunks",
  "self_descriptive_naming": "WI-5354 identifies frozen Git-lifecycle acceptance baseline stabilization",
  "obsolete_guidance_disposition": "the known 180/900 nested-timeout defect remains visible and assigned to WI-5344",
  "history_preservation": "baseline adoption does not rewrite or falsely close the WI-5344 defect lifecycle",
  "baseline": {
    "head_presence": "both paths absent",
    "checker_runtime_seconds": 322.23,
    "checker_assertions": "26 of 26 PASS"
  },
  "expected_result": {
    "head_presence": "both exact hashes present",
    "descendant_scope": "no WI-5344 timeout or process-tree change included"
  },
  "rollback": {
    "instructions": "revert only the exact two-file baseline transaction under separately authorized Git mechanics",
    "test": "rerun the direct checker and exact hash inventory"
  },
  "hard_invariants": [
    "all 26 assertion definitions remain",
    "aggregate capability and status semantics remain",
    "no real Git, dispatcher, or harness mutation occurs during verification",
    "no unrelated worktree byte is absorbed"
  ],
  "fail_closed_conditions": [
    "either candidate hash changes",
    "a third path enters scope",
    "any assertion is removed or weakened",
    "exact Git mechanical authority is absent"
  ],
  "essential_context_preservation": "the full frozen Git lifecycle and all 26 evidence-bearing assertions remain intact"
}
```

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`; `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`; `DCL-GIT-BRANCH-BINDING-PROMOTION-001`; `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_git_lifecycle.py --json` | Exit 0; capability `CAP-GIT-LIFECYCLE`; aggregate `PASS`; exactly `GIT-LIFECYCLE-A1` through `A26`, all PASS with evidence. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-WORK-TREE-HYGIENE-001` | Exact two-file SHA-256/byte inventory plus complete-file review | Both hashes and sizes match; no third path or WI-5344 hunk is included; no assertion is weakened. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mandatory preflights, exact matching claim/start, implementation report, and independent whole-file review | No missing required/advisory specs or blocking clause gaps; exact-byte adoption is independently VERIFIED. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Confirm the wrapper still has its original 180-second marker and 900-second child timeout at the baseline hash | The known WI-5344 defect is preserved, not silently repaired or absorbed; WI-5344 remains a later descendant. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5354/WI-5344 histories and numbered proposal/report/verdict chains | Baseline and descendant repair remain independently traceable. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and exact path inventory | `CLAUSE-IN-ROOT` passes and every dependency resolves under `E:\GT-KB`. |

## Risk / Rollback

Whole-file adoption is intentional only because both candidates are absent from
`HEAD`. The principal risk is misattributing later bytes or hiding the known
WI-5344 defect inside the baseline. Independent review must inspect both
complete files, bind both hashes, rerun the direct checker, and fail closed on
drift. No source or test edit is proposed. Rollback is limited to the exact
two-file baseline transaction under separate Git authority; no broad reset,
cleanup, branch, index, or unrelated operation is permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5354-git-lifecycle-acceptance-baseline`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - restores the missing committed carriers for the pre-existing frozen
Git-lifecycle acceptance contract without changing behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
