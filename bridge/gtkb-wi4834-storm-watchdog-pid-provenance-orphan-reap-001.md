NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 130bf9ae-15f0-4373-a7b5-9286568dbc97
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap — add a dispatch-run pid-provenance ledger so orphaned helper families of dead dispatched roots are reaped safely

bridge_kind: prime_proposal
Document: gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4834

target_paths: ["scripts/ops/storm_watchdog_reap.py", "scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_storm_watchdog_reap.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4834 (improvement): the storm-watchdog leaves orphaned helper families of dead dispatched roots uncollected. `storm_watchdog_reap.decide_reap` only acts on process-family components that contain a **live** `dispatched` root (`in_scope_pids`, `storm_watchdog_reap.py:187-191`). When a dispatched worker root dies but leaves leaf helpers (node_repl, codex-command-runner, codex-windows-sandbox, or a child python) that get reparented, those helpers form a component with **no live dispatched root**, so the decider treats them as an "ambiguous orphan family whose dispatched root has already died" and leaves them entirely untouched (the documented trade-off at `storm_watchdog_reap.py:67-71` and `harness_storm_watchdog.ps1:28-34`). They then accumulate until the OS cleans them — exactly the leak WI-4818's GO and the WI-4670 root-cause notes flagged as the follow-on.

This proposal adds a **dispatch-run pid-provenance ledger**: while a dispatched root is alive, the watchdog records its component members' `(pid, create_time_epoch)` tagged with the dispatched root pid. On a later tick where the root is gone, ledger members still alive (matched by `pid` AND `create_time_epoch`, guarding pid-reuse) are *precisely* attributable to that dead dispatched run and become reapable as `orphan_dead_dispatched_root`. Processes with no provenance record — interactive Codex/Cursor sessions are never recorded because they are never in a dispatched component — remain untouched, preserving the existing safety boundary.

## Problem detail (for LO review)

- `storm_watchdog_reap.py:187-191` — `in_scope_pids` = union of components that intersect `dispatched_pids`. A component with no live `dispatched` member is never in scope, so its processes are skipped at `:197-198`.
- `storm_watchdog_reap.py:67-71` / `:181-186` — the documented safety trade-off: orphan families whose dispatched root has died are left for the OS rather than risk reaping an interactive session. WI-4834 is the named follow-on to attribute those orphans precisely.
- The decider is a pure function of `(processes, leases, now, config)` (`:24-28`); the ledger is I/O, so ledger maintenance belongs in the `main` glue (`:275-319`), not in `decide_reap`. The decider gains the ledger contents as a new pure input.
- Safety invariant to preserve: a process is reapable as a dead-root orphan ONLY if it was recorded in provenance while it was in a dispatched component. Interactive sessions are never in a dispatched component, are never recorded, and therefore can never match — so they are never reaped. The `(pid, create_time_epoch)` match (not pid alone) guards against pid reuse re-attributing a fresh interactive pid to a dead run.

## Proposed change

1. `scripts/ops/storm_watchdog_reap.py`:
   - New frozen dataclass `ProvenanceRecord(pid: int, create_time_epoch: float, dispatch_root_pid: int)` — one observed dispatched-component member.
   - `decide_reap(..., provenance: list[ProvenanceRecord] | None = None)`: after the existing in-scope reap/protect pass, evaluate orphan candidates — processes NOT in `in_scope_pids` (no live dispatched root in their component). For each such process whose `(pid, create_time_epoch)` matches a `ProvenanceRecord` whose `dispatch_root_pid` is NOT currently alive (not in `by_pid`) AND whose `age >= startup_grace_seconds`, reap with reason `orphan_dead_dispatched_root`. Non-matching orphan processes stay untouched (neither reaped nor reported). The existing in-scope logic and all current reasons are unchanged; this only adds reaping for precisely-attributed dead-root orphans.
   - `main` glue: add `--provenance-dir` (default `.gtkb-state/ops/dispatch-provenance`, resolved under `--project-root`). Read the ledger into `ProvenanceRecord`s; pass to `decide_reap`. After deciding, UPDATE the ledger atomically: (a) record current dispatched-component members `(pid, create_time_epoch, dispatch_root_pid)`; (b) prune records whose `pid` is no longer alive in the current `processes` (so the ledger self-bounds and a reaped/exited orphan is not re-attributed forever). Ledger read/write tolerate missing/corrupt files (fail-soft, like `read_leases`).
2. `scripts/ops/harness_storm_watchdog.ps1`: pass `--provenance-dir` to the decider invocation (line ~144) and ensure the provenance dir exists (mirrors the `$opsDir` guard). No change to the gather, the fail-safe contract, or the kill execution.
3. `platform_tests/scripts/test_storm_watchdog_reap.py`: decider unit tests for the new path.

No change to the lease logic, the existing reasons, the fail-safe (reap-nothing-on-error) contract, or `harness_storm_watchdog.ps1` gather/kill behavior beyond passing the provenance dir.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture-of-record; the storm-watchdog reaper is part of the dispatch-reliability contract, and uncollected orphans are a reliability gap.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` — the watchdog reaps corpses/stragglers but never auto-asserts the kill-switch; this change keeps that boundary (it only reaps precisely-attributed dead-root orphans, never an interactive session, and never asserts the kill-switch).
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch-service reliability.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — dispatch lifecycle rules.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4834 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266104` — owner authorization of the surgical storm-watchdog liveness-awareness slice (WI-4670 slice 1, WI-4828), which `decide_reap` implements; WI-4834 is the explicit precise-orphan-attribution follow-on noted in that work.
- `DELIB-20266135` — WI-4818 storm-watchdog Cursor-coverage decision; its GO listed pid-provenance precise orphan attribution as out-of-scope follow-on (this WI).
- `DELIB-20266137` — owner authorization for this dispatcher-reliability drive (Fixes-then-Phases); source authority for WI-4834.
- Deliberation search ("storm watchdog pid provenance orphan reap dispatched root precise attribution") surfaced no prior decision on the attribution mechanism itself.

## Owner Decisions / Input

- Authorized by `DELIB-20266137` (owner AUQ this session, 2026-06-26); `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26` covers WI-4834. No further owner decision is required: the change preserves the interactive-session safety boundary (only provenance-recorded dispatched pids are reapable) and asserts no kill-switch. It widens reaping to precisely-attributed dead-root orphans only.
- Topology this session: Claude (B) = Prime Builder; Cursor (E) = Loyal Opposition reviewer.

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` + `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` (corpse/straggler reaping without harming interactive sessions or asserting the kill-switch) fully constrain the change. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (reap dead-root orphans) | `test_decide_reap_reaps_provenance_attributed_dead_root_orphan` (new) | An orphan process (no live dispatched root in its component) past startup grace, matched by `(pid, create_time)` to a provenance record whose `dispatch_root_pid` is dead, is reaped with reason `orphan_dead_dispatched_root`. |
| SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (never reap interactive) | `test_decide_reap_leaves_unattributed_orphan_untouched` (new) | An orphan process with NO provenance record is left untouched (not reaped, not protected) — the interactive-safety boundary holds. |
| pid-reuse guard | `test_decide_reap_provenance_requires_create_time_match` (new) | A provenance record with the same pid but a different `create_time_epoch` does NOT attribute/reap the current process. |
| live-root unchanged | `test_decide_reap_live_dispatched_root_path_unchanged` (new/existing) | When the dispatched root is alive, the existing in-scope behavior and reasons are unchanged (provenance does not alter live-root decisions). |
| No-regression | existing `test_storm_watchdog_reap.py` decider tests pass unchanged; `ruff check` / `ruff format --check` on the changed `.py` files | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=short`; `ruff check` then `ruff format --check` on the changed `.py` files; PowerShell parse smoke on the edited `.ps1`.

## Risk / Rollback

- Risk: low-moderate. The new reaping is gated on a precise `(pid, create_time)` provenance match to a dead dispatched root, so it cannot reach an interactive session (never recorded) or a live-root family (handled by the unchanged in-scope path). The ledger is fail-soft (missing/corrupt → no provenance → no new reaping) and self-pruning. The main residual risk is pid reuse, mitigated by the create-time match and by pruning dead pids each tick.
- Rollback: revert the decider `provenance` param + the `orphan_dead_dispatched_root` branch, the `main` ledger read/write, and the `.ps1` `--provenance-dir` pass-through, plus the new tests. Prior behavior (dead-root orphans left for the OS) returns. No schema change; append-only KB untouched.
- Out of scope: the storm-watchdog dormancy auto-restart and kill-switch auto-clear (WI-4804), the reset-recipient stale-state reap (WI-4805), and any change to the lease registry or the dispatch trigger.

## Recommended Commit Type

`fix:` — closes the dead-root orphan-reap gap in the storm-watchdog (a dispatch-reliability defect: orphaned helper families accumulated uncollected). Adds a bounded provenance ledger; no new owner-facing capability and no change to the interactive-safety boundary.
