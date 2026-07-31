NEW

# gtkb-wi5407-installed-wheel-source-exclusion (Slice 1) - Distinguish an in-root venv from the source checkout

bridge_kind: prime_proposal
Document: gtkb-wi5407-installed-wheel-source-exclusion
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5407

target_paths: ["platform_tests/scripts/test_modernization_fresh_worker.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Replace one invalid lexical assertion in the frozen fresh-worker acceptance
test. The test already proves the imported `groundtruth_kb` module resolves
inside the newly created isolated venv. Keep that assertion and replace
`not module.is_relative_to(REPO_ROOT)` with exact exclusion of the checkout
source directory at `BUILD_PROJECT / "src"`.

The current test fails only because the canonical pytest basetemp places the
isolated venv beneath `E:/GT-KB/.pytest-tmp`, making every valid wheel install
lexically relative to `REPO_ROOT`. The forced in-root node currently reports
`1 failed` after successfully building, installing, importing, and validating
the packaged-default registry. The repair preserves isolated Python mode,
venv containment, wheel-resource uniqueness, absent root config, and
packaged-default origin while directly excluding source-checkout or editable
fallback.

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - requires packaged manifests to assemble
  deterministic seven-category context in a fresh worker.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - require GT-KB test artifacts to
  stay in-root and forbid treating that containment as source-checkout use.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before the
  protected test changes and independent VERIFIED before completion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the
  assertion repair and verification plan to trace to governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit
  PAUTH, project, work-item, target-path, and slice linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent
  execution of the exact frozen fresh-worker lane.
- `GOV-STANDING-BACKLOG-001` - governs WI-5407 as durable hygiene work.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires every real isolation
  and packaging assertion to remain intact.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires current,
  reproducible evidence under an explicit in-root basetemp.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - require traceable proposal,
  implementation, verification, and completion artifacts.

## Prior Deliberations

_No prior deliberations: WI-5407 applies the current root-containment and
context-manifest contracts to a newly observed acceptance-test false positive;
it introduces no new policy or architectural choice._

## Owner Decisions / Input

No new owner decision is required. The owner authorized the modernization
program and directed every discovered flaw to a hygiene work item while work
continues. Active authority is
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`.
Implementation remains gated on independent GO plus matching work-intent and
implementation-start authority.

## Requirement Sufficiency

Existing requirements sufficient. The context-manifest contract requires a
real packaged-default fresh-worker proof, and the root-boundary requirements
require test fixtures to remain in-root. Exact source-checkout exclusion
satisfies both without a specification change.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5407 forced in-root AT-FRESH-WORKER reproduction",
  "canonical_authority": "DCL-ACTIVITY-CONTEXT-MANIFEST-001 plus the GT-KB root-containment contract",
  "primary_route": "the frozen built-wheel fresh-worker test using isolated Python mode",
  "before_behavior": "a valid wheel installed into an in-root isolated venv is rejected merely because its path is lexically below REPO_ROOT",
  "after_behavior": "the module must remain inside the isolated venv and outside the checkout's groundtruth-kb/src directory",
  "self_descriptive_naming": "BUILD_PROJECT / src names the excluded checkout source boundary directly",
  "obsolete_guidance_disposition": "no guidance changes; the invalid broad lexical assertion is replaced",
  "history_preservation": "WI-5407 retains the exact failing module path and forced-basetemp reproduction",
  "baseline": "the exact node completes wheel installation and payload validation, then fails only the REPO_ROOT lexical assertion",
  "expected_result": "all four frozen fresh-worker tests pass under an explicit in-root basetemp",
  "rollback": "restore the single assertion in a governed test-only transaction",
  "hard_invariants": [
    "the imported module is inside the newly created venv",
    "the imported module is outside the checkout source directory",
    "Python runs with -I isolated mode",
    "the registry origin is packaged_default",
    "the root config remains absent",
    "all expected packaged resources occur exactly once in the wheel",
    "no host authority fallback is introduced"
  ],
  "fail_closed_conditions": [
    "the venv-containment assertion is removed",
    "source-checkout exclusion is absent or broader than the checkout source path",
    "any packaged-resource, context, isolated-mode, or absent-config assertion is weakened",
    "the exact frozen lane fails under in-root basetemp",
    "any production source changes"
  ],
  "essential_context_preservation": "the built-wheel fixture, offline build, no-index install, isolated subprocess, payload equality, registry-version, and package-resource assertions remain unchanged"
}
```

## Spec-Derived Verification Plan

1. Fresh-worker, root-containment, and non-impairment requirements:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --basetemp=E:/GT-KB/.pytest-tmp/wi5407-verification
```

Expected: `4 passed`. The command must use an explicit in-root basetemp.

2. Static and exact scope:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_modernization_fresh_worker.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_modernization_fresh_worker.py
git diff --check -- platform_tests/scripts/test_modernization_fresh_worker.py
git diff -- platform_tests/scripts/test_modernization_fresh_worker.py
```

Expected: all static checks pass and the implementation diff changes only the
one invalid lexical assertion to exact checkout-source exclusion.

3. Bridge and artifact lifecycle:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5407-installed-wheel-source-exclusion --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5407-installed-wheel-source-exclusion
```

Expected: no missing required/advisory specifications and zero blocking clause
gaps, followed by independent Loyal Opposition verification.

## Risk / Rollback

Risk is low and test-only. An assertion that excludes too narrow a path could
miss another checkout alias, so verification must resolve both the module and
`BUILD_PROJECT / "src"` before comparison and retain venv containment as the
primary positive proof. Rollback restores only the one assertion.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5407-installed-wheel-source-exclusion`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - one acceptance assertion is corrected; no production behavior changes.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
