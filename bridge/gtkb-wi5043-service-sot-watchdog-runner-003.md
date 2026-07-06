NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-07-06T16-29-36Z-prime-builder-A-152d23
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex dispatcher-spawned headless Prime Builder; resolved_role=prime-builder; approval_policy=never; workspace=E:\GT-KB

# GT-KB Bridge Implementation Report - gtkb-wi5043-service-sot-watchdog-runner - 003

bridge_kind: implementation_report
Document: gtkb-wi5043-service-sot-watchdog-runner
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5043-service-sot-watchdog-runner-002.md
Approved proposal: bridge/gtkb-wi5043-service-sot-watchdog-runner-001.md
Recommended commit type: feat:

Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-5043

## Implementation Claim

Implemented the detection-first platform service and SoT watchdog runner for WI-5043.

The new runner performs a bounded `gt status` component probe and a SoT-registry health-check pass, catches probe failures as structured findings, emits deterministic JSON status, and leaves restoration/canonical-store mutation out of scope for this slice. It writes status to `.gtkb-state/watchdog/service-sot-status.json` by default and reports explicit empty restore/canonical mutation lists.

The implementation also adds the operational surfaces needed to run and observe the watchdog:

- `scripts/gtkb_service_sot_watchdog.py` as the scheduled/script runner wrapper.
- `gt watchdog service-sot run/status/install/enable/disable/uninstall` CLI commands.
- Windows scheduled-task install/uninstall helpers for hidden periodic execution.
- A project doctor check for scheduled-task registration and recent output health.
- Focused platform tests for payload construction, failure capture, JSON output, scheduled-task parsing, doctor integration, and CLI dispatch.

## Specification Links

- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Requires a platform-wide watchdog that generalizes dispatcher D2/D4 posture to every `gt status` component and every SoT-registry `health_check_function`, with a dependency-light detection path.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Constrains this runner to fresh probes and symptom-based health evidence, and prevents this slice from auto-executing unsafe/canonical restoration.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires all GT-KB implementation targets to remain inside the GT-KB root and not silently resolve to Agent Red or any out-of-root application surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires status-bearing bridge files and dispatcher/TAFE state to be the live workflow authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this implementation proposal to cite all relevant governing specifications and map them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the Project Authorization, Project, and Work Item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the implementation report to carry forward these specifications and execute derived tests before verification.
- `GOV-STANDING-BACKLOG-001` - Treats WI-5043 and PROJECT-GTKB-SERVICE-SOT-WATCHDOG as the durable MemBase work authority for this scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires concrete implementation plans, owner decisions, risks, and future work to be preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Frames this work as part of the durable artifact graph connecting project, work item, bridge proposal, tests, and verification report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Requires lifecycle states and transition evidence to remain explicit as the project moves from proposal to implementation report to verification.

## Owner Decisions / Input

No new owner decision is required by this implementation report.

Carried-forward owner authority:

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` authorized full-project implementation for all six watchdog work items, including WI-5043, with `source`, `tests`, `config`, and `scheduled-task` mutation classes and with credential, deployment, canonical-store mutation, and force-push actions out of scope.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` selected tiered auto-restore plus fail-loud escalation. This implementation records detection status only; restoration execution remains for later project slices.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized the full watchdog project, including WI-5043, while preserving per-WI bridge GO requirements.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected tiered auto-restore for safe/idempotent actions and fail-loud escalation for canonical/at-risk actions; this runner supplies the probe input for that policy.
- `DELIB-20266276` - Dispatcher self-healing precedent: D2 full auto-recovery, D3 scheduled ensure-alive, and D4 alert-and-degrade are the model being generalized.
- `DELIB-20266140` - Visibility-only precedent: owner-marked components must remain visible and must not be silently auto-restored.
- `bridge/gtkb-wi5043-service-sot-watchdog-runner-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5043-service-sot-watchdog-runner-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | `platform_tests/scripts/test_gtkb_service_sot_watchdog.py` verifies `gt status` component enumeration, SoT-registry health-check probing, failure capture, status output, and CLI dispatch. The real `--no-write --component project` smoke run returned `overall=WARN`, `gt_components=1`, `sot_probes=19`, and `findings=6` without crashing. |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | The runner emits `restore_actions_executed: []` and `canonical_mutations_executed: []`, performs fresh probes, and records symptom-oriented findings. Tests assert failed probes become findings rather than unhandled exceptions. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Scope check over approved target paths showed changes only under `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py`, `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py`, `scripts/gtkb_service_sot_watchdog.py`, `scripts/install_service_sot_watchdog_task.ps1`, `scripts/uninstall_service_sot_watchdog_task.ps1`, and `platform_tests/scripts/test_gtkb_service_sot_watchdog.py`. No Agent Red lifecycle-independent repository or out-of-root path was touched. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Before implementation, `gt bridge show gtkb-wi5043-service-sot-watchdog-runner --json --compact` reported latest status `GO`, version count 2, latest path `bridge/gtkb-wi5043-service-sot-watchdog-runner-002.md`; implementation authorization was opened through `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5043-service-sot-watchdog-runner`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's linked specifications, authorization metadata, project metadata, work item, and verification evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Authorization packet was active for `PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION`, `PROJECT-GTKB-SERVICE-SOT-WATCHDOG`, and `WI-5043`; target paths matched the approved implementation scope. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff lint, ruff format check, and a real no-write smoke run were executed and are recorded below. |
| `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The work stayed tied to WI-5043 and is filed as the next numbered bridge implementation report for Loyal Opposition verification. |

## Commands Run

- `.\groundtruth-kb\.venv\Scripts\gt.exe harness roles`
- `.\groundtruth-kb\.venv\Scripts\gt.exe bridge show gtkb-wi5043-service-sot-watchdog-runner --json --compact`
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5043-service-sot-watchdog-runner`
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py status gtkb-wi5043-service-sot-watchdog-runner`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py -q --tb=short`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py -q --tb=short --basetemp .\.gtkb-state\pytest-tmp-service-sot`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check --fix groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff format groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py -q --tb=short --basetemp .\.gtkb-state\pytest-tmp-service-sot`
- `$out = & .\groundtruth-kb\.venv\Scripts\python.exe .\scripts\gtkb_service_sot_watchdog.py --no-write --component project 2>&1; $code = $LASTEXITCODE; $payload = (($out | Out-String) | ConvertFrom-Json); "exit=$code overall=$($payload.overall_status) gt_components=$($payload.summary.gt_status_component_count) sot_probes=$($payload.summary.sot_artifact_probe_count) findings=$($payload.findings.Count)"`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_doctor_bridge_accuracy.py platform_tests/scripts/test_dispatcher_watchdog_control.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py -q --tb=short --basetemp .\.gtkb-state\pytest-tmp-service-sot-regression`

## Observed Results

- Harness role check confirmed harness `A` resolved to `prime-builder`.
- Bridge state check confirmed the selected thread was latest `GO` before implementation.
- Implementation authorization opened successfully with active packet `sha256:b8215a4852e91175209deba1991ea4eab3739f716e22667ad822707ace8810a1` and target paths matching the approved proposal.
- Claim status remained live before report filing: `acting_role=prime-builder`, `claim_kind=go_implementation`, `latest_bridge_status=GO`, `expired=false`.
- The first targeted pytest run without `--basetemp` failed before test execution because local Windows temp creation was denied: `PermissionError: [WinError 5] Access is denied: 'C:\Users\micha\AppData\Local\Temp\pytest-of-micha'`.
- Targeted test rerun with workspace basetemp passed: `6 passed, 2 warnings in 0.28s`. Warnings were an unknown pytest config option `asyncio_mode` and a pytest cache directory creation warning.
- Final targeted test rerun after formatting passed again: `6 passed, 2 warnings`.
- Ruff check and ruff format check passed on all changed Python files: `All checks passed!` and `6 files already formatted`.
- Real no-write smoke run succeeded with exit code 0 and returned `overall=WARN`, `gt_components=1`, `sot_probes=19`, `findings=6`; this confirms the runner handles current project findings without writing status output or crashing.
- Additional nearby regression check was not part of the WI-5043 acceptance gate. It produced `23 passed, 3 failed`; all failures were in `groundtruth-kb/tests/test_doctor_bridge_accuracy.py` before the new service/SoT watchdog check, due an existing Windows project-scaffold path issue around `project\scripts\gtkb_dispatcher_daemon.py`. The dispatcher watchdog and bridge dispatch daemon watchdog regression tests in that command passed.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py`
- `scripts/gtkb_service_sot_watchdog.py`
- `scripts/install_service_sot_watchdog_task.ps1`
- `scripts/uninstall_service_sot_watchdog_task.ps1`
- `platform_tests/scripts/test_gtkb_service_sot_watchdog.py`

Notes:

- `groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py` and `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py` were approved target paths but did not require edits for this detection-runner slice.
- `groundtruth-kb/src/groundtruth_kb/cli.py` already had unrelated dirty work in the worktree before this implementation (`--plan-incomplete` under `projects authorize`); it was preserved and not reverted.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: this slice adds a new watchdog runner capability, its scheduled-task wrapper/control surface, doctor visibility, and targeted tests.

## Acceptance Criteria Status

- [x] Runner enumerates selected `gt status` components through existing status collection and records component status/findings.
- [x] Runner enumerates active SoT registry rows with non-empty `health_check_function` values and invokes supported doctor health checks with bounded exception handling.
- [x] Runner emits deterministic JSON status under `.gtkb-state/watchdog/service-sot-status.json` by default.
- [x] Runner is detection-only for WI-5043; no restore actions or canonical-store mutations are executed.
- [x] CLI and script wrapper are present for scheduled/manual execution.
- [x] Windows scheduled-task install/uninstall helpers are present and support dry-run behavior.
- [x] Doctor exposes service/SoT watchdog registration/output health for platform workspaces.
- [x] Focused tests cover runner payloads, failure handling, JSON write behavior, scheduled-task status parsing, doctor integration, and CLI command dispatch.

## Risk And Rollback

Residual risks:

- The first real project smoke run currently reports `overall=WARN` because existing platform components and SoT checks have findings. That is expected for a detection-first watchdog and is visibility evidence, not proof of a runner crash.
- The doctor check reports scheduled-task health only on Windows platform workspaces and skips elsewhere. That keeps adopter and non-Windows contexts from producing false failures.
- Scheduled-task install helpers were added but not installed during this implementation; installation is an operational action outside this bridge dispatch.

Rollback:

- Revert the new watchdog package, runner script, scheduled-task helper scripts, CLI command group, doctor check, and focused tests in one commit.
- If a scheduled task was installed later, run `scripts/uninstall_service_sot_watchdog_task.ps1` or `gt watchdog service-sot uninstall` before reverting runtime files.
- Bridge audit files remain append-only and must not be rewritten during rollback.

## Loyal Opposition Asks

1. Verify that the runner remains detection-only and dependency-light under `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` and `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`.
2. Verify that the implemented surfaces satisfy WI-5043 without claiming later restore-policy or resource-bounding project slices.
3. Return VERIFIED if the implementation and evidence satisfy the approved proposal; otherwise return NO-GO with concrete findings.
