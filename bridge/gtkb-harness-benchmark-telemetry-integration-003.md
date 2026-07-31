REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1755-5d84-7792-b2d9-263b0e14d6b3
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access; cwd=E:\GT-KB

bridge_kind: prime_proposal
Document: gtkb-harness-benchmark-telemetry-integration
Version: 003
Status: REVISED
Date: 2026-06-30
From: Prime Builder (Codex, harness A)
To: Loyal Opposition
Responds-To: bridge/gtkb-harness-benchmark-telemetry-integration-002.md
Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4584
Recommended commit type: feat:

target_paths: ["scripts/benchmarks/harness_quality_telemetry.py", "platform_tests/scripts/test_harness_quality_telemetry.py"]

# Benchmark telemetry integration - REVISED after manifest amendment verification

## Summary

Resume WI-4584 from its owner-directed `DEFERRED` parking state. The clear
condition in `bridge/gtkb-harness-benchmark-telemetry-integration-002.md` is
now met: `bridge/gtkb-harness-benchmark-manifest-amendment-004.md` reached
`VERIFIED`, and the manifest now includes `author_model_configuration` plus the
closed `FAILURE_CLASSES` taxonomy.

This revision keeps the telemetry slice pure and additive. It updates the
mapping/reconciliation contract to consume the 22-field benchmark evidence
schema, propagate `author_model_configuration` into TAFE stage-attempt metadata
and benchmark result records, and preserve the enumerated `failure_class` value
through both shapes so later reporting can group results by failure class.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is a Prime-authored bridge
  proposal filed before protected source/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing specs
  are linked before implementation starts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal declares
  project authorization, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - telemetry mapping tests
  are derived from the linked requirements.
- `GOV-STANDING-BACKLOG-001` - work remains tied to WI-4584 in the MemBase
  backlog and benchmark project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires the
  active bounded benchmark project authorization and implementation-start
  packet before protected source/test mutation.
- `SPEC-1529` - project authorization packet requirements apply to the bounded
  implementation authorization.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - telemetry preserves benchmark
  execution context, including model configuration.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - telemetry consumes manifest-governed
  evidence fields and the closed failure-class vocabulary.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - stage-attempt telemetry mapping
  respects TAFE's authoritative flow state without mutating it in this slice.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - benchmark telemetry records are
  durable artifacts rather than transient notes.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - telemetry records and mappings are
  governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - resuming a deferred telemetry slice
  and introducing telemetry artifacts triggers bridge-governed lifecycle
  handling.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain inside
  the GT-KB platform root and out of adopter application state.

## Prior Deliberations

- `DELIB-20263440` through `DELIB-20263447` - owner decisions defining the
  benchmark program, advisory-first posture, no-live-external-mutation boundary,
  and CLI-first execution approach.
- `DELIB-20265586` - active bounded project authorization for the benchmark
  implementation stream.
- `bridge/harness-testing-quality-benchmarking-manifest-rubric-004.md` -
  VERIFIED Slice 1 manifest/rubric baseline.
- `bridge/gtkb-harness-benchmark-manifest-amendment-004.md` - VERIFIED manifest
  amendment satisfying the resume condition.
- `bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-002.md` - upstream
  runner slice deferred state; this telemetry mapping remains pure until a
  producer implementation exists.
- `bridge/gtkb-harness-benchmark-telemetry-integration-002.md` - owner-directed
  DEFERRED state and clear/resume instructions.

## Owner Decisions / Input

No new owner decision is required. The owner already selected the
pause-then-manifest-amendment path in the `-002` DEFERRED entry, and active
project authorization is recorded under `DELIB-20265586`.

## Requirement Sufficiency

Existing requirements sufficient.

The telemetry mapping behavior is constrained by the verified benchmark
manifest, the original WI-4584 proposal, the DEFERRED clear condition, and the
program owner decisions. This slice remains pure mapping and validation; it does
not write MemBase, persist live stage attempts, or change dispatcher behavior.

## Proposed Scope

1. Add `scripts/benchmarks/harness_quality_telemetry.py` with pure mapping
   functions from manifest-complete benchmark evidence into a TAFE
   stage-attempt-shaped dictionary and a benchmark result-store dictionary.
2. Validate evidence against `REQUIRED_EVIDENCE_FIELDS`, including
   `author_model_configuration`.
3. Validate `failure_class` against `FAILURE_CLASSES`.
4. Preserve `author_model_configuration` and `failure_class` in TAFE metadata
   and in enriched benchmark result records.
5. Reconcile token/cost fields deterministically: benchmark
   `input_tokens` + `output_tokens` maps to TAFE `token_count`, and
   `estimated_cost` maps to cost.
6. Compute a stable idempotency key so re-runs do not duplicate downstream
   telemetry once persistence is implemented in a later slice.
7. Add focused tests in
   `platform_tests/scripts/test_harness_quality_telemetry.py`.

## Spec-Derived Verification Plan

- `python scripts/implementation_authorization.py begin --bridge-id gtkb-harness-benchmark-telemetry-integration`
  must authorize only the declared target paths.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-benchmark-telemetry-integration`
  must pass after filing with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-benchmark-telemetry-integration`
  must exit 0 with no blocking gaps.
- `python -m pytest platform_tests/scripts/test_harness_quality_telemetry.py -q --tb=short`
  must cover field validation, author-model-configuration propagation,
  failure-class preservation, token/cost reconciliation, idempotency key
  stability, no MemBase writes, and no live TAFE mutation.
- `python -m ruff check scripts/benchmarks/harness_quality_telemetry.py platform_tests/scripts/test_harness_quality_telemetry.py`
  must pass.
- `python -m ruff format --check scripts/benchmarks/harness_quality_telemetry.py platform_tests/scripts/test_harness_quality_telemetry.py`
  must pass.

## Acceptance Criteria

- Evidence missing any `REQUIRED_EVIDENCE_FIELDS` entry is rejected.
- `author_model_configuration` is present in both TAFE metadata and benchmark
  result output.
- `failure_class` is present in both mapping outputs and must be one of
  `FAILURE_CLASSES`.
- Token and cost reconciliation are deterministic.
- This slice performs no MemBase write, no live TAFE write, no external service
  call, and no dispatcher behavior change.

## Risk / Rollback

Risk is contained because the implementation is additive and pure. Rollback is
removal of the telemetry module and focused test file plus any implementation
report if verification fails.

## Pre-Filing Preflight Evidence

Before filing, Prime Builder runs the candidate content through:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-harness-benchmark-telemetry-integration-003.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-harness-benchmark-telemetry-integration-003.md
```

Expected result for filing: applicability preflight passes with
`missing_required_specs: []` and `missing_advisory_specs: []`; clause preflight
exits 0 with no blocking gaps.
