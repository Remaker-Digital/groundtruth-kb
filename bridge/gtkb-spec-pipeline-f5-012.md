# NO-GO: F5 Requirement Intake Pipeline v6 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-011.md
**Prior review:** bridge/gtkb-spec-pipeline-f5-010.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F5 v6 resolves the prior dual-classifier activation blocker by making the settings-level doctor check mandatory and adding both-active tests. The proposal is still not implementation-ready because the mandatory settings parser can abort `gt doctor` on malformed project-owned configuration, and the existing-project upgrade path is underspecified relative to the current `gt project upgrade` workflow.

## Findings

### 1. Blocking: malformed settings.local.json can abort doctor instead of returning a diagnostic

**Claim:** The new mandatory doctor check safely verifies that exactly one classifier hook is active in `.claude/settings.local.json`.

**Evidence:**
- F5 v6 defines `_check_settings_classifiers()` and calls `json.loads(settings_path.read_text())` without any `JSONDecodeError`, `OSError`, or shape/type handling at bridge/gtkb-spec-pipeline-f5-011.md:45-60.
- F5 v6 defines warning/pass branches for missing settings, zero classifiers, both classifiers, and one classifier at bridge/gtkb-spec-pipeline-f5-011.md:51-95, but does not define behavior for malformed JSON.
- The check is mandatory and is called alongside `_check_hooks()` at bridge/gtkb-spec-pipeline-f5-011.md:98-100.
- Current `run_doctor()` appends project checks directly and computes the report without wrapping individual checks at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:491-505.
- Scaffolded template files become project-owned and editable after creation at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/templates.md:101-104.
- The v6 test plan covers only-intake, only-spec, both-active, and neither-active settings cases at bridge/gtkb-spec-pipeline-f5-011.md:119-124; it does not include malformed settings JSON.

**Risk/impact:** A user-edited `settings.local.json` with invalid JSON can crash `gt doctor` before it reports the classifier problem. That defeats the purpose of adding this as a diagnostic safety guard for upgraded projects.

**Required action:** Define malformed/unreadable settings behavior and test it. The doctor should catch at least `json.JSONDecodeError` and `OSError` and return a warning or failure ToolCheck that names the settings file and explains that classifier activation could not be verified.

### 2. Major: existing-project upgrade behavior is not tied to gt project upgrade

**Claim:** Existing projects can opt into the intake hook through the upgrade path.

**Evidence:**
- F5 v5, retained by v6, says existing projects opt in via the upgrade path and must ensure `intake-classifier.py` exists in `.claude/hooks/` before replacing `spec-classifier.py` in settings at bridge/gtkb-spec-pipeline-f5-009.md:46 and bridge/gtkb-spec-pipeline-f5-009.md:87-95.
- GT-KB documents `gt project upgrade` as the scaffold template refresh command at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/cli.md:403-418.
- Current upgrade planning manages hook files through `_MANAGED_HOOKS`, but that list contains `spec-classifier.py` and not `intake-classifier.py` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:26-33.
- For non-bridge profiles, upgrade planning narrows managed hooks to `assertion-check.py` and `spec-classifier.py` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:84-95.

**Risk/impact:** An implementer can update templates and docs while leaving `gt project upgrade` unable to add the new hook file to existing scaffolded projects. Existing projects then need a manual copy step that is not enforced by the product's own upgrade command.

**Required action:** Either include `intake-classifier.py` in the managed upgrade plan with tests, or explicitly state that F5 opt-in is manual-only and add docs/doctor output that tells existing projects how to copy the hook when it is missing.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py tests/test_cli.py -q --tb=short` passed in groundtruth-kb: `177 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.

## Conditions For GO

1. Add malformed/unreadable settings handling and a doctor test for it.
2. Resolve the `gt project upgrade` relationship for `intake-classifier.py`, either by managing the hook in upgrade planning or by explicitly documenting and diagnosing the manual opt-in path.
