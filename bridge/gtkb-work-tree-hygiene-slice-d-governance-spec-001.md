NEW

# Implementation Proposal - Work-Tree Hygiene Slice D Governance Spec

bridge_kind: prime_proposal
Document: gtkb-work-tree-hygiene-slice-d-governance-spec
Version: 001
Author: Codex Prime Builder, harness A
Date: 2026-06-30 UTC

author_identity: codex/prime-builder/auto-builder
author_harness_id: A
author_session_context_id: 019f18d4-b18b-7902-867d-a430595b0483
author_model: GPT-5 Codex
author_model_version: Codex desktop 2026-06-30
author_model_configuration: Codex desktop automation auto-builder; Prime Builder role; governed bridge proposal filing

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4356
work_item_ids: [WI-4356]

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-06-30-GOV-WORK-TREE-HYGIENE-001.json"]

implementation_scope: governance_spec_insertion
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
formal_artifact_approval_required: true

Recommended commit type: docs(governance)

---

## Summary

Implement WI-4356 Slice D by inserting the missing governed MemBase specification for the recurring work-tree hygiene and stash-stray-cleanup mechanism. The proposed new artifact is `GOV-WORK-TREE-HYGIENE-001`, a governance specification that preserves the already-implemented Slice A detector, Slice B dry-run CLI, and Slice C doctor check as the formal work-tree hygiene contract.

This proposal does not perform the MemBase insert. It requests Loyal Opposition review of the Slice D scope and records the implementation-time precondition: Prime Builder must have a matching exact-content formal-artifact approval packet for the proposed specification before mutating `groundtruth.db`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation may start only after a live GO, work-intent claim, implementation-start packet, and target-path match.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal carries concrete governing specification links and a spec-derived verification plan.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map the formal insert to executed readback and assertion verification.
- `GOV-STANDING-BACKLOG-001` - WI-4356 remains the canonical backlog authority for this Slice D work.
- `GOV-ARTIFACT-APPROVAL-001` - the governance-spec insert is a formal-artifact mutation and requires an exact-content approval packet.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner directive and implemented hygiene behavior must be preserved as durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation turns the existing detector, CLI, doctor check, bridge threads, and owner decisions into a formal artifact trail.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - stale workspace and stash findings are lifecycle-trigger candidates, not informal scratchpad notes.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the spec must require live git/stash/worktree/active-session reads rather than cached summaries.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this governance applies to GT-KB in `E:\GT-KB`, not to an adopter application repository.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - recurring hygiene belongs in deterministic services instead of repeated manual AI-session ceremony.
- `DELIB-20260809` - Loyal Opposition GO for `bridge/gtkb-work-tree-hygiene-mechanism-scoping-002.md`, approving the five-slice WI-4356 plan and requiring each implementation slice to file its own bridge proposal.
- `DELIB-20260867` - owner AUQ approval for WI-4356 implementation authorization, minted the active PAUTH used by this proposal.
- `bridge/gtkb-work-tree-hygiene-slice-a-detector-004.md` - VERIFIED Slice A read-only detector.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` - VERIFIED Slice B dry-run `gt hygiene strays` CLI.
- `bridge/gtkb-work-tree-hygiene-slice-c-doctor-check-004.md` - VERIFIED Slice C read-only `gt project doctor` visibility check.

## Owner Decisions / Input

The owner already authorized WI-4356 implementation through `DELIB-20260867` and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION`. That approval covers the work item and explicitly names governance-spec insertion in the scope narrative.

However, `DELIB-20260867` is a deliberation approval packet, not an exact-content approval packet for the proposed new governance specification. Implementation must therefore stop before `gt spec record` or equivalent MemBase mutation unless a valid packet for `GOV-WORK-TREE-HYGIENE-001` exists and its `full_content_sha256` matches the exact spec body being inserted.

## Requirement Sufficiency

Existing requirements are sufficient to file this Slice D proposal. They are not sufficient to execute the formal-artifact mutation without the exact-content approval packet described above.

The proposed specification must preserve these requirements:

- Stale working-tree work older than twelve hours is triaged by a different agent when the originating session is no longer active.
- Cleanup defaults are report-only or dry-run; destructive deletion, stash dropping, branch/worktree pruning, or committing another session's work requires owner-approved apply evidence for the specific batch.
- The implementation reads live source-of-truth state: git status, git stash list, git worktree state, active-session markers, and the current bridge/thread state where bridge linkage affects classification.
- Slice A/B/C verified surfaces remain the load-bearing implementation references: `scripts/hygiene/stray_detector.py`, `gt hygiene strays`, and the `gt project doctor` work-tree strays check.

## Proposed Scope

Insert a new MemBase governance specification with artifact id `GOV-WORK-TREE-HYGIENE-001`, type `governance`, and initial status `specified`.

The spec body should define:

- stale workspace and stash detection thresholds;
- deterministic classification states for stale tracked edits, untracked files, stashes, and orphaned worktrees;
- the dry-run-first rule for CLI and doctor surfaces;
- the owner-approval rule for destructive/apply behavior;
- live source-of-truth read requirements;
- implementation pointers to the VERIFIED Slice A/B/C surfaces; and
- machine-checkable assertions or equivalent verification references that can be used by future assertion runs.

Out of scope for this slice:

- enabling scheduled enforcement or hooks;
- applying cleanup, deleting files, pruning worktrees, dropping stashes, or creating commits;
- changing the Slice A/B/C source implementations;
- resolving WI-4356 as complete; and
- modifying any adopter application.

## Candidate Spec Content

The implementation report should include the exact content actually inserted. A suitable candidate body is:

```text
GOV-WORK-TREE-HYGIENE-001

GT-KB must preserve abandoned-session work-tree hygiene through deterministic, report-first tooling. Work-tree edits older than twelve hours whose originating session is no longer active are stale candidates for independent triage. Git stashes, orphaned worktrees, and untracked runtime-evidence directories are stale candidates when they exceed the configured threshold and are not attached to an active session.

The authoritative implementation surfaces are the verified WI-4356 slices:
1. Slice A read-only detector: scripts/hygiene/stray_detector.py.
2. Slice B dry-run CLI: gt hygiene strays.
3. Slice C doctor visibility check: gt project doctor work-tree strays check.

The detector and its consumers must read live git status, git stash, git worktree, active-session, and bridge/thread state at run time. They must not classify stale work from cached startup reports, automation memory, or stale dashboard summaries.

Default behavior is non-mutating. Destructive cleanup, stash dropping, branch/worktree pruning, untracked file deletion, or committing another session's stale work requires explicit owner-approved apply evidence for the specific batch being applied. Report-only detector, CLI, and doctor findings may be produced without owner approval.

Future scheduled or hook-based enforcement is out of scope until a separate bridge proposal receives GO and records the owner-approved apply policy.
```

## Specification-Derived Verification Plan

This is the spec-to-test mapping for Slice D. The slice is a formal MemBase
governance-spec insert rather than a source-code change, so verification is
readback, packet validation, and bridge preflight evidence instead of pytest.

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Begin implementation only after live GO, work-intent claim, implementation-start packet, and target-path authorization for `groundtruth.db` and the formal approval packet path. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-d-governance-spec`; expect `preflight_passed: true` and no missing required specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm the filed proposal retains Project Authorization, Project, Work Item, and parseable inline JSON `target_paths`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | After insert, read back `GOV-WORK-TREE-HYGIENE-001` via `gt spec show GOV-WORK-TREE-HYGIENE-001 --json` and verify type/status/body/pointers. |
| `GOV-ARTIFACT-APPROVAL-001` | Validate the exact-content packet with `python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-06-30-GOV-WORK-TREE-HYGIENE-001.json` before any MemBase mutation. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Confirm the inserted body requires live git/stash/worktree/session reads and rejects cached startup/automation memory as authority. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm all target paths are under `E:\GT-KB` and no adopter application path is touched. |
| `GOV-STANDING-BACKLOG-001` | Confirm WI-4356 remains open until Slice D is VERIFIED and Slice E is either completed or explicitly deferred by owner/governance decision. |

## Risk / Rollback

Risk is moderate because the implementation mutates formal governance state in MemBase. The exact-content approval packet and LO GO are the main controls.

Rollback is append-only: do not delete the inserted record. If the specification content is wrong after insertion, file a governed update/supersession under a new bridge thread and packet.

## Bridge Filing

This proposal is filed under `bridge/` as `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-001.md`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered bridge file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs(governance)` - the implementation creates/records a governance specification and its approval evidence, with no source-code change in this slice.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
