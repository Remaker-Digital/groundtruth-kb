NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - cross_harness_bridge_trigger.py manual CLI state-only ops collide with hook-fired instances

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-cli-single-instance-lock
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4526

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The manual `--reset-recipient` CLI path in `scripts/cross_harness_bridge_trigger.py` (`main()`, the `if args.reset_recipient:` branch) performs a NON-coordinated, whole-file read-modify-write of `dispatch-state.json`: it calls `_load_dispatch_state()` to read the entire state, mutates a recipient's `failure_count` / `circuit_breaker_tripped`, then calls `_write_dispatch_state()` to atomically rename a full snapshot back. Hook-fired `run_trigger` instances (registered as PostToolUse + Stop hooks in `.claude/settings.json` and `.codex/hooks.json`) concurrently perform their OWN whole-file read-modify-write of the same file with last-writer-wins semantics. A hook-fired instance that loaded state BEFORE the manual reset's write clobbers the reset when it writes its own (stale) snapshot. The sanctioned circuit-breaker reset is therefore silently lost during active sessions, which is what forces the owner into manual `dispatch-state.json` surgery (the WI-4481 concurrent-write hazard the WI calls out). The fix is to give the state-only manual op a safe, non-blocking fast-path that re-reads the freshest snapshot immediately before writing under a short-lived fail-fast guard, so the reset is never clobbered and never wedges.

## Defect / Reproduction

Root cause: `_write_dispatch_state` (per-invocation temp + atomic rename, per `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-003.md`) makes each individual write atomic, but it does NOT serialize a read-modify-write *transaction* across processes. The whole `recipients` map is the unit of serialization, so any concurrent full-state writer that read an older snapshot overwrites a peer's targeted field change on its next rename.

Reproduction (logical, deterministic in a test):
1. Seed `dispatch-state.json` with a recipient (e.g. `loyal-opposition:A`) carrying `failure_count > 0` and `circuit_breaker_tripped: true`.
2. Simulate the interleave: process X (`--reset-recipient loyal-opposition`) loads state; concurrently process Y (a hook-fired `run_trigger`/full-state writer) loads the SAME pre-reset state.
3. X writes its reset snapshot (`failure_count: 0`, `circuit_breaker_tripped: false`).
4. Y writes its snapshot, computed from the pre-reset read it captured in step 2 — restoring `failure_count > 0` / `circuit_breaker_tripped: true`.
5. Observed: the recipient's circuit breaker is back to tripped; the reset was silently lost. Expected: the reset survives because the state-only op re-reads immediately before writing under a fail-fast guard, so it either merges onto Y's fresh snapshot or fails fast (non-zero advisory) without wedging — never producing a silent clobber.

`--diagnose` is already read-only (no state mutation) and lock-free; it is unaffected by the defect and remains lock-free fast-path after the fix. The defect surface is the state-mutating `--reset-recipient` op only.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`. No path outside the GT-KB root is read, written, verified, or required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the dispatch-state circuit-breaker reset is bridge-dispatch infrastructure state; this fix keeps the sanctioned reset operation reliable so bridge dispatch liveness can be restored without out-of-band JSON surgery, preserving bridge-state authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - `dispatch-state.json` is a durable operational record; the fix prevents a concurrent-write race from silently corrupting that record, keeping the artifact consistent with the operator's intended state transition.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification for the change (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan below derives each regression test from a cited spec clause (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform dispatch surface (`scripts/...`) and platform tests; no adopter/application surface is touched and no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4526 is a standing-backlog work item (P2, origin=defect) under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the trigger is invoked from BOTH Claude (`.claude/settings.json`) and Codex (`.codex/hooks.json`) PostToolUse/Stop hooks; the manual-vs-hook concurrency race spans both harnesses, so the fix must hold regardless of which harness fired the concurrent instance (hook-parity relevance).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the corrected state transition remains artifact-backed (the on-disk `dispatch-state.json`) rather than inferred, so the reset's effect is durably observable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the manual state-only op with the concurrent lifecycle writes of the same artifact so they no longer race destructively.

## Prior Deliberations

- `DELIB-20263376` - GO: WI-4396 dispatch suppression routing - same `dispatch-state.json` / `dispatch-failures.jsonl` substrate this fix operates on; establishes the shared-chokepoint discipline for state writes.
- `DELIB-20263188` - WI-4529 Windows subprocess.Popen CREATE_NO_WINDOW fix owner authorization - sibling cross-harness-trigger reliability defect under the same standing reliability authorization.
- `DELIB-20263272` - Loyal Opposition GO Verdict: WI-4480 Dispatch-Starvation Telemetry - prior dispatch-state observability work; informs keeping `--diagnose`/`status` visibility unchanged while only the durable write path is hardened.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-4526 is in scope (P2, pipeline-reliability).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4526 is origin=defect, single-concern, introduces no new public surface and no new/revised spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items, pipeline-repair and P1/P2 first; WI-4526 is a P2 pipeline-reliability defect in that batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing reliability fast-lane direction that PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING operationalizes; authorizes small, single-concern reliability defect fixes to proceed through the bridge protocol under the standing project authorization without a fresh per-item owner approval.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge-dispatch-state authority) and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (durable-artifact consistency) already require that operational bridge-state records remain authoritative and uncorrupted; this fix enforces that contract for the manual state-only reset path by making its read-modify-write safe against concurrent hook-fired writers. No new or revised requirement/specification is introduced — the manual `--reset-recipient` and `--diagnose` CLI surfaces keep their existing flags, semantics, and output; only the durable-write coordination of the reset op changes.

## Proposed Scope

1. In `scripts/cross_harness_bridge_trigger.py`, give the state-mutating manual op (`--reset-recipient`) a safe, non-wedging fast-path:
   - Add a small, non-blocking, fail-fast advisory guard helper using the atomic-exclusive-create technique already proven in-tree (`bridge_lease_registry` / `bridge_dispatch_concurrency` use `os.open(..., O_CREAT | O_EXCL | O_WRONLY)`). The guard is acquired only for the brief reset transaction, has a short staleness TTL so an abandoned guard is reclaimed (mirroring `_acquire_lock` in `single_harness_bridge_dispatcher.py`), and on contention returns immediately (NO blocking wait) so the manual CLI can never wedge behind a hook-fired instance.
   - Within the guard, perform the reset as: re-read `dispatch-state.json` (`_load_dispatch_state`) immediately before mutating, apply the targeted recipient `failure_count` / `circuit_breaker_tripped` reset to the freshest snapshot, then `_write_dispatch_state`. This eliminates the stale-snapshot clobber window (a concurrent writer's snapshot is loaded after the guard re-read, so the reset is not silently lost).
   - On guard contention, print a clear, deterministic operator message (e.g. "another trigger instance is mutating dispatch-state; retry the reset") and exit 0 per the fire-and-forget contract, rather than blocking or wedging. No silent failure.
2. Keep `--diagnose` exactly as-is: it is read-only, takes no guard, and remains a lock-free fast-path (it does not write `dispatch-state.json`). This satisfies the WI's "lock-free fast-path for state-only ops (reset/diagnose)" ask for both ops — diagnose by being read-only, reset by re-reading under a fail-fast guard.
3. Add regression tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (see verification plan) covering the clobber-avoidance interleave, the non-wedging fail-fast contention behavior, and the unchanged read-only `--diagnose` path.

Out of scope (would require a new requirement and is explicitly excluded from this fast-lane defect fix): wiring `bridge_dispatch_concurrency.py` into the dispatch path; any change to hook-fired `run_trigger` dispatch behavior; any new CLI flag; any change to `dispatch-state.json` schema.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (sanctioned bridge-state reset must remain authoritative) | `test_reset_recipient_survives_concurrent_full_state_write` | After a `--reset-recipient` op, a hook-fired full-state write that loaded a pre-reset snapshot does NOT restore the tripped circuit breaker; the recipient's `failure_count == 0` and `circuit_breaker_tripped is False` persist in `dispatch-state.json`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (manual state-only op must not wedge) | `test_reset_recipient_fails_fast_when_guard_held` | When the advisory reset guard is already held by a fresh peer, `--reset-recipient` returns immediately (exit 0) with a clear contention message and does NOT block / wedge (bounded wall-clock, no busy-wait). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (diagnose stays a lock-free read-only fast-path) | `test_diagnose_is_read_only_and_lock_free` | `--diagnose` neither creates the reset guard file nor mutates `dispatch-state.json` (file mtime/content unchanged), confirming the read-only fast-path is preserved. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`
- `python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Acceptance Criteria

1. A `--reset-recipient` op is not silently clobbered by a concurrent hook-fired full-state write: the reset's `failure_count: 0` / `circuit_breaker_tripped: false` persists after the interleave.
2. `--reset-recipient` never blocks/wedges: on guard contention it returns immediately (exit 0) with a clear, deterministic operator message; there is no blocking wait or busy-wait loop.
3. `--diagnose` remains read-only and lock-free (no guard file created, no `dispatch-state.json` mutation).
4. The three derived tests pass; `ruff check` and `ruff format --check` are clean on the two changed files.
5. No new CLI flag, no `dispatch-state.json` schema change, and no change to hook-fired `run_trigger` dispatch behavior.

## Risks / Rollback

- Risk: an abandoned reset guard file could block future resets. Mitigation: the guard carries a short staleness TTL and is reclaimed when stale (mirroring `_acquire_lock`'s sanity-TTL reclamation in `single_harness_bridge_dispatcher.py`); contention is also fail-fast, so the worst case is "retry the reset", never a permanent wedge.
- Risk: over-scoping the guard onto the read-only `--diagnose` path would regress its lock-free property. Mitigation: the guard is applied ONLY to the state-mutating `--reset-recipient` branch; `--diagnose` is explicitly left untouched and asserted lock-free by a regression test.
- Risk: residual race if a concurrent writer's transaction spans the guard window. Mitigation: the guard serializes the reset's read-modify-write and the re-read-immediately-before-write merges onto the freshest snapshot; the conservative posture is fail-fast on contention, so no silent clobber can occur.
- Rollback: revert the guard helper and the reset-branch change in `cross_harness_bridge_trigger.py` plus the added tests. The change is additive (one helper + one guarded branch + tests), fully reversible, with no migration and no schema/flag change.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Recommended Commit Type

`fix`
