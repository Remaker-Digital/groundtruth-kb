NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d5a77c21-caee-404a-8fb3-6629ba276960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report

# gtkb-wi4861-soft-reset-prune-stale-dispatch-runs — Post-implementation report: soft reset prunes stale dispatch-runs records

Document: gtkb-wi4861-soft-reset-prune-stale-dispatch-runs
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4861
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESIDUE-CLEANUP-2026-06-27
Responds to: bridge/gtkb-wi4861-soft-reset-prune-stale-dispatch-runs-002.md (GO)
Recommended commit type: fix

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented the GO'd (`-002`) soft-reset dispatch-runs prune. `soft_reset` now removes stale/orphaned `dispatch-runs/` sidecars (exited or dead-PID workers) so the live-worker count is accurate after a soft reset, while preserving genuinely-live workers.

## Implemented Changes

`groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`:
- Added module constant `DISPATCH_RUNS_DIR_NAME = "dispatch-runs"`.
- Added `stale_dispatch_runs_pruned: int = 0` to `ResetResult` (and its `to_json_dict()`).
- Added `_dispatch_run_pid_alive(pid)` — local cross-platform liveness probe (psutil → Win32 tasklist / POSIX `os.kill`), fail-closed to not-alive; defined locally to preserve the module dependency direction (the trigger imports from this module, not vice versa).
- Added `_prune_stale_dispatch_runs(dispatch_dir, *, dry_run)` — for each `dispatch-runs/*.pid`, prunes the full `<id>.*` sidecar set when the worker has exited (`<id>.exit_code` present/non-empty) OR the PID is not alive/unparseable; preserves live workers (PID alive, no exit_code); honors `dry_run`; returns the count.
- `soft_reset` calls `_prune_stale_dispatch_runs` per `dispatch_dir`, accumulating `result.stale_dispatch_runs_pruned` and appending a detail line. `hard_reset` inherits this via its `soft_reset` call.

`platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py` (new): 4 spec-derived tests.

Purely additive: no change to recipient/quiesce/guard/lease clearing, dispatch selection, the lease guard, or `_count_live_dispatched_processes`. The new prune returns 0 when no `dispatch-runs/` dir exists.

## Specification Links

Carried forward from `-001`:
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `GOV-17` — Automation script modification approval gate; owner-authorized (DELIB-20266268, PAUTH cited).
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher operability (accurate live-worker accounting).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — specs cited; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4861 + project + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — prune behavior maps to derived tests, executed below.
- `GOV-STANDING-BACKLOG-001` — WI-4861 authorized standing-backlog item.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| WI-4861: dead-PID sidecar pruned | `test_soft_reset_prunes_dead_pid_dispatch_run` | PASS |
| WI-4861: exited worker sidecar pruned | `test_soft_reset_prunes_exited_dispatch_run` | PASS |
| WI-4861: live worker preserved | `test_soft_reset_preserves_live_dispatch_run` | PASS |
| WI-4861: dry-run counts without removing | `test_soft_reset_dry_run_does_not_remove` | PASS |

## Verification Evidence

Repo venv `groundtruth-kb/.venv/Scripts/python.exe`:
- `python -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py -q` → `4 passed in 0.19s`.
- `python -m ruff check` on both changed files → `All checks passed!`.
- `python -m ruff format --check` on both files → `2 files already formatted`.
- PID liveness simulated deterministically (`os.getpid()` for alive; PID 999999 for dead); dispatch-runs dir is a tmp fixture (no live dispatch substrate touched).

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement (WI-4861 acceptance) is that a soft reset leave the live-worker count accurate by reaping stale/orphaned dispatch-runs records. DELIB-20266268 authorizes the fix. No new requirement.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESIDUE-CLEANUP-2026-06-27` (active; includes WI-4859 + WI-4861 + GOV-17 + ADR-DISPATCHER-ARCHITECTURE-001; cites `DELIB-20266268`). The owner selected "Clear daemon residue WIs first" via AskUserQuestion (S20260627). No additional owner decision is required for this report.

## Prior Deliberations

- `DELIB-20266268` — owner AUQ (S20260627): "Clear daemon residue WIs first".
- `DELIB-20266203` — autonomous-loop plan; accurate dispatcher accounting supports PHASE-Y go-live.
- `bridge/gtkb-wi4861-soft-reset-prune-stale-dispatch-runs-001.md` (NEW proposal), `-002.md` (Cursor LO GO). Related WI-4805 / WI-4857 (dispatch-runs lifecycle).

## Risk / Rollback

- Risk: pruning a just-exited worker's logs before the monitor recorded them. Mitigated: prune fires only on an explicit soft/hard reset and only for exited/dead workers; live workers preserved; steady-state count path unchanged.
- Risk: mis-detecting a live PID as dead. Mitigated: `_dispatch_run_pid_alive` fails closed only on probe error; `test_soft_reset_preserves_live_dispatch_run` asserts a live `os.getpid()` is preserved.
- Rollback: single-commit revert removes the helpers, the `ResetResult` field, and the `soft_reset` call. No KB mutation.

## Recommended Commit Type

`fix` — repairs inaccurate live-worker accounting after soft reset. No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
