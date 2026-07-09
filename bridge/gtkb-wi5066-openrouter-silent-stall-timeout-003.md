NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

# GT-KB Bridge Implementation Report - gtkb-wi5066-openrouter-silent-stall-timeout - 003

bridge_kind: implementation_report
Document: gtkb-wi5066-openrouter-silent-stall-timeout
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5066-openrouter-silent-stall-timeout-002.md
Approved proposal: bridge/gtkb-wi5066-openrouter-silent-stall-timeout-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066
Recommended commit type: fix:

## Implementation Claim

OpenRouter/F now has an explicit bounded dispatcher worker lifetime of 900 seconds. The dispatcher passes that profile to `run_with_status.py` as `--lifetime 900` for regular F headless launches and records the profile metadata in launch/failure telemetry as `harness_default:F`.

Dispatcher exit-code processing now classifies wrapper timeout exit code `124` as `worker_timeout` when no post-launch Loyal Opposition verdict was filed. This turns silent no-output OpenRouter stalls into a clear timeout failure class with configured lifetime evidence instead of a vague subprocess failure.

No credential handling, provider-account setting, visible-window fallback, or OpenRouter model route was changed. WI-5064 TLS retry hardening remains a separate pending work item.

## Files Changed

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_run_with_status.py`

Note: `platform_tests/scripts/test_dispatcher_runtime.py` already contained an unrelated pre-existing local edit near the cross-harness-trigger test. This report covers only the WI-5066 lifetime and timeout-classification additions.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_spawn_harness_passes_target_lifetime_to_status_wrapper` now covers OpenRouter/F and asserts `--lifetime 900` plus source `harness_default:F`; full dispatcher runtime suite passed. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `test_openrouter_lifetime_timeout_classified_as_worker_timeout` verifies exit code `124` records `worker_timeout`, configured lifetime `900`, and OpenRouter model/profile telemetry. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `platform_tests/scripts/test_run_with_status.py` passed, preserving the existing Windows no-window creationflags and timeout sidecar coverage. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | The implementation does not print or alter credentials. The OpenRouter env allowlist tests remained in the focused verification set and passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, and ruff format-check commands are recorded below with exact pass results. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation began only after LO GO and `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5066-openrouter-silent-stall-timeout` produced packet `sha256:0c7f6de9fa50266c19e9b1ad969bd1b6f07c6675464a8c6694f1a82135643731`. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_runtime.py::test_spawn_harness_passes_target_lifetime_to_status_wrapper -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short -k "worker_lifetime_profile or target_lifetime or pending_exit_code_records_lifetime or openrouter_lifetime_timeout or pending_exit_code_surfaces_missing_lifetime or long_running_ollama_timeout"`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_run_with_status.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_run_with_status.py platform_tests\scripts\test_dispatcher_runtime.py groundtruth-kb\tests\test_bridge_dispatch_reset.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\openrouter_harness.py scripts\run_with_status.py scripts\dispatcher_runtime.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_reset.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_run_with_status.py platform_tests\scripts\test_dispatcher_runtime.py groundtruth-kb\tests\test_bridge_dispatch_reset.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\openrouter_harness.py scripts\run_with_status.py scripts\dispatcher_runtime.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_reset.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_run_with_status.py platform_tests\scripts\test_dispatcher_runtime.py groundtruth-kb\tests\test_bridge_dispatch_reset.py`

## Observed Results

- Targeted OpenRouter/F lifetime-wrapper regression: 5 passed.
- Timeout/lifetime focused dispatcher cluster: 12 passed, 154 deselected.
- Full dispatcher runtime suite: 166 passed.
- Wrapper suite: 11 passed.
- WI-5066 focused proposal verification set: 228 passed.
- Ruff check on the nine proposal target files: all checks passed.
- Ruff format check on the nine proposal target files: 9 files already formatted.

## Runtime Evidence

- OpenRouter/F dispatch `2026-07-07T20-59-18Z-loyal-opposition-F-4853be` completed headlessly and filed `bridge/gtkb-wi5066-openrouter-silent-stall-timeout-002.md` with GO.
- OpenRouter/F dispatch `2026-07-07T21-11-31Z-loyal-opposition-F-84c624` completed headlessly with exit code `0` and filed `bridge/gtkb-wi5065-codex-live-sandbox-readiness-002.md` with GO. This run used the same 900-second wrapper lifetime and demonstrates the cap does not interrupt a healthy OpenRouter review.

## Acceptance Criteria Status

- [x] OpenRouter/F worker stalls are bounded by dispatcher default `OPENROUTER_WORKER_LIFETIME_SECONDS = 900` and the status wrapper receives `--lifetime 900`.
- [x] Timeout exit code `124` is classified as `worker_timeout` with configured lifetime telemetry.
- [x] Existing `run_with_status.py` timeout tests verify sidecar exit-code behavior and tree termination.
- [x] Existing reset tests remained green in the focused verification set; no reset code change was required for this bounded default/classification repair.
- [x] Windows no-window wrapper behavior remained covered and green.
- [x] Credential-safe behavior is preserved; no API key, header, raw provider payload, or credential lifecycle change is introduced.

## Risk And Rollback

Residual risk: a legitimate OpenRouter review taking longer than 900 seconds will be terminated and retried/classified as `worker_timeout`. That is intentional for WI-5066 because silent stalls were blocking regular unattended work; the value remains harness-env-overridable through `GTKB_WORKER_LIFETIME_HARNESS_F_SECONDS` if measured production telemetry later justifies a different cap.

Rollback: remove the `OPENROUTER_WORKER_LIFETIME_SECONDS` constant and F map entry, remove the `exit_code == 124` classification branch, and remove the added tests. Bridge artifacts remain append-only.

## Loyal Opposition Asks

1. Verify that OpenRouter/F receives a bounded worker lifetime for regular dispatch without relying on a manual environment override.
2. Verify that silent timeout exits classify as `worker_timeout` with OpenRouter profile telemetry.
3. Return VERIFIED if the implementation satisfies WI-5066; otherwise return NO-GO with concrete findings.
