NEW

# WI-4868 Claim Role Session-Marker Authority

bridge_kind: prime_proposal
Document: gtkb-wi4868-claim-role-session-marker-authority
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019f1503-6938-7d72-904c-09e18a3b2d4b
author_model: gpt-5-codex
author_model_version: 2026-06-19
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4868

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "platform_tests/scripts/test_go_impl_claim_timebox.py"]

implementation_scope: source, tests, bridge-protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Fix the WI-4868 defect where work-intent claim attribution and GO-implementation eligibility can still consult the shared `.claude/session/active-session-role.json` fallback when no per-session marker is available. In concurrent sessions, that shared marker is peer-clobberable: another harness can overwrite it with `loyal-opposition`, causing a Prime Builder claim to persist `acting_role=loyal-opposition`, `acting_role=null`, or fail eligibility despite valid Prime authority.

The implementation should make claim-role resolution deterministic under concurrency: dispatch-format session ids resolve from the durable harness registry; interactive session ids resolve only from the matching per-session role marker/envelope keyed to that session id. The shared single-file marker must not be positive authority for `go_implementation` claim eligibility or the persisted `acting_role` field. Any remaining compatibility use of the shared marker must be explicitly outside GO-implementation authority and covered by tests.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected source/test changes require a live GO, a work-intent claim, implementation-start evidence, and post-implementation verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites the bridge, role-resolution, and backlog specifications that constrain the change.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal carries Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must map tests back to these linked specifications before Loyal Opposition can mark the work VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-4868 is the durable MemBase backlog authority for this defect.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable role records govern headless dispatch routing; interactive session evidence must not be replaced by a peer-clobberable cache.
- `DCL-SESSION-ROLE-RESOLUTION-001` — role resolution must preserve the split between dispatch authority and session-stated role evidence.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` — interactive transcript role persistence must survive compaction/resume without depending on another session's shared marker write.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the defect is preserved as a work item and this proposal routes the repair through durable bridge artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — implementation must update source, tests, and verification evidence as a traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the implementation report and verification verdict must preserve the active-to-verified lifecycle evidence for WI-4868.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are GT-KB platform paths under `E:\GT-KB`, not Agent Red adopter surfaces.

## Prior Deliberations

- `INTAKE-e7d44d40` — Intake: GO-implementation claims are time-boxed with an owner-extendable deadline to produce the implementation report
- `INTAKE-e71dd673` — Intake: Default interactive session envelope role continuity
- `INTAKE-d9d4764d` — Intake: Default interactive session envelope role continuity
- `INTAKE-b4928376` — Intake: Bridge review eligibility is harness-agnostic; durable role is a fallback, not a review/verdict gate
- WI-4540 per-session marker context-envelope work established per-session role marker reads for interactive sessions. WI-4868 narrows the remaining fallback hazard in claim attribution and GO-implementation eligibility.
- WI-4534 claim-role eligibility work established that GO-implementation claims are Prime-only. WI-4868 preserves that guard while removing shared-marker authority that can be written by an unrelated session.

## Owner Decisions / Input

No new owner decision is required. `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` actively authorizes bounded Harness Parity Phase 2 implementation work, and WI-4868 is an open work item in `PROJECT-HARNESS-PARITY-PHASE-2`.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4868, `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`, and the active Harness Parity Phase 2 project authorization are sufficient for this source/test repair. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4868-claim-role-session-marker-authority` after GO and claim acquisition | Implementation-start packet authorizes only the declared target paths. |
| `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001` | `python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short` | Dispatch-format session ids resolve role from the harness registry; interactive GO-implementation eligibility no longer accepts a peer-written shared marker as positive authority. |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | Add or update tests in `platform_tests/scripts/test_bridge_work_intent_registry.py` that create conflicting per-session and shared markers for different session ids | The matching per-session marker is authoritative; absent/mismatched per-session evidence fails closed instead of falling through to a shared marker written by another session. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Implementation report cites changed files, command output, and in-root target paths | The repair leaves durable source/test/bridge evidence inside the GT-KB platform root. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward with exact command output | Loyal Opposition has spec-derived verification evidence before VERIFIED. |

```text
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py -q --tb=short
python -m ruff check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py
python -m ruff format --check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py
```

## Risk / Rollback

Risk is moderate because claim eligibility gates protected implementation work. The implementation must not break legitimate dispatch-format Prime Builder claims, and it must not make interactive Prime sessions impossible when a valid per-session marker exists.

Rollback is a single commit revert of the source/test changes. Bridge files and work-intent history remain append-only audit artifacts and must not be deleted by rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4868-claim-role-session-marker-authority`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

This repairs a concurrency defect in bridge claim role attribution and GO-implementation eligibility; it does not introduce a new user-facing capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
