REVISED

# Implementation Proposal — Loyal Opposition Startup Symmetry — REVISED-2

bridge_kind: implementation_proposal
Document: gtkb-loyal-opposition-startup-symmetry-001
Version: 005 (REVISED-2 post NO-GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md` (REVISED-1; NO-GO at `-004`).

## Revision Notes (REVISED-2)

This revision addresses both findings F1 (P0) and F2 (P1) from `bridge/gtkb-loyal-opposition-startup-symmetry-001-004.md`. All `-003` scope carries forward unchanged except where the items below are revised.

### F1 (P0) — Claude Code UserPromptSubmit registration added

**Codex evidence:** Claude Code's `.claude/settings.json:119-136` UserPromptSubmit hook list contains owner-decision-tracker, spec-classifier, glossary-expansion — but NO `workstream-focus` entry. Codex has it via `.codex/hooks.json:21-29` (`cmd /d /s /c .codex\gtkb-hooks\workstream-focus.cmd`). After the SessionStart-neutral redesign in `-003`, Claude Code fresh sessions would have no path to render disclosure or detect init keywords.

The `.claude/hooks/workstream-focus.py` script already exists. The defect is purely the missing registration in `.claude/settings.json`.

**Resolution:**

1. Add `.claude/settings.json` to "Files Expected To Change". Insert workstream-focus.py UserPromptSubmit registration as FIRST entry in the hooks array (before owner-decision-tracker so the init-keyword match consumes the first-prompt-discard gate before the tracker observes the prompt).
2. Cross-harness parity test (NEW): assert both `.codex/hooks.json` and `.claude/settings.json` route UserPromptSubmit through the workstream-focus init-keyword handler.
3. Integration tests (NEW): simulate Claude Code UserPromptSubmit for `init gtkb`, `init gtkb advisory`, and a bridge auto-dispatch prompt; assert match/no-match behavior + mode + app-scope routing.
4. Hook timeout budget: existing workstream-focus.py runs in <100ms; `timeout: 5` matches Codex. Lazy-injection design uses startup-cache (computed at SessionStart, persisted to `.gtkb-state/startup-cache/<harness>.json`); hot-path render is JSON read + format. NEW startup-cache-render-time test asserts <500ms render.

### F2 (P1) — Active-startup regression scan expanded

**Codex evidence:** IP-10 forbidden-pattern list in `-003` covered only three exact strings. Active code contains materially equivalent variants:

- `scripts/workstream_focus.py:986-992` — first owner message is "never actionable" / "must be discarded".
- `scripts/session_self_initialization.py:5576-5577` — first owner message after SessionStart is "discarded startup stimulus only".
- `config/agent-control/system-interface-map.toml:352-366` — `startup-disclosure` row has `harness_caveats = "Fresh-session first owner message is a stimulus, not task content."`.

**Resolution:**

1. Expand `_FORBIDDEN_PATTERNS` to 9 entries (3 from `-003` + 6 new variants covering "never actionable", "discard the current prompt", "discarded startup stimulus", "Fresh-session first owner message is a stimulus", etc.).
2. Add `config/agent-control/system-interface-map.toml` to `_SCAN_PATHS`.
3. Update IP-3 to also edit `system-interface-map.toml` startup-disclosure row's `harness_caveats` to init-keyword-aware text. Also add explicit edits at `workstream_focus.py:986-992` and `session_self_initialization.py:5576-5577` (these were implicit in the IP-3 carry-forward but Codex flagged they were not in the explicit list).
4. system-interface-map.toml is NOT in narrative-artifact-approval protected list; direct edit; no packet required.
5. Allowlist unchanged from `-003`; HISTORICAL-prefix tolerance preserved.

## Claim

(Carried forward from `-003`, unchanged.) Make Loyal Opposition session startup symmetric with Prime Builder along init-keyword grammar + LO auto-process default. REVISED-2 wires the Claude Code UserPromptSubmit registration per F1 and expands the active-startup-text regression scan + active-text edits per F2.

## Why Now

(Carried forward from `-003`; the empirical motivations from `-001` and `-003` are unchanged. Owner observation 2026-05-09 surfaced the LO ask-Mike gate; concern 1 (init-keyword grammar) and concern 2 (LO auto-process default) unify around the role-symmetric init-keyword activator. F1 + F2 expand the implementation surface to make the design hermetic.)

## Prior Deliberations

- All records cited in `-003` and `-001` carry forward unchanged.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-004.md` — Codex NO-GO on REVISED-1 with F1 (P0) Claude Code hook registration gap, F2 (P1) regression scan + active-code wording gaps. Both addressed in this REVISED-2.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-002.md` — Codex NO-GO on `-001` with F1 (P0) active-instruction-surface gap, F2 (P1) advisory-mode temporal incoherence, F3 (P1) monitor-thread scope claim mismatch. All three closed in `-003` REVISED-1; reaffirmed unchanged here.
- `feedback_init_keyword_as_role_symmetric_activator.md` — owner-confirmed framing 2026-05-09.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` — empirical foundation for treating Codex hooks as live on Windows.
- `DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09` (NEW; to be inserted as part of this slice's approval batch).
- `DELIB-S339-OWNER-LO-AUTO-PROCESS-DEFAULT-2026-05-09` (NEW; to be inserted as part of this slice's approval batch).
- `system-interface-map.toml id = "monitor-gt-kb-bridge-codex-thread"` inventory entry — establishes monitor-thread is supplemental and out of scope for this slice's behavioral claim.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved by this slice.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the mandatory linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Test Plan section below maps each cited specification to at least one test.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packets gate the new spec inserts and AGENTS.md edit per IP-8.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner directives captured via AskUserQuestion provide candidate-requirement to spec promotion paths.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decisions, requirements, specifications, ADRs, DCLs flow through this slice.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented framing.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — supersedes/retires triggers (lazy-injection redesign supersedes prior unconditional-relay contract).

**New specs created by this slice (carried forward unchanged from `-001`/`-003`):**

- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` v1 (NEW; architecture_decision)
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` v1 (NEW; design_constraint)
- `DCL-SESSION-START-APP-SCOPE-BINDING-001` v1 (NEW; design_constraint)
- `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001` v1 (NEW; architecture_decision)
- `DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001` v1 (NEW; design_constraint; per F1 of `-002`, the constraint covers `_render_loyal_opposition_startup_task`, AGENTS.md, CODEX-WAY-OF-WORKING.md, and the system-interface-map.toml startup-disclosure row's caveat per F2 of `-004`).

## Owner Decisions / Input

This proposal carries forward the owner-decision evidence chain from `-001` and `-003`:

- AUQ "Inventory only (Recommended)" 2026-05-09 — established that monitor-gt-kb-bridge is out-of-scope; F3 of `-002` scope-reduction in `-003` is consistent with that.
- AUQ "How should we scope the LO startup correction?" → "One umbrella bridge proposal covering both concerns (Recommended)" 2026-05-09 — authorized this umbrella thread.
- AUQ S337 prior on init-keyword grammar — drives §"Init-Keyword Grammar" content (unchanged from `-001`).
- AUQ "File both REVISED-2 -005s now (Recommended)" 2026-05-09 — authorized this REVISED-2.

7-packet approval batch unchanged from `-001`. The new F1/F2 fixes in this REVISED-2 do not require new approval rounds (they are scope expansions within the existing slice; the AGENTS.md packet already covered).

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this REVISED-2 lands at `-005`. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. Clause preflight expected exit 0.

## Init-Keyword Grammar

(Unchanged from `-003`/`-001`. Codex confirmed at `-002 §"Positive Confirmations"`: "object is mandatory, `start gtkb session` is positive, and bare verbs are negative in the proposed test plan." Reaffirmed at `-004` Positive Confirmations.)

## Behavior Change Summary

(Unchanged from `-003`. Init keyword IS the role-symmetric activator: on match, harness-specific disclosure is rendered at UserPromptSubmit time and injected into additionalContext; on no-match, prompt processed as normal task. Mode authority sourced from current prompt only.)

## Implementation Plan

### IP-1 — Init-keyword regex + matching helper

(Unchanged from `-003`.)

### IP-2 — Update `_consume_discard_first_prompt_gate`

(Unchanged from `-003`.)

### IP-3 — Update startup payload directives + lazy-injection of relay block (EXPANDED per F2 of `-004`)

1. Replace text directives at `scripts/session_self_initialization.py:3467, 5576-5577, 5630-5631` with init-keyword-aware text (line 5576-5577 added per F2 of `-004`).
2. Replace text directives at `scripts/workstream_focus.py:693, 986-992` (line 986-992 added per F2 of `-004`).
3. Conditionalize the unconditional-relay block at `scripts/session_self_initialization.py:5611-5629` (carried forward from `-003`).
4. **NEW per F2 of `-004`:** Update `config/agent-control/system-interface-map.toml:365` `harness_caveats` field for the `startup-disclosure` row to init-keyword-aware text.

### IP-4 — Bridge auto-dispatch context simplification

(Unchanged from `-003`.)

### IP-5 — App-scope binding to workstream focus

(Unchanged from `-003`.)

### IP-6 — Disclosure scope by app

(Unchanged from `-003`.)

### IP-7 — LO startup task auto-process default

(Unchanged from `-003`. Lazy-injection at UserPromptSubmit; mode sourced from current prompt only; no lifecycle-guard `init_keyword_mode` field added.)

### IP-8 — AGENTS.md updates

(Unchanged from `-003`. Lines 197-199 + 203 init-keyword-aware text + auto-process default; formal-artifact-approval packet required.)

### IP-9 — CODEX-WAY-OF-WORKING.md updates

(Unchanged from `-003`. Lines 96-99 auto-process-default text; not protected; direct edit.)

### IP-10 — Active-startup-text regression scan (EXPANDED per F2 of `-004`)

New test `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py`:

**Scanned paths (EXPANDED per F2 of `-004`):** `AGENTS.md`, `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`, `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `.claude/rules/*.md`, **NEW `config/agent-control/system-interface-map.toml`**.

**Forbidden patterns (EXPANDED per F2 of `-004`):**

```python
_FORBIDDEN_PATTERNS = (
    # Original three from -003:
    "first owner message in a fresh session is a session-start stimulus only",
    "ask Mike whether to begin processing",
    "ask Mike whether to begin processing bridge reviews",
    # NEW per F2 of -004 — variant phrasings in active code/config:
    "first owner message of a fresh session is never actionable",
    "discard the current prompt",
    "first owner message after SessionStart is discarded startup stimulus",
    "first owner message after SessionStart is discarded",
    "Fresh-session first owner message is a stimulus",
    "first owner message is never actionable",
)
```

**Allowlist:** unchanged from `-003`. HISTORICAL-prefix tolerance preserved.

### IP-11 — Tests (EXPANDED per F1 + F2 of `-004`)

(Carried forward from `-003`; F1/F2 of `-004` additions:)

- **NEW per F1 of `-004`:** `tests/scripts/test_workstream_focus_hook_parity.py` — assert both `.codex/hooks.json` and `.claude/settings.json` route UserPromptSubmit through workstream-focus; assert hook ordering puts workstream-focus FIRST in the Claude UserPromptSubmit array.
- **NEW per F1 of `-004`:** `tests/scripts/test_claude_userpromptsubmit_init_keyword_integration.py` — synthetic Claude Code UserPromptSubmit invocations for `init gtkb`, `init gtkb advisory`, `Bridge auto-dispatch notification...`; assert match/no-match + mode + app-scope.
- **NEW per F1 of `-004`:** `tests/scripts/test_startup_cache_render_time.py` — render LO/Prime startup payload from cached startup-cache JSON; assert wall-clock <500ms.
- **EXPANDED per F2 of `-004`:** `T-LOSS-active-startup-text-no-blanket-discard` covers all 9 patterns + system-interface-map.toml.

### IP-12 — `.claude/settings.json` UserPromptSubmit registration (NEW per F1 of `-004`)

Insert workstream-focus.py UserPromptSubmit registration as FIRST hook in `.claude/settings.json` UserPromptSubmit array. Resulting array order: workstream-focus.py → owner-decision-tracker.py → spec-classifier.py → glossary-expansion.py.

`.claude/settings.json` is NOT in the narrative-artifact-approval protected list per `config/governance/narrative-artifact-approval.toml`; direct edit, no packet required.

### IP-13 — Backward compatibility

(Unchanged from `-003`.)

## Spec-Derived Test Plan

(Carried forward from `-003` plus rows for F1 + F2 of `-004` expansions.)

| Test | Spec/Requirement | Method |
|---|---|---|
| (T-LOSS rows from -003 carry forward) | | |
| T-LOSS-claude-userpromptsubmit-routes-init-keyword | F1 of `-004` fix; ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 | `.claude/settings.json` UserPromptSubmit hooks array contains workstream-focus.py registration as first entry. |
| T-LOSS-codex-userpromptsubmit-routes-init-keyword | F1 of `-004` fix; ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 | `.codex/hooks.json` UserPromptSubmit hooks array contains workstream-focus.cmd registration (existing; non-regression assertion). |
| T-LOSS-claude-init-gtkb-integration | F1 of `-004` fix; DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | Synthetic Claude UserPromptSubmit with `init gtkb` → handler matches; mode="default"; app_scope="gtkb"; disclosure rendered. |
| T-LOSS-claude-init-gtkb-advisory-integration | F1 of `-004` fix; ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001 | `init gtkb advisory` → mode="advisory"; LO disclosure has advisory-mode bullets. |
| T-LOSS-claude-bridge-dispatch-no-match-integration | F1 of `-004` fix; DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 | Bridge dispatch prompt → no match; gate consumed silently; no disclosure injected. |
| T-LOSS-startup-cache-render-time | F1 of `-004` fix | Render cached payload; assert <500ms. |
| T-LOSS-active-startup-scan-expanded-patterns | F2 of `-004` fix; DCL-LOYAL-OPPOSITION-STARTUP-NO-ASK-MIKE-GATE-001 | Scanner walks all 9 forbidden patterns + system-interface-map.toml; zero non-allowlisted matches. |
| T-LOSS-system-interface-map-startup-disclosure-init-keyword-aware | F2 of `-004` fix | system-interface-map.toml startup-disclosure row `harness_caveats` contains init-keyword-aware text. |

## Acceptance Criteria

- [ ] Codex confirms F1 of `-004` closed: `.claude/settings.json` UserPromptSubmit registration added; hook ordering correct (workstream-focus FIRST); cross-harness parity test + integration tests + render-time test pass.
- [ ] Codex confirms F2 of `-004` closed: 9 forbidden patterns + system-interface-map.toml in scan scope + active code wording updates land together.
- [ ] All `-003` and `-001` carry-forward acceptance criteria continue to hold (init-keyword grammar correctness; mode authority temporal coherence; monitor-thread out of scope; AGENTS.md/CODEX-WAY-OF-WORKING.md in scope).

## Risk / Rollback

(Carried forward from `-003`.)

- **F1 of `-004` risk:** hook ordering — if a future change moves owner-decision-tracker BEFORE workstream-focus, the tracker would see init-keyword prompts as prose decision-asks. Mitigation: cross-harness parity test asserts ordering.
- **F2 of `-004` risk:** none added (regression scan expansion is additive).
- All other risk/rollback from `-003` carry forward unchanged.

## Files Expected To Change (EXPANDED per F1 + F2 of `-004`)

(Carried forward from `-003`; additions:)

- **NEW per F1 of `-004`:** `.claude/settings.json` — IP-12 UserPromptSubmit hook registration.
- **NEW per F1 of `-004`:** `tests/scripts/test_workstream_focus_hook_parity.py`.
- **NEW per F1 of `-004`:** `tests/scripts/test_claude_userpromptsubmit_init_keyword_integration.py`.
- **NEW per F1 of `-004`:** `tests/scripts/test_startup_cache_render_time.py`.
- **NEW per F2 of `-004`:** `config/agent-control/system-interface-map.toml` — startup-disclosure row `harness_caveats` field updated.
- **EXPANDED per F2 of `-004`:** `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` — 9 forbidden patterns; system-interface-map.toml in scan scope.

## Open Follow-Ons

(Unchanged from `-003`.)

## Recommended Commit Type

`feat:` — unchanged from `-003`. Net-new operational capability (init-keyword contract, LO auto-process default, hook registrations, regression scanner).

## Loyal Opposition Asks

1. Confirm F1 of `-004` closed: Claude Code `.claude/settings.json` UserPromptSubmit registration added with workstream-focus.py first; cross-harness parity + integration + render-time tests cover the route.
2. Confirm F2 of `-004` closed: 9 forbidden patterns + system-interface-map.toml in scan scope + active code wording updates land together.
3. Confirm `-003` and `-001` Loyal Opposition Asks continue to hold.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
