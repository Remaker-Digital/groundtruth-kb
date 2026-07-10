NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; resolved Prime Builder role via `::init gtkb pb`; WI-5135 implementation report

# GT-KB Bridge Implementation Report - gtkb-wi5135-codex-shell-no-window-dispatch - 009

bridge_kind: implementation_report
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 009 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-008.md
Approved proposal: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-007.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5135
target_paths: ["scripts/dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "scripts/codex_no_window_smoke_probe.py", "scripts/windows_subprocess.py", "scripts/codex_shell_no_window_wrapper.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_windows_subprocess.py", "platform_tests/scripts/test_codex_shell_no_window_wrapper.py"]
Recommended commit type: fix

## Implementation Claim

Implemented the WI-5135 no-window dispatch slice under the live GO and implementation-start gate. The selected containment mechanism is GT-KB-side Windows private-desktop containment for Codex dispatch, paired with schema-v2 live proof that requires repeated multi-command marker-chain evidence and zero visible `pwsh`/PowerShell windows.

The implementation keeps Codex-A persistent dispatch quiesced. The public Codex dispatch verifier now accepts the live no-window proof, while still reporting `dispatchable: false` because the separate `.codex` ACL readiness check remains unhealthy.

## Authorization Evidence

- Work-intent claim: `gtkb-wi5135-codex-shell-no-window-dispatch`, rowid `31112`, claim kind `go_implementation`.
- Implementation-start packet: `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch --expires-minutes 75` returned latest status `GO`, proposal `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-007.md`, GO `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-008.md`, and packet hash `sha256:0bac473f92add5211d56f55eb5d2812c6fc6b58c8dc5d771b48209cf37880cd4`.
- Live PAUTH: `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710`, rowid `566`, status `active`, mutation classes `source`, `tests`, `bridge`, `governance_evidence`.

## Owner Decisions / Input

- `DELIB-202666064` - owner decision to pursue WI-5135 as the Prime harness path and to back the implementation-scoped authorization for this source/test slice.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710` - implementation-scoped project authorization created from that owner decision; status `active`; project `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`; work item `WI-5135`; mutation classes `source`, `tests`, `bridge`, `governance_evidence`.
- No additional owner input is required by this implementation report; Codex-A steady-state dispatch enablement remains out of scope and still requires a separate governed step.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - PB authored this NEW implementation report after the latest LO GO; PB did not author GO, NO-GO, or VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable implementation evidence is captured in this bridge report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the operative proposal's specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused tests and live runtime proof are included for LO verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - header carries PAUTH, Project, Work Item, and machine-readable `target_paths`.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision `DELIB-202666064` remains the implementation authorization basis.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - changes remain in GT-KB platform dispatcher/test surfaces, not adopter application scope.
- `GOV-STANDING-BACKLOG-001` - WI-5135 remains a governed backlog continuation item.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - live proof exercises Codex behavior rather than assuming hook parity or parent-process flags.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation/report artifacts carry durable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - bridge lifecycle continues through LO verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - protected mutation was gated by the live PAUTH and implementation-start packet.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - no protected target mutation occurred without latest GO and target-path authorization.
- `GOV-WORK-TREE-HYGIENE-001` - implementation scope is limited to the approved target paths; `groundtruth.db` and generated harness registry state are not staged or proposed for this report.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch containment is implemented in dispatcher-owned command spawning and verification helpers.
- `ADR-DISPATCHER-ARCHITECTURE-001` - daemon-owned dispatch remains the model; no retired poller or harness-trigger path is restored.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - Codex-A remains quiesced until separate governed enablement.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - prior NO-ACTION/NO-GO lifecycle corrections are preserved.

## Changes Made

- Added Windows private-desktop helpers in `scripts/windows_subprocess.py` and used them for Codex worker launch in `scripts/dispatcher_runtime.py`.
- Added schema-v2 Codex no-window validation in dispatcher readiness and `scripts/verify_codex_dispatch.py`, including fail-closed rejection for legacy schema, insufficient run/command proof, stale proof, missing marker proof, and visible-window evidence.
- Added `scripts/codex_no_window_smoke_probe.py`, which writes schema-v2 verification evidence with at least two runs and three linked command steps per run.
- Added `scripts/codex_shell_no_window_wrapper.py` as a small no-window command wrapper.
- Added and updated focused platform tests for dispatcher runtime, verifier behavior, Windows subprocess helpers, smoke probe behavior, and shell wrapper behavior.

## Commands Run

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch --expires-minutes 75
groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts\codex_no_window_smoke_probe.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\dispatcher_runtime.py scripts\verify_codex_dispatch.py scripts\codex_no_window_smoke_probe.py scripts\windows_subprocess.py scripts\codex_shell_no_window_wrapper.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_codex_no_window_smoke_probe.py platform_tests\scripts\test_windows_subprocess.py platform_tests\scripts\test_codex_shell_no_window_wrapper.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\dispatcher_runtime.py scripts\verify_codex_dispatch.py scripts\codex_no_window_smoke_probe.py scripts\windows_subprocess.py scripts\codex_shell_no_window_wrapper.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_codex_no_window_smoke_probe.py platform_tests\scripts\test_windows_subprocess.py platform_tests\scripts\test_codex_shell_no_window_wrapper.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_windows_subprocess.py platform_tests\scripts\test_codex_shell_no_window_wrapper.py platform_tests\scripts\test_codex_no_window_smoke_probe.py platform_tests\scripts\test_verify_codex_dispatch.py platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short --basetemp .harness-tmp\wi5135-final
groundtruth-kb\.venv\Scripts\python.exe scripts\codex_no_window_smoke_probe.py --json --timeout 240 --dispatch-wrapper
groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --json
groundtruth-kb\.venv\Scripts\python.exe -c "from pathlib import Path; from scripts.dispatcher_runtime import _evaluate_harness_dispatch_readiness; import json; print(json.dumps(_evaluate_harness_dispatch_readiness('codex', Path.cwd()), indent=2, sort_keys=True))"
```

## Observed Results

- `py_compile`: passed.
- `ruff check`: passed, `All checks passed!`.
- `ruff format --check`: passed, `10 files already formatted`.
- Focused pytest: `204 passed, 1 warning in 23.21s`; warning is the existing pytest config warning for unknown `asyncio_mode`.
- Dispatch-wrapper smoke: `result: pass`, `schema_version: 2`, `dispatcher_wrapper_path: true`, `containment_mechanism: windows_private_desktop`, `run_count: 2`, `commands_per_run: 3`, `marker_chain_ok: true`, `visible_window_detected: false`, four sampled PowerShell window observations with `visible_count: 0`.
- Written live proof: `.gtkb-state/bridge-poller/codex-no-window-verification.json`, `verified_at: 2026-07-10T17:58:24.425133Z`, `expires_at: 2026-07-10T21:58:24.425133Z`.
- Dispatcher runtime readiness helper: `ready: true`, `reason: codex_no_window_verification_current`, `live_headless_ready: true`.
- Public verifier: `live_headless_ready: true`, `live_headless_reason: codex_no_window_verification_current`, `live_headless_failure_class: null`; full `dispatchable` remains `false` because `.codex` ACL readiness is still unhealthy (`codex_dotdir_acl_ok: false`, `errors_count: 208`, no `CodexSandboxUsers` allow).

## Acceptance Criteria Status

- Selected containment mechanism identified: GT-KB-side Windows private desktop via `CreateDesktopW`, recorded as `windows_private_desktop`.
- Acceptance is efficacy-gated: live proof requires zero visible `pwsh`/PowerShell windows during repeated multi-command Codex shell activity.
- Schema-v2 smoke evidence writes two runs, three command steps per run, marker proof, return codes, previews, and window observations.
- Verifier and dispatcher readiness reject legacy/insufficient/stale/visible-window evidence by focused tests; current live proof is accepted.
- Bounded dispatcher-path proof uses `scripts/run_with_status.py --config-env` and passed with zero visible windows.
- Focused tests passed with `--basetemp .harness-tmp\wi5135-final`.
- Ruff check and format check passed for the changed Python paths.
- Codex-A persistent `can_receive_dispatch` remains false pending separate governed enablement and the still-failing `.codex` ACL readiness check.

## Files Changed

- `scripts/dispatcher_runtime.py`
- `scripts/verify_codex_dispatch.py`
- `scripts/codex_no_window_smoke_probe.py`
- `scripts/windows_subprocess.py`
- `scripts/codex_shell_no_window_wrapper.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_windows_subprocess.py`
- `platform_tests/scripts/test_codex_shell_no_window_wrapper.py`

## Recommended Commit Type

- Recommended commit type: `fix`
- Justification: this is a dispatcher readiness bug fix with focused source and platform-test coverage.

## Residual Risk And Rollback

Residual risk is limited to Windows-specific process containment behavior. The implementation keeps Codex-A persistent dispatch disabled, so rollback is a scoped revert of the listed source/test paths plus removal of the live schema-v2 proof file if LO rejects the approach. No `groundtruth.db` or generated harness registry projection state should be staged or committed as part of this WI.

The live proof expires at `2026-07-10T21:58:24.425133Z`; if LO verification occurs after that point, rerun the smoke probe before accepting current readiness.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications, the approved target paths, and the executed command evidence.
2. Confirm that the no-window gate is fixed independently of the separate `.codex` ACL readiness blocker.
3. Return VERIFIED if the implementation satisfies WI-5135; otherwise return NO-GO with focused findings.
