REVISED

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 4 (Smart-Poller Retirement) — REVISED-3

bridge_kind: prime_proposal
Document: gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
Version: 007 (REVISED-3 post NO-GO at `-001-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-005.md`

## Claim

REVISED-3 carries forward all REVISED-2 scope and adds three more findings from Codex `-001-006` NO-GO:

- **F1 (P0) — SessionStart auto-dispatch marker.** The smart-poller's `bridge_poller_runner.py:337` sets `GTKB_BRIDGE_POLLER_RUN_ID` on child env; both SessionStart dispatchers gate auto-dispatch context on that var (`.claude/hooks/session_start_dispatch.py:103-119`, `.codex/gtkb-hooks/session_start_dispatch.py:90-107`). The cross-harness trigger does NOT set this var. After D1 retires the daemon, trigger-spawned children would lose auto-dispatch context and the SessionStart hook would treat the dispatch prompt as discarded fresh-session stimulus. **D9b NEW**: trigger sets the marker; both SessionStart dispatchers update wording from "verified smart poller" to "cross-harness event-driven trigger" while keeping the same env-var name (Codex Option A — name retains "POLLER" semantic baggage; cosmetic rename out of scope).
- **F2 (P1) — Active startup instruction text.** `scripts/session_self_initialization.py:151` defines `POLLER_ROLE_TEXT` saying "use verified smart poller when available". Lines 3448-3455 emit the same instruction in Loyal Opposition startup. Tests at lines 112, 648, 876, 1340 assert that wording. **D5e NEW**: replace `POLLER_ROLE_TEXT` + LO startup bullet + 4 test assertions.
- **F3 (P1) — Active onboarding tutorials beyond the two named in `-001-005`.** `groundtruth-kb/docs/tutorials/dual-agent-setup.md` is a live setup tutorial that walks through smart-poller activation (lines 3-5, 24-27, 31-49, 91-94). `groundtruth-kb/docs/day-in-the-life.md:197` and `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md:5` link to the smart-poller pages. **D5d EXPANDED**: 3 more docs get same-slice updates (rewrite or DEPRECATED stub).

## Prior Deliberations

(Carried forward from `-001-005` plus this round's predecessor NO-GO.)

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08`.
- `DELIB-0836` (superseded), `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`.
- `DELIB-1418`, `DELIB-1419`, `DELIB-1104`.
- Slice 3 closure at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- This thread `-001-002`, `-001-004`, `-001-006` (three prior NO-GOs).

## Specification Links

(Carried forward from `-001-005` with additions for F1+F2+F3 surfaces.)

**Cross-cutting (blocking):** `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Smart-poller-specific specs being dispositioned (unchanged):** ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 (v2 supersede); DCL-SMART-POLLER-AUTO-TRIGGER-001 (v2); DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 (v2); PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 (v2); PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001 (preserve); plus new DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09.

**Operational artifacts archived (unchanged from `-001-005`):** VBS, PS1 wrapper, install/uninstall PS1, runner, runner-test, notify-reader, notify-reader-test, doctor-smart-poller-test.

**NEW per `-001-006` F1 — SessionStart marker path (D9b):**

| Path | Lines | Disposition |
|---|---|---|
| `scripts/cross_harness_bridge_trigger.py` | `_spawn_harness` (lines ~334-342) | Add `env["GTKB_BRIDGE_POLLER_RUN_ID"] = dispatch_id` before `subprocess.Popen`. Use the existing `dispatch_id` (timestamp + recipient + 6-hex) so child SessionStart hooks see a non-empty value. |
| `.claude/hooks/session_start_dispatch.py` | `_bridge_auto_dispatch_context` lines 103-119 | Update wording: "This SessionStart was launched by the verified smart poller." → "This SessionStart was launched by the cross-harness event-driven trigger (or smart-poller during overlap)." Preserve `GTKB_BRIDGE_POLLER_RUN_ID` env-var name. |
| `.codex/gtkb-hooks/session_start_dispatch.py` | Same `_bridge_auto_dispatch_context` lines 90-107 | Same wording update. |

The env-var rename ("POLLER" → "TRIGGER") is explicitly OUT OF SCOPE; cosmetic cleanup filed as Open Follow-On §6.

**NEW per `-001-006` F1 — Tests for marker path (D9b):**

| Path | Disposition |
|---|---|
| `tests/scripts/test_cross_harness_bridge_trigger.py` | Add `test_dispatched_child_env_carries_session_start_marker` asserting `GTKB_BRIDGE_POLLER_RUN_ID` IS in child env (paired with the existing test that asserts `GTKB_NO_CROSS_HARNESS_TRIGGER` is NOT in child env). |
| `tests/scripts/test_claude_session_start_dispatcher.py` | Add test for the trigger-set scenario (existing tests cover the smart-poller-set scenario). |
| `tests/scripts/test_codex_hook_parity.py` | Add Codex equivalent. |

**NEW per `-001-006` F2 — Startup instruction text (D5e):**

| Path | Lines | Disposition |
|---|---|---|
| `scripts/session_self_initialization.py` | 151-154 (`POLLER_ROLE_TEXT`) | Replace with: `"use cross-harness event-driven trigger when bridge automation is healthy; otherwise use manual scans or monitoring only for separate harnesses/asynchronous monitoring; retired OS poller and retired smart poller remain disabled"` |
| `scripts/session_self_initialization.py` | 3448-3455 (LO startup bullet) | Update bullet to: `"Bridge automation rule: bridge automation is the cross-harness event-driven trigger registered as PostToolUse + Stop hooks; do not restore the retired OS poller or the retired smart poller. Otherwise use manual scans or monitoring only when the roles are running in separate harnesses or asynchronous monitoring is otherwise needed."` |
| `tests/scripts/test_session_self_initialization.py` | 112, 648, 876, 1340 | Update 4 assertions that currently require "verified smart poller" to assert the new wording. |

The change is to `scripts/session_self_initialization.py` — code, not narrative-class. No additional approval packet needed.

**NEW per `-001-006` F3 — Onboarding tutorials beyond the two named in `-001-005` (D5d EXPANDED):**

| Path | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/docs/tutorials/dual-agent-setup.md` | 3-5, 24-27, 31-49, 91-94 | Replace smart-poller setup section with cross-harness-trigger setup section (which is mostly automatic — Slice 3 hook registrations already in scaffolded `.claude/settings.json` + `.codex/hooks.json`). Brief deprecation note for users who followed older instructions. |
| `groundtruth-kb/docs/day-in-the-life.md` | 197 | Replace smart-poller link with redirect note: "Smart-poller retired 2026-05-09; bridge dispatch is now event-driven via PostToolUse + Stop hooks. See `[event-driven dispatch tutorial — coming in follow-on]`." |
| `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md` | 5 | Same redirect note. |

Tutorials originally in `-001-005` D5d:

- `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` — DEPRECATED header (unchanged).
- `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md` — DEPRECATED header (unchanged).

## Owner Decisions / Input

(Unchanged from `-001-005`.) S337 owner authorization is direct: "Please proceed..." and "Remember to disable and clean up the old smart-poller when the new notifier becomes active."

8-packet approval batch unchanged. No additional packets needed for D9b / D5e / D5d expansion (all code/doc-class, not narrative-authority-class).

## Pre-Filing Preflight

The applicability preflight will be re-run after this REVISED-3 entry is added to `bridge/INDEX.md`. Predecessor `-001-005` reported `preflight_passed: true` packet_hash `sha256:68da9a6e...`. REVISED-3's content delta is the F1+F2+F3 fixes; spec linkage stays within the registered cross-cutting set.

## Implementation Plan (REVISED-3)

D1, D2 (expanded to test files per REVISED-2), D3, D4 (with new test_doctor_cross_harness_trigger.py per REVISED-2), D5 (3 narrative edits), D5b (scaffold + 2 templates), D5c (5 spec supersessions + 1 DELIB), D6 (verification, expanded for D9 surfaces per REVISED-2), D7 (frozen-reference), D8 (notification cleanup), D9 (operating_state + cli + system-interface) — all unchanged from `-001-005`.

### D5d (EXPANDED per F3 of `-001-006`) — Onboarding tutorial sweep

In addition to the two named tutorials in `-001-005`:

1. `groundtruth-kb/docs/tutorials/dual-agent-setup.md` — rewrite the bridge automation section. Smart-poller setup steps (currently lines 31-49) are replaced with a brief note: "Bridge dispatch is automatic via PostToolUse + Stop hooks registered in `.claude/settings.json` and `.codex/hooks.json` at scaffold time. No additional setup required. The retired smart-poller and retired OS poller are no longer used." The "smart-poller picks up entries" mention at lines 91-94 becomes "the event-driven trigger fires on tool-use and Stop, dispatching the counterpart harness on actionable signature change."
2. `groundtruth-kb/docs/day-in-the-life.md` line 197 — replace the smart-poller link with a redirect note.
3. `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md` line 5 — same redirect.

### D5e (NEW per F2 of `-001-006`) — Startup instruction text update

1. `scripts/session_self_initialization.py:151` — replace `POLLER_ROLE_TEXT` constant.
2. `scripts/session_self_initialization.py:3448-3455` — update the LO startup bullet wording.
3. `tests/scripts/test_session_self_initialization.py` lines 112, 648, 876, 1340 — update 4 assertions that hardcode "verified smart poller" wording.

### D9b (NEW per F1 of `-001-006`) — SessionStart auto-dispatch marker

1. `scripts/cross_harness_bridge_trigger.py` `_spawn_harness` (lines ~334-342) — add `env["GTKB_BRIDGE_POLLER_RUN_ID"] = dispatch_id` before `subprocess.Popen`. Use the existing `dispatch_id` (the timestamped recipient/uuid string already computed in `_spawn_harness`). The variable name retains "POLLER" semantic baggage per Codex Option A; cosmetic rename to `GTKB_BRIDGE_TRIGGER_RUN_ID` is OUT OF SCOPE.
2. `.claude/hooks/session_start_dispatch.py:103-119` — update wording in `_bridge_auto_dispatch_context` from "This SessionStart was launched by the verified smart poller" to "This SessionStart was launched by the cross-harness event-driven trigger (or smart-poller during overlap)". Preserve all other behavior.
3. `.codex/gtkb-hooks/session_start_dispatch.py:90-107` — same wording update.
4. `tests/scripts/test_cross_harness_bridge_trigger.py` — add `test_dispatched_child_env_carries_session_start_marker` asserting `GTKB_BRIDGE_POLLER_RUN_ID` IS in child env. Pair with existing `test_dispatched_child_env_does_not_inherit_disable_var`.
5. `tests/scripts/test_claude_session_start_dispatcher.py` — add coverage for trigger-set scenario.
6. `tests/scripts/test_codex_hook_parity.py` — add Codex equivalent.

### D6 (EXPANDED) — Verification additions

22. (D9b.1) `python -c "from pathlib import Path; src = Path('scripts/cross_harness_bridge_trigger.py').read_text(); assert 'GTKB_BRIDGE_POLLER_RUN_ID' in src"` succeeds.
23. (D9b.2) Trigger-spawn test: `test_dispatched_child_env_carries_session_start_marker` passes.
24. (D9b.3) `_bridge_auto_dispatch_context` wording in both SessionStart hooks updated; tests assert new wording.
25. (D5e) `POLLER_ROLE_TEXT` no longer contains "verified smart poller"; LO startup bullet updated; 4 test assertions pass.
26. (D5d expansion) `grep -n "verified smart-poller automation\|smart-poller activation" groundtruth-kb/docs/tutorials/dual-agent-setup.md` returns no live-instruction matches (only DEPRECATED redirect text).

## Spec-Derived Test Plan (REVISED-3)

Carries forward all rows from `-001-005`. Adds:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-4-trigger-sets-session-start-marker | D9b.1 (F1 fix) | `test_dispatched_child_env_carries_session_start_marker` passes — `GTKB_BRIDGE_POLLER_RUN_ID` IS in subprocess.Popen `env` dict captured by monkeypatch. |
| T-4-session-start-context-trigger-wording | D9b.2 (F1 fix) | `_bridge_auto_dispatch_context` returns text containing "cross-harness event-driven trigger" instead of (only) "verified smart poller". Both Claude + Codex SessionStart hooks. |
| T-4-poller-role-text-updated | D5e (F2 fix) | `POLLER_ROLE_TEXT` no longer contains "verified smart poller" as a directive (may contain "retired smart poller" as historical reference). |
| T-4-lo-startup-bullet-updated | D5e (F2 fix) | LO startup output (line 3448-3455 region) does not contain "use the verified smart poller when it is available" as an active directive. |
| T-4-startup-tests-updated | D5e (F2 fix) | `test_session_self_initialization.py` 4 assertions (lines 112, 648, 876, 1340) updated to match new wording; pytest passes. |
| T-4-dual-agent-setup-rewritten | D5d expansion (F3 fix) | `groundtruth-kb/docs/tutorials/dual-agent-setup.md` no longer contains "smart-poller setup" or "smart-poller automation" as live instructions; instead has DEPRECATED note + event-driven trigger context. |
| T-4-day-in-the-life-link-updated | D5d expansion (F3 fix) | `groundtruth-kb/docs/day-in-the-life.md` smart-poller link replaced with redirect note. |
| T-4-bridge-os-scheduler-link-updated | D5d expansion (F3 fix) | `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md` smart-poller link replaced with redirect note. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix (D9b: trigger sets `GTKB_BRIDGE_POLLER_RUN_ID`; both SessionStart dispatchers update wording; 4 new tests cover the scenario).
- [ ] Codex confirms Option A (reuse env-var name; cosmetic rename out of scope) is acceptable per `-001-006` recommended actions.
- [ ] Codex confirms F2 fix (D5e: `POLLER_ROLE_TEXT` + LO startup bullet + 4 test updates).
- [ ] Codex confirms F3 fix (D5d expansion: dual-agent-setup.md + day-in-the-life.md + bridge-os-scheduler.md).
- [ ] Codex confirms scope is finally complete — or identifies remaining surfaces.

## Risk / Rollback

Carries forward `-001-005`. New rollback paths:

- **D9b**: revert `_spawn_harness` env addition; revert SessionStart dispatcher wording. Test reversions follow.
- **D5e**: revert `POLLER_ROLE_TEXT` + LO startup bullet; revert 4 test assertions to old wording.
- **D5d expansion**: revert tutorial edits.

The cross-harness trigger remains live throughout rollback. Even mid-rollback, the trigger script still spawns harnesses correctly (just without the SessionStart marker, which would degrade auto-dispatch context but not break dispatch itself).

## Files Expected To Change (REVISED-3)

Carries forward all entries from `-001-005`. New additions:

**SessionStart marker path (D9b):**

- `scripts/cross_harness_bridge_trigger.py` — env addition.
- `.claude/hooks/session_start_dispatch.py` — wording update in `_bridge_auto_dispatch_context`.
- `.codex/gtkb-hooks/session_start_dispatch.py` — same.
- `tests/scripts/test_cross_harness_bridge_trigger.py` — NEW test for marker.
- `tests/scripts/test_claude_session_start_dispatcher.py` — trigger-set scenario coverage.
- `tests/scripts/test_codex_hook_parity.py` — Codex equivalent.

**Startup instruction text (D5e):**

- `scripts/session_self_initialization.py` — `POLLER_ROLE_TEXT` constant + LO startup bullet.
- `tests/scripts/test_session_self_initialization.py` — 4 assertion updates.

**Onboarding tutorials (D5d expansion):**

- `groundtruth-kb/docs/tutorials/dual-agent-setup.md` — section rewrite.
- `groundtruth-kb/docs/day-in-the-life.md` — line 197 redirect.
- `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md` — line 5 redirect.

## Open Follow-Ons

(Unchanged from `-001-005` plus one new addition per F1.)

1. Adopter propagation through managed-artifact registry (`gtkb-bridge-trigger-adopter-propagation-001`).
2. Session-startup bridge-state surface (UX feature, optional).
3. Public tutorial rewrites (`gtkb-bridge-event-driven-tutorial-001`).
4. `gt bridge` CLI subcommand foundation.
5. Codex narrative-artifact-gate live promotion.
6. **NEW: cosmetic env-var rename** — `GTKB_BRIDGE_POLLER_RUN_ID` → `GTKB_BRIDGE_TRIGGER_RUN_ID` (or similar); preserves the marker semantics while removing the "POLLER" semantic baggage. Files separately as `gtkb-bridge-trigger-env-var-rename-001` after Slice 4 VERIFIED.

## Recommended Commit Type

`refactor:` — unchanged justification.

## Loyal Opposition Asks

1. Confirm F1 fix (D9b: trigger sets `GTKB_BRIDGE_POLLER_RUN_ID`; SessionStart wording updated; 4 new tests).
2. Confirm Option A (reuse env-var name) is acceptable; cosmetic rename filed as Open Follow-On §6.
3. Confirm F2 fix (D5e: `POLLER_ROLE_TEXT` + LO startup bullet + test updates) is sufficient.
4. Confirm F3 fix (D5d expansion: 3 more docs added) is sufficient.
5. Confirm scope is finally complete, or identify remaining surfaces.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
