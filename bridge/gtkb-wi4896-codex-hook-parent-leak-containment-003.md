NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Report - Codex hook parent-shell leak containment

bridge_kind: implementation_report
Document: gtkb-wi4896-codex-hook-parent-leak-containment
Version: 003
Responds to GO: bridge/gtkb-wi4896-codex-hook-parent-leak-containment-002.md
Approved proposal: bridge/gtkb-wi4896-codex-hook-parent-leak-containment-001.md
Recommended commit type: fix

## Implementation Claim

Implemented the approved WI-4896 hook containment follow-up. The durable Codex hook registry now uses one hidden `pythonw.exe` launcher command per event or matcher, and multi-hook fanout is moved inside `.codex/gtkb-hooks/run_py_no_window.py` batch execution. The batch catalog preserves the governance hooks while removing the prior many-command Codex hook registration shape that amplified parent-shell creation.

The implementation also adds extensionless launcher shims used by the durable registry, shared no-window subprocess helpers, and regression coverage for registry shape, extensionless shims, batch target existence, and Windows no-window helper behavior. During verification, two stale old-shape parent-shell rows were still visible through WMI from this already-running Codex session, but direct `Get-Process` checks could not find live killable processes for those PIDs. This is consistent with Codex retaining pre-change hook commands in memory until reload or restart; the release artifact on disk no longer registers those old fanout commands.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`

## Owner Decisions / Input

- `DELIB-20266297` - active owner decision authorizing WI-4896 dispatcher console-window suppression.
- Owner release directive in the active thread: no GT-KB automation path may spawn visible console windows; this remains a release blocker until verified after hook reload/restart.

## Prior Deliberations

- `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-002.md` - Loyal Opposition GO verdict.

## What Changed

- `.codex/hooks.json` now registers a single `pythonw.exe ... run_py_no_window` command per Codex hook event or matcher.
- `.codex/gtkb-hooks/run_py_no_window.py` now supports `--batch <name>` with governed batches for `user-prompt-submit`, `pretooluse-bash`, `pretooluse-apply-patch`, `posttooluse-bash`, `posttooluse-apply-patch`, and `stop`.
- Batch paths were corrected to use `scripts/bridge_verified_backlog_reconciler.py` and `scripts/advisory_grilling_gate_lint.py` where those scripts actually live.
- The Codex Python hook child timeout default was raised from 4 seconds to 10 seconds because the project-completion surface completes successfully but can take about 5 seconds on the current worktree.
- `.codex/gtkb-hooks/run_py_no_window` and `.codex/gtkb-hooks/run_cmd_no_window` extensionless shims delegate to the tracked Python wrappers.
- `scripts/windows_subprocess.py` provides shared Windows no-window creation flags and `pythonw.exe` preference logic.
- `platform_tests/scripts/test_codex_hook_runtime_containment.py` now verifies durable hook registry shape, forbids retired trigger registrations, verifies extensionless shims, rejects unknown batches, and checks that every batch target exists.
- `platform_tests/scripts/test_windows_subprocess.py` verifies Windows no-window subprocess helper behavior.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch health --json` returned `health_status: PASS` with Antigravity C selected as LO and Codex A selected as PB. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | `platform_tests/scripts/test_codex_hook_runtime_containment.py` asserts `.codex/hooks.json` commands contain no `cross_harness_bridge_trigger.py`, `single_harness_bridge_automation.py`, `single_harness_bridge_dispatcher.py`, `bridge-dispatch-trigger`, `dispatcher-daemon.cmd`, or `gtkb_dispatcher_daemon.py`. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Direct batch probe executed all six Codex hook batches with hidden process settings; all exited 0 after path and timeout fixes. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Focused hook parity/containment tests passed: `platform_tests/scripts/test_codex_hook_runtime_containment.py` plus `platform_tests/scripts/test_windows_subprocess.py`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation proceeded after `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-002.md` GO and implementation authorization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps each linked spec to executed command evidence and observed results. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_windows_subprocess.py -q --tb=short`
- `python -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py::test_wi4933_repeated_no_progress_marker_is_max_turn_failure platform_tests\scripts\test_ollama_dispatch.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_windows_subprocess.py -q --tb=short`
- `python -m ruff check .codex\gtkb-hooks\run_py_no_window.py scripts\openrouter_harness.py scripts\dispatcher_runtime.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_windows_subprocess.py`
- `python -m ruff format --check .codex\gtkb-hooks\run_py_no_window.py scripts\openrouter_harness.py scripts\dispatcher_runtime.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_windows_subprocess.py`
- Direct batch probe over `user-prompt-submit`, `pretooluse-bash`, `pretooluse-apply-patch`, `posttooluse-bash`, `posttooluse-apply-patch`, and `stop` using `run_py_no_window --batch <name>` with hidden process settings and `{}` stdin.
- `gt bridge dispatch health --json`
- `gt bridge dispatch status --json`

## Observed Results

- Focused WI-4896 tests: 11 passed in 1.29s.
- Combined focused dispatcher/hook bundle: 57 passed in 6.89s.
- Ruff check: `All checks passed!`
- Ruff format check: `10 files already formatted`
- Direct batch probe: all six batches exited 0. Observed user-prompt stdout was `{}`-style hook no-op payload output; stderr was empty after the path and timeout corrections.
- Dispatcher health: PASS, with Antigravity C selected as the sole current LO lane and Codex A selected as PB.

## Files Changed

- `.codex/hooks.json`
- `.codex/gtkb-hooks/run_py_no_window.py`
- `.codex/gtkb-hooks/run_py_no_window`
- `.codex/gtkb-hooks/run_cmd_no_window`
- `scripts/windows_subprocess.py`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`
- `platform_tests/scripts/test_windows_subprocess.py`

## Acceptance Criteria Status

- [x] `.codex/hooks.json` remains populated with governance hooks, but durable hook fanout is collapsed to one hidden launcher command per event or matcher.
- [x] Focused tests fail on missing batch target paths and pass with the corrected catalog.
- [x] Existing no-window wrapper tests pass.
- [x] Retired trigger and single-harness automation fallback references are not present in durable Codex hook commands.
- [x] Dispatcher health remains PASS with the current safe LO lane.
- [ ] A fresh Codex process must reload `.codex/hooks.json` before claiming that the current interactive process no longer has old in-memory hook commands. This is a runtime reload caveat, not an on-disk release artifact defect.

## Risk And Rollback

Residual risk is medium until a fresh Codex process proves that the new durable hook registry no longer produces visible console windows. The current implementation reduces durable hook fanout and fixes batch correctness, but it cannot rewrite hook commands already loaded in the currently running Codex process.

Rollback is a revert of `.codex/hooks.json`, `.codex/gtkb-hooks/run_py_no_window.py`, the extensionless shims, `scripts/windows_subprocess.py`, and the two focused test files. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the durable hook registry, batch catalog, extensionless shims, and focused tests.
2. Treat the current-session in-memory hook caveat explicitly: return VERIFIED only if durable release-state suffices, or NO-GO if fresh-process proof is mandatory before release closure.
