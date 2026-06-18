NEW

Document: gtkb-harness-benchmark-fixture-corpus
Version: 001
Status: NEW
Date: 2026-06-17
From: Prime Builder (harness B / Claude)
To: Loyal Opposition
Project Authorization: PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4580
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e
author_model: claude-opus-4-8
author_model_version: Claude Opus 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Benchmark fixture corpus - framework, isolation contract, and deterministic-family fixtures

## Summary

Build the foundational slice of the isolated GT-KB benchmark fixture corpus
(Slice 2 of the Harness Testing and Quality Benchmarking program): a fixture
framework (schema + builder/loader), an airtight fixture-isolation contract
(path-boundary containment, a no-live-mutation guarantee, and an explicit
promotion gate), an answer-key schema keyed to the Slice-1 manifest's
deterministic_evidence fields, and seeded-defect fixtures with answer keys for
the five deterministic-only challenge families. Fixtures adapt real GT-KB
source material (bridge proposals, implementation reports, ADR/DCL/GOV specs,
startup overlays, dispatcher rules, hooks, prompts) into isolated workspaces and
inject documented expected defects; they MUST never enter live bridge, backlog,
spec, ADR/DCL/GOV, or MemBase state unless explicitly promoted. The corpus is
the ground-truth the runner (WI-4581) dispatches against and the deterministic
scorer (WI-4583) grades against.

The six challenge families carrying an adjudicated scoring dimension
(role_adoption, bridge_protocol_compliance, review_verdict_quality,
source_citation_quality, responsiveness_reliability_cost,
future_enforcement_readiness) are explicitly DEFERRED to a follow-on sub-slice;
this slice delivers the framework plus the machine-checkable deterministic-only
families so the runner and deterministic scorer have a ground-truth foundation
to build on.

## Specification Links

- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the corpus is verification
  ground-truth; this slice's isolation, schema-conformance, and answer-key tests
  derive from it.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - fixtures are isolated workspaces
  that remain in-root under scripts/benchmarks/fixtures/ and must never touch
  live platform state; the isolation contract operationalizes the in-root
  isolation discipline.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the corpus and its decision
  trail are preserved as durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - fixtures and answer keys are
  durable artifacts under change control.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - the corpus is a new durable
  artifact class with an explicit promotion lifecycle, exercising
  artifact-lifecycle triggers.

## Prior Deliberations

<!-- reviewed -->

- DELIB-20263446 - owner decision selecting "isolated benchmark fixtures built
  from real GT-KB source material" - the direct authority for WI-4580.
- DELIB-20263440 through DELIB-20263447 - the eight owner grill-me-for-
  clarification decisions defining the benchmark program (GT-KB-native fixtures,
  no live external mutation, advisory-first), recorded as OWNER_DECISION_IDS in
  the Slice-1 manifest.
- harness-testing-quality-benchmarking-umbrella (VERIFIED) - sequenced WI-4580
  as the Slice-2 fixture corpus; the umbrella does not authorize implementation.
- harness-testing-quality-benchmarking-manifest-rubric (VERIFIED, WI-4579) -
  delivered the read-only manifest contract (challenge families, per-family
  deterministic_evidence, fixture evidence fields fixture_id / fixture_root /
  source_artifact_refs / promotion_status, and the eight safety invariants) the
  fixtures must conform to. Its GO explicitly placed the fixture corpus out of
  Slice-1 scope.
- No direct prior deliberation exists on the fixture-corpus implementation
  itself.

## Requirement Sufficiency

Existing requirements sufficient. The slice implements DELIB-20263446 and the
already-VERIFIED Slice-1 manifest schema; it introduces no new or revised
requirement or specification, no policy or architecture sign-off, and no
destructive, deployment, or credential action (fixtures are isolated workspaces
that never mutate live state).

## Problem / Background

The benchmark program needs a controlled ground-truth corpus: realistic GT-KB
artifacts with KNOWN, documented defects so a harness's detection behavior can
be scored against an answer key. Slice 1 (WI-4579) froze the contract - the
~11 challenge families, each with expected_evidence and (for most) named
deterministic_evidence keys (e.g. missing_go_rejected, phantom_spec_absent,
status_matrix_result, target_path_match), plus fixture evidence fields and the
safety invariants no_live_membase_mutation and
no_live_bridge_backlog_spec_challenge_mutation. Nothing yet BUILDS the fixtures.
The hard part is two-fold: (1) designing seeded defects + machine-checkable
answer keys that are realistic and unambiguously detectable, and (2) an airtight
isolation contract proving the corpus can never leak into live bridge / backlog
/ spec / MemBase state.

## Proposed Change

Add a fixture framework module scripts/benchmarks/fixture_corpus.py and a
scripts/benchmarks/fixtures/ tree:

1. Fixture schema (frozen dataclass) carrying the manifest fixture evidence
   fields: fixture_id, fixture_root, source_artifact_refs (the real GT-KB
   artifacts adapted), challenge_family, promotion_status (default
   "unpromoted"), and expected_evidence (the per-family answer key).
2. Answer-key schema keyed to the manifest's per-family deterministic_evidence
   tokens, so each seeded defect declares the deterministic evidence a correct
   detection must produce (e.g. missing_go_rejected=True).
3. Isolation contract + enforcement: a builder/loader that materializes fixtures
   only under scripts/benchmarks/fixtures/ (path-boundary), imports NO live
   MemBase/bridge/backlog mutating API, and exposes an explicit promotion gate
   (promotion_status must be deliberately changed; default-unpromoted fixtures
   are inert relative to live state).
4. Seeded-defect fixtures + answer keys for the five deterministic-only
   challenge families: implementation_start_safety, proposal_report_correctness,
   direct_mutation_refusal, cli_first_operation, and fixture_isolation. Each
   fixture adapts a real GT-KB artifact and injects a documented expected defect
   with its answer key.
5. A loader API the runner (WI-4581) consumes to enumerate fixtures and their
   expected evidence without mutating them.

target_paths: ["./scripts/benchmarks/fixture_corpus.py", "./scripts/benchmarks/fixtures/**", "./platform_tests/scripts/test_harness_quality_fixture_corpus.py"]

## Verification Plan (spec-derived)

- Isolation (manifest safety invariants no_live_membase_mutation,
  no_live_bridge_backlog_spec_challenge_mutation; fixture_isolation family
  deterministic_evidence fixture_outside_live_bridge_state,
  no_live_membase_mutation) -> tests assert: all fixture paths resolve under
  scripts/benchmarks/fixtures/ (path-boundary); an AST/structural test asserts
  fixture_corpus.py imports no live MemBase/bridge/backlog mutating API and
  calls no mutating function; default fixtures are promotion_status="unpromoted"
  and a promotion requires an explicit deliberate call.
- Schema conformance -> test asserts every fixture conforms to the fixture
  schema and references a valid manifest challenge family.
- Answer-key integrity -> test asserts every seeded-defect fixture has a
  non-empty answer key whose keys are drawn from its family's manifest
  deterministic_evidence tokens.
- Coverage -> test asserts the five deterministic-only families each have at
  least one seeded-defect fixture.
- Commands: groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_harness_quality_fixture_corpus.py -q ; plus ruff
  check and ruff format --check on the new files.

## Risk / Rollback

- Risk: a fixture or the builder accidentally references or mutates live state.
  Mitigation: the path-boundary + no-mutating-import (AST) + default-unpromoted
  tests fail closed; fixtures are plain data under scripts/benchmarks/fixtures/.
- Risk: ambiguous seeded defects produce unscoreable fixtures. Mitigation: every
  seeded defect declares an explicit answer key tied to a manifest
  deterministic_evidence token; the answer-key-integrity test enforces this.
- Rollback: delete the new module, the fixtures tree, and the test; no canonical
  MemBase/bridge state is written (fixtures are inert, unpromoted). No data
  migration.
- Blast radius: additive new subsystem under scripts/benchmarks/fixtures/; no
  change to live dispatch, bridge, backlog, spec, or MemBase state.

## Authorization

Authorized for proposal filing by PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-
UMBRELLA-PROPOSAL (active; lists WI-4580 in included_work_item_ids; allowed
mutation class "bridge proposal filing for harness benchmark design"). Per that
PAUTH's forbidden_operations, source/test implementation proceeds only after
this proposal receives a Loyal Opposition GO and a work-intent claim is taken
(standard bridge protocol). No fresh owner decision is required (the program,
PAUTH, and ranked WIs were owner-authorized via DELIB-20263440..20263447).

## Recommended Commit Type

`feat:` - a net-new benchmark fixture-corpus subsystem (framework module,
fixture data tree, and tests), not a defect repair or refactor.
