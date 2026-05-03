VERIFIED

# Loyal Opposition Verification - GTKB-ISOLATION-017 Slice 4 Revision 1

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-011.md`
Role: Codex Loyal Opposition
Verdict: VERIFIED

## Review Scope

I reviewed the live bridge entry from `bridge/INDEX.md`, the selected latest
REVISED post-implementation report at `-011`, the prior NO-GO at `-010`, and
the current implementation in:

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`
- `groundtruth-kb/tests/test_upgrade_isolation.py`
- `groundtruth-kb/tests/test_upgrade.py`
- `groundtruth-kb/tests/test_preflight_checks.py`
- `groundtruth-kb/tests/test_doctor_isolation.py`

I focused on the `-010` blocking issue: check #5
(`isolation:hooks-point-to-wrappers`) was previously classified auto-fixable
without proof that all live warning modes could be fixed. The revised
implementation now reclassifies that check as needs-adopter-input and refuses
even with `--accept-migration` when it fires.

## Evidence

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:65` through
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:82` now classify the
  isolation universe as 1 hard-refuse, 4 auto-fixable, and 4
  needs-adopter-input checks, with `isolation:hooks-point-to-wrappers` in
  `_PARTITION_NEEDS_ADOPTER_INPUT`.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:93` through
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:101` remove
  `.claude/settings.json` from the isolation auto-fix surface and explain that
  check #5 was reclassified.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:486` through
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:490` map fixers only
  for the 4 auto-fixable checks. There is no check #5 fixer in the dispatcher.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1259` through
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1263` refuse
  needs-adopter-input checks when `accept_migration=True`, which gives check #5
  refusal semantics instead of a no-op auto-fix path.
- `groundtruth-kb/tests/test_upgrade_isolation.py:179` through
  `groundtruth-kb/tests/test_upgrade_isolation.py:195` verify that all current
  auto-fixable checks fire and pass post-migration.
- `groundtruth-kb/tests/test_upgrade_isolation.py:206` through
  `groundtruth-kb/tests/test_upgrade_isolation.py:239` parameterize T4 over the
  needs-adopter-input partition and explicitly trigger check #5 with an
  adopter-owned non-wrapper hook command.
- `groundtruth-kb/tests/test_upgrade_isolation.py:482` through
  `groundtruth-kb/tests/test_upgrade_isolation.py:484` assert that
  `_ISOLATION_FIXER_MAP` keys equal the auto-fixable partition.
- `groundtruth-kb/src/groundtruth_kb/cli.py:921` through
  `groundtruth-kb/src/groundtruth_kb/cli.py:932` update CLI guidance to say
  there are 4 isolation auto-fixers and that hooks-point-to-wrappers requires
  manual inspection.
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md:41` through
  `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md:49` update the
  adopter recipe's migration behavior to refuse checks #4, #5, #7, and #9 and
  run only 4 in-place auto-fixers.

## Verification Commands

```text
python -m pytest groundtruth-kb/tests/test_upgrade_isolation.py -q --tb=short
23 passed, 1 skipped, 1 warning in 9.42s

python -m pytest groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/test_preflight_checks.py -q --tb=short
102 passed, 1 skipped, 1 warning in 28.92s

python -m ruff check groundtruth-kb/src/groundtruth_kb/project/upgrade.py groundtruth-kb/src/groundtruth_kb/project/preflight.py groundtruth-kb/src/groundtruth_kb/project/rollback.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_preflight_checks.py
All checks passed!
```

## Gate Checks

- Root-boundary gate: PASS. Reviewed active files are under `E:\GT-KB`.
- Mandatory specification linkage gate: PASS. `-011` carries forward the
  proposal's specification links and owner-decision citations.
- Mandatory specification-derived verification gate: PASS. The revised tests
  now map to the revised partition: all auto-fixable checks are verified as
  fixed, and check #5 is verified as needs-adopter-input refusal.
- Command verification: PASS.

## Non-blocking Observation

Two stale explanatory strings still say "5" where the live code now has 4
auto-fixers:

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:61` and
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:84`
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md:70`

These are not blocking because the executable partition, CLI refusal behavior,
tests, and main adopter recipe steps are correct. Clean them up with the
post-VERIFIED CVR/IPR update to avoid future reviewer confusion.

## Verdict

VERIFIED. The `-010` NO-GO condition is resolved by reclassifying check #5 to
needs-adopter-input and proving the revised behavior with executed tests.

File bridge scan: 1 entry processed.
