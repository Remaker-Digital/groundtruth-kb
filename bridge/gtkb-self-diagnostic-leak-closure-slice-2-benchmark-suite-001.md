# Implementation Proposal - Benchmark Suite (Self-Diagnostic Leak Closure Slice 2)

bridge_kind: prime_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Work Item: new MemBase work item to be created from this proposal's IP-1 SPEC creation; current proposal scope is Slice 2 of the GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE umbrella
target_paths: ["scripts/benchmarks/__init__.py", "scripts/benchmarks/linkage_heatmap.py", "scripts/benchmarks/recall_coverage.py", "scripts/benchmarks/tool_identification.py", "scripts/benchmarks/deliberation_recall.py", "scripts/benchmarks/advisory_latency.py", "scripts/benchmarks/assertion_signal_noise.py", "scripts/benchmarks/cli.py", "scripts/benchmarks/common.py", "platform_tests/scripts/test_benchmark_linkage_heatmap.py", "platform_tests/scripts/test_benchmark_recall_coverage.py", "platform_tests/scripts/test_benchmark_tool_identification.py", "platform_tests/scripts/test_benchmark_deliberation_recall.py", "platform_tests/scripts/test_benchmark_advisory_latency.py", "platform_tests/scripts/test_benchmark_assertion_signal_noise.py", "groundtruth.db", ".claude/skills/gtkb-benchmarks/SKILL.md", ".codex/skills/gtkb-benchmarks/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json"]

## Claim

Implement six read-only benchmark scripts that measure GT-KB's behavioral fidelity to its own governance contracts. Each benchmark operates on existing MemBase tables and bridge files, emits a JSON+markdown report, and writes nothing to canonical state. The suite is the smallest action that establishes baseline measurement coverage for the leaks identified in S349 self-diagnostic investigation.

The six benchmarks correspond to the six probes Mike named plus the cross-artifact heat map he asked me to design:

1. Cross-Artifact Linkage Heat Map - 5x5 matrix of reference density between spec/test/WI/delib/bridge.
2. Recall Evidence Coverage - per-mutation evidence-of-prior-state-review rate.
3. Tool Identification - skill-attribution-marker presence on mutations.
4. Deliberation Recall Quality - precision@k for `gt deliberations search` against sampled owner decisions.
5. Advisory-to-Action Latency - time from LO advisory filing to Prime acknowledgement/routing.
6. Assertion Signal/Noise Ratio - categorization of failing assertions by drift/noise/flaky/healthy.

The suite is advisory-only in this slice. No hooks block writes, no gates enforce metrics, no automated remediation runs. This is the Phase 1 passive baseline collector recommended by Codex's `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM` advisory.

## Why Now

S349 self-diagnostic surfaced LEAK 2 (broken structured-graph linkage), LEAK 3 (assertion drift detection silently disabled), and the fact that GT-KB has no observed-behavior measurement layer. The Codex Self-Measurement advisory designed the architecture; this slice implements the smallest concrete subset of that architecture that produces actionable data.

The benchmarks are portable to adopter applications by construction: they operate on standardized MemBase tables and bridge files that every GT-KB-managed application has. Establishing the suite on the GT-KB platform itself is the prerequisite for the meta-claim "GT-KB can self-diagnose and self-improve" to extend to applications.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - live `bridge/INDEX.md` remains the authoritative bridge queue; this proposal files governed work before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths are inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites relevant existing governing specs and names new specs to be created at IP-1 before code semantics depend on them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification requires tests derived from linked specs.
- GOV-STANDING-BACKLOG-001 - benchmark output flows to the standing backlog as candidate work items, not authoritative directives.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - measurement outputs are durable artifacts, not transient session state.
- ADR-DA-READ-SURFACE-PLACEMENT-001 - benchmark reports are placed on paths the system already traverses (dashboard, doctor); placement-over-coercion.
- GOV-18 ASSERTION-QUALITY - meaningfulness over coverage; the assertion signal-noise benchmark operationalizes this principle.
- GOV-ARTIFACT-APPROVAL-001 - SPECs proposed at IP-1 follow the standard formal-artifact-approval-packet workflow.
- DCL-CONCEPT-ON-CONTACT-001 - "benchmark", "metric snapshot", "linkage heat map" are new load-bearing concepts; glossary entries added at IP-1.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - measurement is repetitive plumbing; belongs in services not sessions.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities flow to MemBase backlog; benchmark output produces candidate WIs.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §3 Implemented vs. Intended Surfaces - benchmark reports must distinguish implemented from intended.
- `.claude/rules/peer-solution-advisory-loop.md` - five-state disposition vocabulary applies to benchmark-surfaced findings.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md` - the LO advisory that designed the architecture this slice implements.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC) - Mike asked Prime to probe agent behavior for leaks/gaps/waste; investigation produced quantitative evidence (1.7% WI->spec linkage, 87.3% deliberation orphan rate, 86.7% assertion failure rate, 16,077 dispatch failures); Mike authorized "File both, sequenced" via AskUserQuestion; Mike then authorized "parallelize this work to the maximum extent possible" in a follow-on prompt.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex Loyal Opposition advisory, 2026-05-10) - designed the GT-KB Effectiveness Observatory architecture; this slice implements Phase 1 (Passive Baseline Collector) of that roadmap.
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY (Codex Loyal Opposition advisory, 2026-05-11) - companion advisory for LO-side hygiene orchestration; this slice provides the measurement data the hygiene skill would consume.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - repetitive plumbing belongs in services; measurement is repetitive plumbing.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities flow to MemBase backlog; benchmark outputs are candidate WIs.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION - project-scoped owner authorization pattern; S349 AUQ is the parent authorization for this slice.
- DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS - placement-over-coercion principle; benchmarks are placed on existing read paths (dashboard, doctor) rather than introducing new behaviors.
- DELIB-0860 (gtkb-da-harvest-coverage-implementation VERIFIED) - prior harvest infrastructure provides patterns this slice reuses for deliberation analysis.
- DELIB-1476 (Loyal Opposition NO-GO on prior DA Harvest Catch-Up) - prior NO-GO that informs evidence discipline for harvest-adjacent work.

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner asked Prime Builder to investigate GT-KB behavior for leaks/gaps/waste; investigation produced quantitative findings.
- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion (Slice 1 advisory-router + Slice 2 benchmark suite + Slice 3 assertion S/N triage).
- 2026-05-13 UTC, S349: owner authorized "parallelize this work to the maximum extent possible" via direct prompt, lifting the prior sequencing constraint for Slices 2 and 3.

The AUQ in S349 plus the parallelization directive together constitute owner authorization for this slice. No additional owner decision is required before review. SPEC creation at IP-1 runs through the standard formal-artifact-approval-packet workflow per `GOV-ARTIFACT-APPROVAL-001`.

## Requirement Sufficiency

Existing requirements sufficient.

The Codex Self-Measurement advisory establishes the architecture; existing governance (GOV-18 assertion quality, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DELIB-S341 standing directive) authorizes measurement work as platform self-improvement. One umbrella SPEC plus six per-benchmark SPECs are created at IP-1 to formalize the measurement contract. No new product behavior; this is platform self-instrumentation.

## Current Implementation Baseline

- MemBase has `specifications`, `tests`, `work_items`, `deliberations`, `documents` tables with append-only versioning. S349 measurements (1.7% WI->spec, 80.4% test->spec, 87.3% delib orphan) were computed directly via `db.py` queries.
- Bridge files are append-only markdown under `bridge/`; `bridge/INDEX.md` is canonical workflow state.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` contains LO advisory reports with SPEC/WI ID headers per `.claude/rules/deliberation-protocol.md`.
- `groundtruth-kb/src/groundtruth_kb/db.py` already implements lifecycle metrics (lines 4083-4330 per Codex advisory citation): revision rounds, spec-to-implemented duration, defect injection/resolution, regression rate, verified-with-tests, stale tests, implemented-without-test count. The benchmark suite reuses these existing primitives.
- `scripts/deliberation_health.py` already implements thresholded metrics for DA population, linkage, conflict quarantine, redaction, duplicates.
- `groundtruth-kb/src/groundtruth_kb/operating_state.py:229-247` counts bridge threads by status but does not compute cycle times.
- No current code computes a cross-artifact linkage heat map, recall coverage, tool-identification attribution, deliberation recall precision@k, advisory-to-action latency, or assertion signal/noise categorization.

## Proposed New Specs

IP-1 creates these MemBase records:

1. SPEC-GTKB-BENCHMARK-SUITE-001 - umbrella spec defining the benchmark contract (read-only execution, standardized output format under `.gtkb-state/benchmarks/<run_id>/`, no canonical state mutation, dimensions: harness, role, application/platform, time window).
2. SPEC-BENCHMARK-LINKAGE-HEATMAP-001 - 5x5 matrix; cell = percentage of source rows referencing at least one target row of the column type; thresholds per edge owner-configurable; flag cells below threshold as drift candidates.
3. SPEC-BENCHMARK-RECALL-COVERAGE-001 - per-mutation evidence-of-prior-state-review rate; measured at `work_items`/`specifications`/`deliberations` insert and bridge proposal write.
4. SPEC-BENCHMARK-TOOL-IDENTIFICATION-001 - percentage of mutations attributable to encoded skill versus manual/improvisation; measurement source is `changed_by` attribution.
5. SPEC-BENCHMARK-DELIBERATION-RECALL-001 - precision@1 and precision@3 and MRR for `gt deliberations search` against sampled owner-decision queries; sample size 50; rubric-graded.
6. SPEC-BENCHMARK-ADVISORY-LATENCY-001 - time from advisory filing (`INSIGHTS-*.md` ctime or bridge ADVISORY entry timestamp) to first Prime acknowledgement (WI created with related path or bridge thread opened referencing advisory).
7. SPEC-BENCHMARK-ASSERTION-SIGNAL-NOISE-001 - categorizes failing assertions as genuine_drift (PASS history >5, newly FAIL) / chronic_noise (FAIL history >50 consecutive) / flaky (PASS/FAIL alternating in 10-run window) / healthy (otherwise).

All seven SPECs are mechanically checkable; each carries `assertions` field with concrete pass/fail predicates.

## Proposed Scope

### IP-1: Create SPECs with formal-artifact-approval packets

1. For each of the 7 SPECs above, create `.groundtruth/formal-artifact-approvals/2026-05-13-<SPEC-ID>.json` with required fields.
2. Insert SPECs via `db.insert_specification()`, citing packet path in `change_reason` and S349 AUQ as `presented_to_user` evidence.

### IP-2: Implement shared common module

1. Create `scripts/benchmarks/__init__.py` and `scripts/benchmarks/common.py` with:
   - `BenchmarkResult` dataclass (run_id, benchmark_id, window_start, window_end, value, dimensions, source_commit, source_query, generated_at).
   - `write_run_outputs(run_id, results)` writes JSON + markdown to `.gtkb-state/benchmarks/<run_id>/`.
   - `compute_idempotency_key(benchmark_id, window_start, window_end, source_commit)` for run-deduplication.

### IP-3: Implement six benchmark scripts

Each script is a standalone Python module with `run(window_start, window_end, project_root) -> BenchmarkResult`:

1. `linkage_heatmap.py` - executes 25 queries (5x5 matrix), returns matrix as dimensions; flags below-threshold cells.
2. `recall_coverage.py` - queries `work_items` and `deliberations` for evidence-field population; returns coverage rate per mutation class.
3. `tool_identification.py` - queries `changed_by` attribution patterns; returns percentage attributed to encoded-skill markers.
4. `deliberation_recall.py` - samples 50 recent owner-decision deliberations, runs `gt deliberations search` for each, returns top-3 IDs; precision graded externally (skill output, not benchmark).
5. `advisory_latency.py` - scans `CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` ctimes and bridge ADVISORY entries; cross-references against `work_items.related_bridge_threads` for first acknowledgement.
6. `assertion_signal_noise.py` - queries `assertion_runs` for history; classifies each currently-failing assertion into one of four categories.

### IP-4: Implement CLI

1. Create `scripts/benchmarks/cli.py`:
   - `python scripts/benchmarks/cli.py run [--benchmark <id>|all] [--window-days N] [--output-dir <path>]`
   - `python scripts/benchmarks/cli.py report --run-id <id>` reads existing run and emits formatted markdown.
   - `python scripts/benchmarks/cli.py compare --run-id-from <id> --run-id-to <id>` emits delta.

### IP-5: Add gtkb-benchmarks skill

1. Create `.claude/skills/gtkb-benchmarks/SKILL.md` with usage guidance for both Prime and LO.
2. Add capability registry entry; run `scripts/generate_codex_skill_adapters.py --update-registry` to produce `.codex/skills/gtkb-benchmarks/SKILL.md`.
3. Verify parity with `python scripts/check_harness_parity.py --all --markdown`.

## Tests

`platform_tests/scripts/test_benchmark_<name>.py` per benchmark; each test module includes at minimum:

1. `test_<benchmark>_produces_result_against_fixture` - given a fixture MemBase, returns expected BenchmarkResult.
2. `test_<benchmark>_idempotency_key_stable_across_runs` - same inputs produce same key.
3. `test_<benchmark>_dimensions_populated` - result has harness, role, application/platform, time window.
4. `test_<benchmark>_empty_data_handled` - empty fixture returns zero-value result without crashing.
5. `test_<benchmark>_writes_output_files` - run() writes JSON + markdown to expected paths.

Total: 30 tests (6 benchmarks x 5 tests each). Plus CLI smoke tests and skill-adapter parity tests.

## Verification Plan

Post-impl report at version -003 (or higher) must include:

1. All 30+ tests PASS.
2. Single full-suite run against live MemBase: output captured at `.gtkb-state/benchmarks/<run_id>/`, summary metrics cited in report.
3. The linkage heat map result: actual percentages for the 25 cells, with thresholds marked.
4. The recall coverage result: actual percentages for `work_items` insert evidence, `deliberations` insert linkage, bridge-proposal evidence.
5. The assertion signal/noise result: actual counts in each of four categories from the 1,463 currently-failing assertions.
6. Idempotency proof: two consecutive full-suite runs produce identical results when MemBase state is unchanged.
7. Specification linkage check: every linked spec from above remains satisfied at post-impl time.
8. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite` returns preflight_passed=true.
9. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite` returns no blocking gaps.

## Risks and Rollback

Risks:

- Query performance: benchmark scripts that scan all `work_items` or `tests` rows on every run could be slow. Mitigation: queries are bounded by window_start/window_end; full-table scans only on first baseline.
- Deliberation recall benchmark depends on `gt deliberations search` CLI which currently has an unrelated trace-back on some queries (observed in S349). Mitigation: benchmark catches exceptions per-sample and reports failure rate as an explicit dimension.
- Threshold setting: linkage heatmap cell thresholds are not yet defined. Mitigation: this slice ships with thresholds=None (advisory-only); a follow-on bridge thread sets thresholds after baseline data is collected.

Rollback:

- Retire SPECs created at IP-1 via standard `db.update_specification()` with `status='retired'`.
- Delete benchmark scripts: file removal is reversible from git.
- Remove skill: registry entry removal + adapter regeneration.
- No data mutation in canonical state; only `.gtkb-state/benchmarks/` outputs accumulate, which are explicitly non-authoritative per the SPEC.

## Sequenced Follow-Ons

Per S349 owner directive "parallelize this work to the maximum extent possible", Slice 2 no longer waits for Slice 1 VERIFIED. Filing in parallel.

Independent follow-ons after Slice 2 VERIFIED:

- Slice 2a: MemBase event-ledger schema migration (per Codex advisory Phase 2). Adds `measurement_events`, `metric_definitions`, `metric_snapshots`, `improvement_hypotheses` tables.
- Slice 2b: Dashboard panels for benchmark results.
- Slice 2c: Doctor check that reads latest benchmark run and flags below-threshold cells.

## Recommended Commit Type

`feat:` - new functionality (six benchmark scripts, CLI, skill, capability registry entry, seven SPECs). Backfill commit (running benchmarks against historical data for trend baseline) is a separate `chore:` if owner prefers.

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section with cited governing specs (12 blocking + 3 advisory).
- non-empty `## Prior Deliberations` section with cited DELIB-IDs and INSIGHTS files.
- non-empty `## Owner Decisions / Input` section enumerating S349 AUQ + parallelization directive.
- `target_paths` metadata in header block (21 paths, all in-root).
- `## Requirement Sufficiency` subsection with explicit state.
- `## Recommended Commit Type` per governance hygiene bundle.
