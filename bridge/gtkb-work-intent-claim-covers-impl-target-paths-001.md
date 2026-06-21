NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Work-intent claim does not cover in-flight implementation target_paths (concurrent-impl collision risk)

bridge_kind: prime_proposal
Document: gtkb-work-intent-claim-covers-impl-target-paths
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4471

target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The bridge work-intent claim (`work_intent_claims` table, keyed by `thread_slug` in `scripts/bridge_work_intent_registry.py`) provides mutual exclusion only at the *thread-slug* granularity: it prevents two sessions from claiming the **same** bridge thread, but it carries no knowledge of the GO'd `target_paths` (the packet's `target_path_globs`). The implementation-start gate (`scripts/implementation_start_gate.py::gate_decision`) authorizes a protected mutation when (a) the mutating session's OWN packet authorizes the path and (b) that session holds the claim for its OWN bridge thread (`work_intent_claim_block_reason`). Nothing checks whether a *different* active claim, held by a *different* session, has already reserved the same path through *its* packet's `target_path_globs`. Two sessions working different bridge threads whose packets' globs overlap on a shared file can therefore both pass the gate and edit that file concurrently — the concurrent-impl collision WI-4471 describes. There is no path-keyed reverse index from a target path to the set of active claims/packets that have reserved it.

## Defect / Reproduction

Reproduction (logical): 

1. Session A files claim for bridge `alpha` whose GO'd packet `target_path_globs` includes `scripts/foo.py`. A holds an active `go_implementation` claim and begins editing `scripts/foo.py`. A's gate decision passes: A's packet authorizes the path and A holds `alpha`'s claim.
2. Session B (a concurrent Prime Builder, interactive or dispatched) files claim for a *different* bridge `beta` whose GO'd packet `target_path_globs` also covers `scripts/foo.py` (either by literal overlap or by a broad glob such as `scripts/**`).
3. Session B edits `scripts/foo.py`. In `gate_decision`, `validate_targets` resolves B's OWN claimed bridge (`beta`) → B's packet, which authorizes `scripts/foo.py`; `work_intent_claim_block_reason(root, "beta", session_B)` returns `None` because B holds `beta`'s claim. The gate ALLOWS the mutation.

Result: A and B both mutate `scripts/foo.py` while A's implementation is in flight. The work-intent claim did not protect A's reserved file set from a peer session working a different thread. Expected: when a protected target is already reserved by another session's active claim+packet, the gate surfaces a collision (warn or block) so the second editor is alerted before clobbering an in-flight implementation scope.

The defect is an *absence* of a cross-claim path check; the existing `path_authorized` / `validate_targets` / `current_holder` machinery already provides every primitive needed to detect the overlap — there is simply no call site that asks "does any OTHER active claim's packet reserve this path for a different session?".

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`, `platform_tests/scripts/test_implementation_start_gate.py`.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - WI-4471 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES; this proposal implements that tracked defect.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the work-intent claim and implementation-start gate are bridge-coordination machinery; this fix strengthens the bridge's concurrency-safety contract without weakening its GO/VERIFIED authority or audit trail.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the in-flight reservation (an active claim + its packet) is a durable runtime artifact; the fix keeps the gate's allow/deny decision consistent with that reservation artifact rather than ignoring it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives tests from the cited specs and runs them (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - the new collision check is a deterministic predicate returning a canonical allow/deny/warn outcome (no owner prompt mid-gate); it follows the deterministic-policy pattern this spec establishes and does not introduce an ad-hoc owner-decision path inside the gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to GT-KB platform scripts (`scripts/...`) and platform tests; no adopter/application surface under `applications/` is touched and no placement boundary is crossed.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the implementation-start gate is a shared cross-harness enforcement surface; the fix is harness-neutral (operates on session-id + packet state, not on a specific harness), preserving Claude/Codex parity of the gate's behavior.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the collision verdict is derived from artifact-backed state (the `work_intent_claims` rows and by-bridge packet files), not inferred from transient conversation context.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the check reads claim/packet lifecycle state (active vs expired/lapsed vs terminal) so the gate fires only against live reservations and never against stale ones.

## Requirement Sufficiency

Existing requirements sufficient. `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and `GOV-FILE-BRIDGE-AUTHORITY-001` already establish that protected implementation mutations must be governed by live bridge authorization and that the bridge's coordination state is authoritative; this fix closes a concurrency gap in enforcing that contract at the path level. No new or revised requirement/specification is introduced — the change adds a derived check over existing artifact state, not a new behavior the owner must specify.

## Proposed Scope

This is the defect-removal path: add a cross-claim path-collision check and wire it into the gate. Minimal, single-concern.

1. **`scripts/implementation_authorization.py`** — add a read-only helper `cross_claim_path_collision_reason(project_root, *, targets, bridge_id, session_id)` that returns a human-readable collision reason or `None`:
   - Enumerate the by-bridge named packets (reuse the existing `by-bridge` directory scan pattern from `_named_packets_authorizing_targets` / `list_named_packets`).
   - For each named packet whose `bridge_id` differs from the mutating session's own `bridge_id`, test whether it authorizes any of the `targets` (reuse the existing `path_authorized` / `_unauthorized_targets` glob logic).
   - For each such overlapping packet, consult `bridge_work_intent_registry.current_holder(other_bridge_id, project_root=...)` (already TTL-/lapse-aware) and report a collision only when an active holder exists whose `session_id` differs from the mutating session.
   - Skip the session's own bridge, expired/lapsed claims, and `BOOTSTRAP_BRIDGE_IDS`. A registry read error fails soft (returns `None`) so packet resolution is never broken by a work-intent lookup failure, matching the existing fail-soft posture in `validate_targets`.
2. **`scripts/implementation_start_gate.py`** — in `gate_decision`, after the existing `work_intent_claim_block_reason` check passes and before/around the fail-soft auto-extend, call `cross_claim_path_collision_reason(...)` with the resolved `protected` targets, the resolved `bridge_id`, and `session_id`. On a non-`None` reason, return the standard `{"decision": "block", "reason": ...}` block envelope citing `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and naming the colliding bridge/session, with a suggested fix (coordinate or wait for the other claim to release). The collision check never changes the verdict for the single-session case (no other active overlapping claim ⇒ `None` ⇒ allow), preserving all existing gate behavior.

The WI's alternative framing ("add a separate advisory implementation lock keyed to the impl-start packet's target_path_globs") is satisfied by reusing the existing packet `target_path_globs` + active-claim state rather than introducing a new lock artifact; no new persisted lock file or schema is added.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge authorization must govern protected mutation) | `test_gate_blocks_when_other_session_claim_packet_reserves_target` | A mutation by session B to a path reserved by session A's active claim+packet (different bridge thread) returns `decision == "block"` with a collision reason naming A's bridge/session. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (no concurrent bypass of an in-flight scope) | `test_gate_allows_when_no_other_session_reserves_target` | The same mutation is ALLOWED (empty decision) when no other active claim's packet overlaps the target — single-session behavior is unchanged. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (check fires only against live reservations) | `test_collision_ignores_expired_claim_for_overlapping_packet` | An overlapping packet whose claim is TTL-expired/lapsed does NOT trigger a collision; the mutation is allowed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (same-session re-entrancy) | `test_collision_ignores_same_session_overlapping_claim` | When the overlapping claim is held by the SAME session (e.g., a session legitimately holding two threads), no collision is reported. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`
- `python -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`
- `python -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`

## Acceptance Criteria

1. `gate_decision` blocks a protected mutation whose target is reserved by a *different* session's active work-intent claim through that claim's by-bridge packet `target_path_globs`, with a reason naming the colliding bridge_id and session.
2. The gate's allow/deny verdict is unchanged for: the single-session case (no other overlapping active claim), same-session multi-thread holds, and overlapping packets whose claims are expired/lapsed/terminal.
3. The collision check is read-only and fail-soft: a work-intent registry error or missing by-bridge directory yields no collision (allow), never an exception.
4. The four derived tests pass; `ruff check` and `ruff format --check` are clean on the three changed files.

## Risks / Rollback

- Risk: false-positive collisions from stale by-bridge packets that no longer have an active claim. Mitigation: the check requires an ACTIVE `current_holder` (TTL-/lapse-aware) for the overlapping bridge, so a stale packet with no live claim never triggers a block.
- Risk: over-blocking a session that legitimately holds multiple overlapping threads. Mitigation: the check excludes claims held by the SAME session and the session's own bridge.
- Risk: a registry/DB read failure inside the gate could spuriously block. Mitigation: the helper fails soft (returns `None`) on any registry error, mirroring `validate_targets`' existing posture, so a lookup failure can never convert an authorized edit into a block.
- Rollback: revert the helper in `implementation_authorization.py` and the single call site in `implementation_start_gate.py`; the change is additive (one new function + one guarded call) plus tests, fully reversible with no migration or schema change.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing authorization for the reliability fast-lane via `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4471 is origin=defect, single-concern, introduces no new public API/CLI and no new/revised spec, and is bounded to 2 source files + 1 test (well under the fast-lane size guide), so it is covered by this standing authorization through active project membership in PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope for that batch).
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing fast-lane direction that established `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`; authorizes small reliability defect fixes to proceed through the bridge protocol under the standing PAUTH without a fresh per-item owner approval.

## Recommended Commit Type

`fix`
