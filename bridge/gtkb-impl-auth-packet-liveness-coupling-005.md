NEW

bridge_kind: implementation_report
Document: gtkb-impl-auth-packet-liveness-coupling
Version: 005
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder; explanatory output style; autonomous PB loop
Responds-To: bridge/gtkb-impl-auth-packet-liveness-coupling-004.md

Project Authorization: PAUTH-WI4532-IMPL-AUTH-LIVENESS-COUPLING-20260613
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4532

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

---

# Implementation Report — Impl-Auth Packet TTL Shrink + Liveness-Coupling Proof (WI-4532)

## Summary

Implemented WI-4532 per the REVISED design GO'd at `-004` (Antigravity/Gemini-LO, harness C), under impl-start packet `sha256:e7d0eb7013de6e1c902a25f09aa0370e2ac9675c89902b95bfd27768cb0ed485`. Two changes to `scripts/implementation_authorization.py` (one already applied as a subset under the `-002` GO) plus two tests:

1. **TTL shrink** — `DEFAULT_EXPIRY_MINUTES` 480 → 120, so an impl-start authorization packet can no longer outlive the work-intent claim's 2-hour hard cap (`GO_IMPLEMENTATION_MAX_HOLD_SECONDS`). This closes the orphan-lock defect WI-4532 names: the 8-hour packet that lingered after a session died (claim lapsed in 10–40 min) now self-expires in ≤ 2 h.
2. **Gate-level liveness-coupling proof** — a characterization test documenting that the gate's existing `work_intent_claim_block_reason` step-2 already rejects orphaned packets (no live claim → block), which is why the broad `_validate_packet` orphan check (GO'd at `-002`) was withdrawn as redundant and destructive (it broke 14 tests incl. the WI-4443 and WI-4452 verified contracts).

**Live confirmation:** the impl-start packet minted for THIS implementation has `expires_at` 2 hours out (`19:30:13Z` → `21:30:13Z`), not 8 hours — direct evidence the shrink is in effect.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the gate's protected behavior preserved exactly; the orphan-lifetime window is shrunk.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (CLAUSE-INDEX-IS-CANONICAL) — preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — work item, target paths, project authorization, and governing specs linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable `Project Authorization:` / `Project:` / `Work Item:` metadata present in the header.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — WI-4532 active member of PROJECT-GTKB-RELIABILITY-FIXES.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + executed evidence below.
- `GOV-STANDING-BACKLOG-001` — WI-4532 backlog authority; its verified predecessors are preserved untouched.

## Owner Decisions / Input

Owner directives (S438, AskUserQuestion, this session): (1) "Liveness-coupled + shrink TTL" — the original design choice; (2) "TTL shrink + proof test" — the finalize choice made after I surfaced that the GO'd `_validate_packet` orphan check breaks 14 tests (incl. 2 verified contracts) and is redundant with the gate's step-2. This report implements decision (2). Captured under the autonomous-backlog-loop directive `DELIB-20263143` via `PAUTH-WI4532-IMPL-AUTH-LIVENESS-COUPLING-20260613`.

## Files Changed

1. `scripts/implementation_authorization.py` — `DEFAULT_EXPIRY_MINUTES = 120` (was 480), with a comment explaining it tracks `GO_IMPLEMENTATION_MAX_HOLD_SECONDS` (2 h) and noting the orphan-check design was withdrawn in favor of the existing gate-level coupling. No change to `_validate_packet`, `begin`, `activate`, schema, or on-disk layout.
2. `platform_tests/scripts/test_implementation_authorization.py` — two tests added (no existing test modified):
   - `test_default_expiry_minutes_tracks_claim_max_hold` — asserts the packet TTL is at most `GO_IMPLEMENTATION_MAX_HOLD_SECONDS // 60` and equal to 120; fails closed if the TTL is ever re-widened past the claim cap.
   - `test_gate_rejects_orphaned_packet_via_work_intent_claim_check` — proves the gate-level liveness coupling: no live claim → `work_intent_claim_block_reason` denies; live claim → permits; a claim held by a different session still blocks the caller (cross-scope denial preserved).

## Verification Evidence (commands + observed results)

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --no-header
-> 78 passed (76 prior + 2 new). The WI-4443 session-aware and WI-4452 clobber-fallback
   contract tests are UNMODIFIED and green.

python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
-> All checks passed!  (one SIM300 Yoda-condition was fixed during implementation)

python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
-> 2 files already formatted.

Live runtime evidence: implementation_authorization.py begin --bridge-id gtkb-impl-auth-packet-liveness-coupling
-> packet expires_at = 2026-06-13T21:30:13Z (minted 19:30:13Z) = 2h TTL, confirming DEFAULT_EXPIRY_MINUTES=120 in effect.
```

## Spec-to-Test Mapping

| Spec / behavior | Test evidence | Result |
|---|---|---|
| TTL no longer outlives the claim hard cap | `test_default_expiry_minutes_tracks_claim_max_hold` | PASS |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — orphan packet cannot authorize a mutation (coupling at gate) | `test_gate_rejects_orphaned_packet_via_work_intent_claim_check` (orphan-blocked + live-permits + cross-session-blocked) | PASS |
| WI-4443 session-aware contract preserved | existing `test_validate_targets_session_aware_prefers_claimed_bridge_packet` (unmodified) | PASS |
| WI-4452 clobber-fallback contract preserved | existing `test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber` (unmodified) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + executed commands above | PASS |

## Scope Adherence

Implemented exactly the GO'd `-004` target_paths (2 files); no existing test modified (only 2 added); `_validate_packet` untouched. The withdrawn broad orphan check is NOT present. The session-aware and clobber-fallback verified contracts are preserved and re-confirmed green.

## Recommended Commit Type

`fix:` — closes WI-4532 (P1 8-hour-TTL orphan-lock reliability defect) via the TTL shrink; the characterization test documents the pre-existing gate-level liveness coupling. No new feature surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
