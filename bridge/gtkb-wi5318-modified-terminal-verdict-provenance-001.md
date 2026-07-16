NEW

# WI-5318 Modified Terminal-Verdict Provenance Guard

bridge_kind: prime_proposal
Document: gtkb-wi5318-modified-terminal-verdict-provenance
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-15 UTC

author_identity: Codex A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5.5
author_model_version: 5.5
author_model_configuration: Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5318

target_paths: ["groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py", "platform_tests/scripts/test_worktree_finalization_triage.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Correct the report-only worktree finalization planner so terminal bridge status
does not masquerade as ownership of modified audit bytes. The live planner
currently labels three staged, substantial rewrites of already committed
`VERIFIED` verdict files as `safe_commit`, even though none of their staged
blobs exists in Git history and no item-specific finalization evidence owns
those rewrites.

The bounded fix keeps a newly created, untracked terminal verdict eligible for
the existing evidence-gated `safe_commit` candidate path. A tracked
modification or deletion of an existing terminal verdict must instead remain
`manual_owner_review`. This proposal changes classification only; it does not
alter the index, commit any verdict, or add an actuator bypass.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — terminal status belongs to the append-only
  bridge chain and cannot authorize an unexplained rewrite of an existing entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  implementation proposal to cite its governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the PAUTH,
  project, and work-item linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent
  verification to execute tests derived from the linked specifications.
- `GOV-WORK-TREE-HYGIENE-001` — requires explicit dirty-path ownership and
  evidence-backed finalization without absorbing another session's work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — requires the work item, proposal,
  implementation, test, and verdict evidence to remain traceably linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — distinguishes a terminal workflow
  state from a later candidate Git mutation of the underlying artifact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires this discovered risk and
  corrective work to be preserved as durable governed artifacts.

## Prior Deliberations

- `INTAKE-afbe241e` — universal author/provenance metadata is relevant evidence,
  but metadata on a verdict does not prove ownership of later modified bytes.
- `INTAKE-9314e628` — defines required VERIFIED verdict fields; this proposal
  preserves that status contract while separating it from Git finalization
  authority for a modified artifact.

## Owner Decisions / Input

The owner directed Prime Builder to fix blocking issues, inventory ownership,
record flaws as work items, and finalize only independently verified scopes
with exact mechanical authority until the worktree is clean. The active Tree
Stabilization PAUTH covers this source/test repair. No additional owner decision
is required to request independent review.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-WORK-TREE-HYGIENE-001` requires
specific disposition and evidence before mutation, while
`GOV-FILE-BRIDGE-AUTHORITY-001` defines terminal bridge state without granting
rewrite authority.

## Spec-Derived Verification Plan

- `GOV-WORK-TREE-HYGIENE-001`:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_worktree_finalization_triage.py -q --tb=short`
  must prove a tracked modified or deleted terminal verdict is
  `manual_owner_review`, while a new untracked terminal verdict remains an
  evidence-gated `safe_commit` candidate.
- `GOV-FILE-BRIDGE-AUTHORITY-001`:
  the same suite must preserve recognized bridge status and append-only chain
  reporting while refusing to infer ownership from the `VERIFIED` token alone.
- Proposal/linkage and verification DCLs:
  mandatory applicability and clause preflights must pass with zero blocking
  gaps, and the post-implementation report must carry the executed command and
  observed results into independent verification.
- Artifact-oriented ADR/DCL/GOV requirements:
  `gt backlog show WI-5318 --json` and
  `gt bridge threads --wi WI-5318 --json --compact` must expose the durable
  work-item/proposal lifecycle and its current state without relying on
  scratch files.
- Hygiene regression check:
  `python scripts/worktree_finalization_triage.py --root E:\GT-KB --format json`
  must report the three current tracked modified terminal verdicts as manual
  review, with no index or worktree mutation.

## Risk / Rollback

The principal risk is over-tightening the planner so genuinely new terminal
verdicts lose their existing finalization candidate path. The regression suite
must cover both sides. Rollback is a single exact two-file commit; the report-
only planner has no destructive side effect and no staged verdict is touched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5318-modified-terminal-verdict-provenance`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the change removes an unsafe provenance inference in the
finalization classifier.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
