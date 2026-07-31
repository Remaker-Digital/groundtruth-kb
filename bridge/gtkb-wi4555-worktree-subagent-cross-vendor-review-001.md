NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Omnigent alignment worktree subagent cross-vendor review

bridge_kind: prime_proposal
Document: gtkb-wi4555-worktree-subagent-cross-vendor-review
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-OMNIGENT-ALIGNMENT
Work Item: WI-4555

target_paths: ["config/dispatcher/swarm-worktree-review.toml", "scripts/swarm_worktree_review_plan.py", "platform_tests/scripts/test_swarm_worktree_review_plan.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OMNIGENT-WORKTREE-CROSS-VENDOR-REVIEW-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement a planning/control-plane slice for worktree-per-subagent execution with cross-vendor review routing, modeled after Omnigent Polly. This proposal does not spawn subagents or mutate git worktrees; it creates the config contract, planner, and evidence report needed before any later runtime orchestration.

This proposal itself will be filed as `bridge/gtkb-wi4555-worktree-subagent-cross-vendor-review-001.md`, an append-only numbered bridge file in the versioned bridge file chain.

## Requirement Sufficiency

Existing requirements are sufficient for a non-runtime planning slice. The active Omnigent Alignment PAUTH covers WI-4555, and the owner directive is to emulate overlapping Omnigent capability shapes while preserving GT-KB bridge and review independence.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete spec links in the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `ADR-CROSS-HARNESS-PARITY-001` - cross-vendor review must preserve equivalent review authority or typed waivers.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - worktree review routing must not bypass bridge lifecycle states.

## Prior Deliberations

- `DELIB-OMNIGENT-ADVISORY-20260614` - Omnigent advisory source context.
- `DELIB-20263229` - owner-grilling-gate Omnigent alignment direction.
- `DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610` - bridge-orchestration vision context.
- `DELIB-20265586` - snapshot-bound project authorization.

## Owner Decisions / Input

- `PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23` - active authorization covering WI-4555.

## Proposed Scope

- Add a disabled-by-default cross-vendor worktree review planning config.
- Add a read-only planner that maps candidate implementation lanes to isolated worktree needs, reviewer-vendor separation, bridge-status routing, and finalization constraints.
- Emit a governed report identifying which pieces are already satisfied by current dispatcher/bridge behavior and which require future owner approval.
- Add tests proving the planner does not create worktrees, spawn agents, invoke harnesses, or bypass bridge review.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active WI-4555 PAUTH and target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected mutation occurs before GO and implementation-start. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests prove planner output preserves NEW/GO/report/VERIFIED bridge sequencing. |
| `ADR-CROSS-HARNESS-PARITY-001` | Tests/report confirm reviewer separation is expressed as harness/vendor constraints with typed-waiver handling. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run live applicability preflight and confirm no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Include exact targeted pytest output in the implementation report. |

## Acceptance Criteria

- Worktree/subagent orchestration remains planning-only and disabled-by-default.
- Planner output names worktree isolation, reviewer separation, bridge lifecycle, and finalization requirements.
- Tests prove no worktree creation, no harness invocation, and no bridge bypass.

## Risks / Rollback

Risk is moderate because this work shapes future swarm execution. Mitigation is planning-only implementation and explicit non-launch tests. Rollback is a revert of config, planner, tests, and report.

## Files Expected To Change

- `config/dispatcher/swarm-worktree-review.toml`
- `scripts/swarm_worktree_review_plan.py`
- `platform_tests/scripts/test_swarm_worktree_review_plan.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OMNIGENT-WORKTREE-CROSS-VENDOR-REVIEW-*.md`

## Recommended Commit Type

`feat`
