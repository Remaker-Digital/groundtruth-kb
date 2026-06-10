NEW

# Implementation Proposal - Startup Enhancements P2: Claude Startup-Freshness Contract (GTKB-STARTUP-ENHANCEMENTS)

bridge_kind: prime_proposal
Document: gtkb-startup-enhancements-p2-freshness-contract
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-STARTUP-ENHANCEMENTS

target_paths: ["scripts/session_self_initialization.py", "tests/scripts/test_session_self_initialization.py", "groundtruth-kb/tests/test_startup_freshness.py"]

This NEW proposal advances the next-slice work on GTKB-STARTUP-ENHANCEMENTS: P2 sub-slice — Claude startup-freshness contract. Per the WI description, P1 already VERIFIED at S309; P2 is the smaller standalone bridge of "P2 Claude startup-freshness contract OR P3 six-primer registry".

## Claim

Define and enforce a startup-freshness contract: at session start, the cached startup payload (from `scripts/session_self_initialization.py`) must be no more than N minutes old (default 15) AND must reflect current `harness-state/role-assignments.json` + `bridge/INDEX.md` state. If stale, regenerate before rendering.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup self-initialization spec.
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` - proactive engagement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `bridge/gtkb-startup-enhancements-p1-006.md` - P1 VERIFIED (predecessor slice).

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-SESSION-LIFECYCLE-UX authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI description identifies P2 as the "smaller standalone bridge" of the remaining options.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI, one slice (P2 only); member of PROJECT-GTKB-SESSION-LIFECYCLE-UX per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (freshness check) + IP-2 (regeneration trigger) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Freshness check in session_self_initialization.py

Add `_is_payload_fresh(payload_path, max_age_seconds=900)` helper:
- Returns True if `payload_path` exists AND `mtime < max_age_seconds` AND payload's recorded role/role-map signature matches current.
- Returns False otherwise.

### IP-2: Regeneration trigger

In the startup payload load path:
1. If `_is_payload_fresh()` is False, log diagnostic "payload stale: <reason>" and regenerate.
2. If True, use cached payload directly.

Cache invalidation triggers: role-map mtime newer than payload mtime, or bridge/INDEX.md mtime newer than payload mtime, or payload age > 15 min.

### IP-3: Tests

Tests cover: fresh-payload reuse, stale-by-age regeneration, role-map-drift regeneration, bridge-index-drift regeneration.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Fresh payload reused | `test_fresh_payload_reused` |
| Stale-by-age triggers regen | `test_stale_by_age_regenerates` |
| Role-map drift triggers regen | `test_role_map_drift_regenerates` |
| INDEX drift triggers regen | `test_index_drift_regenerates` |
| Regen produces equivalent shape | `test_regenerated_payload_shape` |
| Logging on stale-payload diagnostic | `test_diagnostic_log_emitted` |

Run: `python -m pytest tests/scripts/test_session_self_initialization.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: regen on every session-start adds latency. Mitigation: only when stale; default 15min cache window.
- Rollback: revert freshness check; payload always regenerates (current default).

## Recommended Commit Type

`feat` - startup-freshness contract. ~60 LOC + tests.
