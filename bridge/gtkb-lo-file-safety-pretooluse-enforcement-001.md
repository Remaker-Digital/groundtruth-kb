NEW

# Implementation Proposal - LO File-Safety PreToolUse Enforcement (WI-3308)

bridge_kind: implementation_proposal
Document: gtkb-lo-file-safety-pretooluse-enforcement
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: WI-3308

target_paths: [".claude/hooks/lo-file-safety-gate.py", ".claude/settings.json", ".codex/gtkb-hooks/lo-file-safety-gate.py", ".codex/hooks.json", "tests/hooks/test_lo_file_safety_gate.py", "platform_tests/hooks/test_lo_file_safety_gate.py"]

This NEW proposal lands a PreToolUse hook that mechanically enforces `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule": when the active harness is assigned Loyal Opposition, Write/Edit on files not authored in-session is blocked unless an explicit owner approval packet is present.

## Claim

S350 incident: Codex (assigned LO per harness-state/role-assignments.json) edited `scripts/implementation_authorization.py` and other implementation files while in LO mode, violating the file-safety rule. The rule was advisory until now; mechanical enforcement closes the gap.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - approval-packet evidence path the hook integrates with.
- `PB-ARTIFACT-APPROVAL-001` - protected behavior contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - LO operates within bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-side parity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3308 tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-GOVERNANCE-HARDENING authorization including WI-3308.

## Requirement Sufficiency

Existing requirements sufficient. `.claude/rules/loyal-opposition.md` § File Safety Rule + S350 incident form the operative spec.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-GOVERNANCE-HARDENING per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (hook) + IP-2 (registration) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: lo-file-safety-gate.py hook

In `.claude/hooks/lo-file-safety-gate.py`:
1. Read `harness-state/role-assignments.json`; resolve current harness role.
2. If role set does NOT contain `loyal-opposition`, exit allowed (gate skips).
3. If LO active: examine Write/Edit target path. Allow if: (a) target was authored or modified by this session (track in `.gtkb-state/lo-authored-files/<session-id>.json`); (b) `GTKB_LO_FILE_OVERRIDE_PACKET` env var present and packet valid.
4. Otherwise: emit `{"decision": "block", "reason": "BLOCKED (LO file-safety): Loyal Opposition role cannot modify files not authored in-session without explicit owner approval. ..."}`.

### IP-2: Hook registration + Codex mirror

Add registration entry to `.claude/settings.json` under `hooks.PreToolUse[]` for Write|Edit|MultiEdit. Mirror at `.codex/gtkb-hooks/lo-file-safety-gate.py` + `.codex/hooks.json`.

### IP-3: Tests

Tests cover: role-detection, in-session-authored allowance, override-packet allowance, block-with-reason, Codex parity.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Prime role: gate inactive | `test_prime_role_gate_skips` |
| LO role + in-session-authored file: allowed | `test_lo_authored_file_allowed` |
| LO role + non-authored file: blocked | `test_lo_non_authored_file_blocked` |
| LO role + override packet: allowed | `test_lo_override_packet_allowed` |
| Block reason cites rule | `test_block_reason_cites_lo_rule` |
| Codex parity exists | `test_codex_mirror_exists` |
| Multi-element role set with LO blocks | `test_multi_role_set_lo_blocks` |

Run: `python -m pytest tests/hooks/test_lo_file_safety_gate.py platform_tests/hooks/test_lo_file_safety_gate.py -v`.

## Acceptance Criteria

- IP-1 hook landed; 7 tests PASS.
- IP-2 registered in both harnesses.
- Both preflights PASS.

## Risks / Rollback

- Risk: in-session-authored tracking adds state; if state file goes stale, false blocks. Mitigation: per-session state file with TTL.
- Risk: legitimate LO advisory writes (own DELIB drafts) might trigger. Mitigation: `.groundtruth/` and `bridge/` paths are in allowed-write prefixes.
- Rollback: remove hook registration; the hook script itself is benign without registration.

## Recommended Commit Type

`feat` - new governance gate. ~100 LOC + tests.
