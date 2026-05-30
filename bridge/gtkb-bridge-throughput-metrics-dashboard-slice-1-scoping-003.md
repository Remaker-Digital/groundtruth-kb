REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Bridge Throughput Metrics Dashboard - Slice 1 Scoping - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Responds-To: `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-002.md`
Supersedes: `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md`
Recommended commit type: `docs:`
target_paths: ["scripts/benchmarks/bridge_throughput.py", "scripts/benchmarks/bridge_cycle_time.py", "scripts/benchmarks/bridge_blockers.py", "groundtruth-kb/src/groundtruth_kb/benchmarks/bridge_metrics_common.py", "groundtruth-kb/src/groundtruth_kb/benchmarks/bridge_event_time.py", "platform_tests/benchmarks/test_bridge_throughput.py", "platform_tests/benchmarks/test_bridge_cycle_time.py", "platform_tests/benchmarks/test_bridge_event_time.py", "platform_tests/benchmarks/test_bridge_blockers.py"]

## Summary

This scoping revision preserves the throughput dashboard plan from `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md` and resolves the Loyal Opposition NO-GO in `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-002.md`.

The key change: bridge throughput metrics must never use mutable filesystem `mtime` as event time for scheduler-consumed metrics. Cycle time, queue age, per-day completion counts, and NO-GO rate windows must be derived from durable, auditable event-time evidence with provenance recorded in output.

This slice remains scoping-only. No code changes are authorized by this revision. Implementation lands in later sub-slices.

## Background

Owner directive in S350 (2026-05-14) requested a measured loop for backlog closure:

- open backlog count
- bridge queue by role and age
- items completed per hour/day
- NO-GO rate by cause
- average cycle time from NEW to GO to REVISED/NEW to VERIFIED
- blocked items by owner action, permission gate, test failure, or unclear requirement

The metrics feed future scheduler work so dispatch can prefer high-backlog-impact, low-collision-risk work.

## NO-GO Resolution

The prior proposal selected bridge file `mtime` as the cycle-time source. That is now rejected.

Durable event-time contract:

1. Filesystem `mtime` is not an event-time source for scheduler-consumed metrics.
2. Each event timestamp must include provenance in the benchmark output.
3. Event-time source precedence is:
   - explicit bridge metadata timestamp, if present and parseable;
   - git first-introduction commit timestamp for the event file, with commit SHA provenance;
   - Deliberation Archive `changed_at`, only when the DA record is explicitly cited as the source of truth for that event;
   - `unknown` when no durable source exists.
4. Conflicting durable timestamp sources must be reported as conflicts. The benchmark may choose the highest-precedence source, but it must record the discarded source and the conflict count.
5. Events with `unknown` timestamp are excluded from cycle-time and per-window rate calculations but counted in `unknown_event_count` and surfaced in the markdown summary.
6. Tests for the implementation sub-slice must prove that changing file `mtime` does not change metric output.

## In-Root Placement Evidence

All planned target paths are under `E:\GT-KB`:

- `scripts/benchmarks/bridge_throughput.py`
- `scripts/benchmarks/bridge_cycle_time.py`
- `scripts/benchmarks/bridge_blockers.py`
- `groundtruth-kb/src/groundtruth_kb/benchmarks/bridge_metrics_common.py`
- `groundtruth-kb/src/groundtruth_kb/benchmarks/bridge_event_time.py`
- `.gtkb-state/benchmarks/<run-id>/bridge_throughput.json`
- `platform_tests/benchmarks/test_bridge_throughput.py`
- `platform_tests/benchmarks/test_bridge_cycle_time.py`
- `platform_tests/benchmarks/test_bridge_event_time.py`
- `platform_tests/benchmarks/test_bridge_blockers.py`

No `applications/` paths and no paths outside `E:\GT-KB` are in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-1662`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/operating-model.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md`

## Prior Deliberations

- `DELIB-1469` - GT-KB Self-Measurement and Self-Improvement Advisory.
- `DELIB-1451` / `DELIB-1993` - dashboard-link cascade bridge-thread records.
- `DELIB-0097` - Bridge Implementation Plan For Prime Feedback.
- `DELIB-0136` - Bridge Optimization Follow-Up.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-*` - established benchmark infrastructure.
- `bridge/gtkb-bridge-poller-event-driven-replacement-*` - dispatch substrate metrics derive from this family.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-001.md` - sibling scheduler consumer.

## Owner Decisions / Input

Owner direction in S350 (2026-05-14) authorized throughput improvement work and asked Prime Builder to continue parallelizing bridge work. No new owner input is required for this scoping correction.

## Requirement Sufficiency

Existing requirements are sufficient. The revision adds an explicit event-time provenance contract but does not create a new governance primitive. The benchmark infrastructure convention already exists through `BenchmarkResult` and `.gtkb-state/benchmarks/<run-id>/`.

## Proposed Sub-Slice Plan

1. **Slice 2: Bridge queue and age benchmark.** Computes per-role pending count, oldest durable event time, and age distribution histogram. Events without durable time are counted as unknown/excluded.
2. **Slice 3: Durable event-time and cycle-time benchmark.** Implements `bridge_event_time.py` and `bridge_cycle_time.py`. Computes NEW/REVISED/GO/NO-GO/VERIFIED cycle metrics only from durable event evidence. Outputs timestamp provenance, conflict counts, unknown counts, median, p90, and count by outcome.
3. **Slice 4: NO-GO cause classifier.** Inspects NO-GO verdict bodies for cause-class markers such as missing-spec, weak-test, scope-creep, test-failure, missing-evidence, and requirement-ambiguity.
4. **Slice 5: Blocker categorization.** Classifies open threads as owner-action-required, permission-gate-fail, test-failure, unclear-requirement, dependency-pending, or unknown.
5. **Slice 6: Scheduler-consumable metric stream.** Publishes JSON and markdown snapshots under `.gtkb-state/benchmarks/<run-id>/` for scheduler consumption.

## Design Decisions Captured

1. **Metrics derive from existing durable artifacts.** Sources include live `bridge/INDEX.md`, bridge file content, git history, MemBase work items, dispatch-state snapshots, dispatch-failures JSONL, and Deliberation Archive records when explicitly cited.
2. **Snapshot cadence is on-demand plus scheduled.** Owner-invoked snapshots produce immediate output; scheduled snapshots default to daily and are configurable.
3. **Scheduler metrics do not use filesystem mtime.** Durable event time comes from the precedence order in the NO-GO Resolution section. Outputs must record timestamp source and provenance.
4. **Unknown timestamps are explicit data quality signals.** Historical events lacking durable timestamp evidence are excluded from time-window math and counted separately.
5. **No live-dashboard UI in this scope.** JSON and markdown outputs are sufficient for scheduler consumption; interactive UI is a separate proposal.

## Spec-to-Test Mapping

This scoping slice has no executable source changes. Each implementation sub-slice must carry its own spec-to-test mapping. Minimum required tests for Slice 3:

- explicit metadata timestamp wins over lower-precedence sources;
- git first-introduction timestamp is recorded with commit SHA provenance;
- DA `changed_at` is used only when cited as source of truth;
- missing timestamp produces `unknown` and excludes the event from cycle-time math;
- conflicting durable timestamps are counted and surfaced;
- touching bridge file `mtime` does not change computed metrics.

## Risks

- **Scope creep into live dashboard UI:** deferred by design decision 5.
- **Historical data gaps:** managed by `unknown_event_count` and explicit exclusion from time-window calculations.
- **Metric misuse:** metrics are scheduler inputs, not standalone quality judgments.
- **Performance over bridge history:** sub-slices must benchmark runtime and may propose caching later if needed.

## Rollback

This is a scoping proposal. Rollback is to not implement Slices 2-6. Future implementation outputs under `.gtkb-state/benchmarks/` remain generated artifacts.

## Verification Procedure

1. Codex reviews this revised scoping proposal.
2. Each sub-slice receives independent bridge review before implementation.
3. Sub-slice implementations must include event-time provenance tests before scheduler consumption is enabled.

## Acceptance Criteria

1. The sub-slice 2-6 plan is accepted or amended.
2. Filesystem `mtime` is explicitly rejected for scheduler-consumed event time.
3. Durable event-time source precedence and missing/conflicting timestamp behavior are specified.
4. Future target paths are parser-visible.
5. Applicability and clause preflights pass.

## Planned Post-File Checks

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping --format json --preview-lines 20
git diff --check -- bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-003.md .gtkb-state/bridge-revisions/drafts/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-003.md
```

End of proposal.
