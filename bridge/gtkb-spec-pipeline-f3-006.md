# GO: F3 Spec Quality Gate v3 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f3-005.md
**Prior review:** bridge/gtkb-spec-pipeline-f3-004.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** GO

## Rationale

F3 v3 addresses the prior persistence blockers. It adds session attribution to the proposed per-spec score table, explicitly places `spec_quality_scores` in the export/import path, and requires a roundtrip test for persisted quality history.

## Findings

No blocking findings.

**Evidence:**
- The revised schema stores `session_id` and keys scores by `(spec_id, spec_version, session_id)` at bridge/gtkb-spec-pipeline-f3-005.md:20-34.
- The revised API returns quality history including `session_id` at bridge/gtkb-spec-pipeline-f3-005.md:49-60.
- The proposal now requires adding `spec_quality_scores` to `export_json()` and `_IMPORTABLE_TABLES`, and validates `flags` JSON on import, at bridge/gtkb-spec-pipeline-f3-005.md:39-45.
- Current GT-KB export and import are both explicit allowlists, so the proposal targets the right integration points: E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2565-2585 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317-334.
- The revised test plan includes persistence with session attribution, export/import roundtrip, and malformed `flags` handling at bridge/gtkb-spec-pipeline-f3-005.md:62-71.

## Implementation Conditions

1. Add `spec_quality_scores` to schema creation, export scope, and import allowlist in the same change.
2. Validate `flags` as a JSON list during import, with deterministic skip-or-error behavior matching the chosen import mode.
3. Include the proposed persistence and export/import roundtrip tests before marking implementation complete.

## Verification

- `python -m pytest tests/test_db.py tests/test_deliberations.py tests/test_assertions.py -q --tb=short` passed: `168 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.
- `python -m ruff format --check src/ tests/` passed: `39 files already formatted`.
