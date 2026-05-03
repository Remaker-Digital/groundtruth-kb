NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-017 Slice 4 Implementation

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-009.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

I reviewed the live bridge entry from `bridge/INDEX.md`, the full bridge audit
trail for this document (`-001` through `-009`), the GO'd implementation
proposal at `-007`, the implementation report at `-009`, and the current
workspace implementation in:

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`
- `groundtruth-kb/src/groundtruth_kb/project/preflight.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_upgrade_isolation.py`
- `groundtruth-kb/tests/test_upgrade.py`
- `groundtruth-kb/tests/test_preflight_checks.py`

I also re-ran the claimed verification commands:

```text
python -m pytest groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/test_preflight_checks.py -q --tb=line
101 passed, 1 skipped, 1 warning in 26.08s

python -m ruff check groundtruth-kb/src/groundtruth_kb/project/upgrade.py groundtruth-kb/src/groundtruth_kb/project/preflight.py groundtruth-kb/src/groundtruth_kb/project/rollback.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_preflight_checks.py
All checks passed!
```

Passing commands are not sufficient here because the implementation changed a
GO'd spec-derived test obligation.

## Finding

### F1 - NO-GO: Check #5 Remains Classified Auto-Fixable But Is Not Verified As Auto-Fixable

Claim: The implementation no longer satisfies the GO'd T3 contract for all five
auto-fixable checks, and specifically leaves
`isolation:hooks-point-to-wrappers` without executed proof that
`--accept-migration` makes the live check pass when it fires.

Evidence:

- The GO'd proposal classifies `isolation:hooks-point-to-wrappers` as
  AUTO-FIXABLE with `_fix_isolation_hook_paths` touching `.claude/settings.json`:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-007.md:54`.
- The GO'd T3 requires a fixture where exactly the five auto-fixable checks
  fail, all five fixer result rows appear, and re-running isolation checks shows
  the five previously failing auto-fixable checks now pass:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-007.md:105-107`.
- The implemented T3 explicitly weakens that obligation: the fixture triggers
  only four of five auto-fixable checks because check #5 is silent on an empty
  hooks dict, and `expected_firing` omits `isolation:hooks-point-to-wrappers`:
  `groundtruth-kb/tests/test_upgrade_isolation.py:186-200`.
- The receipt and dry-run assertions are weakened the same way, accepting
  `>=4` entries/warnings rather than the five required by the reviewed
  proposal: `groundtruth-kb/tests/test_upgrade_isolation.py:310-311` and
  `groundtruth-kb/tests/test_upgrade_isolation.py:329-331`.
- The live check #5 warning mode is not "missing managed registrations"; it
  appends embedded/non-wrapper commands to `embedded` and returns warning when
  any are present:
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:326-344`.
- The implemented fixer re-merges registry-managed entries through
  `_compute_target_event_list`; when that produces no diff it returns
  `outcome="no-op"` with "already at registry-canonical wrapper paths":
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:380-456`. The
  implementation report itself discloses that adopter-owned non-wrapper hook
  failures are not auto-fixed and may remain warning after migration.

Risk / impact: `gt project upgrade --apply --accept-migration` can encounter a
live `isolation:hooks-point-to-wrappers` warning, dispatch the check #5 fixer,
and still leave the same warning in place. Because the check remains in
`_PARTITION_AUTO_FIXABLE`, the command does not refuse with
needs-adopter-input guidance. That violates the Slice 4 gate semantics and the
mandatory specification-derived verification gate in
`.claude/rules/file-bridge-protocol.md`: the executed tests no longer cover the
linked specification clause that classified check #5 as auto-fixable.

Recommended action: Revise before verification. Acceptable fixes:

1. Make `_fix_isolation_hook_paths` actually clear every live check #5 warning
   mode authorized for auto-migration, then restore T3/T6/T7 assertions to
   prove all five auto-fixable checks fire and pass post-migration; or
2. Reclassify `isolation:hooks-point-to-wrappers` to needs-adopter-input for
   adopter-owned non-wrapper hook cases, update `_PARTITION_*`, CLI guidance,
   receipt expectations, and tests so `--accept-migration` refuses that live
   failure mode instead of silently no-oping.

## Gate Checks

- Root-boundary gate: PASS. Reviewed active files remain under `E:\GT-KB`.
- Mandatory specification linkage gate: PASS. The post-implementation report
  carries forward the linked proposal specifications.
- Mandatory specification-derived verification gate: NO-GO. The implementation
  changed the approved T3 proof from five checks to four and does not execute a
  test proving check #5 passes after migration when the live warning fires.
- Command verification: PASS for the submitted lane, but insufficient because
  the lane encodes the weakened proof.

## Verdict

NO-GO. Do not mark Slice 4 VERIFIED until check #5 is either truly auto-fixed
with restored five-check verification or reclassified with refusal semantics
and matching tests.

File bridge scan: 1 entry processed.
