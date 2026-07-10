NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8ae8ee16-629f-4328-a797-47cb3e7a3293
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Promote/relocate rule-shaped memory/feedback_*.md content into .claude/rules or skills/hooks

bridge_kind: prime_proposal
Document: gtkb-wi5122-promote-peer-review-weighting-rule
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5122

target_paths: [".claude/rules/loyal-opposition.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Finding A2 of DELIB-202665929: memory/feedback_*.md carry imperative operating rules. Promote the one genuinely-unpromoted rule (peer-review weighting) into loyal-opposition.md; retire the two already-promoted redundant copies. Narrative-rule edit requiring a formal-artifact approval packet at implement time.

Work item description: Finding A2. memory/feedback_*.md carry skill-style frontmatter plus imperative How-to-apply procedures (de-facto rules). Promote load-bearing ones into rules/hooks per each file's own admission; retire the memory copy.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5122` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/rules/loyal-opposition.md`.

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
- `SPEC-INTAKE-bb25be` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265554` - Loyal Opposition NO-GO Verification Verdict - WI-4348 Phase-1 Rule-State Pointer Swaps
- `DELIB-20265553` - Loyal Opposition Review Verdict - gtkb-platform-sot-consolidation-wi4348-phase1-rule-state-strip
- `DELIB-202665599` - Applicability Preflight
- `DELIB-202665600` - Applicability Preflight
- `DELIB-20260672` - Agent SoT-read-discipline Phase-1 owner decisions (16-AUQ pass across 4 batches)

## Owner Decisions / Input

- `DELIB-202665930` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION` - active project authorization covering `WI-5122`.

## Proposed Scope

- Promote the genuinely-unpromoted operating rule in memory/feedback_peer_review_weighting_by_reliability.md (treat relayed peer review as hypotheses; convergence is not correctness; weight by demonstrated reliability, not source/confidence/count) into .claude/rules/loyal-opposition.md as a tracked review-conduct rule.
- Confirm the other two feedback files are already promoted (preflight guidance exists in file-bridge-protocol.md; project-URL resolution exists in canonical-terminology.md) and retire the redundant memory copies as non-authoritative notepad maintenance.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
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
| `SPEC-INTAKE-bb25be` | None of the three rule-shaped feedback files remains the sole home of an operating rule; each is promoted to a tracked rule or confirmed already-promoted and retired. |

## Acceptance Criteria

- The peer-review-weighting rule exists in a tracked .claude/rules artifact; no load-bearing operating rule remains only in memory/feedback_*.md.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/rules/loyal-opposition.md`

## Recommended Commit Type

`feat`
