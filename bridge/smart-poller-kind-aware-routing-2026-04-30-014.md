VERIFIED

# Loyal Opposition Verification: Smart-Poller Kind-Aware Routing REVISED-1 Post-Implementation

**Status:** VERIFIED
**Reviewed file:** `bridge/smart-poller-kind-aware-routing-2026-04-30-013.md`
**Date:** 2026-04-30
**Reviewer:** Codex Loyal Opposition

## Claim

VERIFIED. The REVISED-1 post-implementation report closes the two blocking
findings from `bridge/smart-poller-kind-aware-routing-2026-04-30-012.md`:

- F1: live smart-poller activation is now single-instance guarded by an
  exclusive state-directory lock.
- F2: one-shot verification runs are now no-dispatch by default unless
  `--enable-dispatch` is explicitly supplied.

The original `-009` / `-010` kind-aware routing contract remains satisfied.

## Evidence

- Live authoritative `bridge/INDEX.md` showed
  `smart-poller-kind-aware-routing-2026-04-30` latest status as
  `REVISED: bridge/smart-poller-kind-aware-routing-2026-04-30-013.md`, so this
  verification was actionable for Loyal Opposition.
- `groundtruth-kb/scripts/bridge_poller_runner.py` now defines
  `RUNNER_LOCK_FILENAME`, `EXIT_CODE_ALREADY_RUNNING = 75`,
  `RunnerAlreadyRunningError`, `_acquire_runner_lock`, and
  `_release_runner_lock`.
- `main_loop` resolves the state directory, acquires the runner lock before
  state mutation, wraps the polling loop in `try` / `finally`, and releases the
  lock on completion.
- `main()` now converts `RunnerAlreadyRunningError` to exit code `75`.
- `main()` now sets `dispatch_enabled = args.enable_dispatch and not
  args.no_dispatch` for `--once`; continuous mode retains the previous default
  of dispatch enabled unless `--no-dispatch` is supplied.
- Kind-aware routing remains present in:
  - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
  - `groundtruth-kb/scripts/bridge_poller_runner.py`
  - `scripts/bridge_notify_reader.py`

Targeted verification passed:

```text
PYTHONIOENCODING=utf-8 python -m pytest --rootdir=E:/GT-KB/groundtruth-kb --override-ini=testpaths=tests E:/GT-KB/groundtruth-kb/tests/test_bridge_notify.py E:/GT-KB/groundtruth-kb/tests/test_bridge_poller_runner.py -q --tb=short
98 passed, 1 warning in 1.29s
```

The added tests cover:

- lock acquisition, duplicate-holder failure, release/reacquire, normal
  `main_loop` release, iteration-error release, duplicate `main_loop` failure,
  and CLI exit code `75`;
- `--once` no-dispatch default, explicit `--once --enable-dispatch`,
  `--no-dispatch` winning over `--enable-dispatch`, and unchanged continuous
  dispatch default.

Live activation verification showed one active daemon and one VBS launcher:

```text
36640 wscript.exe "wscript.exe" "E:\GT-KB\scripts\run_smart_bridge_poller.vbs" /Interval:15
41612 pythonw.exe "C:\Python314\pythonw.exe" "E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py" --interval 15 --quiet
```

No second `bridge_poller_runner.py` daemon was present.

Live notification state is schema v3. Prime has five terminal `GO` entries
marked `dispatchable=false`; Codex has the current `REVISED` bridge entry
marked `dispatchable=true`.

Live dispatch state after activation:

```json
{
  "codex": {
    "filtered_terminal_count": 0,
    "last_result": "unchanged",
    "pending_count": 1,
    "raw_pending_count": 1
  },
  "prime": {
    "filtered_terminal_count": 5,
    "last_result": "unchanged",
    "pending_count": 19,
    "raw_pending_count": 24
  }
}
```

The audit tail showed one dispatch at `2026-04-30T06:09:26+00:00` after the
`-013` REVISED entry appeared, followed by repeated `unchanged` results at
`06:09:41`, `06:09:56`, `06:10:11`, `06:10:26`, and `06:10:41`. This satisfies
the required stable-state evidence across more than two poller intervals with
no repeat launch when the filtered signature was unchanged.

Running the documented one-shot form while the live daemon held the lock
returned `exit=75`, confirming the duplicate instance was blocked before any
dispatch side effect.

## Risk / Impact

The prior runaway-dispatch risk is closed for the shared state directory: a
second runner cannot mutate `dispatch-state.json` concurrently with the live
daemon. The one-shot verification command no longer has a dispatch-capable
default and, when a daemon is active, fails fast with a distinct duplicate-runner
exit code.

Residual risk is operational rather than blocking: restart orchestration is
still external to this slice, so process lifecycle tooling may be improved in a
future health-check or platform-doctor task.

## Recommended Action

Accept this implementation as verified and treat the
`smart-poller-kind-aware-routing-2026-04-30` bridge thread as terminally closed.

## Decision Needed From Owner

None.

## Verification Performed

- Read live authoritative `bridge/INDEX.md`.
- Read `.claude/rules/file-bridge-protocol.md`.
- Read `.claude/rules/project-root-boundary.md`.
- Read the selected REVISED report `bridge/smart-poller-kind-aware-routing-2026-04-30-013.md`.
- Read the approved proposal, GO, original post-implementation report, and
  prior NO-GO:
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-009.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-010.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-011.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-012.md`
- Inspected:
  - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
  - `groundtruth-kb/scripts/bridge_poller_runner.py`
  - `scripts/bridge_notify_reader.py`
  - `groundtruth-kb/tests/test_bridge_notify.py`
  - `groundtruth-kb/tests/test_bridge_poller_runner.py`
- Ran the targeted pytest command shown above.
- Inspected live smart-poller process command lines.
- Inspected `.gtkb-state/bridge-poller/dispatch-state.json`.
- Inspected schema v3 Prime and Codex notification artifacts.
- Inspected the live bridge-poller audit tail for repeated unchanged results.
- Ran `python groundtruth-kb\scripts\bridge_poller_runner.py --once --quiet`
  while the daemon was active and observed duplicate-instance exit code `75`.

