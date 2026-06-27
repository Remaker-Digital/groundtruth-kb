NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-27T04-22-55Z-prime-builder-B-4118e2
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: Claude Code headless dispatch; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-wi4857-reap-orphaned-dispatched-workers — Post-Implementation Report

Document: gtkb-wi4857-reap-orphaned-dispatched-workers
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4857
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4857-REAP-ORPHANED-WORKERS
Recommended commit type: fix

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

---

## Summary

Implementation complete for WI-4857. The daemon now reaps orphaned and in-flight dispatched workers at two lifecycle points, preventing worker leakage when the daemon crashes or is stopped while workers are running.

### Changes made

**`scripts/cross_harness_bridge_trigger.py`** — new public function `reap_inflight_dispatched_workers(runs_dir: Path) -> int`:
- Enumerates `runs_dir/*.pid` sidecars
- A worker is reaped iff its `.pid` exists with a parseable PID, its `.exit_code` sidecar is absent/empty, and the PID is alive
- For each matched worker: `_terminate_pid_tree(pid)`, then writes `"124\n"` to the `.exit_code` sidecar so the dispatch monitor classifies the outcome as a killed worker (not `corrupt_output`)
- Workers with an existing exit_code or a dead PID are skipped untouched
- File errors never raise (best-effort)
- Returns the count of workers actually reaped

**`scripts/gtkb_dispatcher_daemon.py`** — new private function `_reap_dispatched_workers(project_root: Path) -> int`:
- Delegates to `trigger.reap_inflight_dispatched_workers(runs_dir)` after resolving `runs_dir = _bridge_poller_state_dir(project_root) / trigger.DISPATCH_RUNS_SUBDIR`
- Loads the trigger via the existing `_load_trigger_module()` pattern
- Wraps the call to never raise so reap failure cannot break daemon startup or shutdown
- Returns the count of workers reaped (0 on any failure)

**`scripts/gtkb_dispatcher_daemon.py` — `run_loop` update** (two call sites added):
1. **Startup reclaim** (after `acquire_daemon_lock`): holding the lock proves no prior daemon is alive, so any live dispatched worker at that point is an orphan; calling `_reap_dispatched_workers(project_root)` before writing `daemon.pid` handles the abrupt-crash case that the finally block cannot reach.
2. **Graceful-shutdown reap** (first line of `finally` block): calling `_reap_dispatched_workers(project_root)` before `(state_dir / PID_FILENAME).unlink()` and `release_daemon_lock` ensures in-flight workers are terminated before the daemon releases its ownership marker.

**`platform_tests/scripts/test_gtkb_dispatcher_daemon.py`** — four new spec-derived tests:
- `test_reap_inflight_terminates_live_worker` — spawns a real sleeper, writes a `.pid` sidecar with no `.exit_code`, calls the helper, asserts reaped=1 and exit_code="124", verifies the process is dead
- `test_reap_inflight_skips_completed_worker` — live sleeper with a pre-populated `.exit_code`, asserts reaped=0 and process still alive
- `test_reap_inflight_skips_dead_pid` — dead PID sidecar with no exit_code, asserts reaped=0 and no exit_code written
- `test_daemon_reap_helper_reaps_orphan` — exercises the daemon-level `_reap_dispatched_workers` wrapper end-to-end via the bridge-poller runs-dir path

### No change to
- Dispatch selection logic
- Worker spawning (`_spawn_harness`)
- Concurrency cap or live-count accounting
- KB mutation (none)

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as append-only numbered bridge file
- `GOV-17` — Automation script modification approval gate; authorized via PAUTH and DELIB-20266203
- `ADR-DISPATCHER-ARCHITECTURE-001` — daemon worker-lifecycle ownership is part of the operability contract; this fix closes the orphan-leakage gap
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing specs cited and carried forward
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4857 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — four spec-derived tests executed; mapping below
- `GOV-STANDING-BACKLOG-001` — WI-4857 is an authorized standing-backlog item

## Prior Deliberations

- `DELIB-20266203` — owner approved the full Phase X daemon fix-chain (Q2); WI-4857 is step X5
- WI-4855 — daemon process-lifecycle hardening (startup-reclaim invariant depends on the lock semantics established there)
- WI-4805 / WI-4834 — existing storm-watchdog and reset-time reap of stale PIDs; this adds the daemon-lifecycle reap, reusing the same sidecar contract

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| WI-4857: live worker without exit_code is terminated + recorded | `test_reap_inflight_terminates_live_worker` | PASS |
| WI-4857: completed worker (exit_code present) is not touched | `test_reap_inflight_skips_completed_worker` | PASS |
| WI-4857: dead PID is skipped safely | `test_reap_inflight_skips_dead_pid` | PASS |
| WI-4857: daemon startup reaps an orphan worker | `test_daemon_reap_helper_reaps_orphan` | PASS |
| Non-regression — existing daemon suite | full `test_gtkb_dispatcher_daemon.py` | 30/30 PASS |

## Test Execution Evidence

```
platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_reap_inflight_terminates_live_worker PASSED
platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_reap_inflight_skips_completed_worker PASSED
platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_reap_inflight_skips_dead_pid PASSED
platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_daemon_reap_helper_reaps_orphan PASSED

30 passed in 4.50s  (full daemon test suite)
```

## Code Quality Gates

- `ruff check` (lint): 1 pre-existing E402 in `cross_harness_bridge_trigger.py` line 89 (import ordering; present before this change; unrelated to the reap feature). No new lint errors introduced.
- `ruff format --check`: 3 files already formatted — PASS

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement (WI-4857) is that the daemon track dispatched-worker liveness and reap orphaned/timed-out workers, and that daemon shutdown handle in-flight workers. No new requirement needed.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4857-REAP-ORPHANED-WORKERS` (active; includes WI-4857 + GOV-17 + ADR-DISPATCHER-ARCHITECTURE-001; cites `DELIB-20266203`). The owner approved the full Phase X daemon fix-chain (DELIB-20266203 Q2), of which WI-4857 is step X5. No additional owner decision required.

## Recommended Commit Type

`fix` — repairs daemon-death-orphaned / in-flight dispatched-worker leakage by adding a reap helper (additive but corrects a lifecycle defect, not a new capability).

## Applicability Preflight

- packet_hash: `sha256:424cd907a2c3e0aa75245da0e6655aacce47f51f45b86b804a2309115f667d1f`
- bridge_document_name: `gtkb-wi4857-reap-orphaned-dispatched-workers`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi4857-reap-orphaned-dispatched-workers-001.md`
- operative_file: `bridge/gtkb-wi4857-reap-orphaned-dispatched-workers-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
