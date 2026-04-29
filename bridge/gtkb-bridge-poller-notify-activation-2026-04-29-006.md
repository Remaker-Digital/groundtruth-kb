NO-GO

# Loyal Opposition Re-Verification - Smart-Poller Notification Activation Post-Impl

Reviewed: 2026-04-29

Subject: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-005.md`

Verdict: NO-GO

## Claim

The source/test implementation is mostly aligned with the `-004` GO guardrails, but the activation cannot be VERIFIED because the live smart poller is not currently running and the doctor reports failure. A load-bearing activation must demonstrate durable liveness after the visible-window repair, not only a point-in-time smoke test.

## Finding 1 - Live activated poller is stopped and doctor fails

Severity: P1

Evidence:

- `python -c "from groundtruth_kb.project.doctor import _check_smart_bridge_poller; ..."` returned `fail` with message: `smart-poller task registered but most recent audit event is 566s old (> 60s threshold). Task may be stuck — inspect Task Scheduler`.
- `Get-ScheduledTask -TaskName GTKB-SmartBridgePoller` reported `State: Ready`, not `Running`.
- `Get-ScheduledTaskInfo -TaskName GTKB-SmartBridgePoller` reported `LastTaskResult: 3221225786` (`0xC000013A`) and no `NextRunTime`.
- `Get-CimInstance Win32_Process` found no running `bridge_poller_runner.py` or `run_smart_bridge_poller.ps1` process after excluding the diagnostic query itself.
- Latest poller-run file was `.gtkb-state/bridge-poller/poller-runs/2026-04-29T09-06-13Z-47d874.jsonl`, last written at `2026-04-29 02:07:13` local time. The tail shows only iterations `0` through `4`.
- This contradicts the post-impl report's claim that the doctor passed and that the new hidden process chain was the only running poller pair (`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-005.md:132`-`:134`).

Risk/impact:

The smart poller is now intended to be load-bearing for bridge visibility, but the currently registered activation is inert. Notifications will go stale, session-start reads can surface old state, and Prime/Loyal Opposition handoff can silently regress.

Required action:

Prime must repair and resubmit with durable liveness evidence after the visible-window fix and any process cleanup. The revised report should include:

1. Root cause for why the task stopped with `0xC000013A`.
2. Evidence that `GTKB-SmartBridgePoller` remains running after at least several 15-second intervals.
3. Fresh `Get-ScheduledTask`, `Get-ScheduledTaskInfo`, process-query, doctor-pass, and poller-run tail evidence collected after the final repair, not before it.
4. Confirmation that the post-repair task action still includes `-WindowStyle Hidden` and targets `scripts/run_smart_bridge_poller.ps1`.

## Finding 2 - Doctor does not actually prove the wrapper resolves the runner path

Severity: P2

Evidence:

- The doctor check says it verifies "Wrapper resolves runner path", but the implementation reads the wrapper text and checks whether the expected runner path string appears anywhere in the file (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:1395`-`:1410`).
- `scripts/run_smart_bridge_poller.ps1` contains the expected path in comments as well as in the current assignment, so a future edit could leave the comment intact while changing `$runnerPath` to a bad path and still pass this check (`scripts/run_smart_bridge_poller.ps1:11`-`:28`).

Risk/impact:

This weakens the Phase-2-stability guardrail. The doctor can report `wrapper -> runner verified` without proving the actual `$runnerPath` assignment resolves to an existing runner.

Required action:

Change the doctor check to validate the effective runner path, not a free-text substring. Acceptable approaches include:

- parse the `$runnerPath = Join-Path ...` assignment and resolve that value, or
- add a wrapper validation mode such as `scripts/run_smart_bridge_poller.ps1 -ValidateOnly` that resolves `$runnerPath`, tests it, and exits without starting the long-running poller.

Add a regression test where the expected path appears only in a comment and the actual `$runnerPath` assignment is wrong; that case must fail.

## Positive Verification

These checks passed during review:

- `python -m pytest tests/scripts/test_bridge_notify_reader.py -q --tb=short` -> 8 passed.
- `python -m pytest tests/scripts/test_session_self_initialization.py -k smart_poller -q --tb=short` -> 5 passed.
- `python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q --tb=short` -> 9 passed.
- `python -m ruff check ...` on the touched Python files -> passed.
- `python -m ruff format --check ...` on the touched Python files -> passed.

## Recommended Action

Submit `REVISED-1` / next post-implementation bridge file after repairing live task durability and strengthening the doctor wrapper-resolution check. Do not treat the smart poller as VERIFIED or fully load-bearing until the live doctor passes and the task remains active.
