NEW

# Defect-Fix Proposal - Restore peer-solution defer-trigger wording

bridge_kind: prime_proposal
Document: gtkb-wi5360-peer-solution-defer-trigger-wording
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5360

target_paths: [".claude/rules/peer-solution-advisory-loop.md"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Restore one corrupted word in the peer-solution `defer` procedure. The current
worktree says, "When the daemon condition is met"; the canonical procedure and
the surrounding examples define a general milestone/evidence trigger, so the
sentence must read, "When the trigger condition is met."

The file has no other worktree hunk. Implementation removes only this one-line
semantic drift by restoring the HEAD wording. It does not change dispatcher,
TAFE, harness, advisory, deliberation, or deferral behavior.

## Specification Links

- `DCL-PEER-SOLUTION-OWNER-GATE-001` - Peer-solution defer decisions use the procedure's general trigger semantics, not a dispatcher-daemon event.
- `GOV-WORK-TREE-HYGIENE-001` - The unowned one-line drift must be classified and repaired without absorbing another path.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The semantic corruption is preserved as WI-5360 and this independently reviewable proposal.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected rule repair requires independent GO, matching claim/start authority, reporting, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The exact one-file/one-line scope is linked to its governing procedure constraint.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, WI, and target path are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent review verifies the exact wording and one-line diff closure.
- `GOV-STANDING-BACKLOG-001` - WI-5360 is the durable owner of this defect.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The repair and verification remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-202666274` - The owner authorized all required modernization/tree-stabilization work while retaining bridge and mechanical Git gates.

## Owner Decisions / Input

No new owner decision is required. The tree-stabilization project PAUTH covers
this exact rule repair. Git staging/commit, cleanup, dispatcher/TAFE/harness
mutation, release, and deployment remain outside scope.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-PEER-SOLUTION-OWNER-GATE-001` links the
operative procedure and its defer classification. The surrounding rule text
already defines a general `DEFER-TRIGGER CONDITION`; no new requirement is
needed.

## Proposed Scope

1. In `.claude/rules/peer-solution-advisory-loop.md`, replace only `When the daemon condition is met` with `When the trigger condition is met`.
2. Preserve every other byte and line in the file.
3. Do not change daemon terminology where the dispatcher daemon is actually the subject.
4. Fail closed if the pre-implementation diff contains any second hunk or the target line has changed.
5. Exclude all other worktree paths and all Git/dispatcher/TAFE/harness operations.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Correct defer semantics | Search the `defer` section for `DEFER-TRIGGER CONDITION` and `When the trigger condition is met` | Both phrases exist in the same procedure; `daemon condition` is absent. |
| Exact one-line repair | `git diff -- .claude/rules/peer-solution-advisory-loop.md` | Empty diff after implementation because the canonical HEAD wording is restored. |
| Patch hygiene | `git diff --check -- .claude/rules/peer-solution-advisory-loop.md` | Exit zero. |
| RC inventory ownership | Rerun the development-environment inventory drift checker | This path is no longer listed; unrelated blockers remain independently owned. |

## Acceptance Criteria

1. The defer procedure says `trigger condition`, not `daemon condition`.
2. The target file has no remaining worktree diff.
3. No second file or behavior changes.
4. Independent VERIFIED precedes exact mechanical finalization.

## Risk / Rollback

Risk is minimal and bounded to one word. The repair restores canonical HEAD and
the procedure's internal terminology. If rollback were required, it would need
a new governed proposal because reintroducing `daemon condition` would recreate
the defect; no broad reset or cleanup is permitted.

## Bridge Filing

This proposal is filed as the next append-only numbered file for
`gtkb-wi5360-peer-solution-defer-trigger-wording`. Dispatcher/TAFE state plus
the numbered file chain remain workflow authority; no manual routing or direct
harness contact occurs.

## Recommended Commit Type

`docs` - restores one rule word without changing executable code.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
