# Implementation Proposal REVISED-2 - Benchmark Suite (Self-Diagnostic Leak Closure Slice 2)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-004.md` (F1 + non-blocking SPEC-1662 citation)
Work Item: new MemBase work item to be created from this proposal under existing SPEC-1662 (GOV-18: Assertion Quality Standard) + GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 governance
target_paths: ["scripts/benchmarks/__init__.py", "scripts/benchmarks/linkage_heatmap.py", "scripts/benchmarks/recall_coverage.py", "scripts/benchmarks/tool_identification.py", "scripts/benchmarks/deliberation_recall.py", "scripts/benchmarks/advisory_latency.py", "scripts/benchmarks/assertion_signal_noise.py", "scripts/benchmarks/cli.py", "scripts/benchmarks/common.py", "platform_tests/scripts/test_benchmark_linkage_heatmap.py", "platform_tests/scripts/test_benchmark_recall_coverage.py", "platform_tests/scripts/test_benchmark_tool_identification.py", "platform_tests/scripts/test_benchmark_deliberation_recall.py", "platform_tests/scripts/test_benchmark_advisory_latency.py", "platform_tests/scripts/test_benchmark_assertion_signal_noise.py", ".claude/skills/gtkb-benchmarks/SKILL.md", ".codex/skills/gtkb-benchmarks/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json", ".claude/rules/canonical-terminology.md", ".gtkb-state/benchmarks/**", ".groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-benchmark-terms.json"]

## Claim

Implement six read-only benchmark scripts that measure GT-KB's behavioral fidelity against existing governance contracts. The suite operates under existing requirements (SPEC-1662 GOV-18: Assertion Quality Standard, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DELIB-S312, DELIB-S341, INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM advisory). No new SPECs are created in this slice; the benchmarks are mechanical measurement plumbing.

Six benchmarks: Cross-Artifact Linkage Heat Map, Recall Evidence Coverage, Tool Identification, Deliberation Recall Quality, Advisory-to-Action Latency, Assertion Signal/Noise Ratio. Each emits a JSON+markdown report to `.gtkb-state/benchmarks/<run_id>/`. No canonical state mutation other than the IP-6 canonical glossary additions required by `DCL-CONCEPT-ON-CONTACT-001`.

## Why Now

Same rationale as -001 and -003.

## Changes from -003 (addressing Codex NO-GO F1 + non-blocking note)

- **F1 (concept-on-contact routed to wrong surface):** Added `.claude/rules/canonical-terminology.md` to target_paths because the proposal introduces "benchmark", "linkage heat map", "advisory latency", and "metric snapshot" as new load-bearing platform concepts. Added `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-benchmark-terms.json` to target_paths. Added IP-6 to draft glossary entries plus approval packet. Verification plan extended.
- **Non-blocking note (machine-retrievable spec citation):** Updated citation from shorthand `GOV-18` to retrievable `SPEC-1662 (GOV-18: Assertion Quality Standard)` throughout the proposal. The shorthand `GOV-18` is preserved alongside for human readability.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge proposal filed before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing spec; no new SPEC creation in this slice.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification carries forward these spec links.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - directly governs assertion-signal-noise measurement (Benchmark 6).
- GOV-19 OUTSIDE-IN-TESTING - benchmarks measure surfaces and behaviors.
- GOV-STANDING-BACKLOG-001 - benchmark output produces candidate WIs under standing-backlog authority.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - measurement output is durable artifacts.
- ADR-DA-READ-SURFACE-PLACEMENT-001 - benchmark reports placed on existing read paths.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - benchmarks are artifact-oriented.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - benchmark surface activates as downstream consumer of artifact lifecycle events.
- DCL-CONCEPT-ON-CONTACT-001 - "benchmark", "linkage heat map", "advisory latency", "metric snapshot" are new load-bearing concepts; IP-6 places glossary entries in `.claude/rules/canonical-terminology.md` per the DCL's canonical surface.
- GOV-ARTIFACT-APPROVAL-001 - this slice does NOT create formal GOV/ADR/DCL/SPEC/PB artifacts but DOES edit a protected narrative artifact (canonical-terminology.md), which requires the per-artifact approval packet at IP-6.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §3.
- `.claude/rules/peer-solution-advisory-loop.md`.
- `.claude/rules/canonical-terminology.md` - canonical glossary surface, target of IP-6.
- `config/governance/narrative-artifact-approval.toml` - protected-path config.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md`.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY (Codex LO advisory, 2026-05-11).
- DELIB-1469 - GT-KB Self-Measurement and Self-Improvement Advisory.
- DELIB-S321-TRIAD-COMPLETENESS.
- DELIB-1212 and DELIB-0731 - prior gtkb-phase-a-metrics-collector bridge history.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-1512 and DELIB-1513 - per Codex F1 evidence in -004 NO-GO; prior review history around DCL-CONCEPT-ON-CONTACT-001 and canonical glossary promotion.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-002.md - Codex NO-GO at -002 (F1, F2 addressed in -003).
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-004.md - Codex NO-GO at -004 (F1 addressed in this -005).

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion, then "parallelize this work to the maximum extent possible" via direct prompt.
- 2026-05-13 UTC, S349: Codex returned NO-GO twice on this slice (-002, -004); this REVISED-2 addresses the latest finding.

No additional owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

Same justification as -003 with updated citation to SPEC-1662 (GOV-18: Assertion Quality Standard) for machine retrievability. The IP-6 glossary edits are concept-on-contact compliance work mandated by `DCL-CONCEPT-ON-CONTACT-001`.

## Current Implementation Baseline

Unchanged from -003. Additionally:

- `.claude/rules/canonical-terminology.md` does not currently contain entries for "benchmark", "linkage heat map", "advisory latency", or "metric snapshot". IP-6 adds the entries.
- canonical-terminology.md is a protected narrative artifact; edits require a formal-artifact approval packet.

## Proposed Scope

### IP-1: Implement shared common module

Same as -003 IP-1.

### IP-2: Implement six benchmark scripts

Same as -003 IP-2.

### IP-3: Implement CLI

Same as -003 IP-3.

### IP-4: Tests

Same as -003 IP-4.

### IP-5: Add gtkb-benchmarks skill

Same as -003 IP-5, with the clarification that the skill file describes how to RUN benchmarks; canonical vocabulary placement is IP-6 (not the skill).

### IP-6: Add canonical glossary entries for benchmark-suite concepts

1. Draft canonical-terminology.md entries for four concepts. Format follows existing entries:

   - `benchmark` - a read-only deterministic measurement procedure that emits a `BenchmarkResult` (JSON+markdown) to `.gtkb-state/benchmarks/<run_id>/`. Source: S349; INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM. Implementation pointer: `scripts/benchmarks/`. Not to be confused with: test (verification artifact); assertion (machine-verifiable check).

   - `linkage heat map` - a 5x5 matrix benchmark output where each cell is the percentage of source-artifact rows referencing at least one target-artifact row. Source: S349 self-diagnostic. Implementation pointer: `scripts/benchmarks/linkage_heatmap.py`.

   - `advisory latency` - the time interval between an LO advisory's filing and the first Prime acknowledgement (WI created, bridge thread opened, or explicit deferral). Source: S349 self-diagnostic. Implementation pointer: `scripts/benchmarks/advisory_latency.py`.

   - `metric snapshot` - a timestamped computed value with provenance fields (run_id, metric_id, window_start, window_end, value, dimensions, source_commit, generated_at) per the GT-KB Effectiveness Observatory architecture in INSIGHTS-2026-05-10-13-26. Stored in `.gtkb-state/benchmarks/<run_id>/`. Not to be confused with: metric definition (the registry entry describing what the metric measures).

2. Create `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-benchmark-terms.json` with required fields, listing all four entries in `full_content` with a single combined `full_content_sha256`.

3. Edit `.claude/rules/canonical-terminology.md` to insert the four entries under "## GT-KB DA Read-Surface and Operational Vocabulary".

4. Verify the narrative-artifact-approval-gate hook accepts the Edit.

## Tests

Per -003 §"Tests" plus:

- `test_canonical_glossary_contains_benchmark_entries` - regression test that grep finds each of the four canonical glossary entries.

## Verification Plan

Per -003 with these additions:

- Verify all four canonical glossary entries exist with source citations.
- Verify the formal-artifact approval packet exists and validates.
- Verify the narrative-artifact-approval-gate hook permitted the Edit.
- Verify all SPEC citations resolve in MemBase (specifically SPEC-1662).
- Carry forward applicability and clause preflight outputs from -003.

## Risks and Rollback

Per -003 with these additions:

- Four glossary entries can be removed in a single edit if rollback is required.

## Sequenced Follow-Ons

Per S349 parallelization directive.

Independent follow-ons after Slice 2 VERIFIED:

- Slice 2a: Formal SPEC creation once baseline data confirms metric stability.
- Slice 2b: MemBase event-ledger schema migration.
- Slice 2c: Dashboard panels.
- Slice 2d: Doctor check.

## Recommended Commit Type

`feat:` - new functionality plus canonical-terminology.md additions bundled per `DCL-CONCEPT-ON-CONTACT-001`.

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section.
- non-empty `## Prior Deliberations` section.
- non-empty `## Owner Decisions / Input` section.
- expanded `target_paths` including `.claude/rules/canonical-terminology.md` and the named approval-packet path.
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type`.
- explicit `Changes from -003` section.
- SPEC-1662 cited for machine retrievability.
