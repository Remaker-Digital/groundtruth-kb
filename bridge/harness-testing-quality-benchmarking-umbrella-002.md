REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-desktop-20260616-harness-testing-quality-benchmarking-1
author_model: GPT-5 Codex
author_model_version: 2026-06-16
author_model_configuration: Codex desktop default coding-agent configuration
author_metadata_source: explicit Codex bridge fallback filing

# Umbrella Proposal - Harness Testing and Quality Benchmarking 1

bridge_kind: prime_proposal
Document: harness-testing-quality-benchmarking-umbrella
Version: 002
Date: 2026-06-16 UTC
Supersedes: bridge/harness-testing-quality-benchmarking-umbrella-001.md

Project Authorization: PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4579

target_paths: ["scripts/benchmarks/", "platform_tests/scripts/", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/", "config/dispatcher/rules.toml"]

Umbrella proposal coordinating multiple related work items for regular, GT-KB-native harness testing across Prime Builder and Loyal Opposition roles, output quality, responsiveness, reliability, cost, and Dispatcher/Bridge CLI use.

## Claim

GT-KB should implement a benchmark system that regularly tests every registered harness in both Prime Builder and Loyal Opposition benchmark modes using isolated, GT-KB-native challenge fixtures, hybrid deterministic/adjudicated scoring, telemetry-backed cost and responsiveness measurement, advisory-first reporting, and a later explicitly gated path for benchmark-informed dispatcher enforcement.

Revision 002 adds the owner requirement that benchmark tests must run through the Dispatcher/Bridge CLI and serve as first-class use cases for that CLI. Where sensible, skills should sit on top of CLI commands rather than raw file or DB mutations. Agents should be explicitly barred from mutating GT-KB artifacts except through governed skills or direct CLI access.

This umbrella does not authorize direct implementation mutations. It creates the project and backlog structure, records the owner decisions that shape the benchmark, and proposes ranked implementation slices for Loyal Opposition review.

## Revision Summary

- Added `DELIB-20263447` as a governing owner decision for CLI-first benchmark operation.
- Captured formal spec-intake candidate `INTAKE-f8bc08a3` for later confirm/reject as a governance specification.
- Added `WI-4587` / `TEST-11154`: Expose harness benchmark execution through Dispatcher/Bridge CLI.
- Updated `PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL` to version 2, including `WI-4587` and forbidding agent mutation outside governed skills or direct Dispatcher/Bridge CLI access.

## Investigation Summary

- Existing benchmark infrastructure already exists under `scripts/benchmarks/` with shared result/run helpers and report output under `.gtkb-state/benchmarks/`.
- Existing platform tests cover benchmark CLI behavior under `platform_tests/scripts/test_benchmark_*.py`.
- TAFE stage-attempt telemetry already contains fields useful for benchmark runs, including harness ID, session/context/model/provider, dispatch decision, lease ID, start/end timestamps, duration, token count, cost, outcome, verdict, test summary, failure class, and artifact links.
- Current dispatcher configuration already models per-harness `dispatch_cost`, `dispatch_quality`, and `availability`, but those are static configuration values rather than regularly measured benchmark results.
- `gt bridge dispatch status --json` reported dispatcher health PASS during investigation, with Codex as current PB target and Ollama/OpenRouter/Antigravity as LO-order targets, but benchmark coverage must be broader than currently selected routing.
- Existing verification scripts and tests for Ollama, Antigravity, OpenRouter, dispatch, role projection, and harness capability checks are candidates to adapt into GT-KB-native benchmark probes.
- The Dispatcher/Bridge CLI must become the execution surface for these benchmark runs, so the benchmark system doubles as a real adoption test for GT-KB's primary mutating system UI.

## Umbrella Inventory

Ranked work items created under `PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1`:

1. `WI-4579` / `TEST-11146` - Define GT-KB-native harness benchmark rubric and manifest. Priority P1.
2. `WI-4580` / `TEST-11147` - Build isolated GT-KB benchmark fixture corpus with seeded flaws. Priority P1.
3. `WI-4581` / `TEST-11148` - Implement full cross-role benchmark dispatch runner. Priority P1.
4. `WI-4587` / `TEST-11154` - Expose harness benchmark execution through Dispatcher/Bridge CLI. Priority P1.
5. `WI-4582` / `TEST-11149` - Implement cheap role and protocol smoke probes. Priority P1.
6. `WI-4583` / `TEST-11150` - Implement hybrid deterministic and adjudicated scoring pipeline. Priority P1.
7. `WI-4584` / `TEST-11151` - Integrate benchmark telemetry for responsiveness reliability and cost. Priority P2.
8. `WI-4585` / `TEST-11152` - Add tiered benchmark cadence reporting and remediation surfaces. Priority P2.
9. `WI-4586` / `TEST-11153` - Design gated future enforcement path for benchmark-informed dispatch. Priority P3.

## Requirement Sufficiency

New or revised requirements required before implementation.

The owner decisions captured in this session are sufficient to rank the project and file this revised umbrella proposal, but implementation should start with `WI-4579`: a GT-KB-native benchmark manifest/rubric that converts the decisions into durable benchmark requirements, challenge-case schema, evidence fields, CLI execution contract, and scoring thresholds. No source/config/hook/dispatcher implementation should proceed until that manifest/rubric is accepted by review.

`INTAKE-f8bc08a3` should be confirmed or rejected before implementing the broader governance rule that agents may mutate GT-KB artifacts only through governed skills or direct CLI access.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Use existing credential scanners; benchmark fixtures use prose descriptions or runtime-assembled synthetic markers rather than credential-shaped literals. | Run credential scan and fixture-content tests before filing implementation reports. |  |
| CQ-PATHS-001 | Yes | Keep mutable artifacts under the configured project root and keep seeded benchmark fixtures outside live bridge/backlog/spec authority. | Add path-boundary tests for fixture generation and dispatch-run artifact writes. |  |
| CQ-COMPLEXITY-001 | Yes | Keep runner, CLI surface, fixture, scorer, and reporter modules separated by responsibility with typed data structures for benchmark cases and results. | Run focused unit tests plus `ruff` complexity/static checks for touched modules. |  |
| CQ-CONSTANTS-001 | Yes | Centralize benchmark dimensions, challenge families, thresholds, cadence names, and CLI operation names in a manifest/schema rather than duplicating literals across tests. | Add manifest validation tests that fail on unknown or duplicated dimensions. |  |
| CQ-SECURITY-001 | Yes | Forbid live cloud, deployment, credential, and production mutations; simulate unsafe requests and score refusal/escalation behavior. | Add tests proving benchmark cases do not invoke live external mutation paths and that unsafe-change probes expect escalation. |  |
| CQ-DOCS-001 | Yes | Document challenge families, scoring dimensions, run tiers, CLI commands, and interpretation of advisory benchmark results in the manifest/report surfaces. | Verify generated reports and manifest docs include required sections. |  |
| CQ-TESTS-001 | Yes | Each work item has a linked GOV-12 test; implementation slices must add unit/integration tests for manifest, fixtures, runner, CLI, scoring, telemetry, and reports. | Run linked tests `TEST-11146` through `TEST-11154` plus targeted platform tests. |  |
| CQ-LOGGING-001 | Yes | Record structured benchmark telemetry without secrets, including CLI command path, harness, role, model/provider, timestamps, duration, token/cost when available, outcome, and artifact links. | Add telemetry serialization tests and redaction checks for run artifacts. |  |
| CQ-VERIFICATION-001 | Yes | Each slice implementation report must cite spec-derived verification and distinguish deterministic score evidence from adjudicated score evidence. | Loyal Opposition verifies implementation reports against the linked tests and scoring artifacts. |  |

## In-Root Placement Evidence

All expected target paths are under the configured project root: `scripts/benchmarks`, `platform_tests/scripts`, `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher`, `config/dispatcher/rules.toml`.

## Specification Links

- `SPEC-1529` - Existing benchmark/performance-baseline anchor; this project extends benchmark coverage from performance baselines to harness-quality baselines.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - Dispatch envelopes are the natural substrate for synthetic cross-role benchmark dispatch and CLI operation.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - Synthetic benchmark envelopes must satisfy dispatch-envelope schema constraints.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - Benchmark attempts and bridge-related outputs should align with TAFE-authoritative bridge state and generated bridge views.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Implementation work remains bridge-governed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Owner decisions, benchmark requirements, work items, reports, and remediation candidates must become durable artifacts when they cross the governance threshold.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Slice proposals must cite applicable specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Implementation reports must include specification-derived verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal links project, authorization, and work item metadata.
- `GOV-STANDING-BACKLOG-001` - Work items are the backlog authority for future implementation slices.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Benchmark cases must test harness prompt/hook behavior while respecting Codex hook parity limitations.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Benchmark fixtures, outputs, and decisions must be modeled as durable artifacts where appropriate.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Benchmark failures should trigger appropriate artifact lifecycle actions without skipping owner confirmation.

## Prior Deliberations

- `DELIB-20263440` - Owner selected the full cross-role matrix: every registered harness is tested in PB and LO benchmark modes without changing durable role assignment.
- `DELIB-20263441` - Owner selected hybrid scoring: deterministic evidence primary, calibrated adjudication for subjective quality dimensions.
- `DELIB-20263442` - Owner selected no live external mutations in benchmark tasks.
- `DELIB-20263443` - Owner required GT-KB-native/adapted benchmarks over generic standardized benchmark authority.
- `DELIB-20263444` - Owner selected advisory-first benchmark consequences, with dispatcher enforcement/ranking gated behind later explicit approval.
- `DELIB-20263445` - Owner selected tiered cadence: frequent cheap probes, scheduled/on-change full suites, less frequent calibrated adjudication.
- `DELIB-20263446` - Owner selected isolated benchmark fixtures built from real GT-KB source material.
- `DELIB-20263447` - Owner required benchmark tests to run via Dispatcher/Bridge CLI and required skills to sit over CLI commands where sensible.
- `DELIB-2572` - Prior role/status orthogonality dispatch review is relevant to role-routing benchmark probes.
- `DELIB-20260798` - Prior active-status capability gate lifecycle verification is relevant to harness availability and dispatchability measurement.
- `DELIB-20261425` - Prior role/status orthogonality resolver review is relevant to full cross-role matrix behavior.

## Owner Decisions / Input

- `DELIB-20263440` through `DELIB-20263447` capture the completed clarification decisions for this project.
- `INTAKE-f8bc08a3` captures the CLI-first artifact-mutation rule as a pending governance specification candidate.
- `PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL` version 2 bounds this umbrella to proposal/backlog metadata and forbids implementation mutations until later bridge GO and work-intent claim.

## Proposed Scope

Slice 1 (`WI-4579`): Define the benchmark manifest, schema, rubric, scoring dimensions, evidence model, challenge-family taxonomy, CLI execution contract, and GT-KB-specific benchmark acceptance criteria.

Slice 2 (`WI-4580`): Build isolated benchmark fixture workspaces from real GT-KB materials with seeded defects and answer keys. Include LO review fixtures, PB implementation/proposal fixtures, role-adoption fixtures, protocol-boundary fixtures, citation/DA-search fixtures, unsafe live-change escalation fixtures, and direct-artifact-mutation refusal fixtures.

Slice 3 (`WI-4581` + `WI-4587`): Implement the full harness-by-role benchmark runner exposed through the Dispatcher/Bridge CLI. The runner must use synthetic benchmark envelopes, must not change durable role assignments, and must be invokable as the primary system UI for benchmark operation.

Slice 4 (`WI-4582`): Implement cheap role and protocol smoke probes. Include checks that agents do not mutate GT-KB artifacts except through governed skills or direct CLI access.

Slice 5 (`WI-4583`): Implement deterministic and adjudicated scoring. Deterministic checks include seeded-defect recall, false positives, required artifact citations, ADR/spec/deliberation inspection, lint/test results, role/protocol compliance, CLI-path compliance, latency, reliability, and cost. Adjudication covers design choices, code-review judgment, explanation quality, and citation usefulness.

Slice 6 (`WI-4584`): Integrate telemetry with existing TAFE/stage-attempt and benchmark result surfaces, including CLI command path and token/cost data when available.

Slice 7 (`WI-4585`): Add tiered cadence, benchmark run reports, dashboard summaries, trend views, and advisory remediation/backlog suggestions.

Slice 8 (`WI-4586`): Design but do not activate benchmark-informed dispatch enforcement. Any routing/ranking/eligibility effect requires a separate owner-approved bridge proposal after score thresholds mature.

## Specification-Derived Verification Plan

- `WI-4579` / `TEST-11146`: Manifest/rubric test proves challenge families, scoring dimensions, evidence fields, CLI execution contract, and thresholds are tied to `DELIB-20263440` through `DELIB-20263447` and prioritize GT-KB-native behavior.
- `WI-4580` / `TEST-11147`: Fixture-corpus test proves seeded cases are isolated from live bridge/backlog/spec authority while preserving GT-KB role, prompt, hook, procedure, limit, governance, dispatcher, and CLI realism.
- `WI-4581` / `TEST-11148`: Runner test proves every registered harness is enumerated across PB and LO benchmark roles and durable harness role assignments are unchanged.
- `WI-4587` / `TEST-11154`: CLI test proves benchmark execution is available through the Dispatcher/Bridge CLI, skills delegate to CLI commands where sensible, and direct agent mutation outside governed skills or CLI access is detected or blocked.
- `WI-4582` / `TEST-11149`: Smoke-probe test proves role adoption, bridge-protocol compliance, mutation-boundary compliance, CLI-path compliance, and unsafe external-change escalation failures are detected.
- `WI-4583` / `TEST-11150`: Scoring test proves deterministic metrics and calibrated adjudication scores are separately recorded and rolled up.
- `WI-4584` / `TEST-11151`: Telemetry test proves normalized fields are persisted for CLI command path, harness, role, provider/model, timestamps, duration, token/cost when available, outcome, artifacts, and reliability.
- `WI-4585` / `TEST-11152`: Cadence/reporting test proves smoke, full, and calibration tiers can run separately and produce actionable advisory reports without changing dispatcher routing.
- `WI-4586` / `TEST-11153`: Enforcement-design test proves benchmark results are advisory by default and any dispatcher influence remains disabled without separate owner-approved authorization/proposal.

## Acceptance Criteria

- The benchmark suite is GT-KB-native: challenge cases exercise real GT-KB roles, prompts, hooks, bridge protocol, dispatcher behavior, CLI behavior, ADR/spec/deliberation obligations, work-item/project procedure, and mutation boundaries.
- Benchmark runs are invokable through the Dispatcher/Bridge CLI and serve as use cases for that CLI.
- Skills that operate benchmark or artifact mutation paths delegate to CLI commands where sensible.
- Agents are tested against and explicitly barred from GT-KB artifact mutation except through governed skills or direct CLI access.
- Every registered harness can be benchmarked in both PB and LO roles without changing durable role assignment.
- No benchmark task performs live external cloud, deployment, credential, or production mutation.
- Benchmark challenge cases are isolated fixtures built from real GT-KB source material; seeded defects do not enter live bridge, backlog, or spec authority.
- The scoring model separates deterministic evidence from adjudicated quality and records both.
- Responsiveness, reliability, and cost are captured per harness/model/run where available.
- Results are advisory at first. No automatic dispatcher ranking, eligibility, or suspension change is activated by this project without a later explicit owner-approved bridge proposal.
- Full implementation proceeds by ranked work item and must receive normal bridge GO and work-intent claim before protected file mutations.

## Risks / Rollback

- Risk: Generic benchmark drift. Mitigation: `WI-4579` requires GT-KB-native challenge taxonomy before implementation.
- Risk: Fixture pollution of live artifacts. Mitigation: isolated fixture workspaces; no seeded defects in live bridge/backlog/spec surfaces.
- Risk: CLI bypass by skills or agents. Mitigation: `WI-4587` requires CLI-first benchmark execution and direct-mutation probes.
- Risk: Cost growth from full cross-role matrix. Mitigation: tiered cadence and separate cheap smoke probes.
- Risk: Subjective scoring instability. Mitigation: deterministic metrics remain primary and adjudication is separately labeled/calibrated.
- Risk: Benchmark results prematurely affect dispatch. Mitigation: `WI-4586` is design-only; enforcement remains disabled until later explicit approval.
- Rollback: disable scheduled benchmark tiers, remove generated benchmark run artifacts from `.gtkb-state/benchmarks/`, and revert source changes per slice. Because live external mutations are forbidden, rollback does not require cloud/deploy/credential recovery.

## Files Expected To Change

- `scripts/benchmarks/`
- `platform_tests/scripts/`
- `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/`
- `config/dispatcher/rules.toml`

Additional target paths may be added by later slice proposals after the manifest/rubric identifies exact implementation needs.

## Recommended Commit Type

`docs`
