NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1078-0168-7573-8a31-a68af5b9842a
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Prime Builder automation auto-builder; governed bridge proposal filing

# Implementation Proposal - Define and implement recurring work-tree hygiene + stash-stray-cleanup mechanism

bridge_kind: prime_proposal
Document: gtkb-work-tree-hygiene-slice-c-doctor-check
Version: 001
Date: 2026-06-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4356

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_work_tree_hygiene_doctor.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Slice C integrates the verified WI-4356 work-tree strays detector and dry-run CLI into gt project doctor as a read-only warning-level visibility check.

Work item description: Owner directive 2026-06-04 S-loop: 'agents wont return after 12h; need recurring work-tree hygiene + stray-cleanup mechanism'. Scope: stale-detection criteria, triage rules, CLI surface + doctor check + optional scheduled enforcement. DELIB precedent: today drop'd 9 stashes (3d to 2wk old) after confirming zero recoverable unique content.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4356` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `platform_tests/scripts/test_work_tree_hygiene_doctor.py`.

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
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266072` - Loyal Opposition Review - WI-4720 Narrative Staged EOL Parity
- `DELIB-20266333` - Separation Check
- `DELIB-20266120` - Owner decision: resolve WI-3502 and WI-3503 as substantially-addressed (SoT-freshness final closure)
- `DELIB-20265989` - Verdict
- `DELIB-20266206` - Owner reconciliation decision: repair 10 corrupted related_bridge_threads links

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION` - active project authorization covering `WI-4356`.

## Proposed Scope

- Add a gt project doctor check that invokes the verified work-tree stray scan in summary mode and reports stale workspace/stash/worktree counts plus age distribution.
- Keep the doctor check read-only and warning-level: it must not delete files, drop stashes, prune worktrees, create commits, mutate MemBase, or change bridge state.
- Reuse the verified Slice B package adapter instead of duplicating git/stash/worktree parsing in doctor.py.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | python -m pytest platform_tests/scripts/test_work_tree_hygiene_doctor.py -q --tb=short |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | python -m pytest platform_tests/scripts/test_work_tree_hygiene_doctor.py platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | python -m pytest platform_tests/scripts/test_work_tree_hygiene_doctor.py -q --tb=short |

## Acceptance Criteria

- gt project doctor JSON and text output include a work-tree strays check when stale items exist.
- The doctor check is warning-level, read-only, and fail-soft when git state cannot be collected.
- A clean repository reports pass with zero stale findings.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_work_tree_hygiene_doctor.py`

## Recommended Commit Type

`feat`
