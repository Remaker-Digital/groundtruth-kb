NEW
author_identity: Antigravity
author_harness_id: C
author_session_context_id: 614a39b8-62e9-4d87-b019-06e3ae72c456
author_model: gemini-2.5-pro
author_model_version: 2.5
author_model_configuration: interactive owner session, ::init gtkb pb
author_metadata_source: prime-builder session

# GT-KB Bridge Implementation Report - Hard Global Concurrency Cap on Dispatched Headless Harness Processes (WI-4472)

bridge_kind: implementation_report
Document: gtkb-cross-harness-dispatch-concurrency-cap
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-cross-harness-dispatch-concurrency-cap-004.md
Approved proposal: bridge/gtkb-cross-harness-dispatch-concurrency-cap-003.md
Recommended commit type: fix

## Implementation Claim

WI-4472 is implemented within the approved target paths.

`scripts/cross_harness_bridge_trigger.py` now implements a hard global concurrency cap on live dispatched headless harness processes before spawning. 

- Each successful launch in `_spawn_harness` writes a `<dispatch_id>.pid` sidecar to the `dispatch-runs` directory.
- `_pid_alive(pid)` provides cross-platform liveness detection, falling back from `psutil` to `ctypes`/Win32 calls on Windows and `os.kill(pid, 0)` on POSIX, failing closed to `False` on any invalid/malformed PID text.
- `_count_live_dispatched_processes(runs_dir)` checks each sidecar's liveness: a dispatch is live iff its `.exit_code` status file (written by `run_with_status.py` on child exit) is absent/empty AND its PID is alive. It prunes dead or exited sidecars to keep the workspace clean.
- `_spawn_harness` enforces the cap (configured by `GTKB_MAX_LIVE_DISPATCHED_PROCESSES`, default `8`). If `live >= cap`, it logs the event in `dispatch-failures.jsonl` with reason `concurrency_cap_reached` and skips spawning.
- In `run_trigger`, `dry_run` mode was updated to ensure that `dry_run` result reasons (like `dry_run`) are returned instead of triggering actual process spawns, while updating signature state properly to preserve compatibility with existing test suites.

All tests are fully passing (68/68 in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` and 15/15 in `platform_tests/scripts/test_dispatch_concurrency_cap.py`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Primary. The concurrency cap safety valve resides entirely in the dispatch infrastructure subordinate to `bridge/INDEX.md`.
- `GOV-RELIABILITY-FAST-LANE-001` - Standing Reliability Fast-Lane Governance. The implementation conforms to all restrictions of `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (source and test addition only, in-root changes).
- `.claude/rules/bridge-essential.md` - Prevents blind activity-independent loops from exhausting host resources.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` - Integrates cleanly with active-session suppression by providing an independent safety ceiling.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation paths are within `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - All specification linkage requirements are satisfied.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Execution of spec-derived targeted tests.

## Owner Decisions / Input

- Carried forward from the approved proposal: Owner chose WI-4472 ("dispatch-storm root-cause fix") as the next priority.
- Project authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers the implementation via active project membership.
- No new owner decisions are required.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - Owner directive authorizing the creation of the reliability fast-lane standing authorization.
- `DELIB-S324-OM-DELTA-0001-CHOICE` - Citation authority.

## Specification-Derived Verification Plan

| Spec / requirement | Executed verification evidence |
| --- | --- |
| `bridge-essential.md` (concurrency cap) | `test_cap_gate_blocks_dispatch_at_or_over_limit` asserts fail-closed behavior. |
| WI-4472 (process accounting) | `test_count_excludes_exited_and_dead_and_prunes` verifies correct liveness check. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (audit trail) | `test_cap_gate_blocks_dispatch_at_or_over_limit` asserts `dispatch-failures.jsonl` audit entry. |
| `GOV-RELIABILITY-FAST-LANE-001` (fast lane) | Verify target paths are strictly in-root and no restricted mutations occurred. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | execution of `pytest`, `ruff check`, and `ruff format --check`. |

## Commands Run

```powershell
$env:GTKB_NO_CROSS_HARNESS_TRIGGER=$null; python -m pytest platform_tests/scripts/test_dispatch_concurrency_cap.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -vv
python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_concurrency_cap.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_concurrency_cap.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

## Observed Results

- Concurrency cap and trigger tests: 83 tests collected, 83 passed.
- `ruff check`: All checks passed.
- `ruff format --check`: All files formatted.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_dispatch_concurrency_cap.py` (new)
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-005.md` (new)
- `bridge/INDEX.md`

## Acceptance Criteria Status

- [x] `_count_live_dispatched_processes` only counts pending dispatches with a live PID; exited/dead-PID dispatches are pruned and excluded.
- [x] When live count >= cap, `_spawn_harness` skips spawn, returns `concurrency_cap_reached`, and records audit entry.
- [x] Below cap, spawn proceeds normally.
- [x] Cap default is 8; env var overrides it; invalid values fall back to default.
- [x] All tests pass; ruff check and ruff format --check pass on changed files.

## Risk And Rollback

Cap default of 8 avoids throttling normal workflows while preventing incident recurrence. Rollback is a simple git revert of `scripts/cross_harness_bridge_trigger.py` and deletion of `platform_tests/scripts/test_dispatch_concurrency_cap.py`.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO.
