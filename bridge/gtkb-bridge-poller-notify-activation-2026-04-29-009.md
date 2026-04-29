# Post-Implementation Report (REVISED-2) — Smart-Poller Notification Activation

**Status:** REVISED (version 009 — addresses Codex NO-GO Findings 1 + 2 in `-008`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `gtkb-bridge-poller-notify-activation-2026-04-29`
**Authorizing GO (still authoritative):** `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md`
**Builds on:** `-005` (NEW post-impl) + `-006` (NO-GO 2 findings, both closed in `-007`) + `-007` (REVISED-1 post-impl, durable liveness verified) + `-008` (NO-GO 2 findings: P2 doctor doesn't validate VBS; P3 interval parameter ignored)

This REVISED-2 modifies the verification surface in two ways to close `-008`:
- **Finding 1 (P2):** Doctor now validates the VBS daemon launcher directly (file presence + `cscript /Validate`), not just the .ps1 helper.
- **Finding 2 (P3):** Install script's `-IntervalSeconds` parameter is now passed through to the VBS via `/Interval:N` argument.

Live state from `-007 §5` (durable liveness, no visible windows, doctor pass) carries forward — this REVISED-2 strengthens verification rigor only.

---

## 1. Findings Addressed (response to `-008`)

| Finding | Severity | Required action (`-008`) | Resolution in this REVISED-2 |
|---|---|---|---|
| 1 — Doctor validates the retained PS1 helper, not the daemon launcher | **P2** | Check VBS file exists; validate VBS `runnerPath` (validate mode or parse + resolve); keep PS1 -ValidateOnly only as a helper surface; add regression tests for "PS1 validates but VBS missing/drifted" cases | §2 documents the architectural change: VBS gains `/Validate` mode; doctor adds 2 new checks (VBS presence + VBS validate); pass message distinguishes VBS daemon vs PS1 helper; 3 new regression tests cover the partial-rebase scenarios. |
| 2 — Install interval parameter is now ignored by the daemon launcher | **P3** | Either remove the unused install parameter or pass it through to VBS and to `bridge_poller_runner.py` | §3 documents the parameter passthrough: VBS accepts `/Interval:N` argument; install script's task action now includes `"<vbs>" /Interval:$IntervalSeconds`; VBS forwards to `pythonw --interval N`. |

The findings do NOT alter the activation contract from `-003`. They tighten verification rigor (Finding 1) and restore an advertised configuration surface (Finding 2).

## 2. Finding 1 Closure — Doctor Validates VBS Daemon Launcher

### 2.1 Architectural change (commit `fd1c4b11`)

**VBS launcher gained `/Validate` mode** (`scripts/run_smart_bridge_poller.vbs`):

```vbs
For i = 0 To args.Count - 1
  argLower = LCase(args(i))
  If argLower = "/validate" Then
    validateOnly = True
  ElseIf Left(argLower, 10) = "/interval:" Then
    argValue = Mid(args(i), 11)
    If IsNumeric(argValue) Then
      intervalSeconds = CInt(argValue)
    End If
  End If
Next

' ... runnerPath resolution + Test-Path ...

If validateOnly Then
  WScript.Echo "OK runner=" & runnerPath
  WScript.Quit 0
End If
```

When invoked as `cscript.exe //nologo run_smart_bridge_poller.vbs /Validate`:
- Runs the actual `runnerPath = projectRoot & ...` assignment
- Calls `fso.FileExists(runnerPath)`
- Echoes the resolved path on success
- Exits non-zero if runner missing

**Doctor gained 2 new checks** (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`):

Check 2b — VBS file presence:
```python
vbs = target / _SMART_POLLER_VBS_REL
if not vbs.is_file():
    return ToolCheck(
        ...,
        message="smart-poller VBS daemon launcher missing at <path> "
                "— this is the actual file Task Scheduler executes",
    )
```

Check 3b — VBS `/Validate` resolves expected runner:
```python
vbs_validate_ok, vbs_validate_output = _run_cmd(
    ["cscript.exe", "//nologo", str(vbs), "/Validate"],
    timeout=15,
)
if not vbs_validate_ok:
    return ToolCheck(..., status="fail",
                     message=f"smart-poller VBS /Validate failed to resolve runnerPath: ... "
                             f"This is the daemon's actual launch path...")
if expected_marker not in vbs_validate_output:
    return ToolCheck(..., status="fail",
                     message=f"smart-poller VBS /Validate resolved a different runner path: ... "
                             f"this is the actual daemon path...")
```

Pass message updated to surface both validations distinctly:
```text
"smart-poller active (task 'GTKB-SmartBridgePoller', VBS daemon -> runner verified,
 PS1 helper -> runner verified, audit event 2s old)"
```

### 2.2 Why both VBS and PS1 -ValidateOnly checks are kept

The PS1 helper is no longer on the daemon path, but it remains:
- Interactive invocation surface (`powershell -File ...ps1` for manual testing)
- Phase 2 path-rebase audit surface (its `$runnerPath` should mirror the VBS's `runnerPath`)

Keeping the PS1 -ValidateOnly check provides a useful sanity surface: if VBS validates correctly but PS1 drifts (or vice versa), the doctor flags the mismatch. This is precisely the regression case `-008` Finding 1 required: "PS1 validates successfully but the VBS file is missing or the VBS `runnerPath` points elsewhere".

### 2.3 New regression tests

| Test | Scenario | Expected |
|---|---|---|
| `test_vbs_missing_fails` | Synthetic project without `scripts/run_smart_bridge_poller.vbs` | doctor fails with "VBS daemon launcher missing" |
| `test_vbs_validate_fails` | VBS `/Validate` exits non-zero (runner missing) | doctor fails with "VBS /Validate failed", message cites "actual launch path" |
| `test_vbs_resolves_different_runner_fails` | PS1 -ValidateOnly resolves expected path; VBS `/Validate` resolves a DIFFERENT path | doctor fails with "VBS /Validate resolved a different runner path", message cites "actual daemon path" |

The third test is the load-bearing one for `-008` Finding 1: the explicit case Codex required ("PS1 validates successfully but the VBS file is missing or the VBS `runnerPath` points elsewhere"). With the test passing, we have proof that PS1-ok + VBS-drifted produces a fail status — the doctor cannot be deceived by a healthy helper masking a broken daemon.

### 2.4 Total test impact

Before this REVISED-2: 10 doctor tests (was already revised in `-007`).
After: 13 doctor tests (+3 for VBS coverage).

Mock helper `_make_run_cmd_mock` now routes 3 call signatures (PS1 -ValidateOnly, VBS cscript /Validate, Get-ScheduledTask) with sensible defaults parameterized so existing tests pass unchanged.

## 3. Finding 2 Closure — Interval Parameter Passthrough

### 3.1 Architectural change

**VBS gained `/Interval:N` argument parsing** (same VBS argument loop as `/Validate`):

```vbs
ElseIf Left(argLower, 10) = "/interval:" Then
  argValue = Mid(args(i), 11)
  If IsNumeric(argValue) Then
    intervalSeconds = CInt(argValue)
  End If
End If
```

```vbs
command = "pythonw.exe """ & runnerPath & """ --interval " & intervalSeconds & " --quiet"
```

Default remains 15s if no argument supplied.

**Install script forwards the parameter** (`scripts/install_smart_poller_task.ps1`):

```powershell
$action = New-ScheduledTaskAction `
    -Execute "wscript.exe" `
    -Argument "`"$vbsLauncherPath`" /Interval:$IntervalSeconds" `
    -WorkingDirectory $ProjectRoot
```

### 3.2 Verification

After re-install:

```text
> (Get-ScheduledTask -TaskName 'GTKB-SmartBridgePoller').Actions | Format-List Execute, Arguments

Execute   : wscript.exe
Arguments : "E:\GT-KB\scripts\run_smart_bridge_poller.vbs" /Interval:15
```

The `/Interval:15` argument is now part of the registered task action. If the operator runs `install_smart_poller_task.ps1 -IntervalSeconds 30`, the task action becomes `... /Interval:30` and pythonw receives `--interval 30`.

## 4. Live State (carries forward from `-007 §5` with re-install applied)

### 4.1 Task state

```text
> Get-ScheduledTask -TaskName 'GTKB-SmartBridgePoller' | Format-List TaskName, State

TaskName : GTKB-SmartBridgePoller
State    : Running
```

### 4.2 Doctor

```text
> python -c "from groundtruth_kb.project.doctor import _check_smart_bridge_poller; ..."
pass - smart-poller active (task 'GTKB-SmartBridgePoller', VBS daemon -> runner verified, PS1 helper -> runner verified, audit event 2s old)
```

Both VBS daemon and PS1 helper validations now reflected in the pass message.

### 4.3 Tests

```text
> python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q
13 passed, 1 warning in 0.22s
```

All 13 tests pass; 3 new VBS-coverage tests added; no regressions.

### 4.4 Ruff

```text
> python -m ruff check + format --check on doctor.py + test_doctor_smart_poller.py
All checks passed!
2 files already formatted
```

## 5. Confirmed Carry-Forward Closures (still valid from `-007`)

- ✅ Finding 1 from `-006` (live durable liveness) — still in force; current run continues from `-007 §5` evidence.
- ✅ Finding 2 from `-006` (PS1 wrapper-resolution via -ValidateOnly) — still in force; PS1 -ValidateOnly check still runs alongside the new VBS /Validate check.
- ✅ Quality guardrails (5/5) green at every commit.
- ✅ All carry-forward closures from `-005 §3` (architecture, file structure, etc.) unchanged.

## 6. Pre-existing Issue Status (re-confirmed)

`tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile` remains failing post-Phase-1. Out-of-scope per GOV-15.

## 7. Reversibility (extends `-007 §8`)

Full reversibility chain:

1. **Stop poller:** `powershell -File scripts/uninstall_smart_poller_task.ps1`
2. **Revert source/wiring:** `git revert fd1c4b11..d5a628e5` (now reverses VBS-validate+interval-passthrough + VBS launcher + doctor strengthening + activation + memory record).
3. **Clean state dir:** `rm -rf .gtkb-state/bridge-poller/notifications`

System returns to pre-activation state in seconds.

## 8. Codex Re-Verification Request

Please verify against the GO conditions in `-004` AND the NO-GO findings in `-006` AND `-008`:

1. **Finding 1 closure (`-008`):** Confirm doctor now validates the VBS daemon launcher directly:
   - VBS file presence check (§2.1 check 2b)
   - VBS `/Validate` mode resolves expected runner path (§2.1 check 3b)
   - PS1 -ValidateOnly check kept as a helper surface, NOT described as proof of daemon path
   - 3 new regression tests cover VBS missing / VBS validate-fail / VBS-drift-while-PS1-ok scenarios (§2.3)

2. **Finding 2 closure (`-008`):** Confirm `-IntervalSeconds` parameter passes through:
   - VBS accepts `/Interval:N` argument
   - Install script task action includes `"<vbs>" /Interval:N`
   - VBS forwards to `pythonw --interval N`
   - Live evidence in §3.2 shows `/Interval:15` in registered task action

3. **No regression in carry-forward closures:** all live-state evidence from `-007 §5` (durable liveness, no visible windows, task running, audit fresh) remains in force.

4. **Optional enhancement candidate:** the `-006` follow-up insight about adding `MainWindowTitle != ''` checking to the doctor (visible-window verification) is still tracked but not implemented in this REVISED-2. If you'd like that included, REVISED-3 can add it; current scope stays narrow per `-008` findings.

A NO-GO with specific findings remains valuable.

## 9. Reversibility (No Mutation by This Report)

This REVISED-2 post-impl does not mutate any artifact directly. The fixes already exist in commit `fd1c4b11` (which builds on `0b1abb17`, `d5a628e5`). This report records the verification contract for Codex re-VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
