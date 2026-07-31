NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f68b0-30a8-7843-867b-6f37d981a975
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Bind implementation-start provenance lookup to the acting harness

bridge_kind: prime_proposal
Document: gtkb-wi5353-implementation-start-harness-selector
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5353-IMPLEMENTATION-START-HARNESS-SELECTOR-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5353

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization_harness_selector.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the one remaining implementation-start call site that ignores the acting harness document selector and therefore rejects valid PB provenance whenever concurrent harness projections reuse a session id. The resolver's no-selector ambiguity guard remains unchanged. Implementation is explicitly sequenced after WI-5346 releases the shared source file.

Work item description: scripts/implementation_authorization.py finalizes an implementation-start packet by calling resolve_worker_role_provenance with only the session id. When concurrent harness projections contain the same session id, the resolver correctly fails closed as globally ambiguous even though the acting CLI has GTKB_HARNESS_NAME and an exact valid harness-scoped worker document. Claim acquisition and MemBase attribution already pass that selector. Bind implementation-start provenance lookup to the acting harness selector without deriving role from harness identity. Preserve global no-selector ambiguity failure, wrong-harness/missing/mismatched document denial, claim/PAUTH/target gates, and dispatcher worker authority. Do not delete or rewrite runtime/session-envelope evidence. Sequence implementation after WI-5346 releases scripts/implementation_authorization.py.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5353` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `platform_tests/scripts/test_implementation_authorization_harness_selector.py`.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-20266094` - Owner decision: verify-by-reference resolution of PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION (6 done-but-unlinked WIs)
- `DELIB-20263293` - NO-GO Verdict - WI-4534 Claim Role-Eligibility Guard Slice A
- `DELIB-20261467` - Loyal Opposition Verification - Interactive Session Role Override Slice 6 Attribution Role-Awareness
- `DELIB-2620` - Loyal Opposition Verification - Interactive Session Role Override Slice 6 Attribution Role-Awareness
- `DELIB-20260711-WI5118-BY-REFERENCE-FINALIZATION-WAIVER` - WI-5118 scoped by-reference finalization waiver

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5353-IMPLEMENTATION-START-HARNESS-SELECTOR-20260716` - active project authorization covering `WI-5353`.

## Proposed Scope

- After WI-5346 is independently verified and its implementation packet is closed, add a document-selector helper in scripts/implementation_authorization.py that uses explicit GTKB_HARNESS_NAME first and only deterministic interactive harness signals as a non-authoritative document selector.
- Pass that selector to resolve_worker_role_provenance during implementation-start finalization; role remains exclusively document-authoritative.
- Add a focused isolated regression module covering same-session conflicting Codex/LO documents, selected wrong-harness and identity mismatch denial, and unchanged no-selector ambiguity.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Run the focused harness-selector regression module and existing worker-role provenance tests; prove role comes from the selected document and global ambiguity remains fail-closed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability and implementation-start gate checks against the filed proposal; verify no protected mutation precedes GO, claim, and implementation-start. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate the generated packet against PAUTH-DISPATCHER-BLACK-BOX-WI5353-IMPLEMENTATION-START-HARNESS-SELECTOR-20260716 and both exact targets. |

## Acceptance Criteria

- The proposal remains review-only while WI-5346 owns scripts/implementation_authorization.py; no protected mutation may begin until the shared target is released and a fresh implementation-start packet validates both exact target paths.
- A valid Codex Prime Builder document selected by GTKB_HARNESS_NAME permits implementation-start despite a conflicting LO document with the same session id.
- Missing, closed, wrong-harness, role-conflicting, or provenance-conflicting selected documents fail closed, and calling resolve_worker_role_provenance without a harness selector remains ambiguous.
- Claim kind, holder session, PAUTH operation-time, target-path, role, and focused-commit gates are unchanged.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization_harness_selector.py`

## Recommended Commit Type

`feat`
