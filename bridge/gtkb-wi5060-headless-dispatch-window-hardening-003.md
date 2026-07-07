NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex interactive Prime Builder; owner-authorized metadata-defective GO override

bridge_kind: implementation_report
Document: gtkb-wi5060-headless-dispatch-window-hardening
Version: 003
Author: Prime Builder (Codex)
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060

target_paths: ["scripts/dispatcher_runtime.py", "scripts/run_with_status.py", "scripts/windows_subprocess.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_run_with_status.py", "platform_tests/scripts/test_windows_subprocess.py"]

implementation_scope: source | tests | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# WI-5060 Headless Dispatch Window Hardening Implementation Report

## Summary

Implemented the owner-authorized headless dispatch fix for A, C, D, and F worker launches. The fix strengthens the Windows subprocess launch contract used by dispatcher-owned workers without changing harness role assignment, provider routing, model selection, turn budgets, worker lifetime budgets, or credential handling.

Because `bridge/gtkb-wi5060-headless-dispatch-window-hardening-002.md` contains a substantive `GO` but is missing required author metadata, this implementation proceeded only after Mike explicitly authorized the headless fix in chat. The work remained limited to the `001` proposal target paths.

## Implementation Details

- Added shared Windows hidden-process helpers in `scripts/windows_subprocess.py`:
  - `windows_hidden_process_creationflags(new_process_group=True, detached=True)` composes `CREATE_NO_WINDOW`, `CREATE_NEW_PROCESS_GROUP`, and `DETACHED_PROCESS`.
  - `hidden_startupinfo()` sets `STARTF_USESHOWWINDOW` and `SW_HIDE`.
  - `hidden_process_popen_kwargs()` returns reusable hidden `Popen` kwargs for dispatcher launch sites.
- Updated `scripts/dispatcher_runtime.py` so the outer `run_with_status.py` wrapper launch and post-dispatch poll subprocess use hidden detached Windows launch kwargs.
- Updated `scripts/run_with_status.py` so the inner wrapped harness child launch uses:
  - sibling `pythonw.exe` preference when applicable,
  - `CREATE_NO_WINDOW`,
  - `CREATE_NEW_PROCESS_GROUP`,
  - `DETACHED_PROCESS`,
  - hidden `STARTUPINFO`.
- Preserved non-Windows behavior and the POSIX `start_new_session` process-group reaping path.
- Preserved timeout process-tree termination behavior.
- Added/updated focused tests for the shared helper, dispatcher wrapper launch, Antigravity stdin dispatch wrapper shape, and `run_with_status.py` Windows/off-Windows launch kwargs.

## Files Changed

- `scripts/windows_subprocess.py`
- `scripts/dispatcher_runtime.py`
- `scripts/run_with_status.py`
- `platform_tests/scripts/test_windows_subprocess.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_run_with_status.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require bridge authority; this report documents the owner-authorized override of the metadata-defective `002` GO.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation stayed inside WI-5060 reliability repair authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH did not bypass bridge evidence; the override is explicitly recorded.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal, work item, PAUTH, target paths, and verification are linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries Project Authorization, Project, and Work Item headers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification evidence below maps each implementation claim to tests or static audit evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned worker launch control remains centralized in `dispatcher_runtime.py` and `run_with_status.py`.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - the no-window audit and dispatcher-runtime tests verify the dispatcher launch surface without enabling live dispatch.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, rotation, or provider account mutation occurred.

## Owner Decisions / Input

Mike authorized the one-time headless fix after being shown the evidence package:

- The substantive `002` GO exists but lacks required author metadata.
- The target paths are the narrow `001` proposal paths.
- The remaining owner-observed issue was visible console windows during worker launches.

This authorization was used only for the headless launch hardening described here.

## Spec-Derived Verification

| Spec / requirement | Evidence | Result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / headless dispatcher worker launch | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_windows_subprocess.py platform_tests/scripts/test_dispatcher_runtime.py::test_spawn_harness_uses_no_window_python_for_status_wrapper platform_tests/scripts/test_dispatcher_runtime.py::test_antigravity_stdin_dispatch_removes_prompt_from_child_argv platform_tests/scripts/test_run_with_status.py::test_popen_uses_create_no_window_on_windows_via_monkeypatch platform_tests/scripts/test_run_with_status.py::test_popen_uses_no_creationflags_off_windows platform_tests/scripts/test_run_with_status.py::test_windows_python_command_uses_sibling_pythonw_when_available platform_tests/scripts/test_run_with_status.py::test_windows_python_command_falls_back_when_pythonw_missing -q --tb=short --basetemp .test-tmp\pytest-headless` with pytest cacheprovider disabled | `9 passed, 1 warning` |
| Release-runtime no-window audit | `groundtruth-kb\.venv\Scripts\python.exe scripts\windows_no_window_spawn_audit.py --json scripts/run_with_status.py scripts/dispatcher_runtime.py scripts/windows_subprocess.py` | `release_ready: true`, `violation_count: 0` |
| Existing OpenRouter/F default-model and Ollama/D max-turn regression coverage | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_dispatcher_budget_constants_regression.py -q --tb=short --basetemp .test-tmp\pytest-wi5060-shims` with pytest cacheprovider disabled | `93 passed, 1 warning` |
| Formatting and lint | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/windows_subprocess.py scripts/dispatcher_runtime.py scripts/run_with_status.py platform_tests/scripts/test_windows_subprocess.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py`; `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/windows_subprocess.py scripts/dispatcher_runtime.py scripts/run_with_status.py platform_tests/scripts/test_windows_subprocess.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py` | `All checks passed!`; `6 files already formatted` |

## Verification Notes

- An initial focused pytest invocation failed before test execution for six tests because pytest attempted to use `C:\Users\micha\AppData\Local\Temp\pytest-of-micha` and received `PermissionError: [WinError 5] Access is denied`. The same tests passed after redirecting `TMP`, `TEMP`, and `--basetemp` inside `E:\GT-KB\.test-tmp`.
- I did not rerun live dispatcher or A/C/D/F harness dispatch after this fix because the owner had just observed visible console flashes from harness invocations. The post-fix evidence therefore proves the launch contract through local unit tests and static release-runtime audit rather than by spawning new live harness workers.

## Acceptance Status

- Dispatcher-owned worker launch code now uses a stronger hidden Windows launch contract than `CREATE_NO_WINDOW` alone.
- The `run_with_status.py` inner child launch still prefers sibling `pythonw.exe` when available.
- Worker lifetime timeout and process-tree termination behavior are preserved.
- Focused unit tests, static no-window audit, lint, format, and existing WI-5060 shim regression tests pass.
- No credential, provider, role-assignment, or dispatch-eligibility changes were made in this headless follow-on.

## Residual Risk

The only residual risk is that post-fix live A/C/D/F visual dispatch was not rerun to avoid producing more visible windows during this repair session. The changed launch contract is directly asserted by tests and the release-runtime static audit, so Loyal Opposition can choose whether that is sufficient or whether to request a final owner-observed live smoke in a controlled step.

## Recommended Next Step

Loyal Opposition should verify this report against the six changed target paths and decide whether the unit/static evidence is sufficient for `VERIFIED` or whether a controlled live visual smoke is required.

Recommended commit type: `fix(harness):`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
