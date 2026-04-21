GO

# GT-KB Upgrade Pre-Flight Checks Implementation Review

**Verdict:** GO, with required implementation conditions
**Reviewed file:** `bridge/gtkb-upgrade-pre-flight-checks-implementation-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The implementation plan may proceed. It correctly carries forward the scoped
Area 5 tranche from `gtkb-upgrade-pre-flight-checks-002.md`: in-flight bridge
awareness, malformed settings halt-on-apply, and scaffold coverage reporting.

This GO is conditional. Prime must implement the action-safety and enumerator
conditions below before filing a post-implementation verification bridge. This
review does not authorize any Agent Red source writes beyond this bridge file
and the required `bridge/INDEX.md` coordination update.

## Evidence Reviewed

- Current `UpgradeAction.action` surface is limited to `update`, `add`, `skip`,
  `merge-event-hooks`, and `append-gitignore`
  (`src/groundtruth_kb/project/upgrade.py:47-65`).
- Current `skip` behavior is not safe for WARN/INFO rows under `--force`:
  `_apply_file_actions` skips only when `action == "skip" and not force`, then
  attempts template mapping/copy behavior (`src/groundtruth_kb/project/upgrade.py:728-754`).
- `execute_upgrade` currently performs git preconditions and payload branch
  setup before `_apply_file_actions` (`src/groundtruth_kb/project/upgrade.py:647-666`),
  and `_apply_file_actions` rewrites `groundtruth.toml` whenever a manifest is
  present (`src/groundtruth_kb/project/upgrade.py:756-760`).
- The CLI calls `plan_upgrade(target)` and passes the full action list to
  `execute_upgrade(target, actions, force=force)` whenever the list is non-empty
  (`src/groundtruth_kb/cli.py:703-718`).
- Current tests intentionally prove `execute_upgrade(..., [])` updates the
  manifest version (`tests/test_upgrade.py:223-230`), so a warning/info-only
  action list must be handled explicitly if it is meant to cause zero git and
  zero writes.
- Malformed settings already surface as a dry-run `skip` action from
  `_plan_settings_registration` (`src/groundtruth_kb/project/upgrade.py:298-307`)
  and are covered by an existing dry-run regression
  (`tests/test_upgrade.py:706-718`).
- `scaffold_project` is a writer and writes across registry-backed and
  non-registry-backed surfaces (`src/groundtruth_kb/project/scaffold.py:67-145`,
  `src/groundtruth_kb/project/scaffold.py:168-213`,
  `src/groundtruth_kb/project/scaffold.py:258-355`,
  `src/groundtruth_kb/project/scaffold.py:409-443`).
- The persisted project manifest records profile and cloud provider but not
  every scaffold option such as `include_ci`, `seed_example`, provider IDs,
  integrations, or Python version (`src/groundtruth_kb/project/manifest.py:16-47`;
  CLI options at `src/groundtruth_kb/cli.py:583-590` and
  `src/groundtruth_kb/cli.py:639-653`).
- Registry APIs provide typed scaffold and upgrade surfaces, but not the
  full non-registry scaffold-output set (`src/groundtruth_kb/project/managed_registry.py:712-744`).

## Findings And Required Conditions

### C1 - Non-mutating action rows must not trigger the apply pipeline

**Severity:** P1

The implementation bridge correctly rejects WARN/INFO encoded as ordinary
`skip` actions and chooses explicit `warning` and `informational` action kinds.
That is necessary but not sufficient. If `plan_upgrade` returns only warning
or informational actions, the current CLI still sees a non-empty action list and
will call `execute_upgrade` on `--apply`. Current `execute_upgrade` performs git
preconditions, branch creation, and manifest rewrite behavior around the action
list. An `_apply_file_actions` early return alone does not satisfy the proposal's
"zero git calls / zero writes" regression.

**Required action:** The implementation must partition action rows by mutating
versus non-mutating semantics before any git or manifest write path. Acceptable
designs include:

- `execute_upgrade` itself short-circuits before `_require_git_repo` when all
  actions are `warning` / `informational`; or
- the CLI filters warning/info rows out of the action list passed to
  `execute_upgrade`, and skips apply entirely when no mutating actions remain.

The malformed-settings halt must run before any such "nothing mutating" success
path, so malformed `.claude/settings.json` still refuses apply before git.

**Required tests:**

- warning-only and informational-only apply paths perform zero git calls, write
  no files, write no manifest version, and create no receipt, even with
  `force=True`;
- mixed warning/info plus mutating actions print the warning/info rows but only
  execute mutating rows;
- `_artifact_classes_touched` excludes `warning` and `informational`.

### C2 - Malformed settings must halt apply before all git and receipt work

**Severity:** P1

The proposed `MalformedSettingsError` placement is correct: dry-run keeps the
diagnostic row, apply refuses. The current code raises git-related errors first
because `_require_git_repo` and `_require_clean_tree` are the first operations in
`execute_upgrade`.

**Required action:** Scan the planned actions for the malformed settings row and
raise `MalformedSettingsError` before `_require_git_repo`, `_require_clean_tree`,
receipt resolution, branch creation, action partitioning success, or any writes.
The CLI must catch this error and exit with code `4`.

**Required tests:**

- dry-run still prints the malformed `.claude/settings.json` row;
- apply with malformed settings raises/exits before any git call;
- the CLI exits `4` for malformed settings, distinct from existing git
  precondition code `2` and merge failure code `3`.

### C3 - Bridge in-flight parser must be latest-status-only

**Severity:** P2

The plan's parser contract is acceptable and matches the file bridge protocol.
The implementation must not scan all historical status lines, because older
`NEW`, `REVISED`, or `GO` lines under a latest `VERIFIED` or `NO-GO` would
false-positive.

**Required action:** Parse `bridge/INDEX.md` by `Document:` blocks and inspect
only the first status line after each document. Ignore header/status-table text,
blank lines, and HTML comments. Warn only for latest `NEW`, `REVISED`, or `GO`.
Remain silent for latest `VERIFIED` and `NO-GO`. Keep `--ignore-inflight-bridges`
as a deterministic suppressor.

**Required tests:** Include the historical older-status cases named in the
implementation bridge, plus a header/comment tolerance case.

### C4 - Scaffold coverage enumeration must not over-claim option-specific paths

**Severity:** P2

The proposed pure enumerator is the right shape, but the implementation must
resolve one ambiguity before coding: the current manifest does not persist every
`ScaffoldOptions` value that affects scaffold outputs. Examples include
`include_ci`, `seed_example`, `integrations`, provider IDs, and Python version.
It does persist `profile` and `cloud_provider`.

If the enumerator reports every output a default `ScaffoldOptions` run would
create, it can produce false "created by scaffold; not tracked by upgrade" rows
for projects initialized with non-default options such as `--no-include-ci`,
`--no-seed-example`, or `--integrations`.

**Required action:** Make the enumerator contract explicit and deterministic:

- enumerate only outputs that are guaranteed by persisted project state
  (`profile`, `cloud_provider`, registry rows, and unconditional scaffold
  outputs); or
- explicitly label option-dependent outputs as unknown/deferred and exclude
  them from the C2 report until the manifest records those options; or
- add a separate, reviewed manifest-schema change before using those options for
  exact coverage reporting.

Do not call `scaffold_project` against the adopter target. Tests must prove the
enumerator is read-only by comparing `git status --short` or equivalent before
and after planning.

**Required tests:** Cover `local-only`, `dual-agent`, and
`dual-agent-webapp`. Also include at least one non-default scaffold option case
or an explicit assertion that option-dependent outputs are not reported in C2.

### C5 - CLI output labels and compatibility

**Severity:** P3

`project_upgrade` currently derives display labels from `action.action.upper()`.
That will naturally produce `[WARNING]` and `[INFORMATIONAL]`, but the
implementation should lock this in with CLI tests because these rows are
adopter-facing pre-flight diagnostics.

**Required action:** Add CLI coverage for dry-run output labels, the
`--ignore-inflight-bridges` option, and the malformed-settings exit code.

## Verification Commands

Executed in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

- `python -m pytest tests/test_upgrade.py tests/test_upgrade_dispatches_by_policy.py -q --tb=short`
  - Result: `33 passed, 1 warning`
- `python -m pytest tests/test_rollback_receipts.py -q --tb=short`
  - Result: `15 passed, 1 warning`
- `python -m ruff check src/groundtruth_kb/project/upgrade.py src/groundtruth_kb/project/scaffold.py src/groundtruth_kb/cli.py tests/test_upgrade.py tests/test_rollback_receipts.py`
  - Result: `All checks passed!`

## Required Next Step

Prime may implement. The post-implementation bridge must show the conditions
above are satisfied, including tests for no git/no write behavior when apply is
fed only `warning` and `informational` rows, and a deterministic scaffold
enumerator contract that does not report option-specific false positives.
