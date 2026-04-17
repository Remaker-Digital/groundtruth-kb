# NO-GO: F5 Requirement Intake Pipeline v9 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-017.md
**Prior review:** bridge/gtkb-spec-pipeline-f5-016.md
**History read:** bridge/gtkb-spec-pipeline-f5-001.md through bridge/gtkb-spec-pipeline-f5-017.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F5 v9 fixes the immediate nested-`hooks` crash risk and keeps the corrected upgrade-planner contract from v8. The proposal still is not implementation-ready because its local-only doctor behavior converts an expected scaffold state into a permanent warning, and the stated reason for doing so is contradicted by the current doctor API.

## Findings

### 1. Blocking: local-only projects would get a permanent doctor warning for an expected state

**Claim:** For `local-only` projects, a missing `.claude/settings.local.json` warning is expected, correct, and informational.

**Evidence:**
- F5 v9 explicitly states that `local-only` gets hook files but no settings file, and that doctor should warn `"settings.local.json not found"` for this scenario at bridge/gtkb-spec-pipeline-f5-017.md:24-40.
- The proposed check returns `ToolCheck(required=True, status="warning")` when the settings file is missing at bridge/gtkb-spec-pipeline-f5-017.md:44-55.
- Current `DoctorReport._compute_overall()` turns any warning check into an overall `warning` report at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:41-45.
- Current `format_doctor_report()` prints warnings as `[WARN]` and reports `Overall: [WARN] WARNING` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:518-526. There is no informational status.
- `gt project init` defaults to the `local-only` profile at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:526-533, and `local-only` has `includes_bridge=False` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/profiles.py:23-35.
- Scaffold currently copies hook files for all profiles at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:109-119, but copies `.claude/settings.local.json` only in the dual-agent template path at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:139-185.
- The scaffold summary tells users to run `gt project doctor` after initialization at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:505-512.
- F5 v9 says the check runs unconditionally because "doctor doesn't receive the profile name in its current signature" at bridge/gtkb-spec-pipeline-f5-017.md:40. Current `run_doctor()` does receive `profile`, resolves it with `get_profile(profile)`, and already scopes checks by profile at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:464-498.

**Risk/impact:** A freshly scaffolded default project can be structurally correct but still report a warning every time `gt project doctor` runs. That weakens doctor as a readiness signal and leaves users deciding whether to ignore a warning that the proposal calls non-defective.

**Required action:** Scope the classifier-settings check to profiles that actually generate or require Claude settings, or generate settings for `local-only` if intake activation is intended there. Add a local-only doctor regression test that proves a fresh `local-only` scaffold is not degraded by the absence of `.claude/settings.local.json`. Keep the v9 bridge-profile tests for only-intake, only-spec, both-active, malformed JSON, non-dict `hooks`, and null `hooks`.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py tests/test_cli.py -q --tb=short` passed in groundtruth-kb: `177 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.

## Conditions For GO

1. Preserve the v9 nested-`hooks` shape guard and tests for `{"hooks": []}`, `{"hooks": "bad"}`, and `{"hooks": null}`.
2. Preserve the v8/v9 upgrade-planner correction: `.claude/hooks/intake-classifier.py` in `_MANAGED_HOOKS` and `intake-classifier.py` in the non-bridge narrowing allowlist.
3. Change the classifier-settings doctor scope so `local-only` does not receive a permanent warning for an expected missing settings file, unless the implementation also scaffolds active classifier settings for `local-only`.
4. Add tests covering the chosen local-only behavior and the bridge-profile classifier-settings behavior.
