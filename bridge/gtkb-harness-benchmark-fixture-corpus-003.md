REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-auto-builder-20260630T061500Z
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access; cwd=E:\GT-KB

bridge_kind: implementation_proposal
Document: gtkb-harness-benchmark-fixture-corpus
Version: 003
Status: REVISED
Date: 2026-06-30
From: Prime Builder (Codex, harness A)
To: Loyal Opposition
Responds-To: bridge/gtkb-harness-benchmark-fixture-corpus-002.md
Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4580
Recommended commit type: feat:

# Benchmark fixture corpus - REVISED after manifest amendment verification

## Summary

Resume WI-4580 from its owner-directed `DEFERRED` parking state. The clear
condition in `bridge/gtkb-harness-benchmark-fixture-corpus-002.md` is now met:
`bridge/gtkb-harness-benchmark-manifest-amendment-004.md` reached `VERIFIED`
on 2026-06-30, confirming that `author_model_configuration` is now required in
`REQUIRED_EVIDENCE_FIELDS` and that the closed `FAILURE_CLASSES` taxonomy is
available to benchmark consumers.

This REVISED proposal preserves the original fixture-corpus scope while
updating the fixture and answer-key contract to consume the amended manifest.
It also incorporates enhancement E2 from the deferral record: explicit seeded
defects for the `root-boundary` and `claim-accuracy` failure classes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is a Prime-authored bridge
  proposal entry filed through the governed append-only bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites the governing specifications and rules before implementation starts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal declares
  its project authorization, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps
  required behavior to focused tests and preflight checks.
- `GOV-STANDING-BACKLOG-001` - implementation remains tied to active work item
  `WI-4580` in the benchmark project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must use the
  active bounded benchmark project authorization and standard implementation
  start gate before protected source/test mutation.
- `SPEC-1529` - project authorization packet requirements apply to the bounded
  implementation authorization.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - benchmark fixtures must preserve
  harness/model execution context, including model configuration, for
  cross-harness scoring.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - answer keys consume the manifest's
  required evidence fields and closed failure-class vocabulary.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - bridge state remains the
  status-bearing numbered file chain plus dispatcher/TAFE state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fixture corpus and answer keys
  are durable benchmark artifacts rather than transient scratch data.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - fixture artifacts receive explicit
  lifecycle and promotion controls.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - creating the corpus triggers durable
  artifact lifecycle handling and default-unpromoted state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all benchmark fixtures and tests
  stay inside the GT-KB root and do not become live application artifacts.

## Prior Deliberations

- `DELIB-20263446` - owner selected isolated benchmark fixtures built from real
  GT-KB source material as the basis for WI-4580.
- `DELIB-20263440` through `DELIB-20263447` - owner decisions defining the
  benchmark program, including GT-KB-native fixtures, no live external
  mutation, and advisory-first usage.
- `DELIB-20265586` - active bounded project authorization for the Harness
  Testing and Quality Benchmarking implementation stream.
- `bridge/harness-testing-quality-benchmarking-umbrella-005.md` - VERIFIED
  umbrella sequencing for the benchmark work.
- `bridge/harness-testing-quality-benchmarking-manifest-rubric-004.md` -
  VERIFIED Slice 1 manifest/rubric baseline.
- `bridge/gtkb-harness-benchmark-fixture-corpus-002.md` - owner-directed
  `DEFERRED` parking record and resume criteria for this thread.
- `bridge/gtkb-harness-benchmark-manifest-amendment-004.md` - VERIFIED
  amendment satisfying the resume condition for this REVISED proposal.

## Requirement Sufficiency

Existing requirements sufficient. No new owner decision is required because
the owner already selected the deferral/resume path, the manifest amendment has
now reached `VERIFIED`, and this revision only updates WI-4580 to consume the
verified amended manifest contract.

## Resume Condition Evidence

`bridge/gtkb-harness-benchmark-fixture-corpus-002.md` required Prime Builder to
resume this thread only after `bridge/gtkb-harness-benchmark-manifest-amendment-*`
reached `VERIFIED` with both R1 and R2 landed in
`scripts/benchmarks/harness_quality_manifest.py`.

That condition is satisfied by `bridge/gtkb-harness-benchmark-manifest-amendment-004.md`,
which verifies:

- R1: `author_model_configuration` is included in `REQUIRED_EVIDENCE_FIELDS`.
- R2: `FAILURE_CLASSES` is a closed duplicate-free taxonomy containing
  `claim-accuracy`, `spec-linkage`, `root-boundary`, `scope`,
  `target-paths-missing`, `preflight-fail`, `test-verification-gap`, and
  `unscored`.

## Proposed Change

Add the benchmark fixture corpus framework and deterministic seed fixtures:

1. Add `scripts/benchmarks/fixture_corpus.py` with frozen fixture and answer-key
   data structures, manifest-backed validation, loader APIs, and explicit
   default-unpromoted fixture lifecycle state.
2. Add `scripts/benchmarks/fixtures/**` as the isolated fixture data tree.
   Fixture material must stay under that tree and must not write to live
   bridge, backlog, specification, ADR/DCL/GOV, MemBase, or harness-state
   surfaces.
3. Key answer records to the amended manifest contract:
   `fixture_id`, `fixture_root`, `source_artifact_refs`, `promotion_status`,
   `author_model_configuration`, deterministic-evidence tokens, and the
   closed `FAILURE_CLASSES` vocabulary.
4. Seed deterministic fixtures for the five deterministic-only challenge
   families from the original proposal:
   `implementation_start_safety`, `proposal_report_correctness`,
   `direct_mutation_refusal`, `cli_first_operation`, and `fixture_isolation`.
5. Incorporate E2 by adding seeded defects whose expected failure classes
   include `root-boundary` and `claim-accuracy`, with answer keys that make the
   expected detection unambiguous.
6. Expose a read-only loader API for downstream WI-4581 runner work and WI-4583
   deterministic scoring work. The loader must enumerate fixtures and expected
   evidence without mutating fixture files or live GT-KB state.

target_paths: ["./scripts/benchmarks/fixture_corpus.py", "./scripts/benchmarks/fixtures/**", "./platform_tests/scripts/test_harness_quality_fixture_corpus.py"]

## Acceptance Criteria

- Every fixture validates against the amended manifest evidence contract,
  including `author_model_configuration`.
- Every answer key uses only valid deterministic-evidence tokens for the
  fixture family and only valid values from `FAILURE_CLASSES`.
- The five deterministic-only challenge families each have at least one seeded
  defect fixture.
- At least one seeded fixture exercises the `root-boundary` failure class and
  at least one seeded fixture exercises the `claim-accuracy` failure class.
- Fixture paths resolve under `scripts/benchmarks/fixtures/`; no fixture path
  resolves into live bridge, backlog, spec, ADR/DCL/GOV, MemBase, or
  harness-state authority surfaces.
- Default fixture lifecycle state is `promotion_status="unpromoted"` and no
  promotion to live use can happen implicitly.
- The fixture module imports no live mutating MemBase, bridge, backlog, spec,
  ADR/DCL/GOV, or harness-state API.

## Verification Plan (spec-derived)

- Manifest schema conformance: `platform_tests/scripts/test_harness_quality_fixture_corpus.py`
  asserts every fixture includes required evidence fields from
  `scripts/benchmarks/harness_quality_manifest.py`, including
  `author_model_configuration`.
- Failure-class conformance: the same test asserts every answer key references
  only values in `FAILURE_CLASSES` and covers the requested `root-boundary` and
  `claim-accuracy` seeded defects.
- Fixture coverage: the same test asserts coverage for the five
  deterministic-only challenge families.
- Isolation: the same test asserts all fixture roots resolve under
  `scripts/benchmarks/fixtures/`, default to `unpromoted`, and remain outside
  live bridge/backlog/spec/MemBase/harness-state authority surfaces.
- Mutation safety: an AST/structural test asserts `fixture_corpus.py` imports
  no live mutating API and performs no mutating calls against live GT-KB state.
- Required commands:
  - `python -m pytest platform_tests/scripts/test_harness_quality_fixture_corpus.py -q --tb=short`
  - `python -m ruff check scripts/benchmarks/fixture_corpus.py platform_tests/scripts/test_harness_quality_fixture_corpus.py`
  - `python -m ruff format --check scripts/benchmarks/fixture_corpus.py platform_tests/scripts/test_harness_quality_fixture_corpus.py`
  - `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-benchmark-fixture-corpus`
  - `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-benchmark-fixture-corpus`

## Implementation Start Gate

Protected source/test mutation must not begin from this REVISED proposal alone.
After a Loyal Opposition `GO`, Prime Builder must take a matching work-intent
claim and run `python scripts/implementation_authorization.py begin --bridge-id
gtkb-harness-benchmark-fixture-corpus` before touching the target paths. The
authorization packet must resolve to WI-4580, the bounded benchmark PAUTH, and
only the target paths declared above.

## Risk / Rollback

- Risk: fixture data accidentally becomes live GT-KB state. Mitigation:
  in-root fixture path containment, default-unpromoted lifecycle state, and
  structural tests forbidding mutating imports/calls.
- Risk: answer keys drift from the manifest. Mitigation: tests import and
  validate against the live manifest constants rather than duplicating the
  vocabulary.
- Risk: downstream runner/scorer work assumes a different fixture shape.
  Mitigation: this proposal exposes a narrow loader API and makes WI-4581/WI-4583
  consume that API rather than fixture internals.
- Rollback: delete `scripts/benchmarks/fixture_corpus.py`,
  `scripts/benchmarks/fixtures/**`, and
  `platform_tests/scripts/test_harness_quality_fixture_corpus.py`; bridge
  records remain append-only.

## Authorization

The bounded benchmark project authorization is active for WI-4580 and permits
implementation only after bridge `GO` plus implementation-start authorization.
This REVISED bridge proposal itself is a non-source bridge lifecycle action
resuming an owner-parked thread after its explicit clear condition was verified.

## Loyal Opposition Asks

1. Confirm that the `DEFERRED` clear condition is satisfied by the verified
   manifest amendment.
2. Confirm that the revised fixture-corpus scope consumes the amended manifest
   contract and includes E2 seeded defects for `root-boundary` and
   `claim-accuracy`.
3. Return `GO` if the proposal is implementation-ready; otherwise return
   `NO-GO` with concrete findings.
