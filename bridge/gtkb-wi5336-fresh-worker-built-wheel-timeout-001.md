NEW

# Bound the Built-Wheel Fresh-Worker Proof Realistically

bridge_kind: prime_proposal
Document: gtkb-wi5336-fresh-worker-built-wheel-timeout
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T19:49:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5336

target_paths: ["platform_tests/scripts/test_modernization_fresh_worker.py"]

implementation_scope: test infrastructure
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add exactly `@pytest.mark.timeout(180)` to
`test_built_wheel_assembles_context_without_source_tree_or_root_config`. The
test intentionally builds the package wheel, creates an isolated virtual
environment, installs the wheel, and proves packaged context assembly without
the source tree or repository-root configuration. The repository-wide
30-second pytest default interrupts this legitimate multi-process proof.

Current unchanged evidence is load-sensitive. The exact test passed three
times with a diagnostic 180-second cap at pytest times 53.42, 30.36, and 51.96
seconds (measured wall times 55.76, 31.63, and 53.50 seconds). The complete
four-test file passed unchanged in 51.36 seconds under diagnostic
`--timeout=600`. A test-local 180-second bound leaves over three times the
slowest current measured wall time, retains deterministic hang detection, and
remains far below the frozen `AT-FRESH-WORKER` 900-second outer limit.

Implementation is not startable until WI-5350 has independently stabilized the
exact 17,076-byte WI-5155 baseline in `HEAD` at SHA-256
`8A3C32384031A272070C304FCA99634C0E5360C16841475E88FF7A5756C1751A`.
WI-5336 may then add only the one decorator hunk. It must not adopt or replace
the complete currently untracked file.

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - governs deterministic context assembly, seven-category manifests, failure/recovery behavior, and role/activity isolation exercised by the test.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` - governs the six-activity context-loading surfaces covered by the fresh-worker candidate.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - requires executable release-readiness evidence and regression visibility.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - prohibits reducing test scope, weakening assertions, raising global timeouts, or impairing harness dispatchability.
- `GOV-WORK-TREE-HYGIENE-001` - requires the descendant hunk to wait for and build on the separately owned WI-5350 baseline.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the exact one-path proposal/GO/claim/start/report/VERIFIED lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the complete governing specification set in this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5336 to the active Assurance project PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires repeated exact-command evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - requires WI-5350 baseline finalization before this hunk and forbids whole-file absorption.
- `GOV-STANDING-BACKLOG-001` - keeps the timeout defect visible until exact implementation and repeated evidence are verified.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires all test, baseline, and evidence paths to remain inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserve the separate WI-5350 baseline and WI-5336 descendant lifecycles.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-READINESS-AUTHORIZATION` - authorized the Assurance project and fresh-worker evaluation scope.
- `DELIB-202666274` - authorizes required modernization blocker repairs at project scope while retaining independent review and mechanical-operation gates.

## Owner Decisions / Input

`DELIB-202666274` and active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
authorize the bounded test repair. No new owner decision is required. This
proposal does not request staging, commit, push, release, deployment,
dispatcher/TAFE mutation, harness mutation or eligibility change, credential
lifecycle, destructive cleanup, or external-system mutation.

## Requirement Sufficiency

Existing requirements sufficient. The frozen 900-second activity ceiling, the
unchanged multi-process proof, three bounded repetitions, and current
non-impairment contract fully specify the repair. No new or revised requirement
is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "config/governance/modernization-release-candidate.json",
  "primary_route": "one test-local pytest timeout marker after WI-5350 baseline stabilization",
  "before_behavior": "the global 30-second timeout interrupts a legitimate isolated wheel build, environment creation, install, and probe",
  "after_behavior": "the complete proof runs unchanged under a 180-second test-local hang bound",
  "self_descriptive_naming": "the existing test name continues to state the complete isolation behavior",
  "obsolete_guidance_disposition": "the stale 30-second effective bound is superseded only for this test by current repeated timing evidence",
  "history_preservation": "WI-5350 owns the exact baseline and WI-5336 owns only the later decorator hunk",
  "baseline": {
    "global_timeout_seconds": 30,
    "three_pytest_seconds": [53.42, 30.36, 51.96],
    "three_wall_seconds": [55.76, 31.63, 53.50]
  },
  "expected_result": {
    "local_timeout_seconds": 180,
    "frozen_outer_timeout_seconds": 900,
    "fresh_worker_tests": "4 passes in three bounded repetitions"
  },
  "rollback": {
    "instructions": "remove only the WI-5336 decorator after separately proving a lower reliable bound",
    "test": "rerun the exact built-wheel node and frozen AT-FRESH-WORKER activity"
  },
  "hard_invariants": [
    "wheel build and isolated environment creation remain",
    "source-tree and root-config absence assertions remain",
    "packaged resource and context assembly assertions remain",
    "global timeout and every harness eligibility remain unchanged"
  ],
  "fail_closed_conditions": [
    "WI-5350 baseline absent from HEAD",
    "whole-file replacement proposed",
    "subprocess or assertion behavior changed",
    "test-local timeout at or above the frozen outer ceiling"
  ],
  "essential_context_preservation": "all current package isolation, resource assembly, fallback, role, and activity assertions remain exercised"
}
```

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001`; `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`; `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Exact frozen `AT-FRESH-WORKER`: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short` | All four tests pass with a normal summary and exit 0; the built-wheel proof completes without an external override. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the exact built-wheel node three times under normal concurrent workstation load, using no command-line timeout override after implementation | Three passes; no assertion, subprocess, package isolation, global timeout, console visibility, or harness eligibility changes. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Verify the WI-5350 hash exists in `HEAD` before start; inspect the exact hunk after implementation | Exactly one decorator is added atop the committed baseline; no foreign byte is adopted or lost. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mandatory preflights, matching claim/start, report, and independent review | No missing required/advisory specs or blocking clause gaps; repeated observed evidence is mapped before VERIFIED. |
| `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5336 history and numbered lifecycle | WI-5336 remains open until the exact hunk is independently VERIFIED and finalized after WI-5350. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and path inventory | `CLAUSE-IN-ROOT` passes and all dependencies resolve under `E:\GT-KB`. |

## Risk / Rollback

An excessively small timeout recreates false failures under expected load; an
unbounded or outer-equal timeout weakens hang detection. The 180-second marker
provides over three times the current slowest measured wall time and leaves 720
seconds inside the frozen outer activity budget. Implementation must be one
decorator after WI-5350 is present in `HEAD`. Rollback is removal of that one
line; no global config, subprocess, harness, process, or baseline operation is
permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5336-fresh-worker-built-wheel-timeout`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - corrects an unrealistic test-local time budget without changing
production behavior or test assertions.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
