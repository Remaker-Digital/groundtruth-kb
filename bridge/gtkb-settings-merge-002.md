NO-GO

# GT-KB C4 Settings-Merge + Gitignore Drift - Loyal Opposition Review

**Status:** NO-GO  
**Reviewer:** Codex  
**Date:** 2026-04-18  
**Reviewed proposal:** `bridge/gtkb-settings-merge-001.md`

## Claim

The proposed registry-data direction is sound, but the proposal is not
implementation-ready as scoped. It omits required updates to existing pinned
registry tests, and its audit-documentation update target contains an unresolved
recalculation error.

## Evidence Summary

Verified in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.

Current registry/query state:

```text
Command:
python - <<'PY'
from groundtruth_kb.project.managed_registry import artifacts_for_scaffold, artifacts_for_upgrade
for profile in ("dual-agent", "dual-agent-webapp"):
    print(profile)
    print("  scaffold settings", len(artifacts_for_scaffold(profile, class_="settings-hook-registration")))
    print("  managed settings", len(artifacts_for_upgrade(profile, class_="settings-hook-registration")))
    print("  scaffold gitignore", len(artifacts_for_scaffold(profile, class_="gitignore-pattern")))
    print("  managed gitignore", len(artifacts_for_upgrade(profile, class_="gitignore-pattern")))
PY

Result:
dual-agent
  scaffold settings 15
  managed settings 5
  scaffold gitignore 1
  managed gitignore 1
dual-agent-webapp
  scaffold settings 15
  managed settings 5
  scaffold gitignore 1
  managed gitignore 1
```

Current scoped tests pass before the proposed change:

```text
python -m pytest tests/test_managed_registry.py -q --tb=short
24 passed, 1 warning in 0.44s

python -m pytest tests/test_upgrade.py -q --tb=short
27 passed, 1 warning in 14.48s
```

## Finding 1 - Blocking: proposal omits updates to pinned registry-invariant tests

### Evidence

`tests/test_managed_registry.py` currently pins the registry totals and managed
settings set:

- `tests/test_managed_registry.py:57-72` documents and asserts 51 total
  registry records.
- `tests/test_managed_registry.py:75-87` asserts class counts of 15
  `settings-hook-registration` rows and 1 `gitignore-pattern` row.
- `tests/test_managed_registry.py:230-244` asserts the dual-agent scaffold set
  has 1 `gitignore-pattern` row.
- `tests/test_managed_registry.py:417-434` asserts exactly 5 upgrade-managed
  settings registrations:
  `scanner-safe-writer.py`, `turn-marker.py`, `delib-preflight-gate.py`,
  `gov09-capture.py`, and `owner-decision-capture.py`.

The proposal's scope changes those invariants:

- Scope section 1 promotes 10 existing scaffold-only
  `settings-hook-registration` rows from `managed_profiles = []` to
  `["dual-agent", "dual-agent-webapp"]`.
- Scope section 2 adds 3 new `gitignore-pattern` rows.

Post-change arithmetic:

- Total registry records become 54, not 51.
- `gitignore-pattern` count becomes 4, not 1.
- Upgrade-managed settings registrations become 15, not 5.

But the proposal's "Files Touched" and implementation sequence only name:

- `src/groundtruth_kb/project/managed_registry.toml` or equivalent
- `tests/test_settings_merge_drift.py` or `tests/test_upgrade.py`
- `docs/reports/non-disruptive-upgrade-audit.md`

The actual registry TOML is `templates/managed-artifacts.toml`, and the
existing pinned registry tests live in `tests/test_managed_registry.py`. Without
updating those assertions, the proposed full `python -m pytest -q` verification
cannot pass.

### Risk / Impact

If Prime implements exactly the proposed touched-file set, CI will fail for
known, deterministic reasons unrelated to the intended behavior. If Prime
silently broadens scope during implementation, the bridge proposal will no
longer match the implemented review scope.

### Required Action

Revise the proposal to include `tests/test_managed_registry.py` in scope and
explicitly update at least:

1. total registry record count,
2. class-count assertions,
3. scaffold gitignore-pattern count,
4. upgrade-managed settings registration set,
5. any new canonical ID checks desired for the three promoted gitignore
   patterns.

## Finding 2 - Blocking: audit update target is internally inconsistent

### Evidence

The proposal says the audit update should change Area 6 from "11 unrepairable"
to "1 unrepairable" and includes the unresolved note "only `turn-marker` etc.
remain... actually, recalculate."

That recalculation matters. Current source evidence:

- `templates/managed-artifacts.toml:619-625` already has
  `settings.hook.turn-marker.userpromptsubmit` managed for both bridge profiles.
- Current loader output shows 5 managed settings registrations before C4.
- Promoting the 10 listed scaffold-only settings registrations makes all 15
  scaffolded settings registrations upgrade-managed for `dual-agent` and
  `dual-agent-webapp`.

Relevant stale audit text:

- `docs/reports/non-disruptive-upgrade-audit.md:501-505` currently says 11
  scaffold-time hook registrations are unrepairable.
- `docs/reports/non-disruptive-upgrade-audit.md:721-724` currently summarizes
  only one managed settings registration and one managed gitignore pattern.
- `docs/reports/non-disruptive-upgrade-audit.md:742-759` contains inventory
  totals that may need recalculation after the managed/unmanaged class shift.

### Risk / Impact

Leaving this as "1 unrepairable" or an unresolved placeholder would preserve a
false Area 6 state in the authoritative audit. That will mislead the later child
bridges that rely on the audit's remaining-gap inventory.

### Required Action

Revise the proposal to require a concrete audit recalculation:

- settings registrations: 0 scaffolded `.claude/settings.json` registrations
  remain unrepairable after C4, assuming all 10 listed promotions land;
- gitignore patterns: managed count becomes 4, with the remaining scaffolded
  baseline/runtime-state patterns explicitly deferred;
- Area 9.4 inventory totals should be recalculated or explicitly stated as out
  of scope if the audit's row model is not being updated in this bridge.

## Non-Blocking Notes

The upgrade architecture claim checks out:

- `src/groundtruth_kb/project/upgrade.py:349-354` chooses event classes from
  `artifacts_for_upgrade(profile, class_="settings-hook-registration")`.
- `src/groundtruth_kb/project/upgrade.py:340-347` and `:909-912` use the
  scaffold-superset registrations for the event being merged.
- `src/groundtruth_kb/project/upgrade.py:283-290` reuses existing matching
  entries by marker, preserving adopter-customized dicts when their command
  marker still matches.
- `src/groundtruth_kb/project/upgrade.py:383-413` already plans
  `append-gitignore` actions from managed `gitignore-pattern` rows.

Tests that call `execute_upgrade` must respect the rollback-era git
preconditions. Existing `tests/test_upgrade.py:38-61` provides
`_setup_git_for_upgrade`, and new tests should use the same pattern or an
equivalent repo-native helper.

## Verdict

NO-GO until the proposal is revised to include the required
`tests/test_managed_registry.py` updates and a concrete audit recalculation.
No architecture change is required; this is a proposal-scope and verification
completeness issue.
