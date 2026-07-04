NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 2026-07-04T16-34-17Z-prime-builder-A-b374ae
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: codex-exec-xhigh-approval-never-workspace-write

# GT-KB Bridge Implementation Report - gtkb-wi4455-platform-tests-bridge-derived-spec-before-code - 003

bridge_kind: implementation_report
Document: gtkb-wi4455-platform-tests-bridge-derived-spec-before-code
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-002.md
Approved proposal: bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4455
Recommended commit type: fix:

## Implementation Claim

Implemented WI-4455 Option A for the managed `spec-before-code` template hook.

The hook now preserves the existing `source_paths` lookup for all source files and adds a narrowly scoped fallback for `platform_tests/` source paths. When the target path is under `platform_tests/`, the hook scans in-root numbered, status-bearing bridge markdown files and treats the path as covered only when the bridge evidence explicitly references that platform test path. This lets bridge Spec-to-Test Mapping or `target_paths` evidence satisfy the advisory without requiring a duplicate `source_paths` mirror for platform tests.

The implementation did not edit the active root `.claude/hooks/spec-before-code.py`, dispatcher runtime/configuration, MemBase schema, formal specifications, or unrelated dirty-tree files.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the implementation remains in the numbered bridge chain and consumes numbered bridge files as the authority surface for bridge-derived evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries Project Authorization, Project, Work Item, and scoped file evidence forward from the approved proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal cited governing specs and this report maps verification evidence back to them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused tests derived from the approved acceptance criteria were added and executed.
- `GOV-STANDING-BACKLOG-001` - WI-4455 advanced through project authorization, bridge GO, and this implementation report without resolving the work item prematurely.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the implementation uses durable bridge artifacts instead of ad hoc or harness-local scratch evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Option A avoids creating a second `source_paths` mirror for platform-test linkage.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the implementation follows the proposal -> GO -> implementation report lifecycle state chain.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the hook keeps the stdin/stdout JSON contract exercised by the existing hook test harness.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation files are in-root GT-KB platform paths authorized by the proposal.
- `SPEC-AUQ-POLICY-ENGINE-001` - no new owner input was collected; this implementation relies on the standing PAUTH and Loyal Opposition GO.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` and `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` remain the carried-forward owner authorization evidence for this Reliability Fixes work item.
- `bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-002.md` is the Loyal Opposition GO authorizing this implementation.
- No new owner decision was requested or required during implementation.

## Prior Deliberations

- `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md` - Loyal Opposition policy GO for WI-4455 Option A.
- `bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-16-11-wi4455-platform-tests-spec-before-code-decision-packet.md` - decision packet identifying Option A as the preferred path.

## Implementation Details

- Added path normalization and explicit path-token matching helpers to `groundtruth-kb/templates/hooks/spec-before-code.py`.
- Limited bridge-derived coverage to targets whose normalized path is under `platform_tests/`.
- Limited the bridge scan to in-root `bridge/*.md` files whose filenames are numbered bridge versions and whose first non-blank line is a canonical status token.
- Preserved the existing `source_paths` behavior for source files outside `platform_tests/`, including existing no-source-paths, matched, unmatched, non-source, and migrated-DB cases.
- Added regression coverage for a mapped platform test path and an unmapped platform test path in `groundtruth-kb/tests/test_governance_hooks.py`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi4455-platform-tests-bridge-derived-spec-before-code --json --compact` reported latest status `GO`; implementation report prepared as next numbered bridge entry `-003`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-wi4455-platform-tests-bridge-derived-spec-before-code` produced packet hash `sha256:8bc503416f589615cab978d064468adc909a68589cdfc4de4acf716cb62ff5b8`, PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, project `PROJECT-GTKB-RELIABILITY-FIXES`, WI `WI-4455`, and the two authorized target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal's linked specifications and maps the implementation/tests back to each governing surface. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest command executed the existing source-path cases plus the two new bridge-derived platform-test cases: `7 passed`. |
| `GOV-STANDING-BACKLOG-001` | No work-item resolution or MemBase mutation was performed before Loyal Opposition verification; WI-4455 remains represented through the bridge chain. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The implementation reads only status-bearing numbered bridge files for bridge-derived evidence and ignores harness-local scratch surfaces. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The new positive test proves bridge evidence can satisfy a platform test path without matching `source_paths`; the negative test proves unrelated bridge evidence does not broaden coverage. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This report is the post-implementation `NEW` lifecycle artifact responding to the GO verdict. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests invoke the hook through `_run_hook`, preserving the subprocess stdin/stdout JSON contract. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only -- groundtruth-kb/templates/hooks/spec-before-code.py groundtruth-kb/tests/test_governance_hooks.py` showed only the two approved in-root files for this implementation slice. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No prose owner decision or AskUserQuestion interaction was needed; implementation authority came from standing PAUTH plus GO. |

## Commands Run

- `.\groundtruth-kb\.venv\Scripts\gt.exe harness roles`
- `.\groundtruth-kb\.venv\Scripts\gt.exe bridge show gtkb-wi4455-platform-tests-bridge-derived-spec-before-code --json --compact`
- `.\groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status --json`
- `.\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4455-platform-tests-bridge-derived-spec-before-code`
- With `TMP`, `TEMP`, and `PYTEST_DEBUG_TEMPROOT` set to `E:\GT-KB\.harness-tmp`: `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_governance_hooks.py::test_spec_before_code_no_source_paths groundtruth-kb\tests\test_governance_hooks.py::test_spec_before_code_match groundtruth-kb\tests\test_governance_hooks.py::test_spec_before_code_no_match groundtruth-kb\tests\test_governance_hooks.py::test_spec_before_code_non_source_file groundtruth-kb\tests\test_governance_hooks.py::test_spec_before_code_match_via_migrated_db groundtruth-kb\tests\test_governance_hooks.py::test_spec_before_code_platform_tests_match_via_bridge_evidence groundtruth-kb\tests\test_governance_hooks.py::test_spec_before_code_platform_tests_unmapped_bridge_evidence_warns -q --tb=short`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\templates\hooks\spec-before-code.py groundtruth-kb\tests\test_governance_hooks.py`
- `.\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\templates\hooks\spec-before-code.py groundtruth-kb\tests\test_governance_hooks.py`
- With `TMP`, `TEMP`, and `PYTEST_DEBUG_TEMPROOT` set to `E:\GT-KB\.harness-tmp`: `.\groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_governance_hooks.py -q --tb=short`

## Observed Results

- Role resolution: Codex harness `A` resolved as `prime-builder`.
- Bridge status: selected document latest status was `GO` at `bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-002.md`.
- Dispatcher status: dispatcher health was `PASS`; Prime Builder recipient showed the work intent already held for this dispatch.
- Implementation authorization: succeeded with packet hash `sha256:8bc503416f589615cab978d064468adc909a68589cdfc4de4acf716cb62ff5b8`, expiring `2026-07-04T18:36:28Z`.
- Focused spec-before-code pytest: `7 passed, 1 warning in 3.38s` after rerun with the workspace temp root.
- Ruff lint: `All checks passed!`
- Ruff format check: `2 files already formatted`.
- Broader `groundtruth-kb/tests/test_governance_hooks.py` run: `17 failed, 41 passed, 2 warnings in 19.31s`. The failures were in pre-existing destructive-gate, credential-scan, and bridge-compliance expectations, not in the spec-before-code cases. Direct self-test sanity checks outside this change showed current `destructive-gate.py --self-test` emits `{"decision": "block", ...}` and current `credential-scan.py --self-test` emits `{}`, matching the broader failures' out-of-scope behavior. This implementation did not edit those hook templates.
- Initial pytest attempts using the default Windows temp root failed before test execution with `PermissionError: [WinError 5] Access is denied: 'C:\Users\micha\AppData\Local\Temp\pytest-of-micha'`; reruns used the workspace temp root.

## Files Changed

Implementation-scope files changed by this dispatch:

- `groundtruth-kb/templates/hooks/spec-before-code.py`
- `groundtruth-kb/tests/test_governance_hooks.py`

The helper plan detected a large pre-existing dirty tree. Those unrelated files were not modified as part of this WI-4455 implementation and are intentionally excluded from this report's implementation-scope file list.

## Acceptance Criteria Status

- Complete: A `platform_tests/.../test_*.py` path with explicit bridge Spec-to-Test Mapping and `target_paths` evidence no longer emits the false `No specification found covering ...` advisory.
- Complete: An unrelated `platform_tests/.../test_*.py` path without matching `source_paths` or matching bridge-derived evidence still emits the advisory.
- Complete for WI-4455 scope: existing spec-before-code no-source-paths, matching-source-paths, non-matching-source-paths, non-source-file, and migrated-DB tests continue to pass.
- Complete: No active root hook restoration, dispatcher/config mutation, MemBase schema mutation, or formal artifact insertion was performed in this implementation slice.

## Risk And Rollback

Residual risk: the bridge-evidence scan is intentionally text-based. It is limited to `platform_tests/` targets, numbered bridge filenames, canonical status-token files, and exact path-token matches to keep false positives narrow. Loyal Opposition should inspect the path matching for overbreadth.

Rollback path: revert the changes to `groundtruth-kb/templates/hooks/spec-before-code.py` and `groundtruth-kb/tests/test_governance_hooks.py`. The bridge audit chain remains append-only.

## Recommended Commit Type

Recommended commit type: fix:

Justification: this repairs a hook-layer false advisory for platform tests without adding a new external capability surface.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Treat the broad `test_governance_hooks.py` failures as out-of-scope unless inspection shows this WI-4455 change caused or worsened them.
