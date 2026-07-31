NO-GO

# WI-4986 Model-Aware Dispatch Timers — Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4986-model-aware-dispatch-timers
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4986-model-aware-dispatch-timers-001.md (NEW)
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 901d970b-b437-4794-83bc-b84ac044f8d9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; ::init gtkb lo; ::open build; auto-process loop; resolved role loyal-opposition

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4986-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4986

---

## Verdict Summary

**NO-GO — constructive; the design is right, three fixes needed.** This proposal
correctly targets the exact defect the owner just directed a fix for
(model-aware / per-harness generous timeout allowances so slow models like Opus
4.8 Max are not falsely `worker_timeout`'d), and its scope aligns well with the
owner directive: generous initial per-harness/model/config allowances, elapsed-
time telemetry, and evidence-based dial-in. Authorization is valid, Requirement
Sufficiency is present, both mandatory preflights pass, and review independence
holds. However, three items block GO:

1. **Root-cause gap (blocking):** the proposal sets generous allowances but does
   NOT address why the *already-configured* per-role LO lifetime (1800s, WI-4845,
   `dispatcher_runtime.py` L4154) was **not reaching the launched worker** —
   B-35d3b7 (claude-opus-4-8 --effort max) died at the ~600s `run_with_status.py`
   default, not the 30-min cap. Setting *new* generous per-harness values will
   not help if the configured value still fails to reach the worker (likely a
   **stale dispatcher daemon** running pre-wiring code — the daemon showed
   `Running: False`, heartbeat ~31 min stale). The fix must ensure the configured
   allowance actually applies to the live worker (daemon-freshness / launch-path),
   not just define new numbers.
2. **Prior Deliberations placeholder (blocking):** the section is the uncurated
   `_No prior deliberations auto-loaded; author must confirm before review._`
   placeholder (mechanical NO-GO trigger). Relevant priors exist and must be
   cited — see below.
3. **Owner's latest directive not cited (blocking-with-#2):** the proposal cites
   `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` but not the owner's newer
   `DELIB-202665303` (2026-07-03: per-harness timers, generous-first, verify the
   lifetime reaches the worker, iterate). The revised proposal must reflect and
   cite it.

## Review Independence

- Proposal (`-001`) author session context: `019f247b-4dc8-7b32-a2ab-25839614d33f` (Codex, harness A).
- Review session context: `901d970b-b437-4794-83bc-b84ac044f8d9` (Claude, harness B).
- Distinct session contexts and distinct harnesses; review independence satisfied.

## Applicability Preflight

- operative_file: `bridge/gtkb-wi4986-model-aware-dispatch-timers-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability (Slice 2; mandatory gate)

- Operative file: `bridge/gtkb-wi4986-model-aware-dispatch-timers-001.md`
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

## Findings

### N1 — [P1, BLOCKING] Root cause (lifetime not reaching worker) not addressed

- **Observation.** Live evidence: dispatched LO worker B-35d3b7 (claude-opus-4-8
  --effort max) was `worker_timeout` (exit 124) at ~10 min, despite the intended
  1800s (30-min) LO lifetime (WI-4845). `dispatcher_runtime.py` L4154 *does* pass
  `--lifetime 1800`, yet the worker died at `run_with_status.py`'s 600s default —
  so the override is not reaching the live worker. The daemon reported
  `Running: False`, heartbeat ~31 min stale.
- **Deficiency rationale.** WI-4986's scope defines generous per-harness values
  but does not ensure they *apply* to the launched worker. A new generous value
  that also fails to reach the worker fixes nothing. This is the load-bearing
  half of the fix.
- **Proposed solution.** Add scope to verify/repair that the resolved per-harness
  allowance reaches the live worker — check for a stale dispatcher daemon running
  pre-wiring code (restart to pick up current `dispatcher_runtime.py`) and/or a
  launch-path that bypasses the `--lifetime` wiring; add a regression test that a
  dispatched worker's effective lifetime equals its configured per-harness value.
- **Prime Builder context.** Evidence: `dispatcher_runtime.py` L4154 (--lifetime
  wiring), `run_with_status.py` L15 (600s default) / L183 (single lifetime wait);
  `gt bridge dispatch daemon status` (Running/heartbeat).

### N2 — [P2, BLOCKING] Prior Deliberations placeholder + missing owner directive

- **Observation.** `## Prior Deliberations` is the uncurated placeholder; the
  proposal cites `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` but not
  `DELIB-202665303` (owner's per-harness-generous-first directive).
- **Proposed solution.** Complete the section citing: `DELIB-202665303` (owner
  per-harness/generous-first/verify-reaches-worker/iterate directive),
  `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS`, `WI-4845`/`DELIB-20266203`
  (per-role lifetimes), `WI-4977` (dispatch-stability, adjacent), and `WI-4987`
  (a **duplicate backlog capture now resolved/superseded by WI-4986** — cite for
  provenance so the duplication is on record).
- **Prime Builder context.** Prior Deliberations section only.

### N3 — [P3] Generic verification plan; N4 — [P3] spurious auto-attached spec links

- 11 of 13 verification rows are the generic "run candidate/live preflights"
  filler; several spec links (e.g., `SPEC-AUQ-POLICY-ENGINE-001`) are auto-attached
  with no governing relationship. Map concrete per-spec tests (per-harness lifetime
  derivation, lifetime-reaches-worker regression, telemetry-field assertions,
  Ollama route-budget bound) and curate the link set.

## Required Revisions

1. **N1** — Add scope + a test that the resolved per-harness allowance actually
   reaches the live worker (daemon-freshness / launch-path root cause).
2. **N2** — Complete Prior Deliberations citing `DELIB-202665303` +
   `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` + WI-4845/WI-4977 + the
   WI-4987 supersession.
3. **N3/N4** — Concrete per-spec tests; curate spec links.

## Positive Confirmations

- Scope aligns with the owner's per-harness/generous-first/telemetry/dial-in
  directive; Opus 4.8 Max 15-30 min allowance and Ollama route-budget raise are
  correct targets.
- Authorization (WI-4986 open/P1, PAUTH active), Requirement Sufficiency,
  independence, and both preflights are all in order.
- Recommended commit type `feat` is appropriate.

## Prior Deliberations

- Deliberation Archive semantic search this session returned no direct matches;
  the governing owner directives are `DELIB-202665303` and
  `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS`.
- `WI-4987` — LO duplicate capture of this same defect, resolved/superseded by
  WI-4986 (self-corrected by this reviewer).

## Commands Executed

```
gt bridge show gtkb-wi4986-model-aware-dispatch-timers   # NEW at -001
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4986-model-aware-dispatch-timers   # preflight_passed: true
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4986-model-aware-dispatch-timers          # exit 0
# root-cause evidence: dispatcher_runtime.py L4154 (--lifetime 1800 wired), run_with_status.py L15 (600s default); daemon Running:False; B-35d3b7 exit 124 at ~10 min
```

## Owner Decisions / Input

- Standing LO authority over actionable NEW bridge entries; no new owner decision
  required for this NO-GO. Owner directive `DELIB-202665303` (2026-07-03) governs
  the revised design.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
