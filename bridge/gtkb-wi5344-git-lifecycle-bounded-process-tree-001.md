NEW

# Bound the Frozen Git-Lifecycle Checker and Reap Its Process Tree

bridge_kind: prime_proposal
Document: gtkb-wi5344-git-lifecycle-bounded-process-tree
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T20:06:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5344

target_paths: ["platform_tests/scripts/test_modernization_git_lifecycle.py"]

implementation_scope: frozen acceptance test runtime
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair only the frozen Git-lifecycle black-box wrapper after WI-5354 has placed
its exact baseline in `HEAD`:

1. replace `@pytest.mark.timeout(180)` with a 750-second test-local wrapper
   bound;
2. replace `subprocess.run(..., timeout=900)` with `Popen.communicate()` under a
   600-second child bound;
3. launch the checker in a hidden/new process group using the existing
   `scripts.windows_subprocess.hidden_process_popen_kwargs` helper;
4. on child timeout, call the existing and integration-tested
   `scripts.run_with_status._terminate_process_tree` helper, then fail with
   bounded diagnostic output; and
5. add a fast monkeypatched timeout regression proving that the wrapper invokes
   tree termination and never treats a timeout as PASS.

Current direct evidence shows why both bounds are required. The unchanged
checker completed in 322.23 seconds with capability `CAP-GIT-LIFECYCLE`, status
`PASS`, and 26/26 required assertions passing. The present 180-second wrapper
therefore interrupts legitimate work, while its 900-second child timeout is
larger than the wrapper and equal to the frozen activity ceiling. The proposed
600/750/900 child-wrapper-activity ordering leaves 277.77 seconds above the
measured checker runtime, 150 seconds for timeout cleanup/reporting, and 150
seconds of external activity margin.

Implementation is not startable until WI-5354 has independently stabilized
the exact checker and wrapper baseline in `HEAD`. This proposal changes only
the wrapper file. It does not modify the checker, shared process helpers,
semantic runner, subprocess internals, harness configuration, eligibility, or
dispatcher behavior.

## Specification Links

- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - governs the production Git lifecycle modeled by the checker.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - requires all lifecycle outcomes and fail-closed behavior to remain covered.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - governs the 26 branch-binding, scoped-commit, integration, and promotion assertions.
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` - governs released-state and promotion authority exercised by the checker.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - prohibits skipping assertions, reducing checker scope, removing time bounds, opening console windows, or impairing harness dispatchability.
- `GOV-WORK-TREE-HYGIENE-001` - requires WI-5354 baseline finalization before this one-file descendant hunk.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the exact proposal/GO/claim/start/report/VERIFIED lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the complete governing specification set in this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5344 to the active Git Lifecycle project PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires repeated frozen-command and forced-timeout evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - requires WI-5354 first and keeps WI-5261's broader process-wrapper work separate.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserve the baseline, timeout repair, and broader WI-5261 lifecycles independently.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires every implementation and evidence path to remain inside `E:\GT-KB`.

## Prior Deliberations

- `INTAKE-c5792b0c` - confirmed the governed Git lifecycle and bounded dispatcher-coordination requirement exercised by the checker.
- `DELIB-20260710-GTKB-MODERNIZATION-GIT-LIFECYCLE-CHARTER` - established the frozen Git Lifecycle project and acceptance family.
- `DELIB-202666274` - authorizes required modernization blocker repairs at project scope while preserving independent review and mechanical-operation gates.

## Owner Decisions / Input

`DELIB-202666274` and active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE`
authorize the bounded test repair. No new owner decision is required. This
proposal does not authorize staging, commit, branch/ref mutation, merge, push,
release, deployment, dispatcher/TAFE mutation, harness mutation or eligibility
change, credential lifecycle, destructive cleanup, or external-system
mutation.

## Requirement Sufficiency

Existing requirements sufficient. The frozen 900-second activity ceiling, the
26-assertion checker contract, measured 322.23-second runtime, existing tested
tree-termination helper, and current non-impairment requirements fully specify
the repair. No new or revised requirement is needed.

## Cross-Harness Disposition

| Surface | Disposition |
|---|---|
| Claude, Codex, Cursor, Antigravity, Ollama, OpenRouter, Alibaba | No harness configuration, role, eligibility, dispatch, or worker-runtime change. Every harness executes the same repository pytest wrapper when running the frozen activity. |
| Windows | Checker child uses the existing hidden/new-process-group helper; timeout reuses the existing `taskkill /T` tree terminator. No visible console is introduced. |
| POSIX | Checker child starts a new session; timeout reuses the existing process-group termination path. |
| TAFE/bridge | Proposal publication and independent review only. No routing or dispatcher configuration is changed by implementation. |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "config/governance/modernization-release-candidate.json",
  "primary_route": "one frozen-wrapper repair reusing existing hidden-process and process-tree helpers",
  "before_behavior": "a 180-second wrapper interrupts a legitimate checker while a 900-second child timeout cannot govern first",
  "after_behavior": "the checker has nested 600-second child, 750-second wrapper, and 900-second frozen activity bounds with complete tree cleanup",
  "self_descriptive_naming": "named child and wrapper timeout constants make the nested envelope explicit",
  "obsolete_guidance_disposition": "the inconsistent 180/900 ordering is replaced by current measured bounds",
  "history_preservation": "WI-5354 owns baseline bytes, WI-5344 owns this wrapper repair, and WI-5261 retains broader semantic-runner work",
  "baseline": {
    "checker_runtime_seconds": 322.23,
    "wrapper_timeout_seconds": 180,
    "child_timeout_seconds": 900
  },
  "expected_result": {
    "child_timeout_seconds": 600,
    "wrapper_timeout_seconds": 750,
    "activity_timeout_seconds": 900,
    "assertions": "26 of 26 PASS"
  },
  "rollback": {
    "instructions": "revert only the WI-5344 wrapper hunks after separately proving another bounded envelope",
    "test": "rerun the timeout-path regression and exact frozen activity"
  },
  "hard_invariants": [
    "all 26 checker assertions remain required",
    "timeout remains failure",
    "complete child tree is terminated on timeout",
    "no console window or harness eligibility change is introduced"
  ],
  "fail_closed_conditions": [
    "WI-5354 baseline absent from HEAD",
    "checker or shared helper modification proposed",
    "child timeout not strictly below wrapper and activity bounds",
    "timeout reported as PASS or without tree termination"
  ],
  "essential_context_preservation": "the complete frozen Git-lifecycle checker, evidence payload, and all assertion diagnostics remain intact"
}
```

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`; `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`; `DCL-GIT-BRANCH-BINDING-PROMOTION-001`; `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` | Exact frozen `AT-GIT-LIFECYCLE`: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short` | Wrapper and timeout-path regression pass; checker reports `CAP-GIT-LIFECYCLE`, aggregate PASS, and exactly A1-A26 PASS with evidence. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the exact frozen command three times under normal concurrent workstation load | Three bounded passes; all 26 assertions remain; no leaked descendants, visible console, global timeout, harness eligibility, or dispatcher change. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Verify both WI-5354 hashes exist in `HEAD` before start; inspect the exact descendant diff | Only `platform_tests/scripts/test_modernization_git_lifecycle.py` changes; no baseline or WI-5261 byte is absorbed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mandatory preflights, matching claim/start, implementation report, and independent review | No missing required/advisory specs or blocking clause gaps; repeated evidence is mapped before VERIFIED. |
| Process-tree fail-closed requirement | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -k timeout -q --tb=short` and `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py::test_terminate_process_tree_reaps_grandchild_on_windows -q --tb=short` on Windows | Forced wrapper timeout invokes tree termination and fails; existing integration proves both child and grandchild are gone. POSIX review confirms `start_new_session=True` plus existing `killpg` path. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5354/WI-5344/WI-5261 histories and numbered lifecycles | Baseline, immediate RC repair, and broader process-wrapper work remain distinct and traceable. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and exact path inventory | `CLAUSE-IN-ROOT` passes and all dependencies resolve under `E:\GT-KB`. |

## Risk / Rollback

An undersized child bound recreates false failures; an activity-equal child
bound reverses control; a bare `Popen.kill()` leaks descendants. The proposed
600/750/900 ordering is based on a 322.23-second complete run and reuses an
existing tree terminator with a real grandchild-reaping regression. The only
implementation target is the wrapper after WI-5354 is in `HEAD`. Rollback is
limited to the WI-5344 wrapper hunks; no checker, shared helper, harness,
dispatcher, global timeout, branch, index, or unrelated operation is permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5344-git-lifecycle-bounded-process-tree`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - corrects the frozen acceptance runtime envelope and timeout cleanup
without changing production Git behavior or checker assertions.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
