NEW

# WI-4868 Work-Intent Acting Role Isolation

bridge_kind: prime_proposal
Document: gtkb-wi4868-work-intent-acting-role-isolation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1501-8f8d-77c0-8afe-962b633224b6
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4868

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "scripts/gtkb_session_id.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]

implementation_scope: source, tests, bridge-protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`WI-4868` captures a concurrency defect in bridge work-intent claims: draft and implementation claim metadata can still derive `acting_role` from the shared `.claude/session/active-session-role.json` transition marker when the current session lacks a valid per-session marker or dispatch-session id. Concurrent sessions overwrite that shared file, so a Prime Builder draft claim can be persisted as `loyal-opposition`, confusing bridge filing and same-role/project contention logic.

This proposal removes the shared single-file marker from work-intent claim role attribution and eligibility. Work-intent role attribution must come from one of two scoped authorities only: a dispatch-format session id resolved through the harness projection registry, or a per-session marker whose stored `session_id` matches the querying session. If neither source is available, the claim may still exist where drafting permits it, but `acting_role` must be `None` instead of inheriting a peer session's role.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge work-intent claims are part of the protected file-bridge authority boundary and must not carry role-confused author/claim metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal names the governing bridge, role-resolution, and project-authorization requirements before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal includes active project authorization, project id, work item id, and inline JSON target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation verification must prove the role-attribution and role-eligibility behavior with focused tests.
- `GOV-STANDING-BACKLOG-001` — `WI-4868` is an active P1 work item included in Harness Parity Phase 2.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` authorizes this bounded source/test/protocol slice while preserving bridge GO and verification gates.
- `GOV-SESSION-ROLE-AUTHORITY-001` — session role authority must not be inferred from a peer-clobberable cache when a per-session role source is required.
- `DCL-SESSION-ROLE-RESOLUTION-001` — role resolution must distinguish transcript/per-session role evidence from durable dispatcher role hints and shared cache artifacts.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` — interactive role persistence must be tied to the current session context, not another session's marker file.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — bridge claim behavior must remain consistent for Codex, Claude Code, Cursor, Antigravity, and dispatched provider harness workers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the concurrency defect is promoted from backlog observation into a bridge proposal, tests, implementation report, and verification chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the implementation must preserve the durable artifact graph for the defect, owner authority, tests, and rollback evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — this proposal distinguishes active implementation, verification, rollback, and blocked states instead of leaving the role-confusion fix in scratch context.

## Prior Deliberations

- `INTAKE-e71dd673` — Intake: Default interactive session envelope role continuity
- `INTAKE-d9d4764d` — Intake: Default interactive session envelope role continuity
- `INTAKE-b4928376` — Intake: Bridge review eligibility is harness-agnostic; durable role is a fallback, not a review/verdict gate
- `INTAKE-97211546` — Intake: Harness registrar role assignment and independent review requirements
- `INTAKE-702b8ea6` — Intake: Interactive transcript-defined session role authority
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — related parity implementation authorization context cited by `WI-4868`; the defect blocked cross-harness parity Slice 1 filing.
- `bridge/gtkb-wi4540-per-session-role-marker-context-envelope-003.md` and GO at `bridge/gtkb-wi4540-per-session-role-marker-context-envelope-004.md` — introduced per-session role markers as the non-clobbering session-context authority; this proposal completes that direction for work-intent claim attribution by removing the transition fallback from this surface.
- `bridge/gtkb-session-id-shared-resolver-unification-003.md` and GO at `bridge/gtkb-session-id-shared-resolver-unification-004.md` — established the shared session-id resolver and bridge-work-intent env-var order that this proposal preserves.

## Owner Decisions / Input

No new owner decision is required before filing this proposal. The work item is already part of the active Harness Parity Phase 2 project authorization (`PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`) backed by `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`, and `WI-4868` states the defect and required authority boundary.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-4868`, `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`, and the active Harness Parity Phase 2 PAUTH provide enough authority to remove shared-marker role fallback from work-intent claim attribution and test the corrected behavior. No new GOV/DCL/SPEC mutation is needed in this slice.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short` | Claim metadata remains valid and bridge work-intent claims do not inherit role labels from a peer-clobberable shared marker. |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `DCL-SESSION-ROLE-RESOLUTION-001`; `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | Add/update focused tests in `platform_tests/scripts/test_bridge_work_intent_registry.py` proving per-session marker match is accepted, per-session mismatch is rejected, absent per-session marker ignores `active-session-role.json`, and dispatch-format ids still use harness projection roles. | Work-intent role attribution is session-scoped and dispatcher-role resolution is preserved for headless dispatch ids. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short` | Existing go-implementation eligibility behavior remains aligned across harness session-id sources and does not regress dispatched Prime eligibility. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward with exact command output plus focused ruff checks for changed Python files. | Loyal Opposition can verify the implementation against each linked requirement. |

```text
python -m pytest platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short
python -m ruff check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/gtkb_session_id.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_work_intent_role_eligibility.py
python -m ruff format --check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/gtkb_session_id.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_work_intent_role_eligibility.py
```

## Risk / Rollback

Risk: the shared marker fallback may still be needed by an older interactive path that has not yet been migrated to per-session markers. Mitigation: preserve dispatch-id registry resolution and per-session marker behavior, fail closed for go-implementation eligibility when no scoped evidence exists, and use focused tests to expose any legacy dependency before implementation report filing.

Risk: changing draft-claim `acting_role` to `None` when scoped role evidence is absent may weaken same-role/project contention detection for legacy sessions. Mitigation: per-thread claim exclusivity remains the correctness boundary; same-role/project contention is advisory and already fails open on missing role metadata.

Rollback: revert the implementation commit and re-run the focused claim/eligibility tests. Bridge proposal, report, and verdict files remain append-only audit artifacts.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4868-work-intent-acting-role-isolation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

The expected diff repairs a bridge-claim concurrency/role-attribution defect and adds regression tests. It does not add a new user-facing feature.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
