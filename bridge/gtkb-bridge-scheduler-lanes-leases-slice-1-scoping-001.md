# Implementation Proposal — Bridge Scheduler with Lanes and Leases (Slice 1: Scoping)

bridge_kind: prime_implementation_proposal

## Summary

Scoping proposal for replacing the current fixed-cap dispatch policy (`DEFAULT_MAX_ITEMS = 2` in `scripts/cross_harness_bridge_trigger.py:92` and a parallel cap in `scripts/single_harness_bridge_dispatcher.py:72`) with a lease-based work scheduler that supports per-role concurrency limits, per-document leases, a serialized `bridge/INDEX.md` writer, work-lane classification, and aging+priority weighting.

This slice scopes the design only. No code changes here. Implementation lands in subsequent slices each filed under this thread family.

## Background

Owner directive in S350 (2026-05-14) under the 6-point throughput improvement plan, points 2 and 3:

> "Replace 'cap of 2' with a real worker scheduler... per-role concurrency limits, for example LO review workers 2-4, Prime implementation workers 1-3; per-document leases so two workers never write verdicts for the same thread; one serialized bridge/INDEX.md writer, or an atomic compare-and-swap index update; aging and priority weighting so old items do not starve behind fresh bridge noise."

> "Split work into lanes... Review lane: LO proposal/verification analysis can run in parallel, but final verdict writes must serialize. Implementation lane: Prime can run multiple workers only when target paths and MemBase mutations are disjoint. Verification lane: tests, ruff, bridge preflights, credential scans, and drift checks can run aggressively in parallel. Governance lane: formal artifact mutations, owner-decision-sensitive work, and MemBase writes stay serialized unless the operation is explicitly batch-safe."

Live signal supports the need: dispatch-state at S350 shows `pending_count: 17` for prime-builder and `pending_count: 10` for loyal-opposition with `selected_count: 2` — 27 pending items being serviced 2 at a time. The fixed cap is the visible bottleneck.

## In-Root Placement Evidence

All target paths and runtime artifacts for the eventual sub-slices in-root under `E:\GT-KB`:

- `E:\GT-KB\scripts\cross_harness_bridge_trigger.py` — scheduler entry point.
- `E:\GT-KB\scripts\single_harness_bridge_dispatcher.py` — single-harness dispatcher (parallel substrate; same scheduler should apply).
- `E:\GT-KB\.gtkb-state\bridge-poller\leases\` — new per-document lease registry directory (in-root, created by the lease sub-slice).
- `E:\GT-KB\platform_tests\scripts\test_bridge_scheduler_*.py` — new test files per sub-slice.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical workflow state; the serialized-writer sub-slice preserves this invariant under concurrency.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each sub-slice will carry its own spec-to-test mapping; this scoping slice does not implement.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — dispatched prompts must continue to emit the canonical init keyword first line; the scheduler must not alter dispatch prompt content.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — keyword authority preserved across scheduling.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 — supersede authority; auto-trigger contract must continue to fire on actionable signature change.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 — auto-trigger contract preserved.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the scheduler must work in both multi-harness and single-harness topologies.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — coexistence with the single-harness substrate.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — desktop-task wake substrate preserved.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — lease + lane records are durable artifacts (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability preserved (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lease lifecycle: acquired → held → released (advisory).
- `.claude/rules/bridge-essential.md` — bridge dispatch enablement contract; this slice extends the substrate.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants honored.
- `.claude/rules/codex-review-gate.md` — review gate.

## Prior Deliberations

- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` GO at `-004` — established the event-driven trigger substrate this scheduler builds on.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*` — Slice 4 retired interval polling; this scheduler is event-driven by inheritance.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-013.md` Codex GO at `-014` — single-harness dispatcher substrate.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` VERIFIED — suppression contract this scheduler must respect.
- Sibling thread `gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md` — addresses the suppression-throughput gap directly; this scheduler subsumes that scope when it lands.

## Owner Decisions / Input

Owner directive in S350 (2026-05-14): "I would improve throughput in this order... 2. Replace 'cap of 2' with a real worker scheduler... 3. Split work into lanes."

Owner provided explicit per-role concurrency hints: "LO review workers 2-4, Prime implementation workers 1-3."

Owner directive in S350 (2026-05-14): "Please continue to parallelize work" — explicit authorization to file this scoping proposal in parallel with the worker-delivery slice queue. Per `feedback_fix_problems_without_auq`, scoping is execute-able under standing owner direction; no further AUQ needed at this proposal level.

## Requirement Sufficiency

Existing requirements sufficient. The scheduler operates within the existing bridge dispatch contract (`ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2, `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2, `GOV-FILE-BRIDGE-AUTHORITY-001`). No new behavior contract is introduced; the scheduler is a smarter substrate within those contracts.

## target_paths

Scoping slice; no code mutations. Target paths declared here for traceability to the sub-slices that will follow:

- `scripts/cross_harness_bridge_trigger.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `.gtkb-state/bridge-poller/leases/` (new)
- `platform_tests/scripts/test_bridge_scheduler_*.py` (new test files)

## Proposed Sub-Slice Plan

1. **Slice 2: Per-document lease registry.** Atomic lease acquisition/release for `bridge/INDEX.md` document entries. Lease file path `.gtkb-state/bridge-poller/leases/<doc-slug>.lock` with PID + timestamp + expected-action metadata. Two workers cannot hold the same lease simultaneously.
2. **Slice 3: Serialized INDEX writer.** Wrap `bridge/INDEX.md` mutations in a process-level lock or use compare-and-swap on the entire file. Tests: concurrent worker writes do not corrupt INDEX.
3. **Slice 4: Per-role concurrency limits.** Replace `DEFAULT_MAX_ITEMS = 2` with `GTKB_DISPATCH_CONCURRENCY` env or config (default: LO=3, Prime=2 per owner hints). Scheduler tracks in-flight worker count per role.
4. **Slice 5: Lane classification.** Classify each bridge entry into one of: review / implementation / verification / governance. Lane determines concurrency profile (verification = aggressive parallel; governance = serialized).
5. **Slice 6: Aging and priority weighting.** Item age (NEW/REVISED filed timestamp) and a priority field (extracted from proposal metadata or owner directive) feed into the dispatch selector so old items don't starve.

## Implementation Plan (this scoping slice)

No implementation. This slice's deliverable is the sub-slice plan above plus the design decisions below.

### Design Decisions Captured

1. **Lease granularity = per-document, not per-version.** Reasoning: a worker processes a single bridge thread end-to-end (read latest version, write next version); the document slug is the natural lock scope.
2. **Lease TTL = process-bound + sanity-bound.** A lease is released on worker exit OR after `GTKB_LEASE_SANITY_TTL_SECONDS` (default 300) elapses without heartbeat, whichever is sooner.
3. **INDEX serialization = file lock, not in-memory queue.** Reasoning: must work across subprocesses; in-memory queue is process-bound.
4. **Lane assignment = derived from `bridge_kind` header + content classification, not configured per-thread.** Reasoning: lane is a property of the work, not the thread; classification logic lives in the scheduler.
5. **Aging weight = monotonic increasing as a function of (now - filed_at).** Concrete function deferred to Slice 6 proposal.

## Spec-to-Test Mapping

This scoping slice has no executable tests. Each sub-slice will carry its own spec-to-test mapping. Mapping placeholders for the eventual sub-slices:

- `GOV-FILE-BRIDGE-AUTHORITY-001` → Slice 3 (serialized INDEX writer tests).
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` + `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` → Slices 2-6 each assert prompt content unchanged.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 → Slice 4 tests confirm dispatch still fires on actionable signature change.

## Risks

- **Scope creep across 5 sub-slices**: each sub-slice could grow unbounded. *Mitigation:* this scoping slice fixes the sub-slice boundaries; expansion requires a new proposal.
- **Lease corruption under abnormal worker termination**: stale leases block work. *Mitigation:* Slice 2 includes the sanity TTL.
- **INDEX serialization adds latency to worker writes**: workers wait for the lock. *Mitigation:* INDEX writes are infrequent and small; lock-hold time is sub-millisecond. Slice 3 will measure empirically.

## Rollback

No code changes in this scoping slice. Each sub-slice has its own rollback plan.

## Verification Procedure

1. Codex review of this scoping proposal yields GO (sub-slice plan approved) or NO-GO (revise scoping).
2. Each sub-slice (2-6) is independently reviewed and verified after this slice's GO.

## Acceptance Criteria

- Sub-slice 2-6 plan is approved as the implementation sequence for items 2 and 3 of the owner's S350 throughput plan.
- Design decisions captured above are accepted or amended in Codex review.
- All preflights pass for this proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
