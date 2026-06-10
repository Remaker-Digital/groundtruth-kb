NEW

# Repair bridge-stop-drain Deference Gaps: Owner-Decision Recency Window and Missing Wrap-Up-Command Deference (WI-3363)

bridge_kind: prime_proposal
Document: gtkb-bridge-stop-drain-deference-repair
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001; WI-3363
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3363
target_paths: [".claude/hooks/bridge-stop-drain.py", "platform_tests/hooks/**"]
Recommended commit type: fix:

## Claim

`.claude/hooks/bridge-stop-drain.py` — the role-aware Stop-event bridge active-session auto-drain (WI-3359, VERIFIED at `bridge/gtkb-bridge-active-session-autodrain-008.md`) — emits its drain-block in two situations where its own contract requires it to defer. The hook's stated purpose is to drain newly-actionable bridge work when the session would otherwise go idle; it must not block turn-end when the owner is mid-decision or deliberately ending the session.

**Gap 1 — owner-decision deference is silently scoped by a recency window.** `_owner_decision_pending()` counts an unresolved owner decision as pending only when it was asked within `OWNER_DECISION_RECENCY_MINUTES` (30). An unresolved decision older than 30 minutes is treated as not-pending, so the drain fires over it. Observed 2026-05-17: DECISION-0665 (asked `2026-05-17T20:48:52Z`) was unresolved when the drain hook fired at session start (~`21:56Z`) — roughly 67 minutes old, outside the window — and the hook blocked turn-end despite the pending decision. The approved `-005` proposal (`bridge/gtkb-bridge-active-session-autodrain-005.md`, IP-1 bounding) specified the deference unqualified: deference applies when an owner decision is pending. The 30-minute window was introduced during implementation and narrows that specified behavior.

**Gap 2 — no wrap-up-command deference.** `bridge-stop-drain.py` has no awareness of owner wrap-up commands. When the owner ends a turn with a wrap-up command (the `WRAPUP_TRIGGER_COMMANDS` set in `scripts/session_self_initialization.py`: "wrap up", "wrap up this session", "session wrap-up", and the rest), the owner is deliberately ending the session — definitionally not going idle. The drain hook nonetheless evaluates and can block turn-end, interrupting wrap-up.

This proposal repairs both gaps in `bridge-stop-drain.py` so the hook defers (returns the empty allow-stop result) when an owner decision is pending regardless of its age, and when the turn ended on a wrap-up command. It is a small single-concern defect fix to one hook file plus its regression suite, filed under the reliability fast lane per the owner's 2026-05-17 framing decision.

## Specification Links

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — the drain exists to keep the owner out of the loop for dispatchable bridge work; deferring when the owner is mid-decision or wrapping up is part of correctly honoring this ADR, not a contradiction of it.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — the auto-trigger contract; the drain is the active-session arm of it. The deference fix does not change when actionable work triggers a drain, only when the drain must yield to the owner.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge-stop-drain.py` is bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state; the deference fix does not alter the actionable-status reading.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation across proposal, deliberation, and report (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions toward verified (advisory).

## Fast-Lane Eligibility

This thread claims eligibility under `GOV-RELIABILITY-FAST-LANE-001` and the standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers-by-membership: WI-3363 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`). The four eligibility criteria:

1. **Origin defect** — met. WI-3363 has `origin=defect`. Both gaps are `bridge-stop-drain.py` emitting a drain-block where its own contract requires deference.
2. **No new API/CLI/behavior beyond removing the defect** — met. Gap 1: removing the recency window restores the behavior the approved `-005` proposal specified (deference when an owner decision is pending, unqualified); it removes an implementation-introduced narrowing. Gap 2: a wrap-up command means the owner is deliberately ending the session, definitionally outside the hook's drain-instead-of-going-idle purpose; the wrap-up check removes a misfire, it does not add a capability. The hook surface — its `Stop` registration, `--harness` argument, stdin/stdout contract, and exit code — is unchanged.
3. **No new requirement** — met. `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` and the `-005` design deference intent already govern; the owner 2026-05-17 directive clarifies the existing deference requirement rather than creating a new one. No new GOV/SPEC/PB/ADR/DCL artifact is created.
4. **Small single-concern scope** — met. One concern: the drain hook deference gating. One source file (`.claude/hooks/bridge-stop-drain.py`) plus its existing regression suite; no cross-cutting change.

## Prior Deliberations

- `bridge/gtkb-bridge-active-session-autodrain-001.md` through `-008.md` — the parent autodrain thread. `-005` (REVISED) IP-1 specified the owner-decision deference unqualified; `-007` (post-implementation report) disclosed the implemented `OWNER_DECISION_RECENCY_MINUTES` 30-minute window; `-008` recorded VERIFIED. This proposal repairs the gap between the `-005` specified intent and the `-007` implemented behavior, and adds the wrap-up-command deference the autodrain thread did not scope.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — the owner decision establishing `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and `GOV-RELIABILITY-FAST-LANE-001`. This proposal is filed under that standing authorization.
- `DELIB-2081` — owner decision authorizing WI-3359's auto-drain under `PROJECT-ANTIGRAVITY-INTEGRATION`; context for why the autodrain hook exists. This follow-up is a separate reliability-fast-lane work item (WI-3363), not a reopening of WI-3359.
- The owner-decision-tracker Stop-mode hook and the proactive wrap-up emitter (`session_self_initialization.py --emit-wrapup`) are sibling Stop-array hooks. This proposal coordinates `bridge-stop-drain.py` deference with the owner-decision and wrap-up signals but does not modify those hooks.

## Owner Decisions / Input

- 2026-05-17 owner directive (item 3): the owner reported that `bridge-stop-drain.py` fired on a wrap-up command and with an answered-but-unresolved owner decision pending, directed that the hook should defer to both, and instructed Prime Builder to scope this follow-up bridge thread for the deference gap.
- 2026-05-17 via AskUserQuestion the owner chose the reliability fast-lane framing for this thread: a new work item (WI-3363) under `PROJECT-GTKB-RELIABILITY-FIXES`, covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` through active project membership.
- No further owner decision is required before GO. This is a reliability-fast-lane defect fix covered by the standing project authorization; no formal-artifact-approval packet and no new owner decision are required.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` and the approved `-005` proposal deference design govern the required behavior; the owner 2026-05-17 directive clarifies the existing deference requirement. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix to one hook file plus regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3363) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Defer to a pending owner decision regardless of age

In `_owner_decision_pending()`, remove the `OWNER_DECISION_RECENCY_MINUTES` window so that any unresolved owner decision (a `memory/pending-owner-decisions.md` block whose `status` is not `resolved`) suppresses the drain regardless of its `asked_at` age. The `status == "resolved"` skip is preserved (a resolved decision does not suppress). The function continues to fail open (return `False`) when `memory/pending-owner-decisions.md` is absent or unparseable. `OWNER_DECISION_RECENCY_MINUTES` and the `asked_at` cutoff arithmetic are removed; `asked_at` parsing is retained only if used for diagnostics, not for gating.

Tradeoff (stated for Loyal Opposition): with the window removed, a stale unresolved decision suppresses the drain until the owner resolves it. This is the intended behavior — an unresolved owner decision is itself a signal not to autonomously drain bridge work, and the owner clears it deterministically via `resolve DECISION-NNNN`, `defer all`, or `clear pending` (the actions the startup disclosure documents). The `-005` design specified deference when an owner decision is pending with no age qualifier.

### IP-2: Defer when the turn ended on a wrap-up command

Add a wrap-up-command check to the drain decision. The `Stop` event payload on stdin carries `transcript_path`; the hook reads the transcript, extracts the last user message, normalizes it (strip surrounding whitespace; tolerate a leading/trailing "please" and trailing punctuation, matching the tolerance the startup disclosure documents for wrap-up commands), and compares it against the wrap-up command set. On a match, the drain returns the empty allow-stop result (defer). The wrap-up check fails open: if the transcript is absent or unparseable, the check does not fire and the hook proceeds with its existing gates — no worse than current behavior. The wrap-up check is evaluated before the signature-change gate so a deferral does not consume the actionable signature (matching the existing owner-decision deference placement).

The wrap-up command set: `bridge-stop-drain.py` carries a module-level `WRAPUP_TRIGGER_COMMANDS` constant. To avoid importing the large (~6600-line) `scripts/session_self_initialization.py` startup module into a hook that runs on every turn-end, the hook keeps its own copy of the small, stable command tuple; IP-3 adds a drift-guard test that imports `session_self_initialization.WRAPUP_TRIGGER_COMMANDS` (in the test process, where import cost is irrelevant) and asserts byte-equality, so the copy cannot silently diverge from the canonical set. This mirrors the autodrain thread's own no-drift test pattern.

### IP-3: Regression tests

Update `platform_tests/hooks/test_bridge_stop_drain.py`:
- IP-1: the existing `test_stale_owner_decision_does_not_suppress_drain` encodes the recency-window behavior being removed; it is updated to assert that a stale (asked more than 30 minutes ago) unresolved owner decision still suppresses the drain. `test_owner_decision_deference_suppresses_drain` (recent decision) and `test_resolved_owner_decision_does_not_suppress_drain` (resolved decision) continue to hold unchanged.
- IP-2: new tests — a turn whose transcript last user message is a wrap-up command causes the drain to defer; a non-wrap-up last message does not; multiple `WRAPUP_TRIGGER_COMMANDS` variants and the documented normalization tolerance (leading/trailing "please", trailing punctuation) are covered; an absent or unparseable transcript leaves the wrap-up check inert (the hook proceeds with its other gates).
- A drift-guard test imports `session_self_initialization.WRAPUP_TRIGGER_COMMANDS` and asserts the hook local copy is byte-equal (single-source-of-truth guard).

## Out Of Scope

- Any change to the cross-harness trigger, the active-session suppression, the dispatch-state contract, the signature scheme, the circuit breaker, or the heartbeat re-arm — all preserved unchanged.
- Any change to the role-resolution path, the actionable-status selection, or `compute_actionable_pending`.
- Any change to `scripts/session_self_initialization.py` — IP-2 keeps a local command-tuple copy and a drift-guard test; the wrap-up emitter and the canonical command set are not modified.
- Any change to `owner-decision-tracker.py` or the `memory/pending-owner-decisions.md` format.
- The SessionStart idle-drain loop (a separate owner-deferred thread).
- Any file outside `E:\GT-KB`. All target paths are within the project root.

## Files Expected To Change

- `.claude/hooks/bridge-stop-drain.py` — IP-1 (remove the recency window in `_owner_decision_pending()`) and IP-2 (add the wrap-up-command deference check and the local `WRAPUP_TRIGGER_COMMANDS` constant).
- `platform_tests/hooks/test_bridge_stop_drain.py` — IP-3 (update the stale-decision test; add wrap-up-deference tests; add the drift-guard test). Covered by the `platform_tests/hooks/**` target glob.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Tests: a pending owner decision of any age suppresses the drain; a wrap-up-command turn defers the drain — the hook yields to the owner instead of blocking turn-end. |
| IP-1 deference correctness | Test: `test_stale_owner_decision_does_not_suppress_drain` updated to assert a stale unresolved decision still suppresses; recent and resolved cases unchanged. |
| IP-2 wrap-up deference | Tests: wrap-up-command last message defers; non-wrap-up does not; normalization tolerance covered; absent transcript leaves the check inert. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The hook reading of `bridge/INDEX.md` actionable state is unchanged; no regression in the actionable-detection path. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed `pytest` command and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/hooks/test_bridge_stop_drain.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-stop-drain-deference-repair`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-stop-drain-deference-repair`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `_owner_decision_pending()` no longer applies a recency window; any unresolved owner decision suppresses the drain; resolved decisions do not; covered by tests.
- [ ] `bridge-stop-drain.py` defers (returns the empty allow-stop result) when the turn last user message is a wrap-up command; covered by tests.
- [ ] The hook wrap-up command set is asserted byte-equal to `session_self_initialization.WRAPUP_TRIGGER_COMMANDS` by a drift-guard test.
- [ ] No change to the cross-harness trigger, active-session suppression, signature scheme, circuit breaker, heartbeat re-arm, role resolution, or `compute_actionable_pending`.
- [ ] Post-implementation report carries the executed `pytest` command and observed results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight (`scripts/bridge_applicability_preflight.py`) and the ADR/DCL clause preflight (`scripts/adr_dcl_clause_preflight.py`) are run against this proposal content with `--content-file` before the live `NEW` `bridge/INDEX.md` entry is inserted. A non-empty `missing_required_specs` or `missing_advisory_specs` list, or a blocking clause gap, is a self-detected defect corrected before filing. Observed results (run against this `-001` draft content prior to filing): the applicability preflight reported `preflight_passed: true` with `missing_required_specs: []` and `missing_advisory_specs: []` (6 specs matched, all cited); the clause preflight evaluated 5 `must_apply` clauses with 0 evidence gaps and 0 blocking gaps (gate exit 0).

## Risk And Rollback

**Risk R1 (low): removing the recency window lets a stale unresolved decision suppress the drain indefinitely.** This is the intended behavior (see IP-1 tradeoff): an unresolved owner decision is a deliberate do-not-autonomously-drain state, and the owner clears it via `resolve` / `defer all` / `clear pending`. The drain resumes automatically once the decision is resolved.

**Risk R2 (low): the wrap-up-command match misfires.** Mitigation: the match uses the wrap-up command set with the documented normalization tolerance; tests cover variants and the negative case. A false negative degrades to current behavior (the drain still fires); a false positive defers one turn-end, which the next non-wrap-up turn corrects.

**Risk R3 (low): the transcript read fails or the Stop payload lacks `transcript_path`.** Mitigation: the wrap-up check fails open — it does not fire — and the hook proceeds with its existing gates, identical to current behavior.

Rollback: reverting `.claude/hooks/bridge-stop-drain.py` to its prior version restores prior behavior. The change is confined to one file plus its test file; each IP is independently revertible.

## Loyal Opposition Asks

1. Confirm the fast-lane eligibility claim — that removing the recency window (restoring the `-005`-specified behavior) and adding wrap-up-command deference (removing a misfire outside the hook drain-instead-of-going-idle purpose) add no new behavior or requirement.
2. Confirm IP-2's choice — a local `WRAPUP_TRIGGER_COMMANDS` copy in the hook plus a drift-guard test — over importing the large `session_self_initialization` module into a per-turn-end hook.
3. Confirm the IP-1 tradeoff (a stale unresolved decision suppresses the drain until resolved) is the intended deference semantics.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
