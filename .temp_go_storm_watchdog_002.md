GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-25g
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

Proposal is **well-scoped, evidence-grounded, and surgically bounded**. Replaces raw-count family kill with lease-aware pure `decide_reap` logic; fail-safe on decider error; no trigger/dispatch architecture change.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Active PAUTH | pass | `PAUTH-WI-4828-STORM-WATCHDOG-LIVENESS-001` status `active` |
| Owner authorization | pass | `DELIB-20266104` cited (surgical watchdog-liveness scope) |
| Raw-count kill today | pass | `harness_storm_watchdog.ps1` L34-35 thresholds=15; L69-93 `Stop-Process` on exceed |
| Lease registry surface | pass | `bridge_lease_registry.py` records `pid`, `heartbeat_at`, `ttl_seconds` |
| No dispatch trigger mutation | pass | `target_paths` exclude `cross_harness_bridge_trigger.py` |
| Fail-safe on decider error | pass | proposal requires reap-nothing + log on failure |
| Spec-derived test plan | pass | 8 pure-function cases covering protect/reap tiers + determinism |
| Backlog adjacency reviewed | pass | WI-4818/WI-4804 inventoried as complementary/orthogonal |

## Residual Risks

- `.ps1` rewire is inspection/smoke-validated; implementation report should include decider-invocation evidence.
- `max_lifetime_seconds` alignment with WI-4806 worker timeout should be explicit in constants/env docs.

## Prior Deliberations

- `DELIB-20266104` — owner surgical slice authorization.
- `DELIB-20265882`, `DELIB-20265888` — dispatcher architecture anchors.
- `DELIB-20266084` — WI-4787 daemon foundation (parallel track).

## Verdict Rationale

**GO** — narrowing fix with strong root-cause evidence, complete test plan, conservative fail-safe, and zero dispatch-behavior risk. Implementation may proceed.
