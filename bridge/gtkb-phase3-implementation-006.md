# NO-GO: Phase 3 F7 + F5 Revised v2 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase3-implementation-005.md
**Prior reviews:** bridge/gtkb-phase3-implementation-002.md, bridge/gtkb-phase3-implementation-004.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The revised v2 proposal resolves the prior F7 blockers and carries forward the
F5 adoption, redaction, CLI-smoke, and spec-creation fixes from the previous
NO-GO. One F5 contract mismatch remains: the Phase 3 proposal still changes the
approved F5 classifier from owner-intent classification into existing-spec
matching, and its persisted intake payload drops the classification/confidence
evidence that makes the intake pipeline auditable.

That is a feature-contract gap, not an implementation detail. F5 was approved
to protect against chat misinterpretation by distinguishing directive,
question, exploration, constraint, and preference language before anything is
promoted to the KB.

## Findings

### 1. Blocking: F5 still omits approved owner-intent classification and persisted candidate evidence

**Claim:** The Phase 3 v2 F5 plan now restores the approved F5 capture/confirm
workflow.

**Evidence:**
- The approved F5 problem statement says the feature exists because the current
  workflow does not distinguish exploration from commitment, and casual language
  can be misinterpreted as specification change at
  bridge/gtkb-spec-pipeline-f5-001.md:16.
- The approved candidate record includes `raw_text`, `classification`,
  `confidence`, `proposed_type`, and `proposed_authority` at
  bridge/gtkb-spec-pipeline-f5-001.md:35-40.
- The approved classification values distinguish `directive`, `constraint`,
  `preference`, `question`, and `exploration` at
  bridge/gtkb-spec-pipeline-f5-001.md:48-52.
- The approved F5 test plan requires directive and exploration classification
  tests at bridge/gtkb-spec-pipeline-f5-001.md:168-169, and later approved
  revisions preserve those tests at bridge/gtkb-spec-pipeline-f5-005.md:78-79,
  bridge/gtkb-spec-pipeline-f5-007.md:86-87, and
  bridge/gtkb-spec-pipeline-f5-009.md:99-100.
- The approved persistence revision requires raw text plus classification in
  deliberation JSON at bridge/gtkb-spec-pipeline-f5-005.md:29 and explicitly
  stores `raw_text`, `classification`, and `confidence` at
  bridge/gtkb-spec-pipeline-f5-005.md:38-40.
- The final F5 GO says the v10 content parsing and storage remain unchanged
  from earlier revisions, and its unchanged intake API tests still include
  classification at bridge/gtkb-spec-pipeline-f5-019.md:15-17 and
  bridge/gtkb-spec-pipeline-f5-019.md:62-63.
- Phase 3 v2 stores only `intake_type`, `intake_status`, `spec_id`,
  `requirement_text`, `proposed_title`, `proposed_section`, `proposed_scope`,
  `captured_at`, `confirmed_spec_id`, and `rejection_reason` at
  bridge/gtkb-phase3-implementation-005.md:14-26. It does not store
  `classification`, `confidence`, `proposed_type`, or `proposed_authority`.
- Phase 3 v2's classification tests are "matching spec returned" and "no match"
  at bridge/gtkb-phase3-implementation-005.md:158-159, not directive vs.
  exploration owner-intent classification.
- The current target repo can support enriched spec creation because
  `insert_spec()` accepts F1 fields including `type`, `authority`,
  `constraints`, `affected_by`, and `testability` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:677,
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:692,
  and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:694-698.

**Risk/impact:** F5 would still be able to capture and later confirm text, but
it would no longer preserve the evidence needed to know whether the owner was
issuing a directive, asking a question, or exploring an idea. That weakens the
core protection F5 was approved to add: preventing casual or exploratory owner
language from becoming KB specs without an auditable classification step.

It also narrows the F1-enriched spec creation path. Without `proposed_type` and
`proposed_authority`, confirmed governance, constraint, provisional, or inferred
candidates can silently collapse into default requirement/stated specs unless
Prime adds unstated logic outside the proposal.

**Required action:** Restore the approved F5 candidate contract in the Phase 3
proposal:

1. `classify_requirement()` must classify owner intent into the approved
   categories (`directive`, `constraint`, `preference`, `question`,
   `exploration`) with confidence. Existing-spec matching may remain, but it
   should be a separate advisory field such as `related_specs` or
   `target_candidates`, not a replacement for intent classification.
2. `capture_requirement()` must persist an auditable candidate payload including
   raw owner text, classification, confidence, proposed title, proposed section,
   proposed type, proposed authority, and any scope/context needed for confirm.
   `requirement_text` is acceptable only if the proposal explicitly maps it to
   the approved raw-text field.
3. `confirm_intake()` must create the spec from those proposed fields, including
   `type` and `authority` where applicable, then record `confirmed_spec_id`.
4. Tests must include directive classification, exploration/question
   classification, persisted classification/confidence, confirm-to-spec creation
   using the proposed enriched fields, and the prior redaction/list/confirm/reject
   CLI coverage.

## Conditions To Preserve

The next revision should keep the fixes already present in v2:

- F7 snapshots include lifecycle metrics, `get_summary()`, quality distribution,
  and constraint coverage.
- F7 supports current-vs-last delta with graceful no-prior behavior.
- F7 import validates `session_snapshots.data` JSON with deterministic
  skip-or-error behavior.
- F5 confirm creates a KB spec and records `confirmed_spec_id`.
- F5 adoption includes hook, settings, scaffold, doctor, upgrade, docs, CLI
  smoke tests, and redaction coverage.
- The F7 `session_snapshots` implementation must still preserve the explicit
  write contract required by the cross-check: use `INSERT OR REPLACE` or an
  equivalent latest-snapshot replacement, and test it.

## Verification

- Read the full active bridge entry and all versions for this document:
  bridge/gtkb-phase3-implementation-001.md through
  bridge/gtkb-phase3-implementation-005.md.
- Read referenced F7 approvals:
  bridge/gtkb-spec-pipeline-f7-003.md,
  bridge/gtkb-spec-pipeline-f7-005.md, and
  bridge/gtkb-spec-pipeline-f7-006.md.
- Read referenced F5 approvals and history needed for the revised claims:
  bridge/gtkb-spec-pipeline-f5-001.md,
  bridge/gtkb-spec-pipeline-f5-005.md,
  bridge/gtkb-spec-pipeline-f5-007.md,
  bridge/gtkb-spec-pipeline-f5-009.md,
  bridge/gtkb-spec-pipeline-f5-015.md,
  bridge/gtkb-spec-pipeline-f5-019.md, and
  bridge/gtkb-spec-pipeline-f5-020.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current DB,
  CLI import, scaffold, doctor, upgrade, template, docs, impact, quality, and
  constraint APIs.
- `python -m pytest tests/test_deliberations.py tests/test_impact.py tests/test_constraint_propagation.py tests/test_quality_gate.py tests/test_lifecycle_metrics.py tests/test_cli.py -q --tb=short -p no:cacheprovider`
  passed in groundtruth-kb: `194 passed, 1 warning in 38.25s`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb:
  `55 files already formatted`.

## Required Revision

Prime should revise Phase 3 once more before implementation. A GO can be
reconsidered when the F5 proposal preserves the approved intent-classification
and candidate-evidence contract while keeping the v2 fixes listed above.
