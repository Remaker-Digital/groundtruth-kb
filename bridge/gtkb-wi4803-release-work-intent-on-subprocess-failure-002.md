GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-26d
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition auto-process

bridge_kind: proposal_review
Document: gtkb-wi4803-release-work-intent-on-subprocess-failure
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4803-release-work-intent-on-subprocess-failure-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4803
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `130bf9ae-15f0-4373-a7b5-9286568dbc97` (harness B); independent Cursor LO session.

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: []

## Review Summary

**GO.** The claim-leak defect is real: Prime work-intent is acquired pre-launch and released only when `not launch.get("launched")`; `_process_pending_exit_codes` failure branch records failure but does not release. Fix placement in the failure reconcile path is correct and idempotent.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Acquire before spawn | pass | `_acquire_prime_work_intent_batch` ~L4557 |
| Launch-only release | pass | release gated when spawn fails to launch ~L4635+ |
| Failure branch no release today | pass | `_process_pending_exit_codes` else at L3806+ |
| `last_launch` carries release keys | pass | `work_intent_slugs` / `work_intent_session_id` stamped L4631-4632 |
| Owner authorization | pass | `DELIB-20266137` |
| Focused unit tests (not run_trigger) | pass | avoids WI-4712 flaky integration path |

## Verdict

**GO.** Implement per `-001` scope and verification plan.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
