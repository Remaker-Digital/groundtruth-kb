REVISED

# WI-5189 Document-authoritative GO-implementation claim eligibility

bridge_kind: prime_proposal
Document: gtkb-wi5189-document-claim-authority
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated worker session document
author_metadata_source: harness-state/codex/session-envelopes/019f387f-0fc7-7200-abaa-03068ca8eee0.json

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5189-DOCUMENT-CLAIM-AUTHORITY-20260711
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5189

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "platform_tests/scripts/test_work_intent_auto_extend.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_protected_mutation_guard.py"]

implementation_scope: source | test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The approved core repair makes GO-implementation claim authorization resolve
the exact worker session document through `resolve_worker_role_provenance` for
both eligibility and persisted `acting_role`. Role authority no longer comes
from dispatch-token parsing, dispatcher/default state, or role-marker data, and
invalid or non-Prime documents fail closed.

The four-path implementation is complete and passes its approved suite. Broader
claim-registry verification exposed four additional positive fixtures that
still create successful GO-implementation claims without validated worker
session documents. This revision adds only those regression fixtures to the
owner-approved PAUTH and proposal scope. It changes their setup, not their
behavioral assertions.

## Specification Links

- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` - defines document-exclusive claim role authority, fail-closed conditions, prohibited inputs, persisted role attribution, and regression coverage.
- `GOV-SESSION-ROLE-AUTHORITY-001` - worker behavior follows explicit session role authority rather than dispatcher/default state.
- `DCL-SESSION-ROLE-RESOLUTION-001` - validates exact session and harness provenance without using the role registry as authority.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - preserves the owner-declared interactive role through the session document.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH version 3 bounds this work to WI-5189 and the eight declared target paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation begins only after an independent GO, matching claim, and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete governing-spec linkage before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-derived evidence before terminal verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires active PAUTH, project, and work-item metadata.

## Prior Deliberations

- `INTAKE-523b2b75` - captured the document-authority defect after the live claim denial.
- `DELIB-202666148` - owner approved the exact WI-5189 specification text.
- `DELIB-202666150` - owner approved the exact initial WI-5189 PAUTH.
- `DELIB-202666151` - owner approved the first PAUTH scope amendment adding two legacy claim fixtures.
- `DELIB-202666153` - owner approved the second PAUTH scope amendment adding four further positive claim fixtures.
- `DELIB-20263409` - records the predecessor marker transition; marker evidence remains continuity data, not claim-role authority.
- `bridge/gtkb-wi4853-session-role-marker-claim-eligibility-001.md` - historical predecessor superseded for role authority by the WI-5189 specification.
- `bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-002.md` - independently GO-approved WI-5185 remains sequenced after WI-5189 lands.

## Owner Decisions / Input

- `DELIB-202666148`, `DELIB-202666150`, `DELIB-202666151`, and `DELIB-202666153` record the owner's exact specification approval and progressively bounded implementation authorization.
- `.groundtruth/formal-artifact-approvals/2026-07-11-DELIB-202666153.json` validates through the canonical formal-artifact packet validator.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5189-DOCUMENT-CLAIM-AUTHORITY-20260711` version 3 permits only source, test-addition, and governance-evidence work across the eight declared paths. Dispatcher configuration, role/identity maps, selection/routing, providers, credentials, deployment, automatic tuning, destructive cleanup, and unrelated mutation remain forbidden.

## Responses To Prior Review

- Findings 1-3 in `bridge/gtkb-wi5189-document-claim-authority-004.md` were confirmations and remain satisfied.
- The non-blocking stale rollback wording is corrected: rollback covers all eight declared target paths, not two.
- This second expansion follows the same REVISED-after-GO governance path endorsed by the prior review. No added fixture is changed before a new independent GO.

## Requirement Sufficiency

Existing requirements sufficient. The approved specification covers the new
paths, which exercise the same
successful GO-claim contract already specified; no dispatcher, role registry,
or production-selection requirement is introduced.

## Intended Implementation

1. Keep the approved source repair and four already migrated fixtures unchanged except for review-driven corrections.
2. In each newly authorized fixture, create a validated current Prime Builder worker session document before a successful GO-implementation claim.
3. Preserve the existing assertions for dispatcher work-intent lifecycle, implementation authorization ownership, implementation-start gating, and protected-mutation enforcement.
4. Keep negative cases fail closed; do not restore marker-, token-, registry-, or dispatcher-derived role authority.

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` criteria 1-5 | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short` | Prime worker documents authorize claims despite conflicting non-authority data; invalid and non-Prime documents deny; persisted role is document-derived. |
| Same specification criterion 6 and shared claim lifecycle | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_work_intent_auto_extend.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py -q --tb=short` | All eight-path claim and gate regressions pass without weakening timing, exclusivity, authorization, or protected-mutation behavior. |
| `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_kb_attribution_session_role.py -q --tb=short` | Session document provenance and canonical backlog attribution remain document-authoritative. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `-m ruff format --check` on the eight declared target paths | All scoped source and tests pass lint and formatting checks. |

## Pre-Filing Preflight

- `python scripts/bridge_applicability_preflight.py --content-file independent-progress-assessments/CODEX-INSIGHT-DROPBOX/draft-wi5189-005-body.md` must report `preflight_passed: true` and no missing required specifications.
- `python scripts/adr_dcl_clause_preflight.py --content-file independent-progress-assessments/CODEX-INSIGHT-DROPBOX/draft-wi5189-005-body.md` must exit 0 with no blocking clause gaps.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-11-DELIB-202666153.json` reports the packet valid.

## Risk / Rollback

The main risk is accidentally converting a negative fail-closed fixture into a
positive claim. Changes therefore remain limited to successful-claim setup, and
the full scoped suite checks both positive and denial paths. Rollback is one
scoped commit reverting only the eight declared target paths; it does not alter
dispatcher configuration, role maps, or claims already persisted by the fixed
version.

## Bridge Filing

This REVISED proposal is the next status-bearing numbered file for
`gtkb-wi5189-document-claim-authority`. Prior versions remain immutable.

## Recommended Commit Type

`fix(bridge): authorize GO claims from worker session documents (WI-5189)`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
