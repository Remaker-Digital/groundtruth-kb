NEW

# Bound the full loading-graph repeatability test realistically

bridge_kind: prime_proposal
Document: gtkb-wi5335-loading-graph-repeatability-timeout
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T19:27:43Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5335

target_paths: ["platform_tests/scripts/test_modernization_artifact_decontamination.py"]

implementation_scope: test infrastructure
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add exactly `@pytest.mark.timeout(600)` to
`test_effective_loading_graph_is_repeatable`. The frozen test intentionally
builds the complete live repository loading graph twice, compares canonical
report bytes, and asserts non-empty entrypoints/load edges. The repository-wide
30-second pytest default interrupts the second scan and makes
`AT-ARTIFACT-LIFECYCLE` fail without contradicting any lifecycle behavior.

Measured evidence is load-sensitive: an earlier unchanged full activity passed
in 76.01 seconds with `--timeout=180`; on 2026-07-16 one live graph build under
normal concurrent harness load took 121.040 seconds (44 entrypoints, 284 Python
modules, 1,860 import edges, 78 load edges, zero unresolved imports), so two
scans have a measured floor above 242 seconds. The candidate baseline then
completed all 24 tests in 67.21 seconds with `--timeout=600`. A test-local 600s
bound preserves real hang detection, provides margin under expected load, and
remains below the frozen activity's 900s outer ceiling.

Implementation is not startable until WI-5347 has independently stabilized the
exact three-file WI-5142 baseline in `HEAD`. WI-5335 may then add only the one
decorator hunk. It must not adopt the whole currently untracked test file.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — governs the complete repository lifecycle/loading-graph evidence that the test exercises.
- `DCL-SUPERSEDED-SOT-LEAKAGE-001` — requires both complete scans to continue proving that superseded authority does not leak into effective loading.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — prohibits fixing the timeout by reducing scan scope, skipping the second pass, weakening assertions, or impairing harness dispatchability.
- `GOV-WORK-TREE-HYGIENE-001` — requires the descendant hunk to wait for and build on the separately owned WI-5347 baseline.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the exact one-path proposal/GO/claim/start/report/VERIFIED lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires the complete governing specification set in this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5335 to the active Artifact Decontamination project PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires repeated exact frozen-command evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — requires WI-5347 baseline finalization before this hunk and forbids whole-file absorption.
- `GOV-STANDING-BACKLOG-001` — keeps the timeout defect visible until exact implementation and repeated acceptance evidence are verified.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — requires all test, baseline, and evidence paths to remain inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserve the separate WI-5347 baseline and WI-5335 descendant lifecycles.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-AUTHORIZATION` — authorized the full WI-5142 Artifact Decontamination behavior that this test must continue exercising unchanged.
- `DELIB-202666274` — authorizes all required modernization blocker repairs at project scope while retaining independent and mechanical-operation gates.

## Owner Decisions / Input

`DELIB-202666274` and active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE`
authorize the bounded test repair. No new owner decision is required. This
proposal does not request staging, commit, push, release, deployment,
dispatcher/TAFE mutation, harness mutation or eligibility change, credential
lifecycle, destructive cleanup, or external-system mutation.

## Requirement Sufficiency

Existing requirements sufficient. The frozen 900-second activity ceiling, the
complete two-scan test, measured timings, and current non-impairment contract
fully specify the repair. No new or revised requirement is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "config/governance/modernization-release-candidate.json",
  "primary_route": "one test-local pytest timeout marker after WI-5347 baseline stabilization",
  "before_behavior": "the global 30-second bound interrupts an intentional second full loading-graph scan",
  "after_behavior": "both full scans and all graph assertions complete under a 600-second test-local hang bound",
  "self_descriptive_naming": "test_effective_loading_graph_is_repeatable remains the unchanged behavior contract",
  "obsolete_guidance_disposition": "the stale 180-second recommendation is superseded by current concurrent-load measurement",
  "history_preservation": "WI-5347 owns the baseline and WI-5335 owns only the later decorator hunk",
  "baseline": {
    "global_timeout_seconds": 30,
    "single_scan_seconds_under_load": 121.04,
    "two_scan_floor_seconds": 242.08
  },
  "expected_result": {
    "local_timeout_seconds": 600,
    "frozen_outer_timeout_seconds": 900,
    "tests": "24 passes in three bounded repetitions"
  },
  "rollback": {
    "instructions": "remove only the WI-5335 decorator after separately proving a faster reliable bound",
    "test": "rerun the exact frozen activity three times"
  },
  "hard_invariants": [
    "both complete scans remain",
    "canonical byte equality remains",
    "entrypoint and load-edge assertions remain",
    "global timeout and harness eligibility remain unchanged"
  ],
  "fail_closed_conditions": [
    "WI-5347 baseline absent from HEAD",
    "whole-file replacement proposed",
    "scan or assertion weakening",
    "test-local timeout at or above the frozen outer ceiling"
  ],
  "essential_context_preservation": "complete repository loading authority and supersession evidence remains exercised"
}
```

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`; `DCL-SUPERSEDED-SOT-LEAKAGE-001` | Exact frozen `AT-ARTIFACT-LIFECYCLE`: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_artifact_decontamination.py -q --tb=short` | All 24 tests pass with a normal summary and exit 0; both full scans execute. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the exact frozen command three times under normal concurrent harness load | Three passes; no assertion removed, scan reduced, process leaked, console storm introduced, or harness eligibility changed. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Verify the WI-5347 three-file hashes exist in `HEAD` before start; inspect hunk diff after implementation | Exactly one decorator is added atop the committed baseline; no foreign byte is adopted or lost. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mandatory preflights, matching claim/start, report, and independent review | No missing required/advisory specs or blocking clause gaps; observed repeated evidence is mapped before VERIFIED. |
| `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5335 history and numbered lifecycle | WI-5335 remains open until the exact hunk is independently VERIFIED and finalized after WI-5347. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and path inventory | `CLAUSE-IN-ROOT` passes and all dependencies resolve under `E:\GT-KB`. |

## Risk / Rollback

An excessively small local timeout recreates false failures under expected
concurrent load; an unbounded or outer-equal timeout weakens hang detection. A
600-second marker gives over 2x current measured two-scan margin and leaves 300
seconds inside the frozen outer activity bound. The implementation must be one
decorator after WI-5347 is present in `HEAD`. Rollback is removal of that one
line; no global config, scanner, harness, process, or baseline file operation is
permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5335-loading-graph-repeatability-timeout`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` — corrects an unrealistic test-local time budget without changing
production or assertion behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
