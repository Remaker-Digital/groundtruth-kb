NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Report - WI-5657 Protected-Commit Checker: Superseded Predecessor VERIFIED

bridge_kind: implementation_report
Document: gtkb-wi5657-protected-commit-superseded-verified
Version: 003
Responds to: bridge/gtkb-wi5657-protected-commit-superseded-verified-002.md
Reviewed GO: bridge/gtkb-wi5657-protected-commit-superseded-verified-002.md
Recommended commit type: feat

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5657

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

## Summary

Implemented the GO'd fix. The protected-commit authorization checker now treats a
superseded predecessor VERIFIED (a first-line-VERIFIED versioned bridge file with a
higher-numbered same-slug version staged in the SAME commit transaction) as
non-authoritative history: excluded from the transaction VERIFIED-candidate count and
from the terminal-VERIFIED Commit-Finalization-Evidence finding, while the single
latest VERIFIED candidate keeps full validation and zero live candidates fail closed.
This unblocks WI-5441 Phase 1B finalization and the broader WI-5113 dirty-finalizer
class.

## Implementation Claim

Bounded to the two GO-authorized target paths:

- `scripts/check_protected_commit_authorization.py`: added helper
  `_superseded_versioned_bridge(rel_path, snapshot)` (staged-transaction-scoped: a
  higher-numbered same-slug version in `snapshot.selected_paths`; exact bridge_id
  equality + integer version comparison via `VERSIONED_BRIDGE_CAPTURE_RE`). Applied at
  two points: (1) the `_load_transaction_verified_evidence` candidate collector skips a
  superseded first-line-VERIFIED staged file, so only the latest-per-chain VERIFIED
  counts toward the exactly-one-candidate clearance; (2) `_verified_bridge_finalization_finding`
  returns None for a superseded VERIFIED so it commits as inert history without a
  Commit-Finalization-Evidence requirement. Single-latest-VERIFIED validation is
  unchanged (manifest-equals-staged-set, resolver latest-strict-state, review
  independence, evidence anchors, finalized-packet per-path authorization).
- `platform_tests/scripts/test_check_protected_commit_authorization.py`: added eight
  spec-derived WI-5657 tests.

## Adversarial Security Review and Correction

Before filing, a three-lens adversarial security review was run
(authorization-bypass, detection-correctness, edge-cases):

- **Authorization-bypass**: no hole. The fix is fail-closed in the supersession
  direction; a superseded file authorizes nothing (it is excluded from candidacy);
  with zero live candidates a protected commit is simply not authorized; the single
  retained candidate still runs full validation.
- **Detection-correctness (CONFIRMED, medium)**: the initial implementation also
  scanned the ambient worktree `bridge/` directory (status-blind `iterdir`), so an
  untracked or parked higher-numbered same-slug draft could false-positively mark a
  GENUINE latest terminal VERIFIED as superseded, breaking a legitimate commit and
  suppressing the durability finding.
- **Edge-cases**: no defect.

**Correction applied**: supersession is now scoped to the staged transaction only
(`snapshot.selected_paths`); the worktree scan and the helper's `root` parameter were
removed. This is strictly more conservative (it can only REDUCE what is marked
superseded, never grant authorization), it is sufficient for the finalization use case
(the atomic finalizer stages the whole chain together), and the pre-existing resolver
latest-strict-state check backstops any committed-higher edge case. A dedicated
regression test
(`test_wi5657_untracked_worktree_higher_sibling_does_not_supersede_staged_latest`)
guards the exact flagged scenario.

## Specification Links

Carried forward from the GO'd proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Mandatory VERIFIED Commit-Finalization Gate (the gate this fix corrects).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification links.
- `GOV-WORK-TREE-HYGIENE-001` - dirty-finalizer class.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root platform command.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project-linkage metadata.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` defines the
commit-finalization gate the fix corrects; no new requirement is needed.

## Prior Deliberations

- `DELIB-202667182` - owner AUQ authorizing the bounded WI-5657 checker fix for superseded predecessor VERIFIED.
- `bridge/gtkb-wi5441-registry-db-schema-007.md` - the NO-GO that surfaced the finalization deadlock this fix resolves.
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-002.md` - the independent GO for this implementation scope.

## Spec-to-Test Mapping

| Specification | Test / Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (candidate exclusion) | `test_wi5657_staged_higher_sibling_marks_superseded`; `test_wi5657_superseded_plus_latest_yields_single_candidate_not_found_two` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (finding suppression) | `test_wi5657_superseded_verified_yields_no_finalization_finding`; `test_wi5657_non_superseded_terminal_verified_without_evidence_yields_finding` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (fail-closed zero candidates) | `test_wi5657_only_superseded_verified_with_latest_nogo_yields_zero_candidates` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (exact-slug matching) | `test_wi5657_exact_slug_matching_prefix_sharing_not_sibling` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (worktree false-positive regression guard) | `test_wi5657_untracked_worktree_higher_sibling_does_not_supersede_staged_latest` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full suite `platform_tests/scripts/test_check_protected_commit_authorization.py` | yes | PASS, 92 passed |

## Commands Executed

```text
python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q
python -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
python -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
```

Observed results:

- pytest: `92 passed` (84 pre-existing + 8 WI-5657), 1 unrelated `asyncio_mode` config warning.
- ruff check: `All checks passed!`
- ruff format --check: `2 files already formatted`.

## Acceptance Criteria

All GO acceptance criteria satisfied:

- Superseded VERIFIED (-004) + single latest VERIFIED (-007) -> latest is sole candidate, no "found 2". PASS.
- Superseded VERIFIED yields no finalization-evidence finding; a non-superseded terminal VERIFIED lacking evidence still yields it. PASS.
- Only-superseded (latest NO-GO) -> zero live candidates, no authorization (fail closed). PASS.
- Exact-slug matching: a prefix-sharing slug is not a sibling. PASS.
- Existing checker suite continues to pass. PASS (92/92).

## Finalization Path Set For The Verifier

The reviewed target files are uncommitted and the WI-5657 bridge chain is untracked.
A clean atomic `VERIFIED` finalization `--include` set should cover:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-001.md` through `-003.md` (plus the new `VERIFIED` verdict)

Both target-file diffs are scoped to the fix (no unrelated changes). This thread
finalizes cleanly: its own chain has a single VERIFIED candidate and no superseded
predecessor, so it does not depend on the fix it implements.

## Recommended Commit Type

`feat:` - net-new bridge-finalizer capability (superseded-predecessor handling in the
protected-commit checker) plus spec-derived tests.

## Risk / Rollback

Low. The change is a strict simplification toward more-conservative gate behavior
(fewer files marked superseded), guarded by 8 new + 84 existing tests. Rollback is a
revert of the two files. No runtime, configuration, dispatcher, or Git mutation
occurred; the PAUTH forbids git_commit, git_push, git_history_rewrite, and related
operations.

## Owner Decisions / Input

- `DELIB-202667182` (owner AskUserQuestion, 2026-07-23): authorized this bounded
  WI-5657 protected-commit checker fix for superseded predecessor VERIFIED, to unblock
  WI-5441 Phase 1B finalization and the WI-5113 dirty-finalizer class. The bounded
  `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX`
  cites this decision.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
