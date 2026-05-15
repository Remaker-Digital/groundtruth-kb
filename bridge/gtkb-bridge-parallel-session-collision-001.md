NEW

# Implementation Proposal - Bridge Parallel-Session Collision Protection (WI-3274)

bridge_kind: implementation_proposal
Document: gtkb-bridge-parallel-session-collision
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS-BRIDGE-TOOLING-ENHANCEMENTS-PARALLEL-BATCH
Project: PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS
Work Item: WI-3274

target_paths: ["scripts/bridge_work_intent_registry.py", "tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", ".gtkb-state/work-intent/.gitkeep"]

This NEW proposal adds a work-intent registry to prevent concurrent Prime Builder sessions from writing the same bridge thread version simultaneously. Observed defect at S341 (parallel-session commit race), and recurring as documented in `feedback_bridge_parallel_session_packet_contention.md` (S350).

## Claim

Add a lightweight file-locked registry at `.gtkb-state/work-intent/<thread-slug>.json` recording per-thread session ownership. Before writing `bridge/<slug>-NNN.md` or updating `bridge/INDEX.md` for that thread, a session must acquire the lock. Acquire-or-fail semantics with 30-second TTL and stale-lock recovery.

## In-Root Placement Evidence

All target paths in-root. `.gtkb-state/` is runtime state; placeholder file ensures directory presence. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; collision protection preserves index canonicality.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3274 tracked.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization 2026-05-14.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" - explicit authorization.

## Requirement Sufficiency

Existing requirements sufficient. WI-3274 description is the operative spec.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3274); member of PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 + IP-3 single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-bridge-parallel-session-collision-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: Work-intent registry module

In `scripts/bridge_work_intent_registry.py`, expose three functions:

```python
def acquire(thread_slug: str, session_id: str, ttl_seconds: int = 30) -> bool: ...
def release(thread_slug: str, session_id: str) -> None: ...
def current_holder(thread_slug: str) -> dict | None: ...
```

`acquire()` writes `.gtkb-state/work-intent/<slug>.json` atomically (write-temp-then-rename) with `{session_id, acquired_at, ttl_expires_at}`. Returns True if previously absent or expired (stale); False if held by another non-expired session.

`release()` removes the file if it matches `session_id`; no-op otherwise.

`current_holder()` reads file; returns dict (or None if absent/expired).

### IP-2: Hook integration

Optional helper that bridge-propose/Edit-on-bridge paths can call. NOT a hard mechanical gate in this WI — sibling WIs can add bridge-compliance-gate integration after observing acquire-failure behavior.

### IP-3: Tests + (no spec promotion - new mechanism)

Tests cover acquire/release/expiry/stale-recovery semantics on a tmp-path fixture.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Fresh acquire succeeds | `test_acquire_fresh_thread_succeeds` |
| Double acquire fails | `test_acquire_blocked_when_held_by_other` |
| Same-session re-acquire idempotent | `test_acquire_idempotent_for_same_session` |
| Expired stale recovery | `test_acquire_recovers_after_expiry` |
| Release matches session | `test_release_succeeds_for_holder` |
| Release ignores non-holder | `test_release_noop_for_non_holder` |
| Atomic write (no torn read) | `test_acquire_atomic_via_temp_rename` |

Run: `python -m pytest tests/scripts/test_bridge_work_intent_registry.py -v`.

## Acceptance Criteria

- IP-1 module landed; 7 tests PASS.
- Both preflights PASS.
- No regression in existing bridge tooling.

## Risks / Rollback

- Risk: NFS/network-mount filesystems may not support atomic rename. Mitigation: detect and warn; default Windows/local-disk paths are safe.
- Risk: TTL too short for slow Codex review cycles. Mitigation: 30s default is for tool-call-level collision protection; Codex review doesn't hold the lock — only the proposal-write moment does.
- Rollback: remove module file; no integration coupling in this WI.

## Recommended Commit Type

`feat` - new mechanism. ~80 LOC (module + tests).
