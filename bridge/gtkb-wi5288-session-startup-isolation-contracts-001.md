NEW

# Defect-Fix Proposal - Reconcile session startup with platform isolation contracts

bridge_kind: prime_proposal
Document: gtkb-wi5288-session-startup-isolation-contracts
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5288

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: source and test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Correct two release-gate regressions in session self-initialization. The GT-KB
startup model currently marks the axe accessibility integration `partial`
because it recognizes `applications/Agent_Red/tests/accessibility` only when
the active work subject is the application, even though Agent Red is the
in-root reference adopter exercised by the GT-KB release gate. Separately, one
startup test still expects the retired `Agent Red GT-KB Dashboard` title while
the canonical generator and its focused tests require `GT-KB Operations
Dashboard`.

The implementation will recognize the exact in-root reference-adopter test
path in the GT-KB integration inventory and align the stale title assertion.
It will not broaden arbitrary application discovery, alter the generator, or
change application/GT-KB mutation authority.

## Baseline And Scope

- HEAD: `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f`.
- `scripts/session_self_initialization.py` is tracked and clean at blob
  `5be8e89b52981389e52eee2a10c7317bb7455be7`.
- `platform_tests/scripts/test_session_self_initialization.py` is tracked and
  clean at blob `ec10b3c1c92ca0d2c3198f99b472f54d978ef3a1`.
- The exact release pytest batch fails
  `test_startup_model_contains_role_governance_and_kpi_inventory` because axe
  is `partial`, and
  `test_dashboard_and_report_are_written_with_time_series_kpi` because the
  generated title is the canonical `GT-KB Operations Dashboard`.
- Dashboard generator source, Agent Red application files, bridge/TAFE,
  credentials, external systems, and concurrent worktree files are read-only.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - Startup must report current testing
  integrations and dashboard state from live in-root project sources.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` - Startup/dashboard evidence must agree
  on the canonical project dashboard rather than preserve an adopter-specific
  title.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red remains an in-root,
  lifecycle-independent reference adopter; the correction names only that
  canonical path and does not grant application-subject write authority.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Startup context must become more
  accurate without erasing subject boundaries or weakening current behavior.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - The integration
  readiness and dashboard-title contracts remain executable.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Readiness and title
  outcomes are deterministic and directly testable.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected source/test changes require an
  independent GO, matching claim, and implementation-start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Exact files,
  behavior, invariants, and tests are linked here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work
  item, and target paths are explicit above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent VERIFIED
  must rerun the mapped startup, dashboard, lint, and release tests.
- `GOV-STANDING-BACKLOG-001` - WI-5288 records the RC regression durably.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The finding is preserved through
  governed implementation and independent verification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Proposal, source/test correction,
  report, and verdict form one durable packet.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Stale startup expectations are
  repaired explicitly instead of being normalized as baseline noise.

## Prior Deliberations

- `DELIB-0877` - GT-KB/application separation must preserve asymmetric
  authority while allowing GT-KB release engineering and adopter validation.
- `DELIB-1084` - Startup/dashboard behavior is GT-KB platform behavior and
  Agent Red is a consuming reference adopter, not the owner of unique startup
  semantics.
- `DELIB-202666274` - The owner authorized required modernization repairs while
  preserving bridge review and mechanical gates.

## Owner Decisions / Input

The owner authorized the full modernization program and directed repair of all
release blockers. Existing isolation and startup decisions resolve this scope:
GT-KB may inspect its in-root reference adopter for release evidence, while
application-subject sessions do not gain GT-KB product mutation authority. No
additional owner preference is required. This proposal does not authorize Git,
deployment, release, credentials, dispatcher, TAFE, harness, routing, role, or
external-system mutation.

## Requirement Sufficiency

Existing requirements sufficient.

The startup GOV, dashboard specification, and isolation ADR already require
accurate GT-KB project reporting with Agent Red as the reference adopter. The
canonical generator already supplies the correct title and the test suite
already states the expected axe readiness. The implementation reconciles two
stale code/test predicates; no new behavior contract is needed.

## Proposed Scope

1. Treat the exact canonical path
   `applications/Agent_Red/tests/accessibility` as accessibility evidence in
   the GT-KB startup integration inventory regardless of whether the active
   subject is GT-KB or Agent Red.
2. Preserve the existing generic GT-KB `platform_tests/accessibility` and
   `tests/accessibility` checks.
3. Preserve application-subject gating for application package/configuration
   reads not involved in this exact test-presence predicate.
4. Replace the stale test expectation `Agent Red GT-KB Dashboard` with the
   canonical `GT-KB Operations Dashboard`; do not modify the generator.
5. Run focused startup/dashboard tests, Ruff, format, and the release pytest
   subset that exposed both failures.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5288, DELIB-0877, DELIB-1084, and DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short",
  "before_behavior": "GT-KB startup ignores the canonical reference-adopter accessibility suite and one test expects a retired adopter-specific dashboard title.",
  "after_behavior": "GT-KB startup recognizes the exact in-root Agent Red accessibility suite and all startup tests use the canonical GT-KB dashboard title.",
  "self_descriptive_naming": "The canonical applications/Agent_Red path and GT-KB Operations Dashboard title state their ownership directly.",
  "obsolete_guidance_disposition": "The retired Agent Red GT-KB Dashboard expectation is removed from the test; no historical evidence is rewritten.",
  "history_preservation": "Only current source/test behavior changes; prior dashboard and startup history remains untouched.",
  "baseline": {
    "head": "4ba39a438b84ec40c646cfc46c2741d6e7c6a60f",
    "source_blob": "5be8e89b52981389e52eee2a10c7317bb7455be7",
    "test_blob": "ec10b3c1c92ca0d2c3198f99b472f54d978ef3a1",
    "focused_release_failures": 2
  },
  "expected_result": {
    "accessibility_axe_status": "ready",
    "dashboard_title": "GT-KB Operations Dashboard",
    "focused_release_failures": 0,
    "new_application_write_authority": 0
  },
  "essential_context_preservation": "All existing startup role, governance, KPI, project, integration, remediation, and dashboard panel assertions remain in force.",
  "hard_invariants": [
    "no arbitrary application discovery",
    "no application-to-GT-KB write authority expansion",
    "no dashboard generator change",
    "no external service call",
    "only two initially clean tracked targets",
    "frozen modernization acceptance scope unchanged"
  ],
  "fail_closed_conditions": [
    "reference-adopter path is absent",
    "workflow accessibility.yml is absent",
    "dashboard title diverges from canonical generator",
    "focused startup or dashboard tests regress"
  ],
  "rollback": "Restore the exact two reviewed predicates and rerun the focused startup suite."
}
```

## Spec-Derived Verification Plan

| Specification | Verification and expected result |
|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` | Full startup test file passes and reports axe `ready` only when workflow plus an allowed test path exist. |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` | Startup writer test and `test_gtkb_dashboard_grafana.py` agree on `GT-KB Operations Dashboard`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Diff inspection proves only the exact in-root reference-adopter read path is added and no mutation authority changes. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Existing startup assertions and dashboard panel assertions remain green; no generator change. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Exact previously failing tests pass without monkeypatching their expected outcomes. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Readiness and title are asserted as stable machine-readable values. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and clause preflights pass with no blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns all exact commands below before VERIFIED. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Valid GO, matching claim, and implementation-start packet exist before edits. |

Exact commands:

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py::test_startup_model_contains_role_governance_and_kpi_inventory platform_tests/scripts/test_session_self_initialization.py::test_dashboard_and_report_are_written_with_time_series_kpi -q --tb=short
python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_gtkb_dashboard_grafana.py -q --tb=short
python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py
```

## Acceptance Criteria

1. The exact two release failures pass.
2. GT-KB startup reports axe `ready` when `.github/workflows/accessibility.yml`
   and the canonical Agent Red accessibility suite exist.
3. Missing workflow or all allowed test paths still yields non-ready status.
4. Startup/dashboard tests agree on `GT-KB Operations Dashboard`.
5. No dashboard generator, application file, authority rule, credential,
   external system, or concurrent worktree file changes.
6. Full focused suites, Ruff, and format checks pass and are independently
   rerun before VERIFIED.

## Risk / Rollback

The only behavioral risk is incorrectly treating unrelated application tests
as platform evidence. Scope is limited to the literal canonical reference
adopter path already governed under this root. Rollback restores the two
reviewed lines and reruns the focused suite.

## Bridge Filing

This proposal is filed as the append-only numbered bridge file
`bridge/gtkb-wi5288-session-startup-isolation-contracts-001.md`. No prior
version is deleted or rewritten; dispatcher/TAFE state plus numbered bridge
files remain the governed workflow surfaces.

## Recommended Commit Type

`fix` - one startup readiness predicate and one stale test expectation are
corrected. Any commit remains separately mechanically authorized.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
