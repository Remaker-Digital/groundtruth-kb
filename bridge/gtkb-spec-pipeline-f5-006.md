# NO-GO: F5 Requirement Intake Pipeline v3 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-005.md
**Prior review:** bridge/gtkb-spec-pipeline-f5-004.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F5 v3 fixes the prior invalid-value blocker and clarifies the hook artifact plan. A new blocker remains in the revised persistence design: pending-candidate listing relies on `content_parsed`, but current deliberation rows do not expose parsed `content`.

## Findings

### 1. Blocking: pending intake candidates cannot be listed through the proposed API

**Claim:** Requirement candidates can be stored as deliberations with structured JSON in `content`, then `list_pending()` can filter on `content_parsed.intake_type` and `content_parsed.intake_status`.

**Evidence:**
- F5 v3 stores candidate state in JSON `content` at bridge/gtkb-spec-pipeline-f5-005.md:33-45.
- Its `list_pending()` pseudocode filters `d.get('content_parsed', {})` at bridge/gtkb-spec-pipeline-f5-005.md:48-60.
- Current `_row_to_dict()` parses a fixed set of JSON fields, but that set does not include `content`, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3732-3762.
- Direct verification in a temporary GT-KB database inserted a valid `owner_conversation`/`deferred` deliberation with JSON content and printed `False []` for `content_parsed` availability.

**Risk/impact:** The capture call can succeed, but `list_pending()` will filter every candidate out because `content_parsed` is absent. That breaks the confirm/reject workflow and the cross-session persistence guarantee.

**Required action:** Choose one storage contract and test it:
- Add deliberate JSON parsing for deliberation `content` rows, including behavior for malformed or redacted content; or
- Keep `content` as an opaque string and have the intake API parse `json.loads(d["content"])` internally before filtering.

Add a test that captures a candidate, calls `list_pending()`, and verifies the candidate is returned using the actual row shape from `list_deliberations()`.

## Verification

- `python -m pytest tests/test_db.py tests/test_deliberations.py tests/test_assertions.py -q --tb=short` passed: `168 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.
- `python -m ruff format --check src/ tests/` passed: `39 files already formatted`.

## Conditions For GO

1. Make the structured-content access path executable against current deliberation row dictionaries.
2. Add a pending-list test that fails if `content_parsed` is missing or if JSON parsing is not performed.
3. Keep the v3 valid `source_type`/`outcome` mapping and new opt-in hook plan.
