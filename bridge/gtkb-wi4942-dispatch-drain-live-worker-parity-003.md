NEW

# Implementation Report: WI-4942 dispatch drain live-worker parity

bridge_kind: implementation_report
Document: gtkb-wi4942-dispatch-drain-live-worker-parity
Version: 003
Date: 2026-06-30 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-30T23-13-03Z-prime-builder-A-f3f1e0
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4942-DRAIN-LIVE-WORKER-PARITY
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4942

## Summary

Implemented the approved WI-4942 drain/report parity repair. `gt bridge dispatch drain --dry-run` now discovers provenance-verified live dispatch-run workers from `.gtkb-state/bridge-poller/dispatch-runs/*.pid`, not only legacy lease locks. Actual drain uses the same worker discovery path before terminating stragglers, while preserving the existing marker-first drain behavior.

Implementation-start authorization passed before protected-source/test work:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4942-dispatch-drain-live-worker-parity --session-id 2026-06-30T23-13-03Z-prime-builder-A-f3f1e0
```

Packet hash: `sha256:99363192945e997235d7261a49848b48f1b1e0a572a4c98f1413cadd3a5b28e2`.

## Files Changed

WI-4942 implementation changes are scoped to:

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`
- `groundtruth-kb/tests/test_bridge_dispatch_reset.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

Approved target paths with no WI-4942 source change needed:

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`

Dirty-worktree note: `groundtruth-kb/src/groundtruth_kb/cli.py` already had unrelated backlog/audit CLI edits before this implementation pass. Those edits were not changed or relied on for WI-4942; the existing drain CLI already delegates to `bridge_dispatch_reset.drain()`.

## Implementation Details

- Added dispatch-run worker discovery via `read_live_dispatch_runs()`.
- Added `read_live_workers()` to merge dispatch-run workers with legacy lease workers while de-duplicating PIDs.
- Updated drain dry-run and live drain wait/termination paths to use `read_live_workers()`.
- Kept PID provenance strict: live dispatch-run workers require a live PID and matching `*.create_time_epoch` sidecar before drain reports or terminates them.
- Preserved Windows no-window safety by reusing existing PID liveness helpers that pass `CREATE_NO_WINDOW` for `tasklist`.
- Added focused unit, runtime-status, and CLI regression coverage proving drain sees dispatch-run workers.

## Specification-To-Test Mapping

| Governing surface | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `test_drain_dry_run_matches_status_live_dispatch_run_pids`, `test_bridge_dispatch_drain_dry_run_reports_live_dispatch_run_worker`, and live `report`/`drain --dry-run` evidence prove report-visible live workers are drain-visible. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_drain_dry_run_reports_live_dispatch_run_workers` and `test_drain_terminates_live_dispatch_run_workers` prove daemon dispatch-run sidecars are handled through governed drain. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Code inspection: no retired poller/hook path or alternate queue was restored; implementation uses existing dispatcher state directories and `dispatch-runs` sidecars. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Existing no-window PID liveness path remains in use for Windows process probes; no visible-shell launch path was added. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge state remains the numbered file chain plus dispatcher/TAFE state. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries forward linked specs and includes executed command evidence below. |
| `GOV-STANDING-BACKLOG-001` | WI-4942 remains the durable MemBase work item for this regression and this report links the bridge thread back to that WI. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched paths are inside `E:\GT-KB`. |

## Verification Commands

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short
```

Observed result: `66 passed in 5.68s`.

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
```

Observed result: `All checks passed!`

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
```

Observed result: `6 files already formatted`.

Live evidence:

```text
gt bridge dispatch report --json
gt bridge dispatch drain --timeout 1 --dry-run --json
```

Observed parity snapshot after implementation:

- report compact summary: `live_worker_count=2`, live PIDs `28704` and `84888`
- drain dry-run: `drained_pids=[84888, 28704]`, `terminated_pids=[]`, `drain_markers_written=0`

Earlier same-pass live evidence also showed report `live_worker_count=6` and drain dry-run returned six corresponding PIDs: `[94192, 75320, 6320, 1544, 50180, 59768]`.

```text
gt bridge dispatch health --json
```

Observed result: `health_status=WARN`; current findings are unrelated live dispatcher/runtime warnings and failures for other pending bridge work, not a drain/report invisibility result.

```text
gt bridge dispatch daemon status --json
```

Observed result: daemon running under `dispatcher_daemon`, `mode=live`, `pid_provenance_verified=true`, with a fresh heartbeat.

## Acceptance Status

- Report-visible live dispatch-run workers are now drain-visible in dry-run.
- Dry-run remains non-mutating and reports candidate PIDs.
- Actual drain uses the same provenance-verified worker source before terminating stale live workers.
- No routing policy, provider eligibility, credential lifecycle, production deployment, retired poller, hook-triggered dispatch, or alternate queue behavior was changed.
- Windows PID probing remains no-window safe.

## Risks / Rollback

Primary risk is over-termination. The implementation mitigates this by requiring dispatch-run PID liveness plus create-time provenance before reporting or terminating candidates. Rollback is limited to reverting the WI-4942 source/test changes in the files listed above.

## Recommended Commit Type

Recommended commit type: `fix(dispatcher):`
