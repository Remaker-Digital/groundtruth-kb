NEW

# WI-5026 Slice 4 - Doctor Delegation to Dispatcher Complex Health

bridge_kind: prime_proposal
Document: gtkb-dispatcher-complex-doctor-delegation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex interactive Prime Builder; ::init gtkb pb; restarted Codex continuation; approval_policy=never; danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5026

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py", "platform_tests/scripts/test_dispatcher_watchdog_control.py"]

implementation_scope: source-and-tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement `WI-5026` by making `gt project doctor` use the dispatcher-complex
health computation as the single source of truth for dispatcher daemon,
supervisor, and storm-watchdog lifecycle checks. Today the doctor still carries
separate supervisor/watchdog probing paths. Slice 3 just verified
`collect_complex_health(...)`, including per-component severity and watchdog
heartbeat freshness. This slice removes the duplicate health interpretation
from doctor-facing checks while preserving the existing doctor check names,
messages, and non-Windows skip behavior.

This is a delegation/refactor slice only. It must not merge the dispatcher
daemon, Windows supervisor scheduled task, or storm watchdog scheduled task
runtime processes; that separation is explicitly preserved by the project PAUTH
and by the dispatcher daemon architecture.

## Specification Links

- `SPEC-INTAKE-5e9375` - owner-approved requirement for a harmonized dispatcher daemon complex management CLI and unified complex-health contract.
- `ADR-DISPATCHER-COMPLEX-CLI-001` - decision 5 requires doctor delegation to complex-health as the single source of truth.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon, supervisor, and watchdog stay separated for fault isolation; this proposal consumes the health rollup without changing runtime topology.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - scheduled-task health remains explicit and observable.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher control and health visibility remain centralized.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed as a numbered bridge entry and must receive LO `GO` before protected source/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implementation proposal links the governing requirements and maps them to tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries PAUTH/project/work-item metadata and concrete `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward the spec-to-test mapping and executed results.
- `GOV-STANDING-BACKLOG-001` - `WI-5026` is the remaining open work item in the active dispatcher-complex project.
- `SPEC-AUQ-POLICY-ENGINE-001` - no prose owner decision is being collected; existing owner authorization is cited.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root GT-KB platform paths.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use helper-mediated bridge filing and self-enforce bridge gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the proposal preserves the work item, implementation plan, evidence, and verification lifecycle as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the slice keeps requirements, implementation evidence, tests, and verification linked through the bridge.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - implementation and verification evidence crossing the artifact threshold remains in governed bridge/report surfaces.

## Prior Deliberations

- `DELIB-202665481` - owner authorization for `PROJECT-GTKB-DISPATCHER-COMPLEX-CLI`, including the PAUTH covering `WI-5023` through `WI-5026` and the runtime-process-separation constraint.
- `SPEC-INTAKE-5e9375` / `INTAKE-6554ff58` - requirement candidate for the dispatcher daemon complex management and health-rollup contract.
- `DELIB-202665470` - dispatch-resume reconciliation decision whose investigation exposed fragmented dispatcher-health surfaces.
- `DELIB-20266276` - dispatcher daemon resilience lineage preserving dedicated supervision and storm containment.
- `bridge/gtkb-dispatcher-complex-health-rollup-006.md` - Slice 3 VERIFIED verdict, establishing `collect_complex_health(...)` as the verified source for this delegation.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-05-11-35-PB-dispatcher-frontier-reconciliation.md` - current PB reconciliation note recording the `WI-5025` -> `WI-5026` gate and architecture alignment ledger.

## Owner Decisions / Input

No new owner decision is required. Existing owner authorization is carried by
`DELIB-202665481` and the active PAUTH
`PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION`.
The proposal stays within that scope: control-plane and observability only,
with no runtime-process merger, production deployment, or credential change.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-5e9375` and
`ADR-DISPATCHER-COMPLEX-CLI-001` decision 5 define the required behavior:
doctor dispatcher/supervisor checks should delegate to complex-health as the
single source of truth without duplicate check logic or circular dependency.
No new or revised requirement is needed before implementation.

## Proposed Scope

- Add a small doctor helper that reads `collect_complex_health(target)` once and
  returns component payloads for doctor checks.
- Repoint `_check_dispatcher_daemon_supervisor_task(...)` and
  `_check_dispatcher_daemon_watchdog_task(...)` to use the verified
  complex-health component data instead of calling `collect_supervisor_status`
  and `collect_watchdog_status` directly.
- Preserve the public doctor check names, required/found/status conventions,
  install hints, and non-Windows skip behavior.
- Preserve the existing substrate gate: when the bridge substrate is not
  `dispatcher_daemon`, supervisor/watchdog scheduled-task checks remain not
  required.
- Add focused tests proving doctor checks consume `collect_complex_health(...)`
  and that supervisor/watchdog status messages still surface useful install
  guidance.
- Do not change daemon start/stop/control commands, dispatch routing, lane
  scoring, project state, or runtime scheduled-task topology.

## Dependency Gate

Implementation may begin only if
`gt bridge show gtkb-dispatcher-complex-health-rollup --json --compact`
reports latest `VERIFIED`. This was confirmed before filing this proposal:
latest path `bridge/gtkb-dispatcher-complex-health-rollup-006.md`, latest
status `VERIFIED`, commit `e5965833`.

## Spec-Derived Verification Plan

Spec-to-test mapping:

- `SPEC-INTAKE-5e9375` and `ADR-DISPATCHER-COMPLEX-CLI-001` decision 5:
  focused doctor tests show supervisor/watchdog doctor checks consume
  `collect_complex_health(...)` rather than duplicate scheduled-task collectors.
- `ADR-DISPATCHER-ARCHITECTURE-001` and
  `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`: tests preserve separate
  component semantics and verify no daemon/supervisor/watchdog runtime-control
  behavior is changed.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: existing complex-control tests remain
  passing while doctor consumes the central complex-health payload.
- Bridge governance specs: implementation report will carry forward this mapping
  and exact command evidence.

Verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/scripts/test_dispatcher_watchdog_control.py platform_tests/scripts/test_dispatcher_complex_control.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/scripts/test_dispatcher_watchdog_control.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/scripts/test_dispatcher_watchdog_control.py
```

Expected result: all focused tests pass; ruff lint and format checks pass.

## Risk / Rollback

Risk is limited to doctor health reporting for dispatcher supervisor/watchdog
checks. The main behavioral risk is message drift: doctor users still need
actionable install/enable hints when complex-health reports a component problem.
Tests will pin those messages. Rollback is a single scoped commit reverting
`groundtruth-kb/src/groundtruth_kb/project/doctor.py` and the two focused test
files; no DB migration, runtime task mutation, or deployment is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-dispatcher-complex-doctor-delegation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`refactor:` - this changes the doctor implementation to delegate health logic to
the already verified complex-health source of truth while preserving the doctor
surface and adding focused regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
