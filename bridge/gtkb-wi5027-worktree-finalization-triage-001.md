NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop Prime Builder; interactive build envelope; approval_policy=never

# Implementation Proposal - Worktree finalization/commit-discipline lapse: 222 uncommitted bridge verdicts + accumulated cross-stream edits

bridge_kind: prime_proposal
Document: gtkb-wi5027-worktree-finalization-triage
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5027-BATCH-A1-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5027

target_paths: ["scripts/worktree_finalization_triage.py", "platform_tests/scripts/test_worktree_finalization_triage.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5027 Batch A1 first slice: implement a non-mutating worktree finalization triage planner that turns the accumulated dirty tree into deterministic per-stream dry-run action buckets without performing cleanup or commits.

Work item description: Triage 2026-07-05 found ~390 uncommitted worktree files: 222 untracked bridge/ verdicts and reports (append-only audit trail at risk of loss), ~93 modified code/test files (platform_tests 51, groundtruth-kb 26, scripts 16), ~40 cross-harness config/rule edits (.claude/.cursor/.codex/.agent/.api-harness), 1 deleted test (test_doctor_kill_switch_staleness.py), and ~9 junk/scratch files (.harness-tmp, .loyal-opposition, .temp_verdict_body, _temp_draft, draft bodies). Root cause: the multi-harness swarm writes bridge verdicts and source edits without committing; the auto-finalization sweep (WI-4889) plus sweep-commit are not keeping pace. Risks: audit-trail loss, future GO'd items quarantined on dirty target_paths, and commingled state that blocks clean per-thread commits. Not safely bulk-committable. Needs a per-stream finalization strategy or an enhanced auto-finalization/commit mechanism, plus a .gitignore/cleanup pass for the junk/scratch files.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5027` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/worktree_finalization_triage.py`, `platform_tests/scripts/test_worktree_finalization_triage.py`.

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
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5027-BATCH-A1-20260705` - active project authorization covering `WI-5027`.

## Proposed Scope

- Add a read-only worktree finalization triage planner that reads fresh git status and bridge-thread state at runtime and emits deterministic JSON/Markdown plan data only.
- Classify dirty paths into bridge-verdict chains, protected source/test/config edits, harness runtime projections, scratch/junk files, and blocked/manual-owner-review buckets without staging, deleting, committing, stashing, pruning, or resolving backlog records.
- Encode Batch A1 forbidden operations as explicit blocked outcomes so the planner cannot recommend destructive cleanup or committing another session stale work without specific apply evidence.
- Add focused platform tests with synthetic git fixtures proving no mutation, stable grouping, and blocked-action labeling.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Proposal, implementation report, and verification must use live bridge state and preserve the append-only bridge audit trail. |
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
| `GOV-WORK-TREE-HYGIENE-001` | python -m pytest platform_tests/scripts/test_worktree_finalization_triage.py -q --tb=short must prove report-first fresh-state classification, dry-run-only behavior, and no git mutation. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation report must cite PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5027-BATCH-A1-20260705 and show all changes stay within source/test_addition/cli_extension/governance_evidence scope. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before editing protected target_paths, Prime Builder must acquire implementation-start authorization from the latest GO for this bridge thread. |

## Acceptance Criteria

- The planner has a dry-run CLI entry point and produces stable JSON output for a synthetic dirty tree while leaving git status unchanged.
- Bridge verdict chain candidates are identified separately from source/test/config edits and from scratch/runtime noise, with reasons explaining why each bucket is safe, blocked, or owner-review-only.
- Batch A1 forbidden operations are represented as non-actionable blocked outcomes in output and tests.
- No source/test/config mutation occurs until a Loyal Opposition GO exists and implementation-start authorization is acquired for the exact target_paths.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/worktree_finalization_triage.py`
- `platform_tests/scripts/test_worktree_finalization_triage.py`

## Recommended Commit Type

`feat`
