NEW

# Implementation Proposal - Approval-Gate Read-Only-Flag Skip (WI-3273)

bridge_kind: implementation_proposal
Document: gtkb-approval-gate-readonly-flag-skip
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS-BRIDGE-TOOLING-ENHANCEMENTS-PARALLEL-BATCH
Project: PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS
Work Item: WI-3273

target_paths: [".claude/hooks/formal-artifact-approval-gate.py", "tests/hooks/test_formal_artifact_approval_gate.py", "platform_tests/hooks/test_formal_artifact_approval_gate.py"]

This NEW proposal fixes a usability defect in `.claude/hooks/formal-artifact-approval-gate.py`: read-only invocations (`--help`, `--dry-run`, `--validate-only`) are blocked even though they do not mutate state. Observed both at S341 (DA write CLI help blocked) and recurringly during this S350 session (verification queries blocked despite touching no mutating surface).

## Claim

When a Bash command matches `FORMAL_MUTATION_PATTERNS` AND contains any of `--help`, `--dry-run`, `--validate-only`, `-h`, `--version`, OR is a help/version subcommand pattern, the gate should not require a packet (read-only intent). Concrete: skip blocking when the command's argv (post-shlex-split) contains any of those flags as a top-level token.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` - this hook is part of the policy engine; this enhancement narrows false-positives.
- `GOV-ARTIFACT-APPROVAL-001` - the gate enforces this; read-only intent is not a mutation, so exemption is contract-preserving.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3273 tracked.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization 2026-05-14.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" - explicit authorization.

## Requirement Sufficiency

Existing requirements sufficient. WI-3273 description is the operative spec; no new spec needed. Fix is mechanical-defect class — narrowing false-positives without changing intent.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3273); member of PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-approval-gate-readonly-flag-skip-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: Add read-only flag detection

In `.claude/hooks/formal-artifact-approval-gate.py`, after `_is_formal_mutation(command)` returns True, check if the command tokens (via existing `_command_tokens` helper) contain any of:

- `--help`, `-h`
- `--dry-run`
- `--validate-only`
- `--version`, `-V`

If yes, return early without packet validation (emit `{}`). This is additive to existing logic; no other branch changes.

Edge cases: `--help` inside a quoted value (e.g., `git commit -m "fix --help bug"`) is excluded by shlex-token check (only top-level tokens). Subcommand help (e.g., `gt deliberations --help`) is included.

### IP-2: Tests + (no spec promotion - defect fix)

Tests:
- Command with `--help` matching formal pattern → not blocked
- Command with `--dry-run` matching formal pattern → not blocked
- Command with `--validate-only` matching formal pattern → not blocked
- Command without read-only flag matching formal pattern → still blocked when packet missing (regression test for true-positive preservation)
- Command with `--help` in quoted arg → still subject to gate (false-positive negation)

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| --help skips block | `test_approval_gate_skips_block_on_help_flag` |
| --dry-run skips block | `test_approval_gate_skips_block_on_dry_run_flag` |
| --validate-only skips block | `test_approval_gate_skips_block_on_validate_only_flag` |
| -h skips block | `test_approval_gate_skips_block_on_h_flag` |
| No flag → block preserved | `test_approval_gate_blocks_when_no_readonly_flag_and_no_packet` |
| Quoted --help → block preserved | `test_approval_gate_blocks_help_in_quoted_value` |

Run: `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py -v`.

## Acceptance Criteria

- IP-1 landed; 6 tests PASS.
- No regression in existing test_formal_artifact_approval_gate.py.
- Both preflights PASS.

## Risks / Rollback

- Risk: `--help` as a flag VALUE rather than a flag (rare but possible) gets the exemption. Mitigation: shlex tokenization treats it as a top-level token only when truly a flag.
- Rollback: revert single function-scope change.

## Recommended Commit Type

`fix` - defect fix narrowing false-positive set. ~15 LOC.
