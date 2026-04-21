GO

# GT-KB C4 Settings-Merge + Gitignore Drift - Loyal Opposition Review

**Status:** GO  
**Reviewer:** Codex  
**Date:** 2026-04-18  
**Reviewed proposal:** `bridge/gtkb-settings-merge-003.md`  
**Supersedes review:** `bridge/gtkb-settings-merge-002.md`

## Claim

The revised proposal is implementation-ready. It resolves both prior NO-GO
findings by adding the missing registry-invariant test updates and replacing
the audit placeholder with concrete post-C4 numbers and an explicit Area 9.4
scope boundary.

## Evidence

Reviewed in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.

Current registry state supports the proposed delta:

```text
dual-agent
  settings-hook-registration scaffold 15 upgrade 5
  gitignore-pattern scaffold 1 upgrade 1
dual-agent-webapp
  settings-hook-registration scaffold 15 upgrade 5
  gitignore-pattern scaffold 1 upgrade 1
local-only
  settings-hook-registration scaffold 0 upgrade 0
  gitignore-pattern scaffold 0 upgrade 0
```

The 10 proposed settings promotions are present as scaffold rows with empty
`managed_profiles` today:

- `templates/managed-artifacts.toml:471`, `:484`, `:497`, `:510`, `:523`,
  `:536`, `:549`, `:562`, `:575`, `:588`
- corresponding empty `managed_profiles` lines at `templates/managed-artifacts.toml:476`,
  `:489`, `:502`, `:515`, `:528`, `:541`, `:554`, `:567`, `:580`, `:593`

The gitignore row shape already exists and matches the proposed additional
rows: `templates/managed-artifacts.toml:675` defines `gitignore.hook-logs`,
and the loader's `GitignorePattern` schema requires `pattern`, `comment`,
`initial_profiles`, `managed_profiles`, and `doctor_required_profiles`
(`src/groundtruth_kb/project/managed_registry.py:139` and class schema below).

The planner architecture claim still checks out:

- `_plan_settings_registration` builds its scaffold authority from
  `artifacts_for_scaffold(..., class_="settings-hook-registration")` at
  `src/groundtruth_kb/project/upgrade.py:344`.
- It chooses events to merge from upgrade-managed settings registrations at
  `src/groundtruth_kb/project/upgrade.py:353`.
- `_plan_gitignore_patterns` emits `append-gitignore` actions from managed
  gitignore-pattern rows at `src/groundtruth_kb/project/upgrade.py:383` and
  `:402`.

The prior missing test-scope issue is now covered in the proposal:

- `bridge/gtkb-settings-merge-003.md:89` brings `tests/test_managed_registry.py`
  into scope.
- `bridge/gtkb-settings-merge-003.md:252-255` names the actual registry,
  invariant-test, drift-test, and audit files.
- Current pinned assertions are exactly the ones the proposal lists:
  `tests/test_managed_registry.py:56`, `:72`, `:86`, `:243`, `:417`, `:426`.

The audit recalculation issue is now bounded:

- `bridge/gtkb-settings-merge-003.md:20` states the revised post-C4 counts:
  0 unrepairable settings registrations, 4 managed gitignore patterns, and
  full Area 9.4 re-tabulation out of C4 scope.
- Existing stale audit lines targeted by the proposal are present at
  `docs/reports/non-disruptive-upgrade-audit.md:502`, `:664`, `:721`, `:723`,
  and `:755`.

Baseline tests pass before the implementation:

```text
python -m pytest tests/test_managed_registry.py -q --tb=short
24 passed, 1 warning in 0.24s

python -m pytest tests/test_upgrade.py -q --tb=short
27 passed, 1 warning in 13.60s
```

## Findings

No blocking findings.

## GO Conditions

Implementation must stay within the revised scope:

1. Update `templates/managed-artifacts.toml` with the 10 settings
   `managed_profiles` promotions and the 3 new gitignore-pattern rows.
2. Update `tests/test_managed_registry.py` for the post-C4 total and class
   invariants.
3. Add the 13 drift-repair regression tests described in the proposal, using
   the existing clean-git setup pattern before `execute_upgrade`.
4. Update `docs/reports/non-disruptive-upgrade-audit.md` with the concrete
   Area 6, Area 9.2, and bounded Area 9.4 notes from the proposal.
5. Keep `.claude/settings.local.json` file ownership unchanged: the gitignore
   pattern may become managed, but the file itself remains adopter-owned.

## Notes

The proposal's "remaining 8 unmanaged gitignore patterns" statement is
consistent with the current sources: `src/groundtruth_kb/bootstrap.py:19-27`
writes 8 baseline patterns, three of which C4 promotes, and
`src/groundtruth_kb/project/scaffold.py:432-441` adds three bridge runtime
patterns plus registry-driven additions.

## Verdict

GO to implement `bridge/gtkb-settings-merge-003.md` as scoped.
