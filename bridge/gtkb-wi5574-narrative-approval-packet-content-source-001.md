NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user; turn_id=0fdcd215-4319-40cc-9d01-b83531c52c01
author_metadata_source: codex-desktop-request-meta

# Implementation Proposal - Govern narrative approval-packet target/content separation candidate

bridge_kind: prime_proposal
Document: gtkb-wi5574-narrative-approval-packet-content-source
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5574

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py", "groundtruth-kb/tests/test_cli_approval_packet.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5574 governs two pre-existing foreign source hunks that separate narrative approval target identity from intended content. Current regression evidence is 1/1 focused pytest plus Ruff/format/diff PASS, but no existing test exercises the new branch. Review must require exact focused coverage, preserve fail-closed path identity, hold implementation behind WI-5483 linked-test authority, and finalize only exact reviewed hunks.

Work item description: Own the pre-existing tracked candidate in groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py and groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py that lets a narrative packet retain the real target path identity while hashing intended content from an optional in-root content_file. Treat current bytes as foreign and unverified. Before implementation/finalization, independently review semantics; add focused coverage in groundtruth-kb/tests/test_cli_approval_packet.py for pending-content success, unchanged target identity, default target-read behavior, missing content file, and outside-root rejection; prove the packet validates against the intended post-write content; then use exact hunk-only finalization without absorbing unrelated dirt. Governed linked-test creation is deferred to WI-5483 because live PHASE-003 test_ids is malformed and add-work-item correctly fails before mutation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5574` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py`, `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`, `groundtruth-kb/tests/test_cli_approval_packet.py`.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - auto-linked governing or work-item specification.
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

- `DELIB-20261603` - Loyal Opposition Review - gt generate-approval-packet CLI - REVISED-1
- `DELIB-2410` - Loyal Opposition Review - gt generate-approval-packet CLI - REVISED-1
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` - Owner decision: WI-5210 hunk-scoped finalization waiver
- `DELIB-202666285` - Loyal Opposition NO-GO Verdict - Dispatcher Black-Box Spec Foundation V2
- `DELIB-20261604` - Loyal Opposition Review - gt generate-approval-packet CLI

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5574`.

## Proposed Scope

- Independently review and, only after GO plus WI-5483 governed test linkage, adopt or correct the existing optional content_source hunks without taking whole-file ownership.
- Keep target_path as the approval identity while permitting only an existing in-root content_file to supply LF-normalized intended full_content; preserve the no-content-file path exactly.
- Add focused CLI tests for pending-content success, unchanged target identity, legacy default, missing source, outside-root source, and validation against intended post-write content.
- Exclude bridge/TAFE/dispatcher/harness mutation, groundtruth.db finalization, unrelated packet behavior, Git index/history operations, release, deployment, credentials, and all foreign dirt.

## Cross-Harness Disposition

- **all-harnesses**: Shared deterministic CLI and packet-builder behavior; no harness-specific runtime or routing change.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5574; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Own the pre-existing tracked candidate in groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py and groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py that lets a narrative packet retain the real target path identity while hashing intended content from an optional in-root content_file. Treat current bytes as foreign and unverified. Before implementation/finalization, independently review semantics; add focused coverage in groundtruth-kb/tests/test_cli_approval_packet.py for pending-content success, unchanged target identity, default target-read behavior, missing content file, and outside-root rejection; prove the packet validates against the intended post-write content; then use exact hunk-only finalization without absorbing unrelated dirt. Governed linked-test creation is deferred to WI-5483 because live PHASE-003 test_ids is malformed and add-work-item correctly fails before mutation.",
  "after_behavior": "WI-5574 governs two pre-existing foreign source hunks that separate narrative approval target identity from intended content. Current regression evidence is 1/1 focused pytest plus Ruff/format/diff PASS, but no existing test exercises the new branch. Review must require exact focused coverage, preserve fail-closed path identity, hold implementation behind WI-5483 linked-test authority, and finalize only exact reviewed hunks.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5574",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py",
      "groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py",
      "groundtruth-kb/tests/test_cli_approval_packet.py"
    ],
    "linked_specifications": [
      "GOV-ARTIFACT-APPROVAL-001",
      "ADR-ARTIFACT-FORMALIZATION-GATE-001",
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "WI-5574 governs two pre-existing foreign source hunks that separate narrative approval target identity from intended content. Current regression evidence is 1/1 focused pytest plus Ruff/format/diff PASS, but no existing test exercises the new branch. Review must require exact focused coverage, preserve fail-closed path identity, hold implementation behind WI-5483 linked-test authority, and finalize only exact reviewed hunks.",
    "scope": [
      "Independently review and, only after GO plus WI-5483 governed test linkage, adopt or correct the existing optional content_source hunks without taking whole-file ownership.",
      "Keep target_path as the approval identity while permitting only an existing in-root content_file to supply LF-normalized intended full_content; preserve the no-content-file path exactly.",
      "Add focused CLI tests for pending-content success, unchanged target identity, legacy default, missing source, outside-root source, and validation against intended post-write content.",
      "Exclude bridge/TAFE/dispatcher/harness mutation, groundtruth.db finalization, unrelated packet behavior, Git index/history operations, release, deployment, credentials, and all foreign dirt."
    ],
    "acceptance_criteria": [
      "The reviewer confirms whether target/content separation is required by GOV-ARTIFACT-APPROVAL-001 and whether the candidate fails closed without weakening target identity.",
      "Focused tests cover every new branch and prove packet validation against intended content; existing test_cli_approval_packet.py remains green.",
      "Exact current candidate hashes are cli_approval_packet.py AC4EFB8B93708BB137479445F3B9672A6E7F01BECF4D08133E87B669D2DF5AE8 and narrative_artifact_packet.py 9BA359E2137AC51A31074C73E014DA96BE21D776749E818B1D240109BB7297D6; hash drift fails closed.",
      "Implementation cannot start until WI-5483 provides a governed linked test, independent GO is current, and exact claim/start authority succeeds."
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
| `GOV-ARTIFACT-APPROVAL-001` | Run groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli_approval_packet.py -q --tb=short and require focused success/default/fail-closed content-source cases plus the existing CRLF case. |
| `ADR-ARTIFACT-FORMALIZATION-GATE-001` | Inspect generated packet fields in focused tests and require target path identity to remain the real protected target while full_content and its hash match intended content. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run Ruff check, Ruff format --check, git diff --check, and independent LO review over the exact three-target diff; reject missing linked-test evidence or unrelated hunks. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The reviewer confirms whether target/content separation is required by GOV-ARTIFACT-APPROVAL-001 and whether the candidate fails closed without weakening target identity.
- Focused tests cover every new branch and prove packet validation against intended content; existing test_cli_approval_packet.py remains green.
- Exact current candidate hashes are cli_approval_packet.py AC4EFB8B93708BB137479445F3B9672A6E7F01BECF4D08133E87B669D2DF5AE8 and narrative_artifact_packet.py 9BA359E2137AC51A31074C73E014DA96BE21D776749E818B1D240109BB7297D6; hash drift fails closed.
- Implementation cannot start until WI-5483 provides a governed linked test, independent GO is current, and exact claim/start authority succeeds.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py`
- `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`
- `groundtruth-kb/tests/test_cli_approval_packet.py`

## Recommended Commit Type

`feat`
