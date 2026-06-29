NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-2026-06-29T00-18-00Z
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Bridge signal quality inactive substrate diagnostics

bridge_kind: prime_proposal
Document: gtkb-wi4253-inactive-substrate-diagnostics
Version: 001
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY-BRIDGE-SIGNAL-QUALITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY
Work Item: WI-4253

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File governed proposal for WI-4253 to replace repeated inactive-substrate dispatch-failure spam with state-only diagnostics and reason-aware diagnose output.

Work item description: When harness-state/bridge-substrate.json intentionally sets substrate to none, cross_harness_bridge_trigger records repeated dispatch-failure rows with reason substrate_mismatch_inert, while diagnose classifies them as other unknown. Replace per-hook failure-log spam with state-only inactive-substrate diagnostics and make diagnose reason-aware.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4253` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.

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

## Prior Deliberations

- `DELIB-20266287` - Found an existing PAUTH that's a strong scope match: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BATCH` v2 (project:
- `DELIB-20266241` - Spec-to-Test Mapping
- `DELIB-20266245` - Separation Check
- `DELIB-20266204` - Owner reconciliation decision batch 2: resolve 2 verified-done drift WIs (WI-3405, WI-4566)
- `DELIB-20266084` - Owner authorization: WI-4787 dispatcher daemon foundation (Phase 2)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY-BRIDGE-SIGNAL-QUALITY-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4253`.

## Proposed Scope

- Classify intentional bridge substrate none as inactive-substrate state instead of repeated actionable dispatch-failure rows.
- Make diagnose output reason-aware for substrate_mismatch_inert and malformed dispatch JSONL tolerance.
- Preserve existing hard-fail behavior for real dispatch failures and malformed state that should remain actionable.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability preflight and targeted dispatcher-trigger tests before implementation report. |
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

## Acceptance Criteria

- Intentional substrate none appears in dispatch-state and diagnose output without repeated dispatch-failures JSONL appends.
- Diagnose groups inactive substrate explicitly instead of other/unknown.
- Regression coverage includes malformed JSONL tolerance and reason-aware inactive-substrate classification.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Recommended Commit Type

`feat`
