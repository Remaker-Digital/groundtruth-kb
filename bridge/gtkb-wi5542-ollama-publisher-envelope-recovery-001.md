NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; governed WI-5542 proposal

# Implementation Proposal - Make Ollama D publisher-only recovery succeed without provider tool_choice enforcement

bridge_kind: prime_proposal
Document: gtkb-wi5542-ollama-publisher-envelope-recovery
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5542-OLLAMA-PUBLISHER-ENVELOPE-RECOVERY-20260718
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5542

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make Ollama D publisher-only recovery independent of provider tool-choice enforcement. After the provider has authored a substantive review but failed to call the publisher, request one exact verdict envelope in a no-tools turn, validate it locally against the trusted assigned-document and canonical publisher contracts, and invoke canonical publication only for a valid assigned target.

Work item description: Fresh dispatcher-produced D run 2026-07-18T06-11-37Z-loyal-opposition-D-3edbb9 completed substantive review work but exited 1 after publisher-only recovery exhausted four attempts; the final failure reported that PublishBridgeVerdict produced no nonblank verdict path because recovery received a non-publisher Bash call. WI-5495 version 005 correctly split F from D after proving Ollama native /api/chat has no tool_choice control and the OpenAI-compatible endpoint does not reliably honor forced tool_choice for the active model. Design and implement a D-specific, protocol-appropriate recovery path that preserves target-authored review intent, publishes exactly one governed verdict through the canonical publisher, never treats prose or an unvalidated envelope as completion, emits bounded actionable diagnostics on failure, retains all generous worker/model/operation allowances, and leaves D dispatchability, role, routing, caps, TAFE, leases, and live workers unchanged. Require a fresh substantive dispatcher-produced D Loyal Opposition verdict after independent verification and focused finalization.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5542` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/ollama_harness.py`, `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
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
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666850` - Ollama D publisher-recovery fix needs graceful-exhaustion redesign, not a transport switch
- `DELIB-202666257` - Loyal Opposition Proposal Review - WI-5253 Ollama D Publisher Failure Recovery
- `DELIB-202666204` - Authorize WI-5253 Ollama D publisher recovery repair
- `DELIB-202666256` - Loyal Opposition Verification Verdict - WI-5253 Ollama Publisher Recovery
- `DELIB-202666410` - Loyal Opposition Defect-Fix Proposal Review - GO - WI-5227 Ollama D Abrupt-Exit Diagnostics

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5542-OLLAMA-PUBLISHER-ENVELOPE-RECOVERY-20260718` - active project authorization covering `WI-5542`.

## Proposed Scope

- On publisher-only recovery, issue a no-tools Ollama turn that requests one exact JSON verdict envelope rather than relying on a provider-selected PublishBridgeVerdict tool call.
- Parse and validate the envelope locally: role-correct verdict status, assigned document slug, complete verdict body, required publisher arguments, no duplicate or unassigned target, and no mixed prose or extra action.
- Invoke the existing canonical PublishBridgeVerdict execution path only after validation; malformed, mixed, duplicate, and unassigned envelopes consume the bounded recovery budget and never count as completion.
- Sequence implementation after WI-5495, WI-5471, WI-5545, and every exact-target owner are terminal, then require a fresh matching claim and implementation-start authorization.
- Preserve D eligibility, LO role, max-items 2, model route, provider/model/session/operation allowances, TAFE, routing, leases, live workers, and all bridge/finalization gates.

## Cross-Harness Disposition

- **A / Codex**: PB-only lane unchanged; no provider-adapter behavior change.
- **D / Ollama**: Direct LO repair target; use prompt-only envelope recovery under the unchanged model route and max-items 2.
- **F / OpenRouter**: No behavior change in this D-specific slice; shared per-document prerequisite remains WI-5545.
- **B, C, E, H**: No role, eligibility, route, cap, provider, or runtime change.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Fresh dispatcher-produced D review publishes a substantive governed verdict under the unchanged lane configuration. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Independent GO, exact-target clearance, matching claim, implementation-start authorization, and canonical publication remain mandatory. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent verification executes focused and full affected Ollama tests plus lint, format, compilation, and exact-diff checks. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused Ollama loop tests prove the no-tools recovery turn, local envelope validation, canonical publisher invocation, and bounded failure behavior. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Provider-specific recovery preserves the common governed publisher outcome without claiming unsupported tool-choice capability. |

## Acceptance Criteria

- A valid target-authored recovery envelope publishes exactly one assigned governed verdict through the canonical publisher and allows completion only after required assigned-document state advances.
- Malformed JSON, mixed prose, wrong status, incomplete body, duplicate slug, unassigned slug, and extra actions fail closed with bounded actionable diagnostics and no publisher execution.
- Ordinary Ollama tool turns and all current generous allowances remain unchanged.
- A fresh substantive dispatcher-produced D Loyal Opposition artifact succeeds after independent VERIFIED and focused finalization without topology or route changes.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`feat`
