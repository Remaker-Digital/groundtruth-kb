NEW

Document: gtkb-deliberation-search-stale-segment-failfast
Version: 003
Status: NEW
Date: 2026-06-19
From: Prime Builder (harness A / Codex)
To: Loyal Opposition
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4568
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T03-43-54Z-prime-builder-A-2de538
author_model: Codex GPT-5
author_model_version: GPT-5
author_model_configuration: Codex headless bridge auto-dispatch; approval_policy=never
parent_bridge_id: gtkb-deliberation-search-stale-segment-failfast-002
bridge_kind: implementation_report

# Implementation Report: Deliberation-search stale-segment fast-fail and semantic-only fail-closed

## Summary

Implemented the approved non-destructive WI-4568 reliability slice:

- `KnowledgeDB.search_deliberations` now classifies known stale/incompatible Chroma HNSW segment errors and breaks without retrying the same doomed semantic query.
- Transient Chroma query errors still retain the configured retry budget.
- Each deliberation search records internal per-call semantic status so callers can distinguish successful semantic zero-match from degraded SQLite LIKE fallback.
- `gt deliberations search --semantic-only` now exits non-zero when semantic search degraded, instead of reporting a clean no-match after fallback.
- Added hermetic regression coverage for stale-segment fast-fail, transient retry preservation, successful zero-match status, and semantic-only fail-closed behavior.

No destructive Chroma recovery, segment deletion, process/thread reaping, schema migration, or public CLI expansion was performed.

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001 - WI-4568 defect-origin reliability fix under the standing reliability fast lane.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 - deliberation search is a mandatory governance read surface; degraded semantic-only search must not be silent.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - implementation includes spec-derived regression tests and executed evidence.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries forward the proposal's governing specification links.
- GOV-FILE-BRIDGE-AUTHORITY-001 - implementation and verification are routed through the numbered bridge chain.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - defect, fix, tests, and verification are preserved as durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - the reliability defect and remediation are captured in the bridge workflow.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - deliberation-search changes are represented through the artifact lifecycle.

## Implementation Authorization

- Implementation-start packet created with `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-deliberation-search-stale-segment-failfast`.
- Packet hash: `sha256:89d58172b1ff0b4a62a121335784891b82056c9e6ed961447db3b57f67745ed9`.
- Live latest bridge status at implementation start: `GO`.
- Scope matched approved `target_paths`.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_deliberation_search_stale_segment.py`

The worktree contained many unrelated pre-existing modified/untracked files before this dispatch. They were not included in this implementation report's scope.

## Spec-to-Test Mapping

| Specification / acceptance criterion | Test or verification evidence |
|---|---|
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001: stale/incompatible semantic search failures must not silently mask the Deliberation Archive read surface | `platform_tests/scripts/test_deliberation_search_stale_segment.py::test_stale_segment_error_fast_fails_without_retry`; `::test_semantic_only_fails_closed_when_semantic_pass_degrades` |
| Proposal stale-format fast-fail: stale HNSW/knn/log replay error should be attempted once and then fall back to LIKE | `test_stale_segment_error_fast_fails_without_retry` asserts one query call despite `_CHROMA_QUERY_RETRIES=4`, text-match fallback results, and `degradation_reason == "stale_segment"` |
| Proposal transient retry preservation: non-stale generic errors keep retry behavior | `test_transient_chroma_error_still_retries` asserts the second attempt succeeds semantically and `semantic_degraded` is false |
| Proposal degradation signal: successful semantic zero-match is distinct from degraded fallback | `test_successful_empty_semantic_pass_is_not_degraded` asserts empty semantic collection success records `semantic_succeeded` true and `semantic_degraded` false |
| Proposal semantic-only fail-closed: degraded semantic pass exits non-zero instead of clean no-match | `test_semantic_only_fails_closed_when_semantic_pass_degrades` asserts exit code 1 and no fallback row output |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | New focused test file plus existing CLI/search regressions executed; ruff lint and format gates passed |
| GOV-FILE-BRIDGE-AUTHORITY-001 / DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This post-implementation report carries forward governing specs and is filed as the next numbered bridge entry |

## Commands And Observed Results

Pytest was run with `-o addopts=''` and workspace `--basetemp` paths because this Windows dispatch environment lacks the configured `pytest-timeout` addopt plugin and default `%TEMP%` access is denied. Those environment issues were isolated from test behavior.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts='' --basetemp E:\GT-KB\.gtkb-tmp\pytest-wi4568-report-new platform_tests/scripts/test_deliberation_search_stale_segment.py -q --tb=short
```

Observed result: `4 passed, 2 warnings in 2.72s`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts='' --basetemp E:\GT-KB\.gtkb-tmp\pytest-wi4568-report-regressions groundtruth-kb/tests/test_cli_deliberations.py::TestDeliberationsSearch groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py platform_tests/scripts/test_fab17_chroma_read_path.py -q --tb=short
```

Observed result: `16 passed, 3 warnings in 15.26s`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_deliberation_search_stale_segment.py
```

Observed result: `All checks passed!`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_deliberation_search_stale_segment.py
```

Observed result: `3 files already formatted`.

```powershell
git diff --check -- groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_deliberation_search_stale_segment.py
```

Observed result: exit 0, no whitespace errors.

## Acceptance Status

- Stale-format fast-fail: satisfied.
- Per-call degradation signal: satisfied through package-internal search status.
- `--semantic-only` fail-closed on degradation: satisfied.
- Transient retry preservation: satisfied.
- Optional dependency and existing fallback behavior: regression coverage passed.
- Destructive recovery policy: unchanged and out of scope.

## Risk / Rollback

- Risk: stale-segment pattern matching could catch an error that might have recovered on retry. Mitigation: patterns are specific to known HNSW/log replay/knn stale segment failures; non-matching errors still retry.
- Risk: strict semantic-only mode may now fail workflows that previously treated degraded fallback as no-match. Mitigation: that silent success was the defect; default non-strict search behavior remains fallback-tolerant.
- Rollback: revert the two source edits and remove `platform_tests/scripts/test_deliberation_search_stale_segment.py`; no data migration or index mutation is involved.

## Recommended Commit Type

Recommended commit type: `fix:`

`fix:` - repairs doomed semantic retry amplification and silent semantic-only degradation on the deliberation-search read path.
