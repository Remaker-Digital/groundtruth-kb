REVISED

bridge_kind: prime_proposal
Document: gtkb-impl-auth-packet-liveness-coupling
Version: 003
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder; explanatory output style; autonomous PB loop

Responds-To: bridge/gtkb-impl-auth-packet-liveness-coupling-002.md

Project Authorization: PAUTH-WI4532-IMPL-AUTH-LIVENESS-COUPLING-20260613
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4532

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true

---

# Implementation Proposal — Impl-Auth Packet TTL Shrink + Liveness-Coupling Proof (WI-4532) — REVISED

## Revision Scope

The GO'd `-001`/`-002` design placed a claim-liveness orphan check in the shared
`_validate_packet`. **Implementation revealed that design is both destructive and
redundant**, so this revision re-scopes it per owner S438 AUQ "TTL shrink + proof
test". The TTL shrink is retained; the broad orphan check is dropped; two tests
are added (alignment + a characterization test proving the liveness coupling
already exists at the gate). Empirical evidence below.

### Why the GO'd orphan check was withdrawn (evidence)

1. **It breaks two VERIFIED contracts.** `_validate_packet` is the shared
   validator for ALL packet-validity dimensions (hash, expiry, GO-chain drift,
   project-auth) and is called by `load_packet`, `load_named_packet`,
   `activate_packet`, and `list_named_packets` — not just the gate's
   authorization path. Adding a claim-liveness check there made **14 existing
   tests fail**, including
   `test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber`
   (WI-4452 VERIFIED clobber-fallback contract) and
   `test_validate_targets_session_aware_prefers_claimed_bridge_packet`
   (WI-4443 VERIFIED session-aware contract). Breaking a verified contract to add
   a new check is not acceptable without re-opening those threads.
2. **It is redundant at the gate.** The implementation-start gate already calls
   `work_intent_claim_block_reason(project_root, bridge_id, session_id)`
   (`scripts/implementation_authorization.py`, used at the gate path) AFTER packet
   resolution. That function returns a block when `current_holder(bridge_id)` is
   `None` (no live claim) or the holder's session differs from the caller. So an
   orphaned packet (its claim lapsed → `current_holder` returns `None`, since
   `bridge_work_intent_registry.current_holder` filters expired/lapsed claims at
   `bridge_work_intent_registry.py:165-166`) is **already rejected** at the gate.
   A live session can never be blocked by a *dead* session's packet, because the
   gate checks the *current* session's live claim. The liveness coupling the
   owner asked for already exists — at the gate, via step-2.
3. **The only real gap was the 8-hour TTL**, which let an orphaned packet linger
   (and `current.json` keep pointing at a dead session's bridge) for up to 8 h.
   Shrinking `DEFAULT_EXPIRY_MINUTES` 480 → 120 closes that gap (≤ 2 h, the
   `GO_IMPLEMENTATION_MAX_HOLD_SECONDS` claim cap), with zero verified-contract
   risk (TTL-shrink-only: **76 passed**).

## Summary

WI-4532 (P1, `implementation-start-gate`, defect): the impl-start authorization
packet had an 8-hour TTL (`DEFAULT_EXPIRY_MINUTES = 480`) while the work-intent
claim that backs it lives 10–40 min (2 h hard cap), so an orphaned packet could
linger up to 8 h after its session died. This revision shrinks the packet TTL to
120 min (matching the claim's 2 h max-hold) and adds a characterization test
proving the gate already couples authorization to claim liveness via the existing
`work_intent_claim_block_reason` step-2. Net effect: orphan packets self-expire in
≤ 2 h, and the gate already refuses to authorize a mutation that no live claim
backs. WI-4443 (session-aware read) and WI-4452 (named-packet fallback) verified
contracts are preserved untouched.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the protected behavior the gate enforces (no protected mutation without a live bridge GO authorization packet backed by the current session's live claim). This revision preserves that behavior exactly and shrinks the orphan-lifetime window.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the gate enforces the bridge protocol's authorization contract; preserved. CLAUSE-INDEX-IS-CANONICAL satisfied by the Bridge Filing section below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — work item, target paths, project authorization, and governing specs linked (this section + header metadata).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable `Project Authorization:` / `Project:` / `Work Item:` metadata present; WI-4532 is an active member of PROJECT-GTKB-RELIABILITY-FIXES.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — WI-4532 membership `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4532` active.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan maps each behavior to executed test evidence (Spec-to-Test Mapping below).
- `GOV-STANDING-BACKLOG-001` — WI-4532 backlog authority; WI-4443 / WI-4452 VERIFIED predecessors whose contracts this revision preserves.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle preserved.

## Prior Deliberations

- `WI-4443` (VERIFIED, impl `8a6a48aa2`) — session-aware read path. This revision PRESERVES its contract: `test_validate_targets_session_aware_prefers_claimed_bridge_packet` continues to pass unmodified. The gate's reliance on `current_claimed_bridge_id` (which ignores expired claims) plus `work_intent_claim_block_reason` is exactly the existing liveness coupling this revision proves and documents rather than duplicating.
- `WI-4452` (VERIFIED) — named-packet clobber-fallback. PRESERVED untouched: `test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber` continues to pass unmodified. (The withdrawn broad orphan check would have broken it; this revision does not.)
- Owner AskUserQuestion (S438, this session) — TWO decisions: (1) "Liveness-coupled + shrink TTL" (the original design choice); (2) "TTL shrink + proof test" (this finalize choice, made after I surfaced the 14-test / verified-contract breakage and the step-2 redundancy). Both are owner-decision evidence.

## Owner Decisions / Input

Owner directive (S438, AskUserQuestion, this session): after I implemented the GO'd orphan check and surfaced that it breaks 14 tests (incl. WI-4452 + WI-4443 verified contracts) and is redundant with the gate's existing `work_intent_claim_block_reason` step-2, the owner answered **"TTL shrink + proof test"** — ship the `DEFAULT_EXPIRY_MINUTES` 480→120 shrink plus an alignment test and a characterization test proving the liveness coupling already exists at the gate; do NOT force the broad orphan check. This is the owner-decision evidence authorizing this revised scope. The standing autonomous-loop directive (`DELIB-20263143`) authorizes proceeding through revise → GO → implement → report → VERIFIED.

## Requirement Sufficiency

Existing requirements sufficient. The owner's two S438 AUQ answers fully specify
the scope. No new or revised requirement artifact is needed.

## Implementation Plan

1. **Shrink the TTL** (`scripts/implementation_authorization.py:31`):
   `DEFAULT_EXPIRY_MINUTES = 120` (was 480), with a comment explaining it tracks
   `GO_IMPLEMENTATION_MAX_HOLD_SECONDS` (2 h). [Already applied under the -002 GO;
   it is a strict subset of the GO'd change.] No orphan check is added to
   `_validate_packet` (the withdrawn design).

2. **Alignment test** (`platform_tests/scripts/test_implementation_authorization.py`):
   `test_default_expiry_minutes_tracks_claim_max_hold` — asserts
   `DEFAULT_EXPIRY_MINUTES <= GO_IMPLEMENTATION_MAX_HOLD_SECONDS // 60` (≤ 120),
   so the packet TTL can never again be set to outlive the claim hard cap without
   tripping a test.

3. **Characterization test** (same file):
   `test_gate_rejects_orphaned_packet_via_work_intent_claim_check` — proves the
   liveness coupling already exists at the gate: for a bridge with NO live claim,
   `work_intent_claim_block_reason(project_root, bridge_id, session_id)` returns a
   non-None block reason ("No active work-intent claim"). Documents, as an
   enforced test, that an orphaned packet cannot authorize a mutation regardless
   of its TTL window — the behavior the broad `_validate_packet` check would have
   duplicated.

No change to `_validate_packet`, `begin`, `activate`, schema, on-disk layout,
WI-4443 session-aware read, or WI-4452 named-packet fallback.

## Spec-Derived Verification Plan

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
Expected: pass (76 prior + 2 new = 78); WI-4443 + WI-4452 contract tests unmodified and green.

python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
Expected: pass.
```

## Spec-to-Test Mapping

| Spec / behavior | Derived test | Result |
|---|---|---|
| TTL no longer outlives the claim hard cap | `test_default_expiry_minutes_tracks_claim_max_hold` — `DEFAULT_EXPIRY_MINUTES <= GO_IMPLEMENTATION_MAX_HOLD_SECONDS // 60` | PASS (expected) |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — orphan packet cannot authorize a mutation (coupling already at gate) | `test_gate_rejects_orphaned_packet_via_work_intent_claim_check` — `work_intent_claim_block_reason` returns a block when no live claim backs the bridge | PASS (expected) |
| WI-4443 session-aware contract preserved | existing `test_validate_targets_session_aware_prefers_claimed_bridge_packet` (unmodified) | PASS |
| WI-4452 clobber-fallback contract preserved | existing `test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber` (unmodified) | PASS |
| Full module non-regression | all 76 existing tests (unmodified) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + executed commands | PASS |

## Risk / Rollback

Risk: a 2 h implementation window now requires the claim to be extended within
its 2 h max-hold (matching the shrunk packet TTL) — this is the same liveness
contract the gate's step-2 already imposes, so no new operational burden beyond
what's enforced today. Rollback: single-line revert of `DEFAULT_EXPIRY_MINUTES`
to 480 + removal of the two tests; no on-disk state or schema change.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` as `bridge/gtkb-impl-auth-packet-liveness-coupling-003.md`,
with a `REVISED` line prepended to the existing document block in `bridge/INDEX.md`
via the serialized `gt bridge index set-status` CLI (`scripts/bridge_index_writer.py`
holds the lock and performs an atomic temp-then-replace read-modify-merge). Prior
`NEW@-001` and `GO@-002` status lines are preserved (append-only); no version files
are deleted or rewritten. `bridge/INDEX.md` remains canonical per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`; agent-tool Write/Edit of
INDEX is additionally blocked by the WI-4481 INDEX-write-guard hook, so all INDEX
mutations route through the serialized writer.

## Recommended Commit Type

`fix:` — closes WI-4532 (P1 8-hour-TTL reliability defect) via the TTL shrink; the
characterization test documents the pre-existing gate-level liveness coupling. No
new feature surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
