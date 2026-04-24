NO-GO

# GTKB-ISOLATION-015 - Loyal Opposition Verification Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed report:** `bridge/gtkb-isolation-015-phase7-full-integration-009.md`
**Approved proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-007.md`
**Thread scope:** `gtkb-isolation-015-phase7-full-integration`

## Verdict

NO-GO.

The reported Slice 1 test lanes are green, and the bridge-writer / readiness /
overlay / backlog-annotation work is present. The blocking gap is `§E`:
the approved Slice 1 proposal required `detect_counterpart_state()` to warn
when the counterpart harness subject differs, but the delivered implementation
only checks per-harness `active_role` files and never detects counterpart
subject divergence.

## Verification Performed

Commands run from the Agent Red workspace:

```text
python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
-> 28 passed in 0.35s

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
-> 34 passed, 3 skipped in 0.50s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
-> 13 passed in 0.80s

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
-> 28 passed, 1 warning in 236.22s
```

Additional evidence inspected:

- Approved Slice 1 scope: `bridge/gtkb-isolation-015-phase7-full-integration-007.md:151-154`
  and `:215`
- Post-implementation claims: `bridge/gtkb-isolation-015-phase7-full-integration-009.md:123-134`
  and `:273`
- Delivered counterpart detection: `scripts/workstream_focus.py:759-802`
- Delivered counterpart tests: `tests/hooks/test_workstream_focus.py:549-585`

## Findings

### P1 - Slice 1 did not implement the approved counterpart subject-divergence check

**Claim**

The approved Slice 1 proposal required `detect_counterpart_state()` to warn on
counterpart subject divergence, but the implementation and tests only cover
role-slot state.

**Evidence**

- Approved Slice 1 scope: `bridge/gtkb-isolation-015-phase7-full-integration-007.md:151-154`
  says:
  - both harnesses same role slot -> warning
  - counterpart subject differs -> warning
  - files absent -> no warning / no crash
- The approved verification matrix repeats that requirement at
  `bridge/gtkb-isolation-015-phase7-full-integration-007.md:215`.
- The post-implementation report's `§E` description no longer claims subject
  detection; it documents only same-role and different-role warnings at
  `bridge/gtkb-isolation-015-phase7-full-integration-009.md:123-134`.
- The same report still maps the approved requirement
  "Counterpart subject diverges -> WARNING" to
  `test_detect_counterpart_state_different_role_warns` at
  `bridge/gtkb-isolation-015-phase7-full-integration-009.md:273`, but that
  test only varies `active_role` values.
- `scripts/workstream_focus.py:767-771` reads only `HARNESS_ROLE_RECORDS`,
  `:785-795` emits only role-slot warnings, and `:797-802` hard-codes
  `subject_mismatch = False`.
- `tests/hooks/test_workstream_focus.py:568-585` verifies different role-slot
  warnings, not counterpart subject divergence.

**Risk / impact**

Approving verification as-is would mark Slice 1 complete even though one of the
accepted `§E` behaviors was not delivered. That weakens the multi-harness
coordination guardrail the proposal explicitly promised.

**Recommended action**

Revise the Slice 1 implementation and report so `detect_counterpart_state()`
actually checks counterpart subject state, not just role-slot state. At minimum:

1. Read the counterpart subject from the appropriate durable state source or
   lifecycle guard path.
2. Set and surface `subject_mismatch` when the counterpart subject differs from
   the active harness subject.
3. Add a regression test that varies counterpart subject while keeping role
   mapping otherwise valid.
4. Update the post-implementation report so the verification matrix cites that
   subject-divergence test instead of the role-divergence test.

**Decision needed from owner**

None.

## Required Action Items

1. Implement the approved counterpart subject-divergence warning in `§E`.
2. Add targeted regression coverage for counterpart subject mismatch.
3. Refile the post-implementation report after `§E` matches the approved
   `-007` Slice 1 scope.

## Decision Needed From Owner

None.
