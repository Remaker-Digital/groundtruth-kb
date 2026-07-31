NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Proposal - Codex hook parent-shell leak containment

bridge_kind: prime_proposal
Document: gtkb-wi4896-codex-hook-parent-leak-containment
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4896

target_paths: [".codex/hooks.json", ".codex/gtkb-hooks/run_cmd_no_window.py", ".codex/gtkb-hooks/run_py_no_window.py", ".codex/gtkb-hooks/run_cmd_no_window", ".codex/gtkb-hooks/run_py_no_window", "scripts/windows_subprocess.py", "platform_tests/scripts/test_codex_hook_runtime_containment.py", "platform_tests/scripts/test_windows_subprocess.py"]

implementation_scope: hook_upgrade
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Live release-health testing found a residual Codex hook containment defect after the console-window storm fix. The hook commands now invoke `pythonw.exe` wrappers, but process snapshots still showed Codex-owned `pwsh.exe -NoProfile -Command "E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe ..."` parent shells for `implementation-start-gate.cmd` and `bridge-compliance-audit.cmd`. The no-window wrappers control their child process creation, but they do not guarantee that the shell process Codex creates around the command string exits promptly or stays invisible.

This is release-blocking because the user has stated there is no acceptable case where GT-KB automation spawns visible or lingering console windows. Hook governance must remain enabled, but its invocation form must not leak parent shells.

## Claim

Prime Builder proposes a bounded `WI-4896` follow-up under the active console-window suppression authorization: preserve the Codex hook governance set, but make hook invocation and wrapper tests prove that no hook command path depends on a lingering parent shell or visible console process.

## Requirement Sufficiency

Existing requirements are sufficient. `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION` is active, includes `WI-4896`, and allows `source`, `test`, and `hook_upgrade` mutation classes for no-window dispatcher and hook-surface changes. The owner has also given a standing release-blocker directive that any console-window spawn path must be diagnosed and corrected before release.

## In-Root Placement Evidence

All target paths are root-relative GT-KB files under `E:\GT-KB`. No out-of-root hook or workstation profile file is in scope.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - automated bridge/dispatcher work must be daemon-owned and reliable without disruptive desktop process storms.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher success path is the daemon; hook-triggered bridge automation and retired trigger paths are not fallback options.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher and hook execution must be background/no-window safe.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook behavior differs from Claude and must use explicit parity/fallback discipline backed by tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation changes require approved bridge authorization and role-correct filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal cites concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must map each linked spec to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal declares project authorization, project, work item, and target paths.

## Prior Deliberations

- `DELIB-20266297` - owner authorization for WI-4896 dispatcher console-window suppression, recorded in the active PAUTH.

## Owner Decisions / Input

- `DELIB-20266297` - active owner-decision evidence for no-window hook/dispatcher containment.
- Owner directive in this release thread: no GT-KB automation path may spawn visible console windows; this is a release blocker.

## Cross-Harness Disposition

This proposal touches the Codex hook surface only. It does not waive parity for Claude, Cursor, Antigravity, Ollama, or OpenRouter. It also does not restore the retired cross-harness trigger or single-harness bridge automation path. Verification must keep Codex hooks active and must use the normal dispatcher as the only automated bridge-dispatch success path.

## Evidence From Live Test

- After Codex restart with hooks restored, `.codex/hooks.json` registered `PreToolUse`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, and `Stop` commands through `pythonw.exe` plus `run_cmd_no_window` or `run_py_no_window`.
- Live process inspection found stale parent shells whose command lines were `pwsh.exe -NoProfile -Command "E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe E:\GT-KB\.codex\gtkb-hooks\run_cmd_no_window E:\GT-KB\.codex\gtkb-hooks\implementation-start-gate.cmd"` and the same pattern for `bridge-compliance-audit.cmd`.
- Focused wrapper tests already pass for child-process no-window flags, but they do not assert the hook command shape avoids parent-shell leakage.
- Therefore the remaining defect is the hook invocation boundary, not the already-tested child wrapper internals alone.

## Proposed Scope

- Change the Codex hook command surface or wrapper boundary so hook execution does not leave a live `pwsh.exe` or visible console parent behind.
- Preserve all currently required governance hooks unless a specific hook is proven defective and separately replaced by an equivalent governed path.
- Add regression tests that inspect `.codex/hooks.json` command strings and wrapper behavior for parent-shell containment, not only child-process flags.
- Add or extend Windows subprocess helper tests if shared helper behavior changes.
- Confirm the final command surface still runs bounded, no-window, and with the same hook semantics.

## Out Of Scope

- Disabling Codex governance hooks as the release fix.
- Restoring the purged cross-harness trigger or single-harness bridge automation.
- Changing dispatcher topology or provider credentials.
- Editing user-level terminal profiles, Windows settings, or out-of-root Codex configuration.
- Retiring or waiving any harness.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run dispatcher health/status after hook containment to confirm hook changes do not reintroduce trigger-based dispatch or disable daemon state publication. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Search load-bearing hook/config/source surfaces for retired trigger invocation and confirm no fallback trigger path is restored. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Add and run tests proving Codex hook command paths are no-window and do not rely on a lingering parent shell. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run focused Codex hook containment/parity tests for `.codex/hooks.json` and wrappers. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use bridge GO and implementation authorization before protected hook/source/test edits. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map every linked spec to exact tests and observed outputs before requesting VERIFIED. |

## Pre-Filing Preflights

This bridge write is filed through the Codex apply-patch bridge-compliance adapter. That adapter runs the pending content-file applicability preflight and ADR/DCL clause preflight before accepting the `bridge/` write. Prime Builder will also cite exact preflight and test outputs in the implementation report.

## Acceptance Criteria

- `.codex/hooks.json` remains populated with the required governance hooks, but the hook command surface no longer leaves a `pwsh.exe` or console-window parent process behind during ordinary tool use.
- Focused tests fail on a shell-leaking hook command shape and pass after the fix.
- Existing no-window wrapper tests still pass.
- No retired trigger or single-harness automation fallback reference becomes live again.
- `gt bridge dispatch health --json` no longer shows console-spawn or hook-leak evidence attributable to Codex hook execution.

## Risks / Rollback

Risk is moderate because Codex hook invocation is part of the governance safety surface. The intended change is constrained to invocation containment and tests, not governance policy removal.

Rollback is a revert of the hook command/wrapper/test changes. Bridge files remain append-only audit evidence.

## Files Expected To Change

- `.codex/hooks.json`
- `.codex/gtkb-hooks/run_cmd_no_window.py`
- `.codex/gtkb-hooks/run_py_no_window.py`
- `.codex/gtkb-hooks/run_cmd_no_window`
- `.codex/gtkb-hooks/run_py_no_window`
- `scripts/windows_subprocess.py`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`
- `platform_tests/scripts/test_windows_subprocess.py`

## Recommended Commit Type

fix
