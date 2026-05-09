VERIFIED

# Loyal Opposition Verification - Bridge Poller Event-Driven Replacement Slice 1 + Slice 2 Corrected

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed implementation report: `bridge/gtkb-bridge-poller-event-driven-replacement-009.md`
Verdict: VERIFIED

## Claim

The `-009` report repairs both P1 blockers from `-008`.

- F1 is addressed: the trigger now signs the selected dispatch batch, not the full pending list, and the default dispatch cap is restored to the smart-poller default of 2.
- F2 is addressed: child harness dispatch no longer receives `GTKB_NO_CROSS_HARNESS_TRIGGER=1`; reciprocal dispatch is governed by durable per-recipient signature state.

Slice 1's governance evidence remains accepted from prior verification passes, and Slice 2 remains non-live because no hook registration invokes the new script yet.

## Prior Deliberations

- `DELIB-0836` (rowid 844): predecessor owner decision accepting the prior Codex Windows hook limitation and fallback posture.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550): empirical retest showing Codex hooks fire on Windows in Codex CLI v0.128.0-alpha.1.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551): Slice 1 supersession deliberation refreshing the stance from `DELIB-0836`.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001
```

Observed:

- packet_hash: `sha256:cc8f0278be16ef59fad53426380dac714a600cd19e1502ac9489f9f1e8f73bc0`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-009.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-009.md`
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
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-009.md`
- Clauses evaluated: `5`
- must_apply: `4`, may_apply: `1`, not_applicable: `0`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`
- Mode: mandatory default invocation; exit code `0`

## Supporting Verification

Commands run during this review:

```text
python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py tests/scripts/test_cross_harness_bridge_trigger.py
rg -n "cross_harness_bridge_trigger|GTKB_NO_CROSS_HARNESS_TRIGGER|cross-harness-trigger" .claude .codex config scripts tests groundtruth-kb/scripts groundtruth-kb/tests
```

Observed:

- `tests/scripts/test_cross_harness_bridge_trigger.py`: `12 passed, 1 warning`.
- Ruff: `All checks passed!`
- Hook-registration search found only the script, tests, and bridge-skill references; no `.claude` or `.codex` hook currently invokes the script.

Code-level checks:

- `scripts/cross_harness_bridge_trigger.py` sets `DEFAULT_MAX_ITEMS = 2`.
- `run_trigger` computes `selected = _selected_oldest_first(filtered, max_items)` and signs `_signature(selected)`.
- Dispatch state records `signature_scope: "selected_dispatch_batch"` and `selected_count`.
- `_spawn_harness` sets `GTKB_PROJECT_ROOT` but strips `GTKB_NO_CROSS_HARNESS_TRIGGER` from child env before `subprocess.Popen`.
- The tests import the smart-poller helper for the selected-batch parity case and prove selected-batch and full-list signatures differ when the queue exceeds the cap.
- The round-trip test proves `NEW -> unchanged -> GO` dispatches Codex first, suppresses unchanged repeat dispatch, then dispatches Prime after the live INDEX changes.

## Findings

No blocking findings.

Non-blocking note: `_spawn_harness` still has a stale local docstring line saying it sets `GTKB_NO_CROSS_HARNESS_TRIGGER=1` in the child env. The executable behavior and tests are correct, and the surrounding module/commentary has been updated, but Prime should clean that stale docstring before or during the Slice 2 commit if practical.

## Decision

VERIFIED for the combined Slice 1 + Slice 2 `-009` implementation report. Slice 3 hook registrations remain a separate future bridge step and should not ship until filed and reviewed.

File bridge scan: 1 entry processed by this response; the glossary entry was already handled concurrently at `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-006.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
