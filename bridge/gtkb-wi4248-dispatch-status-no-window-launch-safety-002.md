REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex Desktop; Prime Builder; approval_policy=never; sandbox=danger-full-access; cwd=E:\GT-KB

# Implementation Proposal - WI-4248 Dispatcher Status and No-Window Launch Safety

bridge_kind: prime_proposal
Document: gtkb-wi4248-dispatch-status-no-window-launch-safety
Version: 002
Responds to: bridge/gtkb-wi4248-dispatch-status-no-window-launch-safety-001.md
Revises: bridge/gtkb-wi4248-dispatch-status-no-window-launch-safety-001.md
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4248

target_paths: ["scripts/dispatcher_runtime.py", "scripts/run_with_status.py", "scripts/windows_subprocess.py", "scripts/windows_no_window_spawn_audit.py", "scripts/ops/dispatch_parity.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_bridge_dispatch_per_document_lease.py", "platform_tests/scripts/test_dispatcher_runtime_drains_pending_before_recipient_resolution.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py", "platform_tests/scripts/test_dispatch_author_meets_reviewer.py", "platform_tests/scripts/test_dispatch_non_transient_fast_trip.py", "platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py", "platform_tests/scripts/test_governing_specs_preserved.py", "platform_tests/scripts/test_run_with_status.py", "platform_tests/scripts/test_windows_subprocess.py", "platform_tests/scripts/test_windows_no_window_spawn_audit.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Revision 002 expands the target paths and verification scope after baseline testing showed stale dispatcher-runtime test references outside the initial proposal target list. The source behavior claim remains unchanged: fix no-window worker wrapping, read-only observation safety, and stdin-backed prompt routing without reviving retired trigger automation.

Proposal for a release-blocking dispatcher safety slice under Harness Parity Phase 2 and WI-4248.

GT-KB must not spawn visible console windows during regular operation. Current evidence shows the dispatcher worker wrapper still starts `scripts/run_with_status.py` through console `sys.executable` in `scripts/dispatcher_runtime.py` before `run_with_status.py` can rewrite child Python commands to `pythonw.exe`. That wrapper launch can create `conhost.exe` / OpenConsole windows. The same slice should prove that read-only dispatcher observation surfaces cannot launch workers or mutate dispatch-run state, and should fix stdin-backed harness prompt routing so Antigravity-style long prompts are not carried in argv.

## Claim

Prime Builder proposes a bounded implementation to make dispatcher observation and worker launch paths release-safe:

- read-only dispatcher surfaces remain read-only and cannot invoke `_spawn_harness`;
- Windows dispatcher worker wrappers use the shared no-window/GUI-Python subprocess discipline before `run_with_status.py` starts;
- stdin-backed harnesses do not keep the full dispatch prompt in the command argv when the wrapper is already supplying `--stdin`;
- focused tests prove the no-window wrapper and read-only status/report/health behavior.

## Requirement Sufficiency

Existing requirements are sufficient. The owner has directed that all harnesses are active, no harness is waived or retired, no regular GT-KB path may spawn visible console windows, and dispatcher release health is a release blocker. WI-4248 already authorizes investigation and GT-KB-side mitigation for Windows process-launch instability where project automation can correct or contain the failure. Harness Parity Phase 2 and the active PAUTH cover dispatchability and Windows no-window parity.

No new owner decision is required for this proposal because it narrows an already-stated release blocker into source/test changes guarded by bridge GO and verification.

## Evidence

- `scripts/dispatcher_runtime.py` builds `wrapped_command` with `sys.executable` followed by `scripts/run_with_status.py`, then starts it with `subprocess.Popen`.
- `scripts/run_with_status.py` already has child-process no-window behavior, including `CREATE_NO_WINDOW` and sibling `pythonw.exe` selection for Python child commands.
- `scripts/windows_subprocess.py` already provides shared no-window creation flags and `prefer_pythonw_executable`.
- A live failed OpenRouter dispatch run showed a wrapper process using console Python for `scripts/run_with_status.py`, with child console-host symptoms before containment.
- `groundtruth-kb/src/groundtruth_kb/cli.py` implements dispatcher `status`, `health`, and `report` as observation commands. The release fix must add regression coverage proving those commands cannot route into worker spawning or dispatch-run mutation.
- Antigravity dispatch support writes a prompt stdin file, but `_harness_command` substitutes `{{PROMPT}}` into argv before `_spawn_harness` appends `--stdin`, leaving a Windows command-line length hazard.

## Proposed Scope

1. Refactor dispatcher worker wrapper construction so Windows uses the shared GUI-Python/no-window helper for the `run_with_status.py` wrapper process itself, not only for the wrapper's child command.
2. Preserve stdout, stderr, status-file, lifetime, environment, work-intent, and PID/create-time behavior.
3. Make stdin-backed dispatch targets remove or replace the prompt argv element when `--stdin` is supplied, so large prompts move through the status wrapper's stdin file instead of Windows argv.
4. Add focused tests proving:
   - `_spawn_harness` invokes the wrapper with GUI Python/no-window discipline on Windows;
   - `run_with_status.py` still rewrites Python child commands to `pythonw.exe` where available and still uses `CREATE_NO_WINDOW`;
   - dispatcher `status`, `health`, and `report` paths do not call `_spawn_harness` and do not create dispatch-run artifacts;
   - Antigravity/stdin-backed dispatch does not include the full prompt in argv when stdin handoff is configured.
5. Update the no-window audit, if needed, so it catches future console-Python wrapper regressions in dispatcher runtime and CLI daemon-control paths.

## Non-Scope

- Do not reintroduce the retired cross-harness trigger or single-harness automation paths.
- Do not waive, retire, or suspend any harness.
- Do not change provider credentials or ask the owner to rotate credentials.
- Do not broaden this slice into full provider timeout remediation unless the code change directly reveals the same launch-safety root cause.
- Do not commit or merge release work under this proposal until implementation receives LO `VERIFIED`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test/config changes require bridge GO, work-intent, and implementation-start authorization.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - work must remain inside the active Harness Parity Phase 2 project authorization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal review requires relevant specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map each linked requirement to executed tests.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - harness parity and role enforcement apply across all active harnesses.
- `ADR-CROSS-HARNESS-PARITY-001` - active harnesses should be semantically fungible where their capabilities allow.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity gaps must be tracked and tested instead of assumed.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher daemon is the success path for automated bridge work; retired trigger paths are not fallbacks.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex parity relies on deterministic fallback/runtime controls where native hook behavior differs.
- `GOV-STANDING-BACKLOG-001` - release-blocking reliability work must remain tracked through work items and bridge state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - evidence and implementation claims must be preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation should reduce ambiguity by updating canonical source/test surfaces.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - transient incident evidence that affects release readiness must be promoted to governed artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains in the GT-KB root and does not treat Agent Red as an integrated artifact.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner directed full active-harness parity, no waivers for Antigravity or Claude Code, and dispatcher release readiness as a blocker.
- `DELIB-20266350` - prior headless readiness and worker Python launch findings.
- `DELIB-20266353` - prior console residual fix context.
- `bridge/gtkb-wi4248-codex-windows-parallel-shell-flake-001.md` - approved investigation scope for the Windows shell launch flake.
- `bridge/gtkb-wi4248-codex-windows-parallel-shell-flake-002.md` - LO GO for the initial WI-4248 investigation.
- `bridge/gtkb-wi4248-codex-windows-parallel-shell-flake-003.md` - current post-implementation report awaiting LO verification.
- `bridge/gtkb-run-with-status-worker-lifetime-timeout-005.md` - related run-with-status lifetime advisory.

## Owner Decisions / Input

No new owner input is required. The proposal implements already-stated owner direction: no visible console windows during regular GT-KB operation, no retired trigger fallback, all harnesses active, and dispatcher health as a release blocker.

## Verification Plan

Run focused tests:

```powershell
python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_dispatcher_runtime_drains_pending_before_recipient_resolution.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_dispatch_author_meets_reviewer.py platform_tests/scripts/test_dispatch_non_transient_fast_trip.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py platform_tests/scripts/test_governing_specs_preserved.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_windows_subprocess.py platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short
```

Run focused lint/format checks for touched files:

```powershell
python -m ruff check scripts/dispatcher_runtime.py scripts/run_with_status.py scripts/windows_subprocess.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_windows_subprocess.py platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
python -m ruff format --check scripts/dispatcher_runtime.py scripts/run_with_status.py scripts/windows_subprocess.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_windows_subprocess.py platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
```

Run dispatcher health after implementation using read-only health/report surfaces only:

```powershell
gt bridge dispatch health --json
```

Do not use `gt bridge dispatch status --json` as verification until the implementation has a regression test proving that status cannot spawn workers or mutate dispatch-run artifacts.

## Spec-To-Test Mapping

- `GOV-FILE-BRIDGE-AUTHORITY-001` -> implementation-start authorization command and bridge implementation report evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` -> bridge target paths and PAUTH metadata; implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` -> bridge-compliance preflight.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` -> applicability preflight and LO review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -> implementation report test mapping.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` -> dispatcher runtime tests for stdin-backed harness prompt routing and no-window worker launch parity.
- `ADR-DISPATCHER-ARCHITECTURE-001` -> tests that observation surfaces remain read-only and that the dispatcher daemon/runtime path is the only automated dispatch path.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` -> no-window audit and run-with-status tests covering Windows fallback behavior.
- `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` -> bridge proposal/report evidence and root-boundary target-path validation.

## Acceptance Criteria

- Dispatcher worker wrapper launches cannot spawn visible console windows on Windows.
- Status/report/health observation surfaces have tests proving they do not launch workers or create dispatch-run artifacts.
- Stdin-backed harnesses do not receive large dispatch prompts through argv when stdin handoff is configured.
- Existing run-with-status timeout, stdout/stderr capture, exit-code, and process-tree cleanup semantics remain intact.
- Focused pytest, ruff check, and ruff format checks pass for touched files.
- Implementation report includes exact command evidence and LO verification reaches `VERIFIED`.

## Risk And Rollback

Risk is moderate because this touches the worker launch path used by all dispatched harnesses. The implementation should be small and test-first where practical. Rollback is a single commit revert restoring the previous wrapper command construction; if rollback is needed, automated dispatch should remain disabled or limited to owner-initiated manual assignment until a corrected no-window launch fix is approved.

## Pre-Filing Preflight

Applicability preflight on the candidate content passed:

- command: `python scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-propose-drafts\gtkb-wi4248-dispatch-status-no-window-launch-safety-001.md --json`
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:d3c89e8470b1649a35bb4f4a418306b77c6976e1c8e48333e680edb3f967dc0a`

Clause preflight on the candidate content passed:

- command: `python scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-propose-drafts\gtkb-wi4248-dispatch-status-no-window-launch-safety-001.md`
- must_apply: 4
- evidence_gaps_in_must_apply_clauses: 0
- blocking_gaps: 0
- exit_code: 0

## Recommended Commit Type

`fix:`
