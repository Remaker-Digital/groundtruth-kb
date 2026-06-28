NEW

# GT-KB Bridge Implementation Report - gtkb-wi4894-storm-watchdog-pythonw-output-repair - 003

bridge_kind: implementation_report
Document: gtkb-wi4894-storm-watchdog-pythonw-output-repair
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-002.md
Approved proposal: bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4894-REAPER-OUTPUT
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4894
Implementation branch: codex/formal-release-main-20260627
Implementation worktree: E:\GT-KB\.tmp\formal-release-main-20260627
Implementation commit: pending post-VERIFIED release commit
Recommended commit type: fix:
Date: 2026-06-28 UTC
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop; release branch formalization

## Implementation Claim

Implemented the WI-4894 storm-watchdog reaper output repair in the clean formal-release worktree.

The reaper decider now accepts `--output-file` and writes the same decision JSON schema to that file when requested. The normal stdout CLI behavior is unchanged when `--output-file` is omitted. The Windows watchdog now invokes the decider with `pythonw.exe` through `Start-Process -Wait -PassThru -WindowStyle Hidden`, reads the decision JSON from a short-lived per-run file under `.gtkb-state/ops`, then removes that file after reading.

This preserves the WI-4896 no-visible-console behavior without depending on stdout capture from the GUI-subsystem interpreter. It also preserves the existing fail-safe behavior: if the decider exits nonzero, the output file is missing/empty, or JSON parsing throws, the watchdog reaps nothing and still has no raw-count fallback or automatic kill-switch assertion.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected script/test implementation proceeded only after the current bridge thread reached GO and a matching work-intent claim plus implementation-start packet were created.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation stayed within the proposal's cited governing surfaces and four target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the report carries the approved project, work item, and project authorization metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps each linked governing surface to executed verification evidence.
- `GOV-STANDING-BACKLOG-001` - `WI-4894` remains the active backlog authority for this defect.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the repair sustains the dispatcher reliability envelope by making watchdog corpse-reaping functional again.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the watchdog can again make an observable parseable reap decision instead of repeatedly fail-safing on empty output.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - the repair only changes the decider transport path and preserves the dispatch-worker decision schema.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` - the watchdog still does not auto-assert the kill switch and does not fall back to raw process-count killing.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - the scheduled Windows watchdog uses `pythonw.exe` and hidden `Start-Process` invocation, avoiding visible console windows.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed implementation paths remain inside the GT-KB root; no Agent Red or external checkout is treated as authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the work item, proposal, GO, implementation evidence, and verification request are preserved as bridge artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the release-blocking defect was fixed through a bounded work item and bridge chain rather than scratch state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the release-blocking watchdog finding was promoted into formal WI/bridge implementation evidence.

## Owner Decisions / Input

No new owner decision was required. The work is covered by `DELIB-20266276` through `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4894-REAPER-OUTPUT` and by the GO verdict at `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-002.md`.

## Prior Deliberations

- `DELIB-20266104` - owner authorized the surgical storm-watchdog liveness-awareness slice.
- `DELIB-20266079` - WI-4780 verification that the watchdog must not auto-assert the global kill switch.
- `DELIB-20266135` - owner directed the storm-watchdog watched-set repair for Cursor coverage.
- `DELIB-20266276` - owner scope-lock for daemon/dispatcher resilience, carried by the active PAUTH.
- `DELIB-20266297` - WI-4896 no-console direction; this repair preserves it by avoiding stdout capture from `pythonw.exe`.
- `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge_claim_cli.py claim` succeeded for this slug under session `019f09c9-2db0-7b00-a337-40f998b07e56`; `implementation_authorization.py begin` produced packet `sha256:df6fff0f6034ba6106dec357e22d2cc959673cb53ab6f68d4c35e6fdb8a07a0b`; `implementation_authorization.py validate` authorized exactly the four target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The implementation diff is limited to `scripts/ops/storm_watchdog_reap.py`, `scripts/ops/harness_storm_watchdog.ps1`, `platform_tests/scripts/test_storm_watchdog_reap.py`, and `platform_tests/scripts/test_harness_storm_watchdog.py`; these are the four GO-authorized target paths. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries `PROJECT-GTKB-DISPATCHER-RELIABILITY`, `WI-4894`, and `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4894-REAPER-OUTPUT`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps linked specifications to executed evidence; focused pytest, ruff, format, and manual `pythonw.exe` transport checks all passed. |
| `GOV-STANDING-BACKLOG-001` | `gt bridge threads --wi WI-4894` showed this thread as the current GO bridge thread for `WI-4894` before implementation. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Focused watchdog tests passed: `25 passed`; manual `pythonw.exe` transport produced parseable reap/protect/reasons JSON instead of empty output. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_main_writes_decision_to_output_file_without_stdout` covers the output-file transport; manual Start-Process smoke test with `pythonw.exe` returned `exit=0` and emitted a decision file. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | The decision schema remains `{"reap": [...], "protect": [...], "reasons": {...}}`; both stdout and output-file tests parse that schema. |
| `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` | Existing `test_watchdog_does_not_auto_assert_kill_switch` still passes; the script still logs fail-safe and never adds a raw-count fallback. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Added `test_watchdog_uses_headless_python_file_transport_for_reap_decider`; it asserts `pythonw.exe`, `Start-Process -Wait -PassThru -WindowStyle Hidden`, `--output-file`, and no stdout capture path. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All commands ran from `E:\GT-KB\.tmp\formal-release-main-20260627` and referenced only GT-KB-root paths. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The release worktree now carries the proposal and GO bridge artifacts alongside the implementation patch; this report requests LO verification as the durable review artifact. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The repair is tied to `WI-4894` and the bridge chain instead of untracked scratch notes. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The release-blocking watchdog failure was formalized as `WI-4894` and advanced through proposal, GO, implementation report, and requested verification. |

## Commands Run

- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4894-storm-watchdog-pythonw-output-repair --session-id 019f09c9-2db0-7b00-a337-40f998b07e56 --ttl-seconds 7200 --project-root E:\GT-KB`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py --project-root E:\GT-KB begin --bridge-id gtkb-wi4894-storm-watchdog-pythonw-output-repair --session-id 019f09c9-2db0-7b00-a337-40f998b07e56`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py --project-root E:\GT-KB validate --target scripts/ops/storm_watchdog_reap.py --target scripts/ops/harness_storm_watchdog.ps1 --target platform_tests/scripts/test_storm_watchdog_reap.py --target platform_tests/scripts/test_harness_storm_watchdog.py`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py -q --tb=short`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\ops\storm_watchdog_reap.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\ops\storm_watchdog_reap.py platform_tests\scripts\test_storm_watchdog_reap.py platform_tests\scripts\test_harness_storm_watchdog.py`
- `Start-Process -FilePath E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe -ArgumentList @('scripts\ops\storm_watchdog_reap.py','--now',<epoch>,'--project-root','E:\GT-KB','--provenance-dir','.gtkb-state/ops/dispatch-provenance','--processes-file','E:\GT-KB\.gtkb-state\ops\storm-watchdog-candidates.json','--output-file',<release-worktree-temp-decision-file>) -Wait -PassThru -WindowStyle Hidden`

## Observed Results

- Claim acquired: `claim_kind=go_implementation`, `project_id=PROJECT-GTKB-DISPATCHER-RELIABILITY`, `ttl_expires_at=2026-06-28T01:10:25Z`.
- Implementation-start packet created: `latest_status=GO`, packet hash `sha256:df6fff0f6034ba6106dec357e22d2cc959673cb53ab6f68d4c35e6fdb8a07a0b`, target globs exactly the four authorized paths.
- Target validation returned `authorized: true` for the four target paths.
- Pytest result: `25 passed in 0.30s`.
- Ruff result: `All checks passed!`.
- Ruff format result: `3 files already formatted`.
- Manual `pythonw.exe` Start-Process result: `exit=0`; output file contained parseable JSON with the required top-level keys `protect`, `reap`, and `reasons`.

## Files Changed

- `scripts/ops/storm_watchdog_reap.py`
- `scripts/ops/harness_storm_watchdog.ps1`
- `platform_tests/scripts/test_storm_watchdog_reap.py`
- `platform_tests/scripts/test_harness_storm_watchdog.py`

## Acceptance Criteria Status

- [x] Add a `storm_watchdog_reap.py --output-file` transport that writes the same decision schema to a file for `pythonw.exe` callers.
- [x] Preserve the normal stdout CLI path when `--output-file` is omitted.
- [x] Update the PowerShell watchdog to use `pythonw.exe` without relying on stdout capture.
- [x] Wait for the decider process and use its exit code before reading the output file.
- [x] Remove the short-lived decision file after reading to avoid persistent scratch clutter.
- [x] Preserve fail-safe/no-raw-count-fallback/no-auto-kill-switch semantics.
- [x] Add focused regression coverage for both the Python output-file path and the PowerShell no-console file transport.

## Risk And Rollback

Residual risk is limited to the Windows scheduled-task invocation boundary. The direct Start-Process smoke test verified the same `pythonw.exe --output-file` transport used by the script, but it did not run the full scheduled task loop. Rollback is a single revert of the implementation commit; it restores the previous fail-safe/no-reap behavior.

## Loyal Opposition Asks

1. Verify that the implementation stays within the four GO-authorized paths.
2. Verify that the output-file transport fixes the `pythonw.exe` empty-output failure without reintroducing visible console windows.
3. Verify that fail-safe/no raw-count fallback/no auto-kill-switch behavior remains intact.
4. Return VERIFIED if the report and implementation satisfy the approved proposal; otherwise return NO-GO with concrete findings.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
