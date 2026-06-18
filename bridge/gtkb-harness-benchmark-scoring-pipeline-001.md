NEW

Document: gtkb-harness-benchmark-scoring-pipeline
Version: 001
Status: NEW
Date: 2026-06-17
From: Prime Builder (harness B / Claude)
To: Loyal Opposition
Project Authorization: PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4583
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e
author_model: claude-opus-4-8
author_model_version: Claude Opus 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Hybrid scoring pipeline - deterministic scorer + adjudication seam (Slice 4a)

## Summary

Implement the deterministic spine of the harness-quality scoring pipeline plus a
pluggable adjudication seam. The pipeline consumes a benchmark run's evidence
record (the Slice-1 manifest's 21 REQUIRED_EVIDENCE_FIELDS, including
deterministic_score and adjudication_score) and the fixture's answer key (the
per-family deterministic_evidence tokens), computes a reproducible DETERMINISTIC
score across the deterministic dimensions (seeded-defect recall, false
positives, lint/test outcomes, required-source citation, ADR/spec/deliberation
inspection, role/protocol compliance, latency, reliability, cost), and records
deterministic_score and adjudication_score SEPARATELY with an explicit per-
dimension deterministic-vs-adjudicated label. Scoring output is ADVISORY only;
dispatcher ranking/eligibility enforcement is the separately-gated WI-4586 and
is out of scope.

The calibrated LLM-adjudicator implementation (for the subjective dimensions -
design judgment, reasoning/explanation quality, code-review judgment, citation
usefulness) is DEFERRED to a follow-on sub-slice. This slice delivers the
reproducible deterministic scorer in full plus a no-op-default adjudicator seam,
so deterministic scoring is usable immediately and the adjudicated path has a
stable interface to land in later.

## Specification Links

- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the pipeline's determinism,
  separation, and scoring-correctness tests derive from this constraint;
  reproducible scoring is itself the verification target.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint. (Note: the WI's
  recorded source_spec_id SPEC-1529 is a mis-linkage - SPEC-1529 is
  "Performance baseline benchmarks" for concurrent tenant tests, unrelated to
  harness-quality scoring - so it is deliberately NOT cited as governing. WI-4583
  is governed by the program owner decisions and the Slice-1 manifest contract
  below.)
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the scorer and its decision
  trail are preserved as durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - scores are durable advisory
  artifacts under change control.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - score records are a new
  durable artifact class, exercising artifact-lifecycle triggers.

## Prior Deliberations

<!-- reviewed -->

- DELIB-20263440 through DELIB-20263447 - the program's owner decisions, recorded
  as OWNER_DECISION_IDS in the Slice-1 manifest, including the hybrid
  deterministic+adjudicated scoring-model selection (deterministic evidence is
  the spine; calibrated adjudication for subjective quality) and the
  advisory-output posture (scores advisory until later explicit owner-approved
  enforcement).
- harness-testing-quality-benchmarking-umbrella (VERIFIED) - sequenced WI-4583
  as the Slice-4 scoring work and explicitly states scoring remains future-slice
  work requiring its own implementation report and verification; the umbrella
  does not authorize implementation.
- harness-testing-quality-benchmarking-manifest-rubric (VERIFIED, WI-4579) -
  froze SCORING_DIMENSIONS (deterministic, adjudicated, telemetry), the
  deterministic_score and adjudication_score evidence fields, and the per-family
  deterministic_evidence / adjudication_rationale this pipeline consumes.
- No direct prior deliberation exists on the scoring-pipeline implementation
  itself.

## Requirement Sufficiency

Existing requirements sufficient. The slice implements the already-decided
hybrid scoring model (DELIB-20263440..20263447) and the VERIFIED Slice-1 manifest
contract; it introduces no new or revised requirement or specification, no
policy or architecture sign-off, and no destructive, deployment, or credential
action (scoring is advisory output; enforcement is the separate WI-4586).

## Problem / Background

Slice 1 (WI-4579) froze the scoring contract - the dimensions, the separate
deterministic_score and adjudication_score fields, and per-family
deterministic_evidence answer-key tokens - but nothing computes a score. The
runner (WI-4581, proposed) produces evidence records and the fixtures (WI-4580,
proposed) carry answer keys; this slice turns those into scores. The hard
requirements are: (1) the deterministic scorer must be REPRODUCIBLE for fixed
inputs (a deterministic function of run evidence + answer key), and (2) the
deterministic and adjudicated scores must stay SEPARATELY recorded and labeled,
so an adjudicated (calibrated, non-reproducible) judgment is never silently
mixed into the deterministic score. Because the runner and fixtures are proposed
but not yet implemented, this slice is designed against the FROZEN manifest
contract and tested against synthetic evidence records and answer keys - it does
not depend on WI-4581/WI-4580 being implemented first.

## Proposed Change

Add a scoring module scripts/benchmarks/harness_quality_scoring.py:

1. A deterministic scorer: a pure function score_deterministic(run_evidence,
   answer_key) -> deterministic result, comparing the run's observed
   deterministic evidence against the fixture answer key's
   deterministic_evidence tokens across the deterministic dimensions; computes
   per-dimension sub-scores (e.g., seeded-defect recall, false-positive penalty,
   lint/test outcome, required-source-citation presence) and a deterministic
   rollup. Reproducible: identical inputs always yield identical output.
2. An adjudication seam: an Adjudicator protocol with a no-op default that
   leaves adjudication_score unset (None) for the subjective dimensions; the
   calibrated LLM-adjudicator is a deferred sub-slice. The rollup tolerates an
   absent adjudication_score.
3. A combined result that records deterministic_score and adjudication_score as
   SEPARATE fields plus a per-dimension label (deterministic | adjudicated),
   carrying an advisory_only=True flag and performing no dispatcher
   ranking/eligibility enforcement.
4. A loader/adapter that reads run evidence records (the manifest's 21-field
   schema) and fixture answer keys (WI-4580 schema) without mutating them.

target_paths: ["./scripts/benchmarks/harness_quality_scoring.py", "./platform_tests/scripts/test_harness_quality_scoring.py"]

## Verification Plan (spec-derived)

- Reproducibility (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001) -> test
  asserts score_deterministic returns identical output across repeated calls on
  fixed synthetic inputs (no randomness, no time/identity dependence).
- Separation -> test asserts deterministic_score and adjudication_score are
  distinct fields and that the no-op adjudicator leaves adjudication_score=None
  while deterministic_score is populated; the per-dimension label correctly tags
  each dimension.
- Deterministic correctness -> tests assert: a synthetic run that produces a
  family's deterministic_evidence token (detects the seeded defect) scores
  higher than one that does not (recall); a false-positive detection is
  penalized.
- Advisory-only -> test asserts the result carries advisory_only=True and the
  module performs no dispatcher ranking/eligibility mutation (no mutating-API
  import; enforcement is WI-4586).
- Commands: groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_harness_quality_scoring.py -q ; plus ruff check and
  ruff format --check on the new files.

## Risk / Rollback

- Risk: adjudicated judgment leaking into the deterministic score. Mitigation:
  the separation test asserts the two scores are distinct fields and the
  deterministic path is a pure function; the adjudication seam defaults to no-op.
- Risk: designing against a not-yet-implemented runner/fixtures interface.
  Mitigation: the interface is the FROZEN Slice-1 manifest contract (VERIFIED);
  tests use synthetic evidence records + answer keys conforming to it, so the
  scorer is validated independently of WI-4581/WI-4580 implementation timing.
- Rollback: delete the module and its test; no canonical state is written
  (scores are advisory runtime output). No data migration.
- Blast radius: one additive module plus tests; read-only consumption of run
  evidence + answer keys; advisory output only, no enforcement surface.

## Authorization

Authorized for proposal filing by PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-
UMBRELLA-PROPOSAL (active; lists WI-4583 in included_work_item_ids; allowed
mutation class "bridge proposal filing for harness benchmark design"). Per that
PAUTH's forbidden_operations, source/test implementation proceeds only after
this proposal receives a Loyal Opposition GO and a work-intent claim is taken
(standard bridge protocol). No fresh owner decision is required (the program,
PAUTH, ranked WIs, and the hybrid scoring model were owner-authorized via
DELIB-20263440..20263447).

## Recommended Commit Type

`feat:` - a net-new scoring-pipeline subsystem (deterministic scorer +
adjudication seam) plus tests, not a defect repair or refactor.
