# NO-GO: F5 Requirement Intake Pipeline v2 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-003.md  
**Prior review:** bridge/gtkb-spec-pipeline-f5-002.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The revised capture-confirm-record direction is much closer to the GroundTruth vision and correctly moves candidate persistence into GT-KB-owned artifacts. The proposal is still not implementation-ready because it relies on deliberation `source_type` and `outcome` values that the current API rejects, without specifying the required allowlist changes or tests.

## Findings

### 1. Blocking: proposed deliberation values are invalid in the current API

**Claim:** Requirement candidates can be persisted as deliberations with `source_type='requirement_candidate'` and `outcome='pending'`, then updated to `confirmed` or `rejected`.

**Evidence:**
- F5 v2 specifies `source_type='requirement_candidate'` and `outcome='pending'` at bridge/gtkb-spec-pipeline-f5-003.md:15 and bridge/gtkb-spec-pipeline-f5-003.md:21-49.
- Its tests assert `requirement_candidate`, `confirmed`, and `rejected` behavior at bridge/gtkb-spec-pipeline-f5-003.md:132-139.
- Current `insert_deliberation()` only allows `source_type` values `lo_review`, `proposal`, `owner_conversation`, `report`, `session_harvest`, and `bridge_thread` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3184-3193.
- Current `insert_deliberation()` only allows outcomes `go`, `no_go`, `deferred`, `owner_decision`, `informational`, or `None` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3195-3197.
- Direct verification in a temporary DB produced: `ValueError: Invalid source_type 'requirement_candidate'; must be one of ['bridge_thread', 'lo_review', 'owner_conversation', 'proposal', 'report', 'session_harvest']`.

**Risk/impact:** The first persistence call in the proposed flow fails before any candidate can be listed, confirmed, or rejected.

**Required action:** Choose one:
- Extend the deliberation allowlists to include `requirement_candidate`, `pending`, `confirmed`, and `rejected`, with tests and docs; or
- Reuse existing values, for example `source_type='owner_conversation'` plus structured content/status fields, and adjust filters/tests accordingly.

### 2. Major: hook replacement artifact is contradictory

**Evidence:**
- The change table says `templates/hooks/spec-classifier.py` is updated to call the intake pipeline while existing hook users continue to work at bridge/gtkb-spec-pipeline-f5-003.md:16.
- The hook section then introduces a new `templates/hooks/intake-classifier.py` that replaces `spec-classifier.py` and says old `spec-classifier.py` remains for backward compatibility at bridge/gtkb-spec-pipeline-f5-003.md:53-72.

**Risk/impact:** It is unclear whether implementation should mutate the existing hook template, add a new hook, or do both. That ambiguity can break existing scaffold users or leave upgraded projects wired to the old static reminder.

**Required action:** Specify the exact artifact plan: keep `spec-classifier.py` unchanged and add `intake-classifier.py`, or change `spec-classifier.py` in place with a documented compatibility behavior. Include scaffold/upgrade tests for the chosen path.

## Verification

- `python -m pytest tests/test_deliberations.py -q --tb=short` passed: `69 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.

## Conditions For GO

1. Make the candidate deliberation status model valid against current GT-KB validation.
2. Add tests for the exact accepted `source_type` and `outcome` values.
3. Resolve whether the hook is an in-place replacement or a new opt-in template.
