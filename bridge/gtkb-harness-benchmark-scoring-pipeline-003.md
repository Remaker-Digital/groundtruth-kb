REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1755-5d84-7792-b2d9-263b0e14d6b3
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access; cwd=E:\GT-KB

bridge_kind: prime_proposal
Document: gtkb-harness-benchmark-scoring-pipeline
Version: 003
Status: REVISED
Date: 2026-06-30
From: Prime Builder (Codex, harness A)
To: Loyal Opposition
Responds-To: bridge/gtkb-harness-benchmark-scoring-pipeline-002.md
Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4583
Recommended commit type: feat:

target_paths: ["scripts/benchmarks/harness_quality_scoring.py", "platform_tests/scripts/test_harness_quality_scoring.py"]

# Hybrid scoring pipeline - REVISED after manifest amendment verification

## Summary

Resume WI-4583 from its owner-directed `DEFERRED` parking state. The clear
condition in `bridge/gtkb-harness-benchmark-scoring-pipeline-002.md` is now
met: `bridge/gtkb-harness-benchmark-manifest-amendment-004.md` reached
`VERIFIED`, and the manifest now exposes the 22-field evidence contract plus a
closed `FAILURE_CLASSES` taxonomy.

This revision updates the scoring slice so the deterministic scorer consumes
the amended manifest, scores `failure_class` against the closed taxonomy, and
incorporates the E1 reviewer-rigor enhancement from the DEFERRED entry:
NO-GO-rate-on-seeded-defect-corpus becomes a deterministic reviewer-quality
metric for Loyal Opposition benchmark mode. Scoring output remains advisory;
dispatcher ranking or eligibility enforcement remains out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is a Prime-authored bridge
  proposal filed before protected source/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing specs
  are linked before implementation starts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal declares
  project authorization, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - scoring correctness and
  determinism tests are derived from the linked requirements.
- `GOV-STANDING-BACKLOG-001` - work remains tied to WI-4583 in the MemBase
  backlog and benchmark project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires the
  active bounded benchmark project authorization and implementation-start
  packet before protected source/test mutation.
- `SPEC-1529` - project authorization packet requirements apply to the bounded
  implementation authorization.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - scored evidence records preserve
  harness/model/configuration context from benchmark execution.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - scoring consumes manifest-governed
  evidence fields and validates the closed failure-class vocabulary.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - advisory scoring records do not
  replace or mutate live TAFE/bridge state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - benchmark scores are durable
  artifacts rather than transient comments.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - score records and scorer behavior
  are governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - resuming a deferred scoring slice and
  introducing score artifacts triggers bridge-governed lifecycle handling.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain inside
  the GT-KB platform root and out of adopter application state.

## Prior Deliberations

- `DELIB-20263440` through `DELIB-20263447` - owner decisions defining the
  benchmark program, hybrid deterministic/adjudicated scoring, and
  advisory-first output posture.
- `DELIB-20265586` - active bounded project authorization for the benchmark
  implementation stream.
- `bridge/harness-testing-quality-benchmarking-manifest-rubric-004.md` -
  VERIFIED Slice 1 scoring and manifest baseline.
- `bridge/gtkb-harness-benchmark-manifest-amendment-004.md` - VERIFIED manifest
  amendment satisfying the resume condition.
- `bridge/gtkb-harness-benchmark-fixture-corpus-005.md` - current fixture
  corpus implementation report; scorer must consume fixture answer keys through
  the corpus loader contract.
- `bridge/gtkb-harness-benchmark-scoring-pipeline-002.md` - owner-directed
  DEFERRED state, including E1 reviewer-rigor enhancement.

## Owner Decisions / Input

No new owner decision is required. The owner already selected the
pause-then-manifest-amendment path in the `-002` DEFERRED entry, and active
project authorization is recorded under `DELIB-20265586`.

## Requirement Sufficiency

Existing requirements sufficient.

The scoring behavior is constrained by the verified benchmark manifest, the
original WI-4583 proposal, the DEFERRED clear condition, and the program owner
decisions. This revision introduces no enforcement policy. It keeps all scores
advisory until a separate owner-approved bridge authorizes any dispatcher
ranking or eligibility use.

## Proposed Scope

1. Add `scripts/benchmarks/harness_quality_scoring.py` with pure deterministic
   scoring functions over benchmark evidence and fixture answer keys.
2. Validate input evidence against `REQUIRED_EVIDENCE_FIELDS`, including
   `author_model_configuration`.
3. Validate and score `failure_class` against `FAILURE_CLASSES`; wrong or
   missing expected failure-class matches reduce deterministic score.
4. Add a reviewer-rigor metric for Loyal Opposition benchmark mode:
   NO-GO-rate-on-seeded-defect-corpus, computed from fixture expected defects
   and observed review verdicts.
5. Preserve separate deterministic and adjudication-score fields; the
   adjudicator implementation remains a later slice and defaults to an
   explicit no-op/unavailable state here.
6. Add focused tests in
   `platform_tests/scripts/test_harness_quality_scoring.py`.

## Spec-Derived Verification Plan

- `python scripts/implementation_authorization.py begin --bridge-id gtkb-harness-benchmark-scoring-pipeline`
  must authorize only the declared target paths.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-benchmark-scoring-pipeline`
  must pass after filing with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-benchmark-scoring-pipeline`
  must exit 0 with no blocking gaps.
- `python -m pytest platform_tests/scripts/test_harness_quality_scoring.py -q --tb=short`
  must cover manifest field validation, failure-class scoring, deterministic
  reproducibility for fixed inputs, reviewer-rigor metric calculation,
  advisory-only output, and adjudication-seam separation.
- `python -m ruff check scripts/benchmarks/harness_quality_scoring.py platform_tests/scripts/test_harness_quality_scoring.py`
  must pass.
- `python -m ruff format --check scripts/benchmarks/harness_quality_scoring.py platform_tests/scripts/test_harness_quality_scoring.py`
  must pass.

## Acceptance Criteria

- Fixed evidence plus fixed answer key yields identical deterministic scores
  across runs.
- Evidence missing any `REQUIRED_EVIDENCE_FIELDS` entry is rejected.
- `failure_class` values outside `FAILURE_CLASSES` are rejected.
- Reviewer-rigor scoring uses seeded-defect verdict expectations and does not
  call external services.
- No scorer output changes dispatcher ranking, harness eligibility, MemBase
  state, or live bridge state.

## Risk / Rollback

Risk is contained because the implementation is additive and pure. Rollback is
removal of the scoring module and focused test file plus any implementation
report if verification fails.

## Pre-Filing Preflight Evidence

Before filing, Prime Builder runs the candidate content through:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-harness-benchmark-scoring-pipeline-003.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-harness-benchmark-scoring-pipeline-003.md
```

Expected result for filing: applicability preflight passes with
`missing_required_specs: []` and `missing_advisory_specs: []`; clause preflight
exits 0 with no blocking gaps.
