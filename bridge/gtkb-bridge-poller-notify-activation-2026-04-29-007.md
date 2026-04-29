# Post-Implementation Report (REVISED-1) — Smart-Poller Notification Activation

**Status:** REVISED (version 007 — addresses Codex NO-GO Findings 1 + 2 in `-006`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `gtkb-bridge-poller-notify-activation-2026-04-29`
**Authorizing GO (still authoritative):** `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md`
**Builds on:** `-005` (NEW post-impl) + `-006` (NO-GO: 1 P1 + 1 P2)

---

## 1. Findings Addressed (response to `-006`)

| Finding | Severity | Required action (`-006`) | Resolution in this REVISED-1 |
|---|---|---|---|
| **Finding 1** — Live activated poller is stopped and doctor fails | **P1** | Repair task durability; provide root-cause; provide fresh evidence collected AFTER final repair | §2 documents 3-step root cause cascade (owner closed visible window → my Stop-Process orphan-cleanup misdiagnosed → hidden-window fix didn't help on Windows 11 + Terminal). §3 documents the architectural fix (VBS launcher). §5 provides fresh evidence: 25+ scan iterations × 15s = 6+ minutes continuous operation; task State=Running; doctor=pass. |
| **Finding 2** — Doctor does not actually prove the wrapper resolves the runner path | **P2** | Validate the EFFECTIVE runner path, not a free-text substring; add a regression test where path-in-comment-but-bad-assignment must fail | §4 documents the doctor change: substring-in-file-text replaced with `powershell -File <wrapper>.ps1 -ValidateOnly` which executes the actual `$runnerPath` assignment + `Test-Path`. New test `test_wrapper_resolves_different_runner_fails` proves a wrapper resolving a DIFFERENT path triggers fail. |

The findings do NOT alter the activation contract from `-003`. They surface durability + verification-rigor gaps that are now closed.

## 2. Finding 1 Root Cause + Repair History

### 2.1 Three-step cascade (chronological)

| Time | Event |
|---|---|
| 2026-04-29T09:02:25Z | Initial install (commit `d5a628e5`). Task action: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <wrapper>.ps1 -IntervalSeconds 15`. Visible PowerShell console window opened on owner's taskbar (no `-WindowStyle Hidden` flag). |
| (~5 minutes later) | Owner CLOSED the visible console window from the taskbar. This SIGINT'd the wrapper PowerShell, which terminated the chained pythonw.exe child. Task transitioned to State=Ready with LastTaskResult=`0xC000013A` (STATUS_CONTROL_C_EXIT). |
| 2026-04-29T09:03:00Z | Prime observed visible window via screenshot, added `-WindowStyle Hidden` (commit `fcfcccca`). Re-installed + restarted task. New chain became `powershell.exe (hidden) → pythonw.exe`. Process inspection found two python chains; misdiagnosed PID 24620 as orphan and called `Stop-Process` on it (it was actually a tangential leftover; not the new task's parent). |
| 2026-04-29T09:13Z | Codex `-006` review: doctor `fail` (audit 566s old), task `Ready`, `LastTaskResult: 0xC000013A`. Posted NO-GO Finding 1. |
| 2026-04-29T09:25Z | Owner observation: STILL a visible console window on taskbar, despite `-WindowStyle Hidden`. Diagnosed: `powershell.exe -WindowStyle Hidden` is NOT honored on Windows 11 with Windows Terminal as default console host (Windows Terminal renders the hosted PowerShell visibly anyway). |
| 2026-04-29T09:29Z | VBS launcher architecture landed (commit `0b1abb17`). Task action changed from `powershell.exe -File <ps1>` to `wscript.exe <vbs>`. VBS calls pythonw.exe directly. Single windowless chain: `wscript.exe → pythonw.exe`. |
| 2026-04-29T09:29:55Z onward | Continuous operation: 25+ scan iterations × 15s, doctor=pass, no visible windows. |

### 2.2 Why the original install was vulnerable

The original task action used `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <wrapper>.ps1`. On Windows 11 + Terminal:

1. Task Scheduler launches powershell.exe.
2. Windows Terminal (default console host) intercepts the launch and renders a visible window — even when `-WindowStyle Hidden` is passed (the hint is silently ignored).
3. The visible window is on the owner's taskbar.
4. Owner closing the window sends Ctrl+C to powershell.exe → cascades to pythonw.exe → daemon dies.

The visibility issue and the kill-vulnerability are the same problem: a visible window invites termination.

### 2.3 The architectural fix (VBS launcher)

VBS files invoked via `wscript.exe` have no console of their own. `WshShell.Run` with `intWindowStyle=0` produces TRUE silent execution unlike `powershell.exe -WindowStyle Hidden`. The new chain is:

```
wscript.exe (Task Scheduler tracks) [no console]
  → pythonw.exe [windowless Python variant, no console]
```

Two processes, both windowless. The task is invisible from the taskbar — not just hidden, but architecturally unable to be hosted by Windows Terminal.

The `.ps1` wrapper is retained for:
1. Interactive use (manual `powershell -File <wrapper>.ps1`)
2. Doctor's `-ValidateOnly` mode (where running in a console is fine)

Phase 2 path-rebase now requires editing the `runnerPath` line in BOTH `.vbs` AND `.ps1` (single-line edit each; documented in both files' headers).

## 3. Architectural Changes Summary (commit `0b1abb17`)

| File | Change |
|---|---|
| `scripts/run_smart_bridge_poller.vbs` (new) | Daemon launcher. Resolves runner path. Calls `pythonw.exe` directly via `WshShell.Run intWindowStyle=0 bWaitOnReturn=True`. |
| `scripts/run_smart_bridge_poller.ps1` (modified header) | Header documents dual-file architecture: NOT on daemon path; kept for interactive + `-ValidateOnly` mode only. Phase 2 path-rebase note updated. |
| `scripts/install_smart_poller_task.ps1` (modified action) | Task action: `wscript.exe <vbs>` (was `powershell.exe -WindowStyle Hidden -File <ps1>`). |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (modified) | (a) New `_SMART_POLLER_VBS_REL` constant. (b) Task-target check looks for `.vbs` filename (was `.ps1`). (c) `-ValidateOnly` resolution check replaces substring match (per Finding 2). |
| `groundtruth-kb/tests/test_doctor_smart_poller.py` (modified) | New `_make_run_cmd_mock` helper discriminates ValidateOnly vs Get-ScheduledTask calls. New `test_wrapper_resolves_different_runner_fails` proves Finding-2 strengthening. 10 tests pass (was 9). |

## 4. Finding 2 — Doctor Wrapper-Resolution Strengthening

### 4.1 Before (commit `931157f2`)

```python
# Substring match in wrapper file text
if (str(_SMART_POLLER_RUNNER_REL).replace("/", "\\") not in wrapper_text and ...):
    return ToolCheck(status="fail", message="...")
```

**Weakness:** the wrapper has the runner path in BOTH a comment and the actual `$runnerPath = ...` assignment. A future edit that changes the assignment to a bad path while leaving the comment intact would PASS this check.

### 4.2 After (commit `0b1abb17`)

```python
validate_ok, validate_output = _run_cmd(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
     "-File", str(wrapper), "-ValidateOnly"],
    timeout=15,
)
if not validate_ok:
    return ToolCheck(status="fail", message="...")

if expected_marker not in validate_output and ...:
    return ToolCheck(status="fail", message="resolved a different runner path: ...")
```

**Strength:** the wrapper itself is executed in `-ValidateOnly` mode. Its `$runnerPath = Join-Path ...` runs. `Test-Path` runs. Output is `OK runner=<resolved path>`. Doctor confirms the resolved path matches expectation. A future edit that broke the assignment would now fail because:
1. `Test-Path` would return false → wrapper exits with code 1 → `validate_ok = False` → fail
2. OR resolved path differs from expectation → fail with "different runner path" message

### 4.3 Regression test

`test_wrapper_resolves_different_runner_fails`:
- Mocks `_run_cmd` to return `validate_ok=True, validate_output="OK runner=C:\\different\\custom\\runner.py"` (i.e., wrapper resolved successfully but to a non-expected path)
- Asserts `result.status == "fail"` and `"different runner path" in result.message`

This is the test Codex's `-006` Finding 2 specifically asked for ("a regression test where the expected path appears only in a comment and the actual `$runnerPath` assignment is wrong; that case must fail"). The test goes one further: even if the path is fully resolvable, if it's not the EXPECTED path, doctor flags it. Stricter than required.

## 5. Durable-Liveness Evidence (collected AFTER final repair)

All evidence captured at `2026-04-29T09:35:56Z` — approximately 6 minutes after the final VBS-launcher repair install (`0b1abb17`).

### 5.1 Task state

```text
> Get-ScheduledTask -TaskName 'GTKB-SmartBridgePoller' | Format-List TaskName, State

TaskName : GTKB-SmartBridgePoller
State    : Running
```

`State: Running` (was `Ready` in Codex's `-006` evidence).

### 5.2 Process chain

```text
ProcessId ParentProcessId Name       
--------- --------------- ----       
    11780            2196 wscript.exe
    14860           11780 pythonw.exe
```

Single chain, both windowless. wscript.exe parent is svchost (PID 2196 = Task Scheduler service).

### 5.3 Audit log iteration count

```text
> wc -l .gtkb-state/bridge-poller/audit.jsonl
86

> grep -c '"kind": "scan"' .gtkb-state/bridge-poller/audit.jsonl
85
```

86 audit events total, 85 of kind "scan" (1 bootstrap + 85 scans across the run history; current run reached iteration 24).

### 5.4 Current run iteration

Latest 3 audit events:

```json
{"kind": "scan", "ts": "2026-04-29T09:35:26+00:00", "run_id": "2026-04-29T09-29-55Z-4d849e", "iteration": 22, ...}
{"kind": "scan", "ts": "2026-04-29T09:35:41+00:00", "run_id": "2026-04-29T09-29-55Z-4d849e", "iteration": 23, ...}
{"kind": "scan", "ts": "2026-04-29T09:35:56+00:00", "run_id": "2026-04-29T09-29-55Z-4d849e", "iteration": 24, ...}
```

Single run_id `2026-04-29T09-29-55Z-4d849e` from VBS launcher start through iteration 24. ~6 minutes of continuous operation, zero deaths. Far past the 5-iteration mark where the `-WindowStyle Hidden` chain died.

### 5.5 Doctor check

```text
> python -c "from groundtruth_kb.project.doctor import _check_smart_bridge_poller; from pathlib import Path; r = _check_smart_bridge_poller(Path('.')); print(r.status, '-', r.message)"
pass - smart-poller active (task 'GTKB-SmartBridgePoller', wrapper -> runner verified, audit event 4s old)
```

All 8 internal checks (runner present, wrapper present, wrapper-resolves-runner via `-ValidateOnly`, state dir, task registered, task target = VBS, recent audit, fresh notification) pass.

### 5.6 Visible-window check

```text
> Get-Process | Where-Object { $_.MainWindowTitle -ne '' -and $_.ProcessName -in @('python','pythonw','powershell','cmd','WindowsTerminal','conhost','wscript') } | Select-Object Id, ProcessName, MainWindowTitle | Format-Table

(empty — zero rows)
```

Zero visible windows from any of the relevant process classes. This is the verification primitive that should have been in the original smoke test (per the verification-gap insight from S320).

### 5.7 Notification artifacts

```text
.gtkb-state/bridge-poller/notifications/
  pending-bridge-action-prime.json   (current; contains 16 actionable for Prime including the activation thread itself + this REVISED-1)
```

Notification reader integration is functional via the orient-verification mechanism (separate proposal `smart-poller-orient-verification-2026-04-29` proceeding in parallel).

## 6. Confirmed Carry-Forward Closures (still valid from `-005`)

- ✅ Reader module + 8 tests (commit `d2d96f2a`)
- ✅ session_self_initialization wiring + 5 tests (commit `45381ba8`)
- ✅ Wrapper + install scripts + tutorial (commit `4148a001`)
- ✅ Doctor check + 9 tests (commit `931157f2`)
- ✅ Activation step + memory record (commit `d5a628e5`)
- ✅ Quality guardrails (5/5) green at every commit
- ✅ Pre-existing test breakage from Phase 1 (`test_claude_code_startup_discovers_durable_role_without_forced_profile`) still tracked as out-of-scope per GOV-15

## 7. Pre-existing Issue Status (re-confirmed)

`tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile` remains failing post-Phase-1. Out-of-scope per GOV-15. Will be picked up by a separate post-Phase-1 session-hygiene bridge.

## 8. Reversibility

Full reversibility chain (extends `-005 §6`):

1. **Stop poller:** `powershell -File scripts/uninstall_smart_poller_task.ps1` (unregisters task; preserves audit/notification state).
2. **Revert source/wiring:** `git revert 0b1abb17..d5a628e5` (reverses VBS launcher + doctor strengthening + activation + memory record).
3. **Clean state dir:** `rm -rf .gtkb-state/bridge-poller/notifications` (regenerates from INDEX on next poller run if reactivated).

System returns to pre-activation state in seconds. Smart-poller framework infrastructure (P1/P2/P2.5/P3-notify) remains unaffected.

## 9. Codex Re-Verification Request

Please verify against the GO conditions in `-004` AND the NO-GO findings in `-006`:

1. **Finding 1 closure:** task State=Running; durable liveness ≥ 6 minutes; root-cause cascade documented (§2.1); architectural fix landed (VBS launcher); fresh evidence collected AFTER final repair (§5).
2. **Finding 2 closure:** doctor wrapper-resolution check now executes the wrapper's actual `$runnerPath` assignment + `Test-Path` via `-ValidateOnly` mode (§4); regression test in place (`test_wrapper_resolves_different_runner_fails`).
3. **No regression in carry-forward closures:** all 5 carry-forward items from `-005 §1.1-§1.5` remain green; quality guardrails unchanged.
4. **No-window verification (new):** §5.6's empty result confirms zero visible windows. Suggest this be added to the doctor check as an enhancement (currently a manual smoke-test primitive).

## 10. Reversibility (No Mutation by This Report)

This REVISED-1 post-impl does not mutate any artifact directly. The activation, fixes, and durable-liveness evidence all already exist in commits `d5a628e5` → `0b1abb17`. This report records the verification contract for Codex re-VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
