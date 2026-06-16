NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-automation-keep-working-pb-2026-06-16-wi4579
author_model: gpt-5-codex
author_model_version: 2026-06-16
author_model_configuration: Codex desktop automation session; Prime Builder

# Harness Testing Quality Benchmarking Manifest and Rubric Slice

bridge_kind: prime_proposal
Document: harness-testing-quality-benchmarking-manifest-rubric
Version: 001
Date: 2026-06-16 UTC

Project Authorization: PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4579

target_paths: ["scripts/benchmarks/harness_quality_manifest.py", "platform_tests/scripts/test_harness_quality_manifest.py", "bridge/harness-testing-quality-benchmarking-manifest-rubric-*.md"]

implementation_scope: benchmark_manifest, benchmark_rubric, evidence_schema, challenge_taxonomy, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Implement `WI-4579` as the first concrete slice of Harness Testing and Quality Benchmarking 1 by adding a GT-KB-native harness-quality benchmark manifest and rubric module plus validation tests.

The slice should convert the owner decisions captured in `DELIB-20263440` through `DELIB-20263447` into a durable, executable benchmark contract that later slices can consume. It should not dispatch harnesses, alter durable harness-role assignments, create live bridge/backlog/spec challenge artifacts, mutate dispatcher ranking, or perform external live mutations.

## Dependency / Precedence Check

- The live project `PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1` has active authorization `PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL` covering `WI-4579` through `WI-4587` for bridge proposal filing and backlog/project metadata only.
- The umbrella thread `harness-testing-quality-benchmarking-umbrella` has a latest `GO` for project sequencing, ranked slice order, and review path only.
- The umbrella GO explicitly says implementation should start with `WI-4579`; later implementation slices must not bypass their own bridge review.
- This slice precedes `WI-4580` fixture corpus, `WI-4581` runner, `WI-4587` Dispatcher/Bridge CLI exposure, `WI-4582` smoke probes, `WI-4583` scoring, `WI-4584` telemetry, `WI-4585` reporting, and `WI-4586` future enforcement design.
- No duplicate active WI-4579 slice proposal was found in live bridge state before filing this proposal.

## Implementation Plan

1. Add `scripts/benchmarks/harness_quality_manifest.py` with typed, importable definitions for:
   - benchmark modes: `prime_builder` and `loyal_opposition` synthetic benchmark modes, distinct from durable role assignment;
   - run tiers: cheap role/protocol smoke probes, scheduled/on-demand full quality suites, and less frequent adjudicated calibration;
   - challenge families: role adoption, bridge protocol compliance, implementation-start safety, review/verdict quality, proposal/report correctness, spec/ADR/DCL/deliberation citation, direct-mutation refusal, CLI-first operation, fixture isolation, responsiveness, reliability, token/cost capture, and future-enforcement readiness;
   - scoring dimensions: deterministic checks as the spine, calibrated adjudication for subjective design/reasoning/citation quality, and telemetry dimensions for latency/reliability/cost;
   - evidence schema fields required of later benchmark results;
   - safety invariants forbidding live cloud, deployment, credential, production, durable-role, live bridge/backlog/spec, and dispatcher-ranking mutations.
2. Include validation helpers that fail on duplicate IDs, unknown references, missing owner-decision coverage, missing evidence fields, absent safety invariants, or challenge families without deterministic and/or adjudicated scoring coverage.
3. Keep the module read-only: it must define benchmark contracts and validation functions only. It must not run harnesses, update MemBase, write bridge/backlog/spec artifacts, or invoke external services.
4. Add `platform_tests/scripts/test_harness_quality_manifest.py` covering the manifest shape, owner-decision coverage, safety invariants, cross-role matrix declaration, tier definitions, scoring coverage, evidence schema fields, and no live-mutation contract.
5. Leave Dispatcher/Bridge CLI execution and skill-wrapper delegation to the later `WI-4587` slice. This slice may define the CLI contract requirements as manifest data, but it must not implement the CLI runner.

## Non-Goals

- No benchmark execution runner.
- No fixture corpus generation.
- No live dispatch to Codex, Claude, Antigravity, OpenRouter, Ollama, or future harnesses.
- No durable role assignment changes.
- No live bridge, backlog, specification, ADR, DCL, GOV, cloud, deployment, credential, or production application mutation.
- No dispatcher ranking, eligibility, or enforcement changes.
- No formal specification confirmation for `INTAKE-f8bc08a3`; the manifest should carry the intake reference as pending governance context only.

## Specification Links

- `SPEC-1529` - existing benchmark/performance-baseline anchor; this slice extends benchmark coverage into harness-quality contracts without replacing the existing benchmark output convention.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - later synthetic benchmark dispatch should use dispatch-envelope concepts rather than changing durable roles.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - later benchmark dispatch envelopes and result records must preserve structured envelope fields.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - live bridge state authority remains TAFE/dispatcher/versioned bridge state; benchmark fixtures must remain isolated and non-authoritative unless explicitly promoted.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this bridge proposal must receive LO review before implementation, and later implementation reports must return through the bridge.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries machine-readable project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposal requirements apply to this slice.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map directly to the owner decisions, linked specs, and acceptance conditions below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the manifest preserves owner decisions and benchmark scope as durable artifacts while keeping generated challenge artifacts isolated.
- `GOV-STANDING-BACKLOG-001` - this work is tied to active backlog item `WI-4579` and ranked project sequencing.

## Prior Deliberations

- `DELIB-20263440` - full cross-role benchmark matrix: every registered harness is tested in both PB and LO benchmark modes without durable role changes.
- `DELIB-20263441` - hybrid scoring: deterministic answer keys and tests are primary, with calibrated adjudication for design, reasoning, and citation quality.
- `DELIB-20263442` - no live external mutations: cloud, deploy, credential, and production-change scenarios are simulated and scored on governance behavior.
- `DELIB-20263443` - GT-KB-native benchmark corpus: cases exercise actual GT-KB roles, prompts, hooks, procedures, limits, and governance behavior.
- `DELIB-20263444` - advisory-first consequences: benchmark results record evidence first; dispatcher enforcement requires later explicit approval.
- `DELIB-20263445` - tiered cadence: cheap role/protocol probes run frequently, full suites run on schedule or after relevant changes, adjudicated calibration runs less often.
- `DELIB-20263446` - isolated fixtures: challenge artifacts are copied/adapted from real GT-KB materials and do not enter live bridge/backlog/spec state unless explicitly promoted.
- `DELIB-20263447` - Dispatcher/Bridge CLI-first operation: benchmark execution should become a primary CLI use case; direct artifact mutation outside skills/CLI must be probed and barred.
- `bridge/harness-testing-quality-benchmarking-umbrella-003.md` - LO GO for umbrella/project sequencing and ranked slice order.

## Requirement Sufficiency

Existing requirements are sufficient for this slice.

The governing owner decisions and the umbrella GO are sufficient to implement the manifest/rubric contract because the slice's purpose is to encode those decisions into a durable, testable benchmark manifest. Later source-running, fixture-building, CLI-execution, scoring, telemetry, report, and enforcement slices still require their own proposals and GO verdicts.

`INTAKE-f8bc08a3` remains pending and must not be treated as a confirmed formal governance specification in this slice.

## Acceptance Criteria

- The manifest defines exactly the PB and LO benchmark modes and states that benchmark mode must not alter durable harness-role assignments.
- The manifest encodes all eight owner-decision IDs `DELIB-20263440` through `DELIB-20263447` as required decision coverage.
- The manifest includes challenge-family taxonomy entries tied to GT-KB source material categories and expected evidence, not generic model benchmarks.
- Every challenge family declares scoring coverage and at least one deterministic evidence path unless explicitly marked adjudication-only with rationale.
- The evidence schema includes harness ID, benchmark mode, provider/model when known, dispatch/envelope identifiers when applicable, fixture ID, run tier, start/end timestamps, duration, token/cost fields when available, deterministic score, adjudication score, outcome/verdict, failure class, required-source citations, and artifact links.
- The manifest explicitly forbids live external mutations, durable role changes, live bridge/backlog/spec challenge mutation, dispatcher ranking/eligibility enforcement, and credential lifecycle actions.
- The run tiers distinguish smoke, full quality, and adjudicated calibration cadences.
- The planned validation tests prove uniqueness, required decision coverage, required evidence fields, safety invariants, tier definitions, and scoring coverage.

## Spec-Derived Verification Plan

- Run `python -m pytest platform_tests/scripts/test_harness_quality_manifest.py -q --tb=short`.
- Run `python -m ruff check scripts/benchmarks/harness_quality_manifest.py platform_tests/scripts/test_harness_quality_manifest.py`.
- Run `python -m ruff format --check scripts/benchmarks/harness_quality_manifest.py platform_tests/scripts/test_harness_quality_manifest.py`.
- Run `python scripts/bridge_applicability_preflight.py --bridge-id harness-testing-quality-benchmarking-manifest-rubric --content-file bridge/harness-testing-quality-benchmarking-manifest-rubric-001.md --json` after filing and before implementation reporting.
- Run `python scripts/adr_dcl_clause_preflight.py --bridge-id harness-testing-quality-benchmarking-manifest-rubric --content-file bridge/harness-testing-quality-benchmarking-manifest-rubric-001.md` after filing and before implementation reporting.

## Risk / Rollback

Risk is low and bounded to an additive benchmark contract and focused tests. The main risk is over-specifying future runner or dispatcher behavior in the manifest. Mitigation: keep this slice to manifest data, validation helpers, and tests; leave execution and enforcement to later reviewed slices. Rollback is removal of the additive module and test file plus a normal bridge follow-up report.
