NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 4 Upgrade Revision 1

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-003.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

I reviewed the live bridge entry from `bridge/INDEX.md`, the revised proposal,
the prior NO-GO at `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-002.md`,
and the current upgrade surfaces in:

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/templates/managed-artifacts.toml`

The revision resolves the prior F1-F4 defects in broad structure:

- The partition now uses the live `isolation:work-subject` check name.
- `isolation:work-list-no-product-entries` is consistently kept in
  needs-adopter-input.
- The template registry path is corrected to
  `groundtruth-kb/templates/managed-artifacts.toml`.
- T11 adds the requested partition-contract test.

## Findings

### F1 - NO-GO: Auto-Fixer Actions Have No Executable Dispatch Contract

Claim: The proposal's auto-fix execution path is not implementable against the
current `UpgradeAction` executor as written.

Evidence:

- The proposal says that when auto-fixable checks are present and
  `accept_migration=True`, "injected `UpgradeAction` rows for each
  auto-fixable check are added to the front of the action list before the
  existing payload-branch flow runs":
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-003.md:135`.
- The same proposal then says to add five per-check helper functions beside
  `_apply_file_actions()` and that each helper returns `"FIXED ..."` or
  `"SKIPPED ..."`:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-003.md:138-147`.
- The live `UpgradeAction.action` type only allows `update`, `add`, `skip`,
  `merge-event-hooks`, `append-gitignore`, `warning`, and `informational`:
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:72-80`.
- The live executor only dispatches special actions for
  `merge-event-hooks` and `append-gitignore`; all other mutating rows fall
  through to `_map_target_to_template(action.file)` and copy a registered
  template file:
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:836-861`.
- `_map_target_to_template()` maps only `FileArtifact.target_path` values from
  the managed registry:
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:214-224`.

Risk / impact: A Prime implementation following the proposal can easily create
`UpgradeAction` rows that either cannot type-check, fall through to
`SKIPPED ... no template mapping`, or copy whole templates rather than running
the intended structured fixers for `groundtruth.toml`, `.claude/settings.json`,
and `memory/release-readiness.md`. That would make T3's required "FIXED" rows
and post-fix isolation pass unverifiable or force an unreviewed executor design
change outside the proposal.

Required change: Revise the implementation plan to state the exact executor
contract for isolation fixers. Acceptable shapes include adding explicit
isolation action kinds to `UpgradeAction.action` plus `_apply_file_actions()`
dispatch branches, or not using `UpgradeAction` rows for isolation fixers and
instead invoking a typed isolation-fixer result list inside the payload branch.
The tests must assert that every auto-fixable check reaches its intended helper,
not merely that a generic result string appears.

### F2 - NO-GO: Ownership-Policy Acceptance Criterion Is Not Implemented Or Tested

Claim: The proposal adds an acceptance criterion requiring isolation fixers to
honor the existing `upgrade_policy` filter, but the implementation plan does
not define how the five direct fixers will do that and the test plan has no
coverage for it.

Evidence:

- Acceptance criterion 7 says: "Per-check auto-fixer helpers honor the existing
  `upgrade_policy` filter (no override of `preserve` / `transient` /
  `adopter-opt-in` policies)":
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-003.md:223`.
- The live policy filter is applied only through
  `_managed_file_artifacts()`, `_managed_settings_registrations()`, and
  `_managed_gitignore_patterns()`:
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:108-148`.
- The proposed fixers directly rewrite `groundtruth.toml`,
  `.claude/settings.json`, and `memory/release-readiness.md`:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-003.md:139-145`.
- The proposed tests are T1-T11 only and do not include a policy-negative
  fixture for `preserve`, `transient`, or `adopter-opt-in`:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-003.md:91`,
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-003.md:168-209`.

Risk / impact: This is a governance and data-safety boundary. Without an
explicit policy lookup and negative tests, direct isolation fixers can bypass
the same ownership matrix the upgrade path currently relies on to avoid
mutating adopter-owned or opt-in-only state.

Required change: Add a concrete policy-checking step for each auto-fixer or
for the shared isolation-fixer dispatcher, and add a test that proves a
`preserve`, `transient`, or `adopter-opt-in` registry policy prevents the
corresponding mutation while producing an actionable refusal or skip result.
If a file is intentionally outside the managed-artifact ownership matrix,
state the governing rule that authorizes the mutation and test that boundary
explicitly.

## Gate Checks

- Root-boundary gate: PASS. All proposed active files remain under `E:\GT-KB`.
- Mandatory specification linkage gate: PASS. The revised proposal cites the
  relevant Phase 9 plan, ADR/rules, owner decisions, prior slice results, and
  bridge rules.
- Prior NO-GO remediation: PARTIAL PASS. Prior F1-F4 are corrected, but the
  revised execution contract now exposes the blocking issues above.
- Specification-derived verification gate: NO-GO. The test plan still does not
  cover the proposal's own ownership-policy acceptance criterion, and it does
  not lock down the dispatch path that makes the five auto-fixers executable.

## Verdict

NO-GO. Revise before implementation. Minimum revision scope:

1. Define the exact execution/dispatch contract for the five isolation
   auto-fixers inside the payload branch.
2. Add tests proving the dispatcher invokes the intended helper for each
   auto-fixable check.
3. Define and test how the fixers honor `upgrade_policy`, or document and test
   the governing exception for files outside the managed-artifact matrix.

File bridge scan: 1 entry processed.
