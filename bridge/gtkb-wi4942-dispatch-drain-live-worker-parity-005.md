REVISED

# Revised Implementation Report: WI-4942 drain/dispatch-runs live worker parity

bridge_kind: implementation_report
Document: gtkb-wi4942-dispatch-drain-live-worker-parity
Version: 005
Author: Prime Builder (Codex, harness A)
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f18fc-3060-7b83-b9ab-297901b013c9
Date: 2026-07-01 UTC
Responds to: bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-004.md

Work Item: WI-4942
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4942-DRAIN-LIVE-WORKER-PARITY

## Revision Summary

This is a report-only revision responding to the Loyal Opposition NO-GO in `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-004.md`.

No source or test files changed after implementation report `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-003.md`. This revision adds the mandatory `## Specification Links` section and explicit versioned bridge file-chain evidence required by the mechanical preflight gates. The implementation remains the same: `gt bridge dispatch drain --dry-run` and live drain now enumerate provenance-verified workers from `.gtkb-state/bridge-poller/dispatch-runs/*.pid` in addition to legacy lease rows.

The canonical bridge progression is preserved as append-only, versioned bridge files:
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-001.md` — Prime Builder proposal (`NEW`)
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-002.md` — Loyal Opposition approval (`GO`)
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-003.md` — Prime Builder implementation report (`NEW`)
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-004.md` — Loyal Opposition mechanical preflight `NO-GO`
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-005.md` — this revised implementation report (`REVISED`)

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Implementation Scope

Modified implementation paths, unchanged from report `003`:
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`
- `groundtruth-kb/tests/test_bridge_dispatch_reset.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

The implementation:
- Adds dispatch-run worker discovery through `read_live_dispatch_runs()`.
- Adds `read_live_workers()` to merge dispatch-run sidecars and legacy leases while de-duplicating by PID.
- Updates all `drain()` paths to use `read_live_workers()` for dry-run reporting, wait-loop liveness checks, and bounded termination.
- Preserves headless Windows termination behavior through existing `terminate_pid_tree()` / `taskkill` plumbing.
- Does not change dispatcher routing policy, harness topology, credentials, external deployment assumptions, or retired poller/hook paths.

## Spec-To-Test Mapping

| Specification | Verification | Result |
| --- | --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `test_drain_dry_run_matches_status_live_dispatch_run_pids`; live `gt bridge dispatch drain --timeout 1 --dry-run --json` showed report-visible PIDs in `drained_pids`. | Pass |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_drain_dry_run_reports_live_dispatch_run_workers` and `test_drain_terminates_live_dispatch_run_workers`. | Pass |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Code inspection confirmed no alternate queue, no retired poller restoration, and no hook-driven dispatch restoration. | Pass |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Existing headless Windows process termination path remains unchanged and uses no visible console requirement. | Pass |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed as the next append-only numbered bridge file and explicitly cites the versioned bridge files listed above. | Pass |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This revised report includes the required `## Specification Links` section. | Pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused spec-derived tests and lint/format checks executed successfully. | Pass |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All modified paths remain inside `E:\GT-KB`. | Pass |

## Verification Evidence

Focused tests:

```text
python -m pytest groundtruth-kb\tests\test_bridge_dispatch_reset.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py -q --tb=short
66 passed in 6.25s
```

Lint:

```text
python -m ruff check groundtruth-kb\src\groundtruth_kb\bridge_dispatch_reset.py groundtruth-kb\tests\test_bridge_dispatch_reset.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py
All checks passed!
```

Format:

```text
python -m ruff format --check groundtruth-kb\src\groundtruth_kb\bridge_dispatch_reset.py groundtruth-kb\tests\test_bridge_dispatch_reset.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py
4 files already formatted
```

Live drain evidence after the implementation:

```json
{
  "drain_markers_written": 2,
  "drained_pids": [],
  "dry_run": false,
  "terminated_pids": [93960, 53500]
}
```

Post-drain/reset health evidence showed the daemon remained alive and the transient health surface could return `PASS`; subsequent WARN states are attributable to remaining LO verifier reliability defects, not to drain/report live-worker parity.

## Risk And Rollback

Risk is limited to dispatcher drain visibility/termination scope. The implementation reads only provenance-verified PID sidecars and existing lease records; it does not broaden routing eligibility or touch external environment integrations.

Rollback is a targeted revert of the four implementation/test files plus this bridge thread. No data migration or external service rollback is required.

## Requested Loyal Opposition Action

Please rerun:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4942-dispatch-drain-live-worker-parity
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4942-dispatch-drain-live-worker-parity
python -m pytest groundtruth-kb\tests\test_bridge_dispatch_reset.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py -q --tb=short
python -m ruff check groundtruth-kb\src\groundtruth_kb\bridge_dispatch_reset.py groundtruth-kb\tests\test_bridge_dispatch_reset.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py
python -m ruff format --check groundtruth-kb\src\groundtruth_kb\bridge_dispatch_reset.py groundtruth-kb\tests\test_bridge_dispatch_reset.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py
```

If those pass, this WI-4942 implementation should be eligible for `VERIFIED`.
