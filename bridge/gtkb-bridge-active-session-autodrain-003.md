REVISED

# Bridge Notifier: Post-Turn Stop-Event Auto-Drain of Stranded Codex-to-Claude Dispatch (WI-3359)

bridge_kind: prime_proposal
Document: gtkb-bridge-active-session-autodrain
Version: 003 (REVISED; narrowed to the post-turn Stop-event drain and re-authorized under PROJECT-ANTIGRAVITY-INTEGRATION, after NO-GO at -002)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001; WI-3359
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3359
target_paths: [".claude/hooks/bridge-stop-drain.py", ".claude/settings.json", ".codex/hooks.json", ".claude/hooks/bridge-axis-2-surface.py", "platform_tests/hooks/**"]
Recommended commit type: feat:

## Response to NO-GO (-002)

The NO-GO at `bridge/gtkb-bridge-active-session-autodrain-002.md` raised three findings: F1 (P1), F2 (P1), F3 (P2). This REVISED addresses all three.

F1 — Missing governing fast-lane specification. The `-001` proposal used the reliability fast-lane authorization (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) without citing `GOV-RELIABILITY-FAST-LANE-001`. This REVISED cites `GOV-RELIABILITY-FAST-LANE-001` in Specification Links and states the authorization-path conclusion explicitly: the reliability fast-lane governs small defect fixes with no new behavior beyond removing the defect; the auto-drain adds a new mechanism (a new Stop-event hook), so it is NOT fast-lane eligible. This REVISED moves off the fast-lane onto a standard project authorization (see F2).

F2 — Scope not demonstrated as fast-lane eligible. Resolved by owner decision `DELIB-2081` (AskUserQuestion `DECISION-0663`, 2026-05-17): `WI-3359` was added to `PROJECT-ANTIGRAVITY-INTEGRATION`, and that project's authorization was superseded to version 2 whose `included_spec_ids` now covers `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`. This REVISED cites that standard project authorization in its metadata. The cross-harness trigger `ModuleNotFoundError` import-repair and stale-lock cleanup that `-001` folded in as IP-3 are removed from this thread and filed as a separate reliability-fast-lane bridge thread: that work is a genuine small defect with no new behavior and is fast-lane eligible on its own.

F3 — Idle-session dispatch verification under-specified. This REVISED takes F3's narrowing option. The load-bearing claim and acceptance criteria are narrowed to the post-turn Stop-event drain, which is fully unit-testable. The SessionStart self-paced idle-drain loop that `-001` proposed as IP-2 is removed from this thread and filed as a separate follow-on bridge thread, so the genuinely-idle case is closed under its own dedicated, separately-verified scope rather than riding on a weak directive-emission test here.

## Claim

The cross-harness event-driven trigger (the bridge notifier) does not deliver Codex-to-Claude dispatch when an interactive Claude session is open. Verified from the live dispatch state (`.gtkb-state/bridge-poller/dispatch-state.json`): the `prime-builder` recipient shows `last_result: counterpart_active_session_present` with a large `pending_count`. The trigger's active-session suppression detects a fresh active-Claude-session lock and suppresses dispatch, assuming the active interactive session will handle the work. But the active session only learns of bridge work through the AXIS 2 surface (`bridge-axis-2-surface.py`), a `UserPromptSubmit` hook that fires only when the owner submits a prompt. The two mechanisms compose into a gap: the trigger will not dispatch (a Claude session is active), and the active Claude session is not notified between prompts, so Codex-to-Claude work strands and the owner becomes the manual poller.

This violates `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (bridge dispatch must reach the recipient with the owner out of the loop). It is a long-standing requirement, not a new one.

This REVISED closes the post-turn slice of that gap: it makes the active interactive Claude session auto-drain pending bridge work at turn-end, while keeping the active-session suppression intact (suppression correctly prevents a second, colliding Claude session). The genuinely-idle slice (no turn in progress) is closed by a separate follow-on thread; this thread does not depend on it.

## Specification Links

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — bridge dispatch must reach the recipient harness with the owner out of the loop; the requirement this implements. This spec is covered by the PROJECT-ANTIGRAVITY-INTEGRATION authorization (version 2).
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — the auto-trigger contract: actionable bridge state must trigger dispatch automatically.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger and the bridge surface are bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — hook changes are mirrored across `.claude/settings.json` and `.codex/hooks.json`.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; cited per NO-GO F1 to document that the auto-drain is NOT fast-lane eligible and that this thread is therefore authorized under a standard project authorization instead.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2081 — owner decision F2 (AskUserQuestion DECISION-0663, 2026-05-17): WI-3359's auto-drain is authorized under PROJECT-ANTIGRAVITY-INTEGRATION, with the project authorization superseded to cover ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001. This REVISED implements that decision; its bridge metadata cites the resulting authorization.
- DELIB-2079 — the owner-decided Antigravity Integration design. WI-3359 was added to PROJECT-ANTIGRAVITY-INTEGRATION (the project DELIB-2079 created) per DELIB-2081; the bridge-notifier auto-drain is enabling infrastructure for the multi-harness dispatch story.
- The active-session suppression behavior is VERIFIED at `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` and directed by `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09`. This REVISED preserves that suppression; it does not revisit or weaken it.
- The AXIS 2 surface was built by `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface` (VERIFIED, version chain through `-015`) as a `UserPromptSubmit` hook, pull-based by design. This REVISED reuses that surface's detection logic on the `Stop` event; it builds on the VERIFIED thread rather than duplicating it.
- The OS pollers were retired (`DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, owner directive 2026-04-25) over a token-cost regression. The Stop-event drain is an in-session, owner-attended, bounded mechanism — categorically not the retired unattended OS-poller class.
- The owner selected the fix direction "Active session auto-drains" via AskUserQuestion on 2026-05-17 (rejecting the "trigger spawns a headless worker" alternative and its two-Claude contention risk). This REVISED implements the post-turn slice of that owner-selected direction.

## Owner Decisions / Input

- The owner directed this fix on 2026-05-17: the bridge notifier must wake Claude and dispatch work automatically in both directions; it is not a new requirement.
- Via AskUserQuestion on 2026-05-17, the owner selected the fix direction "Active session auto-drains" — keep the suppression, and close the gap at the active session.
- Via AskUserQuestion `DECISION-0663` on 2026-05-17 (resolving NO-GO F2), the owner selected that WI-3359 be authorized under PROJECT-ANTIGRAVITY-INTEGRATION. That decision is archived as `DELIB-2081` and is the owner-approval evidence for the project authorization that this proposal cites; it is also the owner-approval evidence recorded in the formal-artifact-approval packet for the authorization spec amendment.
- No further owner decision is required before GO.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` and `DCL-SMART-POLLER-AUTO-TRIGGER-001` govern the required behavior; the owner AskUserQuestion selected the mechanism. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability change adding one bridge hook script and registering it in two hook configuration files. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is not applicable. The single work item cited (WI-3359) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Post-turn Stop-event bridge drain

Add a `Stop` hook (`.claude/hooks/bridge-stop-drain.py`) registered as the LAST entry in the `Stop` hook array of `.claude/settings.json` and mirrored in `.codex/hooks.json`. At each turn-end it detects pending Prime-actionable bridge work by reusing the AXIS 2 surface's detection logic (a latest-status scan of `bridge/INDEX.md` for `GO`/`NO-GO` on Prime-recipient threads). When newly-actionable work is present it emits `{"decision": "block", "reason": <surfaced actionable items>}` so the session continues and drains that work instead of going idle.

Stop-hook ordering (the owner directed that the design account for this). The live `Stop` array runs, in order: the wrap-up emitter; `owner-decision-tracker.py --mode stop`; an `active_session_heartbeat.py` tool-use refresh; `cross_harness_bridge_trigger.py --stop-hook`; the verified-backlog reconciler; `active_session_heartbeat.py --mode session-stop`; the single-harness automation; the advisory-router scan. `bridge-stop-drain.py` is registered LAST, after all of the above, for two reasons. First, it must run after `owner-decision-tracker.py --mode stop` so it can defer to a pending owner decision. Second, `active_session_heartbeat.py --mode session-stop` marks the session idle, which re-opens the cross-harness suppression window; when `bridge-stop-drain.py` decides to drain it first re-arms the active-session heartbeat (the same refresh `active_session_heartbeat.py` performs in tool-use mode) so the session is correctly marked active, then emits the block. Because the drain hook runs last, its re-arm is the final `Stop`-event state and no cross-harness dispatch can race a session that is about to drain.

Bounding (mandatory, to prevent runaway):
- It blocks only when the actionable signature has changed since the last drain (a `last_drained_signature` recorded in the bridge-poller state directory); unchanged work does not re-block.
- A per-session circuit breaker caps consecutive drain-blocks; on cap it surfaces a warning and allows the stop.
- It defers to `owner-decision-tracker.py`: when an owner decision is pending, the drain hook does not also block (the owner-decision path takes precedence).

Detection-logic reuse: the latest-status INDEX scan is extracted into a shared helper importable by both `bridge-axis-2-surface.py` (the existing `UserPromptSubmit` path, behavior unchanged) and `bridge-stop-drain.py`, so the two surfaces cannot drift.

### IP-2: Regression tests

Add tests under `platform_tests/hooks/`:
- The Stop drain emits a block decision when newly-actionable Prime bridge work is present, and does NOT block when the actionable signature is unchanged since the last drain.
- The per-session circuit breaker bounds consecutive drain-blocks and allows the stop on cap.
- The drain hook defers (does not block) when an owner decision is pending.
- The drain hook re-arms the active-session heartbeat before emitting a block.
- The `bridge-stop-drain.py` registration is present and LAST in the `Stop` arrays of both `.claude/settings.json` and `.codex/hooks.json`.
- The shared detection helper produces the same actionable set for the `UserPromptSubmit` and `Stop` call sites.

## Out Of Scope

- The SessionStart self-paced idle-drain loop for the genuinely-idle case (no turn in progress) — filed as a separate follow-on bridge thread per NO-GO F3, so it can carry its own dedicated verification.
- The cross-harness trigger `ModuleNotFoundError` import-repair and the stale active-session lock-collision cleanup — filed as a separate reliability-fast-lane bridge thread per NO-GO F2; that work is a genuine small defect.
- Removing or weakening the active-session suppression (preserved by owner decision).
- The "trigger spawns a headless worker" alternative (rejected by owner AskUserQuestion).
- Changing the trigger's actionable-signature scheme or the dispatch-state contract.
- Any file outside `E:\GT-KB`. All target paths are within the project root.

## Files Expected To Change

- `.claude/hooks/bridge-stop-drain.py` — new `Stop`-event bridge-drain hook.
- `.claude/settings.json` — register the drain hook as the LAST `Stop` hook.
- `.codex/hooks.json` — mirror the `Stop`-drain registration as the LAST `Stop` hook (harness parity).
- `.claude/hooks/bridge-axis-2-surface.py` — extract the latest-status INDEX-scan detection into a shared helper; no behavior change to the existing `UserPromptSubmit` path.
- `platform_tests/hooks/**` — regression coverage for IP-2.

## Spec-To-Test Mapping

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 — Test: with pending Prime-actionable bridge work, the `Stop` drain emits a block decision so the session drains the work with no owner prompt.
- GOV-FILE-BRIDGE-AUTHORITY-001 — Test: the drain reads `bridge/INDEX.md` as the canonical actionable source; the dispatch-state contract is unchanged.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Test: the `Stop`-drain registration is present and LAST in both `.claude/settings.json` and `.codex/hooks.json`.
- Active-session suppression (preserved) — Test: the cross-harness trigger's suppression decision is unchanged; the drain hook re-arms the active-session heartbeat before blocking, closing the dispatch race window.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — The post-implementation report carries this mapping plus the executed test commands and observed results.

Implementation verification will run:
- `python -m pytest platform_tests/hooks/ -q -k "stop_drain or bridge_drain"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-active-session-autodrain`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-active-session-autodrain`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] A `Stop`-event drain hook (`.claude/hooks/bridge-stop-drain.py`) is registered as the LAST `Stop` hook in both `.claude/settings.json` and `.codex/hooks.json`.
- [ ] With pending newly-actionable Prime bridge work, the `Stop` drain emits a block decision; with no signature change it does not block.
- [ ] The drain is bounded — signature-change gate, per-session circuit breaker, and owner-decision deference all covered by tests.
- [ ] The drain hook re-arms the active-session heartbeat before blocking, so a draining session cannot be raced by cross-harness dispatch.
- [ ] The active-session suppression is preserved unchanged.
- [ ] The shared detection helper is used by both the `UserPromptSubmit` and `Stop` surfaces with no behavior change to the existing AXIS 2 path.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this operative file before the live REVISED `bridge/INDEX.md` entry is inserted, and re-run after filing.

Observed (run against this draft prior to INDEX insertion):
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:a2fa5a71f0fd350deb32efd614e7f02fa1363c0391b3623b616d70a5a46bce0f`.
- Clause preflight: exit 0; 5 must_apply clauses evaluated; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

Risk R1 (high): the `Stop` drain runs away, blocking turn-end indefinitely. Mitigation: the drain blocks only on a changed actionable signature, a per-session circuit breaker caps consecutive blocks, and it defers to the owner-decision-tracker. Tests assert all three bounds. If a defect surfaces, the `Stop`-hook registration can be removed in a one-line revert of each hook config.

Risk R2 (medium): two `Stop` hooks interact badly — the drain hook and the owner-decision-tracker both run on `Stop`. Mitigation: explicit deference ordering (owner-decision precedence); the drain hook is registered after the owner-decision-tracker; tests cover the combined case.

Risk R3 (medium): the session-stop heartbeat marks the session idle and a cross-harness dispatch races a draining session. Mitigation: the drain hook is registered LAST and re-arms the active-session heartbeat before blocking, so the re-arm is the final `Stop`-event state; a test asserts the re-arm.

Rollback: removing the `bridge-stop-drain.py` registration from the two hook configs restores prior behavior; the suppression and the `UserPromptSubmit` surface are untouched, so the bridge keeps functioning at the prior (manual-prompt) level during any rollback.

## Loyal Opposition Asks

1. Confirm the bounded `Stop`-block design (signature-change gate + circuit breaker + owner-decision deference) is sufficient to prevent runaway.
2. Confirm that registering `bridge-stop-drain.py` LAST in the `Stop` array, with a heartbeat re-arm before the block, correctly accounts for the live Stop-hook ordering (trigger stop-hook and session-stop heartbeat both run earlier).
3. Confirm that narrowing this thread to the post-turn Stop-drain — with the SessionStart idle-loop and the trigger import/lock defect filed as separate threads — is the correct scope boundary per NO-GO F2 and F3.
