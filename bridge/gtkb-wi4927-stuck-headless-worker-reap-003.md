NEW

# GT-KB Bridge Implementation Report - gtkb-wi4927-stuck-headless-worker-reap - 003

bridge_kind: implementation_report
Document: gtkb-wi4927-stuck-headless-worker-reap
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-30 UTC
Responds to GO: bridge/gtkb-wi4927-stuck-headless-worker-reap-002.md
Approved proposal: bridge/gtkb-wi4927-stuck-headless-worker-reap-001.md
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop interactive Prime Builder session; cwd=E:\GT-KB; owner disabled hooks before restart for diagnosis
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4927
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4927-STUCK-HEADLESS-WORKER-REAP
Recommended commit type: fix:

## Implementation Claim

Implemented the WI-4927 stuck headless worker reap slice for dispatcher-owned desktop/headless workers.

- `scripts/ops/harness_storm_watchdog.ps1` now includes daemon `pythonw.exe scripts/run_with_status.py ...` wrapper processes in its candidate set, including Codex `exec` wrappers and non-Codex harness wrappers. It parses each wrapper's `--lifetime` and sends `max_lifetime_seconds` to the decider.
- `scripts/ops/storm_watchdog_reap.py` now protects dispatcher wrapper roots and their descendants while they are within their configured lifetime, and marks them reapable as `over_lifetime_straggler` after that lifetime expires.
- `scripts/cursor_harness.py` now records best-effort Cursor agent orphan provenance during dispatcher-controlled runs only, keyed by `GTKB_BRIDGE_POLLER_RUN_ID` / `GTKB_INHERITED_SESSION_ID`. It snapshots GT-KB-workspace `agent` / `cursor-agent` processes before and after the Cursor Agent launch, then writes newly-created agent PID/create-time records to the existing `.gtkb-state/ops/dispatch-provenance/dispatch-provenance.json` ledger with the current shim PID as dispatch root.
- `scripts/ops/harness_storm_watchdog.ps1` now includes project-bound `agent` / `cursor-agent` processes as non-dispatched candidates. They are ignored unless the existing provenance ledger precisely attributes them to a dead dispatched root, preserving the WI-4828 interactive-session safety boundary.
- Focused regression tests now cover run-with-status wrapper lifetime protection/reap, Cursor agent provenance generation, dispatcher-only provenance recording, project-bound cursor-agent candidate visibility, and provenanced cursor-agent orphan reap.

The surrounding worktree contains substantial unrelated dirty work. This report intentionally scopes evidence and changed-file claims to the WI-4927 target paths below.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected dispatcher/storm-watchdog scripts require bridge GO before mutation.
- `GOV-17` - automation script modification approval gate; this slice modifies dispatcher/storm-watchdog automation.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher owns worker lifecycle; orphaned headless agents violate operability.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - centralized dispatch must not leak stuck workers across harness topologies.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal carries WI/project/PAUTH and target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable linkage block present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report carries exact command evidence for LO verification.
- `GOV-STANDING-BACKLOG-001` - WI-4927 is the governing backlog item.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - stuck workers waste CPU/RAM and block re-dispatch; detection must be low-noise.

## Owner Decisions / Input

No new owner decision is required by this implementation report. Implementation authority carries forward from `bridge/gtkb-wi4927-stuck-headless-worker-reap-001.md` and GO verdict `bridge/gtkb-wi4927-stuck-headless-worker-reap-002.md`.

## Prior Deliberations

- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626`
- `DELIB-20266104`
- `DELIB-20266203`
- `bridge/gtkb-wi4857-reap-orphaned-dispatched-workers-004.md`
- `bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-003.md`
- `bridge/gtkb-wi4927-stuck-headless-worker-reap-001.md`
- `bridge/gtkb-wi4927-stuck-headless-worker-reap-002.md`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4927-stuck-headless-worker-reap --format markdown --preview-lines 220` showed latest `GO` at `bridge/gtkb-wi4927-stuck-headless-worker-reap-002.md`. `python scripts\bridge_claim_cli.py extend gtkb-wi4927-stuck-headless-worker-reap --session-id $env:CODEX_THREAD_ID` extended the active Prime Builder implementation claim through `2026-06-30T02:22:48Z`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / implementation-start gate | `python scripts\implementation_authorization.py validate --target <target>` returned `"authorized": true` for each WI-4927 target: `scripts/dispatcher_runtime.py`, `scripts/cursor_harness.py`, `scripts/ops/storm_watchdog_reap.py`, `scripts/ops/harness_storm_watchdog.ps1`, `platform_tests/scripts/test_storm_watchdog_reap.py`, `platform_tests/scripts/test_harness_storm_watchdog.py`, and `platform_tests/scripts/test_cursor_harness.py`. |
| WI-4927 detect desktop-hosted orphan | `python -m pytest platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py platform_tests\scripts\test_cursor_harness.py -q --tb=short` passed `52` tests. Covered Cursor provenance recording, `cursor-agent` process candidate visibility, and provenanced cursor-agent orphan reap. |
| WI-4927 reap stuck dispatcher wrappers | Same pytest command passed wrapper tests for `live_dispatch_run_within_lifetime`, `descendant_of_lifetime_protected_dispatch`, and `over_lifetime_straggler`. |
| WI-4828 safety boundary | Same pytest command passed tests proving interactive/non-dispatch Cursor runs do not record provenance and unattributed orphan helpers remain untouched. |
| `GOV-17` automation script quality | `python -m ruff check scripts\ops\storm_watchdog_reap.py scripts\cursor_harness.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py platform_tests\scripts\test_cursor_harness.py` returned `All checks passed!`. |
| Formatting | `python -m ruff format --check scripts\ops\storm_watchdog_reap.py scripts\cursor_harness.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py platform_tests\scripts\test_cursor_harness.py` returned `5 files already formatted`. |
| Runtime syntax | `python -m py_compile scripts\ops\storm_watchdog_reap.py scripts\cursor_harness.py; <PowerShell scriptblock parse>` returned `py_compile and PowerShell syntax OK`. |
| Scoped whitespace | `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check -- <WI-4927 files>` exited `0`. Git emitted CRLF conversion warnings for tracked LF files only; no whitespace errors remained under the repo's CRLF-aware check. |
| Dispatch health observation | `gt bridge dispatch health --json` currently reports `WARN`, not `PASS`, due to residual OpenRouter harness F state: `loyal-opposition:F last_result=unchanged with pending_count=1` and older `latest_run=2026-06-30T01-06-42Z-loyal-opposition-F-f9d182 failure_class=subprocess_execution_failed exit_code=1`. Runtime classifications show `live_inflight_dispatch_count: 0` for selected recipients, so this WI-4927 worker-leak fix is not the remaining health blocker. |

## Commands Run

```text
python .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4927-stuck-headless-worker-reap --format markdown --preview-lines 220
python scripts\bridge_claim_cli.py extend gtkb-wi4927-stuck-headless-worker-reap --session-id $env:CODEX_THREAD_ID
python scripts\implementation_authorization.py validate --target <each WI-4927 target>
python -m pytest platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py platform_tests\scripts\test_cursor_harness.py -q --tb=short
python -m ruff check scripts\ops\storm_watchdog_reap.py scripts\cursor_harness.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py platform_tests\scripts\test_cursor_harness.py
python -m ruff format --check scripts\ops\storm_watchdog_reap.py scripts\cursor_harness.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py platform_tests\scripts\test_cursor_harness.py
python -m py_compile scripts\ops\storm_watchdog_reap.py scripts\cursor_harness.py
PowerShell scriptblock parse for scripts\ops\harness_storm_watchdog.ps1
git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check -- <WI-4927 files>
gt bridge dispatch health --json
```

## Observed Results

- Focused regression bundle: `52 passed in 0.66s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `5 files already formatted`.
- Python compile and PowerShell syntax: `py_compile and PowerShell syntax OK`.
- Scoped CRLF-aware diff check: exit `0`.
- Dispatcher health after implementation: `WARN` remains because of OpenRouter F residual state, not because of live stuck worker count.

## Files Changed

- `scripts/cursor_harness.py`
- `scripts/ops/storm_watchdog_reap.py`
- `scripts/ops/harness_storm_watchdog.ps1`
- `platform_tests/scripts/test_cursor_harness.py`
- `platform_tests/scripts/test_storm_watchdog_reap.py`
- `platform_tests/scripts/test_harness_storm_watchdog.py`

`scripts/dispatcher_runtime.py` was authorized by the GO and validated by the implementation-start gate, but no code change was required there: the existing dispatch health status already exposes `live_inflight_dispatch_count`, and the observed post-implementation runtime classifications report `0` live in-flight dispatches for selected recipients.

## Acceptance Criteria Status

- [x] Inventory/detect current daemon-owned worker shapes: collector now handles direct harness Python, `pythonw.exe run_with_status.py` wrappers, Codex exec wrappers, and project-bound Cursor agent processes.
- [x] Detect stuck desktop-hosted Cursor agent children: Cursor shim records newly-created GT-KB workspace agent processes during dispatcher-controlled runs, and the watchdog includes them as candidates.
- [x] Reap safely with provenance gating: provenanced `cursor-agent` orphans are reapable only when the recorded dispatched root PID is no longer alive and the PID/create-time match holds.
- [x] Preserve interactive-session safety: unprovenanced Cursor agents and non-dispatch interactive runs are not reaped or recorded.
- [x] Test Cursor orphan path and non-Cursor wrapper path: focused tests cover both.

## Risk And Rollback

Residual release-health risk remains in OpenRouter harness F (`subprocess_execution_failed`, pending unchanged). That is outside the WI-4927 stuck-worker leak fix and should be handled as the next dispatcher release-health item.

Rollback is a single scoped revert of the six files listed above. Reverting restores the prior watchdog behavior; it also removes Cursor agent orphan provenance and the new wrapper lifetime protection/reap tests.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy WI-4927, otherwise return NO-GO with specific findings.
