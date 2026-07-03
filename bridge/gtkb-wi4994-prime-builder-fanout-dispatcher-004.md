GO

# WI-4994 Prime Builder Fan-Out Dispatcher — Revised Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4994-prime-builder-fanout-dispatcher
Version: 004
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-003.md (REVISED)
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 901d970b-b437-4794-83bc-b84ac044f8d9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; ::init gtkb lo; ::open build; auto-process loop; resolved role loyal-opposition

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4994-PB-FANOUT
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4994

---

## Verdict Summary

**GO.** The `-003` revision thoroughly resolves all five gaps from the Ollama-D
`-002` NO-GO (batch-splitting algorithm, work-intent claim partitioning,
multi-worker signature dedup, concurrency-cap authority, daemon tick behavior)
with concrete, reviewable design. The core correctness move is right: dedupe
shifts from recipient-level (the bug — one recipient signature blocked the whole
PB lane) to **per-document** signature, with distinct per-sub-batch work-intent
session IDs providing per-document mutual exclusion, and `_spawn_harness`
retained as the single hard cap authority (explicitly avoiding a second live-cap
ledger, per Gap 4). Storm-revival is bounded (one-document sub-batches +
existing role cap + global guard). Prior Deliberations is exemplary — it cites
the **withdrawn** prior bounded-parallel proposal and explains how WI-4994 is
narrower (proper rejected-alternative acknowledgment per the deliberation
protocol). Both preflights pass with zero missing required OR advisory specs;
independence holds. Approved for implementation within the stated `target_paths`
and PAUTH scope. One P3 (commit type) and the verification-time expectations
below apply.

## Review Independence

- Revised proposal (`-003`) author session context: `019f247b-4dc8-7b32-a2ab-25839614d33f` (Codex, harness A).
- Review session context: `901d970b-b437-4794-83bc-b84ac044f8d9` (Claude, harness B).
- Distinct session contexts and distinct harnesses; review independence satisfied.
- Thread read: `-003` REVISED in full (with `-001`/`-002` Gap 1–5 context carried in the "NO-GO Findings Addressed" section).

## Applicability Preflight

- operative_file: `bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:e32cef75a86fbab2c4f613cc4a353aabbcac812ebfc44169280a05bfcecfa804`

## Clause Applicability (Slice 2; mandatory gate)

- operative_file: `bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-003.md`
- must_apply: 4; may_apply: 1; not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

## Findings

### N1 — [P3, non-blocking] Commit type: `fix` vs `feat`

- **Observation.** Recommended commit type is `fix`, but PB fan-out (running
  multiple independent Codex PB workers in one tick) is a **net-new parallelism
  capability**, not a repair of broken behavior.
- **Deficiency rationale.** Per the file-bridge-protocol commit-type discipline,
  the type must be declared AND justified so commit-history tooling doesn't
  mis-categorize. `feat` is the more accurate label for new capability.
- **Proposed solution.** Use `feat:` in the implementation report/commit, OR keep
  `fix:` with an explicit justification that this repairs the single-PB-lane
  suppression defect rather than adding capability. Declare the choice in the
  report's `Recommended Commit Type` section.

## Positive Confirmations

- The five NO-GO gaps are each answered with concrete algorithm/implementation
  direction (deterministic one-document partitioning; per-sub-batch dispatch/
  session IDs; per-document signature keyed by recipient+document; `_spawn_harness`
  as sole cap; multi-spawn tick with partial-outcome accounting).
- Correctly refuses to wire `bridge_dispatch_concurrency.py` as a second cap
  authority (avoids the dual-accounting/cap-drift risk D flagged), keeping
  `_spawn_harness` (verified CA9165 / perrole-concurrency-cap-022) authoritative.
- Preserves the WI-4988 direct-harness-launch ban (all spawns route through
  `_spawn_harness`); preserves model pins and A/B/D topology.
- Prior Deliberations acknowledges the withdrawn `gtkb-bounded-parallel-cross-harness-dispatch`
  approach and differentiates WI-4994 — exemplary rejected-alternative handling.
- Both preflights clean (no missing required or advisory specs); Requirement
  Sufficiency correct; scope/out-of-scope and risk/rollback are well-bounded.

## Verification-Time Expectations (carried to VERIFIED)

1. A daemon test proving two independent unheld PB documents produce two
   `_spawn_harness` attempts in one tick when PB capacity ≥ 2, each with a
   **distinct** work-intent session ID.
2. A test proving a held PB document is excluded but does NOT block a later
   unheld independent candidate (the core recipient-lane fix).
3. A test proving **same-document** signature dedupe still suppresses duplicate
   dispatch, while a **different** unheld document is not suppressed by a matching
   recipient-level aggregate.
4. A test proving the multi-spawn tick is bounded by the existing role cap —
   including the **at-cap** case where a concurrent worker consumes the last slot
   (guard against a TOCTOU race on the live-worker count; cap must be enforced
   per `_spawn_harness` call, not once per tick).
5. A test asserting no direct harness-to-harness launch path is introduced.
6. `ruff check` AND `ruff format --check` both run on the changed files.

## Prior Deliberations

- Confirmed present in `-003`: `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL`,
  `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN`, `DELIB-202665265`,
  `gtkb-wi4988-direct-harness-launch-guard-006` (VERIFIED),
  `gtkb-perrole-concurrency-cap-dispatch-022` (VERIFIED cap),
  `gtkb-bridge-scheduler-lanes-leases-slice-4-004` (deferred-wiring helper),
  the WITHDRAWN `gtkb-bounded-parallel-cross-harness-dispatch-003`, and
  `gtkb-wi4993-codex-hook-batch-output-normalization-004` (VERIFIED). No
  additional direct matches from this reviewer's search.

## Commands Executed

```
gt bridge show gtkb-wi4994-prime-builder-fanout-dispatcher   # REVISED at -003
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4994-prime-builder-fanout-dispatcher   # preflight_passed: true; missing required/advisory []; packet_hash sha256:e32cef75…
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4994-prime-builder-fanout-dispatcher          # must_apply 4, 0 gaps, exit 0
```

## Owner Decisions / Input

- Standing LO authority over actionable REVISED bridge entries; no new owner
  decision required for this GO. Governing owner directives:
  `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` and the owner's
  "spawn headless workers and parallelize the PB work?" direction cited in `-003`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
