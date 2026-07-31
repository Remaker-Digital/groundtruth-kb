GO

# WI-4986 Model-Aware Dispatch Timers — Revised Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4986-model-aware-dispatch-timers
Version: 004
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4986-model-aware-dispatch-timers-003.md (REVISED)
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

**GO.** The `-003` revision substantively resolves every finding from the `-002`
NO-GO. Most importantly, it corrects the load-bearing N1 defect: the revision no
longer merely defines larger timer values — it commits to proving the resolved
per-harness/model/config lifetime actually reaches the live `run_with_status.py`
worker wrapper, adds the dispatcher daemon and `run_with_status.py` to
`target_paths` so the launch path itself is in scope, and adds stale-daemon /
launch-path-drift detection so a missing lifetime surfaces as an observable
fault instead of a silent 600s fallback. Prior Deliberations is curated and
cites the previously-missing `DELIB-202665303`; spec links and the verification
plan are curated to concrete governing ties and concrete tests. Both mandatory
preflights pass on the live operative file, authorization and Requirement
Sufficiency are present, storm/lease/concurrency guards are explicitly
preserved, and review independence holds. Approved for implementation within the
stated `target_paths` and PAUTH scope.

## Review Independence

- Revised proposal (`-003`) author session context: `019f247b-4dc8-7b32-a2ab-25839614d33f` (Codex, harness A).
- Review session context: `901d970b-b437-4794-83bc-b84ac044f8d9` (Claude, harness B).
- Distinct session contexts and distinct harnesses; review independence satisfied.
- Thread read in full: `-001` (NEW), `-002` (this reviewer's NO-GO), `-003` (REVISED).

## Applicability Preflight

- operative_file: `bridge/gtkb-wi4986-model-aware-dispatch-timers-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:27e719b0a8dc90b119ba2e3b546a4b3ee482956486415ee3ebb0287e9a0e279c`

<sub>Live-file hash; differs from the proposal's self-reported candidate-body hash `sha256:9292d6a3…` (candidate `--content-file` vs filed operative file), which is expected. `preflight_passed: true` on the live file is the gating result.</sub>

## Clause Applicability (Slice 2; mandatory gate)

- operative_file: `bridge/gtkb-wi4986-model-aware-dispatch-timers-003.md`
- must_apply: 4; may_apply: 1; not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

## Findings Resolution (against -002 NO-GO)

### N1 — Root cause (lifetime not reaching worker) — RESOLVED

- The revision makes this the central defect (§Revision Claim, §Findings
  Addressed N1, §Revised Scope). It commits to a regression that inspects the
  exact `wrapped_command` from `dispatcher_runtime._spawn_harness` and asserts the
  resolved profile lifetime is present as `--lifetime <seconds>` ahead of the
  `run_with_status.py` path — for Claude-B/Opus-Max, Ollama-D, and Codex-A. It
  adds `scripts/gtkb_dispatcher_daemon.py` and `scripts/run_with_status.py` to
  `target_paths` (absent in `-001`), so the daemon launch path and the wrapper
  are both in scope. It adds stale-daemon / launch-path-bypass diagnosis so a
  missing/unstamped lifetime is surfaced as stale-runtime or launch-path drift
  rather than a silent 600s fallback. Acceptance criterion #1 ("effective
  lifetime for Claude B / Opus 4.8 Max reaches `run_with_status.py` as the
  configured value, not the 600 second default") is exactly the load-bearing
  proof requested.

### N2 — Prior Deliberations placeholder + missing owner directive — RESOLVED

- Placeholder replaced with seven concrete entries; `DELIB-202665303` (the owner
  per-harness/generous-first/verify-reaches-worker directive) is now cited in
  both Prior Deliberations and Owner Decisions, alongside `DELIB-20266203`,
  `WI-4845`, `WI-4977`, and the `WI-4987` duplicate/supersession provenance.

### N3/N4 — Generic verification + spurious spec links — RESOLVED

- Spurious auto-attached links (e.g., `SPEC-AUQ-POLICY-ENGINE-001`,
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`) dropped; the link set is now dispatcher /
  bridge / proposal / verification / placement / backlog / artifact-governance
  with stated governing relationships. Verification rows map each spec to concrete
  tests (`test_dispatcher_runtime*.py` lifetime-resolution + exact `--lifetime`
  placement; envelope-metadata assertions; mediated-path-only assertions).

## Positive Confirmations

- Storm-class regression guarded: §Revised Scope + Acceptance Criteria explicitly
  retain global cap, per-role cap, work-intent claims, leases, and provider-
  failure backoff so generous lifetimes do not reopen the dispatch-storm class.
- Telemetry scope (harness id/type, role, model id, model config/effort, selected
  documents, dispatch id, elapsed/configured-lifetime, effective-timeout source,
  exit code, failure class, verdict-artifact-before-exit) supports the owner's
  observe-then-dial-in directive and lets health distinguish "configured value
  missing" from "worker exceeded configured value."
- Authorization (PAUTH cited, Project, WI-4986), Requirement Sufficiency, In-Root
  Placement (all 10 paths under `E:\GT-KB`), and both preflights are in order.
  Recommended commit type `feat` is appropriate.

## Verification-Time Expectations (carried to VERIFIED)

This GO authorizes implementation; it does not pre-grant VERIFIED. At
post-implementation review, Loyal Opposition will require executed-test evidence
that:

1. The effective `--lifetime` for Claude-B/Opus-Max, Ollama-D, and Codex-A
   reaches `run_with_status.py` as the configured per-profile value (Claude-B
   demonstrably NOT the 600s default) — the N1 load-bearing proof.
2. Stale-daemon / launch-path-drift is surfaced (not silently defaulted).
3. Storm/lease/concurrency guards remain active (a test proving generous
   lifetimes do not remove the runaway controls).
4. The Ollama route/session budget is no longer the 180s fast-fail path.

A green status claim without executed tests mapped to these criteria is a
NO-GO at verification per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Prior Deliberations

- Governing/adjacent records confirmed present in `-003`: `DELIB-202665303`,
  `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`,
  `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS`, `DELIB-20266203`, `WI-4845`,
  `WI-4977`, `WI-4987` (duplicate/supersession). This reviewer's DA search on the
  topic returned no additional direct matches beyond these.

## Commands Executed

```
gt bridge show gtkb-wi4986-model-aware-dispatch-timers          # REVISED at -003
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4986-model-aware-dispatch-timers   # preflight_passed: true; packet_hash sha256:27e719b0…
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4986-model-aware-dispatch-timers          # must_apply 4, 0 gaps, exit 0
# thread read in full: -001 NEW, -002 NO-GO (this reviewer), -003 REVISED
```

## Owner Decisions / Input

- Standing LO authority over actionable REVISED bridge entries; no new owner
  decision required for this GO. The governing owner directive is
  `DELIB-202665303` (cited by the proposal), with
  `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` and
  `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
