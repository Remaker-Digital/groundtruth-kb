VERIFIED

# GTKB-ISOLATION-015 - Loyal Opposition Verification Review

**Status:** VERIFIED
**Date:** 2026-04-24
**Reviewed report:** `bridge/gtkb-isolation-015-phase7-full-integration-015.md`
**Approved proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-007.md`
**Thread scope:** `gtkb-isolation-015-phase7-full-integration`

## Verdict

VERIFIED.

`-015` closes the last `§E` blocker from `-014`. The live implementation now
sources the active harness subject from its own lifecycle-guard file first,
keeps the canonical-state fallback only for pre-upgrade compatibility, and the
Codex-side asymmetry repro now warns correctly. The delivered code, tests, and
live guard files match the report's claims closely enough to verify Slice 1.

## Verification Performed

Commands run from the Agent Red workspace:

```text
python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
-> 28 passed in 0.35s

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
-> 37 passed, 3 skipped in 0.54s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
-> 13 passed in 0.81s

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
-> 29 passed, 1 warning in 247.66s
```

Additional runtime verification:

```text
Inline Python repro of the -014 asymmetric case:
- GTKB_HARNESS_NAME=codex
- codex guard current_subject=gtkb_infrastructure
- claude guard current_subject=application
- shared canonical current_subject=application
-> detect_counterpart_state():
   subject_mismatch=true
   warning cites codex=gtkb_infrastructure and claude=application
```

Current live guard files inspected:

- `C:\Users\micha\.codex\agent-red-hooks\session-lifecycle-guard.json`
- `C:\Users\micha\.claude\agent-red-hooks\session-lifecycle-guard.json`

Both now include `current_subject`, which was the live-wiring gap called out in
`-012`.

## Evidence

- Reported `-014` resolution and verification matrix:
  `bridge/gtkb-isolation-015-phase7-full-integration-015.md:29-44`,
  `:56-99`, `:104-113`
- Symmetric active-harness read path:
  `scripts/workstream_focus.py:814-839`
- Counterpart warning emission:
  `scripts/workstream_focus.py:840-846`
- Lifecycle-guard writer persists `current_subject`:
  `scripts/session_self_initialization.py:4936-4969`
- Startup path passes the active subject into the guard writer:
  `scripts/session_self_initialization.py:5076-5088`
- Codex-side regression for the exact `-014` repro:
  `tests/hooks/test_workstream_focus.py:631-694`
- Live writer-path regression:
  `tests/scripts/test_session_self_initialization.py:1348-1419`
- Durable backlog annotation remains in place:
  `memory/work_list.md:225-253`

## Findings

No blocking findings remain for Slice 1.

## Verification Scope

This VERIFIED result is limited to Slice 1 as defined in `-007` and reported in
`-015`:

- subject-labeled startup / readiness / test outputs
- bridge live-state writer / validator
- overlay-aware startup status
- multi-harness counterpart-state detection, including symmetric subject-divergence warnings
- `memory/work_list.md` Slice 1 / Slice 2 annotation

`GTKB-ISOLATION-015` remains open overall until Slice 2 lands. Upstream
clean-adopter delivery remains owned by `GTKB-ISOLATION-017`.

## Decision Needed From Owner

None.
