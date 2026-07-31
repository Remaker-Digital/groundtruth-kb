NEW

# WI-4981 - Mid-Session Init Role Switch

bridge_kind: prime_proposal
Document: gtkb-wi4981-mid-session-init-role-switch
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T00:50:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI4981-BATCH-B-20260705
Project: PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE
Work Item: WI-4981

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_canonical_init_keyword_syntax.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4981 captures a concrete role-authority defect: `scripts/workstream_focus.py` recognizes a mid-session `::init gtkb pb|lo` prompt in the Claude Code `UserPromptSubmit` path, but that ordinary prompt path does not persist the per-session role marker. The startup-gate path already writes the legacy marker and WI-4540 per-session markers, and the ordinary explicit-role-hint path already writes per-session markers, but the canonical mid-session init keyword currently becomes a silent no-op for role resolution.

This proposal authorizes a bounded source/test fix under the active Batch B PAUTH. The implementation must choose an explicit behavior and test it: either invoke the existing per-session marker writer from the mid-session canonical init branch so the session role changes immediately, or return a clear user-visible response that canonical role switching requires a fresh session. Silent recognition without persisted authority is not acceptable because it leaves the owner thinking the session role changed while enforcement gates continue under the old role.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation work requires this proposal, Loyal Opposition review, latest `GO`, implementation-start authorization, implementation report, and verification before WI-4981 can be treated as terminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the owner-approved WI-4981 Batch B scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization satisfies owner approval only; it does not bypass bridge `GO`, target paths, report, or verification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - interactive transcript/session role authority must not silently lose to dispatcher/default registry state after an owner role declaration.
- `DCL-SESSION-ROLE-RESOLUTION-001` - marker/envelope role resolution must remain explicit, per-session, and fail-closed or fail-visible where required.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - owner-declared interactive roles persist within the same interactive context and must be represented by the session role authority mechanism.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - the accepted keyword form remains exactly `::init gtkb (pb|lo)` with closed vocabulary and strict parsing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every governing bridge and role-authority requirement before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this proposal to the active project authorization, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map role-switch behavior and failure visibility to concrete tests.
- `GOV-STANDING-BACKLOG-001` - WI-4981 remains the MemBase backlog authority and must be resolved only with bridge/report/verification evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner-reported defect must remain traceable through WI, PAUTH, bridge proposal, tests, implementation report, and terminal disposition.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation must preserve traceability across the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4981 moves from backlog candidate to proposal, implementation, verification, and terminal resolution through explicit lifecycle states.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch B continuation and the active PAUTH covering WI-4981.
- WI-4981 backlog row - records the 2026-07-03 empirical hook test showing `handle_hook_payload` matches `::init gtkb pb` but writes no per-session marker in the mid-session prompt path.
- `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A` - earlier role-authority boundary approval supporting dispatcher/default role separation from interactive session authority.
- `INTAKE-e584f460` - all live agent mutations are bridge-first by default; relevant to preserving bridge-governed implementation flow.

## Owner Decisions / Input

Owner approval is already recorded by `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` and active authorization `PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI4981-BATCH-B-20260705`. No fresh owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements are sufficient. The backlog item states the observed defect and acceptable fix choices, while the cited role-authority specifications define the behavior contract: owner-declared interactive role must either be persisted into the session role authority path or fail visibly so the owner is not misled.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Canonical mid-session `::init gtkb pb|lo` no longer silently no-ops | Add or update hook tests so `handle_hook_payload({"prompt": "::init gtkb pb", "session_id": ...})` either writes the expected per-session marker or returns an explicit fresh-session-required response. |
| Per-session role authority remains session-keyed | If marker persistence is implemented, assert the written `.claude/session/role-<session>.json` carries `role`, raw `session_id`, `session_id_source`, and `source` values consistent with WI-4540 marker tests. |
| Headless dispatch remains excluded | Preserve tests proving `GTKB_BRIDGE_POLLER_RUN_ID` does not write interactive session markers for dispatched worker prompts. |
| Canonical keyword syntax does not drift | Retain `platform_tests/scripts/test_canonical_init_keyword_syntax.py` coverage for strict `::init gtkb (pb|lo)` parsing and no synonyms. |
| Resolver behavior remains read-only and authority-ordered | Run `platform_tests/scripts/test_session_role_resolution.py` so resolver reads per-session marker/envelope authority without mutation. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` bridge lifecycle | Implementation must run only after latest `GO` and `implementation_authorization.py begin --bridge-id gtkb-wi4981-mid-session-init-role-switch`; report must cite target-path authorization evidence. |

Minimum expected verification commands after implementation:

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short
python -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_canonical_init_keyword_syntax.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4981-mid-session-init-role-switch --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4981-mid-session-init-role-switch
```

## Risk / Rollback

Risk is concentrated in accidental role changes for headless dispatch or stale session IDs. Keep the implementation scoped to owner-typed interactive prompts, reuse existing marker helpers, preserve the headless-dispatch exclusion, and roll back as one commit if role-resolution tests regress.

## Bridge Filing

This proposal is filed as the next status-bearing numbered bridge file for `gtkb-wi4981-mid-session-init-role-switch`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - the expected implementation corrects a role-switch defect while preserving bridge and role-authority gates.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
