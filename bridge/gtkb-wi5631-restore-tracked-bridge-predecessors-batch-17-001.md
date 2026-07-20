NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Restore 17 missing tracked bridge predecessors byte-exactly

bridge_kind: prime_proposal
Document: gtkb-wi5631-restore-tracked-bridge-predecessors-batch-17
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5631

target_paths: ["bridge/gtkb-wi5178-operation-time-authority-enforcement-004.md", "bridge/gtkb-wi5211-failed-verified-finalization-repair-003.md", "bridge/gtkb-wi5328-session-envelope-role-writeback-008.md", "bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-002.md", "bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-006.md", "bridge/gtkb-wi5345-failed-verified-finalization-repair-003.md", "bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-002.md", "bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-006.md", "bridge/gtkb-wi5351-failed-verified-finalization-repair-003.md", "bridge/gtkb-wi5353-implementation-start-harness-selector-002.md", "bridge/gtkb-wi5354-git-lifecycle-acceptance-baseline-002.md", "bridge/gtkb-wi5355-startup-payload-latency-cliff-002.md", "bridge/gtkb-wi5355-startup-payload-latency-cliff-004.md", "bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-002.md", "bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md", "bridge/gtkb-wi5360-peer-solution-defer-trigger-wording-002.md", "bridge/gtkb-wi5363-applicability-scope-semantics-002.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Restore exactly the 17 missing tracked numbered bridge predecessors from their pinned committed blobs through the independently verified exact-path service, preserving the index and every unrelated worktree byte.

Work item description: The shared worktree has exactly 17 tracked numbered bridge predecessor files in unstaged-deletion state. No archive copies exist, every deleted file is still referenced by a later live numbered artifact, and at least one live reviewer has documented the resulting incomplete version count. After WI-5474 is independently VERIFIED, restore only the exact 17 immutable committed blobs through the governed restore-deleted-path service, one path at a time, preserving the Git index and every unrelated status byte. Stop on any manifest, blob, status, worker, lock, or unrelated-state drift; perform no broad restore, staging, commit, dispatcher/runtime, MemBase, credential, push, deployment, or release mutation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5631` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5178-operation-time-authority-enforcement-004.md`, `bridge/gtkb-wi5211-failed-verified-finalization-repair-003.md`, `bridge/gtkb-wi5328-session-envelope-role-writeback-008.md`, `bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-002.md`, `bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-006.md`, `bridge/gtkb-wi5345-failed-verified-finalization-repair-003.md`, `bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-002.md`, `bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-006.md`, `bridge/gtkb-wi5351-failed-verified-finalization-repair-003.md`, `bridge/gtkb-wi5353-implementation-start-harness-selector-002.md`, `bridge/gtkb-wi5354-git-lifecycle-acceptance-baseline-002.md`, `bridge/gtkb-wi5355-startup-payload-latency-cliff-002.md`, `bridge/gtkb-wi5355-startup-payload-latency-cliff-004.md`, `bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-002.md`, `bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md`, `bridge/gtkb-wi5360-peer-solution-defer-trigger-wording-002.md`, `bridge/gtkb-wi5363-applicability-scope-semantics-002.md`.

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
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667001` - NO-GO — WI-5370 missing-targets WI-5316 finalization repair (report 003)
- `DELIB-202667009` - Loyal Opposition Corrected NO-GO - WI-5370 Missing-Targets Repair (Target Superseded, Not Malformed)
- `DELIB-202667004` - Loyal Opposition Corrected Verdict (review_no_action) - NO-GO - WI-5370 Stale-Target Repair Proposal (wi5336-004 is live in-flight bridge state, not a terminal artifact)
- `DELIB-202666567` - Loyal Opposition Corrected Verdict (review_no_action) - GO - WI-5354 Failed VERIFIED Finalization Repair
- `DELIB-202666984` - NO-GO — WI-5362 Parity Entrypoint Import Shadowing (finalization-mechanics blocker)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5631`.

## Proposed Scope

- Hard predecessor: do not execute any live restore until WI-5474 exact-path tracked-file restore is latest VERIFIED; a GO verdict alone is insufficient.
- Immediately before execution require zero live dispatcher workers, no .git/index.lock, an empty staged index, and an unchanged exact 17-path unstaged-deletion manifest; do not stop workers, quiesce, or reconfigure dispatcher state to manufacture these conditions.
- Invoke only the independently VERIFIED production exact-path restore service, one declared path per operation, pinned to source commit 74bf972770862d462261b2a6eaddc9bea681ca4b; stop at the first non-PASS without attempting later paths.
- Each path is an append-only numbered bridge predecessor still required by a later live chain; restore it in place byte-exactly and do not create an archive substitute.
- Manifest: bridge/gtkb-wi5178-operation-time-authority-enforcement-004.md source blob dcc8cab7a192cdfb32abea8c72f758564accd8bb status NO-GO.
- Manifest: bridge/gtkb-wi5211-failed-verified-finalization-repair-003.md source blob 0c1a1d043d37dc54c127dce9d06380a56938bdc2 status GO.
- Manifest: bridge/gtkb-wi5328-session-envelope-role-writeback-008.md source blob fb7259e9c317bd0aa4587c01e97f4357e3ed32c4 status NO-GO.
- Manifest: bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-002.md source blob 7624fcb534875b919e6347059a2593436d1b6a32 status GO.
- Manifest: bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-006.md source blob 10b495ea8cbe6341deb46e1c852b9e7a4d5cefdc status NO-GO.
- Manifest: bridge/gtkb-wi5345-failed-verified-finalization-repair-003.md source blob 570dfd81d0fdff866240e54eda51fd37ecdf1784 status GO.
- Manifest: bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-002.md source blob 1d9029de7d898e666c27620ff0e888f3663a33e4 status GO.
- Manifest: bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-006.md source blob c74ff0b9ae35ded77a2b80e2c0522373a3a1daa2 status NO-GO.
- Manifest: bridge/gtkb-wi5351-failed-verified-finalization-repair-003.md source blob c547aa9bd603d713f8bfbc038556be92120fe43d status GO.
- Manifest: bridge/gtkb-wi5353-implementation-start-harness-selector-002.md source blob 91737871ba65b400d8db4b50507e26bccb91c47b status GO.
- Manifest: bridge/gtkb-wi5354-git-lifecycle-acceptance-baseline-002.md source blob 39d2ad30703ae22feae2688e814992d66aa883f2 status GO.
- Manifest: bridge/gtkb-wi5355-startup-payload-latency-cliff-002.md source blob 8dc4e098ecc0070874fb1b644a966f6740b4bf13 status GO.
- Manifest: bridge/gtkb-wi5355-startup-payload-latency-cliff-004.md source blob 084a65ae2d0042c73c00bd40b5cd2209c9041e6f status NO-GO.
- Manifest: bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-002.md source blob 5ec9c66198fbf92088dddf4a0a1d2ba239204219 status GO.
- Manifest: bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md source blob 0527a2e07d5db2da72b6f26cec125f9b1315ae1c status NO-GO.
- Manifest: bridge/gtkb-wi5360-peer-solution-defer-trigger-wording-002.md source blob d6b7c219f4dbe175ba488b2188103cc15f073508 status GO.
- Manifest: bridge/gtkb-wi5363-applicability-scope-semantics-002.md source blob fe9bfa675424b51ffc08b9d0903385d428606696 status GO.
- Do not stage, commit, push, mutate dispatcher/runtime/TAFE/MemBase/configuration, restore any undeclared path, perform a broad Git restore, or change any unrelated worktree byte.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5631; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "The shared worktree has exactly 17 tracked numbered bridge predecessor files in unstaged-deletion state. No archive copies exist, every deleted file is still referenced by a later live numbered artifact, and at least one live reviewer has documented the resulting incomplete version count. After WI-5474 is independently VERIFIED, restore only the exact 17 immutable committed blobs through the governed restore-deleted-path service, one path at a time, preserving the Git index and every unrelated status byte. Stop on any manifest, blob, status, worker, lock, or unrelated-state drift; perform no broad restore, staging, commit, dispatcher/runtime, MemBase, credential, push, deployment, or release mutation.",
  "after_behavior": "Restore exactly the 17 missing tracked numbered bridge predecessors from their pinned committed blobs through the independently verified exact-path service, preserving the index and every unrelated worktree byte.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5631",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "bridge/gtkb-wi5178-operation-time-authority-enforcement-004.md",
      "bridge/gtkb-wi5211-failed-verified-finalization-repair-003.md",
      "bridge/gtkb-wi5328-session-envelope-role-writeback-008.md",
      "bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-002.md",
      "bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-006.md",
      "bridge/gtkb-wi5345-failed-verified-finalization-repair-003.md",
      "bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-002.md",
      "bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-006.md",
      "bridge/gtkb-wi5351-failed-verified-finalization-repair-003.md",
      "bridge/gtkb-wi5353-implementation-start-harness-selector-002.md",
      "bridge/gtkb-wi5354-git-lifecycle-acceptance-baseline-002.md",
      "bridge/gtkb-wi5355-startup-payload-latency-cliff-002.md",
      "bridge/gtkb-wi5355-startup-payload-latency-cliff-004.md",
      "bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-002.md",
      "bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md",
      "bridge/gtkb-wi5360-peer-solution-defer-trigger-wording-002.md",
      "bridge/gtkb-wi5363-applicability-scope-semantics-002.md"
    ],
    "linked_specifications": [
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-GIT-BRANCH-BINDING-PROMOTION-001",
      "GOV-WORK-TREE-HYGIENE-001"
    ]
  },
  "expected_result": {
    "summary": "Restore exactly the 17 missing tracked numbered bridge predecessors from their pinned committed blobs through the independently verified exact-path service, preserving the index and every unrelated worktree byte.",
    "scope": [
      "Hard predecessor: do not execute any live restore until WI-5474 exact-path tracked-file restore is latest VERIFIED; a GO verdict alone is insufficient.",
      "Immediately before execution require zero live dispatcher workers, no .git/index.lock, an empty staged index, and an unchanged exact 17-path unstaged-deletion manifest; do not stop workers, quiesce, or reconfigure dispatcher state to manufacture these conditions.",
      "Invoke only the independently VERIFIED production exact-path restore service, one declared path per operation, pinned to source commit 74bf972770862d462261b2a6eaddc9bea681ca4b; stop at the first non-PASS without attempting later paths.",
      "Each path is an append-only numbered bridge predecessor still required by a later live chain; restore it in place byte-exactly and do not create an archive substitute.",
      "Manifest: bridge/gtkb-wi5178-operation-time-authority-enforcement-004.md source blob dcc8cab7a192cdfb32abea8c72f758564accd8bb status NO-GO.",
      "Manifest: bridge/gtkb-wi5211-failed-verified-finalization-repair-003.md source blob 0c1a1d043d37dc54c127dce9d06380a56938bdc2 status GO.",
      "Manifest: bridge/gtkb-wi5328-session-envelope-role-writeback-008.md source blob fb7259e9c317bd0aa4587c01e97f4357e3ed32c4 status NO-GO.",
      "Manifest: bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-002.md source blob 7624fcb534875b919e6347059a2593436d1b6a32 status GO.",
      "Manifest: bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-006.md source blob 10b495ea8cbe6341deb46e1c852b9e7a4d5cefdc status NO-GO.",
      "Manifest: bridge/gtkb-wi5345-failed-verified-finalization-repair-003.md source blob 570dfd81d0fdff866240e54eda51fd37ecdf1784 status GO.",
      "Manifest: bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-002.md source blob 1d9029de7d898e666c27620ff0e888f3663a33e4 status GO.",
      "Manifest: bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-006.md source blob c74ff0b9ae35ded77a2b80e2c0522373a3a1daa2 status NO-GO.",
      "Manifest: bridge/gtkb-wi5351-failed-verified-finalization-repair-003.md source blob c547aa9bd603d713f8bfbc038556be92120fe43d status GO.",
      "Manifest: bridge/gtkb-wi5353-implementation-start-harness-selector-002.md source blob 91737871ba65b400d8db4b50507e26bccb91c47b status GO.",
      "Manifest: bridge/gtkb-wi5354-git-lifecycle-acceptance-baseline-002.md source blob 39d2ad30703ae22feae2688e814992d66aa883f2 status GO.",
      "Manifest: bridge/gtkb-wi5355-startup-payload-latency-cliff-002.md source blob 8dc4e098ecc0070874fb1b644a966f6740b4bf13 status GO.",
      "Manifest: bridge/gtkb-wi5355-startup-payload-latency-cliff-004.md source blob 084a65ae2d0042c73c00bd40b5cd2209c9041e6f status NO-GO.",
      "Manifest: bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-002.md source blob 5ec9c66198fbf92088dddf4a0a1d2ba239204219 status GO.",
      "Manifest: bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md source blob 0527a2e07d5db2da72b6f26cec125f9b1315ae1c status NO-GO.",
      "Manifest: bridge/gtkb-wi5360-peer-solution-defer-trigger-wording-002.md source blob d6b7c219f4dbe175ba488b2188103cc15f073508 status GO.",
      "Manifest: bridge/gtkb-wi5363-applicability-scope-semantics-002.md source blob fe9bfa675424b51ffc08b9d0903385d428606696 status GO.",
      "Do not stage, commit, push, mutate dispatcher/runtime/TAFE/MemBase/configuration, restore any undeclared path, perform a broad Git restore, or change any unrelated worktree byte."
    ],
    "acceptance_criteria": [
      "At operation time the exact 17 declared paths are still the complete unstaged-deletion manifest for this batch and each pinned source blob resolves from commit 74bf972770862d462261b2a6eaddc9bea681ca4b.",
      "All 17 paths are restored byte-exactly through the production exact-path service, with one structured PASS result per path and immediate stop on any non-PASS.",
      "The staged index remains byte-identical and empty, no Git lock is created or left behind, and every unrelated porcelain status record remains byte-identical after every operation.",
      "All affected numbered bridge chains are complete after restoration and the total dirty-worktree entry count falls by exactly 17, solely because the 17 tracked deletions disappear.",
      "Independent LO verifies the exact manifest, source commit and blobs, production-service evidence, chain completeness, and nonimpairment before any focused commit or later cleanup batch."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify every restored file is the exact historical numbered predecessor at its original bridge path, every later chain remains append-only and complete, and no archive or aggregate queue artifact substitutes for the canonical predecessor. |
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
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | Use TEST-11676 in an in-root isolated fixture to reproduce all 17 exact deletions and pinned blobs through the production service; assert one-path-only restore, source-ref resolution, byte identity, fail-closed drift behavior, and unchanged index/unrelated status after every operation. |
| `GOV-WORK-TREE-HYGIENE-001` | Capture before/after full porcelain bytes, staged-index tree identity, index-lock absence, exact dirty-entry count, and per-path structured results; require exactly a 17-entry reduction and no unrelated delta. |

## Acceptance Criteria

- At operation time the exact 17 declared paths are still the complete unstaged-deletion manifest for this batch and each pinned source blob resolves from commit 74bf972770862d462261b2a6eaddc9bea681ca4b.
- All 17 paths are restored byte-exactly through the production exact-path service, with one structured PASS result per path and immediate stop on any non-PASS.
- The staged index remains byte-identical and empty, no Git lock is created or left behind, and every unrelated porcelain status record remains byte-identical after every operation.
- All affected numbered bridge chains are complete after restoration and the total dirty-worktree entry count falls by exactly 17, solely because the 17 tracked deletions disappear.
- Independent LO verifies the exact manifest, source commit and blobs, production-service evidence, chain completeness, and nonimpairment before any focused commit or later cleanup batch.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `bridge/gtkb-wi5178-operation-time-authority-enforcement-004.md`
- `bridge/gtkb-wi5211-failed-verified-finalization-repair-003.md`
- `bridge/gtkb-wi5328-session-envelope-role-writeback-008.md`
- `bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-002.md`
- `bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-006.md`
- `bridge/gtkb-wi5345-failed-verified-finalization-repair-003.md`
- `bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-002.md`
- `bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-006.md`
- `bridge/gtkb-wi5351-failed-verified-finalization-repair-003.md`
- `bridge/gtkb-wi5353-implementation-start-harness-selector-002.md`
- `bridge/gtkb-wi5354-git-lifecycle-acceptance-baseline-002.md`
- `bridge/gtkb-wi5355-startup-payload-latency-cliff-002.md`
- `bridge/gtkb-wi5355-startup-payload-latency-cliff-004.md`
- `bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-002.md`
- `bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md`
- `bridge/gtkb-wi5360-peer-solution-defer-trigger-wording-002.md`
- `bridge/gtkb-wi5363-applicability-scope-semantics-002.md`

## Recommended Commit Type

`feat`
