NEW

# Implementation Proposal - Codex Feedback Pattern Lints (WI-3268)

bridge_kind: implementation_proposal
Document: gtkb-codex-feedback-pattern-lints
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: WI-3268

target_paths: ["scripts/bridge_proposal_pattern_lint.py", "tests/scripts/test_bridge_proposal_pattern_lint.py"]

This NEW proposal lands a pre-filing lint catching recurring Codex NO-GO patterns observed across the bridge protocol. Per memory `feedback_bridge_protocol_iteration_throughput_s341.md`, 4 mechanical defect classes hit 2-3x each: bare `pytest` command, "Codex VERIFIED (pending)" framing, missing CODEX-WAY-OF-WORKING reference, missing OWNER ACTION REQUIRED section.

## Claim

CLI: `python scripts/bridge_proposal_pattern_lint.py --bridge-id <id>`. Reads the bridge proposal, checks for the 4 recurring patterns, emits a per-pattern report. Non-blocking by default; `--strict` returns non-zero.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; lint catches recurring violations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - one of the lint targets.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - one of the lint targets (pytest invocation patterns).
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `GOV-STANDING-BACKLOG-001` - WI-3268 tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-GOVERNANCE-HARDENING including WI-3268.

## Requirement Sufficiency

Existing requirements sufficient. WI-3268 description enumerates 4 patterns.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-GOVERNANCE-HARDENING per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (lint) + IP-2 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Pattern lints

`scripts/bridge_proposal_pattern_lint.py` checks for:

1. **Bare `pytest` command**: regex `\bpytest\b` not preceded by `python -m `. Flag with suggestion to use `python -m pytest`.
2. **"Codex VERIFIED (pending)" framing**: literal substring. Flag — Prime cannot pre-author Codex verdict status.
3. **Missing CODEX-WAY-OF-WORKING reference** (when proposal is REVISED responding to NO-GO): scan `Responds to:` line; if present, require `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` mentioned in proposal or related thread reading.
4. **Missing OWNER ACTION REQUIRED section** (when proposal requires owner input per pending decision): scan for `pending decision`, `owner approval needed`, `awaiting owner` patterns without a corresponding `## Owner Action Required` heading.

### IP-2: Tests

Each pattern gets a positive + negative test case.

## Specification-Derived Verification Plan

| Pattern | Test |
|---|---|
| Bare pytest flagged | `test_bare_pytest_flagged` |
| Bare pytest not flagged when python -m present | `test_python_m_pytest_not_flagged` |
| Codex VERIFIED pending flagged | `test_codex_verified_pending_flagged` |
| Missing CODEX-WAY-OF-WORKING flagged on REVISED | `test_missing_cww_flagged_on_revised` |
| OWNER ACTION REQUIRED present when needed | `test_owner_action_required_present_when_needed` |
| OWNER ACTION REQUIRED missing flagged | `test_owner_action_required_missing_flagged` |
| --strict exit code | `test_strict_mode_exits_nonzero` |
| Default exit 0 | `test_default_exit_zero` |

Run: `python -m pytest tests/scripts/test_bridge_proposal_pattern_lint.py -v`.

## Acceptance Criteria

- IP-1, IP-2 landed; 8 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: false-positives reduce lint usefulness. Mitigation: configurable severity per pattern.
- Rollback: remove the script.

## Recommended Commit Type

`feat` - new lint tool. ~120 LOC.
