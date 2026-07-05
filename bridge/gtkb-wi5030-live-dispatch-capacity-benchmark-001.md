NEW
author_identity: Codex Prime Builder A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop Prime Builder; interactive build envelope; approval_policy=never

# Implementation Proposal - Add a live dispatch capacity/load benchmark to empirically determine safe concurrency-cap ceilings (global / per-role / max_items)

bridge_kind: prime_proposal
Document: gtkb-wi5030-live-dispatch-capacity-benchmark
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5030-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5030

target_paths: ["scripts/benchmarks/live_dispatch_capacity_benchmark.py", "platform_tests/scripts/test_live_dispatch_capacity_benchmark.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add a dispatch capacity/load benchmark that measures safe concurrency ceilings for global caps, per-role caps, and max_items using deterministic local workers by default and explicit live-run guardrails for expensive provider-backed runs.

Work item description: Gap surfaced by owner question 2026-07-05 (how high can the dispatcher caps go before failure/degradation). The question is currently unanswerable empirically: existing tooling does not load-test live dispatch. scripts/ops/dispatch_chaos_harness.py is a deterministic STUB (does not start the daemon, invoke harnesses, or spend provider calls); scripts/benchmarks/benchmark_dispatch_envelope.py is synthetic input data (does not invoke workers). Need a real capacity/load test that drives live (or faithfully simulated) concurrent dispatch and measures the binding constraints in order: (1) provider rate-limit/cost (shared API keys, N-times TPM/RPM and burn); (2) git .git/index.lock contention at commit/finalization time (documented as a process-count problem causing finalization deadlocks); (3) groundtruth.db SQLite write serialization (WAL: concurrent readers ok, writers serialize; stock 5s busy timeout); (4) machine RAM/CPU (each worker is a process tree, ~1.6 OS procs per logical worker per storm-watchdog heartbeat codex=9 family=15); (5) hung-worker behavior (openrouter LO workers observed hanging 44-60min, holding slots to the 1800s TTL). Deliverable: measured max-before-degradation per cap so 8/3/4 can be raised on evidence rather than inference. Consideration-only; not implementation approval.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5030` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/benchmarks/live_dispatch_capacity_benchmark.py`, `platform_tests/scripts/test_live_dispatch_capacity_benchmark.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-20260705-WI5029-5031-IMPLEMENT-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5030-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5030`.

## Proposed Scope

- Create a live-dispatch-capacity benchmark harness that can sweep global cap, per-role cap, and max_items values and report throughput, saturation, failure classes, and max-before-degradation.
- Default to deterministic local/simulated worker mode so CI and routine verification do not spend provider calls; require explicit opt-in flags for provider-backed live dispatch.
- Measure or expose the binding constraints called out by the WI: provider/rate-limit risk, git index-lock/finalization contention, MemBase SQLite write serialization, host CPU/RAM pressure, and hung-worker slot retention.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run the new live dispatch capacity benchmark unit tests and any targeted dispatcher tests needed to prove benchmark inputs map to dispatcher-owned cap settings. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Verify benchmark defaults use deterministic STUB/local workers and preserve daemon-owned dispatch architecture; real harness load requires explicit opt-in. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Verify the benchmark performs cheap deterministic measurement by default and gates expensive provider-backed dispatch behind explicit flags. |

## Acceptance Criteria

- Benchmark emits JSON with tested cap values, observed throughput/saturation, binding constraint classification, and recommended safe ceiling.
- Default verification path is deterministic and does not launch real harness/provider workers.
- Provider-backed/live mode is visibly gated and cannot run accidentally from tests or CI.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/benchmarks/live_dispatch_capacity_benchmark.py`
- `platform_tests/scripts/test_live_dispatch_capacity_benchmark.py`

## Recommended Commit Type

`feat`
