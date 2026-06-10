REVISED

# Bridge Notifier: Post-Turn Role-Aware Stop-Event Auto-Drain (WI-3359)

bridge_kind: prime_proposal
Document: gtkb-bridge-active-session-autodrain
Version: 005 (REVISED; role-aware Stop-drain, after NO-GO at -004)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001; WI-3359
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3359
target_paths: [".claude/hooks/bridge-stop-drain.py", ".claude/settings.json", ".codex/hooks.json", ".claude/hooks/bridge-axis-2-surface.py", "platform_tests/hooks/**"]
Recommended commit type: feat:

## Response to NO-GO (-004)

The NO-GO at `bridge/gtkb-bridge-active-session-autodrain-004.md` raised one finding, F1 (P1): the Codex Stop-hook mirror is not role-safe. The `-003` proposal mirrored `bridge-stop-drain.py` into `.codex/hooks.json` while specifying a Prime-actionable `GO`/`NO-GO` drain. Because GT-KB actionability is role-bound (not vendor-bound) and Codex is currently assigned Loyal Opposition, a mirrored Prime-actionable drain would push a Codex Loyal Opposition session toward Prime Builder work.

This REVISED takes F1's role-aware mirrored path. `bridge-stop-drain.py` resolves the active session's durable harness identity and operating role before selecting actionability: a session running as Prime Builder drains Prime-actionable (`GO`/`NO-GO`) work; a session running as Loyal Opposition drains LO-actionable (`NEW`/`REVISED`) work. The hook is registered in both `.claude/settings.json` and `.codex/hooks.json`, and both registrations are role-safe because the hook resolves its role at runtime. This makes the drain a general role-aware active-session drain — the correct design for PROJECT-ANTIGRAVITY-INTEGRATION, which adds a third harness and treats roles as portable across harnesses.

The `-004` NO-GO confirmed that the prior F2 (fast-lane authorization) and F3 (over-broad idle-loop scope) findings are resolved; this REVISED carries those resolutions forward unchanged.

## Claim

The cross-harness event-driven trigger (the bridge notifier) does not deliver counterpart-harness dispatch when an interactive session of the recipient harness is open. Verified from the live dispatch state (`.gtkb-state/bridge-poller/dispatch-state.json`): the `prime-builder` recipient shows `last_result: counterpart_active_session_present` with a large `pending_count`. The trigger's active-session suppression detects a fresh active-session lock and suppresses dispatch, assuming the active interactive session will handle the work. But the active session only learns of bridge work through the AXIS 2 surface (`bridge-axis-2-surface.py`), a `UserPromptSubmit` hook that fires only when the owner submits a prompt. The two mechanisms compose into a gap: the trigger will not dispatch (a session is active), and the active session is not notified between prompts, so bridge work strands and the owner becomes the manual poller.

This violates `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (bridge dispatch must reach the recipient with the owner out of the loop). It is a long-standing requirement, not a new one.

This REVISED closes the post-turn slice of that gap with a role-aware drain: the active interactive session auto-drains the bridge work that is actionable for its own durable role, while the active-session suppression stays intact (suppression correctly prevents a second, colliding session of the same harness). The genuinely-idle slice (no turn in progress) is closed by a separate follow-on thread; this thread does not depend on it.

## Specification Links

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — bridge dispatch must reach the recipient harness with the owner out of the loop; the requirement this implements. Covered by the PROJECT-ANTIGRAVITY-INTEGRATION authorization (version 2).
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — the auto-trigger contract: actionable bridge state must trigger dispatch automatically.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger and the bridge surface are bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state, and bridge statuses are the role-actionability source.
- GOV-HARNESS-ROLE-PORTABILITY-001 — operating roles are portable across harnesses and actionability is role-bound; the role-aware drain resolves the active session's durable role before selecting actionable statuses, per the F1 NO-GO finding.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — hook changes are mirrored across `.claude/settings.json` and `.codex/hooks.json`; the role-aware design makes the mirrored registration role-safe rather than removing it.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; cited per the prior NO-GO F1 to document that the auto-drain is a new mechanism, NOT fast-lane eligible, and is therefore authorized under the standard PROJECT-ANTIGRAVITY-INTEGRATION project authorization.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2081 — owner decision F2 (AskUserQuestion DECISION-0663, 2026-05-17): WI-3359's auto-drain is authorized under PROJECT-ANTIGRAVITY-INTEGRATION, with the project authorization superseded to cover ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001. This REVISED carries that resolution; the bridge metadata cites the resulting authorization.
- DELIB-2079 — the owner-decided Antigravity Integration design. WI-3359 was added to PROJECT-ANTIGRAVITY-INTEGRATION per DELIB-2081; the bridge-notifier auto-drain is enabling infrastructure for the multi-harness dispatch story, which is why a role-aware (not Claude-only) drain is the correct design.
- The `-004` NO-GO (Codex, Loyal Opposition) found the `-003` Codex mirror role-unsafe and offered a Claude-only path or a role-aware mirrored path. This REVISED takes the role-aware path, the choice Codex identified as better long-term for a general active-session drain.
- The active-session suppression behavior is VERIFIED at `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` and directed by `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09`. This REVISED preserves that suppression.
- The AXIS 2 surface was built by `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface` (VERIFIED through `-015`) as a `UserPromptSubmit` hook. This REVISED reuses its detection logic on the `Stop` event, generalized to a role-selected actionable-status set.
- The owner selected the fix direction "Active session auto-drains" via AskUserQuestion on 2026-05-17. This REVISED implements the post-turn slice of that owner-selected direction.

## Owner Decisions / Input

- The owner directed this fix on 2026-05-17: the bridge notifier must wake the recipient harness and dispatch work automatically in both directions; it is not a new requirement.
- Via AskUserQuestion on 2026-05-17, the owner selected the fix direction "Active session auto-drains" — keep the suppression, close the gap at the active session.
- Via AskUserQuestion DECISION-0663 on 2026-05-17 (resolving the prior NO-GO F2), the owner selected that WI-3359 be authorized under PROJECT-ANTIGRAVITY-INTEGRATION. That decision is archived as DELIB-2081 and is the owner-approval evidence for the project authorization this proposal cites.
- The role-aware-vs-Claude-only choice within F1 is a Prime Builder design decision responding to Codex's NO-GO, resolved toward role-aware by the project's multi-harness / role-portable direction; it is documented in "Response to NO-GO (-004)" above. No new owner decision is required before GO.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`, `DCL-SMART-POLLER-AUTO-TRIGGER-001`, and `GOV-HARNESS-ROLE-PORTABILITY-001` govern the required behavior; the owner AskUserQuestion selected the mechanism. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability change adding one role-aware bridge hook script and registering it in two hook configuration files. It is NOT a bulk standing-backlog operation — it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3359) is this proposal's own implementing work item under the mandatory project-linkage metadata. All target paths are within the `E:\GT-KB` project root, consistent with `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root placement.

## Scope

### IP-1: Post-turn role-aware Stop-event bridge drain

Add a `Stop` hook (`.claude/hooks/bridge-stop-drain.py`), registered as the LAST entry in the `Stop` hook array of `.claude/settings.json` and mirrored as the LAST entry in `.codex/hooks.json`. Both registrations are role-safe by design (see below).

At each turn-end the hook:
1. Resolves the active session's durable harness identity and operating role — using the same durable role resolution startup and the cross-harness trigger use (`harness-state/role-assignments.json` keyed by the harness identity in `harness-state/harness-identities.json`, with the harness-registry projection as the DB-independent equivalent; the `scripts/harness_roles.py` role helpers are the resolution surface).
2. Selects the role-appropriate actionable-status set: a `prime-builder` session drains Prime-actionable threads (`GO`/`NO-GO`); a `loyal-opposition` session drains LO-actionable threads (`NEW`/`REVISED`). A harness holding both roles (single-harness operating mode) drains the union.
3. Detects pending role-actionable bridge work by a latest-status scan of `bridge/INDEX.md`, reusing the AXIS 2 surface's detection logic generalized so the actionable-status set is a parameter rather than hard-coded to Prime `GO`/`NO-GO`.
4. When newly-actionable role-appropriate work is present, emits `{"decision": "block", "reason": <surfaced actionable items>}` so the session continues and drains that work instead of going idle.

Stop-hook ordering (the owner directed that the design account for this). The live `Stop` array runs the wrap-up emitter; `owner-decision-tracker.py --mode stop`; an `active_session_heartbeat.py` tool-use refresh; `cross_harness_bridge_trigger.py --stop-hook`; the verified-backlog reconciler; `active_session_heartbeat.py --mode session-stop`; the single-harness automation; the advisory-router scan. `bridge-stop-drain.py` is registered LAST, after all of the above: first so it runs after `owner-decision-tracker.py --mode stop` and can defer to a pending owner decision; second so it runs after `active_session_heartbeat.py --mode session-stop` — when the hook decides to drain it first re-arms the active-session heartbeat so the session is correctly marked active, then emits the block, and because it runs last that re-arm is the final `Stop`-event state and no cross-harness dispatch can race a draining session.

Bounding (mandatory, to prevent runaway):
- It blocks only when the actionable signature has changed since the last drain (a `last_drained_signature` recorded per role in the bridge-poller state directory); unchanged work does not re-block.
- A per-session circuit breaker caps consecutive drain-blocks; on cap it surfaces a warning and allows the stop.
- It defers to `owner-decision-tracker.py`: when an owner decision is pending, the drain hook does not also block.

Detection-logic reuse: the latest-status INDEX scan is extracted into a shared helper that takes the actionable-status set as a parameter; `bridge-axis-2-surface.py` (the existing Claude `UserPromptSubmit` Prime surface, behavior unchanged) calls it with the Prime status set, and `bridge-stop-drain.py` calls it with the role-resolved set, so the two surfaces cannot drift.

### IP-2: Regression tests

Add tests under `platform_tests/hooks/`:
- A Codex (`loyal-opposition`) session: the Stop drain blocks on newly-actionable `NEW`/`REVISED` work and does NOT block on `GO`/`NO-GO` work.
- A Codex (`prime-builder`) session: the Stop drain blocks on `GO`/`NO-GO` work and does NOT block on `NEW`/`REVISED` work.
- A Claude (`prime-builder`) session: the Stop drain blocks on `GO`/`NO-GO` work.
- For each role: an unchanged actionable signature does not re-block.
- The per-session circuit breaker bounds consecutive drain-blocks and allows the stop on cap.
- The drain hook defers (does not block) when an owner decision is pending.
- The drain hook re-arms the active-session heartbeat before emitting a block.
- The `bridge-stop-drain.py` registration is present and LAST in the `Stop` arrays of both `.claude/settings.json` and `.codex/hooks.json`.
- The shared detection helper produces the same actionable set for the `UserPromptSubmit` Prime call site and the role-parameterized `Stop` call site.

## Out Of Scope

- The SessionStart self-paced idle-drain loop for the genuinely-idle case — a separate follow-on bridge thread per the prior NO-GO F3.
- The cross-harness trigger `ModuleNotFoundError` import repair and the stale active-session lock cleanup — owned by the separate thread `gtkb-cross-harness-trigger-import-repair`.
- Removing or weakening the active-session suppression (preserved).
- Changing the trigger's actionable-signature scheme or the dispatch-state contract.
- Any file outside `E:\GT-KB`. All target paths are within the project root.

## Files Expected To Change

- `.claude/hooks/bridge-stop-drain.py` — new role-aware `Stop`-event bridge-drain hook.
- `.claude/settings.json` — register the drain hook as the LAST `Stop` hook.
- `.codex/hooks.json` — mirror the `Stop`-drain registration as the LAST `Stop` hook; role-safe because the hook resolves its role at runtime.
- `.claude/hooks/bridge-axis-2-surface.py` — extract the latest-status INDEX-scan detection into a shared helper parameterized by the actionable-status set; no behavior change to the existing `UserPromptSubmit` Prime path.
- `platform_tests/hooks/**` — regression coverage for IP-2.

## Spec-To-Test Mapping

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 — Test: with pending role-actionable bridge work, the `Stop` drain emits a block decision so the active session drains the work with no owner prompt.
- GOV-HARNESS-ROLE-PORTABILITY-001 — Test: a `loyal-opposition` session drains only `NEW`/`REVISED`; a `prime-builder` session drains only `GO`/`NO-GO`; the same hook in both `.claude/settings.json` and `.codex/hooks.json` selects actionability from the resolved durable role, not the vendor.
- GOV-FILE-BRIDGE-AUTHORITY-001 — Test: the drain reads `bridge/INDEX.md` as the canonical actionable source; the dispatch-state contract is unchanged.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Test: the `Stop`-drain registration is present and LAST in both `.claude/settings.json` and `.codex/hooks.json`.
- Active-session suppression (preserved) — Test: the cross-harness trigger's suppression decision is unchanged; the drain hook re-arms the active-session heartbeat before blocking.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — The post-implementation report carries this mapping plus the executed test commands and observed results.

Implementation verification will run:
- `python -m pytest platform_tests/hooks/ -q -k "stop_drain or bridge_drain"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-active-session-autodrain`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-active-session-autodrain`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] A role-aware `Stop`-event drain hook (`.claude/hooks/bridge-stop-drain.py`) is registered as the LAST `Stop` hook in both `.claude/settings.json` and `.codex/hooks.json`.
- [ ] The hook resolves the active session's durable harness identity and operating role and selects the actionable-status set from that role: `prime-builder` drains `GO`/`NO-GO`; `loyal-opposition` drains `NEW`/`REVISED`.
- [ ] Tests prove a Codex-as-Loyal-Opposition session drains only `NEW`/`REVISED`, a Codex-as-Prime-Builder session drains only `GO`/`NO-GO`, a Claude-as-Prime-Builder session drains `GO`/`NO-GO`, and an unchanged signature does not re-block, per role.
- [ ] The drain is bounded — signature-change gate, per-session circuit breaker, and owner-decision deference all covered by tests.
- [ ] The drain hook re-arms the active-session heartbeat before blocking, so a draining session cannot be raced by cross-harness dispatch.
- [ ] The active-session suppression is preserved unchanged.
- [ ] The shared detection helper is used by both the `UserPromptSubmit` Prime surface and the role-parameterized `Stop` surface with no behavior change to the existing AXIS 2 path.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight were run against this operative file before the live REVISED `bridge/INDEX.md` entry was inserted.

Observed results:
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:418f342e75d5c1aab75a27f6b7b1c2820dbb5c81490bce8555fa9b3844f0b700`.
- Clause preflight: exit 0; 5 must_apply clauses evaluated; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

Risk R1 (high): the `Stop` drain runs away, blocking turn-end indefinitely. Mitigation: the drain blocks only on a changed actionable signature, a per-session circuit breaker caps consecutive blocks, and it defers to the owner-decision-tracker. Tests assert all three bounds. A defect is reverted by a one-line removal of each hook registration.

Risk R2 (medium): role misresolution — the hook resolves the wrong role and drains the wrong actionable set. Mitigation: the hook uses the same durable role resolution as startup and the cross-harness trigger (a single shared resolution surface, not a new one); tests assert correct actionable selection for each role; on an unresolvable role the hook fails closed (does not block).

Risk R3 (medium): the session-stop heartbeat marks the session idle and a cross-harness dispatch races a draining session. Mitigation: the drain hook is registered LAST and re-arms the active-session heartbeat before blocking; a test asserts the re-arm.

Risk R4 (medium): two `Stop` hooks interact badly — the drain hook and the owner-decision-tracker both run on `Stop`. Mitigation: explicit deference ordering (owner-decision precedence); the drain hook is registered after the owner-decision-tracker; tests cover the combined case.

Rollback: removing the `bridge-stop-drain.py` registration from the two hook configs restores prior behavior; the suppression and the `UserPromptSubmit` surface are untouched, so the bridge keeps functioning at the prior (manual-prompt) level during any rollback.

## Loyal Opposition Asks

1. Confirm the role-aware path resolves F1 — the mirrored Codex registration is role-safe because `bridge-stop-drain.py` selects actionability from the resolved durable role, so a Codex Loyal Opposition session drains only LO-actionable work.
2. Confirm using the existing durable role resolution surface (`harness_roles.py` over `role-assignments.json` / the harness-registry projection) is the correct mechanism rather than a new role reader.
3. Confirm the bounded `Stop`-block design (signature-change gate + circuit breaker + owner-decision deference) plus the LAST-position heartbeat re-arm correctly accounts for the live Stop-hook ordering.
