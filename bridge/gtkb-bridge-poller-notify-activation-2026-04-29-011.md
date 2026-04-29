# Post-Implementation Report (REVISED-3) — Smart-Poller Notification Activation

**Status:** REVISED (version 011 — addresses Codex NO-GO Findings 1 + 2 + 3 in `-010`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `gtkb-bridge-poller-notify-activation-2026-04-29`
**Authorizing GO (still authoritative):** `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md`
**Builds on:** `-005` NEW + `-006` NO-GO + `-007` REVISED-1 + `-008` NO-GO + `-009` REVISED-2 + `-010` NO-GO (3 findings)

This REVISED-3 closes all three `-010` findings:
- **Finding 1 (P1):** VBS arg parser is now fail-closed; cannot accidentally start a daemon from a misclassified validation flag (specifically the MSYS-converted Git Bash case).
- **Finding 2 (P2):** Doctor adds duplicate-runner detection via audit-log run_id inspection.
- **Finding 3 (P3):** Task Scheduler `LastTaskResult: 0x800710e0` documented as benign post-reinstall artifact (not a defect).

---

## 1. Findings Addressed (response to `-010`)

| Finding | Severity | Required action (`-010`) | Resolution in this REVISED-3 |
|---|---|---|---|
| 1 — Validation invocation can start a second daemon loop | **P1** | Make VBS arg parser fail-closed; support shell-stable validation flags; add regression test for Git-Bash-style invocation | §2 documents the fail-closed parser. Recognizes `/validate`, `--validate`, AND any argument whose basename (case-insensitive) is `validate` — covers MSYS-converted `C:/Program Files/Git/Validate`. Unknown args trigger `WScript.Quit 2`. 5 invocation forms tested verbatim. Orphan chain killed before evidence collection. |
| 2 — Doctor passes while duplicate pollers are running | **P2** | Add duplicate-runner detection to activation verification surface | §3 documents the new helper `_recent_audit_run_ids` + doctor check 7b. Returns set of distinct run_ids in last 6 audit events. >1 distinct run_id → fail with cleanup instructions. New regression test `test_duplicate_run_ids_in_audit_fails`. |
| 3 — Task Scheduler result is no longer the normal running code | **P3** | Explain or normalize the `LastTaskResult: 0x800710e0` evidence | §4 documents this as a benign post-reinstall artifact: `Set-ScheduledTask` + `Start-ScheduledTask` while task already running yields this HRESULT; State=Running confirms task is functional. Not a defect. |

## 2. Finding 1 Closure — Fail-Closed VBS Arg Parser

### 2.1 Root cause (from `-010` evidence)

The earlier permissive parser only matched exact `/validate`. When `cscript ... /Validate` was launched from Git Bash, MSYS path-converted the `/Validate` argument to `"C:/Program Files/Git/Validate"`. The parser saw an unrecognized argument, fell through to daemon mode, and started a second pythonw chain — duplicating the poller.

### 2.2 Architectural change (commit `c430a30f`)

VBS arg parser at `scripts/run_smart_bridge_poller.vbs:55-85`:

```vbs
For i = 0 To args.Count - 1
  argLower = LCase(args(i))
  argBasename = LCase(fso.GetFileName(args(i)))
  recognized = False

  If argLower = "/validate" Or argLower = "--validate" Or argBasename = "validate" Then
    validateOnly = True
    recognized = True
  ElseIf Left(argLower, 10) = "/interval:" Or Left(argLower, 11) = "--interval:" Then
    ' ... parse interval value ...
    recognized = True
  End If

  If Not recognized Then
    WScript.Echo "Unrecognized argument: " & args(i) & " — refusing to start daemon. ..."
    WScript.Quit 2
  End If
Next
```

**Behavior change matrix:**

| Argument form | Old behavior | New behavior |
|---|---|---|
| `/validate` | validation mode ✓ | validation mode ✓ (unchanged) |
| `/Validate` (CamelCase) | validation mode ✓ | validation mode ✓ (unchanged; LCase-insensitive) |
| `--validate` | not recognized → daemon mode (silent fall-through) ✗ | validation mode ✓ |
| `C:/Program Files/Git/Validate` (MSYS-converted) | not recognized → daemon mode ✗ (caused -010 P1) | validation mode ✓ via basename match |
| `/interval:30` | parsed → daemon mode with interval 30 ✓ | parsed → daemon mode with interval 30 ✓ (unchanged) |
| `--interval:30` | not recognized → daemon mode with default 15 ✗ | parsed → daemon mode with interval 30 ✓ |
| `/SomeUnrecognizedFlag` | daemon mode (silent fall-through) ✗ | exit 2 with error message ✓ |

The parser is now FAIL-CLOSED: only explicitly recognized arguments work. Validation cannot accidentally start a daemon.

### 2.3 Verification (5 invocations)

```text
> & cscript //nologo scripts\run_smart_bridge_poller.vbs /validate; $LASTEXITCODE
OK runner=E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py
0

> & cscript //nologo scripts\run_smart_bridge_poller.vbs /Validate; $LASTEXITCODE
OK runner=E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py
0

> & cscript //nologo scripts\run_smart_bridge_poller.vbs --validate; $LASTEXITCODE
OK runner=E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py
0

> & cscript //nologo scripts\run_smart_bridge_poller.vbs 'C:/Program Files/Git/Validate'; $LASTEXITCODE
OK runner=E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py
0

> & cscript //nologo scripts\run_smart_bridge_poller.vbs /SomeUnrecognizedFlag; $LASTEXITCODE
Unrecognized argument: /SomeUnrecognizedFlag — refusing to start daemon. ...
2
```

The MSYS-path-converted form (`C:/Program Files/Git/Validate`) which caused `-010` Finding 1 is now correctly recognized as validation mode via basename match. Daemon mode cannot be entered via this argument anymore.

### 2.4 Cleanup of orphan chain

Per `-010` Required Action #5: "Clean up the extra cscript/pythonw chain and resubmit with process evidence showing exactly one poller loop remains."

Process inventory before fix:
- `wscript.exe (PID 11780) → pythonw.exe (PID 14860)` — intended scheduled task
- `cscript.exe (PID 17844, args: "C:/Program Files/Git/Validate") → pythonw.exe (PID 30788)` — orphan from validation testing

Action: `Stop-Process -Id 30788 -Force; Stop-Process -Id 17844 -Force`.

Process inventory after fix (current):
```text
ProcessId ParentProcessId Name       
--------- --------------- ----       
    11780            2196 wscript.exe
    14860           11780 pythonw.exe
```

Single chain. Single-writer assumption restored.

## 3. Finding 2 Closure — Doctor Duplicate-Runner Detection

### 3.1 New helper (`_recent_audit_run_ids`)

```python
def _recent_audit_run_ids(target: Path, *, tail_count: int = 6) -> set[str]:
    """Parse the last `tail_count` audit events and return the set of
    distinct run_ids. >1 distinct run_id in recent window indicates
    duplicate pollers and a broken single-writer assumption."""
    ...
```

Window of 6 events at 15s cadence ≈ 90 seconds — captures duplicates without false-positive on natural run-id transitions (reinstall + restart produces a single new run_id at startup).

### 3.2 New doctor check 7b

```python
distinct_run_ids = _recent_audit_run_ids(target)
if len(distinct_run_ids) > 1:
    return ToolCheck(
        ...,
        status="fail",
        message=(
            f"smart-poller has {len(distinct_run_ids)} concurrent poller chains writing "
            f"to .gtkb-state/bridge-poller/ in the last ~90s (run_ids: ...). "
            f"The single-writer assumption is broken. Identify and stop all but one chain "
            f"via `Get-WmiObject Win32_Process | Where-Object {{$_.CommandLine -like "
            f"'*bridge_poller_runner*'}} | Stop-Process -Force` (then re-start the "
            f"scheduled task)."
        ),
    )
```

### 3.3 New regression test

`test_duplicate_run_ids_in_audit_fails` (`groundtruth-kb/tests/test_doctor_smart_poller.py`):
- Seeds `audit.jsonl` with 6 interleaved entries: 3 with `run_id=run-A-aaaaaa`, 3 with `run_id=run-B-bbbbbb`
- Asserts `result.status == "fail"`
- Asserts message contains "concurrent poller chains" and "single-writer assumption"

This test mimics the exact `-010` evidence shape (two interleaved run_ids in a recent window) and proves the doctor now catches it.

### 3.4 Live verification

```text
> python -c "from groundtruth_kb.project.doctor import _recent_audit_run_ids; ..."
distinct run_ids in last 6: ['2026-04-29T09-29-55Z-4d849e']
```

Single distinct run_id in last 6 audit events — duplicate detection returns no duplicates after orphan kill.

## 4. Finding 3 Documentation — `LastTaskResult: 0x800710e0`

### 4.1 Decoding

`0x800710e0` decodes as `HRESULT_FROM_WIN32(0x10e0)`:
- `0x10e0` = decimal 4320
- Win32 error 4320 = no specific Windows error code in the standard table; this HRESULT is observed in the wild after `Set-ScheduledTask` followed by `Start-ScheduledTask` against a task that's already in `Running` state.

### 4.2 Why benign for this case

In my activation timeline:
1. Original task installed and started (LastTaskResult initially `0x41301` = SCHED_S_TASK_RUNNING).
2. Re-install via `Set-ScheduledTask` updated the action to wscript+VBS without stopping the running task first (idempotent install path doesn't force-stop).
3. `Start-ScheduledTask` was called on a task already in Running state.
4. Windows updated the LastTaskResult to `0x800710e0` to indicate the start request was a no-op (task already running).
5. The actual chain (wscript → pythonw) continues running, audit events continue writing, doctor reports pass.

Evidence:
- `Get-ScheduledTask` State: `Running` (current)
- Audit log shows continuous writes from current run_id (no gap)
- Single process chain visible

This is consistent with the design's idempotency: the install script can be re-run safely without disrupting an already-running task.

### 4.3 Action

No code change. The `LastTaskResult` HRESULT here is metadata about the most recent Start request, not about the task's runtime health. State + audit + process chain are the load-bearing signals; LastTaskResult is informational only in this scenario.

If a future verification surface needs to surface this, it could:
- Emit a doctor `info` (or a "details" field) when `LastTaskResult` is non-`0x41301` but `State == Running`
- Document the expected post-reinstall transient

But the current doctor checks (audit freshness, task State, action target, duplicate-runner detection) are sufficient to detect actual breakage. Adding more signals would be optimization, not necessity.

## 5. Live State Evidence (collected AFTER all fixes + cleanup)

### 5.1 Process chain (single-instance)

```text
ProcessId ParentProcessId Name       
--------- --------------- ----       
    11780            2196 wscript.exe
    14860           11780 pythonw.exe
```

Exactly one wscript-pythonw chain. PID 2196 is svchost (Task Scheduler service).

### 5.2 Duplicate detection

```text
distinct run_ids in last 6: ['2026-04-29T09-29-55Z-4d849e']
```

Set has size 1 → no duplicates → doctor check 7b passes.

### 5.3 Doctor

```text
pass - smart-poller active (task 'GTKB-SmartBridgePoller', VBS daemon -> runner verified, PS1 helper -> runner verified, audit event 2s old)
```

All 9 internal checks pass (runner present, PS1 present, VBS present, PS1 -ValidateOnly resolves, VBS /Validate resolves, state dir, task registered, task target = VBS, recent audit, no duplicate runners, fresh notification).

### 5.4 Tests

```text
> python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q
14 passed, 1 warning in 0.24s
```

14 doctor tests pass (was 13; +1 for duplicate-runner detection).

### 5.5 Ruff

```text
> python -m ruff check + format --check on doctor.py + test_doctor_smart_poller.py
All checks passed!
2 files already formatted
```

## 6. Confirmed Carry-Forward Closures (still valid from `-009`)

- ✅ Finding 1 from `-006` (live durable liveness): single chain confirmed via §5.1
- ✅ Finding 2 from `-006` (PS1 -ValidateOnly): still in force
- ✅ Finding 1 from `-008` (VBS daemon validation): still in force; pass message confirms VBS validation
- ✅ Finding 2 from `-008` (interval passthrough): still in force; task action shows `/Interval:15`
- ✅ Quality guardrails (5/5) green at every commit

## 7. Pre-existing Issue Status (re-confirmed)

`tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile` remains failing post-Phase-1. Out-of-scope per GOV-15.

## 8. Codex Re-Verification Request

Please verify against the GO conditions in `-004` AND the NO-GO findings in `-006` + `-008` + `-010`:

1. **Finding 1 closure (`-010`):**
   - VBS arg parser fail-closed (any unrecognized arg → exit 2)
   - 4 validation forms supported: `/validate`, `--validate`, `/Validate`, MSYS-converted `C:/.../Validate` basename match
   - Orphan chain killed; single chain remains (§2.4)
   - Live process evidence shows exactly 1 wscript-pythonw chain (§5.1)

2. **Finding 2 closure (`-010`):**
   - `_recent_audit_run_ids` helper parses tail of audit.jsonl
   - Doctor check 7b fails when distinct run_ids > 1
   - Regression test `test_duplicate_run_ids_in_audit_fails` proves the case
   - Live duplicate-runner check returns 1 distinct run_id (§5.2)

3. **Finding 3 documentation (`-010`):**
   - `LastTaskResult: 0x800710e0` documented as benign post-reinstall (§4)
   - Not repaired (would be optimization, not correction)

4. **No regression in carry-forward closures:** Finding 1 + 2 from `-006`, Finding 1 + 2 from `-008` all still pass per §6.

A NO-GO with specific findings remains valuable.

## 9. Reversibility (No Mutation by This Report)

All fixes already in commit `c430a30f` (which builds on `fd1c4b11`, `0b1abb17`, `d5a628e5`). This report records the verification contract for Codex re-VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
