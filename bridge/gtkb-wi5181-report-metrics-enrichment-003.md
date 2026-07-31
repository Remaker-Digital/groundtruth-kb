NEW

# GT-KB Bridge Implementation Report - gtkb-wi5181-report-metrics-enrichment - 003

bridge_kind: implementation_report
Document: gtkb-wi5181-report-metrics-enrichment
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5181-report-metrics-enrichment-002.md
Approved proposal: bridge/gtkb-wi5181-report-metrics-enrichment-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5181-REPORT-METRICS-20260711
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5181
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated worker session document
author_metadata_source: validated worker session document
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]
Recommended commit type: feat:

## Implementation Claim

Extended only the existing compact JSON and human `gt bridge dispatch report`
views with bounded `recent_work_metrics` derived from the latest canonical
WI-5180 snapshot in MemBase. The reader opens SQLite in read-only mode,
validates the versioned snapshot, projects an explicit allowlist, bounds every
distribution and breakout, preserves provider-reported and benchmark-estimated
cost coverage separately, and reports unavailable, partial, stale, or observed
states without suppressing workflow queues.

`build_bridge_dispatch_report` and the full `--json` payload are unchanged. The
feature has no provider request, raw-runtime recomputation, competing command,
metrics write, tuning, or dispatcher/role/claim/configuration mutation path.

## Specification Links

- `SPEC-DISPATCH-REPORT-METRICS-ENRICHMENT-001`
- `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001`
- `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001`
- `SPEC-HARNESS-OBSERVABILITY-SELF-TUNING-PROGRAM-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Owner Decisions / Input

No new owner decision is required. WI-5180 is independently VERIFIED and
committed at `5c9fd3bf`; the WI-5181 PAUTH, independent GO, matching claim, and
implementation-start packet governed this work.

## Specification-Derived Verification Plan

| Requirement | Evidence |
| --- | --- |
| Full JSON preservation | Existing exact top-level contract test plus the WI-5181 test assert no `recent_work_metrics` key in full JSON. |
| Compact/human parity | Tests assert the same snapshot id, availability, record count, and coverage are rendered by both views. |
| Snapshot-only bounded projection | Tests seed canonical snapshots and assert 20-record breakout bounds and fixed allowlisted fields. |
| Availability semantics | Separate tests cover unavailable, partial, and stale states while queues remain visible. |
| Cost/privacy safety | Tests prove cost categories remain separate and injected prompt/tool/provider-body content is absent. |
| Read-only behavior | Tests byte-compare MemBase, dispatcher config, registry, and runtime state before and after all report variants. |

## Commands Run

- `python -m pytest -o addopts= platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short`
- `python -m pytest -o addopts= platform_tests/groundtruth_kb/test_dispatch_default_metrics.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`
- `python -m groundtruth_kb.cli bridge dispatch report --compact --json`

## Observed Results

- Focused dispatcher-report suite: `15 passed`.
- Combined canonical-snapshot and report suite: `19 passed`.
- Ruff check: passed.
- Ruff format check: passed (`2 files already formatted`).
- Live compact report: passed and returned
  `availability=unavailable`, `reason=canonical_snapshot_unavailable`, while
  preserving status, in-flight work, and both role queues.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

The test file still contains the proposal-disclosed foreign three-line removal
of the `sys.modules` cache-reset loop. WI-5181 did not create or alter that hunk.
The reviewed WI-5181-only test patch is:
`.gtkb-state/verified-hunk-patches/wi5181-report-tests.patch`.

For VERIFIED finalization, pass the source path normally and pass the test path
in the include set with:
`--hunk-patch .gtkb-state/verified-hunk-patches/wi5181-report-tests.patch`.
This leaves the unrelated deletion uncommitted in the shared worktree.

## Acceptance Criteria Status

- [x] Full report JSON remains contract-compatible and has no metrics key.
- [x] Compact JSON adds one bounded canonical `recent_work_metrics` object.
- [x] Human workflow renders an equivalent section after queues.
- [x] Unavailable, partial, stale, and nullable values are explicit.
- [x] Provider and benchmark cost coverage remain separate.
- [x] Workflow status, in-flight work, and queues remain present.
- [x] Report variants are read-only and privacy-bounded.

## Risk And Rollback

The feature is observational. Rollback is limited to the two authorized paths.
The hunk patch keeps the pre-existing foreign test deletion outside the WI-5181
commit.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and test evidence.
2. Use the supplied hunk patch during finalization so the unrelated cache-reset deletion remains unstaged.
3. Return VERIFIED if the implementation satisfies the approved scope, otherwise return NO-GO with concrete findings.
