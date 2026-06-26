GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-26a
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition auto-process

bridge_kind: proposal_review
Document: gtkb-wi4845-configurable-worker-lifetime
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4845-configurable-worker-lifetime-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4845
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `e6490e91-a7fd-489d-be63-363714e9ba47` (harness B); independent Cursor LO session.

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: []

## Clause Applicability

- Clauses evaluated: 5; blocking gaps: 0; exit 0.

## Review Summary

**GO.** Root cause confirmed: `run_with_status.py` hardcodes 600s lifetime and dispatcher spawns inherit it with no override, killing cloud LO workers (exit 124) before verdict emission. The `--lifetime` CLI parameter plus LO-specific 1800s routing in `cross_harness_bridge_trigger.py` is the minimal fix aligned with `DELIB-20266136` and WI-4806 deferred configurability.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| 600s hardcoded default | pass | `run_with_status.py` L15, L137 |
| Dispatcher passes no override | pass | no `--lifetime` in trigger spawn path today |
| Owner authorization | pass | `DELIB-20266136` configurable cap + LO budget |
| Bounded envelope preserved | pass | default 600s unchanged; LO gets 1800s only |
| Storm guards retained | pass | max_turns, per-call timeout, WI-4828/WI-4472 unchanged |
| Spec-derived test plan | pass | four mapped tests across two files |

## Prior Deliberations

- `DELIB-20266136` — owner AUQ authorizing this fix.
- `DELIB-20266132` — WI-4670 fork into WI-4845.

## Verdict

**GO.** Implement per `-001` scope and verification plan.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
