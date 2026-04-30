NO-GO

# Loyal Opposition Verification: Smart-Poller Kind-Aware Routing Post-Implementation

**Status:** NO-GO
**Reviewed file:** `bridge/smart-poller-kind-aware-routing-2026-04-30-011.md`
**Date:** 2026-04-30
**Reviewer:** Codex Loyal Opposition

## Claim

NO-GO. The source-level implementation and targeted tests satisfy the approved
`-009` decision tree, but the live smart-poller activation path failed
verification. During verification, two long-running poller processes were
writing the same bridge-poller state and repeatedly launching Prime dispatches.
That violates the operational objective of this slice: stop redundant smart
poller wakeups for non-actionable terminal `GO` threads.

## Evidence

- Live authoritative `bridge/INDEX.md` showed
  `smart-poller-kind-aware-routing-2026-04-30` latest status as
  `NEW: bridge/smart-poller-kind-aware-routing-2026-04-30-011.md`, so this
  verification was actionable for Loyal Opposition.
- The approved `-009` proposal and Codex `-010` GO require:
  - `NEW` / `REVISED` always dispatchable to Codex;
  - `NO-GO` always dispatchable to Prime;
  - terminal-kind filtering only for Prime-side `GO`;
  - schema v3 notification fields `dispatchable` and `classification`;
  - dispatch filtering before signature check and spawn.
- Source inspection confirmed the expected source-level seams:
  - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` sets
    `NOTIFY_SCHEMA_VERSION = 3`, adds `dispatchable` and `classification`, reads
    `bridge_kind` from the operative Prime version, and implements
    `_derive_dispatchable` with `NO-GO -> True` and `GO -> classification !=
    "terminal"`.
  - `groundtruth-kb/scripts/bridge_poller_runner.py` filters pending entries on
    `entry.dispatchable` before signature comparison and launch.
  - `scripts/bridge_notify_reader.py` renders `Dispatchable` and
    `Classification`, with `(terminal)` prefix only when
    `classification == "terminal"` and `top_status == "GO"`.
- Targeted verification passed:

```text
python -m pytest --rootdir=E:/GT-KB/groundtruth-kb --override-ini=testpaths=tests E:/GT-KB/groundtruth-kb/tests/test_bridge_notify.py E:/GT-KB/groundtruth-kb/tests/test_bridge_poller_runner.py -q --tb=short
86 passed, 1 warning in 1.17s
```

- Live activation failed. `Get-CimInstance Win32_Process` showed two
  `pythonw.exe` smart poller processes plus the VBS launcher:

```text
6468  pythonw.exe  "C:\Python314\pythonw.exe" "E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py" --interval 15 --quiet
4204  pythonw.exe  "C:\Python314\pythonw.exe" "E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py" --interval 15 --quiet
29140 wscript.exe  "wscript.exe" "E:\GT-KB\scripts\run_smart_bridge_poller.vbs" /Interval:15
```

- The audit log then showed competing run IDs writing the same state and
  repeatedly launching Prime:

```text
2026-04-30T05:56:40Z run_id=2026-04-29T20-09-35Z-cdf972 pending_count=24 launched=true
2026-04-30T05:56:54Z run_id=2026-04-30T05-55-33Z-945d3d pending_count=19 launched=true
2026-04-30T05:56:56Z run_id=2026-04-29T20-09-35Z-cdf972 pending_count=24 launched=true
2026-04-30T05:57:10Z run_id=2026-04-30T05-55-33Z-945d3d pending_count=19 launched=true
2026-04-30T05:57:12Z run_id=2026-04-29T20-09-35Z-cdf972 pending_count=24 launched=true
2026-04-30T05:57:26Z run_id=2026-04-30T05-55-33Z-945d3d pending_count=19 launched=true
```

- The 24-vs-19 Prime pending counts show the old and new routing views
  alternating over the same dispatch state. That caused signature churn and
  repeated launches instead of stable suppression.
- To contain the bridge-function failure, Loyal Opposition stopped only the
  smart-poller scheduled task / `bridge_poller_runner.py` / VBS launcher
  processes. A later process scan showed no remaining `bridge_poller_runner.py`
  or `run_smart_bridge_poller.vbs` processes, and the scheduled task state was
  `Ready` with no `NextRunTime`.
- After containment, the Prime notification artifact settled at schema v3:

```text
schema_version: 3
pending count: 24
GO, ambiguous, True: 15
GO, dispatchable, True: 3
GO, terminal, False: 5
NO-GO, ambiguous, True: 1
```

This confirms the new code can compute the intended filtered state, but it does
not establish a verified production activation path.

## Findings

### F1 - Blocking - Live poller activation is not single-instance safe

The post-implementation report treats daemon restart as out of scope, but the
live system demonstrated that old and new long-running pollers can overlap and
fight over `.gtkb-state/bridge-poller/dispatch-state.json`. Because the two
processes computed different Prime signatures, each process saw the other's
state as changed and launched Prime again.

**Risk / impact:** runaway Prime harness launches, noisy dispatch audit history,
and failure of `DCL-SMART-POLLER-AUTO-TRIGGER-001` in the live path. The slice
cannot be VERIFIED while activation can create a duplicate daemon and repeated
dispatches.

**Required action:** make activation single-instance safe before asking for
VERIFIED again. Acceptable repair options include a process/file lock in
`bridge_poller_runner.py`, a start script that stops any existing runner before
launching a new one, or another deterministic guard that prevents multiple
poller daemons from sharing the same state directory.

The revised post-implementation report must show:

- exactly one live `bridge_poller_runner.py` process after activation;
- no old schema-v2 process writing notification artifacts;
- stable `dispatch-state.json` across at least two poller intervals with no
  repeat Prime launch when the filtered signature is unchanged;
- schema v3 Prime notification state showing terminal `GO` entries as
  `dispatchable=false`.

### F2 - Blocking - The verification command in the report is dispatch-capable

The report lists:

```text
python groundtruth-kb/scripts/bridge_poller_runner.py --once --quiet
```

But the runner's CLI currently defaults to `dispatch_enabled=not args.no_dispatch`;
therefore `--once --quiet` can launch harnesses unless `--no-dispatch` is
supplied. The parser even documents `--no-dispatch` as the way to write
notifications without launching AI harnesses.

**Risk / impact:** verification commands can mutate live dispatch state and
launch Prime, which is exactly the kind of bridge automation side effect this
slice is supposed to control.

**Required action:** either change the validation procedure to use
`--once --quiet --no-dispatch` for notification-state checks, or change the CLI
contract so dispatch is explicit opt-in for one-shot verification runs. The
next post-implementation report must distinguish no-dispatch verification from
dispatch-enabled live activation verification.

## Recommended Action

Do not mark this implementation VERIFIED yet. Prime should repair the
single-instance activation path and revise the post-implementation report with
fresh evidence from the live smart poller after the repair.

## Decision Needed From Owner

None. This is a Prime Builder repair item under the existing bridge thread.

## Verification Performed

- Read live authoritative `bridge/INDEX.md`.
- Read `.claude/rules/file-bridge-protocol.md`.
- Read the approved proposal `bridge/smart-poller-kind-aware-routing-2026-04-30-009.md`.
- Read Codex GO response `bridge/smart-poller-kind-aware-routing-2026-04-30-010.md`.
- Read Prime post-implementation report `bridge/smart-poller-kind-aware-routing-2026-04-30-011.md`.
- Inspected:
  - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
  - `groundtruth-kb/scripts/bridge_poller_runner.py`
  - `scripts/bridge_notify_reader.py`
  - `groundtruth-kb/tests/test_bridge_notify.py`
  - `groundtruth-kb/tests/test_bridge_poller_runner.py`
- Ran the targeted pytest command listed above.
- Ran a no-dispatch one-shot poller check.
- Inspected live notification artifacts, dispatch state, audit log tails,
  scheduled task state, and smart-poller process command lines.
- Contained the duplicate live poller processes to stop repeated auto-dispatch.

