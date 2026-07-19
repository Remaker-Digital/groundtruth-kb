REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex desktop interactive Prime Builder A

# WI-5438: Refresh verdict-evidence anchor integration fixtures

bridge_kind: prime_proposal
Document: gtkb-wi5438-verdict-anchor-fixture-governance-refresh
Version: 003
Responds to: bridge/gtkb-wi5438-verdict-anchor-fixture-governance-refresh-002.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5438

target_paths: ["platform_tests/scripts/test_verdict_evidence_anchor_preflight.py"]
implementation_scope: test fixture content only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision accepts the NO-GO diagnosis. Fixture 3 already has independent
proposal and verdict session provenance; it fails earlier because its raw
status-bearing content omits the mandatory artifact-head envelope. The proposed
fix now adds the exact `::init gtkb pb` and `::open test` lines required for a
raw `NO-GO` body before the unchanged evidence-anchor assertion is evaluated.
The revision adds the two missing governing specifications and their
specification-derived verification mapping. The one-test-file scope is
unchanged.

## Summary

Refresh three stale integration fixtures so the verdict-evidence anchor suite
reaches each named assertion under current review-independence,
author-provenance, proposal-specification, and artifact-head-envelope gates.
Production validators and governance gates remain unchanged. The independently
reproduced clean baseline is 26 collected, 23 passed, and three failed before
their intended anchor assertions.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge writes and verdicts remain governed and independently reviewed.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - fixture authors carry explicit provenance.
- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` - status-bearing raw fixture content carries the responder/activity envelope.
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` - fixture 3 places `::init` and `::open` on lines 2 and 3 after `NO-GO`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries PAUTH, project, and WI linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites all governing requirements identified by independent review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification executes the focused suite and mapped negative coverage.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - fixture changes preserve current governance and production behavior.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, proposal revision, implementation report, and verdict remain durable governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the NO-GO finding triggers this corrected REVISED proposal before implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - WI-5438 and its linked test remain the canonical work carrier.

## Prior Deliberations

- `DELIB-20263475` - canonical Deliberation Archive evidence for WI-4520
  establishes the fabricated-NO-GO evidence failure class and recommends a
  deterministic verdict-evidence-anchor control. This revision changes only
  fixtures for that already-governed control.

No searched deliberation supersedes the artifact-head envelope specifications
or authorizes weakening production validation.

## Owner Decisions / Input

The owner authorized the modernization program at project scope and directed
every discovered bridge, TAFE, or harness defect to become an origin=hygiene
work item with a linked test. Active PAUTH
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
covers test and governance-evidence work while preserving GO, claim,
implementation-start, independent verification, and focused-commit gates. No
new owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient.

The independent NO-GO identified two already-specified envelope requirements
that the first proposal omitted; it did not identify a missing requirement or a
new owner tradeoff. This revision cites those specifications and derives the
fixture correction and verification directly from them. No new or revised
requirement is required before implementation.

## Findings Addressed

### Finding 1 - Fixture 3 root cause was misclassified

Accepted. The fixture already uses distinct proposal/verdict session contexts.
Its direct `_deny_reason_for_content` call evaluates raw `NO-GO` content before
writer normalization, so the artifact-head envelope gate denies first. The
revised implementation adds `::init gtkb pb` and `::open test` immediately
after `NO-GO`; it does not change production code or provenance enforcement.

### Finding 2 - Relevant envelope specifications were missing

Accepted. `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` and
`DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` are now explicit
Specification Links and have a dedicated verification row below.

### Finding 3 - MemBase wording is broader than the corrected diagnosis

The non-blocking metadata suggestion is acknowledged but excluded from this
test-only implementation. The canonical bridge revision records the exact
fixture-specific correction. No `groundtruth.db` mutation is proposed.

## Proposed Scope

1. Give the valid NO-GO fixture distinct valid proposal and verdict session provenance.
2. Give the non-verdict NEW fixture concrete Specification Links and other mandatory positive-proposal metadata.
3. Give the hook-level fabricated-NO-GO fixture a valid status-first artifact-head envelope: `NO-GO`, `::init gtkb pb`, then `::open test`.
4. Change only `platform_tests/scripts/test_verdict_evidence_anchor_preflight.py`; do not change production source, hooks, dispatcher, TAFE, harness, eligibility, runtime state, or MemBase.

## Scope Changes

No target-path or implementation-scope expansion. The only substantive proposal
change is the corrected fixture 3 diagnosis and its two governing specification
links.

## Acceptance Criteria

- All 26 focused tests pass and the three stale fixtures reach their named anchor assertions.
- Fixture 3 carries the exact status-first line-2/line-3 artifact-head envelope required by the governing ADR and DCL.
- Negative governance coverage remains fail-closed for same-session review, missing provenance, malformed artifact-head envelopes, and missing Specification Links.
- Exact implementation diff contains one test path and no production, database, dispatcher, TAFE, or runtime behavior changes.

## Spec-Derived Verification Plan

| Specification | Verification | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | focused 26-test module | writer and hook cases reach intended anchor outcomes; all pass |
| `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`; `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` | inspect fixture 3 plus focused test execution | raw `NO-GO` body has exact line-2 `::init gtkb pb` and line-3 `::open test`; evidence-anchor denial is reached |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | inspect positive NEW fixture and owning negative suites | positive fixture has concrete links; negative gate remains active |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | independent rerun before VERIFIED | exact focused results recorded by an unrelated LO session |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; artifact-oriented governance specifications | Ruff, format, diff-check, one-path diff, bridge-chain inspection | clean, exactly scoped, and durably governed |

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verdict_evidence_anchor_preflight.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
git diff --check -- platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
git diff -- platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
```

## Pre-Filing Preflight Subsection

Before filing, run the applicability preflight against this completed revision
body and require `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`, and `blocking_errors: []`. Run the mandatory
clause preflight against the same body and require zero blocking gaps. Any other
result blocks filing.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5438, TEST-11548, and independent NO-GO version 002",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001; DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verdict_evidence_anchor_preflight.py -q --tb=short",
  "before_behavior": "three positive integration fixtures fail at prerequisite governance gates before their named evidence-anchor assertions",
  "after_behavior": "fixtures satisfy current provenance, specification-linkage, and artifact-head-envelope prerequisites, then exercise unchanged evidence-anchor behavior",
  "self_descriptive_naming": "existing names identify valid NO-GO, non-verdict, and fabricated-NO-GO outcomes",
  "obsolete_guidance_disposition": "replace stale fixture content only; no active governance guidance is removed or weakened",
  "history_preservation": "the append-only bridge chain preserves the corrected diagnosis while production behavior and prior versions remain unchanged",
  "baseline": {
    "collected": 26,
    "passed": 23,
    "failed_before_anchor": 3
  },
  "expected_result": {
    "collected": 26,
    "passed": 26,
    "production_files_changed": 0
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused fixture commit without amending history",
    "test": "rerun the focused module and owning negative governance suites"
  },
  "hard_invariants": [
    "no production, database, dispatcher, TAFE, harness, or runtime path changes",
    "review independence and provenance stay fail-closed",
    "artifact-head envelope and proposal Specification Links remain mandatory"
  ],
  "fail_closed_conditions": [
    "any focused test misses its named assertion",
    "any production or runtime path changes",
    "any negative gate is weakened",
    "GO, claim, or implementation-start authority is absent"
  ],
  "essential_context_preservation": "WI-4520 anchor protections, status-first envelope semantics, shared harness behavior, and unrelated worktree bytes remain intact"
}
```

## Risk And Rollback

Risk is limited to making a positive fixture unrealistically permissive or
masking an earlier governance gate. The exact envelope lines, focused negative
coverage, one-path diff, and independent rerun constrain that risk. Rollback is
a separately governed revert of the focused fixture commit; production behavior
requires no rollback because it is unchanged.

## Recommended Commit Type

`test` - refresh stale integration fixtures without production behavior change.
