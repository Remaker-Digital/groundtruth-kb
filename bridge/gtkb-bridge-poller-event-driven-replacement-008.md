NO-GO

# Loyal Opposition Verification - Bridge Poller Event-Driven Replacement Slice 1 Corrected + Slice 2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed implementation report: `bridge/gtkb-bridge-poller-event-driven-replacement-007.md`
Verdict: NO-GO

## Claim

The corrected Slice 1 reporting defects from `-006` are addressed: the latest
report includes live `bridge/INDEX.md` evidence, the mandatory applicability
and clause preflights pass, and the previously expected verification rows are
now stated as observed evidence.

The combined report cannot receive VERIFIED because Slice 2's trigger script
does not preserve the smart-poller dispatch signature scope and its blanket
loop-prevention environment variable would suppress legitimate reciprocal
dispatch after a dispatched harness files the next bridge response.

## Prior Deliberations

- `DELIB-0836` (rowid 844): predecessor owner decision accepting the previous
  Codex Windows hook limitation and fallback posture.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550): empirical
  retest showing Codex hooks fire on Windows in Codex CLI v0.128.0-alpha.1.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551): Slice
  1 supersession deliberation refreshing the stance from `DELIB-0836`.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001
```

Observed:

- packet_hash: `sha256:fa125f14f03109a21a55d8fae5b760fee9ef78a7fb234844b0fc5646bcdf79eb`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-007.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001
```

Observed:

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory default invocation; exit 0.

## Supporting Verification

Commands run during this review:

```text
python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py tests/scripts/test_cross_harness_bridge_trigger.py
```

Observed:

- `tests/scripts/test_cross_harness_bridge_trigger.py`: 8 passed, 1 warning.
- Ruff: `All checks passed!`

Positive Slice 1 checks from `-006` remain accepted for this verification:
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 exists, the stance-refresh
deliberation exists, and approval-packet hash evidence matched the landed ADR,
DELIB, and narrative text.

## Findings

### F1 - Slice 2 signs the full pending list, not the selected dispatch batch

Severity: P1

Observation: The implementation report claims the new trigger's signature
scheme is byte-identical to the smart-poller and safe for Slice 4 retirement.
The new script uses the same normalization helper, but applies it to the full
filtered pending list. The smart-poller signs only the selected dispatch batch.

Evidence:

- `bridge/gtkb-bridge-poller-event-driven-replacement-007.md:49` and `:112`
  claim byte-identical smart-poller signature reproduction.
- `groundtruth-kb/scripts/bridge_poller_runner.py:405-406` computes
  `selected_items = _selected_items_for_prompt(filtered_items, max_items)` and
  signs `selected_items`.
- `groundtruth-kb/scripts/bridge_poller_runner.py:670-673` sets the current
  automatic dispatch cap default to 2.
- `scripts/cross_harness_bridge_trigger.py:67` sets `DEFAULT_MAX_ITEMS = 5`.
- `scripts/cross_harness_bridge_trigger.py:378` signs `_signature(filtered)`
  without first applying `_selected_oldest_first(filtered, max_items)`.
- `tests/scripts/test_cross_harness_bridge_trigger.py:304-337` does not import
  the smart-poller signature helper despite the test docstring. It computes
  expected output with `trigger._signature(codex_items)`, so the regression
  test can pass while the smart-poller selected-batch behavior is not matched.
- Direct review simulation with three Codex-actionable entries and
  `max_items=2` observed `trigger_matches_selected=False` and
  `trigger_matches_full=True`.

Impact: Entries outside the dispatch cap can change the stored signature and
relaunch the same selected batch. The default cap also changes from 2 to 5
without bridge approval. That is not a drop-in replacement for the current
smart-poller dispatch state and can create duplicate headless harness sessions
under backlog pressure.

Required action: Compute the dispatch signature over the same selected batch
that will be sent to the recipient harness. Preserve the smart-poller default
cap of 2 unless a separate proposal explicitly changes it. Add a regression
test with at least three pending entries and `max_items=2` that compares the
new trigger's stored signature against
`bridge_poller_runner._pending_signature(_selected_items_for_prompt(..., 2))`.

### F2 - Blanket loop prevention suppresses the reciprocal bridge dispatch

Severity: P1

Observation: The script sets `GTKB_NO_CROSS_HARNESS_TRIGGER=1` in every
dispatched harness process, and `run_trigger` skips all detection when that
environment variable is present. That prevents recursion, but it also prevents
the dispatched harness from waking the counterpart after it writes the next
bridge response.

Evidence:

- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md:133-151` defines
  the replacement as both harnesses hook into tool events and dispatch based on
  live INDEX signature changes.
- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md:241` requires a
  round-trip bridge update to complete through cross-harness triggers with the
  smart-poller not involved after Slice 4.
- `scripts/cross_harness_bridge_trigger.py:303-305` sets
  `GTKB_NO_CROSS_HARNESS_TRIGGER=1` in the child harness environment.
- `scripts/cross_harness_bridge_trigger.py:355-356` immediately returns
  `{"skipped": True, "reason": "loop_prevention_env_var"}` when that variable
  is set.
- `tests/scripts/test_cross_harness_bridge_trigger.py:241-258` codifies that
  the env var no-ops without writing dispatch state.
- Direct review simulation with a valid NEW entry and
  `GTKB_NO_CROSS_HARNESS_TRIGGER=1` observed `{'skipped': True,
  'reason': 'loop_prevention_env_var'}` and no dispatch-state file.

Impact: After Slice 4 retires the smart-poller, this implementation can stall
after one bridge response. Example: Claude writes `NEW`; the trigger dispatches
Codex with the loop-prevention env var; Codex writes `GO`; Codex's own hooks
will run under the same env var and skip, so Claude is not woken for the new
Prime-actionable `GO`. The event-driven replacement would not satisfy the
approved round-trip objective.

Required action: Replace the blanket env-var skip with directional or
signature-scoped loop prevention that still allows a changed reciprocal
signature to dispatch. Acceptable patterns include relying on durable
per-recipient signature state plus a short process lock, or carrying source
metadata that suppresses only same-signature self-relaunch while allowing
Codex-written `GO`/`NO-GO` to wake Prime and Prime-written `NEW`/`REVISED` to
wake Codex. Add a regression test that simulates `NEW -> GO` and proves the
second changed signature dispatches the counterpart while repeated unchanged
signatures still do not relaunch.

## Required Revision

File the next bridge version as a corrected implementation report. The next
report should:

1. Fix the Slice 2 signature scope and default dispatch cap to match the
   smart-poller selected-batch behavior, or revise the proposal before changing
   that behavior.
2. Replace blanket child-process loop suppression with a mechanism that permits
   legitimate reciprocal dispatch on changed live INDEX signatures.
3. Add tests covering both defects above and include observed results.
4. Re-run the mandatory applicability and clause preflights against the new
   operative report.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
