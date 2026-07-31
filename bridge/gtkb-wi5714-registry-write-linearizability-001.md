NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Make registry control-plane writes linearizable under concurrent Prime Builder workers

bridge_kind: prime_proposal
Document: gtkb-wi5714-registry-write-linearizability
Version: 001
Date: 2026-07-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5714

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_registry_control_plane.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make registry amendments linearizable under concurrent Prime Builder writers by binding each read-modify-write to its source generation and retrying boundedly from coherent fresh snapshots.

Work item description: The registry control plane has a cooperative file lock, coherent read barrier, atomic canonical and packaged replacement, projection journaling, and recovery. However amend_artifact reads a full generation under one lock acquisition and later calls apply_registry_transaction under another without an expected prior generation digest. Two PB workers can therefore read generation G, amend different records, serialize their writes, and let the second stale full-generation payload overwrite the first accepted amendment. Make every registry read-modify-write operation linearizable or generation-CAS-bound, return a bounded actionable retry on conflict, preserve both non-overlapping changes, and add deterministic multi-process coverage. Keep owner hand-edit observation and admission in WI-5696 and isolated Git worktrees in the Git-lifecycle project.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5714` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, `groundtruth-kb/tests/test_registry_control_plane.py`.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` - auto-linked governing or work-item specification.
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
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - auto-linked governing or work-item specification.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667268` - LO Review - Proposal NO-GO (gtkb-wi5510-per-harness-active-worker-concurrency-cap)
- `DELIB-202666773` - WI-5510 concurrency-cap increase sequenced after git-lock-contention fix
- `DELIB-20260710-GTKB-MODERNIZATION-GIT-LIFECYCLE-WORK-PACKET` - Approve GT-KB Modernization Governed Git Lifecycle work packet
- `DELIB-202667387` - Verdict
- `DELIB-202666144` - Loyal Opposition Verdict — WI-5189 REVISED-008 Scoped-Finalization Report (NO-GO on finalization: the waiver-scoped commit is broken in isolation)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729` - active project authorization covering `WI-5714`.

## Proposed Scope

- Add a typed generation-conflict error beneath RegistryAuthorizationError without changing authorization semantics.
- Bind amend_artifact to the exact generation it read and retry only the caller-declared field delta from a fresh coherent snapshot for at most eight conflicts.
- Preserve successful non-overlapping amendments, order same-field winners by committed transaction order, and fail visibly without false success after retry exhaustion.
- Add deterministic Windows-spawn multi-process, stale-generation, retry-exhaustion, parity, and no-partial-write tests in the one declared test module.

## Cross-Harness Disposition

- **claude**: Shared canonical Python service; no Claude-local projection changes.
- **codex**: Shared canonical Python service; no Codex-local projection changes.
- **goose**: Shared canonical Python service; no Goose-local projection changes.
- **ollama**: Shared canonical Python service; no Ollama-local projection changes.
- **openrouter**: Shared canonical Python service; no OpenRouter-local projection changes.
- **antigravity**: Shared canonical Python service; no Antigravity-local projection changes.
- **alibaba-cloud-studio**: Shared canonical Python service; no Alibaba Cloud Studio-local projection changes.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5714; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "The registry control plane has a cooperative file lock, coherent read barrier, atomic canonical and packaged replacement, projection journaling, and recovery. However amend_artifact reads a full generation under one lock acquisition and later calls apply_registry_transaction under another without an expected prior generation digest. Two PB workers can therefore read generation G, amend different records, serialize their writes, and let the second stale full-generation payload overwrite the first accepted amendment. Make every registry read-modify-write operation linearizable or generation-CAS-bound, return a bounded actionable retry on conflict, preserve both non-overlapping changes, and add deterministic multi-process coverage. Keep owner hand-edit observation and admission in WI-5696 and isolated Git worktrees in the Git-lifecycle project.",
  "after_behavior": "Make registry amendments linearizable under concurrent Prime Builder writers by binding each read-modify-write to its source generation and retrying boundedly from coherent fresh snapshots.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5714",
    "project": "PROJECT-GTKB-HOUSEKEEPING-HARDENING",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py",
      "groundtruth-kb/tests/test_registry_control_plane.py"
    ],
    "linked_specifications": [
      "GOV-PLATFORM-SOT-REGISTRY-001",
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
      "REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001",
      "DCL-SOT-REGISTRY-PROJECTION-PARITY-001",
      "DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001"
    ]
  },
  "expected_result": {
    "summary": "Make registry amendments linearizable under concurrent Prime Builder writers by binding each read-modify-write to its source generation and retrying boundedly from coherent fresh snapshots.",
    "scope": [
      "Add a typed generation-conflict error beneath RegistryAuthorizationError without changing authorization semantics.",
      "Bind amend_artifact to the exact generation it read and retry only the caller-declared field delta from a fresh coherent snapshot for at most eight conflicts.",
      "Preserve successful non-overlapping amendments, order same-field winners by committed transaction order, and fail visibly without false success after retry exhaustion.",
      "Add deterministic Windows-spawn multi-process, stale-generation, retry-exhaustion, parity, and no-partial-write tests in the one declared test module."
    ],
    "acceptance_criteria": [
      "A direct stale-generation apply is rejected before canonical, packaged, projection, or journal mutation and returns the typed conflict.",
      "At least four synchronized spawned writers amending disjoint records all report success and every accepted delta survives in one coherent final generation.",
      "Retry exhaustion is bounded to eight conflicts, fails visibly, and records no false success or partial generation.",
      "Canonical and packaged declarations remain byte-identical; MemBase projection and journal receipts describe the retained generation.",
      "The existing 29-test focused baseline and every new concurrency/negative test pass; Ruff check, Ruff format, and exact two-path diff checks pass."
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
| `GOV-PLATFORM-SOT-REGISTRY-001` | Run the complete test_registry_control_plane.py suite including four-process retained-amendment coverage. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify strict lifecycle, independent GO, exact-session claim, implementation-start packet, report, and independent terminal verdict. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge_applicability_preflight with zero missing required specs or blocking errors. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-run every row in this mapping and report actual counts and outcomes in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every implementation, test, scratch, and evidence dependency within E:/GT-KB. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | Inspect exact two-path worktree/commit scope and leave the primary checkout unchanged outside the authorized implementation and bridge evidence. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Assert canonical/packaged byte identity plus projection and journal generation parity after concurrent writes. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Re-run authorization and dry-run receipt tests and prove stale-generation denial has zero write side effects. |
| `GOV-WORK-TREE-HYGIENE-001` | Run exact target-path git status, diff, and diff-check inspections while preserving unrelated worktree entries. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Verify the active WI-5714-only PAUTH and exact source/test mutation classes before claim and implementation start. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run implementation_authorization begin after GO and verify the packet contains only the two declared targets. |

## Acceptance Criteria

- A direct stale-generation apply is rejected before canonical, packaged, projection, or journal mutation and returns the typed conflict.
- At least four synchronized spawned writers amending disjoint records all report success and every accepted delta survives in one coherent final generation.
- Retry exhaustion is bounded to eight conflicts, fails visibly, and records no false success or partial generation.
- Canonical and packaged declarations remain byte-identical; MemBase projection and journal receipts describe the retained generation.
- The existing 29-test focused baseline and every new concurrency/negative test pass; Ruff check, Ruff format, and exact two-path diff checks pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`

## Recommended Commit Type

`feat`
