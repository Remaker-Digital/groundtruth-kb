NEW

# Post-Implementation Report: Role-Aware Bridge Active-Session Auto-Drain (WI-3359)

bridge_kind: implementation_report
Document: gtkb-bridge-active-session-autodrain
Version: 007 (NEW; post-implementation report for the GO at -006)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001; WI-3359
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3359
target_paths: [".claude/hooks/bridge-stop-drain.py", ".claude/settings.json", ".codex/hooks.json", ".claude/hooks/bridge-axis-2-surface.py", "platform_tests/hooks/**"]
Recommended commit type: feat:

## Summary

This is the post-implementation report for WI-3359 (the bridge-notifier post-turn role-aware Stop-event auto-drain), implemented under the GO at `bridge/gtkb-bridge-active-session-autodrain-006.md`. A new role-aware `Stop` hook (`.claude/hooks/bridge-stop-drain.py`) is registered as the LAST `Stop` hook in both `.claude/settings.json` and `.codex/hooks.json`. At each turn-end the hook resolves the active session's durable harness identity and operating role, computes the bridge work actionable for that role, and — when newly-actionable role-appropriate work is pending — emits `{"decision": "block", "reason": ...}` so the active session drains that work instead of going idle. This closes the post-turn slice of the owner-out-of-loop dispatch gap (`ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`) without an owner prompt. The drain is bounded by a signature-change gate, a per-session circuit breaker, and owner-decision deference. The active-session suppression in the cross-harness trigger is preserved unchanged.

## Specification Links

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — bridge dispatch must reach the recipient harness with the owner out of the loop; the requirement this implements. Covered by the PROJECT-ANTIGRAVITY-INTEGRATION authorization (version 2).
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — the auto-trigger contract: actionable bridge state must trigger dispatch automatically.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger and the bridge surface are bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state, and bridge statuses are the role-actionability source.
- GOV-HARNESS-ROLE-PORTABILITY-001 — operating roles are portable across harnesses and actionability is role-bound; the role-aware drain resolves the active session's durable role before selecting actionable statuses.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — the hook change is mirrored across `.claude/settings.json` and `.codex/hooks.json`; the role-aware design makes the mirrored registration role-safe.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; cited to document that the auto-drain is a new mechanism, NOT fast-lane eligible, and is therefore authorized under the standard PROJECT-ANTIGRAVITY-INTEGRATION project authorization.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this report carries the linked specifications forward from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the spec-to-test mapping and observed results are below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2081 — owner decision F2 (AskUserQuestion DECISION-0663, 2026-05-17): WI-3359's auto-drain is authorized under PROJECT-ANTIGRAVITY-INTEGRATION, with the project authorization superseded to cover ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001. This report's bridge metadata cites the resulting authorization.
- DELIB-2079 — the owner-decided Antigravity Integration design. WI-3359 was added to PROJECT-ANTIGRAVITY-INTEGRATION per DELIB-2081; the role-aware (not Claude-only) drain is the correct design for the multi-harness dispatch story.
- The `-004` NO-GO (Codex, Loyal Opposition) found the `-003` Codex mirror role-unsafe; the `-005` REVISED took the role-aware mirrored path; Codex returned GO at `-006`. This report is the post-implementation submission for that GO.
- The active-session suppression behavior is VERIFIED at `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` and directed by `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09`. This implementation preserves that suppression unchanged.
- The AXIS 2 surface was built by `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface` (VERIFIED through `-015`) as a `UserPromptSubmit` hook. This implementation reuses its detection surface — `groundtruth_kb.bridge.notify.compute_actionable_pending` — on the `Stop` event (see Implementation Notes).

## Owner Decisions / Input

- The owner directed this fix on 2026-05-17: the bridge notifier must wake the recipient harness and dispatch work automatically in both directions; it is a long-standing requirement, not a new one.
- Via AskUserQuestion on 2026-05-17, the owner selected the fix direction "Active session auto-drains" — keep the suppression, close the gap at the active session.
- Via AskUserQuestion DECISION-0663 on 2026-05-17 (resolving the prior NO-GO F2), the owner selected that WI-3359 be authorized under PROJECT-ANTIGRAVITY-INTEGRATION. That decision is archived as DELIB-2081 and is the owner-approval evidence for the project authorization this report cites.
- Via AskUserQuestion on 2026-05-17, the owner approved "Register both now" — registering `bridge-stop-drain.py` in both `.claude/settings.json` and `.codex/hooks.json` immediately, making the hook live in the running session. The registration in this implementation reflects that owner approval.
- No new owner decision is required before verification; this report implements the GO'd `-005` proposal through the governed bridge path.

## Clause Scope Clarification (Not a Bulk Operation)

This is a post-implementation report for a scoped reliability change: one new role-aware bridge hook script, its registration in two hook configuration files, and a regression test file. It is NOT a bulk standing-backlog operation — it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it carries no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is therefore not applicable. The single work item cited (WI-3359) is this report's own implementing work item under the mandatory project-linkage metadata, not the target of a bulk mutation. All changed files are within the `E:\GT-KB` project root, consistent with `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root placement.

## Implementation Summary

- IP-1 — `.claude/hooks/bridge-stop-drain.py` is a new role-aware `Stop` hook. It takes a `--harness <name>` argument supplied by the hook registration, resolves the durable operating-role set for that harness via `scripts/harness_roles.py` over `harness-state/role-assignments.json` (keyed by `harness-state/harness-identities.json`), and computes the role-actionable bridge work. `drain_decision(project_root, harness_name, session_id)` is the testable core, kept pure of stdin parsing. A `prime-builder` session drains Prime-actionable threads (`GO`/`NO-GO`); a `loyal-opposition` session drains LO-actionable threads (`NEW`/`REVISED`); a harness holding both roles drains the de-duplicated union. When newly-actionable role-appropriate work is present the hook emits `{"decision": "block", "reason": <surfaced items>}`. The hook always exits 0 (fire-and-forget); errors append to a state-dir log.
- IP-1 (registration) — `bridge-stop-drain.py` is registered as the LAST entry in the `Stop` hook array of both `.claude/settings.json` (`--harness claude`, 9th of 9) and `.codex/hooks.json` (`--harness codex`, 7th of 7, with a `statusMessage`). LAST placement is required so the hook runs after `owner-decision-tracker.py --mode stop` (deference ordering) and after `active_session_heartbeat.py --mode session-stop` (so its heartbeat re-arm is the final `Stop`-event state).
- IP-1 (bounding) — three runaway guards: a signature-change gate (blocks only when the role-actionable signature has changed since the last drain, recorded per session in the stop-drain state directory); a per-session circuit breaker capping consecutive drain-blocks at `CIRCUIT_BREAKER_CAP` (3); and owner-decision deference (when an unresolved owner decision asked within `OWNER_DECISION_RECENCY_MINUTES` (30) is pending in `memory/pending-owner-decisions.md`, the drain does not block). Before emitting a block the hook re-arms the active-session heartbeat so a draining session cannot be raced by cross-harness dispatch.
- IP-2 — `platform_tests/hooks/test_bridge_stop_drain.py` is a new 15-test regression suite driving `drain_decision()` against fixture project roots plus a CLI-surface subprocess test and the registration assertion.

## Deviation From Proposal: Shared Detection Surface

The `-005` proposal IP-1 described extracting the latest-status INDEX scan into a *new* shared helper parameterized by the actionable-status set, with `bridge-axis-2-surface.py` updated to call it. During implementation this proved unnecessary and was not done. `groundtruth_kb.bridge.notify.compute_actionable_pending` is already the shared detection surface: it parses `bridge/INDEX.md` and returns the `(prime-actionable, codex-actionable)` split, and `.claude/hooks/bridge-axis-2-surface.py` already calls it. `bridge-stop-drain.py` calls the same function and selects the role's list (Prime → prime-actionable; LO → codex-actionable; both → union). No new helper file was created and `bridge-axis-2-surface.py` is UNCHANGED. This is strictly stronger than the proposal's "cannot drift" intent: the two surfaces invoke the literally-same library function rather than two call sites of a newly-extracted helper. `.claude/hooks/bridge-axis-2-surface.py` therefore remains in `target_paths` (the authorized upper bound) but was not modified. `test_both_surfaces_use_shared_compute_actionable_pending` asserts both surfaces reference `compute_actionable_pending`.

## Files Changed

- `.claude/hooks/bridge-stop-drain.py` — NEW (IP-1): role-aware `Stop`-event bridge-drain hook; `drain_decision()` core + `main()` CLI with `--harness`.
- `.claude/settings.json` — IP-1: registered `python "$CLAUDE_PROJECT_DIR/.claude/hooks/bridge-stop-drain.py" --harness claude` as the LAST `Stop` hook (9th of 9).
- `.codex/hooks.json` — IP-1: registered `python E:\GT-KB\.claude\hooks\bridge-stop-drain.py --harness codex` as the LAST `Stop` hook (7th of 7), with `statusMessage` "Bridge active-session auto-drain (role-aware Stop drain)".
- `platform_tests/hooks/test_bridge_stop_drain.py` — NEW (IP-2): 15-test regression suite.
- `.claude/hooks/bridge-axis-2-surface.py` — NOT changed; see Deviation From Proposal above.

## Spec-To-Test Mapping

All 15 tests in `platform_tests/hooks/test_bridge_stop_drain.py` PASS (`15 passed in 2.33s`; command and full output below).

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 (the drain blocks turn-end on actionable work, no owner prompt) — `test_codex_as_lo_drains_new_revised`, `test_codex_as_prime_drains_go_no_go`, `test_claude_as_prime_drains_go_no_go` (each asserts `decision == block` with the actionable items surfaced in the reason); `test_main_cli_surface_emits_block_and_exits_zero` exercises the full `Stop`-hook surface end-to-end (argparse `--harness`, stdin event JSON, stdout block decision, exit 0).
- GOV-HARNESS-ROLE-PORTABILITY-001 (actionability is role-bound, not vendor-bound) — `test_codex_as_lo_drains_new_revised` + `test_codex_as_lo_ignores_go_no_go` prove a `loyal-opposition` session drains only `NEW`/`REVISED`; `test_codex_as_prime_drains_go_no_go` + `test_codex_as_prime_ignores_new_revised` prove the SAME Codex harness, when assigned `prime-builder`, drains only `GO`/`NO-GO`; `test_claude_as_prime_drains_go_no_go` proves Claude-as-Prime drains `GO`/`NO-GO`.
- Bounding — signature-change gate: `test_unchanged_signature_does_not_reblock` (prime) and `test_unchanged_signature_does_not_reblock_lo` (loyal-opposition) prove an unchanged role-actionable signature does not re-block, per role.
- Bounding — circuit breaker: `test_circuit_breaker_bounds_consecutive_blocks` escalates a fresh signature each call and proves the breaker trips at `CIRCUIT_BREAKER_CAP` consecutive blocks and then releases the stop.
- Bounding — owner-decision deference: `test_owner_decision_deference_suppresses_drain` proves a recent unresolved owner decision suppresses the drain; `test_resolved_owner_decision_does_not_suppress_drain` and `test_stale_owner_decision_does_not_suppress_drain` prove the suppression is conditional on an unresolved AND recent decision.
- Risk R3 (stale-lock dispatch race) — `test_drain_rearms_active_session_heartbeat_before_blocking` proves the drain re-arms the active-session heartbeat on the block path.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — `test_bridge_stop_drain_registered_last_in_both_stop_arrays` reads the live `.claude/settings.json` and `.codex/hooks.json` and asserts `bridge-stop-drain.py` is the LAST `Stop` hook in each, with the correct `--harness` argument.
- No-drift shared surface — `test_both_surfaces_use_shared_compute_actionable_pending` asserts `bridge-stop-drain.py` and `bridge-axis-2-surface.py` both call `compute_actionable_pending`.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the hook reads `bridge/INDEX.md` via `parse_index` + `compute_actionable_pending` as the canonical actionable source; every test exercises this read path against a fixture INDEX, and the dispatch-state / suppression contract is untouched.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — this report carries the spec-to-test mapping plus the executed commands and observed results.

## Verification Commands And Observed Results

- `python -m pytest platform_tests/hooks/test_bridge_stop_drain.py -q` — `15 passed in 2.33s`. The 15 tests: `test_codex_as_lo_drains_new_revised`, `test_codex_as_lo_ignores_go_no_go`, `test_codex_as_prime_drains_go_no_go`, `test_codex_as_prime_ignores_new_revised`, `test_claude_as_prime_drains_go_no_go`, `test_unchanged_signature_does_not_reblock`, `test_unchanged_signature_does_not_reblock_lo`, `test_circuit_breaker_bounds_consecutive_blocks`, `test_owner_decision_deference_suppresses_drain`, `test_resolved_owner_decision_does_not_suppress_drain`, `test_stale_owner_decision_does_not_suppress_drain`, `test_drain_rearms_active_session_heartbeat_before_blocking`, `test_both_surfaces_use_shared_compute_actionable_pending`, `test_main_cli_surface_emits_block_and_exits_zero`, `test_bridge_stop_drain_registered_last_in_both_stop_arrays`.
- `python -m py_compile .claude/hooks/bridge-stop-drain.py` — clean.
- `python -c "import json; json.load(open('.claude/settings.json'))"` and the same for `.codex/hooks.json` — both parse; the `Stop` arrays carry 9 and 7 hooks respectively with `bridge-stop-drain.py` LAST in each.

## Implementation Notes

- The detection surface is `groundtruth_kb.bridge.notify.compute_actionable_pending` — the same function `bridge-axis-2-surface.py` uses (see Deviation From Proposal). No new helper file was added.
- The hook fails closed: when the harness identity or operating role cannot be resolved, `drain_decision` returns `{}` (allow the stop). This satisfies the `-006` GO watchpoint "fail closed when the active harness ID or role cannot be resolved."
- `VERIFIED` (and `WITHDRAWN`) bridge entries are excluded from actionability by `compute_actionable_pending` for both roles, so the drain never treats terminal bridge state as queue work — satisfying the `-006` GO watchpoint "keep `VERIFIED` as bridge closure only."
- The Codex `Stop` registration is a bridge-dispatch substrate, not a session-lifecycle wrap-up script; no lifecycle wrap-up emitter was added to the Codex `Stop` array, satisfying the `-006` GO watchpoint.
- The tests import `harness_roles` and `groundtruth_kb` from the real checkout (code, not fixture data) while the fixture project roots supply only the data files `drain_decision` reads; the CLI-surface test carries the real checkout on `PYTHONPATH` while pointing `CLAUDE_PROJECT_DIR` at the fixture.
- Scope note: the WI-3344 changes from earlier this session remain uncommitted per owner AskUserQuestion ("Leave uncommitted"). The eventual WI-3359 commit must be scoped to the four files in Files Changed above and must not bundle the WI-3344 working-tree changes.

## Recommended Commit Type

`feat:` — WI-3359 adds a new capability surface (a role-aware `Stop`-event bridge auto-drain mechanism) plus its hook registrations and regression suite. It is net-new behavior, not a repair of broken behavior, and is therefore not reliability-fast-lane eligible (consistent with the `GOV-RELIABILITY-FAST-LANE-001` citation above).

## Acceptance Criteria

- [x] A role-aware `Stop`-event drain hook (`.claude/hooks/bridge-stop-drain.py`) is registered as the LAST `Stop` hook in both `.claude/settings.json` and `.codex/hooks.json`.
- [x] The hook resolves the active session's durable harness identity and operating role and selects the actionable-status set from that role: `prime-builder` drains `GO`/`NO-GO`; `loyal-opposition` drains `NEW`/`REVISED`.
- [x] Tests prove a Codex-as-Loyal-Opposition session drains only `NEW`/`REVISED`, a Codex-as-Prime-Builder session drains only `GO`/`NO-GO`, a Claude-as-Prime-Builder session drains `GO`/`NO-GO`, and an unchanged signature does not re-block, per role.
- [x] The drain is bounded — signature-change gate, per-session circuit breaker, and owner-decision deference all covered by tests.
- [x] The drain hook re-arms the active-session heartbeat before blocking, so a draining session cannot be raced by cross-harness dispatch.
- [x] The active-session suppression is preserved unchanged (no change to the cross-harness trigger or its dispatch-state contract).
- [x] The shared detection surface is `compute_actionable_pending`, used by both the `UserPromptSubmit` Prime surface and the role-aware `Stop` surface with no behavior change to the existing AXIS 2 path.
- [x] This post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight were run against this report file with `--content-file` before the live NEW `bridge/INDEX.md` entry was inserted.

Observed results:
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:736d1bb2c22ca0ddff07d170337edae86da2491fb61bc33e47177cb6d429bb87`.
- Clause preflight: exit 0; 5 must_apply clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Loyal Opposition Asks

1. Confirm `drain_decision()` correctly closes the post-turn owner-out-of-loop gap for each role — Prime drains `GO`/`NO-GO`, LO drains `NEW`/`REVISED` — with the same hook registered in both harness configs.
2. Confirm the deviation from proposal (reusing `groundtruth_kb.bridge.notify.compute_actionable_pending` rather than extracting a new helper, leaving `bridge-axis-2-surface.py` unchanged) is an acceptable in-scope simplification that satisfies the proposal's "cannot drift" intent.
3. Confirm the bounded `Stop`-block design (signature-change gate + circuit breaker + owner-decision deference) plus the LAST-position heartbeat re-arm correctly accounts for the live Stop-hook ordering, and that the 15-test suite is sufficient spec-derived coverage for VERIFIED.
