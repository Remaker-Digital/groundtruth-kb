VERIFIED

# Loyal Opposition Re-Verification - Smart-Poller Notification Activation REVISED-3

Reviewed: 2026-04-29

Subject: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-011.md`

Verdict: VERIFIED

## Claim

`-011` closes the outstanding `-010` findings. The smart-poller activation is now live, single-instance, windowless, and covered by a doctor check that validates both the VBS daemon launcher and the PS1 helper surface.

## Evidence Reviewed

- Revised report: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-011.md`.
- Prior NO-GO: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-010.md`.
- Current implementation commit: `c430a30f` (`smart-poller: fail-closed VBS arg parser + duplicate-runner detection`), on top of the earlier activation commits.
- Current launcher/doctor files:
  - `scripts/run_smart_bridge_poller.vbs`
  - `scripts/install_smart_poller_task.ps1`
  - `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
  - `groundtruth-kb/tests/test_doctor_smart_poller.py`

## Finding Closure

### 1. Validation cannot accidentally start another daemon - CLOSED

The VBS parser is now fail-closed:

- `/validate` -> validation mode.
- `--validate` -> validation mode.
- `C:/Program Files/Git/Validate` -> validation mode via basename match, covering the MSYS/Git Bash path-conversion case that caused the duplicate daemon in `-010`.
- Unknown arguments exit with code `2` instead of falling through to daemon mode.

Live validation:

- `cscript.exe //nologo scripts\run_smart_bridge_poller.vbs /validate` returned `OK runner=...`, exit `0`.
- `cscript.exe //nologo scripts\run_smart_bridge_poller.vbs --validate` returned `OK runner=...`, exit `0`.
- `cscript.exe //nologo scripts\run_smart_bridge_poller.vbs "C:/Program Files/Git/Validate"` returned `OK runner=...`, exit `0`.
- `cscript.exe //nologo scripts\run_smart_bridge_poller.vbs /SomeUnrecognizedFlag` returned the fail-closed error and exit `2`.

After those checks, process inspection still showed exactly one intended chain:

- `wscript.exe "E:\GT-KB\scripts\run_smart_bridge_poller.vbs"`
- child `pythonw.exe "E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py" --interval 15 --quiet`

### 2. Doctor detects duplicate pollers - CLOSED

`groundtruth-kb/src/groundtruth_kb/project/doctor.py` now includes `_recent_audit_run_ids(...)` and fails when recent audit events contain more than one run ID. The targeted regression test `test_duplicate_run_ids_in_audit_fails` covers the exact failure mode from `-010`.

Live evidence:

- `_recent_audit_run_ids(Path("."))` returned one run ID: `2026-04-29T09-29-55Z-4d849e`.
- The audit tail showed only that run ID in the recent window, with continued 15-second cadence through at least iteration `140`.
- Live doctor returned `pass`: `smart-poller active (task 'GTKB-SmartBridgePoller', VBS daemon -> runner verified, PS1 helper -> runner verified, audit event 5s old)`.

### 3. Task Scheduler result-code concern - ACCEPTED AS NON-BLOCKING

`Get-ScheduledTask` reports `State: Running`; live audit and process evidence prove the daemon is operating. The reported `LastTaskResult: 0x800710e0` is accepted as informational post-reinstall/start metadata, not a blocker for this activation, because the load-bearing signals are task state, process chain, audit freshness, and doctor pass.

## Verification Commands

Executed during review:

- `python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q --tb=short` -> 14 passed, 1 warning.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_smart_poller.py` -> passed.
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_smart_poller.py` -> passed.
- Live VBS validation forms listed above.
- Live process, scheduled-task, audit-tail, and no-visible-window checks.

## Residual Notes

- Duplicate detection is intentionally conservative. A clean restart may temporarily show multiple recent run IDs until the new run has enough audit entries, but that is a safe failure mode compared with accepting concurrent writers.
- The separate orient-verification thread remains latest `NO-GO` and should be revised now that activation is VERIFIED.

## Final Status

Smart-poller notification activation is VERIFIED.
