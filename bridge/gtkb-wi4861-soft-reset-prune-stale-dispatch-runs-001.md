NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d5a77c21-caee-404a-8fb3-6629ba276960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-wi4861-soft-reset-prune-stale-dispatch-runs — Soft reset prunes stale/orphaned dispatch-runs records so the live-worker count is accurate

Document: gtkb-wi4861-soft-reset-prune-stale-dispatch-runs
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4861
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESIDUE-CLEANUP-2026-06-27
Recommended commit type: fix

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`gt bridge dispatch reset --soft` (→ `bridge_dispatch_reset.soft_reset`) clears dispatch-state recipients, quiesce records, reset guards, lease locks, and the provenance ledger, but it never touches the `dispatch-runs/` sidecar directory. The live-worker count (`_count_live_dispatched_processes`) derives from `<dispatch_id>.pid` sidecars; dead-PID sidecars that were never pruned linger, so a soft reset that "cleared 18 recipient and 42 quiesce records" still reported "Live workers 29→30" (S485). Stale live records misreport dispatcher load and, with the per-cycle Loyal Opposition ceiling of 1, can spuriously saturate the LO lane and block legitimate LO dispatch.

This proposal extends `soft_reset` to prune **stale/orphaned** dispatch-runs sidecars — those whose worker has exited (`<dispatch_id>.exit_code` present, non-empty) or whose PID is no longer alive — while **preserving genuinely-live workers** (PID alive, no exit_code). Soft reset must not kill live work; it only removes dead records so the live count reflects reality.

### Behavior change (precise)

In `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`:

- Add module constant `DISPATCH_RUNS_DIR_NAME = "dispatch-runs"`.
- Add a local cross-platform `_dispatch_run_pid_alive(pid: int) -> bool` (prefer `psutil.pid_exists`; fall back to Win32 `OpenProcess`/`GetExitCodeProcess` on Windows and `os.kill(pid, 0)` on POSIX; fail-closed to not-alive on parse/probe error). It is defined locally rather than imported from `cross_harness_bridge_trigger` to preserve the module dependency direction (the trigger imports from this module, not vice versa).
- Add `_prune_stale_dispatch_runs(dispatch_dir: Path, *, dry_run: bool) -> int`: for each `dispatch_dir / DISPATCH_RUNS_DIR_NAME / *.pid`, compute `exited = <id>.exit_code exists and size > 0`; read the PID; if `exited` OR not `_dispatch_run_pid_alive(pid)` (or the PID is unparseable), remove the full `<dispatch_id>.*` sidecar set (`.pid`, `.exit_code`, `.stdout.log`, `.stderr.log`, `.prompt.txt`, `.input.json`, `.stdin.log`) via the existing `_remove_path`; count one prune. A live worker (PID alive, no exit_code) is left untouched. Best-effort; never raises. Honors `dry_run` (counts without removing).
- Add `stale_dispatch_runs_pruned: int = 0` to `ResetResult` (+ include in its `to_dict()` / serialization).
- In `soft_reset`, call `_prune_stale_dispatch_runs` for each `dispatch_dir` and accumulate into `result.stale_dispatch_runs_pruned`, appending a detail line when non-zero. `hard_reset` inherits this via its `soft_reset` call.

No change to dispatch selection, lease serialization, recipient/quiesce clearing, or the `_count_live_dispatched_processes` counting path (which keeps its own inline prune for the steady-state count).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next append-only numbered bridge file.
- `GOV-17` — Automation script modification approval gate; modifies dispatcher automation; owner-authorized (DELIB-20266268, PAUTH cited).
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture; accurate live-worker accounting is part of dispatch operability.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — cites governing specs; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4861 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — prune behavior maps to derived tests.
- `GOV-STANDING-BACKLOG-001` — WI-4861 is an authorized standing-backlog item under the active project.

## Prior Deliberations

- `DELIB-20266268` — owner AUQ (S20260627): "Clear daemon residue WIs first"; authorizes WI-4861 + WI-4859.
- `DELIB-20266203` — autonomous-loop plan; accurate dispatcher accounting supports the PHASE-Y go-live.
- WI-4805 (reset-recipient stale-PID reap), WI-4857 (`reap_inflight_dispatched_workers`) — related dispatch-runs lifecycle work; this proposal adds the soft-reset prune that those did not cover. WI-4725 / WI-4733 referenced by the WI.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESIDUE-CLEANUP-2026-06-27` (active; includes WI-4859 + WI-4861 + GOV-17 + ADR-DISPATCHER-ARCHITECTURE-001; cites `DELIB-20266268`). The owner selected "Clear daemon residue WIs first" via AskUserQuestion (S20260627). No additional owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement (WI-4861 acceptance) is that a soft reset leave the live-worker count accurate by reaping stale/orphaned dispatch-runs records. DELIB-20266268 authorizes the fix. No new requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| WI-4861: dead-PID sidecar is pruned | `test_soft_reset_prunes_dead_pid_dispatch_run` (new) | a `<id>.pid` with a non-live PID and no exit_code → after `soft_reset`, the sidecar is gone and `result.stale_dispatch_runs_pruned == 1`. |
| WI-4861: exited worker sidecar is pruned | `test_soft_reset_prunes_exited_dispatch_run` (new) | a `<id>.pid` (any PID) plus a non-empty `<id>.exit_code` → pruned; count 1. |
| WI-4861: live worker is preserved | `test_soft_reset_preserves_live_dispatch_run` (new) | a `<id>.pid` = `os.getpid()` with no exit_code → NOT pruned; `result.stale_dispatch_runs_pruned == 0`; sidecar remains. |
| WI-4861: dry-run counts without removing | `test_soft_reset_dry_run_does_not_remove` (new) | `dry_run=True` with a dead-PID sidecar → count reflects the prune but the file remains on disk. |
| Non-regression | existing reset behavior | recipients/quiesce/guards/leases clearing unchanged. |

Commands (pre-report): targeted `pytest` over the new test module via the repo venv; `ruff check` AND `ruff format --check` on the changed files. PID liveness is simulated deterministically (`os.getpid()` for alive; a never-allocated PID for dead); the dispatch-runs dir is a tmp fixture (no live dispatch substrate touched).

## Risk / Rollback

- **Risk:** pruning a sidecar for a worker that just exited but whose outcome the monitor hasn't yet recorded could lose post-mortem logs. Mitigated: prune fires only on a soft/hard reset (an explicit operator action to clear transient state), and only for exited/dead workers; live workers are preserved. The steady-state count path is unchanged.
- **Risk:** mis-detecting a live PID as dead would prune a live worker's record. Mitigated: `_dispatch_run_pid_alive` fails closed to not-alive only on probe error; the test asserts a live `os.getpid()` is preserved.
- **Rollback:** single-commit revert removes the prune helper, the `ResetResult` field, and the `soft_reset` call. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Recommended Commit Type

`fix` — repairs inaccurate live-worker accounting after soft reset (stale dispatch-runs records). No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
