NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

# GT-KB Bridge Implementation Report - gtkb-wi5065-codex-live-sandbox-readiness - 003

bridge_kind: implementation_report
Document: gtkb-wi5065-codex-live-sandbox-readiness
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5065-codex-live-sandbox-readiness-002.md
Approved proposal: bridge/gtkb-wi5065-codex-live-sandbox-readiness-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5065
Recommended commit type: fix:

## Implementation Claim

The repo-side Codex/A readiness surfaces now distinguish static dispatch configuration from live headless readiness. `scripts/verify_codex_dispatch.py --json` still reports the static registry/ACL/sandbox state, but it also reports the live no-window smoke state separately through `live_headless_ready`, `live_headless_reason`, `live_headless_failure_class`, and `live_headless_verification`.

The dispatcher live Codex gate now surfaces the observed Windows sandbox setup failure as `codex_windows_sandbox_setup_failed_0xc0000142` while preserving fail-closed suppression. The active disable guard was not cleared, Codex/A was not launched for PB work, and no sandbox/no-window requirement was weakened.

No repo-controlled `windows_subprocess.py` defect was found in this slice. The helper already supplies `pythonw`/hidden process behavior in the existing wrapper path. The current remaining blocker is external to the GT-KB dispatcher code: Codex CLI `v0.130.0-alpha.5` fails the workspace-write shell smoke with `windows sandbox: setup refresh failed with status exit code: 0xc0000142`, and the smoke evidence reports visible windows. Codex/A therefore remains quarantined until a fresh live no-window shell smoke passes.

## Files Changed

- `scripts/dispatcher_runtime.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`

Note: `platform_tests/scripts/test_dispatcher_runtime.py` also contains pre-existing local edits unrelated to WI-5065. This report covers only the Codex live-readiness classification and static-vs-live reporting changes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher tests verify Codex/A remains suppressed when the live no-window smoke is missing or failed, and accepts only fresh clean no-window evidence. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `test_codex_windows_dispatch_classifies_live_sandbox_setup_failure` verifies `0xc0000142` is surfaced as `codex_windows_sandbox_setup_failed_0xc0000142`. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `platform_tests/scripts/test_windows_subprocess.py` passed, preserving no-window helper behavior. No wrapper weakening was introduced. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex remains fail-closed when live smoke evidence is unsafe; no hook or dispatcher fallback bypass was added. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, ruff format-check, and live `verify_codex_dispatch.py --json` evidence are recorded below. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation began only after LO GO and `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5065-codex-live-sandbox-readiness` produced packet `sha256:18239c0551787df71824576b34c9842f3a85483e510b02fade2903b3f9d0e121`. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_windows_subprocess.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\dispatcher_runtime.py scripts\verify_codex_dispatch.py scripts\windows_subprocess.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_windows_subprocess.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\dispatcher_runtime.py scripts\verify_codex_dispatch.py scripts\windows_subprocess.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_windows_subprocess.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --json`

## Observed Results

- Focused WI-5065 pytest set: 187 passed.
- Ruff check on the six proposal target files: all checks passed.
- Ruff format check on the six proposal target files: 6 files already formatted.
- Live static-vs-headless readiness probe: `static_ok=true`, `static_dispatchable=true`, `dispatchable=true`, `live_headless_ready=false`, `live_headless_reason=codex_no_window_probe_detected_visible_window`, `live_headless_failure_class=codex_windows_sandbox_setup_failed_0xc0000142`.

## Runtime Evidence

The current `.gtkb-state/bridge-poller/codex-no-window-verification.json` still reports:

- `result=fail`
- `visible_window_detected=true`
- `probe=dispatcher_codex_no_window_live_shell_smoke_disable_plugins`
- `wrapper=scripts/run_with_status.py`
- `wrapper_executable=E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe`
- `wrapper_returncode=0`
- stderr/stdout preview includes `windows sandbox: setup refresh failed with status exit code: 0xc0000142`

This means the GT-KB wrapper launched and recorded evidence, but Codex's own workspace-write sandboxed shell execution failed. The safe dispatcher result remains `codex_dispatch_not_ready`.

## Acceptance Criteria Status

- [x] Static readiness and live headless readiness are reported separately for Codex/A.
- [x] Failed, missing, or visible-window live-smoke evidence keeps Codex/A suppressed with a clear reason.
- [x] The observed `0xc0000142` Windows sandbox setup failure is classified and surfaced as a Codex live-readiness blocker.
- [x] No repo-controlled no-window wrapper defect was identified in the authorized target path; existing wrapper/no-window tests remain green.
- [x] The Codex dispatcher disable guard remains uncleared because the fresh live smoke is still failing.
- [x] The implementation report includes focused test results and a truthful external-blocker report.

## Residual Blocker

Codex/A is not yet able to process PB work headlessly. The remaining blocker is the live Codex CLI workspace-write shell execution failure on Windows (`0xc0000142`) plus visible-window evidence. Clearing the dispatcher disable guard or bypassing workspace-write/no-window requirements would violate the GO scope and owner safety constraints.

## Risk And Rollback

Residual risk: Codex remains unavailable for headless PB dispatch until the external Codex CLI/Windows sandbox blocker is corrected and a fresh live no-window smoke passes. That is safer than launching visible windows or unsafe PB work.

Rollback: remove the live-readiness fields/classification additions from `scripts/verify_codex_dispatch.py` and `scripts/dispatcher_runtime.py`, and remove the added tests. Do not clear the disable guard as part of rollback.

## Loyal Opposition Asks

1. Verify that the repo now reports static vs live Codex readiness separately.
2. Verify that the dispatcher preserves fail-closed Codex/A suppression and surfaces `0xc0000142` as the live blocker.
3. Return VERIFIED if the external-blocker path satisfies WI-5065; otherwise return NO-GO with concrete findings.
