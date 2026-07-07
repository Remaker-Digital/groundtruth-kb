NEW

# GT-KB Bridge Implementation Report - gtkb-wi5052-dispatcher-codex-no-window-containment - 003

bridge_kind: implementation_report
Document: gtkb-wi5052-dispatcher-codex-no-window-containment
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-002.md
Approved proposal: bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5052-DISPATCHER-NO-WINDOW-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5052
Recommended commit type: fix:
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: gpt-5.5
author_model_version: codex
author_model_configuration: interactive Codex desktop session; role override `::init gtkb pb`; owner-updated headless-dispatch recovery goal

## Implementation Claim

The WI-5052 containment implementation is complete: Windows Codex auto-dispatch now fails closed unless a fresh no-window verification record exists at `.gtkb-state/bridge-poller/codex-no-window-verification.json`, and the no-window audit now covers the dispatcher status-wrapper launch path.

The implementation deliberately does not claim Codex is safe to reactivate for Prime Builder headless work yet. Live Codex shell-tool smokes still create visible Windows Terminal/Git/PowerShell windows and fail with `windows sandbox: setup refresh failed with status exit code: 0xc0000142`. The verification record therefore remains `result: fail`, `visible_window_detected: true`, keeping Codex auto-dispatch quarantined as intended.

In the same owner-directed recovery window, OpenRouter was moved to the Loyal Opposition default role and depleted Antigravity/Ollama receive eligibility was disabled through governed dispatcher transactions. Current dispatcher dry-run selection is `prime-builder:A` (suppressed by failed no-window readiness/work-intent state) and `loyal-opposition:F` (OpenRouter selected).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected dispatcher/config source mutation required a bridge proposal, Loyal Opposition GO, and implementation-start authorization.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - WI-5052 is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5052-DISPATCHER-NO-WINDOW-20260707`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH did not bypass bridge review or implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implementation remains mapped to governing requirements and verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification evidence is mapped below.
- `GOV-STANDING-BACKLOG-001` - WI-5052 is the standing-backlog defect item surfaced by no-window audit repair.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher work must remain headless/no-window safe.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the centralized dispatcher remains the only routing surface; unsafe Codex dispatch is quarantined rather than replaced by an alternate bridge runtime.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - role and receive-eligibility changes used governed dispatcher/mode control surfaces.

## Owner Decisions / Input

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - owner directive that no visible console windows may spawn on this workstation.
- 2026-07-07 owner update in the active Codex thread: OpenRouter must become Loyal Opposition default while Codex and OpenRouter are assessed for headless work. This was applied through `gt mode set-role --harness F --role loyal-opposition` and `gt bridge dispatch config set-eligibility` transactions for depleted C/D receive eligibility.

## Prior Deliberations

- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `INTAKE-8242840e` - repeated worker launch failure should be handled as operations-owned recovery.
- `INTAKE-6554ff58` - dispatcher complex control and guarded quiesce context.
- `INTAKE-37a7892d` - minimal dispatcher quarantine state for unsafe launch paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | GO exists at `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-002.md`; Prime implementation claim rowid 30674 was active; implementation-start packet hash `sha256:8b5ce2c9fb930cd685fa81bd31b1636987915d3758f5e1b6b90420955bb84648` authorized the target paths. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5052-dispatcher-codex-no-window-containment` returned authorized packet hash `sha256:8b5ce2c9fb930cd685fa81bd31b1636987915d3758f5e1b6b90420955bb84648`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Source/test mutations were limited to the GO target paths; dispatcher role/eligibility changes used governed `gt` control transactions rather than direct config edits. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward all linked governing specs from the approved proposal. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata includes `Project Authorization`, `Project`, and `Work Item`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff, no-window audit, static Codex readiness, live no-window smokes, and dispatcher dry-runs were executed and are recorded below. |
| `GOV-STANDING-BACKLOG-001` | WI-5052 behavior is preserved as a bridge implementation report with residual blocker evidence instead of being hidden as local runtime state. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `scripts/windows_no_window_spawn_audit.py --json` reports `release_ready: true`, `violation_count: 0`; live Codex shell smokes report visible windows, so Codex remains fail-closed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `scripts/gtkb_dispatcher_daemon.py tick --dry-run` continues to use the central dispatcher and now selects OpenRouter as `loyal-opposition:F`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch status --json` reports LO target `F:openrouter` and PB target `A:codex`; `gt bridge dispatch health --json` still reports complex lifecycle inactive due the active disable guard. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_windows_no_window_spawn_audit.py -q --no-header`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/dispatcher_runtime.py scripts/windows_no_window_spawn_audit.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/dispatcher_runtime.py scripts/windows_no_window_spawn_audit.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\windows_no_window_spawn_audit.py --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --json`
- `groundtruth-kb\.venv\Scripts\gt.exe mode set-role --harness F --role loyal-opposition --reason "Owner updated 2026-07-07 goal: OpenRouter should become Loyal Opposition default while depleted LO harnesses recover"`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config set-eligibility C --no-can-receive-dispatch --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config set-eligibility D --no-can-receive-dispatch --json`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -ProjectRoot E:\GT-KB -Mode Apply -Json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\gtkb_dispatcher_daemon.py tick --project-root E:\GT-KB --max-items 2 --dry-run`
- Dispatcher-wrapper no-window smoke: `codex --version`, `codex exec --help`, and diagnostic `cmd.exe /c ping -n 4 127.0.0.1 >NUL`.
- Live Codex shell smoke through dispatcher wrapper: `codex exec --model gpt-5.5 -c approval_policy="never" -c model_reasoning_effort="xhigh" --sandbox workspace-write <prompt> --cd E:\GT-KB --add-dir .codex`.
- Live Codex shell smoke through dispatcher wrapper with `--ignore-user-config --ephemeral`.
- Live Codex shell smoke through dispatcher wrapper with `--disable plugins`.

## Observed Results

- Combined pytest: `174 passed, 1 warning`.
- Ruff check: `All checks passed!`.
- Ruff format check: all 4 scoped files already formatted after formatting `platform_tests/scripts/test_dispatcher_runtime.py`.
- No-window audit: `release_ready: true`, `violation_count: 0`, `total_findings: 671`, counts `compliant_no_window: 73`, `interactive_allowlist: 118`, `non_release_runtime: 480`.
- Static Codex readiness after ACL repair: `static_ok: true`, `dispatchable: true`, `.codex` ACL `needs_repair: false`, `risky_deny_count: 0`.
- ACL repair: removed 2 risky explicit deny ACEs from `E:\GT-KB\.codex`; current user and `CodexSandboxUsers` modify allows were already present.
- OpenRouter role transaction: applied at `2026-07-07T19:43:09Z`, previous role set `prime-builder`, new role set `loyal-opposition`.
- Dispatcher receive transactions: C and D receive eligibility disabled through `gt bridge dispatch config set-eligibility`; status later selected `loyal-opposition:F` only.
- Dispatcher status after routing changes: `loyal_opposition = F:openrouter:dispatch=True:status=active:max=1`; `prime_builder = A:codex:dispatch=True:status=active:max=4`; routing health `PASS`.
- Dispatcher dry-run after Codex CLI help smoke: Codex no longer failed for missing verification, but selected PB items were suppressed by work-intent state; OpenRouter selected as `loyal-opposition:F`.
- Live Codex shell smoke failed: wrapper/status exit code `0`, but command output was `windows sandbox: setup refresh failed with status exit code: 0xc0000142`; visible-window probe detected 15 new windows, including `Terminal`, `Windows Terminal`, and `C:\Program Files\Git\cmd\git.exe`.
- Live Codex shell smoke with `--ignore-user-config --ephemeral` failed: command was rejected by policy/read-only posture, plugin startup still attempted git sync, and visible-window probe detected 15 new windows.
- Live Codex shell smoke with `--disable plugins` failed: Codex executed `"C:\Program Files\PowerShell\7\pwsh.exe" -Command 'echo GTKB_CODEX_NO_WINDOW_SMOKE_OK'`, then failed with `windows sandbox: setup refresh failed with status exit code: 0xc0000142`; visible-window probe detected 15 new windows.

## Files Changed

- `scripts/dispatcher_runtime.py`
- `scripts/windows_no_window_spawn_audit.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `harness-state/harness-registry.json`

Operational state/evidence written:

- `.gtkb-state/bridge-poller/codex-no-window-verification.json` currently records the latest failed live Codex shell smoke, keeping Codex quarantined.
- `.gtkb-state/bridge-poller/codex-no-window-smoke/` contains stdout/stderr/exit-code evidence for the smoke probes.
- `.gtkb-state/bridge-dispatch-config-transactions/audit.jsonl` records the governed dispatcher eligibility transactions.
- `.gtkb-state/mode-switches/20260707T194309Z-c9ba0a55.json` records the OpenRouter role switch.

## Acceptance Criteria Status

- [x] Windows Codex dispatch fails closed unless a fresh passing no-window verification record exists.
- [x] Dispatcher dry-run routes Loyal Opposition work to OpenRouter after the owner-directed role/eligibility update.
- [x] No-window audit covers the dispatcher runtime status-wrapper helper path and remains release-ready.
- [x] Static Codex dispatch configuration and ACL posture are repaired.
- [ ] Codex is safe for live Prime Builder headless shell work. Live smokes show it is not yet safe; Codex remains quarantined.
- [ ] Dispatcher complex scheduled-task guard is cleared. The guard must remain active until Codex shell execution is headless-safe or Codex PB dispatch is otherwise excluded from automatic live processing.
- [ ] 120/180-minute no-visible-window observation window is not satisfied.

## Risk And Rollback

Residual risk is now explicit rather than latent: Codex CLI's Windows sandbox/tool execution path can still create visible windows and fail with `0xc0000142`. The containment guard prevents the dispatcher from launching Codex PB workers while this evidence is failing. OpenRouter LO dispatch is separately available and does not require spending Antigravity/Ollama budget.

Rollback for the source/test changes is a normal commit revert of the scoped files. Do not clear `.gtkb-state/watchdog/dispatcher-disable-guard.json` or re-enable the dispatcher complex while the latest `codex-no-window-verification.json` records `result: fail`.

## Loyal Opposition Asks

1. Verify the containment implementation: Codex auto-dispatch must remain fail-closed on Windows when no-window evidence is missing, stale, expired, or failed.
2. Verify the no-window audit/test coverage and the OpenRouter LO routing evidence.
3. Return VERIFIED for WI-5052 if containment is sufficient, while preserving the residual blocker that Codex live PB shell work is not yet headless-safe; otherwise return NO-GO with findings.
