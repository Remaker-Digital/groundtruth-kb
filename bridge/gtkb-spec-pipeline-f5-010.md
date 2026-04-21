# NO-GO: F5 Requirement Intake Pipeline v5 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-009.md
**Prior review:** bridge/gtkb-spec-pipeline-f5-008.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F5 v5 resolves the new-project activation path: it names the settings template update, explains why both hook files may exist on disk, and adds a scaffold activation test. The remaining blocker is the existing-project safety guard. The revision still does not make the "do not run both classifiers" rule a required, tested doctor/settings behavior.

## Findings

### 1. Blocking: both-active classifier detection is specified as optional and untested

**Claim:** F5 v5 addresses the prior hook-adoption blocker and prevents old and new classifier hooks from both becoming active.

**Evidence:**
- The prior review required doctor and upgrade behavior so old and new classifier hooks do not both become active at bridge/gtkb-spec-pipeline-f5-008.md:30-33 and bridge/gtkb-spec-pipeline-f5-008.md:43-45.
- F5 v5 correctly changes new-project settings to activate `intake-classifier.py` instead of `spec-classifier.py` at bridge/gtkb-spec-pipeline-f5-009.md:31-45.
- F5 v5 says both hook files will be present on disk and active hook execution is determined by `settings.local.json` at bridge/gtkb-spec-pipeline-f5-009.md:50-54.
- The proposed doctor behavior only requires at least one classifier hook file to be present, and says a separate advisory check "can warn" if both classifiers appear in `UserPromptSubmit` settings at bridge/gtkb-spec-pipeline-f5-009.md:58-73. That is not a required behavior.
- The revised tests cover scaffold activation and doctor acceptance for only-intake, only-spec, and neither-present cases, but do not test a `settings.local.json` with both classifier commands active at bridge/gtkb-spec-pipeline-f5-009.md:107-108.
- Current GT-KB doctor only checks hook file presence and does not inspect `.claude/settings.local.json` activation at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:295-321.
- Current settings structure permits multiple `UserPromptSubmit` commands, as shown by `spec-classifier.py` and `scheduler.py` both being active in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/project/settings.local.json.

**Risk/impact:** An implementation can pass the proposed tests while an upgraded project has both `spec-classifier.py` and `intake-classifier.py` active in `UserPromptSubmit`. That preserves the double-classifier failure mode the proposal is intended to eliminate.

**Required action:** Make the settings-level classifier check mandatory and test it. At minimum:
1. Define doctor behavior for active classifier commands in `.claude/settings.local.json`: exactly one of `spec-classifier.py` or `intake-classifier.py` may appear in `UserPromptSubmit`.
2. Add a doctor test where both classifier commands are active and the result is a warning or failure.
3. Add a doctor test where both hook files exist on disk but only `intake-classifier.py` is active, proving scaffolded projects pass despite copied fallback templates.

## Verification

- `python -m pytest tests/test_cli.py tests/test_deliberations.py -q --tb=short` passed in groundtruth-kb: `103 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.

## Conditions For GO

1. Keep the v5 settings-template and scaffold activation plan.
2. Require exactly one active classifier hook in `UserPromptSubmit` and test the both-active failure/warning case.
3. Preserve the v4 internal `json.loads(d["content"])` parsing strategy and valid deliberation outcome mapping.
