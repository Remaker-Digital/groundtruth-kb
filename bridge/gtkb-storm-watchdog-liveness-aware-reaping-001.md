NEW

# gtkb-storm-watchdog-liveness-aware-reaping — Slice 1 of WI-4670: make the storm watchdog liveness-aware so it stops killing healthy in-flight workers mid-task

bridge_kind: prime_proposal
Document: gtkb-storm-watchdog-liveness-aware-reaping
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 7ed62043-e9ad-48b9-8e00-0e897085426b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-WI-4828-STORM-WATCHDOG-LIVENESS-001
Project: PROJECT-GTKB-DISPATCHER-COMPLETION
Work Item: WI-4828

target_paths: ["scripts/ops/storm_watchdog_reap.py", "scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_storm_watchdog_reap.py"]

implementation_scope: source + test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This is **slice 1 of the WI-4670 dispatch-storm remediation** — the surgical, low-risk, ADR-neutral fix the owner selected (AUQ 2026-06-25, `DELIB-20266104`). It makes the storm watchdog **liveness-aware** so it stops reaping healthy in-flight workers mid-task.

It does **not** change the dispatch trigger architecture, does not touch `cross_harness_bridge_trigger.py`, and does not perform the daemon cutover. It only makes the *killer* smarter, so it cannot make the storm worse and carries no dispatch-behavior risk.

## Root cause (evidence)

The storm is a re-dispatch loop driven by the watchdog killing healthy workers:

1. **Unit mismatch.** `scripts/ops/harness_storm_watchdog.ps1` force-terminates the entire matched harness process family when **raw OS-process count** exceeds a threshold (`$CODEX_THRESHOLD = 15`, `$NONCODEX_THRESHOLD = 15`). But the concurrency cap (`WI-4472`/CA9165) bounds **logical workers** (~3/role), and **one codex worker spawns ~4 OS processes** (`codex` + `node_repl` + `codex-command-runner` + `codex-windows-sandbox`). So a *within-cap* number of workers blows the 15-process threshold.
2. **Lease-blindness.** The watchdog kills by count with **zero awareness** of the per-document lease registry (`scripts/bridge_lease_registry.py`), which records each holder's `pid` + `acquired_at` + `heartbeat_at` + `ttl_seconds`. It reaps healthy, lease-holding, in-flight workers (exit code `4294967295` = `process_terminated_abruptly`, observed in `dispatch-state.json`).
3. **Loop.** A reaped worker writes no verdict, so the bridge item stays actionable; `process_terminated_abruptly` is not a `FAST_TRIP_FAILURE_CLASSES` member, so the per-recipient breaker is slow to trip; the item is re-dispatched → population climbs back over 15 → watchdog reaps again.

The separation-of-concerns error: **throttling spawns is the concurrency cap's job (WI-4472); corpse/hang reaping is the watchdog's job.** The watchdog was doing throttling-by-kill against the wrong unit, killing healthy workers.

## Design detail (for LO review)

### New: `scripts/ops/storm_watchdog_reap.py` — a pure, unit-testable reap decision

A single pure function (no process I/O, no killing) so the decision logic is fully exercisable under pytest:

```python
def decide_reap(processes, leases, *, now, startup_grace_seconds, max_lifetime_seconds) -> ReapDecision
```

- `processes`: candidate dispatch processes, each `{pid, ppid, name, create_time_epoch}` (gathered by the .ps1 via `Get-CimInstance Win32_Process`).
- `leases`: lease records read from `<dispatch-state-dir>/leases/*.lock` (the `bridge_lease_registry` records; each carries `pid`, `acquired_at`, `heartbeat_at`, `ttl_seconds`).
- Returns `{reap: [pid,...], protect: [pid,...], reasons: {pid: reason}}`.

**Protection tiers** — a process is PROTECTED if ANY holds:
1. `now - create_time < startup_grace_seconds` → `cold_start_grace` (may be mid-startup, pre-lease).
2. its pid is a **fresh** lease holder (`bridge_lease_registry` non-stale) within `max_lifetime_seconds` → `live_lease_holder`.
3. its pid descends (transitively, via `ppid`) from a protected lease-holder pid → `descendant_of_lease_holder` (protects the codex process family of a healthy worker).

**REAPABLE** — none of the above AND one of:
- old + no live lease → `orphan_no_lease` (a true corpse/zombie child of a dead worker).
- lease-holder whose lease age `>= max_lifetime_seconds` → `over_lifetime_straggler` (a genuine hang; backstop behind the `run_with_status.py` worker-lifetime timeout, WI-4806).

Determinism: pure function of `(processes, leases, now, config)` — no clock/random/IO inside `decide_reap`; `now` is injected. Fully pytest-testable.

### Rewire: `scripts/ops/harness_storm_watchdog.ps1` → thin gather/execute shell

The .ps1 keeps its existing conservative process-detection (codex family; registry-declared non-codex harness scripts under the project venv/root; never `claude`; only `node_repl` under the Codex runtime), then:
1. Gathers candidate processes with `pid/ppid/name/create_time`.
2. Resolves the lease records from `<dispatch-state-dir>/leases/`.
3. Invokes the project venv interpreter to run `storm_watchdog_reap.decide_reap`, passing processes + leases as JSON.
4. `Stop-Process -Force` **only** the returned `reap` pids, logging each with its `reason`.

The **raw-count "kill the whole family above 15" path is removed.** Count is logged for observability only. Throttling stays with the concurrency cap; the watchdog reaps only orphans/over-lifetime stragglers — never healthy in-flight workers. The kill-switch remains non-asserted (emergency-only per `WI-4780`/`SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`).

### Config

`startup_grace_seconds` (default 120) and `max_lifetime_seconds` (default aligned to the `run_with_status.py` worker-lifetime timeout, WI-4806) are module constants overridable by env vars, so tuning needs no code change.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture-of-record (persistent daemon owns liveness; this slice makes the interim safety-net liveness-aware without touching the trigger architecture the ADR retires).
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (v2) — centralized dispatch service requirement.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` — kill-switch is emergency-only; this slice keeps the watchdog from auto-asserting it and narrows its kill behavior to genuine corpses/hangs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed via the governed no-index bridge path.
- `GOV-10` (outside-in / exposed-interface testing) — satisfied by extracting the reap decision into a pytest-testable module.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: all governing specs cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project / Work Item / Project Authorization metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4828 (slice of WI-4670) is the governing backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Prior Deliberations

- `DELIB-20266104` — owner authorization for this slice (the surgical watchdog-liveness scope), recorded this session.
- `DELIB-20265882` — 10-branch dispatcher target architecture: the daemon owns throttle/liveness; Branch 10 "stabilize first, then build" sanctions this interim stabilization of the current safety net.
- `DELIB-20265888` — harness/dispatch isolation invariants.
- `DELIB-20265877`, `DELIB-20260612` — congestion is not failure; kill-switch emergency-only; watchdog narrowed (this slice continues that narrowing from raw-count-kill to liveness-aware reaping).
- `DELIB-20266084` — WI-4787 daemon foundation authorization (the landed shadow daemon this remediation track builds toward).
- WI-4670 re-diagnosis (2026-06-25): "external termination of dispatched workers mid-task during a dispatch storm" is the dominant cause; "(1) systemic = dispatcher owning throttle/liveness so workers are not killed mid-task."

## Owner Decisions / Input

Owner made three AskUserQuestion selections in this session (2026-06-25), captured as `DELIB-20266104`:
1. Session focus = **Dispatcher reliability**.
2. Next step = **Design the WI-4670 storm fix**.
3. Design scope = **Surgical watchdog-liveness fix** (slice 1), chosen over broader daemon-liveness-ownership, a phased-umbrella proposal, or a controlled-dispatch-test-first.

No further owner decision is required for this shadow-of-risk slice (the watchdog only narrows its own kill behavior). The daemon cutover and the broader throttle/liveness ownership remain separately surfaced because they change runtime dispatch behavior.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-DISPATCHER-ARCHITECTURE-001` + `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` + `DELIB-20265882` (daemon owns liveness) + the WI-4670 evidence fully constrain this slice. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

All tests run with the repo venv interpreter:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_storm_watchdog_reap.py -q
```

### Spec-to-Test Mapping

| Governing clause | Test | Expected |
|---|---|---|
| Healthy in-flight lease-holder is never reaped | `test_live_lease_holder_protected` | a pid with a fresh lease within max-lifetime → in `protect`, reason `live_lease_holder` |
| Codex family of a healthy worker is protected | `test_descendants_of_lease_holder_protected` | child pids whose `ppid` chain reaches a protected lease pid → protected, reason `descendant_of_lease_holder` |
| Cold-start (pre-lease) worker protected | `test_cold_start_grace_protects_recent_process` | a process younger than `startup_grace_seconds` with no lease → protected, reason `cold_start_grace` |
| True orphan is reaped | `test_orphan_without_lease_reaped` | an old process with no live lease and no protected ancestor → in `reap`, reason `orphan_no_lease` |
| Over-lifetime hang is reaped | `test_over_lifetime_lease_holder_reaped` | a lease-holder whose lease age ≥ `max_lifetime_seconds` → reaped, reason `over_lifetime_straggler` |
| No raw-count kill of healthy workers | `test_many_healthy_workers_none_reaped` | N within-lifetime lease-holders + families, count far over the old 15 threshold → `reap` is empty |
| Determinism | `test_decide_reap_is_pure_for_fixed_inputs` | identical `(processes, leases, now, config)` → identical decision across repeated calls |
| Stale lease is not protective | `test_stale_lease_not_protective` | a lease past its ttl (stale) does not protect its pid; old + stale → reaped |

Code-quality gates on changed Python: `ruff check` + `ruff format --check`. The `.ps1` rewire is validated by inspection + a smoke invocation that confirms it calls the decider and reaps only returned pids (PowerShell behavior is exercised via the decider's pytest coverage, per GOV-10 the decision logic is the exposed testable interface).

## Backlog Conflict / Future Work Review

This is a **single-work-item** proposal (WI-4828), **not a bulk backlog operation** — no bulk-ops owner-approval packet is required (`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is satisfied by the adjacent-WI **inventory** below, which serves as this proposal's backlog **review-packet** evidence). Per the standing backlog-conflict rule, adjacent open watchdog WIs were inventoried (both have **0 active bridge threads**):
- **WI-4818** (storm-watchdog does not account for the Cursor harness — `cursor_harness.py` drift): complementary. The new reap module is **registry-driven** (it consumes lease records + a process list, not a hard-coded harness list), so Cursor workers that hold leases are protected automatically; WI-4818's watched-harness-list extension folds in naturally on top of this slice.
- **WI-4804** (watchdog dormancy + stale kill-switch never auto-clears): orthogonal (dormancy/heartbeat concern); not addressed here, not regressed.

No duplication or interference. The pre-existing uncommitted +3-line delta in `platform_tests/scripts/test_harness_storm_watchdog.py` is left untouched (this slice adds a new `test_storm_watchdog_reap.py` rather than editing the existing test).

## Risk / Rollback

Risk surface is **strictly narrowing**: the watchdog moves from "kill the whole family above a raw-count threshold" to "reap only genuine orphans/over-lifetime stragglers." It cannot kill more than before; it kills strictly fewer (only true corpses/hangs). It performs no dispatch and changes no trigger behavior, so it cannot reintroduce or worsen the storm.

- **Failure mode if the decider errors or the venv is unreachable:** the .ps1 must fail **safe** — reap nothing and log the error (never fall back to the old raw-count kill). This is the conservative default and is asserted by the .ps1 rewire.
- **Rollback:** revert the commit; the watchdog returns to its prior behavior. No state migration; the lease registry and concurrency cap are unchanged.

## Recommended Commit Type

`fix` — this repairs broken behavior (the watchdog killing healthy in-flight workers). The reaping capability pre-exists; the new `storm_watchdog_reap.py` module is an internal extraction-for-testability of the corrected decision, not a new external capability surface. (If LO prefers `feat` on the grounds of the net-new module, that is acceptable; the change is declared and justified here per the Conventional Commits discipline.)

## Bridge Filing

Filed under `bridge/` as the next status-bearing numbered file (`bridge/gtkb-storm-watchdog-liveness-aware-reaping-001.md`); append-only; dispatcher/TAFE state plus versioned numbered bridge files are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
