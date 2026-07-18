NEW

# gtkb-wi5415-doctor-registry-dynamic-discovery (Slice 1) - Preserve extensible doctor-check discovery

bridge_kind: prime_proposal
Document: gtkb-wi5415-doctor-registry-dynamic-discovery
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5415

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py", "platform_tests/scripts/test_check_gt_cli_availability.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Reject the current foreign explicit-loader hunk in
`groundtruth_kb.project.checks`. Restore that source file to its committed
ADR-compliant `pkgutil.iter_modules` discovery implementation, then add one
extensibility regression to the existing GT CLI availability registry test
surface. The regression creates a synthetic future check module under the
in-root pytest temporary directory and proves `get_registered_checks()` imports
and registers it without changing a hardcoded module list.

The current source candidate has Git blob
`d7a63ead3de70646b3e122652a8fb2bc8bbdcb3c`; the committed dynamic baseline is
blob `2740009d40e523fe66678b9196ef20aca05ea40f`. The rejected semantic patch ID is
`87b7888b6e9160b75a73aae72057ef2424debe53`. Existing focused tests pass
`22/22`, demonstrating compatibility with today's two modules but not the
extensibility required by `ADR-REGISTRY-DISCOVERY-001`.

## Specification Links

- `ADR-REGISTRY-DISCOVERY-001` - requires dynamic import and discovery of
  registered check modules and explicitly rejects hardcoded submodule dispatch.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before either
  protected target changes and independent VERIFIED before completion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the
  implementation and tests to trace to the registry-discovery decision.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit
  PAUTH, project, work-item, target-path, and slice linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent
  execution of the ADR-derived extensibility regression.
- `GOV-STANDING-BACKLOG-001` - governs WI-5415 as a visible hygiene defect
  rather than silently accepting or discarding foreign source bytes.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact ownership and a reviewed
  disposition for the dirty source hunk.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires current checks to keep
  working while future check modules remain discoverable.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires the source
  disposition and regression evidence to be current and reproducible.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires the synthetic
  check-module fixture and every live dependency to remain within the GT-KB
  project root; no external application or archive path is allowed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - require durable traceability from the
  discovered defect through proposal, implementation evidence, verification,
  and final disposition.

## Prior Deliberations

_No prior deliberations: the current, implemented
`ADR-REGISTRY-DISCOVERY-001` already records the relevant design choice and
rejected hardcoded-dispatch alternative. WI-5415 applies that decision to a
newly discovered dirty hunk without amending it._

## Owner Decisions / Input

No new owner decision is required. The owner authorized the modernization
program, required every dirty path to receive exact ownership and disposition,
and directed discovered defects to become hygiene work items. Active
project-wide authority is
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE`.
Implementation remains gated on an independent GO plus matching claim and
implementation-start authority.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-REGISTRY-DISCOVERY-001` is explicit:
dynamic check-module discovery is the selected architecture and hardcoded
submodule dispatch is rejected. This proposal implements that existing choice;
it does not amend or supersede the ADR.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5415 dirty-tree inventory plus ADR-REGISTRY-DISCOVERY-001",
  "canonical_authority": "ADR-REGISTRY-DISCOVERY-001 and the committed dynamic-discovery source baseline",
  "primary_route": "groundtruth_kb.project.checks.get_registered_checks",
  "before_behavior": "the dirty source imports exactly two named modules, so a future registered check is silently absent until the tuple is manually edited",
  "after_behavior": "the registry discovers every module on the checks package path and a synthetic future module proves extension without dispatcher edits",
  "self_descriptive_naming": "get_registered_checks continues to describe discovery rather than a fixed loader list",
  "obsolete_guidance_disposition": "the uncommitted hardcoded-loader hunk is rejected under governed evidence; the implemented ADR remains current",
  "history_preservation": "pre-start current and HEAD blob IDs plus the rejected stable patch ID are recorded; no committed history is rewritten",
  "baseline": "22 existing focused checks pass while no test distinguishes hardcoded loading from dynamic discovery",
  "expected_result": "23 focused tests pass, including a synthetic future-module discovery regression, and the source blob matches the committed dynamic baseline",
  "rollback": "restore the independently recorded two-path pre-start snapshot only through a new governed transaction",
  "hard_invariants": [
    "existing gt_cli_availability and stale_test_slots checks remain registered",
    "new check modules require no central loader-list edit",
    "module import failures remain visible rather than silently skipped",
    "all test dependencies and temporary modules remain inside the GT-KB root",
    "no doctor command, dispatcher, TAFE, harness, or database behavior changes"
  ],
  "fail_closed_conditions": [
    "a hardcoded module-name list remains",
    "the synthetic future module is not registered",
    "any existing focused test fails",
    "the source disposition differs from the committed dynamic baseline without separate review",
    "the test writes or imports a live dependency outside E:/GT-KB"
  ],
  "essential_context_preservation": "the decorator registry, public get_registered_checks API, current check modules, and on-touch modularization architecture remain unchanged"
}
```

## Spec-Derived Verification Plan

1. `ADR-REGISTRY-DISCOVERY-001`,
   `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`, and
   `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`, under
   `ADR-ISOLATION-APPLICATION-PLACEMENT-001`:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_stale_test_slots.py platform_tests/scripts/test_check_gt_cli_availability.py platform_tests/scripts/test_fab08_slot_leak_fix.py -q --tb=short
```

Expected: `23 passed`, including a new test that places a synthetic module on a
temporary checks-package path, invokes the production registry API, and
observes its registered check without editing production module names.

2. Exact source disposition and scope:

```text
git hash-object -- groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py
git rev-parse HEAD:groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py
git diff -- groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py platform_tests/scripts/test_check_gt_cli_availability.py
```

Expected: the two source blob IDs are both
`2740009d40e523fe66678b9196ef20aca05ea40f`; the only remaining implementation
diff is the bounded extensibility regression in the test target.

3. Bridge and lifecycle specifications:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5415-doctor-registry-dynamic-discovery --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5415-doctor-registry-dynamic-discovery
```

Expected: no missing required or advisory specifications and zero blocking
clause gaps. Independent Loyal Opposition must review the source restoration,
test implementation, command evidence, and exact target hashes.

4. Static checks:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py platform_tests/scripts/test_check_gt_cli_availability.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py platform_tests/scripts/test_check_gt_cli_availability.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py platform_tests/scripts/test_check_gt_cli_availability.py
```

Expected: all checks pass.

## Risk / Rollback

Dynamic import has the existing ADR-documented startup overhead and surfaces a
bad future module import. Those are intentional properties of the selected
architecture. The new regression isolates its synthetic module and registry
state so it cannot pollute neighboring tests. Rollback requires a new governed
two-path snapshot restoration; no unreviewed `git checkout` or whole-tree
cleanup is permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5415-doctor-registry-dynamic-discovery`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - remove a worktree source regression against the implemented ADR and
add the missing behavior-level extensibility guard.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
