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

# Implementation Proposal - Normalize PHASE-003 test membership to canonical JSON

bridge_kind: prime_proposal
Document: gtkb-wi5615-test-plan-phase-json-normalization
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5615

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_test_plan_phase.py", "platform_tests/scripts/test_cli_test_plan_phase.py", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add a fail-closed canonical gt tests transaction that normalizes one hash-bound phase membership representation, then use it to encode PHASE-003 version 64 as JSON without changing its ordered 269-member set.

Work item description: The canonical PLAN-001 PHASE-003 current test_ids value is comma-delimited plain text instead of the required JSON list. Strict governed writers correctly reject that row as malformed, which blocks add-linked-test and exact linkage repair operations targeting Production Regression. Append one governed phase version that preserves the exact ordered test-id membership while encoding it as a canonical JSON array; prove every member is a unique canonical TEST-* id, no test is added or removed, all governed readers parse the row, and Master Test Plan coverage is unchanged. Do not bypass through direct database mutation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5615` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/cli_test_plan_phase.py`, `platform_tests/scripts/test_cli_test_plan_phase.py`, `groundtruth.db`.

## Specification Links

- `GOV-13` - auto-linked governing or work-item specification.
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
- `GOV-08` - auto-linked governing or work-item specification.
- `GOV-12` - auto-linked governing or work-item specification.
- `SPEC-1493` - auto-linked governing or work-item specification.
- `SPEC-1605` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265110` - Review: POR Step 16.D Phantom Spec-Link Cleanup
- `DELIB-0611` - S277 Remediation Re-Review - NO-GO
- `DELIB-202666859` - Loyal Opposition GO Verdict - Dispatcher Black-Box Spec Foundation (UTC Date-Correction Delta, v031)
- `DELIB-202666592` - Loyal Opposition Verdict - Stabilize Workflow Tamper Diagnostics After Envelope Hardening
- `DELIB-2638` - Loyal Opposition Verdict - Skill Modernization Slice 3 kb-work-item Migration Revision

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5615`.

## Proposed Scope

- Add gt tests normalize-phase-membership with required phase id, expected current version, expected raw SHA-256, dry-run, and JSON output; reject drift before mutation.
- Parse only the exact legacy comma-list representation after proving every member is a unique canonical TEST-* id; preserve exact order and membership and write through KnowledgeDB.update_test_plan_phase with full before/after readback.
- Apply the command only to PHASE-003 version 64 at raw SHA-256 01748e852f01ce716419ffa70dcad4b0806bd028e972777c9888bf5daa26e895; do not add, remove, or repair phantom members in WI-5615.
- Keep the cli.py registration as an exact declared hunk, exclude all foreign cli.py worktree changes, and do not mutate dispatcher/TAFE/runtime state, credentials, Git refs, deployment, or release.

## Cross-Harness Disposition

- **A**: Shared gt CLI and MemBase behavior; no Codex adapter change.
- **B**: Shared gt CLI and MemBase behavior; no Claude adapter change.
- **C**: Shared gt CLI and MemBase behavior; no Antigravity adapter change.
- **D**: Shared gt CLI and MemBase behavior; no Ollama adapter change.
- **E**: Shared gt CLI and MemBase behavior; no Cursor adapter change.
- **F**: Shared gt CLI and MemBase behavior; no OpenRouter adapter change.
- **H**: Shared gt CLI and MemBase behavior; no Alibaba adapter change.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5615; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "The canonical PLAN-001 PHASE-003 current test_ids value is comma-delimited plain text instead of the required JSON list. Strict governed writers correctly reject that row as malformed, which blocks add-linked-test and exact linkage repair operations targeting Production Regression. Append one governed phase version that preserves the exact ordered test-id membership while encoding it as a canonical JSON array; prove every member is a unique canonical TEST-* id, no test is added or removed, all governed readers parse the row, and Master Test Plan coverage is unchanged. Do not bypass through direct database mutation.",
  "after_behavior": "Add a fail-closed canonical gt tests transaction that normalizes one hash-bound phase membership representation, then use it to encode PHASE-003 version 64 as JSON without changing its ordered 269-member set.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5615",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/cli.py",
      "groundtruth-kb/src/groundtruth_kb/cli_test_plan_phase.py",
      "platform_tests/scripts/test_cli_test_plan_phase.py",
      "groundtruth.db"
    ],
    "linked_specifications": [
      "GOV-13",
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
      "GOV-08",
      "GOV-12",
      "SPEC-1493",
      "SPEC-1605"
    ]
  },
  "expected_result": {
    "summary": "Add a fail-closed canonical gt tests transaction that normalizes one hash-bound phase membership representation, then use it to encode PHASE-003 version 64 as JSON without changing its ordered 269-member set.",
    "scope": [
      "Add gt tests normalize-phase-membership with required phase id, expected current version, expected raw SHA-256, dry-run, and JSON output; reject drift before mutation.",
      "Parse only the exact legacy comma-list representation after proving every member is a unique canonical TEST-* id; preserve exact order and membership and write through KnowledgeDB.update_test_plan_phase with full before/after readback.",
      "Apply the command only to PHASE-003 version 64 at raw SHA-256 01748e852f01ce716419ffa70dcad4b0806bd028e972777c9888bf5daa26e895; do not add, remove, or repair phantom members in WI-5615.",
      "Keep the cli.py registration as an exact declared hunk, exclude all foreign cli.py worktree changes, and do not mutate dispatcher/TAFE/runtime state, credentials, Git refs, deployment, or release."
    ],
    "acceptance_criteria": [
      "Dry-run reports 269 unique canonical members, the exact source version/hash, and the proposed JSON hash without changing MemBase.",
      "Apply appends exactly one PHASE-003 version whose JSON-decoded list equals the pre-repair ordered 269-member list byte-for-member; every other phase latest row is unchanged.",
      "Wrong phase, version drift, hash drift, malformed JSON, malformed legacy members, duplicates, absent phase, injected write failure, or readback mismatch fails without partial mutation.",
      "Focused source tests, GOV-12/GOV-13 linkage tests, MemBase integrity checks, and hunk-only finalization checks pass."
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
| `GOV-13` | Exercise dry-run and apply against hermetic phase fixtures; prove canonical JSON membership, exact order/set preservation, and no orphan/coverage regression. |
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
| `GOV-08` | Prove all mutation goes through the canonical KnowledgeDB append-only phase writer and exact before/after readback, with no direct SQL update. |
| `GOV-12` | Prove WI-5615 remains linked to TEST-11660 and the test remains assigned to PHASE-002 throughout the repair. |
| `SPEC-1493` | Prove the current phase remains a versioned MemBase artifact with unchanged plan id, phase order, title, description, gate criteria, and membership semantics. |
| `SPEC-1605` | Prove only PHASE-003 receives one new version and no other phase or test-plan record changes. |

## Acceptance Criteria

- Dry-run reports 269 unique canonical members, the exact source version/hash, and the proposed JSON hash without changing MemBase.
- Apply appends exactly one PHASE-003 version whose JSON-decoded list equals the pre-repair ordered 269-member list byte-for-member; every other phase latest row is unchanged.
- Wrong phase, version drift, hash drift, malformed JSON, malformed legacy members, duplicates, absent phase, injected write failure, or readback mismatch fails without partial mutation.
- Focused source tests, GOV-12/GOV-13 linkage tests, MemBase integrity checks, and hunk-only finalization checks pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_test_plan_phase.py`
- `platform_tests/scripts/test_cli_test_plan_phase.py`
- `groundtruth.db`

## Recommended Commit Type

`feat`
