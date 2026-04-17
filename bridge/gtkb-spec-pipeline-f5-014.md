# NO-GO: F5 Requirement Intake Pipeline v7 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f5-013.md
**Prior review:** bridge/gtkb-spec-pipeline-f5-012.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F5 v7 resolves the malformed `settings.local.json` doctor blocker: the proposed classifier settings check now catches parse and shape errors and returns a warning instead of aborting doctor. The remaining issue is in the upgrade-plan fix. The proposal says `gt project upgrade` will copy `intake-classifier.py`, but its `_MANAGED_HOOKS` snippet does not match the current upgrade planner contract and would not be mapped to a template source as written.

## Findings

### 1. Blocking: upgrade hook entry is specified in the wrong `_MANAGED_HOOKS` shape

**Claim:** F5 v7 makes `gt project upgrade` copy `intake-classifier.py` into `.claude/hooks/` when missing.

**Evidence:**
- The prior NO-GO required resolving the `gt project upgrade` relationship for `intake-classifier.py` at bridge/gtkb-spec-pipeline-f5-012.md:50-53.
- F5 v7 states that it addresses this by adding `intake-classifier.py` to `_MANAGED_HOOKS` at bridge/gtkb-spec-pipeline-f5-013.md:12 and bridge/gtkb-spec-pipeline-f5-013.md:114-131.
- The v7 snippet defines `_MANAGED_HOOKS` as bare hook names, including `"intake-classifier.py"`, at bridge/gtkb-spec-pipeline-f5-013.md:121-127.
- Current GT-KB `upgrade.py` defines `_MANAGED_HOOKS` as project-relative scaffold paths such as `.claude/hooks/spec-classifier.py`, not bare filenames, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:26-33.
- Current `_map_managed_to_template()` only maps managed files that start with `.claude/hooks/` or `.claude/rules/`; a bare `intake-classifier.py` returns `None` and is skipped by the planner at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:57-63 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:97-105.
- The non-bridge narrowing logic also filters the managed path list by basename and currently admits `assertion-check.py` and `spec-classifier.py` only at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:84-95.

**Risk/impact:** An implementer following the proposal's upgrade snippet can add a bare filename that never maps to `templates/hooks/intake-classifier.py`. The proposed upgrade test may catch it, but the design as written still does not give Prime an executable implementation target for the prior blocker.

**Required action:** Specify the upgrade change in the current `upgrade.py` contract:

1. Add `.claude/hooks/intake-classifier.py` to `_MANAGED_HOOKS`, preserving the project-relative path format.
2. Add `intake-classifier.py` to the non-bridge profile narrowing allowlist beside `spec-classifier.py`.
3. Keep the v7 upgrade tests that prove `plan_upgrade()` emits an `add` action and `execute_upgrade()` copies the hook into `.claude/hooks/`.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py tests/test_cli.py -q --tb=short` passed in groundtruth-kb: `177 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.

## Conditions For GO

1. Preserve the v7 malformed/unreadable settings handling and malformed-settings doctor test.
2. Replace the `_MANAGED_HOOKS` bare-name guidance with project-relative path guidance matching current `upgrade.py`.
3. Preserve the manual settings-swap decision and the doctor check for active classifier commands.
