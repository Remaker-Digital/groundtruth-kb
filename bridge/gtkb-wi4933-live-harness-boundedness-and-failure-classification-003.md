NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Report - Live harness boundedness and failure classification

bridge_kind: implementation_report
Document: gtkb-wi4933-live-harness-boundedness-and-failure-classification
Version: 003
Responds to GO: bridge/gtkb-wi4933-live-harness-boundedness-and-failure-classification-002.md
Approved proposal: bridge/gtkb-wi4933-live-harness-boundedness-and-failure-classification-001.md
Recommended commit type: fix

## Implementation Claim

Implemented the approved WI-4933 boundedness and failure-classification follow-up. OpenRouter dispatch now has deterministic filesystem traversal bounds, skips large runtime/cache directories, stops repeated no-progress tool-call loops before max-turn exhaustion, and uses a lower unattended default turn ceiling. Dispatcher runtime and health classification now recognize repeated no-progress OpenRouter loops, Ollama/OpenRouter worker timeouts, and abrupt worker termination distinctly enough for release-health diagnosis.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`

## Owner Decisions / Input

- `DELIB-20266507` - active owner decision authorizing WI-4933 dispatcher backpressure health classification repair.
- Owner release directive in the active thread: continue testing and fixing dispatcher release blockers without waiting for manual processing.

## Prior Deliberations

- `bridge/gtkb-wi4933-live-harness-boundedness-and-failure-classification-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4933-live-harness-boundedness-and-failure-classification-002.md` - Loyal Opposition GO verdict.

## What Changed

- `scripts/openrouter_harness.py`
  - Reduced unattended `DEFAULT_MAX_TURNS` from 80 to 40 while preserving caller override.
  - Added `MAX_FILE_SCAN_ENTRIES`, skipped scan directories, and bounded traversal helpers.
  - Changed Grep and Glob to stream bounded filesystem traversal instead of materializing the entire workspace before result limits.
  - Added repeated tool-call signature detection and fail-closed `OpenRouterHarnessError("repeated no-progress tool loop before final assistant text")`.
- `scripts/dispatcher_runtime.py`
  - Added repeated no-progress OpenRouter marker to fatal worker output classification as `max_turn_exhaustion`.
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
  - Added `worker_timeout` to runtime failure classes.
  - Added recent-run markers for repeated no-progress tool loops and Ollama/OpenRouter session timeouts.
  - Classified exit code `4294967295` as `process_terminated_abruptly` and exit code `124` as `worker_timeout`.
- `platform_tests/scripts/test_openrouter_harness.py`
  - Added regressions for bounded Grep, runtime-directory-pruned Glob, and repeated no-progress loop termination.
- `platform_tests/scripts/test_dispatcher_runtime.py`
  - Added fatal marker classification regression for repeated no-progress OpenRouter output.
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`
  - Added recent-run classification tests for Ollama timeout and abrupt termination.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py` verifies health classification for recent Ollama timeout and abrupt worker termination. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Combined focused dispatcher/hook bundle passed; `gt bridge dispatch health --json` returned PASS after implementation with a safe selected LO lane. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | No retired trigger fallback was introduced; dispatcher health/status still route through `gt bridge dispatch` and selected daemon-backed state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation proceeded after `bridge/gtkb-wi4933-live-harness-boundedness-and-failure-classification-002.md` GO and implementation authorization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps each linked spec to executed command evidence and observed results. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py::test_wi4933_repeated_no_progress_marker_is_max_turn_failure platform_tests\scripts\test_ollama_dispatch.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_windows_subprocess.py -q --tb=short`
- `python -m ruff check .codex\gtkb-hooks\run_py_no_window.py scripts\openrouter_harness.py scripts\dispatcher_runtime.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_windows_subprocess.py`
- `python -m ruff format --check .codex\gtkb-hooks\run_py_no_window.py scripts\openrouter_harness.py scripts\dispatcher_runtime.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_windows_subprocess.py`
- `gt bridge dispatch health --json`
- `gt bridge dispatch status --json`

## Observed Results

- Combined focused dispatcher/hook bundle: 57 passed in 6.89s.
- Ruff check: `All checks passed!`
- Ruff format check: `10 files already formatted`
- Dispatcher health: PASS, with Antigravity C selected as the sole current LO lane and Codex A selected as PB.
- Dispatcher status: PASS, with no runtime health findings for the selected C LO lane; old D/E/F lanes remain disabled in current dispatcher eligibility pending broader live retest.

## Files Changed

- `scripts/openrouter_harness.py`
- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

Note: `platform_tests/scripts/test_ollama_dispatch.py` remains dirty from pre-existing in-scope dispatcher work and was included in verification, but this implementation did not require additional edits there.

## Acceptance Criteria Status

- [x] OpenRouter Grep and Glob stop traversal with deterministic bounds and do not materialize whole-workspace scans before result limits.
- [x] OpenRouter repeated no-progress tool calls become a bounded, diagnosed failure before silent long-spin exhaustion.
- [x] Ollama pre-turn timeout is classified as `worker_timeout`.
- [x] Abrupt/manual worker termination exit code `4294967295` is classified as `process_terminated_abruptly`.
- [x] Focused tests pass for OpenRouter traversal bounds, OpenRouter loop bounds, dispatcher runtime marker classification, Ollama dispatch coverage, and bridge dispatch health CLI classification.
- [x] `gt bridge dispatch health --json` reports PASS for the currently selected safe LO topology.
- [ ] D/E/F lanes are not yet re-enabled in release topology. This report closes the boundedness/classification implementation slice, not the full all-harness live permutation proof.

## Risk And Rollback

Residual risk is medium until D/E/F are re-enabled and live-tested under the dispatcher after this slice is verified. The code now bounds and classifies the known D/F failure family, but the release program still needs live retest and any separate Cursor child-fanout remediation.

Rollback is a revert of the OpenRouter, dispatcher-runtime, health-classification, and focused-test changes. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if this boundedness/classification slice satisfies the approved proposal, otherwise return NO-GO with concrete findings.
