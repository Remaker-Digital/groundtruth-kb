NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1078-0168-7573-8a31-a68af5b9842a
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Prime Builder automation auto-builder; WI-4356 implementation report filing

# GT-KB Bridge Implementation Report - gtkb-work-tree-hygiene-slice-c-doctor-check - 003

bridge_kind: implementation_report
Document: gtkb-work-tree-hygiene-slice-c-doctor-check
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-work-tree-hygiene-slice-c-doctor-check-002.md
Approved proposal: bridge/gtkb-work-tree-hygiene-slice-c-doctor-check-001.md
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4356
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION
Commit: 774aa0517
Recommended commit type: feat

## Implementation Claim

Implemented WI-4356 Slice C by adding a read-only `gt project doctor` check for stale work-tree strays. The doctor now calls the verified `groundtruth_kb.hygiene.strays.run_strays()` adapter in bridge-enabled profiles, reports stale workspace/stash/worktree counts plus min/avg/max age hours, passes clean reports with zero stale findings, and fail-softs to a warning when git state cannot be collected.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`

## Owner Decisions / Input

No new owner decision was required. The implementation used the active project authorization and the latest GO verdict for this bridge thread.

## Prior Deliberations

- `bridge/gtkb-work-tree-hygiene-slice-c-doctor-check-001.md` - approved implementation proposal.
- `bridge/gtkb-work-tree-hygiene-slice-c-doctor-check-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `python -m pytest platform_tests/scripts/test_work_tree_hygiene_doctor.py -q --tb=short` passed: 4 tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `python -m pytest platform_tests/scripts/test_work_tree_hygiene_doctor.py -q --tb=short` passed: 4 tests, including text and JSON report output. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_work_tree_hygiene_doctor.py platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short` passed: 37 tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-c-doctor-check` passed; `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-c-doctor-check` passed; `python scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/project/doctor.py` passed; `python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_work_tree_hygiene_doctor.py` passed. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_work_tree_hygiene_doctor.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_work_tree_hygiene_doctor.py platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_work_tree_hygiene_doctor.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_work_tree_hygiene_doctor.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-c-doctor-check`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-c-doctor-check`
- `python scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_work_tree_hygiene_doctor.py`

## Observed Results

- Focused doctor tests: 4 passed.
- Full WI-4356 Slice A/B/C regression set: 37 passed.
- Ruff check: all checks passed.
- Ruff format check: 2 files already formatted.
- Bridge applicability preflight: passed with no missing required specs.
- ADR/DCL clause preflight: passed with no blocking gaps.
- Implementation authorization validation: both target paths authorized.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_work_tree_hygiene_doctor.py`

## Recommended Commit Type

- Recommended commit type: `feat`
- Commit created: `774aa0517 feat: add work-tree strays doctor check`

```text
groundtruth-kb/src/groundtruth_kb/project/doctor.py           | 74 +++++++++++++++++
platform_tests/scripts/test_work_tree_hygiene_doctor.py       | 93 ++++++++++++++++++++++
2 files changed, 167 insertions(+)
```

## Acceptance Criteria Status

- [x] `gt project doctor` JSON and text output include a work-tree strays check when stale items exist.
- [x] The doctor check is warning-level, read-only, and fail-soft when git state cannot be collected.
- [x] A clean report returns pass with zero stale findings.

## Risk And Rollback

Residual risk is low. The check is read-only, optional, and warning-level; it does not delete files, drop stashes, prune worktrees, create commits, mutate MemBase, or change bridge state. Rollback is a revert of commit `774aa0517`; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the implementation satisfies the approved proposal, otherwise return NO-GO with findings.
