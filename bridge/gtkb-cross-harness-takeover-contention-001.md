NEW

# gtkb-cross-harness-takeover-contention — Stabilize cross-harness takeover contention and rate-limit auto-dispatch

bridge_kind: implementation_proposal
Document: gtkb-cross-harness-takeover-contention
Version: 001
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-17 UTC

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: 68a85c45-4776-4341-b646-3664fc66f02d
author_model: Gemini 3.5 Flash
author_model_version: Gemini 3.5 Flash (High)
author_model_configuration: Antigravity CLI interface, Prime Builder mode

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4560

target_paths: ["scripts/cross_harness_bridge_trigger.py"]

implementation_scope: bridge-dispatch
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal resolves a defect (WI-4560) where the cross-harness dispatch trigger immediately re-grabs expired or lapsed bridge claims, spawning a new headless worker. If a headless worker fails to make progress on a complex thread and its claim expires, this creates an unbreakable "claim-churn-expire-redispatch" livelock that blocks interactive takeovers and wastes tokens.

We will introduce a 30-minute cooldown on headless worker dispatches for any thread whose last claim was held by a headless worker (`trigger-dispatched-*`) and expired/lapsed without any progress (meaning the version was not advanced and the status remains `GO` or `NO-GO`). This gives interactive sessions a window to claim the thread without trigger interference.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — TAFE-backed bridge state and status-bearing numbered files are canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Linked specifications are required for bridge approval.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project and WI linkage metadata must be specified.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Proposal must specify a spec-derived verification plan.
- `GOV-STANDING-BACKLOG-001` — Backlog items are the cross-session work authority.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` — Owner authorized all unimplemented WIs in the May29 Hygiene project.
- `DELIB-20260616-MAY29-HYGIENE-AUTHORIZATION` — Owner authorized defect fixes under S20260616.

## Owner Decisions / Input

- Authorized by owner in deliberation `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` during S445.

## Requirement Sufficiency

- Existing requirements sufficient — Resolving a bug/defect in the implementation of work-intent trigger dispatching.

## Spec-Derived Verification Plan

We will add unit test cases to verify the cooldown suppression logic:
* Execute:
  ```text
  groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --no-header -p no:cacheprovider
  ```
* Expected: All tests pass, including new assertions verifying that expired headless claims trigger the 30-minute cooldown suppression on headless auto-dispatched sessions while permitting interactive prime takeover.

## Risk / Rollback

- **Risk:** Low. The change is isolated to trigger-filtering logic.
- **Rollback:** Single-commit revert of `scripts/cross_harness_bridge_trigger.py`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-cross-harness-takeover-contention`; no prior version is deleted or rewritten (append-only).

## Recommended Commit Type

Recommended commit type: `fix: resolve takeover contention livelock by applying a cooldown on headless dispatches after claim expiration`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
