NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f765b-9cc2-7ae3-bfa1-fc2e2b6fca41
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# WI-5381 Supplemental - Agent Red Pipeline Routing Constant

bridge_kind: prime_proposal
Document: gtkb-wi5381-agent-red-pipeline-routing-constant
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5381

target_paths: ["applications/Agent_Red/src/multi_tenant/superadmin_api/_diagnostics.py"]

implementation_scope: focused Agent Red diagnostics fallback-suite metadata correction required by WI-5381 acceptance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Supplement the active WI-5381 application-root build self-containment work with
one uncovered Agent Red source-file correction. The WI-5381 implementation
restores the application-local test-host package and build surfaces, but the
existing Agent Red diagnostics API fallback metadata still omits `pipeline`
from `_TESTHOST_SUITES` and `_TESTHOST_COUNT_REGISTRY` while separately marking
`pipeline` as a composite suite. Existing Agent Red test-host dispatch and SPA
contract tests expect `pipeline` to be a valid test-host suite, so the focused
source correction is required before the WI-5381 acceptance test suite can
reach an all-pass state.

The approved WI-5381 proposal did not include
`applications/Agent_Red/src/multi_tenant/superadmin_api/_diagnostics.py` in its
target paths. This supplemental proposal requests that exact path and no other
source, test, build, dispatcher, TAFE, bridge-state, or platform-root target.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-1825` requires the Agent Red
test-host verification stage to be functional; the application-isolation and
governed-release requirements require that Agent Red-owned test-host routing be
complete within the application lifecycle; the modernization non-impairment
contract requires the fix to avoid unrelated GT-KB platform, dispatcher, TAFE,
bridge-state, and root build-file mutations.

## Specification Links

- `SPEC-1825` - Agent Red self-service deployment pipeline and test-host
  verification stage.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - Agent Red runtime and
  verification behavior belongs to the application lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed Agent Red artifacts
  remain below `applications/Agent_Red`.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - Agent Red remains a conformant
  reference adopter with governed verification surfaces.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - the changed source file remains
  inside the canonical application namespace.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires
  executable and complete test-host routing evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the correction must preserve
  platform behavior, concurrent work, credentials, and unrelated harness
  operation.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - changed Python source requires focused
  test, lint, formatting, and syntax evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-20265219`, `DELIB-20265220`, and `DELIB-20265227` established the
  Agent Red readiness program, Phase 1 scope, application-isolation contract,
  and app-root minimization foundation.
- `DELIB-202666274` records the active project-scoped modernization authority
  and non-bypass boundaries.
- `DELIB-202666694` records the initial WI-5381 GO and confirms that
  `SPEC-1825` keeps the test-host surface live.
- `bridge/gtkb-wi5381-agent-red-build-root-self-containment-005.md` defines
  the approved non-destructive WI-5381 target inventory and excludes this
  diagnostics source path.
- `bridge/gtkb-wi5381-agent-red-build-root-self-containment-006.md` grants GO
  for the version 005 WI-5381 target inventory only.

## Proposed Scope

- Update only
  `applications/Agent_Red/src/multi_tenant/superadmin_api/_diagnostics.py`.
- Add `pipeline` to the fallback test-host suite allowlist and fallback count
  registry so `pipeline` is a recognized runnable composite test-host suite
  when the external test-host metadata endpoint is unreachable.
- Preserve the existing endpoint shape, response model, diagnostics API
  behavior, and application-root build/test-host files already changed under
  WI-5381.

## Explicit Exclusions

- No mutation to WI-5381 build/dependency/test-host target files already
  covered by `bridge/gtkb-wi5381-agent-red-build-root-self-containment-006.md`.
- No mutation to Agent Red tests or test expectations.
- No mutation to GT-KB platform-root Docker, compose, workflow, dispatcher,
  TAFE, bridge-state, harness, credential, or release files.
- No destructive cleanup.

## Acceptance Criteria

- The Agent Red diagnostics API fallback suite inventory includes `pipeline`
  as a runnable test-host suite when test-host metadata cannot be reached.
- Existing Agent Red dispatch and SPA contract tests that require `pipeline`
  routing pass without editing test expectations.
- The implementation diff for this supplemental proposal is limited to
  `applications/Agent_Red/src/multi_tenant/superadmin_api/_diagnostics.py`.

## Specification-Derived Verification

| Requirement | Verification command or check | Expected result |
| --- | --- | --- |
| `SPEC-1825` | From `applications/Agent_Red`, run `..\..\.gtkb-state\wi5381\test-venv\Scripts\python.exe -m pytest tests\test_host -q --tb=short --confcutdir=tests\test_host`. | All collected Agent Red test-host tests pass. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | From `applications/Agent_Red`, run `..\..\.gtkb-state\wi5381\test-venv\Scripts\python.exe -m py_compile src\multi_tenant\superadmin_api\_diagnostics.py`. | Source syntax compiles successfully. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Inspect `git diff -- applications/Agent_Red/src/multi_tenant/superadmin_api/_diagnostics.py` and `git status --short -- applications/Agent_Red/src/multi_tenant/superadmin_api/_diagnostics.py`. | Only the one approved Agent Red source path changes for this supplemental proposal. |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001` | Confirm no changed path for this supplemental proposal is outside `applications/Agent_Red/`. | All supplemental implementation paths remain application-owned. |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5381 supplemental acceptance gap found during Agent Red test-host verification",
  "canonical_authority": "SPEC-1825 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "bridge-go implementation with work-intent claim and implementation-start authorization",
  "before_behavior": "Agent Red fallback suite metadata exposes composite handling for pipeline but omits pipeline from the fallback suite allowlist and count registry, causing existing dispatch and SPA contract tests to fail.",
  "after_behavior": "Agent Red fallback suite metadata recognizes pipeline as a runnable composite test-host suite while preserving the existing diagnostics endpoint shape.",
  "self_descriptive_naming": "The changed symbol names remain the existing _TESTHOST_SUITES and _TESTHOST_COUNT_REGISTRY names, with the suite token pipeline matching the existing test-host suite vocabulary.",
  "obsolete_guidance_disposition": "No stale guidance or historical root build behavior is promoted; the proposal records that the original WI-5381 target inventory remains unchanged.",
  "history_preservation": "The supplemental bridge thread preserves the reason this path is separate from the approved WI-5381 GO inventory.",
  "baseline": {
    "failing_tests": [
      "tests/test_host/test_dispatch.py::TestSuiteRouting::test_testhost_suites_defined",
      "tests/test_host/test_dispatch_integration.py::TestDispatchRouting::test_pipeline_routes_to_testhost",
      "tests/test_host/test_spa_contract.py::TestSuiteOptionsContract::test_spa_suites_match_api_valid_suites",
      "tests/test_host/test_spa_contract.py::TestSuiteOptionsContract::test_testhost_suites_cover_comprehensive_and_full"
    ],
    "changed_paths": [
      "no supplemental source path has been changed before GO"
    ]
  },
  "expected_result": {
    "test_host_suite_result": "all collected tests pass",
    "changed_paths": [
      "applications/Agent_Red/src/multi_tenant/superadmin_api/_diagnostics.py"
    ]
  },
  "rollback": {
    "instructions": "Revert only the pipeline additions in applications/Agent_Red/src/multi_tenant/superadmin_api/_diagnostics.py.",
    "test": "Rerun the Agent Red test-host suite command from the Specification-Derived Verification table."
  },
  "hard_invariants": [
    "No platform-root build file mutation",
    "No Agent Red test expectation mutation",
    "No dispatcher, TAFE, bridge-state, harness, credential, or release-file mutation",
    "No destructive cleanup"
  ],
  "fail_closed_conditions": [
    "Loyal Opposition does not issue GO for this supplemental path",
    "work-intent claim or implementation-start authorization is absent",
    "the implementation requires a second path outside the declared target_paths"
  ],
  "essential_context_preservation": "WI-5381 remains governed by bridge/gtkb-wi5381-agent-red-build-root-self-containment-006.md; this proposal only adds the missing diagnostics source path needed to finish the same acceptance surface."
}
```

## Cross-Harness And Surface Disposition

Codex Prime Builder may implement only after Loyal Opposition issues GO and a
matching work-intent claim plus implementation-start authorization are active.
Claude, Cursor, Antigravity, dispatcher/TAFE, bridge publication logic,
platform tests, application-root build files, and release automation are
unchanged by this supplemental correction.

## Owner Decision

No new owner decision is required. This proposal stays inside the active
project authorization and only requests the source path needed to complete the
already-approved WI-5381 acceptance surface.
