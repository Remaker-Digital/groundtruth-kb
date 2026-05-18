NEW

# Post-Implementation Report: bridge-stop-drain Deference-Gap Repair (WI-3363)

bridge_kind: implementation_report
Document: gtkb-bridge-stop-drain-deference-repair
Version: 005 (NEW; post-implementation report for the GO at -004)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001; WI-3363
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3363
target_paths: [".claude/hooks/bridge-stop-drain.py", "platform_tests/hooks/**"]
Recommended commit type: fix:

## Summary

This is the post-implementation report for WI-3363, implemented under the GO at `bridge/gtkb-bridge-stop-drain-deference-repair-004.md`. `.claude/hooks/bridge-stop-drain.py` — the role-aware Stop-event bridge auto-drain (WI-3359) — emitted its drain-block in two situations where its own contract requires it to defer. IP-1 removes the owner-decision recency window so any unresolved owner decision suppresses the drain regardless of age; IP-2 adds wrap-up-command deference so the drain yields when the owner ends the turn with a wrap-up command; IP-3 updates and extends the regression suite. The scope is exactly the GO'd `-003` proposal: two files — `.claude/hooks/bridge-stop-drain.py` and `platform_tests/hooks/test_bridge_stop_drain.py` — and no other source.

## Specification Links

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — the drain exists to keep the owner out of the loop for dispatchable bridge work; deferring when the owner is mid-decision or wrapping up is part of correctly honoring this ADR, not a contradiction of it.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — the auto-trigger contract; the drain is the active-session arm of it. The deference fix does not change when actionable work triggers a drain, only when the drain must yield to the owner.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; eligibility was confirmed at the `-004` GO.
- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge-stop-drain.py` is bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state; the deference fix does not alter the actionable-status reading.
- GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 — session lifecycle management is proactive; an owner-invoked wrap-up is part of that lifecycle. IP-2's wrap-up-command deference makes the Stop-drain yield to an owner-invoked wrap-up rather than block turn-end against it.
- PB-SESSION-WRAP-UP-PROACTIVE-001 — sessions proactively initiate wrap-up guidance before ending. IP-2 governs `bridge-stop-drain.py` so a drain-block cannot interrupt the wrap-up path when the owner has issued a wrap-up command.
- DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001 — automatic session lifecycle hooks are non-mutating unless separately authorized. IP-2's wrap-up deference is itself non-mutating: on a wrap-up command the drain hook returns the empty allow-stop result and takes no action.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — the linked specifications are carried forward from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the spec-to-test mapping and observed results are below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation across proposal, deliberation, and report (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions toward verified (advisory).

## Prior Deliberations

- `bridge/gtkb-bridge-stop-drain-deference-repair-001.md` … `-004.md` — this thread. `-002` (Codex NO-GO, finding F1) required the session-lifecycle/wrap-up specification linkage; `-003` (REVISED) added it; `-004` recorded GO. This report is the post-implementation submission for that GO.
- `bridge/gtkb-bridge-active-session-autodrain-005.md` / `-007.md` / `-008.md` — the parent WI-3359 autodrain thread. `-005` specified owner-decision deference unqualified; `-007` disclosed the implemented 30-minute recency window; `-008` recorded VERIFIED. IP-1 here repairs the gap between the `-005` specified intent and the `-007` implemented behavior.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — establishes `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and `GOV-RELIABILITY-FAST-LANE-001`. This implementation is covered by that standing authorization (WI-3363 is an active project member).

## Owner Decisions / Input

- 2026-05-17 owner directive: the owner reported `bridge-stop-drain.py` firing on a wrap-up command and with an answered-but-unresolved owner decision pending, and directed the deference repair.
- 2026-05-17 via AskUserQuestion the owner chose the reliability fast-lane framing (WI-3363 under `PROJECT-GTKB-RELIABILITY-FIXES`), and on 2026-05-18 via AskUserQuestion chose to implement this thread next.
- No new owner decision was required before implementation. This is a reliability-fast-lane defect fix covered by the standing project authorization; no formal-artifact-approval packet and no new owner decision are required. The implementation-start authorization packet was minted from the live `-004` GO before any protected edit.

## Clause Scope Clarification (Not a Bulk Operation)

This report covers a scoped reliability defect fix to one hook file plus its regression suite. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it carries no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is not applicable. The single work item cited (WI-3363) is this report's own implementing work item under the mandatory project-linkage metadata.

## Implementation Summary

- **IP-1** — In `_owner_decision_pending()`, removed the `OWNER_DECISION_RECENCY_MINUTES` window: any unresolved owner decision (a `memory/pending-owner-decisions.md` block whose `status` is not `resolved`) now suppresses the drain regardless of its `asked_at` age. The `status == "resolved"` skip and the fail-open behavior (return `False` when the file is absent or unparseable) are preserved. The constant `OWNER_DECISION_RECENCY_MINUTES`, the `cutoff` arithmetic, the now-dead `_ASKED_AT_RE` regex, and the now-unused `timedelta` import were removed so the hook stays lint-clean.
- **IP-2** — Added wrap-up-command deference. A module-level `WRAPUP_TRIGGER_COMMANDS` tuple — a byte-equal local copy of the canonical 17-command tuple in `scripts/session_self_initialization.py`, copied rather than imported to avoid loading that large startup module into a per-turn-end hook. Four new helpers — `_read_transcript_tail`, `_last_user_message_text`, `_normalize_wrapup_candidate`, `_ended_on_wrapup_command` — read the Stop-event transcript, extract the last real owner message, normalize it, and match it against the tuple. `drain_decision()` gained a `transcript_path: str | None = None` parameter; the wrap-up check runs after the owner-decision deference and before the signature gate — on a match it records `last_result = "deferred_wrap_up_command"` and returns the empty allow-stop result. `main()` extracts `transcript_path` from the Stop payload and passes it. The check fails open: any problem (unset/missing transcript path, unreadable/unparseable transcript, no owner message found) leaves it inert and the existing gates proceed.
- **IP-3** — Updated `platform_tests/hooks/test_bridge_stop_drain.py`. The existing `test_stale_owner_decision_does_not_suppress_drain` (which encoded the recency-window behavior and referenced the removed `OWNER_DECISION_RECENCY_MINUTES`) was renamed to `test_stale_owner_decision_still_suppresses_drain` and inverted — a stale unresolved decision now suppresses. Added a `_write_transcript` fixture helper plus five wrap-up tests and one drift-guard test (`test_wrapup_command_set_matches_canonical`). The suite is now 21 tests.

## Implementation Notes

- IP-2's transcript reading mirrors the sibling Stop hook `.claude/hooks/owner-decision-tracker.py` (`_read_transcript_tail` + the real-user-event boundary detection): same JSONL event format, same skipping of tool_result-only continuations. The test fixtures use that same format, so the wrap-up tests exercise the real transcript shape, not an invented one.
- `_normalize_wrapup_candidate` implements exactly the documented tolerance: lowercase, collapse whitespace, strip final punctuation (`.` `!` `?`), and an optional leading or trailing "please". Mid-string punctuation (for example a comma before "please") is outside the documented tolerance and is not normalized — consistent with the GO'd `-003` IP-2 scope. During verification an over-aggressive test variant (`"session wrap-up, please"`) was corrected to the in-spec form (`"session wrap-up please"`); the implementation was not broadened.
- `OWNER_DECISION_RECENCY_MINUTES`, `_ASKED_AT_RE`, and the `timedelta` import became dead with the recency-window removal and were removed in the same edit.

## Files Changed

- `.claude/hooks/bridge-stop-drain.py` — IP-1 (recency-window removal in `_owner_decision_pending()`; dead-code cleanup) and IP-2 (the `WRAPUP_TRIGGER_COMMANDS` tuple, the four transcript/wrap-up helpers, the `drain_decision` `transcript_path` parameter and wrap-up check, and the `main()` payload extraction).
- `platform_tests/hooks/test_bridge_stop_drain.py` — IP-3 (the `_write_transcript` helper; the renamed/inverted stale-decision test; five wrap-up tests; the drift-guard test).

Working-tree note: both files are part of the WI-3359 autodrain deliverable, which is VERIFIED at `bridge/gtkb-bridge-active-session-autodrain-008.md` but **not yet committed** — they currently show as untracked in git, which is why `git diff --name-only HEAD` does not list them. The shared working tree is additionally entangled with ~25 tracked dirty files from parallel sessions. The WI-3363 implementation commit must be scoped to the `bridge-stop-drain.py` and `test_bridge_stop_drain.py` changes and coordinated with the pending WI-3359 commit; it must NOT bundle the unrelated parallel-session changes.

## Spec-To-Test Mapping

| Specification | Test / verification | Result |
| --- | --- | --- |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | `test_stale_owner_decision_still_suppresses_drain`, `test_owner_decision_deference_suppresses_drain`, `test_resolved_owner_decision_does_not_suppress_drain` — a pending owner decision of any age suppresses the drain; a resolved one does not. `test_wrapup_command_defers_drain` — a wrap-up turn-end defers. The drain yields to the owner instead of blocking turn-end. | PASS |
| GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 / PB-SESSION-WRAP-UP-PROACTIVE-001 / DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001 | `test_wrapup_command_defers_drain` (drain returns the empty allow-stop result on a wrap-up turn — yields to the owner-invoked wrap-up, non-mutating), `test_non_wrapup_message_does_not_defer_drain` (negative case), `test_wrapup_command_normalization_tolerance` (documented tolerance), `test_wrapup_check_skips_tool_result_continuation` (last real owner message), `test_wrapup_check_inert_when_transcript_absent` (fail-open). | PASS |
| IP-1 deference correctness | `test_stale_owner_decision_still_suppresses_drain` updated to assert a stale unresolved decision still suppresses; recent and resolved cases unchanged. | PASS |
| Wrap-up command-set integrity | `test_wrapup_command_set_matches_canonical` — the hook's local `WRAPUP_TRIGGER_COMMANDS` is byte-equal to `session_self_initialization.WRAPUP_TRIGGER_COMMANDS`. | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The 14 unchanged tests (role-aware actionability, signature gate, circuit breaker, heartbeat re-arm, shared detection surface, CLI surface, Stop-array registration) — the actionable-status reading, dispatch-state contract, and bounding gates are unchanged by IP-1/IP-2. | PASS (no regression) |
| GOV-RELIABILITY-FAST-LANE-001 | Fast-lane eligibility (four criteria) confirmed at the `-004` GO. | Confirmed |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the spec-to-test mapping plus the executed commands and observed results below. | — |

## Verification Commands And Observed Results

- `python -m py_compile .claude/hooks/bridge-stop-drain.py` — clean (IP-1 + IP-2 introduce no syntax error).
- `python -m py_compile platform_tests/hooks/test_bridge_stop_drain.py` — clean.
- `python -m pytest platform_tests/hooks/test_bridge_stop_drain.py -q` — `21 passed in 2.44s`. The suite is the 15 prior tests (one renamed: `test_stale_owner_decision_still_suppresses_drain`) plus 6 new IP-3 tests: `test_wrapup_command_defers_drain`, `test_non_wrapup_message_does_not_defer_drain`, `test_wrapup_command_normalization_tolerance`, `test_wrapup_check_skips_tool_result_continuation`, `test_wrapup_check_inert_when_transcript_absent`, `test_wrapup_command_set_matches_canonical`. The 14 unchanged tests pass — IP-1/IP-2 caused no regression.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the proposal (`-004`).
- [x] `_owner_decision_pending()` no longer applies a recency window; any unresolved owner decision suppresses the drain; resolved decisions do not — covered by `test_stale_owner_decision_still_suppresses_drain`, `test_owner_decision_deference_suppresses_drain`, `test_resolved_owner_decision_does_not_suppress_drain`.
- [x] `bridge-stop-drain.py` defers (returns the empty allow-stop result) when the turn's last owner message is a wrap-up command — covered by `test_wrapup_command_defers_drain` and four companion wrap-up tests.
- [x] The hook wrap-up command set is asserted byte-equal to `session_self_initialization.WRAPUP_TRIGGER_COMMANDS` by `test_wrapup_command_set_matches_canonical`.
- [x] No change to the cross-harness trigger, active-session suppression, signature scheme, circuit breaker, heartbeat re-arm, role resolution, or `compute_actionable_pending` — the 14 unchanged tests confirm it.
- [x] This post-implementation report carries the executed `pytest` command and observed results.
- [ ] Loyal Opposition returns VERIFIED.

## Recommended Commit Type

`fix:` — WI-3363 repairs a defect (the Stop-drain hook firing when its own contract requires deference). It adds no new capability surface: IP-1 removes an implementation-introduced narrowing, IP-2 honors existing session-lifecycle/wrap-up specifications, IP-3 is regression coverage. Consistent with the `-003` proposal's recommended type.

## Pre-Filing Preflight Subsection

The applicability preflight (`scripts/bridge_applicability_preflight.py`) and the ADR/DCL clause preflight (`scripts/adr_dcl_clause_preflight.py`) were run against this report content with `--content-file` before the live `NEW` `bridge/INDEX.md` entry was inserted. Observed results: the applicability preflight reported `preflight_passed: true` with `missing_required_specs: []` and `missing_advisory_specs: []` (6 specs matched, all cited); the clause preflight evaluated 5 clauses (4 `must_apply`, 1 `may_apply`) with 0 evidence gaps and 0 blocking gaps (gate exit 0).

## Loyal Opposition Asks

1. Confirm IP-1 removes the recency window such that any unresolved owner decision suppresses the drain regardless of age, with the resolved-decision skip and fail-open behavior preserved.
2. Confirm IP-2's wrap-up deference (transcript last-owner-message match against the local `WRAPUP_TRIGGER_COMMANDS` copy, with the drift-guard test, and fail-open on any transcript problem) correctly honors the session-lifecycle/wrap-up specifications.
3. Confirm the 21-test suite — 14 unchanged plus the IP-1 inversion and 6 new IP-2 tests — is sufficient spec-derived coverage for VERIFIED.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
