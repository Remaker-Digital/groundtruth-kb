# Implementation Proposal REVISED-1 - Benchmark Suite (Self-Diagnostic Leak Closure Slice 2)

bridge_kind: prime_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-002.md` (F1, F2)
Work Item: new MemBase work item to be created from this proposal under existing GOV-18 + GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 governance
target_paths: ["scripts/benchmarks/__init__.py", "scripts/benchmarks/linkage_heatmap.py", "scripts/benchmarks/recall_coverage.py", "scripts/benchmarks/tool_identification.py", "scripts/benchmarks/deliberation_recall.py", "scripts/benchmarks/advisory_latency.py", "scripts/benchmarks/assertion_signal_noise.py", "scripts/benchmarks/cli.py", "scripts/benchmarks/common.py", "platform_tests/scripts/test_benchmark_linkage_heatmap.py", "platform_tests/scripts/test_benchmark_recall_coverage.py", "platform_tests/scripts/test_benchmark_tool_identification.py", "platform_tests/scripts/test_benchmark_deliberation_recall.py", "platform_tests/scripts/test_benchmark_advisory_latency.py", "platform_tests/scripts/test_benchmark_assertion_signal_noise.py", ".claude/skills/gtkb-benchmarks/SKILL.md", ".codex/skills/gtkb-benchmarks/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json", ".gtkb-state/benchmarks/**"]

## Claim

Implement six read-only benchmark scripts that measure GT-KB's behavioral fidelity against existing governance contracts. The suite operates entirely under existing requirements (GOV-18 assertion quality, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DELIB-S312 deterministic services, DELIB-S341 self-improvement standing directive, INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM advisory). No new SPECs are created in this slice; the benchmarks are mechanical measurement plumbing that exposes data the existing governance already authorizes the platform to compute.

The six benchmarks correspond to the S349 probes: Cross-Artifact Linkage Heat Map, Recall Evidence Coverage, Tool Identification, Deliberation Recall Quality, Advisory-to-Action Latency, Assertion Signal/Noise Ratio. Each emits a JSON+markdown report to `.gtkb-state/benchmarks/<run_id>/`. No canonical state is mutated.

## Why Now

Same rationale as -001 §"Why Now": S349 surfaced LEAK 2 (broken structured-graph linkage) and LEAK 3 (assertion drift detection disabled by accumulation). The Codex Self-Measurement advisory designed the architecture; this slice implements the smallest concrete read-only measurement subset.

## Changes from -001 (addressing Codex NO-GO F1, F2)

- **F1 (Requirement Sufficiency contradiction):** Removed seven prerequisite SPEC creations from scope. The benchmarks operate under existing governance and emit advisory-only data. Subsequent slices (2a, 2b, 2c per follow-ons section) may formalize SPECs after baseline data confirms which metrics warrant gating; that future work is a separate bridge thread.
- **F2 (target_paths omits state files):** Removed approval-packet writes (no SPEC creation). Added `.gtkb-state/benchmarks/**` to target_paths for run outputs.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge proposal filed before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing spec; no SPEC creation in this slice.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification carries forward these spec links and maps tests to them.
- GOV-18 ASSERTION-QUALITY - assertion-quality measurement (Benchmark 6) operates under this authority.
- GOV-19 OUTSIDE-IN-TESTING - benchmarks measure surfaces and behaviors, not internals.
- GOV-STANDING-BACKLOG-001 - benchmark output produces candidate WIs under standing-backlog authority; no schema change.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - measurement output is durable artifacts in `.gtkb-state/benchmarks/`.
- ADR-DA-READ-SURFACE-PLACEMENT-001 - benchmark reports are placed on existing read paths.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - benchmarks are artifact-oriented; measurements are durable, reproducible, evidence-cited.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - benchmark surface activates as a downstream consumer of existing artifact lifecycle events.
- DCL-CONCEPT-ON-CONTACT-001 - "benchmark", "linkage heat map", "advisory latency" are new load-bearing concepts; glossary entries added at IP-5 in the gtkb-benchmarks SKILL.md.
- GOV-ARTIFACT-APPROVAL-001 - this slice creates no formal GOV/ADR/DCL/SPEC/PB artifacts and so does not engage the formal-artifact-approval-packet workflow.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - measurement is repetitive plumbing.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities flow to MemBase backlog.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §3 Implemented vs. Intended Surfaces.
- `.claude/rules/peer-solution-advisory-loop.md`.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md` - the LO advisory that designed the architecture this slice implements (Phase 1 Passive Baseline Collector recommendation).

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY (Codex LO advisory, 2026-05-11).
- DELIB-1469 - per Codex F1 evidence in -002 NO-GO; GT-KB Self-Measurement and Self-Improvement Advisory supports passive baseline measurement.
- DELIB-S321-TRIAD-COMPLETENESS - per Codex F1 evidence; relevant to proposed linkage and evidence measurements.
- DELIB-1212 / DELIB-0731 - per Codex F1 evidence; prior `gtkb-phase-a-metrics-collector` bridge history.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION - recent owner authorization pattern.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-002.md - Codex NO-GO at -002; this REVISED-1 addresses F1, F2.

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner asked Prime Builder to investigate GT-KB behavior for leaks/gaps/waste.
- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion, then "parallelize this work to the maximum extent possible" via direct prompt.
- 2026-05-13 UTC, S349: Codex returned NO-GO on -001; this REVISED-1 addresses F1 and F2.

No additional owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

The benchmark suite operates under existing governance:

- `GOV-18` (assertion quality) directly governs assertion-signal-noise measurement.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` authorizes measurement as durable artifact-oriented work.
- `GOV-STANDING-BACKLOG-001` authorizes benchmark output to produce candidate WIs without schema change.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM` provides the architectural blueprint as Loyal Opposition advisory; this slice implements its Phase 1 (Passive Baseline Collector) without creating new formal contracts.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` authorizes mechanical plumbing for repetitive measurement work.

All benchmarks are read-only against existing MemBase tables and bridge files; outputs are non-authoritative measurements in `.gtkb-state/benchmarks/`. No new product behavior is introduced.

## Current Implementation Baseline

Unchanged from -001 §"Current Implementation Baseline".

## Proposed Scope

### IP-1: Implement shared common module

Create `scripts/benchmarks/__init__.py` and `scripts/benchmarks/common.py` with `BenchmarkResult` dataclass, `write_run_outputs()`, `compute_idempotency_key()`.

### IP-2: Implement six benchmark scripts

Each is a standalone Python module with `run(window_start, window_end, project_root) -> BenchmarkResult`:

1. `linkage_heatmap.py` - 5x5 matrix of cross-artifact reference rates.
2. `recall_coverage.py` - per-mutation evidence-of-prior-state-review rate.
3. `tool_identification.py` - skill-attribution-marker presence rate on mutations (queries `changed_by` patterns).
4. `deliberation_recall.py` - samples 50 recent owner-decision deliberations, runs `gt deliberations search`, returns top-3 IDs.
5. `advisory_latency.py` - scans INSIGHTS-*.md ctimes and bridge ADVISORY entries; cross-references against `work_items.related_bridge_threads`.
6. `assertion_signal_noise.py` - queries `assertion_runs` history; classifies failing assertions into four categories per heuristic thresholds.

### IP-3: Implement CLI

`scripts/benchmarks/cli.py` exposes `run`, `report`, `compare` subcommands.

### IP-4: Tests

`platform_tests/scripts/test_benchmark_*.py` per benchmark with 5 tests each (fixture, idempotency, dimensions, empty-data, output-writing) = 30 tests total. Plus CLI smoke tests.

### IP-5: Add gtkb-benchmarks skill

Create `.claude/skills/gtkb-benchmarks/SKILL.md`. Register in capability registry. Run adapter generator. Verify parity.

## Tests

Per -001 §"Tests" plus:

- `test_benchmarks_no_membase_write` - verify no benchmark script writes to MemBase tables (`specifications`, `tests`, `work_items`, `deliberations`); they only read.
- `test_benchmark_output_path_in_gtkb_state` - verify all benchmark output paths fall under `.gtkb-state/benchmarks/`.

## Verification Plan

Per -001 §"Verification Plan" with these adjustments:

- No SPEC creation evidence required (no SPECs created in this slice).
- Verify benchmark output paths fall entirely under `.gtkb-state/benchmarks/`.
- Verify zero MemBase mutations during benchmark runs (post-run row counts unchanged).
- Carry forward applicability and clause preflight outputs from -001 and rerun against -003.

## Risks and Rollback

Per -001 §"Risks and Rollback". Additionally:

- Without formal benchmark SPECs, future threshold-setting work must re-establish authority before promoting any benchmark to a gate; that's a feature, not a bug — it forces explicit decisions about which metrics matter enough to enforce.

## Sequenced Follow-Ons

Per S349 parallelization directive, no longer waiting for any other slice.

Independent follow-ons after Slice 2 VERIFIED:

- Slice 2a: Formal SPEC creation for the benchmark contract (`SPEC-GTKB-BENCHMARK-SUITE-001` + per-benchmark contracts) once baseline data confirms which metrics are stable and worth gating.
- Slice 2b: MemBase event-ledger schema migration (per Codex advisory Phase 2).
- Slice 2c: Dashboard panels for benchmark results.
- Slice 2d: Doctor check that reads latest benchmark run.

## Recommended Commit Type

`feat:` - new functionality (six benchmark scripts, CLI, skill, capability registry entry).

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section (15 blocking + 3 advisory).
- non-empty `## Prior Deliberations` section.
- non-empty `## Owner Decisions / Input` section.
- expanded `target_paths` including `.gtkb-state/benchmarks/**`.
- `## Requirement Sufficiency` subsection with exactly one operative state: "Existing requirements sufficient".
- `## Recommended Commit Type`.
- explicit `Changes from -001` section.
