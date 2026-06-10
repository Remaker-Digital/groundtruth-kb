# Implementation Proposal — Bridge Throughput Metrics Dashboard (Slice 1: Scoping)

bridge_kind: prime_proposal

## Summary

Scoping proposal for a daily/continuous throughput report measuring: open backlog count, bridge queue by role and age, items completed per hour/day, NO-GO rate by cause, average cycle time (NEW → GO → REVISED → VERIFIED), and blocked-item count by category (owner action, permission gate, test failure, unclear requirement). The metrics feed the scheduler (per owner's S350 throughput plan point 2) so dispatch chooses work by highest backlog impact and lowest collision risk.

This slice scopes the metrics surface only. Implementation lands in sub-slices.

## Background

Owner directive in S350 (2026-05-14) under the 6-point throughput improvement plan, point 6:

> "Turn backlog closure into a measured loop. Current MemBase status counts show the real scale: 126 open, 1 in_progress, 1 new, 1 deferred, plus older non-action statuses like wont_fix and not_a_defect. Bridge currently has active pressure too: 11 LO-actionable and 19 Prime-actionable in the last live scan. Add a daily/continuous throughput report... Then let the scheduler choose work based on highest backlog impact and lowest collision risk."

Live signal supports the need: dispatch-state at S350 shows 17 pending Prime, 10 pending LO with 2-at-a-time service rate. No measured cycle-time data exists; without measurement, the scheduler design (sibling thread) cannot tune correctly.

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\scripts\benchmarks\bridge_throughput.py` (new) — metrics computation.
- `E:\GT-KB\scripts\benchmarks\bridge_cycle_time.py` (new) — cycle-time benchmark.
- `E:\GT-KB\.gtkb-state\benchmarks\<run-id>\bridge_throughput.json` (new) — run output.
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\benchmarks\common.py` — existing `BenchmarkResult` dataclass reused per the established benchmark pattern.
- `E:\GT-KB\platform_tests\benchmarks\test_bridge_throughput_*.py` (new) — regression tests.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge as the canonical workflow state; metrics derive from it without modifying it.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — sub-slice spec-to-test mapping deferred.
- `SPEC-1662` (GOV-18) — assertion quality standard; metrics are observability, not enforcement.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — metric snapshots are durable governance artifacts (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability preserved (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — metric snapshot lifecycle: computed → stored → consumed (advisory).
- `.claude/rules/bridge-essential.md` — bridge dispatch enablement; metrics inform the scheduler.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants honored.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md` Codex GO at `-010` — established the `BenchmarkResult` + `.gtkb-state/benchmarks/` convention this proposal reuses.

## Prior Deliberations

- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-*` — established the benchmark infrastructure this proposal extends.
- `bridge/gtkb-bridge-poller-event-driven-replacement-*` — dispatch substrate metrics derive from.
- Sibling thread `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-001.md` — the scheduler is the primary consumer of these metrics.

## Owner Decisions / Input

Owner directive in S350 (2026-05-14): "I would improve throughput in this order... 6. Turn backlog closure into a measured loop."

Owner provided explicit metric list: "open backlog count, bridge queue by role and age, items completed per hour/day, NO-GO rate by cause, average cycle time from NEW -> GO -> NEW -> VERIFIED, blocked items by owner action, permission gate, test failure, or unclear requirement."

Owner directive in S350 (2026-05-14): "Please continue to parallelize work."

## Requirement Sufficiency

Existing requirements sufficient. The benchmark infrastructure pattern is established (`groundtruth_kb.benchmarks.common.BenchmarkResult` + `.gtkb-state/benchmarks/<run_id>/`). This proposal extends with new metric modules.

## target_paths

Scoping slice; no code mutations.

Target paths declared for sub-slice traceability:

- `scripts/benchmarks/bridge_throughput.py`
- `scripts/benchmarks/bridge_cycle_time.py`
- `scripts/benchmarks/bridge_blockers.py`
- `groundtruth-kb/src/groundtruth_kb/benchmarks/bridge_metrics_common.py`
- `platform_tests/benchmarks/test_bridge_*.py`

## Proposed Sub-Slice Plan

1. **Slice 2: Bridge queue + age benchmark.** Computes per-role pending count, oldest filed_at, age distribution histogram. Output: JSON + markdown summary.
2. **Slice 3: Cycle-time benchmark.** Parses bridge file headers (NEW filed_at, GO filed_at, REVISED filed_at, VERIFIED filed_at) to compute per-thread cycle time. Aggregates: median, p90, count by outcome.
3. **Slice 4: NO-GO cause classifier.** Inspects NO-GO verdict bodies for cause-class markers (missing-spec, weak-test, scope-creep, test-failure, missing-evidence). Aggregates: rate per cause per week.
4. **Slice 5: Blocker categorization.** For each open thread, classify the blocker: owner-action-required, permission-gate-fail, test-failure, unclear-requirement, dependency-pending. Output: blocker dashboard.
5. **Slice 6: Scheduler-consumable metric stream.** Slice 1 (sibling scheduler thread) consumes these metrics. Slice 6 here closes the loop: scheduler reads recent metrics to inform dispatch choice.

## Implementation Plan (this scoping slice)

No implementation. This slice's deliverable is the sub-slice plan + design decisions below.

### Design Decisions Captured

1. **Metrics derive from existing artifacts; no new state required.** Sources: `bridge/INDEX.md`, bridge file headers, MemBase work_items, dispatch-state.json, dispatch-failures.jsonl.
2. **Snapshot cadence = on-demand + scheduled.** Owner-invoked snapshots produce immediate output; a scheduled snapshot (configurable interval, default daily) produces durable trend data.
3. **Cycle-time uses bridge file mtime, not git commit time.** Reasoning: file mtime reflects when the verdict was filed locally; git commit can lag.
4. **No live-dashboard surface in this scope.** Scoping covers JSON+markdown outputs that an external Grafana / similar can consume; dashboard UI is a separate concern.

## Spec-to-Test Mapping

This scoping slice has no executable tests. Each sub-slice will carry its own spec-to-test mapping.

## Risks

- **Scope creep into "live dashboard"**: visible metrics invite "make it interactive." *Mitigation:* design decision 4 explicitly defers dashboard UI to a separate effort.
- **Benchmark performance on large bridge histories**: cycle-time over ~200 bridge threads could be slow. *Mitigation:* sub-slices benchmark themselves; if slow, add caching or incremental computation in a follow-on.
- **Metrics misleading without context**: a high NO-GO rate could mean good review hygiene OR poor proposal quality. *Mitigation:* metrics are inputs to scheduler, not direct quality measures; pair with owner judgment.

## Rollback

Scoping slice; rollback is "do not implement Slices 2-6."

## Verification Procedure

1. Codex review of this scoping proposal yields GO or NO-GO.
2. Each sub-slice (2-6) independently reviewed.

## Acceptance Criteria

- Sub-slice 2-6 plan approved.
- Design decisions accepted or amended in review.
- All preflights pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
