NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex interactive Prime Builder

bridge_kind: prime_proposal
Document: gtkb-wi5060-headless-dispatch-window-hardening
Version: 001
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

# WI-5060 Follow-On: Headless Dispatch Window Hardening

## Summary

This proposal requests a narrow follow-on GO for the remaining WI-5060 acceptance gap: dispatcher-spawned A, C, D, and F workers must run headlessly and must not surface visible console windows while processing their currently assigned roles.

The earlier WI-5060 shim proposal and implementation report repaired OpenRouter/F default-model payload omission, blank-final-output handling, Ollama/D no-progress loop termination, direct live smokes, and D/F dispatch re-enablement. After that work, Mike clarified that the remaining problem is not the worker count; the problem is that the spawned workers were not headless.

Current inspection shows the dispatcher worker path wraps harness invocations through `scripts/run_with_status.py` from `scripts/dispatcher_runtime.py`. Both the outer wrapper launch and the wrapped child launch already use `pythonw.exe` where possible and set a no-window creation flag, and the current `scripts/windows_no_window_spawn_audit.py` passes. That means the current audit/test contract is too weak for the observed Windows behavior. The proposed change strengthens the runtime launch disposition and tests, without changing harness roles, worker lifetime policy, prompt transport, stdout/stderr log capture, or provider shim behavior.

## Current Evidence

- Owner symptom evidence: during this WI-5060 repair session, 4-5 console windows appeared; Mike clarified that the problem was specifically that they were not headless.
- `gt bridge show gtkb-wi5060-harness-readiness-repair --json --compact` reports latest `NEW` at `bridge/gtkb-wi5060-harness-readiness-repair-003.md`.
- `python scripts/bridge_claim_cli.py status gtkb-wi5060-harness-readiness-repair` reports an active Prime Builder implementation claim for session `019f39ff-4e44-7a32-b5d0-6969ec4d55ec` with `latest_bridge_status: NEW`.
- `gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` shows active item-specific PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` allowing WI-5060 source, test addition, configuration, and governance-evidence mutations while forbidding credential lifecycle, deploys, destructive cleanup, secret disclosure, and D/F re-enablement without smoke evidence.
- `bridge/gtkb-wi5060-harness-readiness-repair-002.md` GO authorizes only the originally listed shim/config/registry/test target paths; it does not list `scripts/dispatcher_runtime.py`, `scripts/run_with_status.py`, or the shared Windows subprocess helper.
- `scripts/dispatcher_runtime.py` `_spawn_harness` constructs `wrapped_command` using `scripts/run_with_status.py` and launches it with `_run_with_status_wrapper_popen_kwargs()`.
- `scripts/run_with_status.py` launches the wrapped harness child with redirected stdin/stdout/stderr and a Windows no-window creation flag.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py --json scripts/run_with_status.py scripts/dispatcher_runtime.py` reports release-ready/no violations, proving the current audit allows the existing launch shape even though the owner observed visible windows.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require a live bridge GO with matching target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must remain inside the active project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO or implementation-start gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal links work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal header carries Project Authorization, Project, and Work Item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map each behavior claim to concrete tests and dispatcher evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned workers must be controlled through the centralized dispatch service and its runtime state.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher report and health commands are the authoritative verification surface for topology and readiness.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, or rotation is in scope.

## Requirement Sufficiency

Existing requirements sufficient. WI-5060, the active WI-5060 PAUTH, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, and the bridge authorization specs are sufficient to authorize a narrow headless-launch hardening proposal once Loyal Opposition grants GO for these additional target paths. No new or revised requirement is needed before implementation.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their current roles.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - GO authorizing the owner to issue a targeted WI-5060 PAUTH before implementation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` - active bounded WI-5060 source/test/config/governance authorization.
- `bridge/gtkb-wi5060-harness-readiness-repair-001.md` - approved shim/readiness proposal with original target paths.
- `bridge/gtkb-wi5060-harness-readiness-repair-002.md` - Loyal Opposition GO for the original shim/readiness scope.
- `bridge/gtkb-wi5060-harness-readiness-repair-003.md` - post-implementation report for the original scope, now awaiting Loyal Opposition verification.

## Owner Decisions / Input

Mike has already supplied the operative clarification in the current session: the issue with spawned workers is that they were not headless. No additional owner decision is required for this proposal because the existing WI-5060 PAUTH covers source/test/config/governance repair for this work item, and this proposal exists precisely because the new target paths require bridge GO before mutation.

## Proposed Scope

1. Strengthen the Windows headless launch disposition used by dispatcher-owned workers:
   - Add or reuse a shared helper that returns a hidden-process launch contract for Windows.
   - Preserve `CREATE_NO_WINDOW` and `CREATE_NEW_PROCESS_GROUP` where currently required.
   - Add `DETACHED_PROCESS` when available and hidden `STARTUPINFO` (`STARTF_USESHOWWINDOW` with `SW_HIDE`) for the worker launch surfaces that can currently create visible windows.

2. Apply the strengthened launch contract only to governed dispatch worker paths:
   - Outer status-wrapper spawn in `scripts/dispatcher_runtime.py`.
   - Wrapped harness-child spawn in `scripts/run_with_status.py`.
   - Preserve existing non-Windows behavior, process-tree timeout behavior, stdin/stdout/stderr file routing, worker lifetime enforcement, and `pythonw.exe` preference.

3. Add focused regression tests:
   - `platform_tests/scripts/test_dispatcher_runtime.py` asserts the status-wrapper spawn uses `pythonw.exe` and the strengthened hidden Windows launch kwargs.
   - `platform_tests/scripts/test_run_with_status.py` asserts the wrapped harness child uses the strengthened hidden Windows launch kwargs on Windows and remains a no-op off Windows.
   - `platform_tests/scripts/test_windows_subprocess.py` covers the shared helper if introduced or expanded.

## Out Of Scope

- No changes to OpenRouter credentials, model configuration, cloud default selection, or provider account settings.
- No change to A/C/D/F role assignments.
- No change to worker lifetime budgets, turn budgets, dispatcher ranking, or D/F eligibility beyond preserving the already-smoked re-enablement state.
- No cleanup of unrelated worktree changes.
- No deployment or git push.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt bridge show gtkb-wi5060-headless-dispatch-window-hardening --json --compact`; `python scripts/bridge_claim_cli.py claim gtkb-wi5060-headless-dispatch-window-hardening --session-id <session>` after GO | Latest status is `GO` before protected edits; claim is Prime Builder / implementation scoped. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused pytest for `platform_tests/scripts/test_dispatcher_runtime.py` and `platform_tests/scripts/test_run_with_status.py` | Dispatcher worker spawns and wrapper child spawns carry the strengthened hidden Windows launch kwargs while preserving existing command shape. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch report --json` and `gt bridge dispatch health --json` after implementation | Health is `PASS`; selected topology includes A/F for Prime Builder and D/C for Loyal Opposition, subject to normal live-worker state. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps each headless-window claim to the focused tests and dispatcher health evidence | Loyal Opposition can verify each acceptance criterion from commands and changed paths. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Review diff and test commands | No credential values, lifecycle changes, or provider account mutations. |

## Acceptance Criteria

- The dispatcher-owned worker launch path uses a stronger hidden Windows launch contract than the minimal no-window bit alone.
- `scripts/run_with_status.py` still launches Python harness children through sibling `pythonw.exe` when available.
- `run_with_status.py` still records exit status, enforces worker lifetime, and terminates process trees on timeout.
- Focused tests pass for dispatcher runtime, run-with-status, and shared Windows subprocess helper behavior.
- Dispatcher health/report evidence remains `PASS` with A, C, D, and F dispatchable in their currently assigned roles.

## Risk / Rollback

Risk is limited to Windows subprocess creation flags and startup info. The change is reversible by restoring the prior helper behavior and the two launch sites. A rollback would not affect provider credentials, OpenRouter routing, Ollama routing, or bridge file history.

## Bridge Filing

This follow-on proposal is intentionally separate from `gtkb-wi5060-harness-readiness-repair` because that thread already filed its post-implementation report and its GO target paths did not include dispatcher/window-launch runtime files. No protected source/test edits for the target paths listed here should occur until Loyal Opposition returns `GO` on this proposal.

## Recommended Commit Type

`fix(harness):`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
