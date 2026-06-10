REVISED

# Implementation Proposal — Loyal Opposition Startup Symmetry — REVISED-3

bridge_kind: prime_proposal
Document: gtkb-loyal-opposition-startup-symmetry-001
Version: 007 (REVISED-3 post NO-GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md` (REVISED-2; NO-GO at `-006`).

## Revision Notes (REVISED-3)

This revision addresses the single finding F1 (P1) from `bridge/gtkb-loyal-opposition-startup-symmetry-001-006.md`. All `-005` scope carries forward unchanged except where the items below are revised. Codex closed `-006` with: "this thread should be close to GO unless the revision introduces new scope" — this revision is targeted and narrow.

### F1 (P1) — `guard_tool_use` blocked-reason wording added to scope

**Codex evidence:** `scripts/workstream_focus.py:1178-1180` contains an active stale-discard variant in the `guard_tool_use` blocked-reason text:

```
"BLOCKED (GTKB-STARTUP-INPUT-GATE): the first owner message of this fresh session was discarded "
"as startup stimulus. Do not use tools on this turn. Present the startup disclosure and wait for "
"Mike's next message."
```

This is emitted when `_startup_response_pending(project_root)` is True — i.e., when the harness has emitted the startup disclosure but is waiting for the owner's first follow-up. Under the init-keyword redesign (UserPromptSubmit-only mode authority per F2 of `-002`), `startup_response_pending` should never be True after the no-match pass-through path; but the guard still emits stale wording in the legitimate match-then-await path AND in any session that triggers the guard.

**Resolution:**

1. **Add `scripts/workstream_focus.py:1178-1180` to the IP-3 explicit edit list.** The `guard_tool_use` blocked-reason text is replaced with init-keyword-aware wording: `"BLOCKED (GTKB-STARTUP-INPUT-GATE): startup disclosure has been emitted; awaiting owner's next message before tool use. The init-keyword contract relays the disclosure on match (init gtkb / init gtkb advisory / etc.) and passes through on no-match (per ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001)."`

2. **Expand `_FORBIDDEN_PATTERNS` in IP-10 from 9 to 11 entries** to catch the variant phrasings:
    - `"first owner message of this fresh session was discarded"`
    - `"was discarded as startup stimulus"`

3. **Add targeted assertion** in IP-11 tests: `T-LOSS-guard-tool-use-no-stale-discard-wording` — call `guard_tool_use` with `_startup_response_pending=True` after the redesign; assert the blocked-reason text contains init-keyword-aware wording AND does NOT contain `"was discarded as startup stimulus"` or `"first owner message of this fresh session was discarded"`.

4. The guard path itself remains valuable (it prevents tool use during the disclosure-relay-then-await window); only the blocked-reason wording is updated.

## Claim

(Carried forward from `-005`/`-003`/`-001`, unchanged.) Make Loyal Opposition session startup symmetric with Prime Builder along init-keyword grammar + LO auto-process default. REVISED-3 closes the narrow F1 from `-006` by adding the `guard_tool_use` blocked-reason wording to scope.

## Why Now

(Carried forward from `-005`, unchanged.)

## Prior Deliberations

- All records cited in `-005`, `-003`, and `-001` carry forward unchanged.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-006.md` — Codex NO-GO on REVISED-2; F1 (P1) `guard_tool_use` wording missed. Addressed in this REVISED-3.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-004.md` — Codex NO-GO on `-003`; F1 (P0) Claude Code hook registration gap, F2 (P1) regression scan + active-code wording gaps. Both closed in `-005`; reaffirmed.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-002.md` — Codex NO-GO on `-001`; F1-F3 closed in `-003`; reaffirmed.
- `feedback_init_keyword_as_role_symmetric_activator.md` — owner-confirmed framing 2026-05-09.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packets gate spec inserts and AGENTS.md edit per IP-8.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner directives via AskUserQuestion provide candidate-requirement to spec promotion paths.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

**New specs created by this slice (carried forward unchanged from `-001`/`-003`/`-005`):**

- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` v1 (NEW; architecture_decision)
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` v1 (NEW; design_constraint)
- `DCL-SESSION-START-APP-SCOPE-BINDING-001` v1 (NEW; design_constraint)
- `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001` v1 (NEW; architecture_decision)
- `DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001` v1 (NEW; design_constraint; per F1 of `-002`/`-004`/`-006`, the constraint covers `_render_loyal_opposition_startup_task`, AGENTS.md, CODEX-WAY-OF-WORKING.md, system-interface-map.toml startup-disclosure row's caveat, AND `guard_tool_use` blocked-reason text per F1 of `-006`).

## Owner Decisions / Input

(Carried forward from `-005`, unchanged. F1 of `-006` is a narrow scope expansion within the existing slice; no new owner-decision rounds required.)

- AUQ "Inventory only (Recommended)" 2026-05-09 — monitor-gt-kb-bridge out-of-scope; carried forward.
- AUQ "One umbrella bridge proposal covering both concerns (Recommended)" 2026-05-09 — authorized this thread.
- AUQ S337 prior on init-keyword grammar — drives §"Init-Keyword Grammar" content.
- AUQ "File both REVISED-2 -005s now" 2026-05-09 — authorized REVISED-2.
- AUQ "Capture -006 verdicts + inventory new gt-kb-bridge-monitor + file umbrella REVISED-3" 2026-05-09 — authorized this REVISED-3.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this REVISED-3 lands at `-007`. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. Clause preflight expected exit 0.

## Init-Keyword Grammar

(Unchanged from `-005`/`-003`/`-001`.)

## Behavior Change Summary

(Unchanged from `-005`.)

## Implementation Plan

### IP-1, IP-2, IP-4, IP-5, IP-6, IP-7, IP-8, IP-9, IP-12, IP-13

(All unchanged from `-005`.)

### IP-3 — Update startup payload directives + lazy-injection of relay block (EXPANDED per F1 of `-006`)

1. Replace text directives at `scripts/session_self_initialization.py:3467, 5576-5577, 5630-5631` with init-keyword-aware text.
2. Replace text directives at `scripts/workstream_focus.py:693, 986-992` with init-keyword-aware text.
3. **NEW per F1 of `-006`:** Replace `guard_tool_use` blocked-reason text at `scripts/workstream_focus.py:1178-1180`. Old text: `"BLOCKED (GTKB-STARTUP-INPUT-GATE): the first owner message of this fresh session was discarded as startup stimulus. Do not use tools on this turn. Present the startup disclosure and wait for Mike's next message."`. New text: `"BLOCKED (GTKB-STARTUP-INPUT-GATE): startup disclosure has been emitted; awaiting owner's next message before tool use. The init-keyword contract relays the disclosure on match (init gtkb / init gtkb advisory / etc.) and passes through on no-match (per ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001)."`. The guard path itself remains valuable; only the blocked-reason wording is updated.
4. Conditionalize the unconditional-relay block at `scripts/session_self_initialization.py:5611-5629` (carried forward from `-003`).
5. Update `config/agent-control/system-interface-map.toml:365` `harness_caveats` field for the `startup-disclosure` row to init-keyword-aware text (carried forward from `-005` F2 of `-004`).

### IP-10 — Active-startup-text regression scan (EXPANDED per F1 of `-006`)

**Scanned paths:** `AGENTS.md`, `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`, `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `.claude/rules/*.md`, `config/agent-control/system-interface-map.toml`.

**Forbidden patterns (EXPANDED per F1 of `-006` from 9 to 11 entries):**

```python
_FORBIDDEN_PATTERNS = (
    # Original three from -003:
    "first owner message in a fresh session is a session-start stimulus only",
    "ask Mike whether to begin processing",
    "ask Mike whether to begin processing bridge reviews",
    # Six per F2 of -004:
    "first owner message of a fresh session is never actionable",
    "discard the current prompt",
    "first owner message after SessionStart is discarded startup stimulus",
    "first owner message after SessionStart is discarded",
    "Fresh-session first owner message is a stimulus",
    "first owner message is never actionable",
    # NEW per F1 of -006 — guard_tool_use blocked-reason variant:
    "first owner message of this fresh session was discarded",
    "was discarded as startup stimulus",
)
```

**Allowlist:** unchanged from `-005`. HISTORICAL-prefix tolerance preserved.

### IP-11 — Tests (EXPANDED per F1 of `-006`)

(Carried forward from `-005`; F1 of `-006` addition:)

- **NEW per F1 of `-006`:** `T-LOSS-guard-tool-use-no-stale-discard-wording` — call `scripts/workstream_focus.py::guard_tool_use` with `_startup_response_pending=True` after the redesign; assert the blocked-reason text contains init-keyword-aware wording (e.g., `"init-keyword contract relays the disclosure on match"`); assert it does NOT contain `"was discarded as startup stimulus"` or `"first owner message of this fresh session was discarded"`.

## Spec-Derived Test Plan

(Carried forward from `-005`; F1 of `-006` addition:)

| Test | Spec/Requirement | Method |
|---|---|---|
| (T-LOSS rows from -005 carry forward) | | |
| T-LOSS-guard-tool-use-no-stale-discard-wording | F1 of `-006` fix; DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001 | Synthetic call to `guard_tool_use` with `_startup_response_pending=True`; assert blocked-reason contains init-keyword-aware wording AND no stale-discard variants. |

## Acceptance Criteria

- [ ] Codex confirms F1 of `-006` closed: `scripts/workstream_focus.py:1178-1180` blocked-reason text replaced with init-keyword-aware wording; `_FORBIDDEN_PATTERNS` expanded to 11 entries to catch the variant; targeted test asserts the new wording.
- [ ] All `-005`/`-003`/`-001` carry-forward acceptance criteria continue to hold (init-keyword grammar; mode authority temporal coherence; AGENTS.md/CODEX-WAY-OF-WORKING.md in scope; `.claude/settings.json` UserPromptSubmit registration; system-interface-map.toml startup-disclosure caveat update; monitor-thread out of scope).

## Risk / Rollback

(Carried forward from `-005`. F1 of `-006` fix is a small text edit + pattern addition + one targeted test; no new risk surface.)

## Files Expected To Change (UNCHANGED from `-005`)

(All `-005` items carry forward. F1 of `-006` fix is contained within the existing `scripts/workstream_focus.py` and `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` edits; no new files added.)

## Open Follow-Ons

(Unchanged from `-005`/`-003`.)

## Recommended Commit Type

`feat:` — unchanged.

## Loyal Opposition Asks

1. Confirm F1 of `-006` closed: `guard_tool_use` blocked-reason wording at `workstream_focus.py:1178-1180` updated; `_FORBIDDEN_PATTERNS` expanded to 11 entries; targeted test added.
2. Confirm `-005`/`-003`/`-001` Loyal Opposition Asks continue to hold.
3. Confirm scope is now complete and the proposal is ready for GO unless this revision introduces new scope (per Codex's `-006` Decision wording).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
