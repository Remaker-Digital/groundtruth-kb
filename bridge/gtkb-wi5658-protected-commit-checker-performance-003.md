NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T13-53-43Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Report — WI-5658 protected-commit checker performance

bridge_kind: implementation_report
Document: gtkb-wi5658-protected-commit-checker-performance
Version: 003
Responds to GO: bridge/gtkb-wi5658-protected-commit-checker-performance-002.md
Approved proposal: bridge/gtkb-wi5658-protected-commit-checker-performance-001.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5658

## Implementation Claim

The approved WI-5658 implementation is committed in `93f7764662853b3f86a714d34555303a62c2321d` (`feat(bridge-tooling): fix protected-commit checker O(N^2) performance hang (WI-5658)`). It bounds every checker git subprocess at 120 seconds and changes `_load_verified_evidence` to enumerate the committed bridge tree once, group versioned entries by exact slug, and reuse those entries per authorization packet. This changes the relevant complexity from O(packets × committed bridge files) to O(packets + committed bridge files) without changing authorization or verdict semantics.

The commit changes exactly the two approved implementation targets, plus the proposal and GO bridge artifacts. This report adds no source mutation.

## Scope Isolation

The later commits `7b838d9e7`, `f0b27999a`, and `c0c4c40e4` also changed these two files for WI-5657/WI-5659. They are not attributed to WI-5658. The current focused WI-5658 tests exercise only the timeout, exact-slug grouping, and once-only enumeration behavior introduced by `93f776466`; the historical commit diff is the implementation attribution boundary.

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
- `GOV-WORK-TREE-HYGIENE-001`

## Owner Decisions / Input

- `DELIB-202667183` — owner authorization for the bounded WI-5658 performance/timeout repair.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX` remains active, includes WI-5658, permits source/test only, and explicitly excludes WI-5657 and WI-5441.

## Prior Deliberations

- `DELIB-202667183` — owner decision carried forward from the approved proposal and PAUTH.
- `bridge/gtkb-wi5658-protected-commit-checker-performance-001.md` — approved implementation proposal.
- `bridge/gtkb-wi5658-protected-commit-checker-performance-002.md` — independent Loyal Opposition GO.

## Specification-Derived Verification

| Spec / governing surface | Executed evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Reviewed latest GO, PAUTH, target boundary, and `git show --stat 93f776466`. | Commit boundary is the two approved implementation files; later overlapping WI-5657/WI-5659 commits are excluded. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `git show --format=fuller --find-renames 93f776466 -- <two targets>` | Commit preserves source/test rationale and targeted regression cases as durable evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Approved proposal `-001`, GO `-002`, and report linkage above. | Proposal, PAUTH, project, WI, and exact paths remain aligned. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Three WI-5658 selectors and full checker suite below. | Timeout fail-closed, exact-slug grouping, and single enumeration are executed against current code. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `gt projects show-authorization PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX --json` | Active exact-singleton authority, source/test only, excluding WI-5657/WI-5441. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Commit/path review and focused tests from `E:\GT-KB`. | No external/adopter path is involved. |
| `GOV-WORK-TREE-HYGIENE-001` | `git diff --check 93f776466^ 93f776466 -- <two targets>` | Exit 0; the committed WI-5658 diff has no whitespace errors. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py::test_wi5658_run_git_times_out_fails_closed platform_tests/scripts/test_check_protected_commit_authorization.py::test_wi5658_committed_bridge_entries_by_id_groups_by_exact_slug platform_tests/scripts/test_check_protected_commit_authorization.py::test_wi5658_load_verified_evidence_enumerates_committed_bridge_once -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short
python -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
python -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
git diff --check 93f776466^ 93f776466 -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
git log --oneline 93f776466..HEAD -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
```

## Observed Results

- The three exact WI-5658 selectors passed: `3 passed`.
- The full checker suite completed successfully after collecting 113 tests.
- Ruff lint passed; both approved Python files are formatted.
- `git diff --check` for the attributed commit passed.
- Later overlapping commits are present, so this report does not represent their cumulative 949-line post-WI-5658 diff as WI-5658 work.

## Files Changed

- `scripts/check_protected_commit_authorization.py` — committed in `93f776466`; 90 added / 18 removed lines in the attributed commit.
- `platform_tests/scripts/test_check_protected_commit_authorization.py` — committed in `93f776466`; 72 focused regression-test lines added in the attributed commit.

## Recommended Commit Type

Recommended commit type: `feat:` — the attributed commit adds the bounded subprocess and single-inventory capability required to make protected finalization practical.

## Acceptance Criteria Status

- **Met:** one committed bridge-tree enumeration is asserted by `test_wi5658_load_verified_evidence_enumerates_committed_bridge_once`.
- **Met:** timeout behavior fails closed with status 124, asserted by `test_wi5658_run_git_times_out_fails_closed`.
- **Met:** exact slug isolation is asserted by `test_wi5658_committed_bridge_entries_by_id_groups_by_exact_slug`.
- **Met:** existing checker suite and source quality checks pass.
- **For LO verification:** confirm the commit-level source diff preserves authorization semantics and that WI-5657/WI-5659 later hunks are not accepted under this report.

## Risk and Rollback

The remaining risk is incorrectly mixing later finalization work into this performance repair. The report avoids that by pinning attribution to `93f776466`; rollback must revert only that commit's two implementation targets under new governed authority. Bridge artifacts and owner decisions remain append-only.

## Loyal Opposition Asks

1. Verify `93f776466` against the approved WI-5658 proposal and GO.
2. Verify the executed selector and suite evidence.
3. Confirm later WI-5657/WI-5659 hunks are excluded, then finalize VERIFIED through the atomic commit-finalization path when eligible.
