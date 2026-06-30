NEW

# gtkb-wi4905-codex-hook-runtime-stall-containment - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4905-codex-hook-runtime-stall-containment
Version: 003
Responds to GO: bridge/gtkb-wi4905-codex-hook-runtime-stall-containment-002.md
Approved proposal: bridge/gtkb-wi4905-codex-hook-runtime-stall-containment-001.md
Author: Prime Builder (Codex harness A)
Date: 2026-06-30T01:10:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4905
Recommended commit type: fix:

## Implementation Claim

Implemented the approved Codex hook runtime stall containment slice. The release-facing behavior is now:

- `.codex/hooks.json` is intentionally empty during containment, so project hooks cannot trigger another Codex hook storm while the release blocker is being closed.
- `.codex/gtkb-hooks/run_cmd_no_window.py` now reads hook stdin with a short bounded wait, launches child `.cmd` hooks with hidden-window and new-process-group flags, captures stdout/stderr, preserves child exit status, and kills the Windows process tree on internal timeout with exit `124`.
- `.codex/gtkb-hooks/run_py_no_window.py` was added with the same bounded stdin, output preservation, timeout, and process-tree kill semantics for `.py` hook targets.
- `.codex/gtkb-hooks/workstream-focus.cmd` and `.codex/gtkb-hooks/formal-artifact-approval.cmd` no longer start with UTF-8 BOM bytes.
- Focused regression coverage now proves the empty containment registry, finite stdin forwarding, output/exit preservation, timeout behavior, and BOM cleanup.
- Existing Codex/Cursor hook parity tests were kept compatible with the temporary empty Codex hook registry and with Cursor's no-window wrapper expectations.

Root cause confirmed for this slice: the previously verified static no-window shape still allowed runtime stalls because `run_cmd_no_window.py` inherited/depended on hook stdin behavior and had no internal child timeout or process-tree reap. When Codex project hooks fired repeatedly, wrapper/child trees could accumulate and block Codex tool execution. The containment keeps active Codex hooks offline and hardens the shared wrapper path before any future governed re-enable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires bridge proposal, GO, implementation report, and verification before protected hook/config/test edits.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires concrete governing links for implementation proposals.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project, and work item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires report evidence mapped to cited requirements.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Requires Windows desktop/background dispatch and hook paths to avoid visible console storms and unattended process accumulation.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - Requires harness-surface parity behavior to be tested or explicitly waived.

## Owner Decisions / Input

No new owner decision is required by this implementation report. The proposal carried forward the owner directive that no new console window should spawn, that the console storm is a release showstopper, and that Harness Parity Phase 2 repairs are release-blocking. The live project authorization and GO verdict bound this implementation to the exact target paths listed in the proposal.

## Prior Deliberations

- `bridge/gtkb-wi4905-codex-hook-runtime-stall-containment-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4905-codex-hook-runtime-stall-containment-002.md` - independent Antigravity Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi4905-codex-hook-no-window-parity-001.md` through `bridge/gtkb-wi4905-codex-hook-no-window-parity-004.md` - prior static no-window parity work; this report covers the runtime stall/orphan gap found after that verification.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi4905-codex-hook-runtime-stall-containment --json` returned latest status `GO`; `python scripts\implementation_authorization.py validate ...` returned `"authorized": true` for the eight implementation targets. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward every linked specification from the approved proposal and maps each to executed evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries forward `Project Authorization`, `Project`, and `Work Item` metadata from the approved proposal; implementation authorization validation succeeded. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest coverage and code-quality gates below were executed after the implementation. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `test_codex_hook_runtime_containment.py` verifies empty Codex hook containment, bounded stdin, timeout exit `124`, output/exit preservation, and BOM cleanup; the live process scan returned `[]`. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `test_cursor_hook_headless_parity.py` and `test_codex_hook_parity.py` passed under the containment shape: `16 passed, 4 skipped`. |

## Commands Run

- `git status --short`
- `gt bridge show gtkb-wi4905-codex-hook-runtime-stall-containment --json`
- `python scripts\bridge_claim_cli.py status gtkb-wi4905-codex-hook-runtime-stall-containment`
- `python scripts\implementation_authorization.py validate --target .codex\hooks.json --target .codex\gtkb-hooks\run_cmd_no_window.py --target .codex\gtkb-hooks\run_py_no_window.py --target .codex\gtkb-hooks\workstream-focus.cmd --target .codex\gtkb-hooks\formal-artifact-approval.cmd --target platform_tests\scripts\test_codex_hook_runtime_containment.py --target platform_tests\scripts\test_codex_hook_parity.py --target platform_tests\scripts\test_cursor_hook_headless_parity.py`
- `python -m json.tool .codex\hooks.json`
- `python -m py_compile .codex\gtkb-hooks\run_cmd_no_window.py .codex\gtkb-hooks\run_py_no_window.py`
- `python -m pytest platform_tests\scripts\test_codex_hook_runtime_containment.py -q --tb=short`
- `python -m pytest platform_tests\scripts\test_cursor_hook_headless_parity.py platform_tests\scripts\test_codex_hook_parity.py -q --tb=short`
- `python -m ruff check .codex\gtkb-hooks\run_cmd_no_window.py .codex\gtkb-hooks\run_py_no_window.py platform_tests\scripts\test_codex_hook_runtime_containment.py`
- `python -m ruff format --check .codex\gtkb-hooks\run_cmd_no_window.py .codex\gtkb-hooks\run_py_no_window.py platform_tests\scripts\test_codex_hook_runtime_containment.py`
- PowerShell `Get-CimInstance Win32_Process` scan for the prior Codex hook wrapper/handler command patterns.

## Observed Results

- Bridge state: latest path `bridge/gtkb-wi4905-codex-hook-runtime-stall-containment-002.md`, latest status `GO`.
- Work-intent claim: held by this Prime Builder session, not expired at the time of implementation checks.
- Implementation authorization: `"authorized": true` for all eight target paths.
- `.codex/hooks.json`: valid JSON with exactly `{ "hooks": {} }`.
- `py_compile`: passed for `run_cmd_no_window.py` and `run_py_no_window.py`.
- `python -m pytest platform_tests\scripts\test_codex_hook_runtime_containment.py -q --tb=short`: `5 passed in 1.38s`.
- `python -m pytest platform_tests\scripts\test_cursor_hook_headless_parity.py platform_tests\scripts\test_codex_hook_parity.py -q --tb=short`: `16 passed, 4 skipped in 0.98s`.
- `python -m ruff check ...`: `All checks passed!`
- `python -m ruff format --check ...`: `3 files already formatted`.
- Live hook process scan: `[]`, with no matching live processes for the prior Codex wrapper/handler storm patterns.

## Files Changed

Implementation scope is limited to the approved WI-4905 target set:

- `.codex/hooks.json`
- `.codex/gtkb-hooks/run_cmd_no_window.py`
- `.codex/gtkb-hooks/run_py_no_window.py`
- `.codex/gtkb-hooks/workstream-focus.cmd`
- `.codex/gtkb-hooks/formal-artifact-approval.cmd`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`
- `platform_tests/scripts/test_codex_hook_parity.py`
- `platform_tests/scripts/test_cursor_hook_headless_parity.py`

The broader worktree contains many unrelated release/parity changes. They are intentionally excluded from this report and must not be treated as verified by this WI-4905 verification request.

## Acceptance Criteria Status

- [x] `.codex/hooks.json` is valid and intentionally empty for containment.
- [x] `run_cmd_no_window.py` and `run_py_no_window.py` pass finite hook payloads to children instead of inheriting open stdin.
- [x] Both wrappers enforce an internal timeout and return `124` on child timeout.
- [x] Both wrappers preserve child stdout/stderr and exit status.
- [x] BOM-bearing Codex `.cmd` wrappers are normalized to plain ASCII/UTF-8 without BOM.
- [x] Focused regression tests and lint/format checks pass.
- [x] A process scan after probes finds no live orphan hook processes.

## Recommended Commit Type

Recommended commit type: `fix:`

Justification: this is a repair to broken Codex hook runtime behavior that caused visible console storms and Codex stalls; it does not add a new user-facing capability.

## Risk And Rollback

Residual risk: while `.codex/hooks.json` is intentionally empty, Codex-side project hook enforcement is offline. Mitigation: this is a deliberate containment state for a release-blocking incident; Prime Builder self-enforced bridge and implementation-start authorization for this work, and a later governed slice must re-enable only a minimal hook set after runtime safety is proven.

Rollback: restore the prior `.codex/hooks.json` and wrapper versions from git only after terminating any hook process trees. Do not re-enable Codex project hooks without a new governed proposal and runtime verification.

## Loyal Opposition Asks

1. Verify that the implementation matches the approved WI-4905 scope and excludes unrelated worktree changes.
2. Verify the command evidence and spec-to-test mapping above.
3. Return `VERIFIED` if satisfied, or `NO-GO` with findings.
