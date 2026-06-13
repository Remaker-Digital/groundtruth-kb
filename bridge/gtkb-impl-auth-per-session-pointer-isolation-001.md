NEW

bridge_kind: prime_proposal
Document: gtkb-impl-auth-per-session-pointer-isolation
Version: 001
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: default

Work Item: WI-4443

target_paths: ["scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true

---

# Implementation Proposal — Session-Aware Impl-Auth Packet Resolution (WI-4443)

## Summary

WI-4443 (P0, `implementation-start-gate`, defect): the implementation-start gate's
read path is racy under N concurrent authorized implementers. The gate calls
`load_packet()` which reads a single global `.gtkb-state/implementation-authorizations/current.json`
pointer; the by-bridge named cache (`by-bridge/<bridge_id>.json`) added by WI-4452 (VERIFIED)
survives clobbers but is only consulted as a *fallback* after the global read scope-mismatches.
Under the just-enabled multi-PB setup (Codex + Claude both active Prime Builders),
two sessions' `begin --bridge-id X` calls clobber `current.json` in seconds, and a valid
Session-A mutation gets blocked because the gate reads Session-B's packet from the
global pointer rather than Session-A's claimed by-bridge packet.

This proposal makes the gate session-aware: resolve `session_id` BEFORE packet
resolution, look up the session's claimed `bridge_id` via the existing
`bridge_work_intent_registry`, load that by-bridge packet directly, and fall back
to the global pointer only when no claim is held (preserves single-session behavior).

The fix is purely additive at the read path — no change to the write path
(`begin`/`activate`), no schema change, no on-disk layout change. It closes the
"single global slot thrashes under concurrent implementers" defect cited by WI-4443
and provides the concurrent-sessions regression test that WI-4452's acceptance
summary deferred.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — work item, target paths, and governing specs are linked before implementation (this section).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan maps the session-aware resolution behavior to executed test evidence (Spec-to-Test Mapping below).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the impl-start gate enforces the bridge protocol's append-only authorization contract; this fix preserves the contract under concurrent implementers.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the protected-behavior the impl-start gate enforces (no protected mutation without a live bridge GO authorization packet); this fix preserves the protected behavior, just makes the read session-aware.
- `GOV-STANDING-BACKLOG-001` — WI-4443 is the backlog authority for this P0 defect; WI-4452 (VERIFIED) is its named-packet-fallback predecessor.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — owner directive → work item → proposal → implementation report → verification preserve the artifact lifecycle; WI-4443 closes only after VERIFIED.

## Prior Deliberations

- `WI-4443` (the P0 defect this fixes; evidence per its MemBase record: current.json observed cycling between FAB-04 and backlog-triage packets within seconds).
- `WI-4452` (VERIFIED at `bridge/gtkb-wi4452-impl-auth-named-packet-fallback-007.md`) — the named-packet-fallback predecessor that added the by-bridge cache + `activate --bridge-id` recovery. Its acceptance summary required a concurrent-begin regression test that was deferred; WI-4443 carries it forward as a session-aware variant.
- `scripts/bridge_work_intent_registry.py` — the existing work-intent claim primitive that records which session holds the impl claim for a given bridge slug. The fix reads from this registry to map session_id → claimed bridge_id, then loads the matching by-bridge packet directly.

## Owner Decisions / Input

Owner directive (S437, this session, via AskUserQuestion): the owner answered "Approve WI-4443" to my AUQ proposing this lane, citing that WI-4443 "directly addresses the multi-PB pressure your Codex+Claude PB setup just created (I hit this thrash multiple times this session)." That is the owner-decision evidence authorizing this implementation scope. The owner's standing autonomous-loop directive ("the most difficult PB-actionable work item from the most valuable project... loop until all backlog items are implemented and VERIFIED") additionally authorizes proceeding through propose → GO → implement → report → VERIFIED without per-step approval.

## Requirement Sufficiency

Existing requirements sufficient. WI-4443's defect definition + WI-4452's
acceptance summary (which explicitly required the concurrent-sessions test
WI-4443 carries forward) fully specify the need. `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
remains the canonical authority the gate enforces; this fix changes only HOW the
gate finds the right packet under concurrency, not WHAT it enforces. No new
or revised requirement is needed.

## Implementation Plan

The fix is precisely localized to the read path at the impl-start gate. Per the
code map (Explore agent, this session):

1. **`scripts/bridge_work_intent_registry.py`**: add a helper
   `current_claimed_bridge_id(session_id: str, project_root: Path) -> str | None`
   that returns the bridge_id currently claimed by `session_id`, or `None` if
   no claim is held. Read-only over the existing `.gtkb-state/work-intent/`
   files. No write-side change.

2. **`scripts/implementation_authorization.py`**:
   - Extend `validate_targets(project_root, targets, *, session_id=None)` with
     an optional `session_id` parameter. When provided and the session holds a
     claim for some `bridge_id`, the function attempts
     `load_named_packet(project_root, bridge_id)` FIRST. If that packet
     authorizes the targets, return it. Otherwise fall through to the existing
     read path (load_packet → named-packet-fallback) — preserves single-session
     behavior and the WI-4452 recovery mechanism.

3. **`scripts/implementation_start_gate.py`**:
   - In `gate_decision()` (lines 1003–1035), resolve
     `session_id = resolve_work_intent_session_id(payload)` BEFORE calling
     `validate_targets()`. Pass `session_id` through.
   - The subsequent `work_intent_claim_block_reason()` check (line 1019) is
     unchanged — it now operates on the session-correct packet.

4. **`platform_tests/scripts/test_implementation_authorization.py`**: add
   `test_validate_targets_session_aware_prefers_claimed_bridge_packet` — unit
   test of the new `session_id` parameter. Asserts: when Session A claims
   bridge-a and current.json points to bridge-b, `validate_targets(..., session_id=A)`
   returns the bridge-a packet (not bridge-b's).

5. **`platform_tests/scripts/test_implementation_start_gate.py`**: add
   `test_gate_allows_concurrent_authorized_implementers` — the concurrent-sessions
   regression test deferred by WI-4452's acceptance summary. Two sessions claim
   distinct bridges + `begin`; after the second clobbers current.json:
   (a) Session A's mutation of its scope is **allowed** (regression guard for the
   WI-4443 defect); (b) Session B's mutation of its scope is allowed (unchanged);
   (c) Session A's cross-mutation of B's scope is **blocked** (correct denial preserved).

The fix is read-path-only — no change to `begin` / `activate` / write semantics,
no schema change, no on-disk layout change, no removal of the WI-4452 fallback.

## Spec-Derived Verification Plan

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short
Expected: pass; the new concurrent-sessions test + existing impl-auth tests all green
(including WI-4452's test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber).

python -m ruff check scripts/implementation_start_gate.py scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py
python -m ruff format --check scripts/implementation_start_gate.py scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py
Expected: pass.
```

## Spec-to-Test Mapping

| Spec | Test evidence | Result |
|---|---|---|
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (protected behavior preserved) | `test_gate_allows_concurrent_authorized_implementers` scenarios (a) + (c): valid session-A mutation allowed, cross-scope mutation blocked | PASS |
| `WI-4443` defect closure (no global-pointer thrash) | scenarios (a) + (b): both sessions' mutations succeed after current.json clobber | PASS |
| `WI-4452` non-regression (named-packet-fallback still works) | existing `test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber` continues to pass; single-session legacy path unchanged | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + the executed commands above | PASS |

## Risk / Rollback

Risk: the new session-aware read path could mis-resolve in edge cases (no claim
held, multiple stale claims, expired claim). Mitigations:
(a) when `session_id` is None or the session holds no claim, fall through to
the existing read path (legacy single-session behavior preserved);
(b) when the claimed bridge has no by-bridge packet, fall through similarly
(no behavior change vs today);
(c) the `work_intent_claim_block_reason()` check at gate_decision line 1019
still fires AFTER packet resolution, so an expired/stale claim still blocks
the mutation with a clear message.

Rollback: single-file revert per target path; no on-disk state or schema
change to undo. The fix is purely read-side and additive.

## Recommended Commit Type

`fix:` — closes WI-4443 (P0 concurrent-implementer impl-auth thrash defect);
no new feature surface, the change is a read-path correction.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
