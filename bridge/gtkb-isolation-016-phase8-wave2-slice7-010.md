NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 Revision 2

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice7-009.md`
Implementation commits: `7ae15c79`, `f3f2a88d`, `5b3c6ec8`

## Prior Deliberations

The required deliberation search was attempted before review with:

- `GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 excluded_paths python-tests`

The CLI returned no additional rows in this session. Relevant bridge context is this thread: `-008` rejected the implementation because it did not consume `manifest["excluded_paths"]` and did not implement the proposal's `python-tests.yml` target-sensitive classifier.

## Claim

NO-GO for verification. The `excluded_paths` gap is fixed and the focused tests pass, but the new `python-tests.yml` classifier does not classify the live workflow. The implementation only handles simple literal `pytest tests/...` commands, while the real workflow resolves test paths through `test_args=tests/...` outputs and runs `python -m pytest ${{ steps.paths.outputs.test_args }}`.

## Evidence

- The `-009` report says the revision fixes the `python-tests.yml` classifier and distinguishes `pytest tests/groundtruth_kb/` from other `pytest tests/...` targets: `bridge/gtkb-isolation-016-phase8-wave2-slice7-009.md:36` to `:49`.
- The implementation extracts targets with `re.findall(r"pytest\s+tests/(\S*)", content.lower())`: `scripts/rehearse/_ci_inventory.py:141`.
- The live workflow does not contain literal `pytest tests/...` invocations in the run step. It writes shard paths to `$GITHUB_OUTPUT` as `test_args=tests/unit`, `test_args=tests/multi_tenant ...`, etc.: `.github/workflows/python-tests.yml:90` to `:102`.
- The live workflow then runs `python -m pytest ${{ steps.paths.outputs.test_args }}`: `.github/workflows/python-tests.yml:108`.
- Live smoke confirms the classifier falls through:
  - Command: `python scripts/rehearse_isolation.py --phase ci --execute --output-dir C:\temp\agent-red-rehearsal-slice7-revised2-codex-verify`
  - Result: `ci ... ok`
  - `.github/workflows/python-tests.yml` row: `classification = "unclassified"`, `classification_signal = "no_classification_signal"`.
- Positive checks did pass:
  - `python -m pytest tests/scripts/test_rehearse_ci_inventory.py -q --tb=line --timeout=60` -> `24 passed in 0.53s`.
  - Full `tests/scripts/test_rehearse_*.py` suite -> `211 passed in 3.76s`.
  - `python -m ruff check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py` -> `All checks passed!`.
  - `python -m ruff format --check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py` -> `2 files already formatted`.

## Risk / Impact

The lane is supposed to inventory and classify live CI surfaces, not only synthetic fixtures. With the current classifier, the real Python CI workflow becomes an owner-decision row even though the workflow clearly targets Agent Red test paths. That inflates unclassified CI evidence and weakens the Wave 3 migration plan.

## Required Revision

1. Update `_classify_python_tests_workflow()` to recognize the live workflow's resolved test-target pattern, including `test_args=tests/...` lines and `python -m pytest ${{ steps.paths.outputs.test_args }}`.
2. Add a regression test using a fixture shaped like the live `.github/workflows/python-tests.yml` shard resolver. It should assert `classification == "adopter"` and `classification_signal == "agent_red_pytest_workflow"`.
3. Keep the existing framework-only and no-command tests.
4. Rerun the same verification set and live smoke, and include the live `python-tests.yml` row in the post-implementation report.

## Decision Needed From Owner

None.
