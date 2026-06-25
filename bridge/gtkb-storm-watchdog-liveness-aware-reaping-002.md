GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-25h
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition auto-process

bridge_kind: proposal_review
Document: gtkb-storm-watchdog-liveness-aware-reaping
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-25 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-storm-watchdog-liveness-aware-reaping-001.md
Project: PROJECT-GTKB-DISPATCHER-COMPLETION
Work Item: WI-4828
Recommended commit type: fix

## Separation Check

Proposal `-001` session `7ed62043-e9ad-48b9-8e00-0e897085426b`; independent Cursor LO session.

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: []

## Clause Applicability

- Clauses evaluated: 5; blocking gaps: 0; exit 0.

## Review Summary

Proposal is **well-scoped, evidence-backed, and implementation-ready** for WI-4828 slice 1: extract a pure `decide_reap` decision module, rewire the storm watchdog to lease-aware orphan/straggler reaping only, and remove the raw-count kill path that terminates healthy in-flight workers.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Raw-count kill is current behavior | pass | `scripts/ops/harness_storm_watchdog.ps1` L34–35 thresholds; L69–94 kill on count exceed |
| Lease registry carries pid + heartbeat + ttl | pass | `scripts/bridge_lease_registry.py` L159–167 record shape; `_is_stale` L114–132 |
| Unit mismatch (OS processes vs logical workers) | pass | watchdog counts codex family + noncodex; concurrency cap is separate (WI-4472) |
| Pure-function test strategy (GOV-10) | pass | `decide_reap(processes, leases, *, now, ...)` with injected `now`; 8 mapped pytest cases |
| Fail-safe on decider error | pass | proposal Risk/Rollback: reap nothing, log error; no fallback to raw-count kill |
| Narrowing-only risk surface | pass | removes broad kill; reaps only orphans/over-lifetime stragglers |
| Owner authorization | pass | `DELIB-20266104` cited (surgical watchdog-liveness scope) |
| Bounded target paths | pass | `storm_watchdog_reap.py`, `harness_storm_watchdog.ps1`, `test_storm_watchdog_reap.py` |
| Adjacent WI inventory | pass | WI-4818/WI-4804 reviewed; complementary/orthogonal |

## Residual Risks (non-blocking)

- **P3:** Proposal does not pin the dispatch `state_dir` path in the `.ps1` rewire; implementer should default to `.gtkb-state/cross-harness-trigger` (lease dir per `bridge_lease_registry._lease_dir`) and log when absent.
- **P3:** Lease listing is via glob/parse in the shell layer; acceptable for slice 1. Consider a small `list_lease_records(state_dir)` helper in a follow-up if duplication appears.
- **P3:** `cursor_harness.py` remains outside the noncodex watch list (WI-4818); lease-based protection still covers Cursor workers that hold leases, as proposal states.

## Prior Deliberations

- `DELIB-20266104` — owner surgical watchdog-liveness authorization.
- `DELIB-20265882` — daemon owns throttle/liveness long-term; interim stabilization sanctioned.
- `DELIB-20265877`, `DELIB-20260612` — congestion not failure; kill-switch emergency-only.

## Verdict Rationale

**GO** — preflight-clean, owner-authorized, correct root-cause analysis against live watchdog + lease registry, GOV-10-aligned pure decision module with complete spec-to-test mapping, and strictly narrowing operational risk. Implementation may proceed within declared `target_paths`.
