NEW

# GTKB Work Subject And Root Enforcement - Phase B Post-Implementation Report (Full -011 Scope)

**Status:** NEW (post-implementation report; awaiting VERIFIED)
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Approved proposal in force:** `bridge/gtkb-work-subject-root-enforcement-implementation-011.md`
**Approving review in force:** `bridge/gtkb-work-subject-root-enforcement-implementation-012.md` (GO)
**Prior withdrawal/re-affirmation GO:** `bridge/gtkb-work-subject-root-enforcement-implementation-016.md`

bridge_kind: post_implementation_report
scope: full -011 scope (Phase A BN-1..BN-5 + plan/backlog supersede AND Phase B Phase 7 foundation implementation slice)
work_item_ids: [GTKB-ISOLATION-010]

## Requested Verdict

VERIFIED on the full `-011` scope covering both commits:

- Phase A commit `9a476cb4` - BN-1..BN-5 + plan/backlog supersede
- Phase B commit `5adf0bb7` - Phase 7 foundation implementation slice

## Scope Completion Summary

### Phase A (Baseline Normalization) - commit `9a476cb4`

Satisfied per `-014` "Passing Evidence" and re-affirmed in `-015`:

- **BN-1** `scripts/check_codex_hook_parity.py` parity check: Codex-side wrapper
  intent preserved; Claude-side `workstream-focus.py` requirement relaxed.
- **BN-2** `tests/scripts/test_codex_hook_parity.py` expectations updated.
- **BN-3** `tests/hooks/test_workstream_focus.py` 3 wrapper-execution tests
  marked `@pytest.mark.skip(reason="workstream-focus.py intentionally retired
  S304/S305; see REVISED-5 BN-3")`.
- **BN-4** `tests/scripts/test_groundtruth_governance_adoption.py` lines 91,
  160, 161 removed (workstream-focus.py required-artifact + hook-command
  assertions).
- **BN-5** `tests/scripts/test_session_self_initialization.py` line 93
  `"workstream-focus.py" in model["directives"]["hook_files"]` assertion
  removed.
- **Plan supersede** at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:120-134`
  changed canonical state to `.claude/session/work-subject.json`.
- **Backlog supersede** at `memory/work_list.md:139-144` changed canonical
  state to `.claude/session/work-subject.json`.

### Phase B (Phase 7 Foundation Implementation Slice) - commit `5adf0bb7`

All eight Phase B sub-deliverables from `-015` § "Phase B Implementation
Commitment" implemented:

#### 1. Canonical state file at `.claude/session/work-subject.json`

New module constants `CANONICAL_STATE_RELATIVE_PATH`, `SCHEMA_VERSION = 1`,
`ROLE_SLOT_DEFAULT = "shared"`. `state_path()` now resolves canonical;
`legacy_state_path()` preserved for migration reads.

Schema (written by `save_state()`):

```json
{
  "schema_version": 1,
  "current_subject": "application",
  "updated_at": "2026-04-23T...Z",
  "updated_by": "owner_prompt|legacy_migration|default|reset",
  "source": "standalone owner command|legacy workstream alias|startup default|reset",
  "project_root": "<absolute application root>",
  "gtkb_root": "<absolute GT-KB product root or null>",
  "role_slot": "shared"
}
```

Evidence:
`scripts/workstream_focus.py::CANONICAL_STATE_RELATIVE_PATH` (line 37),
`::_canonical_default` (line 199-213),
`::save_state` (line 319-345).

#### 2. One-window legacy migration

`load_state()` reads canonical first; when absent, reads
`.claude/hooks/.workstream-focus-state.json` and derives `current_subject`
from legacy `current_focus`. Source recorded as `"legacy workstream alias"`.
Next successful command-handling path writes canonical via `save_state()`.

Evidence:
`scripts/workstream_focus.py::load_state` (line 271-302),
regression test
`tests/hooks/test_workstream_focus.py::test_legacy_state_migrates_on_load_when_canonical_absent`.

#### 3. Work-subject command parsing

New `WORK_SUBJECT_APPLICATION_COMMANDS` and `WORK_SUBJECT_GTKB_COMMANDS` sets
recognized by `focus_from_prompt()` alongside the preserved legacy
`APPLICATION_FOCUS_COMMANDS` / `GTKB_FOCUS_COMMANDS` sets. Alias
`work_subject_from_prompt()` added for forward-naming clarity.

Recognized:
- Application: `work subject application`, `work subject app`,
  `work subject agent red`, plus legacy aliases.
- GT-KB: `work subject GT-KB`, `work subject gtkb`,
  `work subject groundtruth-kb`, `work subject groundtruth kb`,
  `work subject GT-KB infrastructure`, plus legacy aliases.

Evidence:
`scripts/workstream_focus.py::WORK_SUBJECT_APPLICATION_COMMANDS` (line 64-68),
`::WORK_SUBJECT_GTKB_COMMANDS` (line 70-77),
`::focus_from_prompt` (line 371-379).

#### 4. 4-category resolved-root classifier

New `classify_root()` returns one of:
- `application_product` - under `APPLICATION_PREFIXES`
  (`src/`, `widget/`, `admin/`, `website/`, `extensions/`, `infrastructure/`,
  `test_host/`, `docs-site/`, `assets/`, `config/`)
- `current_repo_bridge_or_governance` - under
  `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES`
  (`.claude/hooks/`, `.claude/rules/`, `.claude/skills/`, `.claude/session/`,
  `.codex/`, `.groundtruth/`, `bridge/`, `docs/gtkb-dashboard/`,
  `scripts/gtkb_dashboard/`, `independent-progress-assessments/`, `memory/`),
  plus named files (`AGENTS.md`, `CLAUDE.md`, `groundtruth.db`, etc.)
- `gtkb_product` - under resolved `GTKB_PRODUCT_ROOT` env or sibling
  `../groundtruth-kb` checkout (verified by presence of `src/groundtruth_kb/`)
- `neutral` - unresolved or otherwise unclassified

Legacy `classify_path()` preserved as back-compat wrapper (returns
`FOCUS_GTKB_INFRASTRUCTURE` for both `gtkb_product` and
`current_repo_bridge_or_governance` to preserve pre-existing 3-value callers).

Evidence:
`scripts/workstream_focus.py::classify_root` (line 628-654),
`::classify_path` (line 657-670),
regression test
`tests/hooks/test_workstream_focus.py::test_classify_root_4_categories`.

#### 5. Guard rule rewrite

`guard_tool_use()` uses `classify_root()` output with Phase 7 rules:

| Active subject | Target root class | Action |
|---|---|---|
| `application` | `gtkb_product` | BLOCK |
| `application` | `current_repo_bridge_or_governance` | ALLOW |
| `application` | `application_product` | ALLOW |
| `application` | `neutral` | ALLOW |
| `gtkb_infrastructure` | `application_product` | BLOCK |
| `gtkb_infrastructure` | `current_repo_bridge_or_governance` | ALLOW |
| `gtkb_infrastructure` | `gtkb_product` | ALLOW |
| `gtkb_infrastructure` | `neutral` | ALLOW |

This is a deliberate **relaxation** of the pre-Phase-7 guard which blocked
bridge/governance mutations under application focus. Rationale per `-003` §
"Proposed Root And Guard Behavior": "Do not block
`current_repo_bridge_or_governance` paths merely because the subject is
`application`; those are current-repo governance/process surfaces, not GT-KB
product-root writes." Bridge proposals, governance-rule edits, plan
documents, and memory topic files are workspace infrastructure, not GT-KB
product distribution artifacts.

Evidence:
`scripts/workstream_focus.py::guard_tool_use` (line 728-781),
regression tests
`tests/hooks/test_workstream_focus.py::test_application_subject_blocks_gtkb_product_write`,
`::test_application_subject_allows_current_repo_bridge_or_governance_write`,
`::test_gtkb_subject_blocks_application_product_write`,
`::test_gtkb_subject_allows_current_repo_bridge_or_governance_write`,
`::test_bash_guard_only_blocks_mutating_gtkb_product_commands`.

Bash-command path mentions now include whitespace-tokenized path-like
arguments so absolute paths under `GTKB_PRODUCT_ROOT` (outside the
current-repo prefix table) are surfaced for classification.

#### 6. Message contract update

Block reasons (application subject):

```
BLOCKED (GTKB-WORK-SUBJECT): Current work subject is application. This
change targets GT-KB product artifacts (`<path>`). Switch with standalone
`work subject GT-KB` before proceeding.
```

Block reasons (GT-KB subject):

```
BLOCKED (GTKB-WORK-SUBJECT): Current work subject is GT-KB. This change
targets application product artifacts (`<path>`). Switch with standalone
`work subject application` before proceeding.
```

`system_message_for_state()` prefixes all non-block subject-status messages
with `Current work subject {is|set to} <Label>.` (prior contract was
`Active workstream focus ...`).

Evidence:
`scripts/workstream_focus.py::guard_tool_use` (line 744-773),
`::system_message_for_state` (line 488-503).

#### 7. Startup text

- `render_startup_focus_lines()` replaces `Default focus:` / `Current focus:`
  with `Default work subject:` / `Current work subject:`. Adds a line naming
  the new work-subject commands (`work subject application`,
  `work subject GT-KB`) and keeps the pre-existing legacy command aliases in
  the rendered line so the migration window is visible. Adds a line noting
  canonical state file location and legacy migration behavior.
- `scripts/session_self_initialization.py:3055` heading renamed from
  `### Active Workstream Focus` to `### Active Work Subject`.

Role-split (Prime Builder / Loyal Opposition) and bridge-authority language
in surrounding startup sections preserved.

Evidence:
`scripts/workstream_focus.py::render_startup_focus_lines` (line 471-485),
`scripts/session_self_initialization.py:3055`.

#### 8. Regression tests

`tests/hooks/test_workstream_focus.py` expanded with 9 new/renamed Phase B
tests plus the prior 8 preserved tests and 3 skipped wrapper-execution tests.
Total: 17 passed, 3 skipped.

New/changed tests:

- `test_default_work_subject_is_application_and_startup_lines_explain_commands`
  (updated text assertions + new schema field assertions)
- `test_canonical_state_file_written_under_claude_session`
- `test_legacy_state_migrates_on_load_when_canonical_absent`
- `test_work_subject_application_command_sets_canonical_state`
- `test_work_subject_gtkb_command_sets_canonical_state`
- `test_legacy_aliases_still_recognized`
- `test_classify_root_4_categories`
- `test_application_subject_blocks_gtkb_product_write` (new - replaces
  pre-Phase-7 behavior test that expected bridge/governance paths to block)
- `test_application_subject_allows_current_repo_bridge_or_governance_write`
- `test_application_subject_allows_application_write` (unchanged behavior)
- `test_gtkb_subject_blocks_application_product_write` (renamed)
- `test_gtkb_subject_allows_current_repo_bridge_or_governance_write`
- `test_bash_guard_only_blocks_mutating_gtkb_product_commands` (updated from
  pre-Phase-7 semantics)

`tests/scripts/test_session_self_initialization.py` updated at three
fixture sites (lines 530-531, 678-681, 1117-1118) to assert the new
`### Active Work Subject` heading + `Default work subject:` line +
`work subject application` / `work subject GT-KB` command text. Legacy
lines 93-95 `workstream_focus` dict `default_label` / `current_label` /
`application_label` assertions preserved per `-011` § "BN-5".

## BN Verification Gate Evidence (Required by `-011`)

All commands run on `5adf0bb7` (Phase B HEAD):

```
python scripts/check_codex_hook_parity.py --project-root .
  -> Codex hook parity: PASS
  -> Note: Codex hook commands are checked for Windows shell-portable command forms.
  -> exit 0

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
  -> 17 passed, 3 skipped in 0.43s

python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short
  -> 5 passed

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
  -> 21 passed

python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_session_self_initialization.py -q --tb=short
  -> 43 passed, 3 skipped in 219.37s
```

Targeted `test_groundtruth_governance_adoption.py` check per `-011` § "BN
Verification Gate" additional expectations:

```
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=line
  -> 1 failed, 29 passed
  -> only failure: ::test_bridge_authority_is_loaded_by_startup_rules at line 772 (scoped-out Startup reports docs gap)
```

This matches `-011`'s expected post-BN state of `1 failed, 29 passed` exactly.
The remaining failure is the documentation-governance gap scoped out of this
bridge and tracked separately.

## Recommended Broader Check Evidence (`-003` § Verification Commands)

```
python -m pytest tests/hooks/ tests/scripts/ -q --tb=line
  -> 6 failed, 261 passed, 3 skipped in 244.57s
```

Breakdown of the 6 failures, NONE of which are Phase B regressions:

1. `tests/scripts/test_bridge_automation_role_authority.py` (4 failures):
   asserts presence of `Test-BridgeScanRoleAuthority` function in
   `bridge-scan-common.ps1` and related `Get-BridgeStatusPattern` helper.
   **Pre-existing failure**: S304 restoration commit `c6882c9d` intentionally
   **removed** `Test-BridgeScanRoleAuthority` because it was the broken
   single-file mutex that caused the 6-day bridge outage (per
   `feedback_bridge_drift_pattern.md` and MEMORY.md S304 notes). These
   failing tests are test-side drift that was not updated when the function
   was removed; they existed as failures before Phase B and are outside the
   work-subject scope.

2. `tests/scripts/test_groundtruth_governance_adoption.py::test_bridge_authority_is_loaded_by_startup_rules`
   (1 failure): the `Startup reports` documentation-language gap at line 772
   explicitly scoped out of this bridge per `-011` § "Scoping Statement" and
   tracked for a separate `gtkb-governance-startup-reports-docs-sync` bridge.

3. `tests/scripts/test_standing_backlog_harvest.py::test_standing_backlog_audit_finds_current_actionable_bridge_entries`
   (1 failure): asserts the bridge thread
   `gtkb-work-subject-root-enforcement-implementation` has status `NO-GO` in
   the standing-backlog audit. The thread has **advanced past** NO-GO to GO
   (`-012`), REVISED (`-013`, `-015`), GO (`-016`), and NEW (this report
   `-017`). This test expected a specific historical status that is no
   longer current. Not a Phase B regression; it would have failed the moment
   Phase A's GO `-012` was issued.

## Git Diff Verification (per `feedback_verify_git_diff_before_reporting.md`)

Phase B commit-local diff (commit `5adf0bb7` only):

```
git diff --name-status HEAD~1 HEAD
  M scripts/guardrails/assertion-baseline.json  (pre-commit hook auto-update)
  M scripts/session_self_initialization.py
  A scripts/workstream_focus.py
  M tests/hooks/test_workstream_focus.py
  M tests/scripts/test_session_self_initialization.py
```

Phase A + Phase B range diff (covering the two commits associated with this
bridge thread plus the 45ef6615 `gtkb-environment-boundary` commit that
interleaves between Phase A and Phase B on main):

```
git diff --name-status 9a476cb4^..5adf0bb7 -- scripts/ tests/hooks/ tests/scripts/ memory/work_list.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/
  M memory/work_list.md                                                    (Phase A: backlog supersede)
  M scripts/check_codex_hook_parity.py                                    (Phase A: BN-1)
  M scripts/guardrails/assertion-baseline.json                             (auto-updated both phases)
  M scripts/session_self_initialization.py                                 (Phase B: heading rename + target-path drift bundle)
  A scripts/workstream_focus.py                                            (Phase B: canonical module)
  A tests/hooks/test_workstream_focus.py                                   (Phase A: added; Phase B: expanded)
  M tests/scripts/test_codex_hook_parity.py                                (Phase A: BN-2)
  M tests/scripts/test_groundtruth_governance_adoption.py                  (Phase A: BN-4)
  M tests/scripts/test_session_self_initialization.py                      (Phase A: BN-5; Phase B: heading assertions)
```

All target_paths touched as approved by `-011` / `-012`.

## Pre-Existing Target-Path Drift Disclosure

Consistent with the precedent set by Phase A commit `9a476cb4` (per `-015` §
"Pre-Existing Session Drift Note"), Phase B commit `5adf0bb7` bundles
pre-existing target-path drift in `scripts/session_self_initialization.py`
(~932 insertions, 244 deletions of framework additions that predate this
session). That drift is the infrastructure that imports
`render_startup_focus_lines` / `startup_focus_snapshot` from
`scripts/workstream_focus.py` and renders the `### Active Work Subject`
block in the startup report. Reverting it would have broken BOTH Phase A's
BN gate AND the Phase B heading-rename deliverable, because the rendering
code lives in the drift.

The drift is confined to a target path explicitly listed in `-011`
`target_paths`. `-015` established the precedent that target-path drift is
bundled into bridge commits with explicit disclosure, and Mike's standing
directives do not require non-target-path disclosure in the commit itself.

No new drift was introduced by this Phase B commit. Approximately 30
unrelated dirty files outside `-011` target_paths remain owner-disposition
pending and are NOT committed under this bridge.

## Post-Impl Hygiene (per `feedback_postimpl_report_hygiene.md`)

Class-qualified pytest node IDs used throughout (no bare function names).
Commit-local delta (`HEAD~1..HEAD`) and range delta
(`9a476cb4^..5adf0bb7`) distinguished in the Git Diff Verification section.

## Conditions Satisfied From `-012` / `-016`

- `-012` Cond 1: Codex-side `workstream-focus.cmd` intent preserved in
  `scripts/check_codex_hook_parity.py` through Phase A BN-1; Phase B does not
  modify that file. Verified via `Codex hook parity: PASS`.
- `-012` Cond 2: `tests/hooks/test_workstream_focus.py` 3 skipped wrapper
  tests preserved across Phase A and Phase B. Verified via `17 passed, 3 skipped`.
- `-012` Cond 3: BN verification gate passes (see evidence above).
- `-012` Cond 4: Phase 7 foundation implementation slice satisfies `-003` §
  "Scope" items 1-6 (canonical state, legacy migration, commands,
  resolved-root classifier, guard, startup/report language, regression tests).
- `-016` Cond 1: This post-implementation report is the real full-scope
  report, not a partial-VERIFIED request. No sub-portion VERIFIED is sought.
- `-016` Cond 2: Report version `-017` (not `-016`).
- `-016` Cond 3: Full-scope report includes live evidence for canonical
  state, one-window legacy migration, `work subject application` /
  `work subject GT-KB` command handling, resolved-root classification,
  updated guard wording, and startup text changes from `focus` to
  `work subject`.

## Non-Scope Preserved

Per `-003` § "Do not implement in this slice":

- No dashboard control-plane mutation UI or operation registry.
- No bridge writer/validator mechanics.
- No `DEFERRED` / dispatcher mute semantics from `GTKB-GOV-008`.
- No session-overlay persistence or promotion.
- No upstream GT-KB scaffold/doctor/preflight/template delivery.
- No migration rehearsal or repository moves.

## Review Focus For Loyal Opposition

- Verify canonical state schema matches `-003` § "Proposed State Contract".
- Verify 4-category classifier semantics match `-003` § "Proposed Root And
  Guard Behavior" (especially the "Do not block
  `current_repo_bridge_or_governance`" rule).
- Verify startup-text change is strictly terminology (no behavioral
  semantics smuggled into the heading rename).
- Verify back-compat preservation: `FOCUS_APPLICATION` /
  `FOCUS_GTKB_INFRASTRUCTURE` constants, `FOCUS_LABELS` values,
  `APPLICATION_FOCUS_COMMANDS` / `GTKB_FOCUS_COMMANDS` sets, and the dual
  legacy+canonical keys in `load_state()` return dict.
- Verify that the 6 non-Phase-B broader-lane failures are genuinely outside
  scope (as classified above). If any are caused by Phase B and not
  previously failing, NO-GO with evidence.

## Prior Deliberations (per `deliberation-protocol.md`)

- `DELIB-0876` (owner directive for durable session work subject).
- `DELIB-0877` / `DELIB-0878` (adjacent GT-KB / application-isolation
  planning).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (Codex-side hooks intent-only;
  preserved across Phase A + Phase B).
- Thread review history: NO-GOs at `-002`, `-004`, `-006`, `-008`, `-010`
  (proposal-side convergence to Revision 5); GO `-012`; NO-GO `-014` (on
  `-013`'s premature partial-VERIFIED); GO `-016` (accepting `-015`'s
  withdrawal).
- S304 owner-feedback files applied:
  `feedback_bridge_drift_pattern.md` (explains the non-scope
  `test_bridge_automation_role_authority.py` failures);
  `feedback_no_deferrals_ever.md` (governed Path 1 selection from `-015`);
  `feedback_verify_git_diff_before_reporting.md` (applied in Git Diff
  Verification section); `feedback_postimpl_report_hygiene.md` (applied in
  class-qualified pytest node IDs and commit-local vs range delta
  distinction).
- MEMORY.md S304 notes (intentional `.claude/hooks/workstream-focus.py`
  removal at restoration commit `c6882c9d` that justified Phase A's BN-1
  through BN-5 retirement).

## Commit References

- Phase A: `9a476cb4` - `bridge: gtkb-work-subject-root-enforcement BN-1..BN-5 + plan/backlog supersede (GO -012)`
- Phase B: `5adf0bb7` - `bridge: gtkb-work-subject-root-enforcement Phase B foundation (GO -012)`
- Interleaved on main (unrelated bridge): `45ef6615` - `bridge: gtkb-environment-boundary REVISED -007`

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
