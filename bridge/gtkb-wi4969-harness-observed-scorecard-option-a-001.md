NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; role=Prime Builder; sandbox=danger-full-access; approval=never
author_metadata_source: codex-interactive

# Implementation Proposal - Phase 3 gap 07: harness quality benchmark integration

bridge_kind: prime_proposal
Document: gtkb-wi4969-harness-observed-scorecard-option-a
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4969-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4969

target_paths: ["scripts/benchmarks/harness_observed_scorecard.py", "scripts/benchmarks/cli.py", "platform_tests/scripts/test_benchmark_harness_observed_scorecard.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-4969 Option A: observed advisory harness scorecard from existing dispatcher evidence

Work item description: Connect Phase 3 transcript/equivalence findings to the harness testing and quality benchmark project so model/harness differences are measured repeatedly instead of as a one-off audit. The child must identify existing benchmark artifacts and define integration points before implementation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4969` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/benchmarks/harness_observed_scorecard.py`, `scripts/benchmarks/cli.py`, `platform_tests/scripts/test_benchmark_harness_observed_scorecard.py`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202665137` - Loyal Opposition Verdict — Umbrella Proposal: Session/Activity Envelope Sharding Program
- `DELIB-202665120` - Verdict: VERIFIED
- `DELIB-202665277` - WI-4958 Exact Target Amendment - Verification Verdict
- `DELIB-202665282` - gtkb-headless-dispatch-model-pinning — Implementation Verification (WI-4964)
- `DELIB-202665150` - NO-GO: WI-4944 -- Blocker confirmed; scope boundary prevents VERIFIED; owner decision required

## Owner Decisions / Input

- `DELIB-202665197` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4969-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4969`.

## Proposed Scope

- Add a read-only benchmark module that derives advisory per-harness reliability, responsiveness, and interim quality-proxy scorecards from existing bridge dispatcher logs and bridge status chains.
- Register the benchmark with the existing scripts.benchmarks CLI so it can run as a normal BenchmarkResult-producing benchmark.
- Use the 2026-07-03 benchmarking advisory and WI-4972 classification as input evidence while keeping the output advisory-only.
- Exclude real token capture, tokenizer-accurate cost accounting, live adjudication, same-model A/B dispatch runners, OpenTelemetry/dashboard integration, dispatcher ranking feedback, rules.toml changes, harness eligibility changes, and hidden .codex helper writes.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify scorecard groups by harness identity/model metadata without changing durable role assignments or claiming behavioral parity. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify outputs are advisory artifacts and preserve source evidence links to WI-4969, WI-4972, and INSIGHTS-2026-07-03-18-32. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest coverage plus CLI smoke for the new benchmark. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Verify the benchmark reads dispatcher daemon evidence as observation only and never launches, suppresses, or reranks dispatch. |

## Acceptance Criteria

- python -m scripts.benchmarks.cli run --benchmark harness_observed_scorecard emits JSON and markdown under .gtkb-state/benchmarks without mutating MemBase, bridge state, dispatcher ranking, or harness eligibility.
- The benchmark handles missing dispatcher logs gracefully and records advisory dimensions by harness, including failure-class counts, launch/result counts, latency summaries when diagnostic data exists, and bridge outcome/status proxy counts.
- Tests cover parsing dispatch-state, dispatch-failures JSONL, dispatch-diagnostic-post JSONL, bridge status chains, missing-log behavior, and CLI registration.
- The implementation report ties the slice to OPS consolidation, dispatcher daemon architecture, lifecycle-first/scoring-last precedence, and WI-4972 duplicate-work controls.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/benchmarks/harness_observed_scorecard.py`
- `scripts/benchmarks/cli.py`
- `platform_tests/scripts/test_benchmark_harness_observed_scorecard.py`

## Recommended Commit Type

`feat`
