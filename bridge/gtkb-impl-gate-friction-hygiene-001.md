NEW

# Implementation Proposal - Implementation Gate Friction Hygiene (WI-3310)

bridge_kind: implementation_proposal
Document: gtkb-impl-gate-friction-hygiene
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3310

target_paths: ["scripts/implementation_start_gate.py", "tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This NEW proposal addresses a cluster of friction-hygiene issues in `implementation_start_gate.py`: null-sink redirect allowlist completeness, state-file recovery semantics, error message clarity, and per-recipient dispatch semantics. Companion to the format-spec false-positive (WI-3317, sibling).

## Claim

Three minor improvements: (1) extend null-sink redirect strip to handle additional Windows variants (`2>NUL`, `>$null`), (2) improve error message to cite specific clause + suggest packet-citation pattern, (3) add `--diagnostic` flag that prints what would be blocked without enforcing.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - gate enforces this; hygiene preserves it.
- `GOV-ARTIFACT-APPROVAL-001` - protected mutation evidence requirement.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3310 tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-APPROVAL-PACKET-ERGONOMICS authorization including WI-3310.

## Requirement Sufficiency

Existing requirements sufficient. WI-3310 description specifies the hygiene scope.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 + IP-3 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: Extend null-sink redirect allowlist

In `scripts/implementation_start_gate.py:NULL_SINK_REDIRECT_STRIP_RE`, ensure pattern handles: `2>/dev/null`, `>/dev/null`, `2>NUL`, `>NUL`, `2>$null`, `>$null`, `&>/dev/null`. Add explicit test fixtures for each.

### IP-2: Block-reason clarity

In `gate_decision()`, when emitting the block reason, format:
```
BLOCKED (GTKB-IMPLEMENTATION-START-GATE): <clause-id>
Reason: <root cause>
Suggested fix: <action>
```
Include the specific PROTECTED_PREFIXES entry that matched (e.g., "scripts/" or "<unknown-mutating-target>"). Suggest acquiring an authorization packet via `python scripts/implementation_authorization.py begin --bridge-id <id>`.

### IP-3: --diagnostic flag

Add a CLI invocation mode: `python scripts/implementation_start_gate.py --diagnostic` reads stdin payload, runs the gate logic, and prints what would be decided + why — without emitting a block decision. Useful for self-checking during proposal authoring.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| 2>NUL allowed as null-sink | `test_null_sink_2_to_nul_allowed` |
| >$null allowed as null-sink | `test_null_sink_dollar_null_allowed` |
| &>/dev/null allowed as null-sink | `test_null_sink_amp_dev_null_allowed` |
| Block reason includes clause + suggestion | `test_block_reason_includes_clause_and_suggestion` |
| --diagnostic prints decision without emitting | `test_diagnostic_mode_no_emit` |
| --diagnostic round-trip matches enforce mode | `test_diagnostic_matches_enforce` |

Run: `python -m pytest tests/scripts/test_implementation_start_gate.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: null-sink allowlist over-broadens may mask real redirects. Mitigation: tests cover false-positive negation alongside true-positive preservation.
- Rollback: revert each IP independently (3 separate function/regex changes).

## Recommended Commit Type

`fix` - friction hygiene + UX improvements. ~40 LOC.
