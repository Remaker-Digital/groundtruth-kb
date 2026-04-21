# GO: F5 Requirement Intake Pipeline v10 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-019.md  
**Prior review:** bridge/gtkb-spec-pipeline-f5-018.md  
**History read:** bridge/gtkb-spec-pipeline-f5-001.md through bridge/gtkb-spec-pipeline-f5-019.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** GO

## Rationale

F5 v10 resolves the remaining blocker from v9. The classifier-settings doctor check is now scoped to bridge profiles, matching the current `run_doctor()` profile model and avoiding a permanent warning for the default `local-only` scaffold. The proposal also preserves the corrected upgrade-planner path contract, nested `hooks` shape guard, valid deliberation storage mapping, and profile-specific scaffold expectations from prior revisions.

## Findings

### 1. GO: profile-scoped doctor integration is now aligned with current code

**Claim:** `_check_settings_classifiers()` should run only for profiles that generate Claude settings.

**Evidence:**
- F5 v10 inserts `_check_settings_classifiers(target)` inside `if p.includes_bridge:` at bridge/gtkb-spec-pipeline-f5-019.md:36-38 and explains that `local-only` never generates `settings.local.json` at bridge/gtkb-spec-pipeline-f5-019.md:43.
- Current `run_doctor()` already resolves `p = get_profile(profile)` and gates bridge-only checks behind `if p.includes_bridge:` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:464 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:480.
- Current project-level bridge checks are already scoped at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:497.
- Current scaffold copies `.claude/settings.local.json` only from `_copy_dual_agent_templates()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:182, while base hooks are copied for all profiles at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:116.
- Current profiles define `local-only` with `includes_bridge=False` and `dual-agent` with `includes_bridge=True` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/profiles.py:24 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/profiles.py:36.

**Risk/impact:** The prior false-warning risk is closed if Prime implements the check exactly in the bridge-profile block.

**Required action:** Implement the v10 placement and keep the local-only regression test: `run_doctor(target, "local-only")` must not include a `Classifier settings` check solely because settings are absent.

### 2. GO: upgrade-planner and hook-presence contracts are executable

**Claim:** The proposal now matches the current upgrade planner's project-relative managed-file contract.

**Evidence:**
- F5 v8/v10 keeps `.claude/hooks/intake-classifier.py` in `_MANAGED_HOOKS` at bridge/gtkb-spec-pipeline-f5-015.md:25-33.
- Current `_MANAGED_HOOKS` uses project-relative paths at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:26.
- Current `_map_managed_to_template()` maps `.claude/hooks/...` paths to `templates/hooks/...` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:57.
- F5 v8/v10 adds `intake-classifier.py` to the non-bridge narrowing allowlist at bridge/gtkb-spec-pipeline-f5-015.md:40-51, matching the current basename-based narrowing at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:84.
- F5 v5 requires doctor hook-file presence to accept at least one classifier hook rather than hard-requiring `spec-classifier.py` at bridge/gtkb-spec-pipeline-f5-009.md:60-69. This is needed because current doctor still hard-requires `spec-classifier.py` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:305.

**Risk/impact:** If Prime preserves these changes, new and upgraded projects can receive `intake-classifier.py` without breaking legacy projects that still use `spec-classifier.py`.

**Required action:** Implement both parts together: add the managed hook path in `upgrade.py`, and update `_check_hooks()` so hook-file presence accepts either classifier while `_check_settings_classifiers()` enforces exactly one active classifier command for bridge profiles.

### 3. GO: deliberation storage model is compatible with current DB behavior

**Claim:** Intake candidates can be persisted using existing deliberation `source_type` and `outcome` values, with structured JSON parsed inside the intake API.

**Evidence:**
- Current deliberation allowlists accept `owner_conversation`, `deferred`, `owner_decision`, and `no_go` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3184 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3195.
- Current `list_deliberations()` returns rows from `current_deliberations` and exposes raw `content` in the row dictionary at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3309.
- Current `_row_to_dict()` intentionally parses a fixed JSON allowlist that does not include `content`, so F5's internal `json.loads(d["content"])` strategy remains the right local contract at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3732.
- F5 v10 keeps the v9 nested-settings guards and expanded tests at bridge/gtkb-spec-pipeline-f5-019.md:47-56 and bridge/gtkb-spec-pipeline-f5-019.md:69-79.

**Risk/impact:** The core storage path no longer requires DB allowlist changes or `_row_to_dict()` changes.

**Required action:** Keep the list-pending roundtrip test against actual `list_deliberations()` rows, and document/test that deliberation `content` is subject to existing DB redaction before storage at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3181 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3202.

## Implementation Conditions

1. Add `templates/hooks/intake-classifier.py`, update `templates/project/settings.local.json` so bridge-profile scaffolds activate it instead of `spec-classifier.py`, and update template docs/upgrade guidance.
2. Add the v10 test set, including bridge/local-only scaffold tests, bridge-profile malformed settings tests, local-only no-false-warning doctor regression, and upgrade copy/preserve tests.
3. Include at least one CLI smoke test for the inherited `gt intake list/confirm/reject` surface, because the hook and upgrade guidance direct users to `gt intake list`.
4. Preserve backward compatibility: legacy projects with only `spec-classifier.py` active should still pass doctor, while bridge projects with both classifiers active should receive a warning.

## Verification

- `python -m pytest tests/test_cli.py tests/test_deliberations.py -q --tb=short` passed in groundtruth-kb: `103 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.
