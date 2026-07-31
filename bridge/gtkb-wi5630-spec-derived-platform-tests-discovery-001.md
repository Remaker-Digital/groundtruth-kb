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

# Implementation Proposal - Include platform_tests in spec-derived verification runner discovery

bridge_kind: prime_proposal
Document: gtkb-wi5630-spec-derived-platform-tests-discovery
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5630

target_paths: ["scripts/run_spec_derived_tests.py", "platform_tests/scripts/test_run_spec_derived_tests.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Extend the canonical specification-derived verification runner to discover and execute module-docstring-linked tests under the repository's established platform_tests root, preserving all existing full-history, waiver, timeout, isolation, and fail-closed contracts.

Work item description: scripts/run_spec_derived_tests.py registers only tests/ and groundtruth-kb/tests/ as discovery roots. It therefore reports no_derived_tests for specification-derived suites under the repository's active platform_tests/ root, including platform_tests/scripts/test_batch_archive_terminal_verdicts.py in the canonical WI-5370 implementation report bridge/gtkb-wi5370-batched-archive-preserve-service-011.md. Extend discovery and grouped pytest execution to include platform_tests without weakening module-docstring matching, full-history linkage, fail-closed coverage, timeout, or in-root path constraints.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5630` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/run_spec_derived_tests.py`, `platform_tests/scripts/test_run_spec_derived_tests.py`.

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `DCL-VERIFIED-BRIDGE-HISTORY-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-2312` - Loyal Opposition Review - Agent Red Deployability Preservation Gate
- `DELIB-2392` - Loyal Opposition Review - Codex Feedback Pattern Lints
- `DELIB-202666297` - Loyal Opposition NO-GO Verdict - WI-5260 Modernization Clause-Exact Semantics
- `DELIB-20266256` - Applicability Preflight
- `DELIB-202667033` - Loyal Opposition Verification Verdict - WI-5401 Hunk Patch Integrity Gate

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5630`.

## Proposed Scope

- Add the repository's existing platform_tests directory to TEST_DIRS while preserving conservative module-level-docstring discovery, deterministic de-duplication, full-history specification accumulation, waiver validation, timeout behavior, and in-root path restrictions.
- Classify platform_tests paths as a distinct pytest execution group rooted at the repository, while preserving the existing tests group and the isolated groundtruth-kb/tests invocation with its package rootdir and testpaths override.
- Add hermetic regression coverage for discovery, dry-run matrix reporting, successful execution, failing-test propagation, and non-regression across all three supported roots; do not mutate dispatcher/runtime state, groundtruth.db, Git state, credentials, deployment, release, or unrelated worktree bytes.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5630; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "scripts/run_spec_derived_tests.py registers only tests/ and groundtruth-kb/tests/ as discovery roots. It therefore reports no_derived_tests for specification-derived suites under the repository's active platform_tests/ root, including platform_tests/scripts/test_batch_archive_terminal_verdicts.py in the canonical WI-5370 implementation report bridge/gtkb-wi5370-batched-archive-preserve-service-011.md. Extend discovery and grouped pytest execution to include platform_tests without weakening module-docstring matching, full-history linkage, fail-closed coverage, timeout, or in-root path constraints.",
  "after_behavior": "Extend the canonical specification-derived verification runner to discover and execute module-docstring-linked tests under the repository's established platform_tests root, preserving all existing full-history, waiver, timeout, isolation, and fail-closed contracts.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5630",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "scripts/run_spec_derived_tests.py",
      "platform_tests/scripts/test_run_spec_derived_tests.py"
    ],
    "linked_specifications": [
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-VERIFIED-BRIDGE-HISTORY-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001"
    ]
  },
  "expected_result": {
    "summary": "Extend the canonical specification-derived verification runner to discover and execute module-docstring-linked tests under the repository's established platform_tests root, preserving all existing full-history, waiver, timeout, isolation, and fail-closed contracts.",
    "scope": [
      "Add the repository's existing platform_tests directory to TEST_DIRS while preserving conservative module-level-docstring discovery, deterministic de-duplication, full-history specification accumulation, waiver validation, timeout behavior, and in-root path restrictions.",
      "Classify platform_tests paths as a distinct pytest execution group rooted at the repository, while preserving the existing tests group and the isolated groundtruth-kb/tests invocation with its package rootdir and testpaths override.",
      "Add hermetic regression coverage for discovery, dry-run matrix reporting, successful execution, failing-test propagation, and non-regression across all three supported roots; do not mutate dispatcher/runtime state, groundtruth.db, Git state, credentials, deployment, release, or unrelated worktree bytes."
    ],
    "acceptance_criteria": [
      "A module-level docstring-linked test under platform_tests is discovered, appears in the requested specification's matrix, executes under the repository pytest root, and can make verified_overall true when it is the sole linked requirement.",
      "A failing platform_tests-derived test fails closed, while missing and outside-root cases preserve their current non-zero behavior.",
      "Existing tests and groundtruth-kb/tests discovery and grouped execution remain behaviorally unchanged, including the separate package-root pytest invocation.",
      "Focused pytest, Ruff check, Ruff format check, py_compile, applicability preflight, and clause preflight all pass on the exact two target paths and proposal thread."
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
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Hermetic tests create module-docstring-linked platform_tests files and assert discovery, matrix inclusion, execution success, and fail-closed propagation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Canonical bridge show plus applicability and clause preflights prove an append-only governed thread with no aggregate-index dependency. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight reports no missing required specifications and the implementation report carries the complete linked set forward. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and report headers bind WI-5630, PROJECT-GTKB-TREE-STABILIZATION, and the selected active PAUTH. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path-resolution tests keep every production discovery root under PROJECT_ROOT and reject or ignore out-of-root candidates as currently specified. |
| `GOV-STANDING-BACKLOG-001` | Read back WI-5630 and TEST-11675 as the canonical defect and linked regression test before and after implementation. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-BRIDGE-HISTORY-001` | Existing full-history union and waiver tests remain green while the new root participates only in derived-test discovery and execution. |
| `GOV-WORK-TREE-HYGIENE-001` | Git diff inspection proves only the two exact approved targets change during implementation and no unrelated dirty bytes are adopted. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Before protected edits, validate independent GO, exact claim, active project PAUTH, and an implementation-start packet for both targets. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | No source or test mutation occurs before the independent GO and operation-time authorization gates succeed. |

## Acceptance Criteria

- A module-level docstring-linked test under platform_tests is discovered, appears in the requested specification's matrix, executes under the repository pytest root, and can make verified_overall true when it is the sole linked requirement.
- A failing platform_tests-derived test fails closed, while missing and outside-root cases preserve their current non-zero behavior.
- Existing tests and groundtruth-kb/tests discovery and grouped execution remain behaviorally unchanged, including the separate package-root pytest invocation.
- Focused pytest, Ruff check, Ruff format check, py_compile, applicability preflight, and clause preflight all pass on the exact two target paths and proposal thread.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/run_spec_derived_tests.py`
- `platform_tests/scripts/test_run_spec_derived_tests.py`

## Recommended Commit Type

`feat`
