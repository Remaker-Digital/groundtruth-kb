NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-05T09-09-20Z-prime-builder-A-898986
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex auto-dispatched Prime Builder worker; ::init gtkb pb; model gpt-5.5; reasoning xhigh

# GT-KB Bridge Implementation Report - gtkb-dispatcher-complex-watchdog-cli-parity - 005

bridge_kind: implementation_report
Document: gtkb-dispatcher-complex-watchdog-cli-parity
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5023
Version: 005 (NEW; post-implementation report after NO-GO correction)
Responds to GO: bridge/gtkb-dispatcher-complex-watchdog-cli-parity-002.md
Responds to NO-GO: bridge/gtkb-dispatcher-complex-watchdog-cli-parity-004.md
Approved proposal: bridge/gtkb-dispatcher-complex-watchdog-cli-parity-001.md
Recommended commit type: feat:

## Implementation Claim

Completed the WI-5023 Slice 1 storm-watchdog CLI parity implementation after the `-004` NO-GO.

This dispatch completed the previously blocked doctor integration:

- Added `_check_dispatcher_daemon_watchdog_task()` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.
- Registered the watchdog check in `run_doctor()` adjacent to the existing dispatcher daemon supervisor check.
- The doctor check mirrors the supervisor-task posture: Windows-only, active only when `harness-state/bridge-substrate.json` selects `dispatcher_daemon`, reports pass when `GTKB-HarnessStormWatchdog` is registered/enabled/hidden and uses `pythonw.exe`, and warns with the governed install command when unhealthy.

The partial implementation reported in `bridge/gtkb-dispatcher-complex-watchdog-cli-parity-003.md` remains part of the full WI-5023 implementation surface: `dispatcher_watchdog.py`, the `gt bridge dispatch daemon watchdog` CLI group, `scripts/install_storm_watchdog_task.ps1`, and focused tests.

## Specification Links

- `SPEC-INTAKE-5e9375` - harmonized complex CLI plus complex health.
- `ADR-DISPATCHER-COMPLEX-CLI-001` - watchdog CLI parity and dispatcher complex CLI architecture.
- `ADR-DISPATCHER-ARCHITECTURE-001` - persistent-daemon / harness-isolation architecture and runtime fault isolation.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - supervision contract the watchdog complements.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - centralized dispatch service.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded project implementation authorization.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH mutation classes and forbidden operations.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge GO, implementation-start, work-intent, or verification gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work-item linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived testing before VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform placement under project root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact-oriented governance/advisory constraints.

## Owner Decisions / Input

No new owner decision is required. The `-004` NO-GO identified an implementation completeness gap, not an owner clarification or approval gap.

Active project authorization:

- `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION`
- Owner decision deliberation: `DELIB-202665481`
- Included work items: `WI-5023`, `WI-5024`, `WI-5025`, `WI-5026`
- Allowed mutation classes: `code`, `test`, `config`
- Forbidden operation: merge daemon, supervisor, and watchdog runtime processes.

## Prior Deliberations

- `bridge/gtkb-dispatcher-complex-watchdog-cli-parity-001.md` - approved Slice 1 implementation proposal.
- `bridge/gtkb-dispatcher-complex-watchdog-cli-parity-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-dispatcher-complex-watchdog-cli-parity-004.md` - Loyal Opposition NO-GO requiring doctor integration and full verification rerun.
- `DELIB-202665481` - project authorization for `PROJECT-GTKB-DISPATCHER-COMPLEX-CLI`.
- `DELIB-202665470` - dispatch resume decision that surfaced the watchdog CLI gap.
- `DELIB-20266276` - dispatcher daemon resilience lineage establishing the watchdog as a separate resilience task.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-DISPATCHER-COMPLEX-CLI-001` decision 2 | `groundtruth-kb/.venv/Scripts/pytest.exe platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py -q --tb=short --basetemp .harness-tmp/pytest-watchdog-cli` - 3 passed. |
| Watchdog-control API / governed installer | `groundtruth-kb/.venv/Scripts/pytest.exe platform_tests/scripts/test_dispatcher_watchdog_control.py -q --tb=short --basetemp .harness-tmp/pytest-watchdog-control` - 14 passed. |
| Doctor watchdog check | `platform_tests/scripts/test_dispatcher_watchdog_control.py::test_doctor_watchdog_task_reports_healthy` and `::test_doctor_watchdog_task_warns_with_install_hint` included in the full 14-passing test run. |
| Fault isolation (`ADR-DISPATCHER-ARCHITECTURE-001`) | `test_watchdog_control_does_not_touch_supervisor_task` included in the full 14-passing control test run. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries forward linked specifications, spec-to-test mapping, exact commands, and observed results. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live bridge state was latest `NO-GO` and implementation authorization resumed from the prior GO with packet `sha256:57be82af91949854652246e2cd02ce1fea346ee971b79fe4d394411bb99a4936`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt projects show PROJECT-GTKB-DISPATCHER-COMPLEX-CLI --json` showed active PAUTH `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION`, including `WI-5023`, allowing `code`, `test`, and `config`, and forbidding runtime-process merging. Implementation still proceeded only after bridge GO plus implementation-start packet. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All WI-5023 files remain under in-root platform source, scripts, and platform tests paths. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/gt.exe harness roles`
- `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status`
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json`
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-dispatcher-complex-watchdog-cli-parity --format json`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-dispatcher-complex-watchdog-cli-parity`
- `groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-GTKB-DISPATCHER-COMPLEX-CLI --json`
- `groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py platform_tests/scripts/test_dispatcher_watchdog_control.py`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py platform_tests/scripts/test_dispatcher_watchdog_control.py`
- `groundtruth-kb/.venv/Scripts/pytest.exe platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py -q --tb=short --basetemp .harness-tmp/pytest-watchdog-cli`
- `groundtruth-kb/.venv/Scripts/pytest.exe platform_tests/scripts/test_dispatcher_watchdog_control.py -q --tb=short --basetemp .harness-tmp/pytest-watchdog-control`

## Observed Results

- Harness identity and role resolution: codex `A`, role `prime-builder`.
- Live bridge state: `gtkb-dispatcher-complex-watchdog-cli-parity` latest status `NO-GO` at `bridge/gtkb-dispatcher-complex-watchdog-cli-parity-004.md`; selected dispatch was current/actionable.
- Implementation authorization: created successfully from the prior GO in a resumable post-GO NO-GO state; packet hash `sha256:57be82af91949854652246e2cd02ce1fea346ee971b79fe4d394411bb99a4936`.
- Ruff lint: `All checks passed!`
- Ruff format: `5 files already formatted`
- CLI pytest: `3 passed, 2 warnings in 0.29s`
- Watchdog control pytest: `14 passed, 2 warnings in 0.99s`
- Pytest warnings were existing environment/cache warnings: unknown `asyncio_mode` config option and inability to update `.pytest_cache` nodeids due a Windows file-exists condition. No test assertion failed.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py` - watchdog scheduled-task status/control API from the partial `-003` implementation.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - `gt bridge dispatch daemon watchdog {status,install,enable,disable,uninstall}` CLI group from the partial `-003` implementation.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` - completed this dispatch's doctor watchdog check and registration.
- `scripts/install_storm_watchdog_task.ps1` - governed hidden `GTKB-HarnessStormWatchdog` installer from the partial `-003` implementation.
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py` - CLI parity tests from the partial `-003` implementation.
- `platform_tests/scripts/test_dispatcher_watchdog_control.py` - watchdog control, fault-isolation, installer, and doctor tests from the partial `-003` implementation.

## Scoped Dirty-Tree Note

`groundtruth-kb/src/groundtruth_kb/project/doctor.py` already contained an unrelated dirty hunk in `_check_sot_duplicate_guard` before this dispatch. This report does not claim that hunk as WI-5023 work. The WI-5023 doctor change is the new `_check_dispatcher_daemon_watchdog_task()` function and its `run_doctor()` registration.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: this implementation adds a governed dispatcher watchdog control capability, CLI surface, doctor health surface, installer, and tests.

## Acceptance Criteria Status

- [x] Governed watchdog-control API.
- [x] `gt bridge dispatch daemon watchdog` command group.
- [x] Doctor watchdog check.
- [x] Governed installer.
- [x] Spec-derived verification rerun with both ruff gates and the focused pytest suites.

## Risk And Rollback

Risk: the live Windows scheduled task can still be unhealthy on a workstation if the task is not installed or is configured outside the governed installer. Mitigation: the new doctor check reports the unhealthy condition and points to `gt bridge dispatch daemon watchdog install`; no Task Scheduler mutation was performed by this implementation session.

Rollback: revert the WI-5023 files listed above or uninstall the task with `gt bridge dispatch daemon watchdog uninstall` if it has been installed. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the `-004` NO-GO finding is resolved by the new doctor check and registration.
2. Verify the full WI-5023 implementation against the linked specifications and executed command evidence.
3. If the unrelated pre-existing `doctor.py` hunk prevents atomic VERIFIED finalization for this bridge thread, return a narrowly scoped NO-GO naming that isolation issue rather than rejecting the watchdog implementation itself.
