NEW

bridge_kind: prime_proposal
Document: gtkb-impl-auth-packet-liveness-coupling
Version: 001
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder; explanatory output style; autonomous PB loop

Project Authorization: PAUTH-WI4532-IMPL-AUTH-LIVENESS-COUPLING-20260613
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4532

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true

---

# Implementation Proposal — Impl-Auth Packet Liveness Coupling + TTL Shrink (WI-4532)

## Summary

WI-4532 (P1, `implementation-start-gate`, defect): the impl-start authorization
packet has an 8-hour TTL (`DEFAULT_EXPIRY_MINUTES = 480`,
`scripts/implementation_authorization.py:31`) while the work-intent claim that is
supposed to back it lives only 10 min (draft) to 40 min (go-implementation:
30 min deadline + 10 min grace), with a 2-hour hard cap
(`GO_IMPLEMENTATION_MAX_HOLD_SECONDS`). The packet therefore outlives its
liveness signal by 4×–48×. When a session dies / sleeps / restarts — observed
repeatedly this session (`dbbdc1`, `6441d1`, `803a2f`, plus a mid-session
harness restart) — its claim lapses in minutes but its 8-hour packet lingers,
and `current.json` keeps pointing at the dead session's bridge.

WI-4443 (VERIFIED, `8a6a48aa2`) fixed read-path *disambiguation* — the
session-aware `current_claimed_bridge_id` (which ignores expired/lapsed claims)
makes the gate prefer the current session's own claimed-bridge packet. But it
did NOT address packet *lifetime*: an orphaned 8-hour packet is still
structurally valid until its 8-hour clock runs out. This proposal closes that
gap by making packet validity *derive from* a live claim, and by shrinking the
fallback TTL to the claim's hard cap.

Owner (S438, AskUserQuestion) directed "Liveness-coupled + shrink TTL": make the
claim the authoritative liveness primitive so orphan packets go stale the moment
their claim lapses.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the protected behavior the impl-start gate enforces (no protected mutation without a live bridge GO authorization packet). This proposal tightens that behavior: a packet is no longer "live" merely because its 8-hour clock has not elapsed; it must be backed by a live work-intent claim. The enforced contract is unchanged (live authorization required); the definition of "live" is corrected.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the impl-start gate enforces the bridge protocol's append-only authorization contract; this fix preserves the contract and removes the orphan-lock unreliability class. CLAUSE-INDEX-IS-CANONICAL is satisfied by the Bridge Filing section below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — work item, target paths, project authorization, and governing specs are linked before implementation (this section + the header metadata).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable `Project Authorization:` / `Project:` / `Work Item:` metadata present in the header (WI-4532 bound to PROJECT-GTKB-RELIABILITY-FIXES via `PAUTH-WI4532-IMPL-AUTH-LIVENESS-COUPLING-20260613`; WI-4532 is an active project member).
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — WI-4532 admitted to PROJECT-GTKB-RELIABILITY-FIXES as an active member (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4532`).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps each behavior to executed test evidence (Spec-to-Test Mapping below).
- `GOV-STANDING-BACKLOG-001` — WI-4532 is the backlog authority for this defect; WI-4443 (VERIFIED) and WI-4452 (VERIFIED) are its predecessors in PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — owner directive → work item → proposal → implementation report → verification preserve the artifact lifecycle; WI-4532 closes only after VERIFIED.

## Prior Deliberations

- `WI-4443` (VERIFIED at `bridge/gtkb-impl-auth-per-session-pointer-isolation-005.md`, impl `8a6a48aa2`) — the session-aware read-path predecessor. Added `current_claimed_bridge_id(session_id)` which ignores expired/lapsed claims. This proposal builds directly on that: the same registry liveness signal (`current_holder` returning None for expired claims, `bridge_work_intent_registry.py:165-166`) now also gates packet *validity*, not just read-path *preference*. WI-4443 is NOT reverted.
- `WI-4452` (VERIFIED) — the named-packet-fallback predecessor (by-bridge cache + `activate --bridge-id` recovery). This proposal's orphan check applies uniformly to `load_packet`, `load_named_packet`, and `activate_packet` because they all route through the shared `_validate_packet`; the named-packet fallback continues to function for live claims and correctly rejects orphaned named packets.
- Owner AskUserQuestion (S438, this session): "Liveness-coupled + shrink TTL" — the owner-decision basis. The owner first diagnosed "8-hour locks on claimed bridge items … are unreliable," then on a fresh code reading confirmed WI-4443 should NOT be reverted and chose this completing fix.

## Owner Decisions / Input

Owner directive (S438, AskUserQuestion, this session): "Liveness-coupled + shrink TTL" — make packet validity contingent on a live work-intent claim (orphan packet → stale the moment its claim lapses) AND shrink `DEFAULT_EXPIRY_MINUTES` from 480 to ≤120 (the 2 h claim max-hold). The claim becomes the authoritative liveness primitive. This answer is the owner-decision evidence authorizing this implementation scope. The owner additionally confirmed (S438) that WI-4443's session-aware fix is VERIFIED and must NOT be reverted; this proposal builds on it. The standing autonomous-loop directive (`DELIB-20263143`) authorizes proceeding through propose → GO → implement → report → VERIFIED.

## Requirement Sufficiency

Existing requirements sufficient. `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
remains the canonical authority the gate enforces; this fix corrects the
*definition of a live packet* (must be claim-backed) without changing WHAT the
gate enforces. The owner's S438 AUQ fully specifies the two mechanisms. No new
or revised requirement is needed.

## Implementation Plan

Two localized changes in `scripts/implementation_authorization.py`, plus tests.

1. **Liveness coupling in `_validate_packet`** (line 1084, the shared validator
   called by `load_packet`, `load_named_packet`, `activate_packet`). Immediately
   after the expiry check (line 1092-1093), add an orphan check:
   - Resolve `bridge_id = str(packet.get("bridge_id") or "")`.
   - If `bridge_id` is non-empty AND not in `BOOTSTRAP_BRIDGE_IDS` (line 32),
     query `bridge_work_intent_registry.current_holder(bridge_id, project_root=project_root)`.
     `current_holder` already returns `None` for expired/lapsed claims
     (`bridge_work_intent_registry.py:165-166`).
   - If the holder is `None`, raise
     `AuthorizationError("…packet for bridge <id> is orphaned: no live work-intent
     claim backs it … re-claim and re-run begin")`.
   - **Fail-open on registry error**: wrap the `current_holder` call in
     `try/except bridge_work_intent_registry.WorkIntentRegistryError` and, on
     error, SKIP the orphan check (do not block). This matches the WI-4443
     precedent (packet resolution must never hard-break on a work-intent lookup
     failure) and preserves the other validations (hash, expiry, GO-chain).
   - This is a no-op in the happy path: a session holding its own live claim
     resolves a non-None holder and passes. It fires only for orphaned packets.

2. **Shrink the fallback TTL** (line 31): `DEFAULT_EXPIRY_MINUTES = 120`
   (was 480), matching `GO_IMPLEMENTATION_MAX_HOLD_SECONDS` (2 h). Defense in
   depth: even if the liveness check is skipped (registry unavailable), the
   packet cannot outlive the claim's hard cap. A direct import of the claim
   constant is avoided to keep `implementation_authorization.py` free of a new
   import cycle; a test asserts the two stay aligned (≤ 120 min).

No change to `begin` / `activate` write semantics, no schema change, no on-disk
layout change, no change to WI-4443's session-aware read path.

## Spec-Derived Verification Plan

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
Expected: pass; new orphan/liveness + TTL tests green; all existing impl-auth tests
(incl. WI-4443 session-aware + WI-4452 named-packet-fallback) still pass.

python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
Expected: pass.
```

## Spec-to-Test Mapping

| Spec / behavior | Derived test | Result |
|---|---|---|
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — orphan packet (no live claim) is rejected | `test_validate_packet_rejects_orphaned_packet` — valid hash/expiry/GO packet, no live claim → `AuthorizationError` ("orphaned") | PASS |
| Happy path preserved — live-claim packet is accepted | `test_validate_packet_accepts_packet_with_live_claim` — same packet + a live `current_holder` for the bridge → validates without error | PASS |
| `BOOTSTRAP_BRIDGE_IDS` exemption | `test_bootstrap_bridge_packet_exempt_from_liveness` — bootstrap bridge_id needs no claim → validates | PASS |
| Fail-open on registry error | `test_validate_packet_liveness_fails_open_on_registry_error` — `current_holder` monkeypatched to raise `WorkIntentRegistryError` → validation still passes (other checks unaffected) | PASS |
| TTL shrink tracks claim hard cap | `test_default_expiry_minutes_tracks_claim_max_hold` — `DEFAULT_EXPIRY_MINUTES <= GO_IMPLEMENTATION_MAX_HOLD_SECONDS // 60` (≤ 120) | PASS |
| WI-4443 / WI-4452 non-regression | existing `test_validate_targets_session_aware_prefers_claimed_bridge_packet`, `test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber`, and the full module suite continue to pass | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + the executed commands above | PASS |

## Risk / Rollback

Risk 1 — a legitimately-working session whose claim lapses mid-implementation
(go-implementation claim: 40 min, extendable to 2 h hard cap) would have its
packet go orphaned and the next protected Write blocked. Mitigation: this is the
*intended* behavior (no long-lived locks); the block message instructs the
session to re-claim (`bridge_claim_cli.py claim`), which is a fast, idempotent
liveness checkpoint. The go-implementation claim is extendable up to 2 h, which
matches the shrunk packet TTL, so a single 2-hour implementation window needs at
most periodic claim extension — the same liveness contract the gate's existing
step-2 `work_intent_claim_block_reason` already imposes.

Risk 2 — registry DB transiently unavailable. Mitigation: fail-open on
`WorkIntentRegistryError` (the orphan check is skipped, the 120-min TTL + GO-chain
checks still apply).

Rollback: single-file revert of `scripts/implementation_authorization.py` (two
hunks) + the test additions; no on-disk state or schema change to undo. Restoring
`DEFAULT_EXPIRY_MINUTES = 480` and removing the orphan block returns prior
behavior exactly.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` as
`bridge/gtkb-impl-auth-packet-liveness-coupling-001.md`, with a `NEW` entry added
to `bridge/INDEX.md` via the serialized `gt bridge index add-document` CLI
(`scripts/bridge_index_writer.py` holds the file lock and performs an atomic
temp-then-replace read-modify-merge). No prior version files are deleted or
rewritten (this is version 001). `bridge/INDEX.md` remains the canonical workflow
state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`; agent-tool
Write/Edit of INDEX is additionally blocked by the WI-4481 INDEX-write-guard hook,
so all INDEX mutations route through the serialized writer.

## Recommended Commit Type

`fix:` — closes WI-4532 (P1 orphan-lock / 8-hour-TTL reliability defect); no new
feature surface, the change corrects packet-validity semantics and a TTL constant.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
