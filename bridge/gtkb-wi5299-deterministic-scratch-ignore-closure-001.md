NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; Prime Builder A; default reasoning configuration

# Implementation Proposal - Handle unignored deterministic scratch residue classes in work-tree hygiene

bridge_kind: prime_proposal
Document: gtkb-wi5299-deterministic-scratch-ignore-closure
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5299

target_paths: [".gitignore", "platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Close only the deterministic scratch-class coverage gaps left by WI-5114, making the exact 128-path residue census non-dirty without deleting any bytes.

Work item description: The verified WI-5114 ignore contract misses seven narrow deterministic scratch classes represented by the 128-path manifest SHA-256 CB076FB568E4DF72BF79D586A05E22C81073B97AA5945E1041CB2C5084B617A1: 94 .harness-tmp-unique-* pytest files; 20 root .tmp_lo_* review helpers; five root loose throwaways (CON, strftime, temp-direct*.txt, temp-test.txt); five test-auth-root fixture files; two .claude verify-helper drafts; and two .codex verify-helper drafts. Extend deterministic .gitignore classification and focused tests for only these classes without deleting bytes or hiding canonical controls.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5299` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.gitignore`, `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`.

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

- `DELIB-202666069` - Loyal Opposition NO-GO verdict - WI-5114 scratch-ignore normalization (.gitignore EOL durability)
- `DELIB-202666067` - Loyal Opposition VERIFIED verdict - WI-5114 scratch-ignore normalization (.gitignore LF durability + standing regression guard)
- `DELIB-202665953` - Loyal Opposition VERIFIED verdict — GTKB Dashboard Industry Alignment Slice 2A (finalization recovery)
- `DELIB-202665876` - Separation Check
- `DELIB-20265665` - Loyal Opposition Verification - Pending Owner Decisions Surface Cache Resurface

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5299`.

## Proposed Scope

- Add only narrow ignore patterns for the seven exact non-authoritative scratch classes in manifest CB076FB568E4DF72BF79D586A05E22C81073B97AA5945E1041CB2C5084B617A1.
- Extend the existing WI-5114 regression test with representative paths and visible canonical controls.
- Do not delete, stage, commit, or hide bridge, source, database, canonical helper, or unrelated untracked paths.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Run platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py and enumerate git check-ignore for the exact 128-path manifest plus control paths. |
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

## Acceptance Criteria

- All 128 manifest paths are ignored by Git after the change and all were visible before it.
- Canonical verify helpers, .gitignore, bridge artifacts, and protected source controls remain visible.
- Focused pytest, git check-ignore assertions, diff check, Ruff, and LF pin checks pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.gitignore`
- `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`

## Recommended Commit Type

`feat`
