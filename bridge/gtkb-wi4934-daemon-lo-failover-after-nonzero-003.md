NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# GT-KB Bridge Implementation Report - gtkb-wi4934-daemon-lo-failover-after-nonzero - 003

bridge_kind: implementation_report
Document: gtkb-wi4934-daemon-lo-failover-after-nonzero
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4934-daemon-lo-failover-after-nonzero-002.md
Approved proposal: bridge/gtkb-wi4934-daemon-lo-failover-after-nonzero-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4934-LO-FAILOVER
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4934
Recommended commit type: fix:

## Implementation Claim

Implemented the daemon LO failover repair authorized by WI-4934.

The daemon tick now reconciles pending dispatch-run exit sidecars before its same-signature dedupe decision, so a failed launched worker no longer strands a bridge item behind `unchanged`. The daemon also preserves successful `_spawn_harness` launch metadata in dispatch state, allowing later exit-code processing to classify that launched worker. Runtime retry/backoff now records worker completion timestamps and uses completion/exit-processing time before launch time when deciding whether retry delay is active. That prevents a slow worker timeout from becoming immediately retryable only because the launch time predates the retry window.

This report does not claim the whole dispatcher is release-healthy. Live evidence still shows separate release blockers: Cursor/E has a prior failed console-spawn path, D/Ollama still timed out on live work, and F/C are showing rate-limit/backpressure warnings. Those are follow-on dispatcher release-health work, not closed by WI-4934.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - daemon-owned dispatcher work must keep bridge review moving through eligible harnesses and expose actionable failures.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher daemon remains the only automated dispatch success path; retired trigger paths are not fallback options.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status, report, and health surfaces must distinguish no-change idempotence from failed-recipient backoff/hold.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher execution must stay background/no-window safe while failures are reported through sidecars and health surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.

## Owner Decisions / Input

- `DELIB-20266508` - owner directive that dispatcher release-health is the active top priority and the failed-recipient LO stall is a release blocker.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4934-LO-FAILOVER` - active project authorization covering `WI-4934` source/test changes.

No new owner decision was required during implementation.

## Prior Deliberations

- `DELIB-20266508` - owner directive for dispatcher release-health continuation and authorization of WI-4934 LO failover repair.
- `DELIB-20266507` - prior dispatcher backpressure health classification authorization.
- `DELIB-20266505` - prior dispatcher diagnostic health release fix authorization.
- `DELIB-20266276` - daemon-resilience program implementation and release-health hardening authorization.
- `bridge/gtkb-wi4934-daemon-lo-failover-after-nonzero-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4934-daemon-lo-failover-after-nonzero-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Files Changed

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Implementation Details

- `scripts/gtkb_dispatcher_daemon.py`
  - Reconciles pending exit sidecars at the start of `compute_shadow_decisions`.
  - Writes dispatch state if reconciliation changed recipient state.
  - Falls through to later LO targets when a prior target is skipped for provider/backoff failure instead of consuming the item from `remaining`.
  - Persists `last_launch` from `_spawn_harness`, including daemon live launches, so later sidecar processing has the dispatch id, selected documents, signature, pid, and log paths it needs.

- `scripts/dispatcher_runtime.py`
  - Adds the observed Ollama timeout text (`session timeout exceeded before Ollama chat turn`) to fatal worker marker classification as `worker_timeout`.
  - Treats `worker_timeout` as a fast-trip worker failure class.
  - Records `exit_processed_at` and `completed_at` when exit sidecars are processed.
  - Backfills missing completion anchors for already-processed launches only when the exit sidecar is present, using the sidecar mtime.
  - Uses completion/exit-processing time, falling back to launch time only for legacy records, as the retry-delay anchor.

- Tests
  - Added a daemon regression proving a same-signature nonzero LO run is reconciled and the daemon falls through to the next LO target.
  - Added runtime regressions proving slow Ollama timeouts back off from completion time and legacy processed exits gain an evidence-based completion anchor without reprocessing.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py -q --tb=short` passed 167 tests. New tests directly cover daemon fallthrough after nonzero LO exit and slow timeout completion-time backoff. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Diff is limited to daemon/runtime dispatch code and focused tests. No retired trigger path is restored or used. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Live dry-run after the D failure no longer reports D `unchanged`; controlled dry-run with `GTKB_DISPATCH_RETRY_DELAY_SECONDS=1800` reports D `provider_failure_backoff_active` and falls through to E/F candidates without spawning. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | The live D run used `pythonw`/sidecar execution and produced no observed visible console window from D. No new shell-wrapper or visible-console spawn path was introduced. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work began only after GO at `bridge/gtkb-wi4934-daemon-lo-failover-after-nonzero-002.md`, work-intent claim `gtkb-wi4934-daemon-lo-failover-after-nonzero`, and implementation authorization validation for the four target files. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Report carries forward all linked specs from the approved proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each linked spec to command/live evidence for LO verification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report includes project authorization, project, work item, and target path evidence. |

## Commands Run

- `python scripts\bridge_claim_cli.py status gtkb-wi4934-daemon-lo-failover-after-nonzero` - claim was active.
- `python scripts\bridge_claim_cli.py extend gtkb-wi4934-daemon-lo-failover-after-nonzero` - claim extended to `2026-06-30T11:21:42Z`.
- `python scripts\implementation_authorization.py validate --target scripts\dispatcher_runtime.py` - authorized.
- `python scripts\implementation_authorization.py validate --target platform_tests\scripts\test_dispatcher_runtime.py` - authorized.
- `python scripts\implementation_authorization.py validate --target scripts\gtkb_dispatcher_daemon.py` - authorized.
- `python scripts\implementation_authorization.py validate --target platform_tests\scripts\test_gtkb_dispatcher_daemon.py` - authorized.
- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py::test_long_running_ollama_timeout_backs_off_from_completion_time -q --tb=short` - passed.
- `python -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py::test_daemon_reconciles_nonzero_exit_and_falls_back_to_next_lo -q --tb=short` - passed.
- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py::test_process_pending_exit_codes_backfills_processed_completion_anchor platform_tests\scripts\test_dispatcher_runtime.py::test_long_running_ollama_timeout_backs_off_from_completion_time platform_tests\scripts\test_dispatcher_runtime.py::test_retry_delay_clears_after_launch_window_elapses platform_tests\scripts\test_dispatcher_runtime.py::test_retry_delay_enforced_within_launch_window -q --tb=short` - passed 4 tests.
- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py::test_lo_provider_failure_backoff_retries_preferred_after_retry_window platform_tests\scripts\test_dispatcher_runtime.py::test_process_pending_exit_codes_backfills_processed_completion_anchor -q --tb=short` - passed 2 tests after tightening the backfill.
- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short` - passed 126 tests.
- `python -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py -q --tb=short` - passed 41 tests.
- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py -q --tb=short` - passed 167 tests in 43.54s.
- `python -m ruff check scripts\gtkb_dispatcher_daemon.py scripts\dispatcher_runtime.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_runtime.py` - passed.
- `python -m ruff format --check scripts\gtkb_dispatcher_daemon.py scripts\dispatcher_runtime.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_runtime.py` - passed; 4 files already formatted.
- `python scripts\gtkb_dispatcher_daemon.py tick --max-items 1 --dry-run` - post-fix live dry-run no longer reported D `unchanged`; default retry window had expired, so D was retry-eligible.
- `GTKB_DISPATCH_RETRY_DELAY_SECONDS=1800 python scripts\gtkb_dispatcher_daemon.py tick --max-items 1 --dry-run` - controlled dry-run showed D `provider_failure_backoff_active` and fallthrough to later LO candidates without spawning unsafe E.

## Observed Live Evidence

- Live D dispatch `2026-06-30T10-20-39Z-loyal-opposition-D-b7f0b9` launched through the daemon path for `gtkb-wi4258-push-readiness-diagnostic`.
- The launch used `C:\Python314\pythonw.exe` wrapping `scripts/run_with_status.py`, with child `groundtruth-kb\.venv\Scripts\pythonw.exe scripts/ollama_harness.py`, so this observed D path was background/no-window safe.
- Sidecar result: `.gtkb-state/bridge-poller/dispatch-runs/2026-06-30T10-20-39Z-loyal-opposition-D-b7f0b9.exit_code` contained `1`.
- Stderr: `.gtkb-state/bridge-poller/dispatch-runs/2026-06-30T10-20-39Z-loyal-opposition-D-b7f0b9.stderr.log` contained `ollama_harness: session timeout exceeded before Ollama chat turn`.
- Dispatcher health after that failure reported runtime failures for D and E, and backpressure warnings for C/F. This is expected residual release-health work, not closed by WI-4934.

## Acceptance Criteria Status

- PASS: A focused daemon regression now proves a same-signature failed LO recipient is not classified as `unchanged` on the next daemon tick.
- PASS: When another eligible LO target is available and ready, the daemon falls through to it in the regression test.
- PASS: Failed launch/timeout evidence is surfaced as `provider_failure_backoff_active`, `worker_timeout`, or concrete failure class evidence instead of silent no-change.
- PASS: Focused runtime + daemon tests pass together: 167 passed.
- PASS: Ruff check and format-check pass for all four touched files.
- PASS WITH RESIDUAL: A post-fix live daemon dry-run no longer reports D `unchanged`; however, with the default 5-minute retry delay already elapsed, live dry-run selected D as retry-eligible. A controlled dry-run with an extended retry window demonstrated the fallthrough path without launching unsafe Cursor/E.

## Risk And Rollback

Risk is moderate because this touches dispatch control flow and retry timing. The change is scoped to failed launched workers: clean same-signature idempotence still produces `unchanged`, and legacy processed records without sidecar evidence keep the previous launch-time fallback.

Rollback is a revert of:

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that WI-4934 is satisfied by the daemon reconciliation/fallthrough behavior and runtime completion-time retry anchor.
2. Do not treat this report as a release-health claim for the entire dispatcher. The remaining D/E/F/C health blockers should continue in subsequent dispatcher release-hardening work.
