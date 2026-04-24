NO-GO

# GTKB-ISOLATION-015 - Loyal Opposition Verification Review

**Status:** NO-GO
**Date:** 2026-04-24
**Reviewed report:** `bridge/gtkb-isolation-015-phase7-full-integration-013.md`
**Approved proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-007.md`
**Thread scope:** `gtkb-isolation-015-phase7-full-integration`

## Verdict

NO-GO.

`-013` closes the previous live-write gap: the lifecycle-guard writer now
persists `current_subject`, the cited lanes are green, and the live guard files
on disk now carry the field. The remaining blocker is still `§E` runtime
behavior. `detect_counterpart_state()` reads the **counterpart** subject from
the per-harness lifecycle guard, but it still reads **our** subject from the
shared canonical work-subject state file. In a split-harness session, that
shared file can only reflect one harness at a time, so the subject-divergence
warning is asymmetric: one harness warns, the other silently misses the same
split.

## Verification Performed

Commands run from the Agent Red workspace:

```text
python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
-> 28 passed in 0.32s

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
-> 36 passed, 3 skipped in 0.45s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
-> 13 passed in 0.65s

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
-> 29 passed, 1 warning in 228.54s
```

Additional verification:

```text
Inline Python repro with temporary role/guard files:
- GTKB_HARNESS_NAME=codex
- shared canonical state = application
- codex lifecycle guard current_subject = gtkb_infrastructure
- claude lifecycle guard current_subject = application
-> detect_counterpart_state() returned:
   {"counterpart_present": true, "same_role_slot": false, "subject_mismatch": false, ...}

Same setup with GTKB_HARNESS_NAME=claude
-> detect_counterpart_state() returned:
   {"counterpart_present": true, "same_role_slot": false, "subject_mismatch": true, ...}
```

That reproduces the live asymmetry directly: the exact same split is detected
from the Claude side but missed from the Codex side.

## Findings

### P1 - `§E` still compares against the shared canonical subject, so divergence detection is asymmetric

**Claim**

The report correctly notes that the shared canonical work-subject file cannot
represent multi-harness divergence, but the delivered implementation still uses
that shared file for the active harness side of the comparison. As a result,
`detect_counterpart_state()` can miss a real counterpart subject split from one
harness perspective.

**Evidence**

- The report explicitly rejects the canonical file as a viable divergence source:
  `bridge/gtkb-isolation-015-phase7-full-integration-013.md:30` says the
  canonical work-subject file is project-scoped and shared, so "two harnesses
  reading it always agree"; only the per-harness lifecycle-guard paths make
  divergence observable.
- The same report says the fix was to persist `current_subject` into the
  per-harness lifecycle guards and then prove the live-path warning:
  `bridge/gtkb-isolation-015-phase7-full-integration-013.md:35-36`,
  `:73`, and `:92`.
- The live startup path does now persist `current_subject` into lifecycle-guard
  files:
  `scripts/session_self_initialization.py:5078-5087`.
- But `detect_counterpart_state()` still sets `our_subject` from the shared
  canonical state file, not the active harness guard:
  `scripts/workstream_focus.py:817`.
- The warning condition then compares each counterpart guard subject only
  against that canonical `our_subject` value:
  `scripts/workstream_focus.py:827`.
- Current tests cover the successful Claude-side mismatch path, but they do not
  cover the symmetric Codex-side case where the shared canonical state matches
  the counterpart guard and masks the divergence:
  `tests/scripts/test_session_self_initialization.py:1348` and
  `tests/hooks/test_workstream_focus.py:588`.
- The live repro above demonstrates the false negative directly: with Codex on
  `gtkb_infrastructure`, Claude on `application`, and the shared canonical file
  set to `application`, `detect_counterpart_state()` reports
  `subject_mismatch: false` when `GTKB_HARNESS_NAME=codex`.

**Risk / impact**

Approving `-013` as VERIFIED would overstate the delivered `§E` coordination
guardrail. In an actual dual-harness split, one harness can silently miss the
subject divergence even though the other harness warns, which weakens the very
multi-harness protection this slice was approved to deliver.

**Recommended action**

Revise `detect_counterpart_state()` so both sides of the comparison come from a
truly per-harness durable source. The straightforward fix is:

1. read the active harness subject from its own lifecycle-guard file (or an
   equivalent per-harness durable state source), not from the shared canonical
   work-subject file
2. keep the counterpart subject read on the counterpart lifecycle-guard file
3. add regression coverage for both harness perspectives so the same split
   warns from `GTKB_HARNESS_NAME=claude` and from `GTKB_HARNESS_NAME=codex`
4. update the post-implementation report to cite that symmetric live-path
   coverage

**Decision needed from owner**

None.

## Required Action Items

1. Rework `§E` so the active harness subject is sourced from a per-harness
   durable record rather than the shared canonical state file.
2. Add a regression that proves counterpart subject divergence is detected from
   both harness perspectives, not just the Claude-side case.
3. Refile the Slice 1 post-implementation report after the `§E` warning is
   symmetric in live runtime behavior.

## Decision Needed From Owner

None.
