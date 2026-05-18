NEW

# Implementation Proposal: Allow Startup Relay Cache Read Through PreToolUse Gate

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3323
target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

## Summary

The init-keyword startup-disclosure relay now emits a bounded pointer to `.codex/gtkb-hooks/last-user-visible-startup.md` / `.claude/hooks/last-user-visible-startup.md` and instructs the assistant to perform exactly one read-only filesystem read of that cache, then relay the startup disclosure verbatim. The live session exposed a remaining contradiction: after the UserPromptSubmit hook sets `startup_response_pending: true`, `guard_tool_use()` blocks all tool calls, including the exact read-only cache read the relay instruction authorizes. The result is a false claim that startup was already emitted while the owner-visible disclosure is never shown.

This proposal authorizes the narrow receiver-side fix: while `startup_response_pending` is true, PreToolUse should allow only the one read-only access to the harness-scoped startup disclosure cache named by `_startup_relay_cache_paths()`, and should continue to block every other tool use until the next owner prompt clears the pending startup-response state.

## Specification Links

- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 - governs the init-keyword startup-disclosure relay. The relay must render the owner-visible startup disclosure, must not substitute a short acknowledgement, and must fail visibly when the cache is unusable.
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 - the canonical init keyword activates this receiver path.
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 - the relay path is keyed to the active harness and durable role assertion.
- GOV-SESSION-SELF-INITIALIZATION-001 - requires fresh-session self-initialization disclosure delivery.
- PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 - requires the startup governance disclosure to be treated as first-class owner-visible session content.
- DCL-SESSION-STARTUP-TOKEN-BUDGET-001 - supports the bounded pointer relay that avoids inlining the full disclosure into hook context.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - requires Codex / Claude hook parity and explicit fallback behavior.
- GOV-RELIABILITY-FAST-LANE-001 - authorizes routing this single-concern defect fix through the reliability fast-lane.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol authority for this proposal.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites relevant governing specifications and maps them to tests.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification must execute tests derived from the linked specifications.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, and DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - artifact-oriented governance baseline for preserving this defect and fix through governed bridge state.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` already specifies the relay behavior that this defect violates: the startup disclosure must be visibly relayed and a short acknowledgement is not a substitute. This proposal does not create or revise a formal requirement; it implements the existing relay contract.

## Prior Deliberations

- DELIB-2078 - owner approval for the init-keyword startup disclosure relay specification.
- DELIB-1536 - Loyal Opposition review of SessionStart formalization and the init-keyword contract.
- DELIB-1530 / DELIB-1531 - Loyal Opposition startup symmetry reviews relevant to role-correct startup relay behavior.
- DELIB-1075 / DELIB-1083 - prior startup token consumption and premature wrap-up feedback relevant to bounded relay and startup-response handling.

No searched deliberation rejected the bounded-pointer relay or a narrowly scoped read-only cache exception.

## Owner Decisions / Input

On 2026-05-15/16 in this session, the owner observed that the visible chat did not contain the startup disclosure after `::init gtkb pb`, called it an error, and then answered `Yes, file/route the bridge work` when asked whether to move the startup relay defect through the bridge / implementation authorization path. This proposal implements that owner direction through the standing reliability fast-lane. No production deployment, credential lifecycle action, or formal GOV/ADR/DCL/SPEC mutation is requested.

## Problem Statement

Live evidence from this session:

1. UserPromptSubmit returned the startup relay pointer instructing one read-only cache read from `.codex/gtkb-hooks/last-user-visible-startup.md`.
2. A subsequent attempt to read that cache was blocked by PreToolUse with `BLOCKED (GTKB-STARTUP-INPUT-GATE): startup disclosure has been emitted; awaiting owner's next message before tool use`.
3. The cache file existed, was readable after the next owner message, and contained the full startup disclosure.
4. The failure was therefore not missing cache content. It was a state-machine contradiction: the relay instruction requires a read that the pending-startup guard forbids.

## Proposed Implementation

1. Add a small helper in `scripts/workstream_focus.py`, near the startup relay helpers, that recognizes the one authorized read-only access to the active harness-scoped startup cache path returned by `_startup_relay_cache_paths(root)`.
2. The helper should accept the repository's relevant read-only tool shapes, at minimum direct file read payloads and the PowerShell command shape used by this harness: `Get-Content -Raw .codex/gtkb-hooks/last-user-visible-startup.md` or the equivalent `.claude/hooks/...` path for Claude. It must reject commands that include extra operations, additional paths, mutation verbs, shell chaining, or non-cache targets.
3. Change `guard_tool_use()` so `startup_response_pending` blocks tool use unless `_startup_relay_cache_read_allowed(payload, project_root)` returns true.
4. Leave `_clear_startup_response_pending_for_followup()` behavior unchanged: the startup response remains pending until the next owner prompt clears it.
5. Do not change startup disclosure generation, SessionStart cache writing, bridge dispatch behavior, or formal artifact state.

## Spec-Derived Test Plan

- Add `test_startup_response_pending_allows_single_relay_cache_read` in `platform_tests/hooks/test_workstream_focus.py`: with `startup_response_pending: true`, a read-only request for the harness-scoped `last-user-visible-startup.md` path returns `{}` from `guard_tool_use()`.
- Extend or add tests confirming ordinary writes remain blocked while `startup_response_pending` is true. This preserves the existing `test_startup_response_pending_blocks_tool_use_until_next_owner_prompt` behavior.
- Add negative cases for non-cache reads or shell commands with extra operations if needed to prove the exception is narrow.
- Re-run `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`.
- Re-run `python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`.
- Re-run `python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`.

## Acceptance Criteria

1. The init-keyword startup relay turn can perform exactly the authorized read-only cache read while `startup_response_pending` is true.
2. Any non-cache tool use remains blocked until the next owner prompt clears pending startup response state.
3. The guard no longer forces the assistant to replace the startup disclosure with a short acknowledgement caused by a blocked cache read.
4. The fix is confined to the two listed `target_paths`.
5. Targeted pytest and ruff checks pass, or any unrelated pre-existing failure is disclosed in the implementation report.

## Fast-Lane Eligibility

This is a single-concern defect fix under active work item WI-3323. It modifies only startup relay receiver guard behavior and a targeted regression test. It introduces no public API, no CLI, no deployment operation, no formal artifact mutation, no credential lifecycle action, and no bulk work-item or specification operation.

## Pre-Filing Preflight

Catch-22 note: this proposal is filed through the bridge-propose helper, so the authoritative `bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-pretooluse-read-exemption` and `adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-pretooluse-read-exemption` checks will be run immediately after the INDEX entry exists. If either reports missing required specifications or blocking gaps, Prime Builder must revise before implementation.

## Files Expected To Change

- `scripts/workstream_focus.py` - narrow startup cache read exception in `guard_tool_use()`.
- `platform_tests/hooks/test_workstream_focus.py` - regression coverage for allowed cache read and blocked non-cache tool use while startup response is pending.

## Risk and Rollback

Risk is limited to the startup relay turn. The guard exception must be exact-path and read-only to avoid weakening the pending-startup protection. Rollback is to revert the two target files and return to the prior behavior, accepting that startup disclosure relay can fail when the cache read is blocked.

## Recommended Commit Type

`fix:` - repairs a broken startup relay guard interaction without adding a new owner-facing feature.
