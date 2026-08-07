WITHDRAWN
::init gtkb lo
::open build
author_identity: owner-authorized/withdrawal
author_harness_id: G
author_session_context_id: G-2026-08-07T02-36-09Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: owner-authorized override; goose-desktop

bridge_kind: operational_state_change
Document: gtkb-wi5671-startup-relay-fail-open
Version: 011
Date: 2026-08-07 UTC
Responds to: bridge/gtkb-wi5671-startup-relay-fail-open-010.md

# WITHDRAWN (owner decision)

## Specification Links

- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - terminal withdrawal lifecycle.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge chain authority.
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 - shared-path conflict resolution.

## Owner Decisions / Input

- Owner-authorized decision (in-session, 2026-08-07, established Wave-0 pattern): withdraw this thread to clear the shared-path conflict blocking PB processing of gtkb-wi5970-work-subject-config-carveout-drift-guard. Owner approval recorded in-session.

## Withdrawal Reason

- This thread (startup-relay fail-open) is closed by owner-authorized decision to clear the shared-path conflict on platform_tests/hooks/test_workstream_focus.py that blocked the GO-approved sibling thread gtkb-wi5970. The v010 NO-GO reflected an unfixed daemon-thread design gap.

## Clear Condition

- This thread is closed by owner decision; its work is preserved in the bridge chain and may be re-filed as a fresh proposal if the owner re-activates it. Terminal close per DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001.

---

When you are finished working, close your session envelope by invoking ::wrap.
