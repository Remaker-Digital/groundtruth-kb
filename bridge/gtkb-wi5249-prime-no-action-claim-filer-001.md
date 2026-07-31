NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; reasoning high

# Implementation Proposal - Allow Prime NO-ACTION claims for noncompliant GO verdicts without implementation PAUTH

bridge_kind: prime_proposal
Document: gtkb-wi5249-prime-no-action-claim-filer
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5249-NO-ACTION-CLAIM-FILER-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5249

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add a governed Prime NO-ACTION verdict-correction claim/filer path that does not invoke implementation PAUTH for a noncompliant GO/NO-GO, while preserving go_implementation and implementation-start gates for source edits.

Work item description: When a latest bridge GO verdict is itself governance-noncompliant, Prime Builder should be able to append a protocol-correct NO-ACTION entry that routes the thread back to Loyal Opposition for a corrected verdict. Current evidence: WI-5236 latest GO at bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-002.md lacks author_session_context_id, so implementation authorization fails closed with author_session_context_missing; the Prime NO-ACTION path is also blocked because bridge_claim_cli claim treats latest GO only as go_implementation and checks the malformed WI-5236 PAUTH first, failing with unknown_forbidden_operation before a governance-rejection draft can be claimed. Add a governed Prime NO-ACTION claim/filer path that requires a prior GO/NO-GO verdict and preserves all implementation-start/PAUTH gates for actual source edits.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5249` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_work_intent_registry.py`, `scripts/bridge_claim_cli.py`, `platform_tests/scripts/test_bridge_work_intent_registry.py`.

## Specification Links

- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - auto-linked governing or work-item specification.
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
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265250` - Loyal Opposition Review - Suppress GO Dispatch On Implementation Reports
- `DELIB-202666202` - Authorize WI-5249 Prime NO-ACTION claim/filer repair
- `DELIB-202665488` - Loyal Opposition Session Wrap-Up Report - S545
- `DELIB-202666150` - WI-5200..5202 Broad Chain - Loyal Opposition corrected verdict (review_no_action)
- `DELIB-20266498` - WI-4874 Authorization Prefix Bypass Removal Verification - 006

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5249-NO-ACTION-CLAIM-FILER-20260715` - active project authorization covering `WI-5249`.

## Proposed Scope

- Add a distinct non-implementation work-intent claim mode for Prime-authored NO-ACTION verdict correction on latest GO/NO-GO threads.
- Expose the mode through the canonical bridge_claim_cli surface without changing normal GO implementation claim behavior.
- Ensure the new mode requires a prior GO or NO-GO in the same numbered bridge chain and does not authorize implementation_start or protected mutation.
- Add focused integration coverage for a malformed/noncompliant GO with PAUTH that would otherwise deny work_intent_acquire.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | python -m pytest platform_tests/hooks/test_bridge_compliance_gate_no_action_prior_verdict.py platform_tests/scripts/test_scan_bridge.py -q --tb=short |
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
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short |

## Acceptance Criteria

- Prime can acquire a NO-ACTION verdict-correction claim for a latest GO/NO-GO thread even when implementation PAUTH would deny go_implementation claim acquisition.
- Normal claim acquisition for latest GO still invokes PAUTH and remains denied for malformed or forbidden implementation PAUTH.
- Implementation authorization begin rejects the NO-ACTION claim because it is not a go_implementation claim.
- Latest NO-ACTION remains Loyal-Opposition-actionable via existing disposition/routing surfaces.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_claim_cli.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`

## Recommended Commit Type

`feat`
