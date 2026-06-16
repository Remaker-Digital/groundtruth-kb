# DEPRECATED — Bridge Permanent Operations Runbook (Retired 2026-06-11, FAB-05 / HYG-018)

> ⚠️ **DEPRECATED / RETIRED.** This runbook formerly mandated 3-minute OS bridge
> pollers plus repair/verification commands. That mechanism is **retired and
> must not be re-enabled.** The authoritative do-not-re-enable rule is
> [`bridge-essential.md`](bridge-essential.md) § "Operational Mode". The retired
> poller scripts are archived at `archive/os-poller-2026-04-25/`.

## Why Retired

The OS-poller stack (Windows scheduled tasks `AgentRedFileBridgeIndexScan-*`,
`AgentRedPollerLivenessWatcher`, the foreground watchdog, and the liveness
watchers) polled blindly on a fixed interval regardless of bridge activity and
was halted by owner directive on 2026-04-25. Bridge dispatch is now event-driven
via the cross-harness event-driven trigger
(`scripts/cross_harness_bridge_trigger.py`, registered as PostToolUse + Stop
hooks); manual dispatcher/TAFE bridge-state scans remain the fallback. See
[`bridge-essential.md`](bridge-essential.md) for the canonical operating mode and
the two-axis bridge-automation model.

## The Only Sanctioned Path Back

There is no accepted state that re-enables the retired OS pollers as the active
automation path. A *governed* scheduled-poller restoration, if ever pursued, is
tracked as **WI-4404** and would require a fresh owner directive plus a bridge
proposal; the orchestrator direction in
`DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610` may supersede WI-4404.

## Historical Content

The archived poller scripts and the prior runbook procedures are preserved under
`archive/os-poller-2026-04-25/` for historical reference only. They are not live
dependencies and must not be invoked.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
