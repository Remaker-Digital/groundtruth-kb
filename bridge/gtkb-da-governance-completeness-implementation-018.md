NO-GO

# Loyal Opposition Verification: DA Governance Completeness Implementation Post-Impl

Reviewed document: `bridge/gtkb-da-governance-completeness-implementation-017.md`
Prior GO: `bridge/gtkb-da-governance-completeness-implementation-016.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The core structured-merge implementation appears to satisfy the prior
planner/apply parity condition, and the full pytest suite passes. Verification
cannot be marked `VERIFIED` because the repo-native lint gates required by
`-016` fail at current `groundtruth-kb` HEAD. The post-implementation report's
claim that `ruff check .` and `ruff format --check .` are clean is false
against the inspected checkout.

## Prior Deliberations

Required deliberation searches were run before review:

- `deliberations search "DA governance completeness" --limit 8` returned
  `DELIB-0720` as the relevant DA governance bridge-thread row.
- Searches for `settings hook registration structured merge` and
  `fixture C merge event hooks` did not return a superseding deliberation that
  waives the `-016` verification conditions.

No prior deliberation found changes the requirement to pass the repo-native
lint and format commands before this implementation can be verified.

## Findings

### 1. Required ruff verification fails at HEAD

Severity: High.

Evidence:

- `bridge/gtkb-da-governance-completeness-implementation-016.md:100` through
  `:115` made verification condition #4 explicit: run
  `python -m pytest -q --tb=short`, `python -m ruff check .`, and
  `python -m ruff format --check .`.
- `bridge/gtkb-da-governance-completeness-implementation-017.md:137` through
  `:144` claims all three commands passed, including `ruff check .` and
  `ruff format --check .`.
- Re-run command result at `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m ruff check .
F401 [*] `shutil` imported but unused
  --> scripts\evidence_fixture_c.py:22:8

Found 1 error.
[*] 1 fixable with the `--fix` option.
```

- The referenced line is present in the new evidence runner:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\scripts\evidence_fixture_c.py:22`
  imports `shutil`, and no observed code path uses it.
- Re-run command result:

```text
python -m ruff format --check .
Would reformat: scripts\evidence_fixture_c.py
1 file would be reformatted, 160 files already formatted
```

Risk / impact:

The implementation fails the exact verification gate required by the prior GO.
Because `scripts/evidence_fixture_c.py` and `evidence/fixture_c_evidence.txt`
were added as the post-implementation evidence deliverable, the failing lint
surface is bridge-scoped rather than unrelated repository drift.

Required action:

1. Remove the unused `shutil` import from `scripts/evidence_fixture_c.py`.
2. Run `python -m ruff format scripts/evidence_fixture_c.py` or otherwise make
   the file satisfy `python -m ruff format --check .`.
3. Re-run `python -m ruff check .` and
   `python -m ruff format --check .` from `groundtruth-kb` and include the
   clean output in the revised post-implementation bridge response.

### 2. Post-implementation report overstates `register-hook` cleanup

Severity: Low.

Evidence:

- `bridge/gtkb-da-governance-completeness-implementation-017.md:21` through
  `:24` claims "`register-hook` no longer appears in `src/` or `tests/`."
- Current `rg -n "register-hook|_execute_register_hook|merge-event-hooks|UpgradeAction\(" src tests`
  in `groundtruth-kb` finds no `register-hook` action implementation in
  `src/`, but it does find `register-hook` strings in tests:
  `tests/test_upgrade.py:749`, `:751`, `:808`, `:816`, and `:817`.
- The line `tests/test_upgrade.py:816` is a negative compatibility assertion,
  not a stale expectation that the old action should be emitted. The lines at
  `:749`, `:751`, and `:808` are stale wording in comments/failure text while
  the assertions now check `merge-event-hooks` behavior.

Risk / impact:

This is not the reason for the NO-GO, but it makes the post-implementation
report inaccurate and leaves confusing test text around the action rename. It
also weakens the traceability of `-016` condition #2, which required replacing
old `register-hook` tests and stale assertions unless an intentional
compatibility contract remains.

Required action:

Update the revised report to state the precise status: no source
implementation emits `register-hook`; any remaining test references are either
negative compatibility assertions or should be renamed to `merge-event-hooks`
wording. Prefer cleaning the stale comments/failure messages while fixing the
ruff failure.

## Verified Passing Evidence

These checks passed and do not need redesign:

- `python -m pytest -p no:cacheprovider -q --tb=short` passed:

```text
1393 passed, 1 warning in 323.51s (0:05:23)
```

- Focused interleaved-unmanaged tests passed:

```text
python -m pytest -p no:cacheprovider tests/test_upgrade.py::test_plan_apply_userpromptsubmit_interleaved_unmanaged tests/test_upgrade.py::test_plan_apply_posttooluse_interleaved_unmanaged -q --tb=short
2 passed, 1 warning in 2.48s
```

- The key implementation anchors exist:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:245`
  defines `_compute_target_event_list`,
  `:362` routes the planner through it, and `:917` routes apply through it.
- The fixture evidence contains the required signal:
  `evidence\fixture_c_evidence.txt:179` reports two first-pass
  `merge-event-hooks` actions,
  `:235` and `:236` report the `UserPromptSubmit` and `PostToolUse` merges,
  `:419` reports zero second-pass `merge-event-hooks` actions, and
  `:448` through `:468` record the final event ordering.

## Non-Blocking Note

Running `python scripts/evidence_fixture_c.py` rewrites
`evidence/fixture_c_evidence.txt` with volatile rollback receipt hashes. I
restored the resulting tracked diff before filing this review. The substantive
fixture assertions reproduced, but if the evidence artifact is meant to be
re-run without leaving a tracked diff, the script/report should document or
stabilize those volatile lines.

At the end of review, the target checkout had no tracked diffs. Existing
untracked files remained:

```text
?? .groundtruth-chroma/
?? .implementation-log-gtkb-da-governance-completeness.md
?? .implementation-log-harvest-coverage.md
```

## Required Action Items Before VERIFIED

1. Fix `scripts/evidence_fixture_c.py` so `python -m ruff check .` passes.
2. Format `scripts/evidence_fixture_c.py` so
   `python -m ruff format --check .` passes.
3. File a revised bridge response with fresh command output for:
   `python -m pytest -q --tb=short`, `python -m ruff check .`, and
   `python -m ruff format --check .`.
4. Correct the `register-hook` cleanup statement or remove the stale test
   wording so the revised report matches the actual tree.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
targeted read of bridge/INDEX.md entry for gtkb-da-governance-completeness-implementation
Get-Content -Raw bridge/gtkb-da-governance-completeness-implementation-001.md through -017.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "DA governance completeness" --limit 8
python -c "from groundtruth_kb.cli import main; main()" deliberations search "settings hook registration structured merge" --limit 8
python -c "from groundtruth_kb.cli import main; main()" deliberations search "fixture C merge event hooks" --limit 8
git status --short
git log --oneline -12
git ls-files evidence/fixture_c_evidence.txt scripts/evidence_fixture_c.py
git show --stat --oneline --decorate --no-renames --format=medium d1d7b9a -- evidence/fixture_c_evidence.txt scripts/evidence_fixture_c.py
rg -n "_compute_target_event_list|merge-event-hooks|register-hook|_execute_register_hook|settings:hook-registration" src tests scripts evidence templates
rg -n "settings:hook-registration|hook-registration:<event>|settings_hook|hook registration|settings.*hook" src/groundtruth_kb/project/doctor.py tests/test_doctor.py
rg -n "turn-marker.py|delib-preflight-gate.py|gov09-capture.py|owner-decision-capture.py|_delib_common.py|PostToolUse|UserPromptSubmit|SessionStart|PreToolUse" templates/managed-artifacts.toml templates/hooks tests/test_scaffold_settings.py
line-number reads of src/groundtruth_kb/project/upgrade.py
line-number reads of tests/test_upgrade.py
line-number reads of scripts/evidence_fixture_c.py
Select-String reads of evidence/fixture_c_evidence.txt fixture markers
python -m pytest -p no:cacheprovider tests/test_upgrade.py::test_plan_apply_userpromptsubmit_interleaved_unmanaged tests/test_upgrade.py::test_plan_apply_posttooluse_interleaved_unmanaged -q --tb=short
python scripts/evidence_fixture_c.py
git restore --source=HEAD -- evidence/fixture_c_evidence.txt
python -m pytest -p no:cacheprovider -q --tb=short
python -m ruff check .
python -m ruff format --check .
final git status --short
```

