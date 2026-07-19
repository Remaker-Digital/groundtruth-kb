NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; active goal continuation

# WI-5344 Post-Implementation Report: Bounded Git Lifecycle Process Tree

bridge_kind: implementation_report
Document: gtkb-wi5344-git-lifecycle-bounded-process-tree
Version: 011
Implements: bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-007.md
Approved by: bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-010.md
Date: 2026-07-17 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5344

target_paths: ["platform_tests/scripts/test_modernization_git_lifecycle.py"]

## Implementation Claim

The approved frozen Git-lifecycle acceptance wrapper now uses a bounded,
headless process group with strict `600 < 750 < 900` child, wrapper, and
activity timeouts. A child timeout terminates the complete process tree,
retains bounded diagnostics, and fails the test. The checker and its 26
assertions remain unchanged.

## Governance Evidence

- Work-intent claim row: `32152`
- Claim kind: `go_implementation`
- Claim session: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`
- Implementation-start packet:
  `sha256:95f7165a543d16d1d7917d7636b98cecfb33c659707f86742ec3e221622b124d`
- Pre-start packet:
  `sha256:3771647f507f221055dd7a868974ac7d61ec2eb8e77719f1dbdb8b40dcbd7c61`
- Approved target count: one
- Source, dispatcher, TAFE, harness, eligibility, runtime JSON, lease, Git
  index, commit, push, release, and deployment state were not mutated.

## Files Changed

### `platform_tests/scripts/test_modernization_git_lifecycle.py`

- Replaced `subprocess.run(..., timeout=900)` with
  `subprocess.Popen(...).communicate(timeout=600)`.
- Uses `hidden_process_popen_kwargs(new_process_group=True)` so Windows
  execution is hidden and assigned a new process group.
- Uses `start_new_session=True` on non-Windows systems so the shared
  `_terminate_process_tree` helper can kill the complete process group.
- Raises an explicit test failure after tree termination and includes at most
  4,000 characters from each partial output stream.
- Raises the test-local pytest timeout from 180 to 750 seconds while preserving
  the frozen 900-second activity ceiling.
- Adds a fast injected-hang regression proving the process-tree terminator is
  called and the timeout cannot become PASS.
- Diff size: 87 insertions, 5 deletions.
- Post-implementation SHA-256:
  `853E232E04930A2B634F2ECC06EF88FFEE5D37B233B218E6C020870A6B040F92`

The checker remains byte-for-byte unchanged at:

- `scripts/check_modernization_git_lifecycle.py`
- SHA-256:
  `FFB2ED61FA8D71496202B1A80BB7C7831233E10240C62FE7FC4EE7194ECC73C4`

## Specification Links

- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Specification-Derived Verification

| Requirement | Executed verification | Observed result |
| --- | --- | --- |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`, `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`, `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | Full target module, three sequential repetitions | PASS at 112.27s, 127.25s, and 114.11s. Each run executed the real checker and required capability `CAP-GIT-LIFECYCLE`, report `PASS`, the exact A1-A26 set, and non-empty PASS evidence for every assertion. |
| `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` | Existing frozen checker assertions in each full run | PASS; no published-state assertion was removed or bypassed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Strict timeout assertion plus three full repetitions | PASS; `600 < 750 < 900` is enforced and valid checker work completed repeatedly without a global timeout increase. |
| Timeout failure and process-tree cleanup | Injected timeout regression and real Windows grandchild reap test | PASS; the injected timeout calls the tree terminator and raises failure, and the shared helper reaped both child and grandchild. |
| Hidden process launch | Windows subprocess helper test and injected Popen argument assertions | PASS; `CREATE_NO_WINDOW` and `CREATE_NEW_PROCESS_GROUP` are present on Windows. |
| `GOV-WORK-TREE-HYGIENE-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target inventory, checker hash, `git diff --check` | PASS; exactly one in-root approved target is modified and the checker hash is unchanged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Corrected GO, exact claim, active PAUTH, and implementation-start packet | PASS; implementation began only after version 010 GO and the WI-5354 baseline was present at HEAD. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report linkage and content-mode applicability preflight | PASS; complete project, PAUTH, work-item, target, and specification linkage is carried forward. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping and all commands below | PASS; every linked behavior has executed evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5344, TEST mapping, proposal, GO, implementation, report, and pending independent verdict | PASS through the implementation-report boundary; independent VERIFIED and focused finalization remain pending. |

## Exact Commands And Observed Results

1. First full repetition, selected through the timeout keyword which also
   matches the module timeout marker:

   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_modernization_git_lifecycle.py -k timeout -q --tb=short`

   Result: `2 passed, 1 warning in 112.27s`.

2. Second full repetition:

   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_modernization_git_lifecycle.py -q --tb=short`

   Result: `2 passed, 1 warning in 127.25s`.

3. Third full repetition:

   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_modernization_git_lifecycle.py -q --tb=short`

   Result: `2 passed, 1 warning in 114.11s`.

4. Fast forced-timeout regression:

   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_modernization_git_lifecycle.py::test_checker_timeout_terminates_process_tree_and_fails -q --tb=short`

   Result: `1 passed, 1 warning in 0.22s`.

5. Real Windows child/grandchild tree-reap coverage:

   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_run_with_status.py::test_terminate_process_tree_reaps_grandchild_on_windows -q --tb=short`

   Result: `1 passed, 1 warning in 1.93s`.

6. Windows hidden/new-group helper coverage:

   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_windows_subprocess.py::test_hidden_process_popen_kwargs_hides_and_detaches_on_windows -q --tb=short`

   Result: `1 passed, 1 warning in 0.21s`.

7. `groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests\scripts\test_modernization_git_lifecycle.py`

   Result: `All checks passed!`

8. `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests\scripts\test_modernization_git_lifecycle.py`

   Result: `1 file already formatted`.

9. `groundtruth-kb\.venv\Scripts\python.exe -m py_compile platform_tests\scripts\test_modernization_git_lifecycle.py`

   Result: exit 0.

10. `git diff --check -- platform_tests/scripts/test_modernization_git_lifecycle.py`

    Result: exit 0. Git emitted only its configured LF-to-CRLF working-copy
    notice; no patch error was reported.

11. `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5344-git-lifecycle-bounded-process-tree`

    Result: exit 0, `preflight_passed: true`,
    `missing_required_specs: []`, `missing_advisory_specs: []`.

12. `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5344-git-lifecycle-bounded-process-tree`

    Result: exit 0, three `must_apply` clauses, zero evidence gaps, zero
    blocking gaps.

All pytest invocations emitted the existing
`PytestConfigWarning: Unknown config option: asyncio_mode`. That warning is
already owned by open hygiene item WI-5262 and did not affect collection,
execution, or results.

## Acceptance Criteria

- PASS: the exact checker and all 26 Git-lifecycle assertions remain mandatory.
- PASS: child, wrapper, and activity bounds are strictly ordered 600/750/900.
- PASS: timeout terminates the complete process tree and remains a failure.
- PASS: three full sequential repetitions complete within the bounded wrapper.
- PASS: Windows launch is hidden and uses a new process group.
- PASS: only the approved in-root test target changed.
- PENDING: independent Loyal Opposition verification and focused finalization.

## Prior Deliberations

- `INTAKE-c5792b0c`
- `DELIB-20260710-GTKB-MODERNIZATION-GIT-LIFECYCLE-CHARTER`
- `DELIB-202666274`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`
- WI-5354 versions 001-004 establish the exact committed prerequisite
  baseline.
- WI-5399 owns the invalid version 008 verdict-publication defect; version 010
  is the corrected independent GO.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666274` and the active project
PAUTH authorize this bounded source/test workflow while preserving exact GO,
claim, implementation-start, independent verification, and focused
finalization gates.

## Risk And Rollback

The remaining risk is platform-specific process behavior not exercised on the
current Windows host. The implementation uses the existing cross-platform
helper contract and explicitly starts a POSIX session so the helper can kill
the process group there. Rollback is a governed focused revert of this sole
test-file hunk; it must not restore a timeout ordering where the outer wrapper
expires before the child.

## Recommended Commit Type

Recommended commit type: `test`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
