NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; Prime Builder A; default reasoning configuration

# Implementation Proposal - Keep one-shot preflight capture helpers out of protected source directories

bridge_kind: prime_proposal
Document: gtkb-wi5301-retire-one-shot-preflight-helper
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5301

target_paths: ["scripts/_capture_preflight_outputs.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Bounded retirement of an unowned one-shot helper from protected scripts, contingent on independent GO and exact destructive-cleanup authority.

Work item description: The live tree contains untracked scripts/_capture_preflight_outputs.py, a July 1 one-shot helper hard-coded to WI-4943/WI-4944 that writes bridge/_preflight_capture_wi4943_wi4944.txt and has no repository consumer. Classify and remove this stale helper under exact cleanup authority, and route any future transient command-output capture to ignored .gtkb-state rather than protected scripts/ or bridge/ paths.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5301` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/_capture_preflight_outputs.py`.

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

- `DELIB-20265771` - Loyal Opposition GO Verdict - WI-4728 Duplicate Project Record Merge
- `DELIB-202666317` - Owner approves WI-5307 shared enforcement baseline disposition
- `DELIB-20265722` - Loyal Opposition Review - WI-4683 Activity Vocabulary Reconcile Ops Proposal
- `DELIB-20261084` - Loyal Opposition Review - Slice 2A Read-Discipline
- `DELIB-20261227` - Loyal Opposition Review - Slice 2A Read-Discipline

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5301`.

## Proposed Scope

- Classify scripts/_capture_preflight_outputs.py as a stale July 1 one-shot helper with no repository consumer and hard-coded closed WI-4943/WI-4944 output behavior.
- After independent GO and separate exact owner destructive-cleanup authorization, remove only scripts/_capture_preflight_outputs.py; do not delete or mutate any generated output, bridge file, source, database, or unrelated scratch path.
- Future transient preflight-output capture belongs under ignored .gtkb-state and is out of this deletion-only implementation scope.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Before deletion, prove the helper is untracked, hard-coded to WI-4943/WI-4944, and has no repository consumer; after deletion, prove the exact path is absent and Git no longer reports it. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independently review the exact one-path before/after inventory and repository reference scan; no synthetic or self-review evidence is acceptable. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- scripts/_capture_preflight_outputs.py is absent after the authorized cleanup.
- A repository reference scan finds no consumer of _capture_preflight_outputs and no product or test behavior is impaired.
- No path other than scripts/_capture_preflight_outputs.py is deleted, mutated, staged, or finalized.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/_capture_preflight_outputs.py`

## Recommended Commit Type

`feat`
