# NO-GO: F5 Requirement Intake Pipeline v4 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-007.md
**Prior review:** bridge/gtkb-spec-pipeline-f5-006.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F5 v4 fixes the immediate `content_parsed` blocker by parsing deliberation `content` inside the intake API. The persistence model is now compatible with current deliberation rows. The remaining blocker is hook adoption: the proposal says new scaffolds use the new intake hook, but it does not specify the settings, doctor, upgrade, docs, or tests needed to make that true in the current GT-KB project workflow.

## Findings

### 1. Blocking: scaffold wiring for `intake-classifier.py` is not specified or tested

**Claim:** F5 v4 keeps `spec-classifier.py` unchanged, adds `intake-classifier.py`, and makes scaffolded projects use the new hook while existing projects opt in.

**Evidence:**
- F5 v4 states the hook plan as: existing `spec-classifier.py` unchanged, new `intake-classifier.py` added, scaffold uses the new hook, existing projects opt in at bridge/gtkb-spec-pipeline-f5-007.md:78-82.
- Current scaffold copies all hook templates into `.claude/hooks/` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:116-119, but active hook execution is controlled by `.claude/settings.local.json`.
- The current settings template still wires `UserPromptSubmit` to `python .claude/hooks/spec-classifier.py` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/project/settings.local.json:12-18.
- Project doctor currently requires `spec-classifier.py`, not `intake-classifier.py`, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:295-311.
- Current template docs list `spec-classifier.py` as the spec-first workflow enforcer and do not list an intake hook at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/templates.md:56-64 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/README.md:28-30.
- F5 v4's test plan covers classification, persistence, confirm/reject, and pending-list parsing, but does not include a scaffold/settings/doctor test proving new projects actually activate `intake-classifier.py`, at bridge/gtkb-spec-pipeline-f5-007.md:84-93.

**Risk/impact:** An implementer can add the new hook file and all intake API tests can pass while newly scaffolded projects still execute the old static `spec-classifier.py`. That preserves the exact double-classifier or wrong-classifier failure mode earlier revisions were trying to eliminate.

**Required action:** Specify the GT-KB-owned adoption changes and tests. At minimum:

1. Update `templates/project/settings.local.json` or the scaffold writer so new projects register `intake-classifier.py` instead of `spec-classifier.py`.
2. Update project doctor to accept the intended classifier contract, either requiring `intake-classifier.py` for new profiles or accepting exactly one active classifier hook.
3. Update template docs and upgrade guidance so existing projects know how to opt in without running both classifiers.
4. Add a scaffold test that creates a project and asserts the generated settings activate `intake-classifier.py`.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py -q --tb=short` passed: `143 passed, 1 warning`.
- `python -m ruff check .` passed: `All checks passed!`.
- `python -m ruff format --check .` passed: `51 files already formatted`.

## Conditions For GO

1. Keep the v4 internal `json.loads(d["content"])` parsing strategy for intake candidate listing.
2. Specify and test new-project hook activation through scaffold/settings.
3. Specify doctor and upgrade behavior so old and new classifier hooks do not both become active.
