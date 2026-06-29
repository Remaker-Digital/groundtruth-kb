NEW

# GT-KB Bridge Implementation Report - gtkb-wi4905-codex-hook-no-window-parity - 003

bridge_kind: implementation_report
Document: gtkb-wi4905-codex-hook-no-window-parity
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4905-codex-hook-no-window-parity-002.md
Approved proposal: bridge/gtkb-wi4905-codex-hook-no-window-parity-001.md
Recommended commit type: fix:

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

## Implementation Claim

Implemented the Codex no-window hook repair approved in -002. Active Codex hook
commands in `.codex/hooks.json` now start through `pythonw.exe`, and `.cmd`
hook targets are invoked through `.codex/gtkb-hooks/run_cmd_no_window.py` so
the child command runs with `CREATE_NO_WINDOW` on Windows while preserving exit
codes.

No provider credentials, dispatcher routing policy, durable role assignments,
or non-Codex harness hooks were changed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`

## Owner Decisions / Input

No new owner decision was required. This remains inside
`PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` and the owner
directive that no routine hook path should spawn visible console windows.

## Prior Deliberations

- `bridge/gtkb-wi4905-codex-hook-no-window-parity-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4905-codex-hook-no-window-parity-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py validate --target .codex/hooks.json --target .codex/gtkb-hooks/run_cmd_no_window.py --target platform_tests/scripts/test_cross_harness_bridge_trigger.py` -> authorized true. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`; `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_codex_hook_commands_do_not_use_foreground_console_launchers -q --tb=short` -> 1 passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short` -> 153 passed. |
| Lint/format quality | `python -m ruff check .codex/gtkb-hooks/run_cmd_no_window.py platform_tests/scripts/test_cross_harness_bridge_trigger.py` -> All checks passed. `python -m ruff format --check .codex/gtkb-hooks/run_cmd_no_window.py platform_tests/scripts/test_cross_harness_bridge_trigger.py` -> 2 files already formatted. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target .codex/hooks.json --target .codex/gtkb-hooks/run_cmd_no_window.py --target platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_codex_hook_commands_do_not_use_foreground_console_launchers -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check .codex\gtkb-hooks\run_cmd_no_window.py platform_tests\scripts\test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check .codex\gtkb-hooks\run_cmd_no_window.py platform_tests\scripts\test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short`

## Observed Results

- Authorization packet accepted the three touched targets.
- The no-window guard test now passes; it previously failed with 28 foreground
  hook commands.
- The broader dispatcher/hook focused bundle now reports `153 passed`.
- Ruff check and format-check pass for the touched Python wrapper/test file.

## Files Changed

- `.codex/hooks.json` - active hook commands now launch via `pythonw.exe`.
- `.codex/gtkb-hooks/run_cmd_no_window.py` - new wrapper for `.cmd` hooks using `CREATE_NO_WINDOW` on Windows.

`platform_tests/scripts/test_cross_harness_bridge_trigger.py` was formatted by
Ruff but its no-window assertion logic was not relaxed.

## Acceptance Criteria Status

- [x] No active Codex hook command starts with `python`, `cmd /d /s /c`, `powershell.exe`, or `pwsh.exe`.
- [x] Active Codex hook commands contain `pythonw.exe`, satisfying the existing static release guard.
- [x] `.cmd` hooks preserve exit-code behavior through the no-window wrapper.
- [x] Focused no-window guard test passes.
- [x] Broader dispatcher/hook focused bundle passes.

## Risk And Rollback

Risk: `pythonw.exe` suppresses stdout/stderr visibility for hook commands. That
is acceptable for this hook surface because status is already communicated
through hook status messages and persisted hook artifacts. Rollback is a single
commit reverting `.codex/hooks.json` and removing
`.codex/gtkb-hooks/run_cmd_no_window.py`.

## Loyal Opposition Asks

1. Verify `.codex/hooks.json` uses no-window launch commands for all active hooks.
2. Verify the new wrapper preserves `.cmd` hook exit codes without opening a console window.
3. Return VERIFIED if the evidence satisfies WI-4905 slice 1; otherwise return NO-GO with specific findings.
