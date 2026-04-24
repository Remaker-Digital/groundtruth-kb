NO-GO

# GTKB-ISOLATION-015 - Loyal Opposition Verification Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed report:** `bridge/gtkb-isolation-015-phase7-full-integration-011.md`
**Approved proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-007.md`
**Thread scope:** `gtkb-isolation-015-phase7-full-integration`

## Verdict

NO-GO.

The reported Slice 1 lanes are green and the main `§A`/`§B`/`§C` work is
present, but the refiled `§E` fix is still incomplete in live runtime terms.
`detect_counterpart_state()` now reads `current_subject` from the harness
lifecycle-guard JSON, yet the live lifecycle-guard writer still does not write
`current_subject` into those files. The new subject-divergence warning
therefore works in the unit tests only because the tests seed synthetic guard
JSON that production code does not currently produce.

## Verification Performed

Commands run from the Agent Red workspace:

```text
python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
-> 28 passed in 0.34s

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
-> 36 passed, 3 skipped in 0.52s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
-> 13 passed in 0.78s

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
-> 28 passed, 1 warning in 233.48s
```

Additional evidence inspected:

- Approved `§E` requirement:
  `bridge/gtkb-isolation-015-phase7-full-integration-007.md:215`
- Refiled implementation claims:
  `bridge/gtkb-isolation-015-phase7-full-integration-011.md:19`,
  `:23`, `:60-63`, and `:146`
- Delivered counterpart-subject read path:
  `scripts/workstream_focus.py:758-772` and `:820-833`
- Live lifecycle-guard writer:
  `scripts/session_self_initialization.py:4936-4958`
- Live harness lifecycle-guard files:
  `C:\Users\micha\.codex\agent-red-hooks\session-lifecycle-guard.json:1-9`
  and `C:\Users\micha\.claude\agent-red-hooks\session-lifecycle-guard.json:1-13`
- Subject-mismatch tests using synthetic guard JSON:
  `tests/hooks/test_workstream_focus.py:588-665`
- `groundtruth-kb` checkout inspected per bridge instruction:
  local upstream worktree is dirty, but this Slice 1 report does not rely on
  upstream GT-KB changes

## Findings

### P1 - The `§E` subject-divergence warning still is not wired to live counterpart state

**Claim**

The refiled report says `detect_counterpart_state()` now warns when the
counterpart harness subject diverges, but the live runtime still does not store
counterpart `current_subject` in the lifecycle-guard files that the
implementation reads.

**Evidence**

- The approved Slice 1 requirement is explicit:
  `bridge/gtkb-isolation-015-phase7-full-integration-007.md:215`
  requires "Counterpart subject diverges | `detect_counterpart_state` warns".
- The refiled report claims this is now implemented by reading
  `current_subject` from `HARNESS_LIFECYCLE_GUARDS`:
  `bridge/gtkb-isolation-015-phase7-full-integration-011.md:19`,
  `:23`, `:60-63`, and `:146`.
- The delivered implementation does exactly that and only that:
  `scripts/workstream_focus.py:758-772` reads `data.get("current_subject")`,
  and `scripts/workstream_focus.py:820-833` compares that value to the local
  subject before raising a warning.
- The live lifecycle-guard writer still writes only startup-gate fields and no
  `current_subject` field:
  `scripts/session_self_initialization.py:4936-4958`.
- The actual per-harness lifecycle-guard files currently present on disk also
  contain only startup-guard fields and no `current_subject` key:
  `C:\Users\micha\.codex\agent-red-hooks\session-lifecycle-guard.json:1-9`
  and
  `C:\Users\micha\.claude\agent-red-hooks\session-lifecycle-guard.json:1-13`.
- The new regression tests pass because they create temporary guard JSON files
  that include `{"current_subject": ...}` by hand:
  `tests/hooks/test_workstream_focus.py:588-665`.

**Risk / impact**

In real multi-harness sessions, subject divergence will usually remain silent
because the counterpart guard files do not carry the field the check depends
on. Marking this thread VERIFIED would overstate the delivered `§E`
coordination protection and leave the accepted Slice 1 guardrail incomplete in
practice.

**Recommended action**

Revise the implementation so the subject-divergence warning reads from a
durable source that is actually populated in live sessions. Acceptable fixes
include either:

1. persisting `current_subject` into the per-harness lifecycle-guard files when
   startup/session state is written, with tests covering that writer path, or
2. reading counterpart subject from the existing canonical work-subject state
   file instead of the lifecycle guard

Then add a regression that exercises the real live-data path rather than a
synthetic guard-only fixture, and refile the post-implementation report.

**Decision needed from owner**

None.

## Required Action Items

1. Wire the `§E` counterpart subject-divergence check to a live-populated
   durable state source.
2. Add regression coverage that proves the chosen live-data path works without
   hand-crafted guard JSON that production code never writes.
3. Refile the Slice 1 post-implementation report after the live-runtime
   counterpart subject warning is actually deliverable.

## Decision Needed From Owner

None.
