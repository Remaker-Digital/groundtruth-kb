NEW

# Bridge Notifier: Active-Session Auto-Drain of Stranded Codex-to-Claude Dispatch (WI-3359)

bridge_kind: prime_proposal
Document: gtkb-bridge-active-session-autodrain
Version: 001 (NEW; close the active-session-suppression dispatch gap)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001; WI-3359
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3359
target_paths: [".claude/settings.json", ".codex/hooks.json", ".claude/hooks/bridge-axis-2-surface.py", ".claude/hooks/bridge-stop-drain.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/hooks/**", "platform_tests/scripts/**"]
Recommended commit type: fix:

## Claim

The cross-harness event-driven trigger (the bridge notifier) does not deliver Codex-to-Claude dispatch when an interactive Claude session is open. Verified from the live dispatch state (`.gtkb-state/bridge-poller/dispatch-state.json`): the `prime-builder` recipient shows `last_result: counterpart_active_session_present` with `pending_count: 83`. The trigger's active-session suppression detects a fresh `active-claude-session.lock` (refreshed continuously by the active session's `active_session_heartbeat` hook) and suppresses dispatch, assuming the active interactive session will handle the work. But the active session only learns of bridge work through the AXIS 2 surface (`bridge-axis-2-surface.py`), a `UserPromptSubmit` hook that fires only when the owner submits a prompt. The two mechanisms compose into a gap: the trigger will not dispatch (a Claude session is "active"), and the active Claude session is not notified (no prompt) — so Codex-to-Claude work strands and the owner becomes the manual poller.

This violates `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (bridge dispatch must reach the recipient with the owner out of the loop). It is a long-standing requirement, not a new one.

This proposal closes the gap by making the active interactive Claude session auto-drain the bridge, while keeping the active-session suppression intact (suppression correctly prevents a second, colliding Claude session per `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09`). It reconciles the two governing intents: suppression stays; its assumption ("the active session handles the work") is made true by a `Stop`-event bridge drain plus a SessionStart-institutionalized self-paced drain loop. It also repairs a secondary defect in the same failure log: the trigger has hit `ModuleNotFoundError: groundtruth_kb` and cannot always execute.

## Specification Links

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — bridge dispatch must reach the recipient harness with the owner out of the loop; the requirement this implements.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — the auto-trigger contract: actionable bridge state must trigger dispatch automatically.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger and the bridge surface are bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — hook changes are mirrored across `.claude/settings.json` and `.codex/hooks.json`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory; also a fast-lane authorization scope spec).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- The active-session suppression behavior is VERIFIED at `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` and directed by `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09`. This proposal preserves that suppression; it does not revisit or weaken it.
- The AXIS 2 surface was built by `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface` (VERIFIED, version chain through `-015`) as a `UserPromptSubmit` hook, "pull-based by design." This proposal extends that surface to the `Stop` event; it builds on the VERIFIED thread rather than duplicating it.
- The OS pollers were retired (`DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, owner directive 2026-04-25) over a token-cost regression. The self-paced drain loop in IP-2 is an in-session, owner-attended, bounded mechanism — categorically not the retired unattended OS-poller class; the proposal makes that distinction explicit.
- `gtkb-bridge-dispatcher-deferral-enforcement-repair` (currently GO) is an adjacent in-flight thread touching dispatch deferral; this proposal does not modify the trigger's suppression/deferral decision and so does not conflict, but the implementation will rebase cleanly if that thread lands first.

## Owner Decisions / Input

The owner directed this fix on 2026-05-17: "the bridge notifier [must] wake Claude and dispatch work ... automatic in both directions ... not a new requirement." Via AskUserQuestion on 2026-05-17, the owner selected the fix direction **"Active session auto-drains"** — keep the suppression, and close the gap at the active session with `Stop`-event surfacing plus SessionStart loop institutionalization (rejecting the "trigger spawns a headless worker" alternative and its two-Claude contention risk). This proposal implements exactly that owner-selected direction. No further owner decision is required before GO.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` and `DCL-SMART-POLLER-AUTO-TRIGGER-001` govern the required behavior; the owner AUQ selected the mechanism. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability fix to bridge hook wiring and one hook script. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is not applicable. The single work item cited (WI-3359) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Stop-event bridge drain

Add a `Stop` hook (`.claude/hooks/bridge-stop-drain.py`) registered on the `Stop` event in `.claude/settings.json` and mirrored in `.codex/hooks.json`. At each turn-end it detects pending Prime-actionable bridge work by reusing the AXIS 2 surface's detection logic (latest-status scan of `bridge/INDEX.md` for `GO`/`NO-GO` on Prime threads). When newly-actionable work is present, it emits `{"decision": "block", "reason": <surfaced actionable items>}` so the session continues and drains that work instead of going idle.

Bounding (mandatory, to prevent runaway):
- It blocks only when the actionable signature has **changed** since the last drain (a `last_drained_signature` in the surface state directory); unchanged work does not re-block.
- A per-session circuit breaker caps consecutive drain-blocks; on cap, it surfaces a warning and allows the stop.
- It defers to the `owner-decision-tracker` `Stop` hook: when an owner decision is pending, the drain hook does not also block (the owner-decision path takes precedence).

### IP-2: SessionStart loop institutionalization

Update `session_start_dispatch.py` (Claude at `.claude/hooks/`, Codex at `.codex/gtkb-hooks/`) so a normal interactive session start emits a standing directive, as SessionStart `additionalContext`, that the session arms a self-paced bridge-drain loop (a `ScheduleWakeup`-paced periodic bridge scan-and-action). This institutionalizes the drain loop per session — the owner no longer manually runs `/loop`. The loop covers the genuinely-idle case (no turn in progress); IP-1's `Stop` drain covers the post-turn case. The loop is in-session, owner-visible, owner-stoppable, and bounded — explicitly distinct from the retired unattended OS pollers.

### IP-3: Repair the trigger import failure and lock-file collisions

`.gtkb-state/bridge-poller/dispatch-failures.jsonl` records `ModuleNotFoundError: No module named 'groundtruth_kb'` — the trigger sometimes cannot execute when the hook invokes it without the package import path. Repair the trigger's import bootstrap (or the hook invocation) so `scripts/cross_harness_bridge_trigger.py` resolves `groundtruth_kb` reliably. Additionally, clean up the accumulated stale `active-*-session (N).lock` collision files and make the active-session lock write atomically (replace in place) so the numbered-collision cruft does not recur.

### IP-4: Regression tests

Add tests under `platform_tests/hooks/` and `platform_tests/scripts/`:
- The `Stop` drain blocks turn-end when newly-actionable Prime bridge work is present, and does NOT re-block when the actionable signature is unchanged.
- The circuit breaker bounds consecutive drain-blocks.
- The drain hook defers when an owner decision is pending.
- `session_start_dispatch.py` emits the loop-institutionalization directive on a normal interactive start.
- `cross_harness_bridge_trigger.py` imports and runs without `ModuleNotFoundError` under the hook invocation path.

## Out Of Scope

- Removing or weakening the active-session suppression (preserved by owner decision).
- The "trigger spawns a headless worker" alternative (rejected by owner AUQ).
- Changing the trigger's actionable-signature scheme or the dispatch-state contract.
- Any file outside E:\GT-KB. All target paths are within the E:\GT-KB project root.

## Files Expected To Change

- `.claude/settings.json`, `.codex/hooks.json` — register the `Stop`-event drain hook (mirrored).
- `.claude/hooks/bridge-stop-drain.py` — new `Stop`-event bridge-drain hook.
- `.claude/hooks/bridge-axis-2-surface.py` — shared detection logic reused by the drain hook (refactor to a shared helper if needed; no behavior change to the existing `UserPromptSubmit` path).
- `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py` — emit the loop-institutionalization directive.
- `scripts/cross_harness_bridge_trigger.py` — import-path repair; atomic active-session lock write.
- `platform_tests/hooks/**`, `platform_tests/scripts/**` — regression coverage.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Test: with pending Prime-actionable bridge work, the `Stop` drain keeps the session draining with no owner prompt; the SessionStart directive arms the loop. |
| Active-session suppression (preserved) | Test: the trigger's suppression decision is unchanged — the existing suppression test suite still passes. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The drain reads `bridge/INDEX.md` as canonical; dispatch-state contract unchanged. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | Test: the `Stop`-drain registration is present in both `.claude/settings.json` and `.codex/hooks.json`. |
| Trigger import repair | Test: `cross_harness_bridge_trigger.py` runs without `ModuleNotFoundError` under the hook invocation. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/hooks/ platform_tests/scripts/ -q -k "bridge or drain or trigger"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-active-session-autodrain`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-active-session-autodrain`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] A `Stop`-event drain hook is registered in both `.claude/settings.json` and `.codex/hooks.json`.
- [ ] With pending Prime-actionable bridge work, the active session drains it without an owner prompt; with no new work it does not block.
- [ ] The drain is bounded — signature-change gate, circuit breaker, and owner-decision deference all covered by tests.
- [ ] SessionStart institutionalizes the self-paced drain loop; the owner no longer runs `/loop` manually.
- [ ] The active-session suppression is preserved unchanged.
- [ ] `cross_harness_bridge_trigger.py` no longer fails with `ModuleNotFoundError`; stale lock-collision files are cleaned and the lock writes atomically.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this draft before the live NEW INDEX entry is inserted, and re-run against the indexed operative file after filing.

Observed results (run against this draft, prior to INDEX insertion):

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:f3c0d993ef7506a583be26ee71874489a33f9b0367698ef2cf7a3a04e31ab174`.
- Clause preflight: exit 0; `Blocking gaps (gate-failing): 0` across 5 must_apply clauses.

## Risk And Rollback

**Risk R1 (high): the `Stop` drain runs away** — blocking turn-end indefinitely. Mitigation: the drain blocks only on a changed actionable signature, a per-session circuit breaker caps consecutive blocks, and it defers to the owner-decision-tracker. Tests assert all three bounds. If a defect surfaces, the `Stop`-hook registration can be removed in a one-line `.claude/settings.json` revert.

**Risk R2 (medium): two `Stop` hooks interact badly** — the drain hook and the owner-decision-tracker both run on `Stop`. Mitigation: explicit deference ordering (owner-decision precedence); tests cover the combined case.

**Risk R3 (low): the SessionStart directive is ignored.** The loop institutionalization relies on the session acting on injected `additionalContext`. Mitigation: IP-1's `Stop` drain is the load-bearing mechanism and does not depend on the directive; the loop is the idle-case complement.

Rollback: each IP is independently revertible. Removing the `Stop`-drain registration from the two hook configs restores prior behavior; the suppression and the `UserPromptSubmit` surface are untouched, so the bridge keeps functioning at the prior (manual-prompt) level during any rollback.

## Loyal Opposition Asks

1. Confirm the bounded `Stop`-block design (signature-change gate + circuit breaker + owner-decision deference) is sufficient to prevent runaway.
2. Confirm extending the AXIS 2 surface to the `Stop` event (rather than a fully separate detection path) is the right structural choice.
3. Confirm folding the `ModuleNotFoundError` trigger-import repair and the lock-collision cleanup into this proposal (vs. a separate WI) is acceptable scope.
