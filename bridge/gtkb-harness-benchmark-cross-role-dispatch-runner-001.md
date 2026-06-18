NEW

Document: gtkb-harness-benchmark-cross-role-dispatch-runner
Version: 001
Status: NEW
Date: 2026-06-17
From: Prime Builder (harness B / Claude)
To: Loyal Opposition
Project Authorization: PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4581
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e
author_model: claude-opus-4-8
author_model_version: Claude Opus 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Implement the cross-role benchmark dispatch runner (Slice 3)

## Summary

Implement the harness-quality benchmark dispatch runner: the first executing
slice of the Harness Testing and Quality Benchmarking program. The runner
enumerates every registered harness across the full cross-role matrix
(each active harness x the two benchmark modes prime_builder and
loyal_opposition), constructs synthetic benchmark dispatch envelopes that
conform to the dispatch-envelope architecture, dispatches them in dry-run /
mock form (no live external side effects), and emits one evidence record per
run carrying the 21 required evidence fields defined by the already-VERIFIED
Slice-1 manifest contract (scripts/benchmarks/harness_quality_manifest.py).
The runner holds all eight manifest safety invariants simultaneously, the
load-bearing one being that benchmark mode is a synthetic, session/envelope-
scoped attribute that MUST NOT mutate durable harness role assignments. The
runner output is the input contract for the later scoring (WI-4583) and
telemetry (WI-4584) slices.

## Specification Links

- ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001 - the WI source specification; the
  runner constructs and dispatches envelopes conforming to this architecture.
- DCL-DISPATCH-ENVELOPE-SCHEMA-001 - synthetic benchmark dispatch envelopes
  must satisfy this schema; a verification test asserts conformance.
- GOV-HARNESS-ONBOARDING-CONTRACT-001 - the cross-role matrix enumerates
  registered harnesses (and a contract for future registered harnesses) from
  the harness registry per the onboarding/capability model.
- GOV-RELIABILITY-FAST-LANE-001 - NOT used here; this is a large new subsystem
  authorized through the project PAUTH below, not the reliability fast lane
  (cited to record the explicit exclusion).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Verification Plan
  derives its tests from the linked specifications and the manifest contract,
  and they will be executed against the implementation before VERIFIED.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the runner, its evidence
  records, and this decision trail are preserved as durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - the work and its design
  decisions are preserved as durable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - the runner consumes the
  Slice-1 manifest artifact and produces benchmark-result artifacts, exercising
  artifact-lifecycle triggers.

## Prior Deliberations

<!-- reviewed -->

- DELIB-20263440 through DELIB-20263447 - the eight owner grill-me-for-
  clarification decisions that define the benchmark program: the full
  cross-role matrix, GT-KB-native fixtures/probes, advisory-first results, and
  the no-live-external-mutation posture. These are recorded as
  OWNER_DECISION_IDS in the Slice-1 manifest and govern this runner's design.
- harness-testing-quality-benchmarking-umbrella (VERIFIED) - sequenced WI-4581
  as the Slice-3 runner; the umbrella does not authorize implementation, which
  this child proposal supplies.
- harness-testing-quality-benchmarking-manifest-rubric (VERIFIED, WI-4579) -
  delivered the read-only manifest contract this runner consumes; its GO
  explicitly placed the runner out of Slice-1 scope.

## Requirement Sufficiency

Existing requirements sufficient. The runner encodes already-decided
requirements (DELIB-20263440..20263447) and the VERIFIED Slice-1 manifest
contract into executable code. It introduces no new or revised requirement or
specification, no policy or architecture sign-off (the dispatch-envelope
architecture is established by ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001 and
DCL-DISPATCH-ENVELOPE-SCHEMA-001), and no destructive, deployment, or
credential action.

## Problem / Background

The Harness Testing and Quality Benchmarking program measures the quality of
each AI coding harness as a Prime Builder and as a Loyal Opposition reviewer.
Slice 1 (WI-4579) delivered only a read-only manifest/rubric contract
(scripts/benchmarks/harness_quality_manifest.py): the benchmark modes, run
tiers, challenge families, the 21 required evidence fields, the eight safety
invariants, and the Dispatcher/Bridge CLI requirements. Nothing yet EXECUTES a
benchmark. WI-4581 (Slice 3) builds the runner that actually dispatches
synthetic probes across the cross-role matrix and produces the evidence records
the scoring (WI-4583) and telemetry (WI-4584) slices consume.

The hard part is dispatching across roles WITHOUT changing any durable state:
benchmark mode must be a synthetic, envelope/session-scoped attribute, never a
mutation of harness-state/harness-registry.json; and external-harness probes
must be dry-run / mock so a benchmark run produces no live external side
effects, no live bridge/backlog/spec mutation, and no dispatcher ranking or
eligibility enforcement.

## Proposed Change

Add a benchmark dispatch runner under scripts/benchmarks/ with these
responsibilities:

1. Harness enumeration. Read the harness registry to enumerate registered
   harnesses (read-only) and form the cross-role matrix: each enumerated
   harness x {prime_builder, loyal_opposition} (the two manifest BENCHMARK_MODES,
   both with durable_role_changes_allowed=False), plus a documented contract
   for future registered harnesses.
2. Synthetic envelope construction. Build benchmark dispatch envelopes that
   conform to DCL-DISPATCH-ENVELOPE-SCHEMA-001 / ADR-DISPATCH-ENVELOPE-
   ARCHITECTURE-001, carrying a synthetic benchmark_mode attribute and a
   dispatch_envelope_id, WITHOUT writing durable role state. Reuse the existing
   dispatch substrate (groundtruth_kb dispatcher + cross-harness trigger code)
   for envelope shape; do not invoke live dispatch.
3. Dispatch + evidence capture. Execute each matrix cell in dry-run / mock mode
   (a pluggable harness-invoker seam defaulting to mock so no external service
   is called), and capture one evidence record per run populated with all 21
   REQUIRED_EVIDENCE_FIELDS (run_id, harness_id, benchmark_mode, provider,
   model, dispatch_envelope_id, fixture_id, run_tier, started_at, ended_at,
   duration_ms, input_tokens, output_tokens, estimated_cost,
   deterministic_score, adjudication_score, outcome, verdict, failure_class,
   required_source_citations, artifact_links). Scores are left unset/placeholder
   here (scoring is WI-4583); the runner guarantees the schema shape.
4. Safety-invariant enforcement. Hold all eight manifest SAFETY_INVARIANT_IDS:
   no_live_cloud_mutation, no_live_deployment_mutation,
   no_credential_lifecycle_action, no_production_application_mutation,
   no_durable_role_assignment_change,
   no_live_bridge_backlog_spec_challenge_mutation,
   no_dispatcher_ranking_or_eligibility_enforcement,
   no_external_service_side_effects.
5. Result emission. Write benchmark-run evidence to a runtime evidence directory
   under .gtkb-state/benchmarks/<run_id>/ (regenerable runtime state, not
   canonical MemBase), in a shape the scoring/telemetry slices consume.
6. Programmatic entrypoint. Expose a clean run(...) API plus a python -m module
   entrypoint. The governed Dispatcher/Bridge CLI subcommand exposure is the
   separate WI-4587 slice; this proposal provides the engine WI-4587 wraps and
   does not add a gt subcommand.

target_paths: ["./scripts/benchmarks/harness_quality_runner.py", "./scripts/benchmarks/benchmark_dispatch_envelope.py", "./platform_tests/scripts/test_harness_quality_runner.py"]

## Verification Plan (spec-derived)

- DCL-DISPATCH-ENVELOPE-SCHEMA-001 -> test asserts every synthetic benchmark
  envelope the runner builds conforms to the dispatch-envelope schema.
- Manifest contract (WI-4579) -> test asserts the runner consumes
  require_valid_manifest and that each emitted evidence record contains exactly
  the 21 REQUIRED_EVIDENCE_FIELDS.
- Cross-role matrix -> test asserts the runner enumerates every registered
  harness x {prime_builder, loyal_opposition} and produces one run per cell.
- no_durable_role_assignment_change -> test asserts harness-state/harness-
  registry.json is byte-identical before and after a full runner pass, and an
  AST/structural test asserts the runner module imports no registry-mutating
  API and calls no role-write function.
- no_external_service_side_effects -> test asserts the default invoker is
  mock/dry-run and that no live external provider call or network egress occurs
  during a run (mock seam asserted).
- no_live_bridge_backlog_spec_challenge_mutation -> test asserts a runner pass
  performs no MemBase, bridge, or backlog write (no mutating-API imports;
  evidence lands only under .gtkb-state/benchmarks/).
- Commands: groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_harness_quality_runner.py -q ; plus
  ruff check and ruff format --check on the new files.

## Risk / Rollback

- Risk: the runner accidentally triggers a live dispatch or a durable-role
  write. Mitigation: dry-run/mock invoker default with no live path wired in
  this slice; explicit safety-invariant tests (durable-role byte-invariance,
  no mutating-API imports, mock-only invoker) fail closed.
- Risk: envelope drift from the canonical schema. Mitigation: schema-conformance
  test against DCL-DISPATCH-ENVELOPE-SCHEMA-001; reuse of the existing envelope
  shape rather than a parallel definition.
- Rollback: delete the three new files; no canonical state is written (evidence
  is regenerable runtime state under .gtkb-state/). No data migration.
- Blast radius: additive new subsystem under scripts/benchmarks/ with read-only
  integration into the dispatcher and harness registry; no changes to live
  dispatch, roles, bridge, or MemBase.

## Authorization

Authorized for proposal filing by PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-
UMBRELLA-PROPOSAL (active; lists WI-4581 in included_work_item_ids; allowed
mutation class "bridge proposal filing for harness benchmark design"). Per that
PAUTH's forbidden_operations, source/test implementation proceeds only after
this proposal receives a Loyal Opposition GO and a work-intent claim is taken
(standard bridge protocol). No fresh owner decision is required.

## Recommended Commit Type

`feat:` - a net-new benchmark dispatch-runner subsystem (new modules + tests),
not a defect repair or refactor.
