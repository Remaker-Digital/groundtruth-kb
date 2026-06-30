REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1755-5d84-7792-b2d9-263b0e14d6b3
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access; cwd=E:\GT-KB

bridge_kind: prime_proposal
Document: gtkb-harness-benchmark-cross-role-dispatch-runner
Version: 003
Status: REVISED
Date: 2026-06-30
From: Prime Builder (Codex, harness A)
To: Loyal Opposition
Responds-To: bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-002.md
Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4581
Recommended commit type: feat:

target_paths: ["scripts/benchmarks/harness_quality_runner.py", "scripts/benchmarks/benchmark_dispatch_envelope.py", "platform_tests/scripts/test_harness_quality_runner.py"]

# Cross-role benchmark dispatch runner - REVISED after manifest amendment verification

## Summary

Resume WI-4581 from its owner-directed `DEFERRED` parking state. The clear
condition in `bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-002.md`
is now met: `bridge/gtkb-harness-benchmark-manifest-amendment-004.md` reached
`VERIFIED` on 2026-06-30, and `scripts/benchmarks/harness_quality_manifest.py`
now exposes both the 22-field `REQUIRED_EVIDENCE_FIELDS` contract including
`author_model_configuration` and the closed `FAILURE_CLASSES` taxonomy.

This revision preserves the original runner slice while updating it to consume
the amended manifest. The runner must emit evidence records containing all
manifest fields, must carry `author_model_configuration` from the synthetic
dispatch envelope into the benchmark evidence, and must populate
`failure_class` with a value from `FAILURE_CLASSES` or the explicit `unscored`
sentinel until downstream scoring supplies a more specific value.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is a Prime-authored bridge
  proposal filed through the append-only bridge protocol before source/test
  mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites
  governing specifications before implementation starts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal declares
  project authorization, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps
  every implementation claim to executable tests and preflights.
- `GOV-STANDING-BACKLOG-001` - work remains tied to WI-4581 in the MemBase
  backlog and benchmark project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires the
  active bounded benchmark project authorization and an implementation-start
  packet before protected source/test mutation.
- `SPEC-1529` - project authorization packet requirements apply to the bounded
  implementation authorization.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - the runner constructs synthetic
  dispatch envelopes while preserving harness/model execution context.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - synthetic envelopes and emitted evidence
  records must satisfy the schema-governed manifest fields.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - benchmark dispatch evidence must
  not compete with live bridge state; TAFE-backed bridge state remains
  authoritative.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - the runner enumerates registered
  harnesses through the harness registry/capability model.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - runner outputs are durable benchmark
  artifacts rather than transient session notes.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - benchmark evidence records are
  governed artifacts with explicit lifecycle handling.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - resuming a deferred benchmark slice
  and introducing runner artifacts triggers bridge-governed lifecycle handling.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain inside
  the GT-KB platform root and do not mutate adopter application state.

## Prior Deliberations

- `DELIB-20263440` through `DELIB-20263447` - owner decisions defining the
  benchmark program, including the full cross-role matrix, GT-KB-native
  fixtures/probes, no live external mutation, and advisory-first result use.
- `DELIB-20265586` - active bounded project authorization for the Harness
  Testing and Quality Benchmarking implementation stream.
- `bridge/harness-testing-quality-benchmarking-manifest-rubric-004.md` -
  VERIFIED Slice 1 manifest/rubric baseline.
- `bridge/gtkb-harness-benchmark-manifest-amendment-004.md` - VERIFIED manifest
  amendment that satisfies this thread's resume condition.
- `bridge/gtkb-harness-benchmark-fixture-corpus-005.md` - current
  implementation report for WI-4580; the runner must consume the fixture corpus
  loader contract rather than duplicate fixture internals.
- `bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-002.md` -
  owner-directed DEFERRED state and clear/resume instructions.

## Owner Decisions / Input

No new owner decision is required for this revision. The owner already selected
the pause-then-manifest-amendment path in the `-002` DEFERRED entry, and the
project implementation authorization is active under `DELIB-20265586`.

## Requirement Sufficiency

Existing requirements sufficient.

The verified manifest amendment, the original WI-4581 proposal, and the
DEFERRED clear condition define the required revised behavior: consume the
22-field manifest, propagate `author_model_configuration`, emit a valid
`failure_class`, preserve the no-live-mutation safety invariants, and keep
benchmark mode synthetic rather than changing durable harness roles.

## Proposed Scope

1. Add `scripts/benchmarks/benchmark_dispatch_envelope.py` with a pure synthetic
   benchmark envelope dataclass/schema helper that carries harness id, benchmark
   mode, provider/model identifiers, and `author_model_configuration`.
2. Add `scripts/benchmarks/harness_quality_runner.py` with read-only functions
   that enumerate benchmark runs, validate benchmark modes against
   `BENCHMARK_MODES`, load fixture ids from the fixture corpus, and emit
   manifest-complete evidence records.
3. Ensure emitted evidence records contain every name in
   `REQUIRED_EVIDENCE_FIELDS`, use `FAILURE_CLASSES` for `failure_class`, and
   default to `unscored` before scoring is available.
4. Preserve all manifest safety invariants: no live bridge/backlog/spec
   challenge mutation, no dispatcher ranking/eligibility enforcement, no
   external service side effects, no credential lifecycle action, and no durable
   harness role assignment change.
5. Add focused platform tests in
   `platform_tests/scripts/test_harness_quality_runner.py`.

## Spec-Derived Verification Plan

- `python scripts/implementation_authorization.py begin --bridge-id gtkb-harness-benchmark-cross-role-dispatch-runner`
  must authorize only the declared target paths.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-benchmark-cross-role-dispatch-runner`
  must pass after filing with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-benchmark-cross-role-dispatch-runner`
  must exit 0 with no blocking gaps.
- `python -m pytest platform_tests/scripts/test_harness_quality_runner.py -q --tb=short`
  must cover manifest-complete evidence output, author-model-configuration
  propagation, `failure_class` validation, no durable role mutation, no live
  bridge/backlog/spec mutation, fixture-corpus consumption, and dry-run/mock
  dispatch behavior.
- `python -m ruff check scripts/benchmarks/harness_quality_runner.py scripts/benchmarks/benchmark_dispatch_envelope.py platform_tests/scripts/test_harness_quality_runner.py`
  must pass.
- `python -m ruff format --check scripts/benchmarks/harness_quality_runner.py scripts/benchmarks/benchmark_dispatch_envelope.py platform_tests/scripts/test_harness_quality_runner.py`
  must pass.

## Acceptance Criteria

- The runner emits a dictionary or typed record containing exactly the manifest
  required evidence field names, including `author_model_configuration`.
- `failure_class` values are rejected unless they appear in `FAILURE_CLASSES`.
- Benchmark mode is synthetic and cannot mutate durable harness role
  assignment.
- Runner execution uses fixture/mock/dry-run inputs only and performs no live
  external service calls or live bridge/backlog/spec mutations.
- The fixture corpus is consumed through its loader/index contract.

## Risk / Rollback

Risk is contained because the proposal adds new benchmark runner modules and a
focused test file only. Rollback is removal of those additive files and the
bridge implementation report if verification fails.

## Pre-Filing Preflight Evidence

Before filing, Prime Builder runs the candidate content through:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-harness-benchmark-cross-role-dispatch-runner-003.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-harness-benchmark-cross-role-dispatch-runner-003.md
```

Expected result for filing: applicability preflight passes with
`missing_required_specs: []` and `missing_advisory_specs: []`; clause preflight
exits 0 with no blocking gaps.
