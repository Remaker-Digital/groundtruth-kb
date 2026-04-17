# GO: F6 Project Scaffold Generator v2 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f6-003.md  
**Prior review:** bridge/gtkb-spec-pipeline-f6-002.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** GO

## Rationale

The revision resolves the main risks: it avoids the existing `ProjectProfile` name, integrates with the existing scaffold path instead of creating a parallel one, gates enriched-authority behavior behind F1, and chooses a safe generated-spec authority policy. The proposal is implementation-ready as a phased scaffold extension.

## Findings

### 1. Existing scaffold integration is now coherent

**Evidence:**
- Current scaffold entry point is `scaffold_project(options)` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:24-41.
- F6 v2 integrates optional spec generation into that flow after project initialization and also exposes standalone `gt scaffold specs` at bridge/gtkb-spec-pipeline-f6-003.md:16-46.
- The current conflicting profile type is `groundtruth_kb.project.profiles.ProjectProfile` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/profiles.py:9-20.
- F6 v2 renames the spec-generation model to `SpecScaffoldConfig` at bridge/gtkb-spec-pipeline-f6-003.md:55-65.

**Risk/impact:** Low. The naming and integration conflicts from v1 are resolved.

**Required action:** Add `spec_scaffold` as an optional field on scaffold options without changing default `gt project init` behavior.

### 2. Authority policy is safe for generated templates

**Evidence:**
- F6 v2 Phase A uses existing schema only and tags generated specs as `scaffold-generated` at bridge/gtkb-spec-pipeline-f6-003.md:68.
- Phase B uses `authority='inferred'` until owner confirmation promotes a spec to `stated` at bridge/gtkb-spec-pipeline-f6-003.md:70-80.
- The test plan includes Phase B authority confirmation coverage at bridge/gtkb-spec-pipeline-f6-003.md:124-131.

**Risk/impact:** The proposal avoids treating AI-generated template text as owner intent before review.

**Required action:** Keep owner confirmation as an explicit versioned `update_spec()` operation when F1 exists.

## Verification

- `python -m pytest tests/test_db.py -q --tb=short` passed: `25 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.

## Conditions For Implementation

1. Implement Phase A against existing schema only.
2. Preserve `dry_run=True` behavior for generator review before writes.
3. On non-empty KBs, skip existing governance handles and never overwrite existing specs.
4. Defer Phase B authority and F3 validation until those feature contracts are implemented.
