NEW

# WI-5189 Document-authoritative GO-implementation claim eligibility

bridge_kind: prime_proposal
Document: gtkb-wi5189-document-claim-authority
Version: 001
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

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]

implementation_scope: source | test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The active Prime Builder session document for `019f387f-0fc7-7200-abaa-03068ca8eee0`
resolves `prime-builder` from the transcript `::init gtkb pb`, but the current
GO-implementation claim guard instead reads a per-session marker and denies the
claim as Loyal Opposition. That blocks the separately GO-approved WI-5185 repair.

This proposal makes the work-intent registry resolve the exact worker session
document through the canonical `resolve_worker_role_provenance` service for both
claim eligibility and persisted `acting_role`. The implementation removes role
authorization reliance on dispatch-token parsing, dispatcher/default registry
state, and marker data. It remains fail-closed for absent, malformed, closed,
ambiguous, mismatched, internally inconsistent, or non-Prime documents.

## Specification Links

- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` - defines document-exclusive claim role authority, the fail-closed conditions, prohibited role inputs, and required regression coverage.
- `GOV-SESSION-ROLE-AUTHORITY-001` - worker behavior follows explicit session role authority rather than dispatcher/default state.
- `DCL-SESSION-ROLE-RESOLUTION-001` - the canonical session-envelope resolver validates exact session and harness provenance without using the role registry as authority.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - preserves the owner-declared interactive role through the session document.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH bounds this work to WI-5189 and the two declared target paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation begins only after an independent GO, matching claim, and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - links every applicable requirement and the spec-derived verification plan before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed test evidence mapped to the approved specification before terminal verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - carries the active PAUTH, project, and work-item metadata in this proposal.

## Prior Deliberations

- `INTAKE-523b2b75` - captured the document-authority requirement candidate after the live claim denial.
- `DELIB-202666148` - owner approved the exact WI-5189 specification text.
- `DELIB-202666150` - owner approved the exact bounded WI-5189 PAUTH scope.
- `DELIB-20263409` - prior verification of the marker transition confirms why marker evidence exists; this proposal narrows claim authorization to the later document authority without deleting marker continuity behavior.
- `bridge/gtkb-wi4853-session-role-marker-claim-eligibility-001.md` - predecessor marker-hardening work remains historical evidence only; its marker-based claim guard is superseded for role authority by the approved WI-5189 requirement.
- `bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-002.md` - independently GO-approved WI-5185 is blocked only because the present claim guard rejects the valid Prime Builder session document.

## Owner Decisions / Input

- `DELIB-202666148` records the owner's `Approve exact WI-5189 spec text` decision and its formal approval packet.
- `DELIB-202666150` records the owner's `Approve exact WI-5189 PAUTH text` decision and its formal approval packet.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5189-DOCUMENT-CLAIM-AUTHORITY-20260711` is active, includes WI-5189 and its source specification, permits only source, test-addition, and governance-evidence work, and explicitly forbids dispatcher/configuration, role-map, routing, provider, credential, deployment, tuning, destructive, and unrelated mutation.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` defines the exact authority source, exclusions, fail-closed cases, persisted-claim attribution, and acceptance tests. This proposal introduces no new requirement and does not broaden WI-5185 or any prior marker transition work.

## Intended Implementation

1. Add a small read-only bridge helper that resolves validated worker role provenance for the supplied session ID and converts documented resolver failures into the existing claim refusal path.
2. Use that helper to determine both GO-implementation eligibility and the persisted `acting_role` value.
3. Leave draft-claim behavior, claim time limits, bridge status parsing, and work-intent ownership semantics unchanged.
4. Add focused fixtures that create session-keyed worker documents and verify document-over-marker and document-over-registry behavior plus every required fail-closed rejection path.

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` criteria 1-5 | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short` | Prime document accepts despite a Loyal Opposition marker; LO/invalid documents deny; persisted acting role equals document role; tests prove no marker or registry authority path. |
| `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` criterion 6 | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_work_intent_auto_extend.py platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short` | Draft claims and bounded GO-claim timebox behavior remain intact. |
| `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_kb_attribution_session_role.py -q --tb=short` | Session document provenance and canonical backlog writer attribution remain document-authoritative. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py` | Focused source and test files pass lint and formatting checks. |

## Risk / Rollback

The main risk is rejecting a legitimate worker whose session document was not
created or cannot validate. The specified fail-closed behavior is intentional:
no GO-implementation claim may be created or replaced without authenticated
worker-role evidence. The focused regression matrix covers the supported
document shapes. Rollback is one scoped commit reverting only the two declared
target paths, which restores the prior marker/registry guard without altering
claims already persisted by the corrected version.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered file
for `gtkb-wi5189-document-claim-authority`; no prior version is deleted or
rewritten. Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(bridge): authorize GO claims from worker session documents (WI-5189)`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
