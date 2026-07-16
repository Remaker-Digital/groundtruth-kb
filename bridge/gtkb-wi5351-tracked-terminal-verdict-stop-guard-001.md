NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bff-bdfc-7c42-a63c-1663409f04d7
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Stop finalization repair on tracked modified or deleted terminal verdicts

bridge_kind: prime_proposal
Document: gtkb-wi5351-tracked-terminal-verdict-stop-guard
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5351

target_paths: ["scripts/per_thread_finalization_repair.py", "platform_tests/scripts/test_per_thread_finalization_repair.py", "docs/procedures/per-thread-finalization-repair.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Move the post-WI-5116 mixed-provenance planner defect onto a valid open child and harden the report-only per-thread finalization planner so tracked modified or deleted terminal VERIFIED verdict files always STOP instead of becoming repair candidates.

Work item description: After WI-5116 was independently VERIFIED, resolved, and committed at b1750002, the live per-thread finalization planner still classified gtkb-wi4567-bridge-proposal-filing-service as terminal_verified_repair_candidate even though its only dirty path is the tracked modified terminal verdict bridge/gtkb-wi4567-bridge-proposal-filing-service-004.md. Tracked modified or deleted terminal VERIFIED verdicts have mixed provenance and must force a STOP classification, never an automatic repair candidate. A proposal and GO were mistakenly filed against already-terminal WI-5116; this child provides valid open work-item traceability for the post-resolution defect. Scope is exactly scripts/per_thread_finalization_repair.py, its focused test module, and the runbook. Do not stage, commit, delete, restore, or finalize the live WI-4567 verdict or any other terminal bridge dirt.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5351` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/per_thread_finalization_repair.py`, `platform_tests/scripts/test_per_thread_finalization_repair.py`, `docs/procedures/per-thread-finalization-repair.md`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
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

- `DELIB-20265762` - Loyal Opposition NO-GO Verification Verdict - WI-4723 VERIFIED finalization index-lock retry
- `DELIB-20265758` - Verdict
- `DELIB-202666157` - WI-5203 Dispatcher Targeted Reoffer and Neutral NO-ACTION Completion - Loyal Opposition Proposal Review: GO
- `DELIB-20265732` - Loyal Opposition Verification Verdict: WI-4691 Verified Finalization Repair
- `DELIB-20265389` - Verdict for gtkb-wi4618-non-activatable-go-scan-reconciliation

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5351`.

## Proposed Scope

- Supersede the implementation intent of gtkb-wi5116-tracked-terminal-verdict-stop-guard without treating its GO against resolved WI-5116 as implementation authority.
- Update the planner so any tracked modified or deleted terminal VERIFIED bridge file in a thread forces mixed_provenance_stop or an equivalent explicit STOP class.
- Add focused tracked-modified and tracked-deleted fixtures while preserving the clean untracked terminal candidate behavior.
- Update the runbook STOP taxonomy and verify the live WI-4567 thread is STOP-classified through the report-only CLI.
- Do not stage, commit, delete, restore, finalize, or otherwise mutate the WI-4567 verdict or any terminal bridge dirt; do not mutate dispatcher/TAFE/runtime/eligibility.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Run the focused planner test module and the live report-only planner command; assert mixed-provenance STOP for tracked dirty terminal verdicts, retained clean-candidate behavior, and zero mutation. |
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

## Acceptance Criteria

- Tracked modified and tracked deleted terminal VERIFIED verdict fixtures never produce terminal_verified_repair_candidate and instead produce an explicit STOP class.
- Existing clean untracked terminal repair-candidate coverage remains green.
- The live gtkb-wi4567-bridge-proposal-filing-service case is report-only STOP-classified with no Git/index/file mutation.
- Focused pytest and Ruff check/format gates pass on the three exact targets.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/per_thread_finalization_repair.py`
- `platform_tests/scripts/test_per_thread_finalization_repair.py`
- `docs/procedures/per-thread-finalization-repair.md`

## Recommended Commit Type

`feat`
