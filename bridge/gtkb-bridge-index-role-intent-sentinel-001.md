NEW

# Implementation Proposal - Bridge INDEX Role-Intent Sentinel (GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL)

bridge_kind: prime_proposal
Document: gtkb-bridge-index-role-intent-sentinel
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL

target_paths: ["bridge/INDEX.md", "scripts/check_index_role_intent_sentinel.py", "tests/scripts/test_index_role_intent_sentinel.py"]

This NEW proposal adds a role-intent sentinel to `bridge/INDEX.md` per owner directive at `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE`. Triggered by S328 session-open role-confusion latency: a session reading INDEX could not quickly tell whether the active role's actionable work was prime-builder, loyal-opposition, or shared.

## Claim

Add a sentinel comment block at the top of `bridge/INDEX.md` that declares the current role context (e.g., active prime-builder harness ID, active loyal-opposition harness ID, last update timestamp). A check script verifies the sentinel is present and well-formed.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; INDEX hygiene.
- `GOV-SESSION-SELF-INITIALIZATION-001` - session startup needs clear role indication.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - originating owner directive.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - originating owner directive (S328).

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-BRIDGE-PROTOCOL-RELIABILITY authorization including this WI; this implementation operationalizes the S328 deferred directive.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE captures the owner directive verbatim.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 + IP-3 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended. Sentinel block addition itself is part of IP-1.

## Proposed Scope

### IP-1: Sentinel block in bridge/INDEX.md

Add HTML-comment block near the top of `bridge/INDEX.md`:

```
<!-- Role-intent sentinel (per GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL):
     Prime Builder harness:    B (Claude)
     Loyal Opposition harness: A (Codex)
     Topology:                 multi_harness
     Sentinel updated:         2026-05-14T23:59:00Z
     Active Prime authorization count: <N>
     Active LO advisory count:         <N>
-->
```

The sentinel is human-readable + machine-parseable. Updated mechanically by `check_index_role_intent_sentinel.py --update` (run after batch authorization or role changes).

### IP-2: Check script

`scripts/check_index_role_intent_sentinel.py`:

- Default mode: parse sentinel block, validate freshness (< 7 days old), validate role IDs match `harness-state/role-assignments.json`. Exit non-zero on mismatch.
- `--update` mode: rewrite the sentinel block with current state.

### IP-3: Tests

Tests verify: sentinel parsing, freshness check, role-map consistency check, update mode.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Sentinel present and parsable | `test_sentinel_parses_correctly` |
| Freshness check fails on stale sentinel | `test_freshness_check_fails_stale` |
| Role-map consistency check passes when aligned | `test_role_map_consistency_passes` |
| Role-map consistency check fails on drift | `test_role_map_consistency_fails_on_drift` |
| Update mode rewrites sentinel | `test_update_mode_rewrites_sentinel` |
| Sentinel preserves non-sentinel comments | `test_update_preserves_other_comments` |

Run: `python -m pytest tests/scripts/test_index_role_intent_sentinel.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 6 tests PASS.
- Both preflights PASS.
- `bridge/INDEX.md` contains the sentinel block with current state.

## Risks / Rollback

- Risk: sentinel staleness becomes a perennial CI failure if not updated regularly. Mitigation: 7-day window + clear update command.
- Risk: INDEX edit + sentinel-update race during parallel sessions. Mitigation: sentinel update is idempotent + atomic-write pattern.
- Rollback: remove sentinel block (single comment-block deletion).

## Recommended Commit Type

`feat` - new INDEX surface + check. ~70 LOC + tests.
