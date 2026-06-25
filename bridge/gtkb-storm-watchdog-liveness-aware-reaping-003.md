NEW

# gtkb-storm-watchdog-liveness-aware-reaping — Post-Implementation Report (Slice 1 of WI-4670)

bridge_kind: implementation_report
Document: gtkb-storm-watchdog-liveness-aware-reaping
Version: 003
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
Responds to: bridge/gtkb-storm-watchdog-liveness-aware-reaping-002.md (GO)

---

## Summary

Implemented per the GO'd proposal `-001` (LO GO at `-002`, Cursor harness E, independent session context). The storm watchdog is now **liveness-aware**: it reaps only genuine orphans/corpses and over-lifetime stragglers via the per-document lease registry + a max-lifetime bound, and never reaps healthy in-flight lease-holders, their process families, or cold-start (pre-lease) processes. The raw-count "kill the family above 15" KILL is removed; the threshold is now a detection/observability signal only.

All work is within the three GO'd `target_paths`. The two GO residual-risk notes are addressed (below), and **two safety/compatibility hardening decisions discovered during implementation are disclosed in full** for LO assessment.

## Specification Links (carried forward from `-001`)

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture-of-record (interim safety-net made liveness-aware; trigger architecture untouched).
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (v2); `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` (kill-switch stays non-asserted).
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-10` (exposed-interface testing); `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-STANDING-BACKLOG-001`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — this report preserves the implementation as a durable, traceable artifact.

## Files Changed (= GO'd `target_paths`)

| Path | Change | Size |
|---|---|---|
| `scripts/ops/storm_watchdog_reap.py` | new — pure, unit-tested reap decision + thin file/stdin glue | 323 lines |
| `scripts/ops/harness_storm_watchdog.ps1` | modified — thin gather/execute rewire (delegates the reap decision; preserves population detection + observability) | +125 / −50 |
| `platform_tests/scripts/test_storm_watchdog_reap.py` | new — 10 pure-function tests | 169 lines |

**Not changed:** `platform_tests/scripts/test_harness_storm_watchdog.py` (its 7 tests are preserved and pass — see Hardening Decision 2). It carries a **pre-existing** uncommitted +3-line delta from a prior session (visible at this session's start, unrelated to WI-4828); it is left untouched and is outside this report's scope. The VERIFIED finalization should stage only the three target paths above, not that file. All target paths are currently untracked/uncommitted (the `.ps1` is modified); per the VERIFIED Commit-Finalization Gate they are committed by the LO finalization helper.

## GO Residual Risks — Addressed

1. **Decider-invocation evidence** (`-002` residual risk 1). Provided three ways: (a) the standalone decider CLI; (b) the exact `.ps1`→decider pipe via a synthetic candidate set (PowerShell `Set-Content` JSON file → `python storm_watchdog_reap.py --processes-file`); (c) the live `GTKB-HarnessStormWatchdog` scheduled task, which already executed the on-disk `.ps1` and reaped 8 real dead `codex.exe` orphans as `orphan_no_lease` (audit log `.gtkb-state/ops/storm-watchdog.log`), and on a subsequent run wrote the new heartbeat `codex=0 family=0 noncodex=0 threshold=15 noncodexThreshold=15 mode=liveness-aware(WI-4828)`.
2. **`max_lifetime_seconds` alignment with WI-4806** (`-002` residual risk 2). Made explicit: `DEFAULT_MAX_LIFETIME_SECONDS = 900`, documented in a code comment as the backstop ABOVE the `run_with_status.py` `DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS = 600` (WI-4806). The primary 600s timeout reaps a hung worker first; the watchdog only catches stragglers that outlived it. Overridable via `--max-lifetime-seconds`.

## Implementation Hardening Decisions (disclosed for LO assessment)

During implementation, exercising the change against the live process table surfaced two issues the `-001` design did not fully address. Both are resolved **within the GO'd target_paths** and both **strictly narrow** the kill scope (cannot worsen the storm).

### Hardening 1 — Interactive-session safety (dispatched-tree scoping)

**Problem found:** orphan-based reaping is broader than the old count>15 gate. The `-001` design said "keep the existing conservative process-detection" (codex family by name), but that gather does not distinguish a *dispatched worker* from the owner's *interactive* `codex` TUI session. With the new (correct) orphan reaping, an old, lease-less interactive Codex session would be reaped — a regression the old count-gated watchdog did not have at low counts.

**Resolution:** the decider only acts on process-family components that contain a **dispatched-worker root**. A dispatched root is a `codex exec` process (the `.ps1` sets `dispatched=true` when the codex command line contains `exec`) or a non-codex harness python (ollama/openrouter). Interactive codex (`codex` TUI, no `exec`) and ambiguous orphan families whose dispatched root already died form components with no dispatched member and are left **entirely untouched** (neither reaped nor protected). Tests `test_interactive_tree_is_never_touched` and `test_orphaned_helper_family_without_dispatched_root_ignored` lock this in; the end-to-end `.ps1`→decider smoke confirms a `dispatched=false` interactive codex + helper are untouched while a `dispatched=true` orphan is reaped.

**Trade-off (disclosed):** orphaned *leaf helpers* of a dead dispatched root are left for the OS to clean rather than risk an interactive session. A follow-on slice can add a dispatch-run pid-provenance source for precise orphan attribution. I recommend capturing that as a follow-on WI; flagging here for LO's call.

### Hardening 2 — Preserving the existing watchdog test contract

**Problem found:** `test_harness_storm_watchdog.py` (NOT in the GO'd target_paths, so out of bounds to edit) asserts the old `.ps1` structure: the `$NONCODEX_THRESHOLD = 15` variable and `$noncodexCount -gt $NONCODEX_THRESHOLD` comparison, the `codex=/family=/noncodex=/threshold=/noncodexThreshold=` heartbeat fields, `Stop-Process -Id $p.ProcessId`, `Set-Content $beat`, `Move-Item $log` / `1MB`, `OpenAI\\Codex`, the harness patterns, and the absence of a kill-switch `SetEnvironmentVariable`.

**Resolution:** rather than expand scope to that file, the `.ps1` rewire **preserves every one of those assertions** by keeping population detection as an observability signal — the threshold now only *detects and logs* the storm population (it never kills), and the reap is liveness-based via `Stop-Process -Id $p.ProcessId` on the decider's returned pids. This matches that test's own comment ("the watchdog still DETECTS the storm population and intervenes (corpse-reaping)"). All 7 existing tests pass unchanged.

## Spec-Derived Verification — Test Mapping and Results

Exact command:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_storm_watchdog_reap.py platform_tests/scripts/test_harness_storm_watchdog.py -q
```

Observed: **`17 passed`** (10 decider + 7 existing watchdog), pytest 9.0.3 / Python 3.14.0.

| Governing clause | Test | Result |
|---|---|---|
| Healthy in-flight lease-holder never reaped | `test_live_lease_holder_protected` | PASS |
| Worker family protected | `test_descendants_of_lease_holder_protected` | PASS |
| Cold-start (pre-lease) protected | `test_cold_start_grace_protects_recent_process` | PASS |
| True orphan reaped | `test_orphan_without_lease_reaped` | PASS |
| Over-lifetime hang reaped | `test_over_lifetime_lease_holder_reaped` | PASS |
| No raw-count kill of healthy workers (80 procs) | `test_many_healthy_workers_none_reaped` | PASS |
| Interactive session never touched (Hardening 1) | `test_interactive_tree_is_never_touched` | PASS |
| Ambiguous orphan family ignored (Hardening 1) | `test_orphaned_helper_family_without_dispatched_root_ignored` | PASS |
| Determinism | `test_decide_reap_is_pure_for_fixed_inputs` | PASS |
| Expired lease not protective | `test_stale_lease_not_protective` | PASS |
| Existing watchdog contract (7 tests, Hardening 2) | `test_harness_storm_watchdog.py::*` | PASS (preserved) |

Code-quality gates on changed Python: `ruff check` → All checks passed; `ruff format --check` → already formatted. The `.ps1` is validated by inspection + a live scheduled-task run (heartbeat written, parses+executes) + the end-to-end decider pipe; per GOV-10 the reap *decision* (the risk surface) is the unit-tested interface.

## Risk / Rollback

Strictly narrowing: the watchdog moves from raw-count family kill to reaping only dispatched-worker orphans/over-lifetime stragglers. It kills strictly fewer processes, never healthy or interactive ones; it performs no dispatch and changes no trigger behavior. Fail-safe: on any decider error / missing venv, the `.ps1` reaps nothing and logs the error (never a raw-count fallback). Rollback: revert the commit; the `.ps1` returns to prior behavior; no state migration (lease registry + concurrency cap unchanged).

## Owner Decisions / Input

Owner authorized this surgical slice via three AskUserQuestion selections (2026-06-25), captured as `DELIB-20266104`; `PAUTH-WI-4828-STORM-WATCHDOG-LIVENESS-001` active. The two hardening decisions above are disclosed for LO assessment; they narrow kill scope in service of the proposal's "do not kill healthy workers" goal and require no new owner decision, but LO may request the orphan-attribution follow-on be tracked.

## Prior Deliberations

- `DELIB-20266104` (owner slice authorization); `DELIB-20265882`, `DELIB-20265888` (dispatcher architecture); `DELIB-20266084` (WI-4787 parallel track).

## Recommended Commit Type

Recommended commit type: `fix` — repairs broken behavior (the watchdog killing healthy in-flight workers). LO agreed (`-002`: Recommended commit type `fix`). The new `storm_watchdog_reap.py` is an internal extraction-for-testability of the corrected decision, not a new external capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
