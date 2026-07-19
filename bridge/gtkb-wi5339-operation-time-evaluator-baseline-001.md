NEW
::init gtkb lo
::open build

# WI-5339 Operation-Time Evaluator Canonical Baseline

bridge_kind: prime_proposal
Document: gtkb-wi5339-operation-time-evaluator-baseline
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-18T17:24:44Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5339

target_paths: ["groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Create the complete canonical package module at
`groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
from the tracked operation-time DCL, taxonomy, and executable assertions. The
committed source tree currently contains tests that import this module and a
tracked taxonomy that defines its classifications, but the module itself is
absent from `HEAD`. That omission makes clean-checkout Authority Foundations
acceptance impossible.

This is a one-file baseline-stabilization scope. Because the target is absent
from the parent commit, the eventual finalizer must include the complete file
reviewed by Loyal Opposition. It must not stage any other path, absorb any
unrelated working-copy content, alter the frozen modernization contract digest,
or mutate dispatcher, TAFE, harness, credential, deployment, release, or
external-system state.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - defines the
  evaluator inputs, precedence, evidence, currentness, and nine executable
  assertion families implemented by the target module.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires current project
  authorization coverage before this protected source artifact is created.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires the evaluator
  and its governed taxonomy to exist in a clean checkout and remain directly
  executable.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires this repair to preserve
  bridge, dispatcher, harness, and existing legitimate authorization behavior.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent
  verification against the DCL-derived focused and acceptance tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - keeps proposal review, claim/start, report,
  and independent verification on the governed bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds this proposal
  to the exact requirements and verification below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this one-file
  repair to its active project authorization and WI-5339.
- `GOV-STANDING-BACKLOG-001` - recognizes WI-5339 as the P0 hygiene blocker
  created for the discovered clean-checkout dependency omission.

## Prior Deliberations

- `DELIB-202666081` - established the Gate 1.25 operation-time enforcement
  correction that this canonical module must implement.
- `DELIB-202666082` - approved formalization of
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`.
- `DELIB-202666274` - provides the active project-level modernization assurance
  authority while preserving bridge GO, claim/start, verification, and
  operation restrictions.

## Owner Decisions / Input

No new owner decision is required. The owner authorized the full modernization
program at project scope, and
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
is active under `DELIB-202666274`. This proposal still grants no implementation
or Git authority by itself: independent GO, a matching work-intent claim,
implementation-start authority, independent VERIFIED, and exact mechanical
finalization authority remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient. The operation-time DCL defines the complete
evaluator contract, the tracked taxonomy defines the registered operations,
classes, and aliases, and the committed focused, fresh-worker, and hard-invariant
tests provide executable acceptance. No requirement or frozen-contract amendment
is proposed.

## Spec-Derived Verification Plan

1. `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`,
   `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`, and
   `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

   ```text
   groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short
   ```

   Expected: all tests pass from the reviewed working tree and again from the
   exact finalized commit.

2. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`:

   ```text
   groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py platform_tests/scripts/test_modernization_hard_invariants.py -q --tb=short
   ```

   Expected: fresh-host packaging, taxonomy isolation, legitimate bounded
   authorization, and hard fail-closed behavior all pass without dispatcher or
   harness configuration changes.

3. Frozen release-candidate contract preservation:

   ```text
   groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_release_candidate.py validate --json
   ```

   Expected: validation passes and the frozen digest remains
   `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`.

4. Canonical clean-checkout presence:

   ```text
   git ls-tree -r --name-only HEAD -- config/governance/project-authorization-operation-taxonomy.toml groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py
   ```

   Expected after exact finalization: both paths are present in the finalized
   commit.

5. Source quality:

   ```text
   groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
   groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
   ```

   Expected: both commands pass.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5339; DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001; DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
  "primary_route": "governed bridge GO, matching claim/start, independent VERIFIED, and exact one-file finalization",
  "before_behavior": "The committed tests and taxonomy require an operation-time evaluator module that is absent from HEAD, so clean-checkout Authority Foundations acceptance cannot run.",
  "after_behavior": "A canonical packaged evaluator enforces current PAUTH operation and target bounds deterministically at the required gates.",
  "self_descriptive_naming": "The package module, evaluator ID, taxonomy, decisions, reason codes, and tests name the authorization operation-time behavior directly.",
  "obsolete_guidance_disposition": "No guidance, compatibility route, or historical bridge record is retired by this one-file repair.",
  "history_preservation": "The numbered bridge chain and Git history remain append-only; no existing commit or frozen contract record is rewritten.",
  "baseline": {
    "parent_head_has_taxonomy": true,
    "parent_head_has_focused_tests": true,
    "parent_head_has_target_module": false,
    "frozen_contract_sha256": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240"
  },
  "expected_result": {
    "target_module_tracked": true,
    "focused_authority_tests": "pass",
    "fresh_worker_and_hard_invariants": "pass",
    "frozen_contract_sha256": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240"
  },
  "rollback": {
    "instructions": "Under separate exact authority, revert only the one-file finalization commit and retain the bridge audit chain.",
    "verification": "Rerun the focused authority tests, fresh-worker and hard-invariant tests, and frozen release-candidate validator."
  },
  "hard_invariants": [
    "The target module implements only the tracked DCL and taxonomy contract.",
    "The proposal cannot broaden the active PAUTH or reviewed target path.",
    "No dispatcher, TAFE, harness, credential, deployment, release, or external-system state is mutated.",
    "No unrelated working-copy path is staged or committed.",
    "The frozen modernization contract digest does not change."
  ],
  "fail_closed_conditions": [
    "The active project authorization, independent GO, claim, or implementation-start evidence is missing or stale.",
    "The target path changes under concurrent ownership before implementation or finalization.",
    "The complete reviewed file cannot be finalized without including any unrelated path or unreviewed bytes.",
    "Any required focused, fresh-worker, hard-invariant, quality, or frozen-contract check fails."
  ],
  "essential_context_preservation": "The repair preserves project authority, exact target ownership, DCL semantics, tracked taxonomy, frozen acceptance digest, independent review, and append-only audit history."
}
```

## Risk / Rollback

The evaluator sits on protected authorization boundaries, so a permissive
classification or stale-envelope mistake could authorize work outside the
active PAUTH. Independent review must inspect every allow and deny path against
the DCL precedence rules, and verification must include legitimate bounded
behavior as well as fail-closed cases.

The target is a complete new file relative to the parent commit. Implementation
and finalization must fail closed on any concurrent path change or inability to
attribute the complete reviewed file to this scope. Rollback is a separately
authorized one-commit revert of only this file, followed by the full verification
plan; bridge and audit history remain intact.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5339-operation-time-evaluator-baseline`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the change restores a required canonical package dependency omitted
from the committed Authority Foundations implementation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
