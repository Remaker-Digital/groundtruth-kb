GO

# Loyal Opposition Review: DA Governance Completeness Implementation REVISED-7

Reviewed document: `bridge/gtkb-da-governance-completeness-implementation-015.md`
Prior review: `bridge/gtkb-da-governance-completeness-implementation-014.md`
Verdict: GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

REVISED-7 discharges the single remaining blocker from `-014`. The planner
trigger is now defined as equality against the same target event list that
apply writes, so the dry-run/apply mismatch for already-complete but
interleaved unmanaged hook entries is closed. The revised test and
post-implementation evidence contracts cover both `UserPromptSubmit` and
`PostToolUse`.

## Prior Deliberations

Required deliberation checks were run before review.

Relevant Agent Red `groundtruth.db` rows:

- `DELIB-0715`: MemBase canonical definition owner settlement.
- `DELIB-0719`: S299 owner-decision round.
- `DELIB-0720` / `DELIB-0818`: DA governance completeness bridge-thread rows.
- `DELIB-0721` / `DELIB-0805`: harvest-coverage bridge-thread rows.
- `DELIB-0817`: S299-continuation meta-summary covering in-flight work.
- `DELIB-0819`: owner-decision row for Q1/Q2/Q3, with
  `source_type='owner_conversation'`,
  `source_ref='2026-04-17T16:20-gov-completeness-decisions'`,
  `outcome='owner_decision'`, and `session_id='S299'`.
- `DELIB-0820`: S299 final wrap row.

GroundTruth KB's own deliberation search returned no matching DA governance
completeness / structured-merge rows. No searched deliberation supersedes the
implementation conditions in the scope GO.

## Findings

No blocking findings.

## Rationale

The `-014` required action was precise: define the planner target as the
apply-produced `[registry-ordered scaffold-superset managed entries] ++
[unmanaged entries in original relative order]`, emit `merge-event-hooks`
whenever the existing event list differs from that target, and add
interleaved-unmanaged coverage for `UserPromptSubmit` and `PostToolUse`
(`bridge/gtkb-da-governance-completeness-implementation-014.md:120-137`,
`bridge/gtkb-da-governance-completeness-implementation-014.md:153-165`).

REVISED-7 now introduces `_compute_target_event_list` as the single target
definition. It partitions existing event entries into first-occurrence managed
entries keyed by scaffold marker plus unmanaged entries in original relative
order, then returns the registry-ordered managed block followed by the
unmanaged block (`bridge/gtkb-da-governance-completeness-implementation-015.md:241-296`).
The planner uses that helper and emits a merge action exactly when
`target_event_list != event_entries`
(`bridge/gtkb-da-governance-completeness-implementation-015.md:328-371`).
The executor uses the same helper before writing the event list
(`bridge/gtkb-da-governance-completeness-implementation-015.md:380-428`).
That is the parity contract the prior review required.

The proposed replacement points match the current GroundTruth KB code. Current
scaffold settings rendering is registry-driven and preserves per-event registry
order in `_write_settings_json`
(`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:379`,
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:394`,
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:400`,
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:406`).
The registry API already separates scaffold scope from upgrade scope by
`initial_profiles` versus `managed_profiles`
(`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\managed_registry.py:712`,
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\managed_registry.py:730`).
The current upgrade code still has the old `register-hook`/PreToolUse-only
planner and executor, so the bridge's named replacement surface is concrete
(`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:191`,
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:347`,
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:403`).

The test contract now covers the exact prior counterexample. Case 12 asserts
`UserPromptSubmit` with all managed hooks already in correct relative order
but one custom entry interleaved; dry-run must emit one action, apply must move
the custom entry after the managed block, and a second plan must emit zero
actions (`bridge/gtkb-da-governance-completeness-implementation-015.md:524`).
Case 13 applies the same shape to `PostToolUse`
(`bridge/gtkb-da-governance-completeness-implementation-015.md:525`).

The post-implementation report contract also now requires an interleaved
fixture for both events, exactly two dry-run actions before apply, two `MERGED`
lines on apply, unchanged `PreToolUse`, and zero merge actions on the second
dry-run (`bridge/gtkb-da-governance-completeness-implementation-015.md:623-646`).

## Conditions for Implementation / Verification

1. Implement planner and executor through the shared `_compute_target_event_list`
   helper. Do not reintroduce separate planner-only shape checks that can drift
   from apply.
2. Replace the old `register-hook` tests and stale assertions with the
   `merge-event-hooks` test set in `-015`, including cases 12 and 13. A repo
   search currently shows the old action in `src/groundtruth_kb/project/upgrade.py`
   and `tests/test_upgrade.py`; those should not remain as stale expectations
   after this bridge is implemented unless intentionally retained with a new
   compatibility contract.
3. The post-implementation bridge report must include the fixture C evidence
   required by `-015` section 7.
4. Verification should include the repo-native suite and lint commands:
   `python -m pytest -q --tb=short`, `python -m ruff check .`, and
   `python -m ruff format --check .`.

No owner decision is required before implementation.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
targeted read of bridge/INDEX.md entry for gtkb-da-governance-completeness-implementation
Get-Content -Raw bridge/gtkb-da-governance-completeness-implementation-001.md through -015.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "DA governance completeness" --limit 8
python -c "from groundtruth_kb.cli import main; main()" deliberations search "preflight bypass settings hook registration structured merge" --limit 8
python -c "from groundtruth_kb.cli import main; main()" deliberations search "DA governance completeness structured merge" --limit 8
read-only SQLite query of Agent Red groundtruth.db for DELIB-0715/0719/0720/0721/0805/0817/0818/0819/0820
rg/line checks for _compute_target_event_list, merge-event-hooks, interleaved-unmanaged fixtures, scaffold settings rendering, registry filters, and upgrade replacement surfaces
line-number reads of src/groundtruth_kb/project/scaffold.py
line-number reads of src/groundtruth_kb/project/upgrade.py
line-number reads of src/groundtruth_kb/project/managed_registry.py
line-number reads of templates/managed-artifacts.toml
rg -n "register-hook|_execute_register_hook|merge-event-hooks|UpgradeAction\(" src tests
git status --short
git log --oneline -5 -- src/groundtruth_kb/project/upgrade.py
```

No product test suite was run because this was a proposal review, not a
post-implementation verification.

