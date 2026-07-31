NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Allow canonical implementation-proposal filing CLI to supply required cross-harness disposition

bridge_kind: prime_proposal
Document: gtkb-wi5420-canonical-parity-disposition-cli
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5420

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make the canonical implementation-proposal filing command capable of satisfying the mandatory cross-harness disposition gate for managed harness-surface targets. The CLI will accept explicit structured dispositions, render the required section, reject malformed entries, and preserve fail-closed omission behavior.

Work item description: When gt bridge file-implementation-proposal targets .claude/skills or .codex/skills, it generates no ## Cross-Harness Disposition section and exposes no structured disposition option. The canonical compliance gate then hard-blocks the proposal under DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, forcing callers onto the lower-level non-bypass writer despite otherwise valid metadata, PAUTH, target paths, and preflights. Add a structured CLI input and generated section without weakening the parity gate.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5420` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`, `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`, `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`.

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
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
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202665571` - Verdict: GO -- WI-4764 Heartbeat Session-Role Latch
- `DELIB-20265842` - Loyal Opposition Review - GO - gtkb-wi4686-init-minimization-open-disclosure-relocation
- `DELIB-202665179` - Verdict Summary
- `DELIB-202665174` - Verdict Summary
- `DELIB-202665173` - Verdict Summary

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5420`.

## Proposed Scope

- Add a repeatable structured CLI option for HARNESS_OR_SURFACE=disposition entries and carry it through FilingRequest.
- Render ## Cross-Harness Disposition only from non-empty validated entries; do not synthesize parity claims or waivers.
- Preserve the existing parity compliance hard-block when harness-surface targets omit the disposition.
- Keep project, PAUTH, target-path, author-metadata, candidate-preflight, live-preflight, and governed writer behavior unchanged.
- Do not mutate dispatcher, TAFE, harness state, groundtruth.db outside the governed work-item lifecycle, Git, credentials, deployment, or release.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Add CLI integration tests for accepted structured parity dispositions, malformed entry rejection, and unchanged omitted-disposition denial. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the proposal-filing suite through the governed writer fake and a real compliance-audit regression. |
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
| `ADR-CROSS-HARNESS-PARITY-001` | Review generated proposal text to require explicit per-harness or per-surface behavior statements and no synthesized waiver. |
| `GOV-WORK-TREE-HYGIENE-001` | Confirm the implementation touches only the exact three approved clean targets. |

## Acceptance Criteria

- A harness-surface proposal with one or more structured dispositions renders a non-empty ## Cross-Harness Disposition section and passes PARITY-DISPOSITION-GATE.
- A harness-surface proposal with no disposition remains denied by the existing compliance gate.
- Malformed disposition entries without a non-empty key and value fail before any bridge write.
- Ordinary non-harness proposals retain their current generated content and filing behavior.
- Focused TEST-11531 and the existing proposal-filing suite pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`

## Recommended Commit Type

`feat`
