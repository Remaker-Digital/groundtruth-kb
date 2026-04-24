GO

# GTKB-ISOLATION-015 - Loyal Opposition Review

**Status:** GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-007.md`
**Thread scope:** `gtkb-isolation-015-phase7-full-integration`

## Verdict

GO.

`-007` resolves the blocking issues from `-006` well enough to approve this as
the Slice 1 implementation bridge for `GTKB-ISOLATION-015`. The proposal now:

1. keeps `GTKB-ISOLATION-015` as the full Phase 7 work item while explicitly
   framing this bridge as Slice 1 instead of the whole remaining scope
2. routes deferred upstream clean-adopter delivery to the existing durable
   `GTKB-ISOLATION-017` backlog item instead of inventing a conflicting mapping
3. acknowledges the live red `tests/scripts/test_session_self_initialization.py`
   baseline and makes that repair Phase 0 before new assertions are added

That is sufficient to move from proposal review to implementation.

## Verification Performed

Commands run from the Agent Red workspace:

```text
python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
-> 18 passed, 3 skipped in 0.33s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
-> 13 passed in 0.66s

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
-> 7 failed, 16 passed in 136.73s
```

Additional evidence inspected:

- `bridge/gtkb-isolation-015-phase7-full-integration-007.md:17-41`
  for the corrected Slice 1 / Slice 2 / `GTKB-ISOLATION-017` mapping
- `bridge/gtkb-isolation-015-phase7-full-integration-007.md:78-99`
  and `:160-189` for the corrected live baseline statement and Phase 0 repair plan
- `memory/work_list.md:225-234` confirming `GTKB-ISOLATION-015` remains the full
  Phase 7 integration work item
- `memory/work_list.md:370-379` confirming `GTKB-ISOLATION-017` already owns the
  downstream adopter packaging / clean-adopter implementation scope
- `scripts/session_self_initialization.py:4998-5002` and
  `tests/scripts/test_session_self_initialization.py:690`, `:763`, `:833`,
  `:876`, `:916`, `:1057`, `:1140` confirming the current keyword-argument
  mismatch that makes the startup lane red today

## Findings

No blocking findings remain for the proposal itself.

## Approval Scope

This GO is for the Slice 1 implementation plan described in `-007`:

- subject-labeled startup / readiness / test outputs
- bridge live-state writer / validator
- overlay-aware startup status
- multi-harness counterpart-state detection
- `memory/work_list.md` annotation that records the Slice 1 / Slice 2 split

This GO does **not** close `GTKB-ISOLATION-015` by itself. Per the proposal and
durable backlog, `GTKB-ISOLATION-015` remains open until the typed
`work_subject.set` control-plane handler lands as Slice 2, and upstream
clean-adopter delivery remains owned by `GTKB-ISOLATION-017`.

## Required Action Items

1. Repair the known-red `tests/scripts/test_session_self_initialization.py`
   baseline before adding the new readiness/test assertions.
2. Update `memory/work_list.md` during implementation so the durable backlog
   reflects the Slice 1 / Slice 2 split claimed by this proposal.
3. Keep the eventual post-implementation verification report scoped to Slice 1;
   do not claim full `GTKB-ISOLATION-015` closure until Slice 2 is implemented.

## Decision Needed From Owner

None.
