# NO-GO: F5 Requirement Intake Pipeline v8 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-015.md
**Prior review:** bridge/gtkb-spec-pipeline-f5-014.md
**History read:** bridge/gtkb-spec-pipeline-f5-001.md through bridge/gtkb-spec-pipeline-f5-015.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F5 v8 fixes the prior upgrade-planner blocker: `.claude/hooks/intake-classifier.py` now matches the current project-relative `_MANAGED_HOOKS` contract, maps through `_map_managed_to_template()`, and is included in the non-bridge narrowing allowlist. The proposal still is not implementation-ready because the mandatory doctor settings guard can still abort on a syntactically valid but shape-invalid `settings.local.json`, and the active-hook behavior is not scoped cleanly across scaffold profiles.

## Findings

### 1. Blocking: classifier settings check still crashes for malformed nested `hooks`

**Claim:** The v7/v8 doctor settings check safely handles malformed project-owned settings and returns a diagnostic instead of aborting `gt doctor`.

**Evidence:**
- F5 v8 keeps the v7 doctor behavior unchanged at bridge/gtkb-spec-pipeline-f5-015.md:15-17.
- The v7 check validates only the top-level `settings` object before calling `settings.get("hooks", {}).get("UserPromptSubmit", [])` at bridge/gtkb-spec-pipeline-f5-013.md:51-60.
- That call still raises `AttributeError` when `settings.local.json` is valid JSON but contains a non-dict `hooks` value, for example `{"hooks": []}`, `{"hooks": "bad"}`, or `{"hooks": null}`. In those cases, the planned non-list `UserPromptSubmit` warning at bridge/gtkb-spec-pipeline-f5-013.md:61-68 is never reached.
- The proposal's defensive-handling list covers missing files, unreadable files, invalid JSON, non-dict top-level JSON, non-list `UserPromptSubmit`, and non-dict array entries, but it does not cover non-dict `hooks` at bridge/gtkb-spec-pipeline-f5-013.md:106-112.
- Current `run_doctor()` appends project checks directly and does not isolate exceptions thrown by individual checks at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:491-505.
- Scaffolded template files become project-owned and editable after creation at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/templates.md:101-104.

**Risk/impact:** A user-edited `settings.local.json` can still crash `gt doctor` instead of reporting the classifier activation problem. This preserves the same failure class that v7 was meant to close.

**Required action:** Validate the nested `hooks` object before reading `UserPromptSubmit`. For example:

```python
hooks = settings.get("hooks", {})
if not isinstance(hooks, dict):
    return ToolCheck(... status="warning", message="hooks is not a JSON object ...")
upsub_hooks = hooks.get("UserPromptSubmit", [])
```

Add doctor tests for at least `{"hooks": []}`, `{"hooks": "bad"}`, and `{"hooks": null}` proving `gt doctor` returns a warning ToolCheck and does not raise.

### 2. Major: scaffold activation scope is ambiguous for the default `local-only` profile

**Claim:** New projects will activate `intake-classifier.py` through `UserPromptSubmit`, while existing projects can opt in manually.

**Evidence:**
- The retained settings-template change replaces `spec-classifier.py` with `intake-classifier.py` in `UserPromptSubmit` at bridge/gtkb-spec-pipeline-f5-009.md:31-45.
- The retained scaffold activation test says a new project should have generated `settings.local.json` with `intake-classifier.py` active and `spec-classifier.py` inactive at bridge/gtkb-spec-pipeline-f5-009.md:107.
- GT-KB's CLI default scaffold profile is `local-only` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:526-533, and the docs list `local-only` as including hooks at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/cli.md:341-347.
- Current scaffold copies hook files for all profiles at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:109-119, but copies `.claude/settings.local.json` only inside `_copy_dual_agent_templates()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:182-185.
- The current settings template is the activation source for `UserPromptSubmit`, and it presently activates `spec-classifier.py` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/project/settings.local.json:12-18.

**Risk/impact:** An implementer can satisfy the dual-agent settings-template path while default `local-only` projects receive hook files but no active classifier settings. Alternatively, if the new doctor classifier check is run unconditionally, default local-only projects may get a new warning for missing `settings.local.json`. The proposal does not say which behavior is intended.

**Required action:** Specify the intended profile scope for active intake classification and test it:
- If `local-only` should activate intake, scaffold a minimal `.claude/settings.local.json` for that profile and add a local-only scaffold activation test.
- If only profiles that already generate Claude settings should activate intake, scope the doctor settings check and docs/tests to that profile set, and add a local-only test proving no false warning/regression.

## Verification

- `python -m pytest tests/test_cli.py tests/test_deliberations.py -q --tb=short` passed in groundtruth-kb: `103 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.

## Conditions For GO

1. Add nested `hooks` shape handling and tests for valid-JSON malformed settings.
2. Define and test classifier activation behavior by scaffold profile, especially `local-only` versus dual-agent profiles.
3. Preserve the v8 upgrade-planner correction: `.claude/hooks/intake-classifier.py` in `_MANAGED_HOOKS` and `intake-classifier.py` in the non-bridge narrowing allowlist.
