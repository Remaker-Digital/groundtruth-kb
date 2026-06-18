NEW

Document: gtkb-harness-benchmark-telemetry-integration
Version: 001
Status: NEW
Date: 2026-06-17
From: Prime Builder (harness B / Claude)
To: Loyal Opposition
Project Authorization: PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4584
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e
author_model: claude-opus-4-8
author_model_version: Claude Opus 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Benchmark telemetry integration - mapping/reconciliation core (Slice 6a)

## Summary

Implement the mapping/reconciliation core that turns a benchmark run evidence
record (the Slice-1 manifest's 21 REQUIRED_EVIDENCE_FIELDS) into the two
telemetry shapes the program needs: the existing TAFE stage-attempt telemetry
field shape and an enriched benchmark result-store record. This slice delivers
the pure, reproducible normalization logic - field mapping, token/cost
reconciliation (benchmark splits input_tokens/output_tokens whereas TAFE carries
a single token_count; benchmark carries estimated_cost vs TAFE cost), and a
stable idempotency key so re-runs do not duplicate telemetry - plus its tests.

The actual persistence write-through (calling the MemBase stage-attempt
telemetry insert and writing the result-store record) is DEFERRED to a follow-on
sub-slice: it requires the WI-4581 runner to be implemented and producing live
evidence records, and it crosses into a MemBase write that is cleaner to land
once a real producer exists. This slice is pure mapping (no MemBase mutation, no
IO write), designed against the frozen Slice-1 manifest contract and tested with
synthetic evidence records, so it is fileable and reviewable now independent of
the runner's implementation timing.

## Specification Links

- ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001 - the WI source decision; it
  establishes TAFE/dispatcher/versioned bridge state as authoritative, and this
  slice maps benchmark evidence onto the TAFE stage-attempt telemetry shape
  consistent with that authority (contextual/governing link, not a field-level
  requirement spec).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the mapping, normalization,
  and idempotency tests derive from this constraint.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the mapping module and its
  decision trail are preserved as durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - telemetry records are
  durable artifacts under change control.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - benchmark telemetry is a new
  durable artifact class, exercising artifact-lifecycle triggers.

## Prior Deliberations

<!-- reviewed -->

- DELIB-20263440 through DELIB-20263447 - the program's owner decisions
  (OWNER_DECISION_IDS in the Slice-1 manifest): GT-KB-native, advisory-first,
  no-live-external-mutation, CLI-first.
- harness-testing-quality-benchmarking-umbrella (VERIFIED) - sequenced WI-4584
  as the Slice-6 telemetry consumer; the umbrella does not authorize
  implementation.
- harness-testing-quality-benchmarking-manifest-rubric (VERIFIED, WI-4579) -
  froze the 21 REQUIRED_EVIDENCE_FIELDS this mapping consumes.
- gtkb-harness-benchmark-cross-role-dispatch-runner (NEW, WI-4581) - the producer
  whose evidence records this telemetry slice consumes; its output contract is
  the frozen manifest, so this slice does not block on the runner's
  implementation.
- No direct prior deliberation exists on the telemetry-integration slice itself.

## Requirement Sufficiency

Existing requirements sufficient. The slice encodes the already-decided field
contract (the VERIFIED Slice-1 manifest) and aligns with the established TAFE
authority (ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001). It introduces no new or
revised requirement or specification, no policy or architecture sign-off, and no
destructive, deployment, or credential action (this slice writes nothing - it is
pure mapping/normalization).

## Problem / Background

The benchmark program (advisory-first, no-live-external-mutation) needs each run's
evidence to land in both the existing TAFE stage-attempt telemetry surface
(typed_artifact_flow record_stage_attempt_telemetry: agent_harness_id, provider,
model_identifier, dispatch_decision, started_at, completed_at, duration_ms,
token_count, cost, outcome, verdict, artifact_links, metadata) and the benchmark
result store (scripts/benchmarks/common.py BenchmarkResult). The manifest's 21
evidence fields and the TAFE telemetry fields are CLOSE but not identical -
benchmark splits input_tokens/output_tokens while TAFE has a single token_count,
benchmark has estimated_cost vs TAFE cost, and the score fields (deterministic/
adjudication) have no TAFE analogue. Reconciling these two shapes consistently,
and computing a stable idempotency key so a re-run does not double-count
telemetry, is the core that must be correct before any write-through wiring.

## Proposed Change

Add a new module scripts/benchmarks/harness_quality_telemetry.py (additive; no
edits to existing files in this slice):

1. evidence_to_stage_attempt(evidence) -> dict: pure mapping from a benchmark
   evidence record (manifest 21 fields) to the TAFE stage-attempt telemetry field
   shape, normalizing token_count = input_tokens + output_tokens, cost =
   estimated_cost, and carrying benchmark-only fields (benchmark_mode, run_tier,
   deterministic_score, adjudication_score, fixture_id, dispatch_envelope_id)
   into the telemetry metadata dict so nothing is lost.
2. evidence_to_result_record(evidence) -> dict: pure mapping to the enriched
   benchmark result-store record shape (consumed by reporting).
3. telemetry_idempotency_key(evidence) -> str: a stable key derived from
   (run_id, harness_id, benchmark_mode, dispatch_envelope_id) so re-emitting the
   same run's telemetry is detectably idempotent.
4. A validate step asserting an evidence record carries all 21 manifest fields
   before mapping (reusing the manifest REQUIRED_EVIDENCE_FIELDS).

All functions are pure (no MemBase/IO writes). The persistence write-through
(MemBase stage-attempt telemetry insert + result-store write) is a deferred
follow-on requiring the live runner.

target_paths: ["./scripts/benchmarks/harness_quality_telemetry.py", "./platform_tests/scripts/test_harness_quality_telemetry.py"]

## Verification Plan (spec-derived)

- Field mapping (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001) -> test: a
  synthetic evidence record with all 21 manifest fields maps to a stage-attempt
  dict whose token_count = input_tokens + output_tokens and cost = estimated_cost,
  with benchmark-only fields preserved in metadata.
- Validation -> test: an evidence record missing any of the 21 REQUIRED_EVIDENCE_FIELDS
  is rejected before mapping.
- Idempotency -> test: telemetry_idempotency_key is stable for fixed inputs and
  differs across distinct (run_id, harness_id, benchmark_mode, dispatch_envelope_id).
- Purity -> test: the mapping functions perform no MemBase/bridge/IO write (no
  mutating-API import; module is import-clean).
- Commands: groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_harness_quality_telemetry.py -q ; plus ruff check
  and ruff format --check on the new files.

## Risk / Rollback

- Risk: the mapping drifts from either the manifest fields or the TAFE telemetry
  fields. Mitigation: the validate step is keyed to the manifest's
  REQUIRED_EVIDENCE_FIELDS; tests assert the exact mapping; pure functions make
  the mapping trivially testable.
- Risk: designing against a not-yet-implemented runner. Mitigation: the input
  contract is the FROZEN Slice-1 manifest (VERIFIED); tests use synthetic
  evidence records; the write-through is deferred until the runner lands.
- Rollback: delete the module and its test; no canonical state is written
  (pure mapping). No data migration.
- Blast radius: one additive module plus tests; no edits to existing files; no
  MemBase write, no IO; pure functions only.

## Authorization

Authorized for proposal filing by PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-
UMBRELLA-PROPOSAL (active; lists WI-4584 in included_work_item_ids; allowed
mutation class "bridge proposal filing for harness benchmark design"). Per that
PAUTH's forbidden_operations, source/test implementation proceeds only after this
proposal receives a Loyal Opposition GO and a work-intent claim is taken
(standard bridge protocol). No fresh owner decision is required (the program,
PAUTH, and ranked WIs were owner-authorized via DELIB-20263440..20263447).

## Recommended Commit Type

`feat:` - a net-new benchmark telemetry mapping module plus tests, not a defect
repair or refactor.
