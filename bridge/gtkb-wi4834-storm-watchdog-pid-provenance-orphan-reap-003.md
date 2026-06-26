NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 130bf9ae-15f0-4373-a7b5-9286568dbc97
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap — Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap
Version: 003

Responds-To: bridge/gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap-002.md (GO)
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4834
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Recommended commit type: fix

## Implementation Report

Implemented per the `-002` GO ("Implement per `-001`") within the authorized `target_paths`. Changes are staged in the working tree (uncommitted) for Loyal Opposition inspection; per the protocol the VERIFIED finalization helper creates the commit with the verified paths plus the verdict.

Verified paths (for the finalization helper `--include`):
- `scripts/ops/storm_watchdog_reap.py`
- `scripts/ops/harness_storm_watchdog.ps1`
- `platform_tests/scripts/test_storm_watchdog_reap.py`

## Files Changed

- `scripts/ops/storm_watchdog_reap.py`:
  - New frozen `ProvenanceRecord(pid, create_time_epoch, dispatch_root_pid)` dataclass.
  - `decide_reap(..., provenance: list[ProvenanceRecord] | None = None)`: after the existing in-scope pass, a process NOT in scope (no live dispatched root in its component) whose `(pid, create_time_epoch)` matches a provenance record with a dead `dispatch_root_pid` (not in the live process set) and past startup grace is reaped with reason `orphan_dead_dispatched_root`. Unmatched processes (interactive sessions are never recorded) are left untouched; a live recorded root defers to the unchanged in-scope path; cold-start grace is honored. The pure-function contract is preserved (provenance is an input).
  - `read_provenance(dir)` + `update_provenance(dir, processes, prior)` glue: fail-soft ledger read; the update records current dispatched-component members tagged with their dispatched root pid, carries forward prior records whose pid is still alive (so a just-died root's descendants stay attributable for the next tick), prunes dead pids, and writes via direct overwrite (not `os.replace`, since the root may be on a cloud-synced volume; torn reads are handled by the fail-soft parse).
  - `main`: new `--provenance-dir` (default `.gtkb-state/ops/dispatch-provenance`, resolved under `--project-root`); reads provenance before deciding, passes it to `decide_reap`, and refreshes the ledger after.
- `scripts/ops/harness_storm_watchdog.ps1`: the decider invocation passes `--provenance-dir '.gtkb-state/ops/dispatch-provenance'` (one-token addition; the decider self-creates the dir). No change to the gather, fail-safe, or kill execution.
- `platform_tests/scripts/test_storm_watchdog_reap.py`: `ProvenanceRecord` import, a `_prov` helper, and 5 decider tests.

No change to the lease logic, the existing reasons/protect tiers, the fail-safe (reap-nothing-on-error) contract, or the interactive-safety boundary.

## Specification Links (carried forward from -001)

- `ADR-DISPATCHER-ARCHITECTURE-001` — the watchdog reaper; uncollected dead-root orphans are a reliability gap this closes.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` — only provenance-recorded dispatched pids are reapable; interactive sessions are never recorded; no kill-switch asserted.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `DCL-DISPATCH-ENVELOPE-RULES-001` — dispatch-service reliability + lifecycle.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4834.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (reap dead-root orphans) | `test_decide_reap_reaps_provenance_attributed_dead_root_orphan` | PASS |
| SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (never reap interactive/unattributed) | `test_decide_reap_leaves_unattributed_orphan_untouched` | PASS |
| pid-reuse guard | `test_decide_reap_provenance_requires_create_time_match` | PASS |
| live-root path unchanged | `test_decide_reap_live_dispatched_root_unchanged_with_provenance` | PASS |
| cold-start grace honored | `test_decide_reap_provenance_orphan_within_grace_protected` | PASS |
| no-regression (existing decider tiers incl. `test_orphaned_helper_family_without_dispatched_root_ignored`) | existing 10 tests | PASS |

## Verification Evidence (commands + observed results)

- `python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=short` → **15 passed** (5 new + 10 existing; the existing dead-root-orphan-ignored test still passes because no-provenance leaves orphans untouched).
- `python -m ruff check scripts/ops/storm_watchdog_reap.py platform_tests/scripts/test_storm_watchdog_reap.py` → **All checks passed**.
- `python -m ruff format --check` (same two `.py` files) → **2 files already formatted**.
- `.ps1` parse smoke (`[System.Management.Automation.Language.Parser]::ParseFile`) → **0 errors**.
- End-to-end glue smoke (`main` with a seeded provenance ledger attributing orphan pid 801 to dead root 800): decision `{"reap": [801], "reasons": {"801": "orphan_dead_dispatched_root"}}`; the ledger carried the still-alive pid forward → **OK** (proves `read_provenance` + `decide_reap` + `update_provenance` integrate).

## Prior Deliberations

- `DELIB-20266104` — owner authorization of the WI-4828 surgical storm-watchdog liveness slice this extends; names this precise-attribution follow-on.
- `DELIB-20266135` — WI-4818 GO listed pid-provenance precise orphan attribution as the out-of-scope follow-on (this WI).
- `DELIB-20266137` — owner authorization for this dispatcher-reliability drive.
- `bridge/gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap-002.md` (Cursor LO GO) — the verdict this report responds to.

## Owner Decisions / Input

- Authorized by `DELIB-20266137` (owner AUQ this session, 2026-06-26); `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26` covers WI-4834. No further owner decision is required: the change preserves the interactive-session safety boundary (only provenance-recorded dispatched pids are reapable) and asserts no kill-switch.

## Requirement Sufficiency

Existing requirements sufficient (carried forward from `-001`). No new or revised requirement was needed.

## Risk / Rollback

- Risk: low-moderate, mitigated. New reaping is gated on a precise `(pid, create_time)` provenance match to a dead dispatched root, so it cannot reach an interactive session (never recorded) or a live-root family (unchanged in-scope path). The ledger is fail-soft (missing/corrupt → no new reaping) and self-pruning; pid reuse is guarded by the create-time match and dead-pid pruning.
- Rollback: revert the decider `provenance` param + `orphan_dead_dispatched_root` branch, the `ProvenanceRecord` dataclass, the `read_provenance`/`update_provenance` glue + `main` wiring, the `.ps1` `--provenance-dir` pass-through, and the 5 tests. Prior behavior (dead-root orphans left for the OS) returns. No schema change; append-only KB untouched.

## Recommended Commit Type

`fix:` — closes the dead-root orphan-reap gap in the storm-watchdog (orphaned helper families accumulated uncollected). Adds a bounded, self-pruning provenance ledger; no change to the interactive-safety boundary and no new owner-facing capability.
