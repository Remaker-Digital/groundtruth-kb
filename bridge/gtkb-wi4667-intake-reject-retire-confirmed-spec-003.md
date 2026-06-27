NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-27T01-11-11Z-prime-builder-B-fdf00f
author_model: Claude Sonnet 4.6
author_model_version: claude-sonnet-4-6
author_model_configuration: explanatory; mode=auto; auto-dispatch
author_metadata_source: bridge-auto-dispatch-env
bridge_kind: implementation_report
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4667-REJECT-RETIRE-SPEC
Work Item: WI-4667
target_paths: ["groundtruth-kb/src/groundtruth_kb/intake.py", "groundtruth-kb/tests/test_intake.py"]

Document: gtkb-wi4667-intake-reject-retire-confirmed-spec
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-wi4667-intake-reject-retire-confirmed-spec-002.md (GO)
Recommended commit type: fix

## Summary

Implemented `reject_intake` retirement of the auto-confirmed spec stub
(`confirmed_spec_id`) when an intake is rejected, as required by
GOV-SPEC-CAPTURE-TRANSPARENCY-001. The fix adds a single-site retirement
call with an idempotency guard after the existing deliberation archiving step.

No direct `groundtruth.db` mutation occurs in this implementation. The changes
add calls to `db.update_spec()` inside `intake.py` — this is normal runtime
application API usage, not a schema change or direct SQLite write during the
implementation step.

## Specification Links

- GOV-SPEC-CAPTURE-TRANSPARENCY-001 — capture lifecycle must reflect approve/reject decisions
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — tests must be derived from linked specs
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — implementation proposals must cite all relevant specs
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge file authority and audit trail requirements

## Prior Deliberations

- bridge/gtkb-wi4667-intake-reject-retire-confirmed-spec-001.md (NEW proposal)
- bridge/gtkb-wi4667-intake-reject-retire-confirmed-spec-002.md (GO)

## Owner Decisions / Input

This report covers a governed implementation under project authorization
PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4667-REJECT-RETIRE-SPEC (cited in
the proposal). No additional owner decisions are required.

## Requirement Sufficiency

Existing requirements sufficient — GOV-SPEC-CAPTURE-TRANSPARENCY-001 specifies
the approve/reject lifecycle; WI-4667 scopes the implementation gap.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/intake.py` — `reject_intake` now reads
  `confirmed_spec_id` from the deliberation content after archiving and calls
  `db.update_spec(..., status="retired")` when the spec exists and is not
  already retired. Idempotency guard: skips the update if status is already
  `"retired"`.

- `groundtruth-kb/tests/test_intake.py` — two new tests added to `TestF5CoreIntake`:
  - `test_reject_intake_retires_confirmed_spec` (test 35): verifies the full
    capture → confirm → reject lifecycle; asserts spec status becomes `"retired"`.
  - `test_reject_intake_pending_has_no_spec_to_retire` (test 36): verifies
    rejecting a pending (not yet confirmed) intake is a safe no-op.

## Spec-to-Test Mapping

| Specification | Test |
|---|---|
| GOV-SPEC-CAPTURE-TRANSPARENCY-001 (reject lifecycle) | `test_reject_intake_retires_confirmed_spec` |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (no-op path) | `test_reject_intake_pending_has_no_spec_to_retire` |

## Verification Evidence

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_intake.py -x -q
```

Result:

```
40 passed, 1 warning in 19.97s
```

All 40 tests pass including the 2 new regression tests.

## Code Quality

```
ruff check groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/tests/test_intake.py
# All checks passed!

ruff format --check groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/tests/test_intake.py
# 2 files already formatted
```

## Acceptance Criteria Check

Per the GO verdict (-002):

- [x] `reject_intake` reads `confirmed_spec_id` from deliberation content and
  retires the spec via `db.update_spec(..., status="retired")`.
- [x] Idempotency guard: only retires when status is not already `"retired"`.
- [x] Regression test for full lifecycle (capture → confirm → reject → retired).
- [x] Regression test for safe no-op when no `confirmed_spec_id` is present.
- [x] All existing intake tests continue to pass.
