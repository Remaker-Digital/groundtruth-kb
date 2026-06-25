NEW

# gtkb-dispatcher-daemon-foundation — Phase 2: persistent dispatcher daemon foundation (shadow mode) + control CLI + independent external heartbeat

bridge_kind: prime_proposal
Document: gtkb-dispatcher-daemon-foundation
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 262d9f16-eb78-4e1f-89d9-1a024611652a
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-WI-4787-DAEMON-FOUNDATION-001
Project: PROJECT-GTKB-DISPATCHER-COMPLETION
Work Item: WI-4787

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/gtkb_dispatcher_heartbeat.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_heartbeat.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Phase 2 of `PROJECT-GTKB-DISPATCHER-COMPLETION` stands up the persistent dispatcher daemon foundation mandated by `ADR-DISPATCHER-ARCHITECTURE-001` (VERIFIED). It delivers three new surfaces and **does not cut dispatch over** from the transitional `cross_harness_bridge_trigger` (the ADR explicitly states the trigger remains until daemon phases land):

1. **Daemon process** (`scripts/gtkb_dispatcher_daemon.py`) — a persistent always-on loop that owns the dispatch *decision* and its own health/liveness state. It runs in **shadow mode**: each tick it reads dispatcher/TAFE bridge state, computes the per-role actionable dispatch decision **reusing the existing signature + kind-aware-routing logic** (no divergent reimplementation), and records what it *would* dispatch to a decision log — **without spawning any worker**. Real spawning stays with the transitional trigger until a later cutover slice. This proves the daemon's decision-ownership against live state with zero runtime/dispatch risk.
2. **Control CLI** (`gt bridge dispatch daemon start | stop | status`) — the daemon's control surface: start/stop the daemon process and report status (running, last-tick age, shadow-decision summary, health).
3. **Independent external heartbeat** (`scripts/gtkb_dispatcher_heartbeat.py`) — a *separate* watchdog process the daemon **cannot suppress**, registered as its own scheduled task distinct from the daemon. It checks the daemon's heartbeat freshness and records a stale/dead alert when the daemon stops writing — the S290–S292 silent-failure lesson (the liveness indicator must be independent of the thing it monitors).

**Why shadow mode is the correct foundation:** cutting real dispatch to the daemon while the trigger is still live would double-dispatch and risk a fresh storm. Shadow mode satisfies WI-4787's "owns dispatch decisions" by exercising the full decision path against live state, while the proven-safe transitional trigger continues real dispatch. Cutover (daemon spawns, trigger disabled) is the next slice, separately proposed and reviewed.

## Design detail (for LO review)

- **Decision reuse, not reimplementation.** The daemon imports the existing actionable-signature computation and kind-aware routing (`groundtruth_kb.bridge.notify.compute_actionable_pending` + the dispatch-eligibility resolution used by `scripts/cross_harness_bridge_trigger.py`) so the shadow decision is byte-comparable to what the trigger would do. The decision log records `(role, signature, would-dispatch recipient, timestamp)`.
- **Heartbeat contract.** Daemon writes `.gtkb-state/dispatcher-daemon/heartbeat.txt` (UTC ISO timestamp) every tick. The independent heartbeat watchdog reads it on its own schedule and, if the timestamp is older than a configurable staleness window (default 180s, mirroring `_HEARTBEAT_STALE_SECONDS`), appends a `daemon_stale` alert to `.gtkb-state/dispatcher-daemon/heartbeat-alerts.jsonl`. The watchdog is a **distinct** scheduled task (`GTKB-DispatcherDaemonHeartbeat`) so the daemon dying cannot silence its own death alert.
- **Process management.** Daemon launched/stopped via the control CLI; persistence via a Windows scheduled task (`GTKB-DispatcherDaemon`) per the `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` platform-binding precedent. Single-instance lock at `.gtkb-state/dispatcher-daemon/daemon.lock`.
- **No retired-poller revival.** This is the sanctioned persistent-daemon replacement per the ADR; it is NOT the retired OS-poller class (`bridge-essential.md` § Operational Mode). The daemon is event/state-driven (acts on actionable-signature change), not a blind fixed-interval expensive spawn; in shadow mode it spawns nothing at all.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — the architecture-of-record this daemon implements (persistent always-on daemon owning queue/dispatch/health + independent heartbeat).
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (v2) — the centralized dispatch service requirement the daemon realizes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed via the no-index bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project / Work Item / Project Authorization metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4787 is the governing backlog item.
- `GOV-RELIABILITY-FAST-LANE-001` (context) — NOT used; this is planned project work, not a fast-lane defect.

## Prior Deliberations

- `DELIB-20265882` — 10-branch dispatcher target architecture; Branch decisions for the persistent daemon and the independent heartbeat (who-watches-the-watcher) are the source of this foundation.
- `DELIB-20265888` — 8 harness/dispatch isolation invariants; the daemon is the GT-KB-owned control plane that removes harnesses from dispatch triggering.
- `DELIB-20266084` — owner authorization for WI-4787 Phase-2 implementation (this work).
- The S290–S292 / OS-poller-retirement history (`bridge-essential.md` Incident History) motivates the independent heartbeat and the no-blind-spawn discipline; this daemon does not revive that retired class.

## Owner Decisions / Input

- Owner directed **"Phase 2 (daemon foundation) please"** (2026-06-25), recorded as `DELIB-20266084` (the formal WI-4787 implementation authorization).
- `ADR-DISPATCHER-ARCHITECTURE-001` (VERIFIED) + `DELIB-20265882` supply the architecture; no further owner decision is required for this shadow-mode foundation. The dispatch cutover (next slice) will be surfaced separately because it changes runtime dispatch behavior.

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` + `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` v2 + `DELIB-20265882` fully constrain the daemon foundation. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

### Spec-to-Test Mapping

All tests run with the repo venv interpreter (`groundtruth-kb/.venv/Scripts/python.exe -m pytest <paths> -q`):

| Governing clause | Test | Expected |
|---|---|---|
| ADR: daemon owns the dispatch decision | `test_daemon_tick_computes_shadow_decision` | a tick reads fixture bridge state and records a `(role, signature, would-dispatch)` decision-log entry matching the existing trigger's computation |
| ADR: shadow mode spawns nothing | `test_daemon_shadow_mode_never_spawns` | over N ticks against actionable state, zero worker subprocesses launched (spawn function patched + asserted uncalled) |
| ADR: daemon writes liveness heartbeat | `test_daemon_writes_heartbeat_each_tick` | heartbeat file timestamp advances per tick |
| WI-4787: independent heartbeat detects death | `test_heartbeat_watchdog_flags_stale_daemon` | given a heartbeat older than the staleness window, the watchdog records a `daemon_stale` alert; given a fresh one, no alert |
| WI-4787: heartbeat is independent | `test_heartbeat_watchdog_runs_without_daemon_process` | watchdog evaluates staleness purely from the heartbeat file, with no dependency on the daemon process being importable/alive |
| WI-4787: control CLI | `test_daemon_control_cli_status_reports_state` | `daemon status` reports running/stopped + last-tick age from state files |
| Single-instance | `test_daemon_single_instance_lock` | a second daemon start while locked refuses to run |

Code-quality gates on changed files: `ruff check` + `ruff format --check` on the four/five target paths.

## Risk / Rollback

Risk surface is entirely additive: new daemon + heartbeat scripts + a `daemon` CLI subgroup + tests. **No runtime dispatch behavior changes** — the daemon spawns nothing (shadow mode) and the transitional trigger is untouched, so this cannot reintroduce the storm. The independent heartbeat only writes alert records (no enforcement). Rollback: stop + unregister the two scheduled tasks and revert the commit; nothing else depends on the daemon until the cutover slice. The daemon's single-instance lock prevents multiple instances.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file (`bridge/gtkb-dispatcher-daemon-foundation-001.md`); no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the versioned numbered bridge files are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` — adds new daemon, heartbeat watchdog, and control-CLI capability surfaces (no behavior change to existing dispatch).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
