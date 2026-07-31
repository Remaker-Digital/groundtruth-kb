NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Make dispatched LO ownership checks use canonical bridge targets and DB-backed claims

bridge_kind: prime_proposal
Document: gtkb-wi5343-lo-review-authority-packet
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5343-LO-REVIEW-AUTHORITY-PACKET-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5343

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Harden dispatched Loyal Opposition review packets so target ownership is derived from the complete numbered bridge chain and work-intent ownership is read from the canonical DB-backed claim service, never stale summaries or retired runtime claim directories.

Work item description: Dispatched Claude B review 2026-07-16T17-40-21Z-loyal-opposition-B-025d3f filed bridge/gtkb-wi5337-latest-no-go-draft-claim-state-002.md with a false F3 ownership finding. It said WI-5307 did not govern scripts/bridge_work_intent_registry.py even though WI-5307 proposal 015, GO 016, report 017, and VERIFIED 018 all declare that exact target. It also treated an empty .gtkb-state/work-intent directory as claim authority instead of the canonical groundtruth.db-backed bridge claim service. Harden dispatcher review packets or the bridge-review skill so ownership comes from the full numbered bridge chain and claims come from canonical gt/bridge_claim_cli status, never stale MemBase summaries or retired runtime directories.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5343` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20263296` - GO - WI-4534 Role-Eligibility Guard on go_implementation Claims
- `DELIB-20265493` - Loyal Opposition GO verdict - WI-4700 narrative approval packet scope fix
- `DELIB-20263298` - NO-GO - WI-4534 Role-Eligibility Guard on go_implementation Claims
- `DELIB-20263293` - NO-GO Verdict - WI-4534 Claim Role-Eligibility Guard Slice A
- `DELIB-20263295` - Loyal Opposition GO Verdict: WI-4534 Claim Role Eligibility Guard

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5343-LO-REVIEW-AUTHORITY-PACKET-20260716` - active project authorization covering `WI-5343`.

## Proposed Scope

- Add an LO-only dispatch-prompt authority block that requires the complete numbered bridge version chain to determine target ownership.
- Require the repo-venv canonical bridge claim status command so dispatched reviewers read the groundtruth.db-backed claim service, not retired runtime claim directories.
- State that MemBase work-item descriptions, startup summaries, copied excerpts, and .gtkb-state/work-intent are context only and cannot establish target or claim ownership.
- Preserve all Prime Builder prompt behavior, routing, selection, TAFE/runtime state, provider adapters, live workers, and unrelated dirty hunks.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused test asserts complete numbered-chain authority and projection non-authority in the LO prompt. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused test builds an LO dispatch prompt and verifies canonical repo-venv command composition without changing target selection or spawn behavior. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Source review and focused test prove the change remains inside dispatcher-owned prompt composition and does not move control into a harness. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Prompt coverage verifies the same canonical authority instructions apply to every LO target without weakening harness guards. |

## Acceptance Criteria

- A focused dispatch-prompt test proves LO workers are directed to read the full numbered chain via gt bridge show and derive target ownership from target_paths in that chain.
- The prompt directs claim checks through groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status and identifies that service as groundtruth.db-backed.
- The prompt explicitly rejects MemBase/backlog summaries and .gtkb-state/work-intent as target or claim authority, while Prime Builder prompt behavior remains unchanged.
- Focused dispatcher-runtime tests, ruff, proposal applicability, and ADR/DCL clause preflights pass without adopting foreign hunks.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`feat`
