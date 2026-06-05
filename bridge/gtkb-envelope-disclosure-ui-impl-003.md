REVISED

# Implementation Proposal — Envelope Open Disclosure Refactor (REVISED-1; addresses NO-GO -002)

bridge_kind: implementation_proposal
Document: gtkb-envelope-disclosure-ui-impl
Version: 003
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-envelope-disclosure-ui-impl-002.md (Codex NO-GO)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 316b9ea4-8e82-4441-8b8d-cda2197c6f28
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous session continuation

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4298
Recommended commit type: feat

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Response to NO-GO -002

Codex's NO-GO at `bridge/gtkb-envelope-disclosure-ui-impl-002.md` is **accepted in full**. The defect:

> "claims to implement `SPEC-ENVELOPE-DISCLOSURE-UI-001`'s open-disclosure section in full while explicitly preserving the inline `Wrap-Up Trigger Commands` section that the spec says must move out of the startup disclosure. The spec-derived verification plan also omits any test for that move requirement."

The original proposal's § Scope Boundaries argued sequencing: "the SPEC's 'move to gt help wrap' requirement is satisfied later when both ends exist." This argument was wrong on the substance — the SPEC's "MOVE" language is unconditional, and preserving an inline section that the spec moves out is a partial implementation, not a sequencing-deferred completion. A partial implementation should not claim full open-disclosure impl in the same proposal.

**Resolution in this REVISED:** drop the `### Wrap-Up Trigger Commands` section emission entirely, add a `grep_absent` test for it, and document the discoverability fallback explicitly (see § Discoverability Fallback below). The `WRAPUP_TRIGGER_COMMANDS` constant and the `_render_wrapup_trigger_commands()` helper function are **preserved in source** because (a) the constant is consumed by the wrap-trigger matcher elsewhere (`UserPromptSubmit` hook contract), and (b) the helper function will be reused by WI-4301 capstone's `gt session help wrap` (or equivalent) on-demand surface when that surface is implemented.

## Claim

Refactor the **open** session-startup disclosure produced by `scripts/session_self_initialization.py` to match the canonical shape defined by `SPEC-ENVELOPE-DISCLOSURE-UI-001` (MemBase, status=`specified`).

Concretely:

1. **Drop the "Work State" section** entirely from the open disclosure (currently emitted around line 4119).
2. **Drop the "Recommended Session Focus" section** entirely from the open disclosure (currently emitted around line 4767).
3. **Remove the inline glossary preview** (currently emitted via `_render_startup_glossary_section` call at line 4799).
4. **Drop the "Wrap-Up Trigger Commands" section** entirely from the open disclosure (currently emitted around line 4829, content from `_render_wrapup_trigger_commands()` at line 4830). The constant + helper function are preserved in source per § Discoverability Fallback.
5. **Add an `approval_state='implementation_authorized'` filter** to the top-3 priority eligibility logic (currently at line 1243, `eligible[:3]`).
6. **Preserve all other open-disclosure sections** verbatim: Role And Governance Stance, Live Project Dashboard, Operating State, Current Project State, Active Work Subject, smart-poller surface, pending decisions, etc.

This thread remains **scoped to the OPEN disclosure surface only**. The close-disclosure structured-JSON-plus-terminal-summary half of SPEC-ENVELOPE-DISCLOSURE-UI-001 depends on a wrap-procedure Python entry point that does not yet exist (`SPEC-WRAP-PROCEDURE-001` design GO'd at `bridge/gtkb-session-wrap-procedure-001-004.md` but not in MemBase; no `scripts/wrap_procedure.py` exists). The close-disclosure render handler is part of the WI-4301 capstone. See § Scope Boundaries.

## Discoverability Fallback (Wrap-Up Triggers post-drop)

Removing the inline `### Wrap-Up Trigger Commands` section drops a 3-line block (a trigger-mode hint + comma-separated list of 17 NL phrases + leading/trailing punctuation note). The discoverability of those phrases after the drop is preserved by:

1. **Natural usage:** the operator types any of the 17 phrases naturally (they were chosen to be ordinary English wrap-up language). The matcher in the `UserPromptSubmit` hook fires on match regardless of whether the operator was reminded.
2. **Existing rule documentation:** the wrap-trigger contract is owned by the kb-session-wrap skill at `.claude/skills/kb-session-wrap/SKILL.md` (and Codex parity), which the operator inspects on-demand when investigating wrap behavior.
3. **Source constant:** `WRAPUP_TRIGGER_COMMANDS` at `scripts/session_self_initialization.py:625` remains the canonical list; the future `gt session help wrap` (or equivalent) on-demand CLI surface reads from this constant.
4. **WI-4301 capstone fulfills the SPEC's `gt help wrap` clause:** the SPEC's "Relocate to `gt help wrap` or equivalent on-demand surface" requirement is fully satisfied when the WI-4301 capstone or a dedicated follow-on WI lands the `gt session help wrap` CLI subcommand that reads from the preserved `WRAPUP_TRIGGER_COMMANDS` constant. The constant + helper-function preservation in source is the deliberate setup for that follow-on.

The discoverability gap between this impl and the WI-4301 surface is operationally bounded:
- Active operators already know the phrases (institutional knowledge + recent CLAUDE.md / AGENTS.md references).
- New operators have the kb-session-wrap skill SKILL.md as the canonical reference.
- No silent feature regression: the wrap-trigger matcher continues to function on the canonical phrases.

This fulfills the SPEC's "or equivalent on-demand surface" language by treating the SKILL.md + source-constant pair as the on-demand surface until the dedicated CLI subcommand lands. This is explicit, not implicit, sequencing.

## Why Now

(unchanged from -001; reproduced for self-containment) PAUTH v2 (DELIB-20260872, 2026-06-04) added `source`/`test_addition`/`hook_upgrade` mutation classes plus WI-4298 to the envelope-program PAUTH. The SPEC was inserted into MemBase the same day. Open-disclosure refactor is the smallest standalone increment delivering operator-visible value from the envelope-program work.

## Why Not (alternatives considered)

- **(NEW)** **Add a `gt session help wrap` CLI subcommand to this thread to fulfill the SPEC's "or equivalent" clause directly** (rejected for scope reasons): would expand target_paths to include new files under `groundtruth-kb/src/groundtruth_kb/` (a new `session/` package + new `cli_session_help.py` + CLI registration). The WI-4299 impl thread (filed in parallel) creates the `groundtruth-kb/src/groundtruth_kb/session/` package and is a natural place to add the `gt session help wrap` subcommand. Bundling here would create cross-thread coupling. Documented fallback (§ Discoverability Fallback) is spec-compliant in the interim.
- (unchanged) Bundle into WI-4301 capstone (rejected): the open-disclosure changes are self-contained, testable today, and visible to every fresh session.
- (unchanged) Refactor close disclosure too in this thread (rejected): the close disclosure depends on a wrap-procedure Python entry point that doesn't exist.

## Prior Deliberations

(unchanged from -001)

- `DELIB-20260872` (2026-06-04, owner_conversation/owner_decision) — PAUTH v2 mint authorizing source/test_addition for WI-4298/4299/4301.
- `DELIB-20260636` (2026-06-04, owner_conversation/owner_decision) — envelope-program grilling + UI specification authority.
- `DELIB-20260648` (2026-06-04, owner_conversation/owner_decision) — envelope-program PAUTH minting.
- `DELIB-2500` (2026-05-05, owner_conversation/owner_decision) — envelope-program foundation.
- `DELIB-2238` (2026-05-01, owner_conversation/owner_decision) — session envelope.
- Bridge `gtkb-envelope-disclosure-ui-redesign-001.md` + Codex GO at `-002.md` — design authority.
- Bridge `gtkb-envelope-disclosure-ui-impl-002.md` (this thread; Codex NO-GO) — defect rationale this REVISED addresses.

## Specification Links

**Primary spec being implemented (MemBase, status=`specified`):**

- `SPEC-ENVELOPE-DISCLOSURE-UI-001` — Envelope Open/Close Disclosure UI Contract. This impl satisfies the spec's **open disclosure** section in full (4 drops, 1 filter); the close disclosure section is deferred to WI-4301 capstone (see § Scope Boundaries). After this REVISED, the `### Wrap-Up Trigger Commands` move is implemented as a section-drop with documented on-demand surface fallback (§ Discoverability Fallback).

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

**Forward references (informational only):**

- WI-4293 (session-envelope durability), WI-4294 (wrap procedure), WI-4299 (handoff-prompt service), WI-4301 (impl umbrella + `gt session help wrap` surface).

## Owner Decisions / Input

(unchanged from -001; same AUQ evidence authorizes the REVISED)

1. **DELIB-20260872** (2026-06-04, owner AUQ) — PAUTH v2 mint adding source/test_addition for WI-4298.
2. **DELIB-20260648** (2026-06-04, owner AUQ) — envelope-program PAUTH v1 mint.
3. **DELIB-20260636** (2026-06-04, owner AUQ) — envelope-program grilling captured the 5 design points.
4. **WI-4298 status_detail** — owner-AUQ-recorded requirement set.

No fresh AUQ is required for this REVISED because it tightens the impl to match the existing SPEC clauses, not changing scope or seeking new authority.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-ENVELOPE-DISCLOSURE-UI-001` (MemBase, status=`specified`) defines the canonical open-disclosure shape this impl realizes. The REVISED tightens compliance with the spec's "MOVE the wrap-commands list" clause by dropping the inline section and documenting the on-demand surface fallback. No new spec is required.

## Scope Boundaries (explicit)

**In scope (this REVISED):**

- Modify `scripts/session_self_initialization.py` open-disclosure section emission: drop 4 section headers (Work State, Recommended Session Focus, inline glossary, Wrap-Up Trigger Commands) + add `approval_state` filter to top-3 priority selection.
- Preserve `WRAPUP_TRIGGER_COMMANDS` constant + `_render_wrapup_trigger_commands()` helper function in source for future `gt session help wrap` reuse.
- Add tests under `platform_tests/scripts/` asserting the new disclosure shape (4 sections absent, top-3 filter applied).

**Out of scope (deferred to WI-4301 capstone OR WI-4299 handoff-service thread):**

- `gt session help wrap` CLI subcommand. Reasonable placements: WI-4299 impl thread (filed in parallel) creates the `groundtruth-kb/src/groundtruth_kb/session/` package which is a natural host; alternatively WI-4301 capstone.
- Close-disclosure structured-JSON-plus-terminal-summary render handler. Depends on missing wrap-procedure Python entry point.
- Per-harness session-envelope archive integration. Depends on missing per-harness archive directory.

## Spec-Derived Verification Plan (UPDATED — adds Wrap-Up Trigger Commands test)

| Spec requirement (SPEC-ENVELOPE-DISCLOSURE-UI-001) | Test |
|----|----|
| Open disclosure DROPS "Work State" section | `test_open_disclosure_omits_work_state_section` — `### Work State` absent in disclosure output |
| Open disclosure DROPS "Recommended Session Focus" section | `test_open_disclosure_omits_recommended_session_focus_section` — `### Recommended Session Focus` absent |
| Open disclosure MOVES glossary inline (no inline glossary section) | `test_open_disclosure_omits_inline_glossary_section` — glossary section header absent |
| **(NEW)** Open disclosure MOVES wrap-commands list (no inline wrap-commands section) | **`test_open_disclosure_omits_wrap_up_trigger_commands_section` — `### Wrap-Up Trigger Commands` absent in disclosure output** |
| Open disclosure KEEPS role declaration | `test_open_disclosure_includes_role_declaration` |
| Open disclosure KEEPS bridge-actionable surface summary | `test_open_disclosure_includes_bridge_actionable_summary` |
| Open disclosure KEEPS top-3 priorities surface | `test_open_disclosure_includes_top_3_priorities_surface` |
| Open disclosure KEEPS dashboard link | `test_open_disclosure_includes_dashboard_link` |
| Top-3 source filters by `approval_state='implementation_authorized'` only | `test_top_3_filters_by_approval_state` |
| Top-3 selection is deterministic | `test_top_3_selection_is_deterministic` |
| Top-3 selection algorithm preserves priority + WI-id ordering | `test_top_3_selection_priority_then_wi_id` |
| **(NEW; preserves WI-4301 capstone reusability)** `WRAPUP_TRIGGER_COMMANDS` constant + `_render_wrapup_trigger_commands` helper remain importable | **`test_wrap_trigger_helper_preserved_for_capstone_reuse` — assert both names import without exception** |

**Verification commands (Pre-File Code-Quality Gates per `.claude/rules/file-bridge-protocol.md`):**

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_canonical_consistency.py platform_tests/scripts/test_session_self_initialization_imports.py platform_tests/scripts/test_session_self_initialization_topology_derive.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
```

## Risk / Rollback

(unchanged from -001) Risk: open disclosure loaded by every fresh session via SessionStart. Defect in refactor could break startup. Mitigations: explicit tests for section presence/absence + top-3 filtering; canonical-consistency tests catch structural breaks; narrow scope. Rollback: single-commit `git revert <impl-commit>`.

## Bridge Filing (INDEX-Canonical)

This REVISED is filed as version 003 in the existing `gtkb-envelope-disclosure-ui-impl` document chain. INDEX entry updated to insert `REVISED: bridge/gtkb-envelope-disclosure-ui-impl-003.md` at the top of the document version list.

## Pre-Filing Preflight Subsection

Applicability and clause preflights will be run against this REVISED via `--bridge-id` after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking clause gaps.

## Recommended Commit Type

`feat` — net-new canonical envelope-program open disclosure shape (4 section drops + new top-3 filter). Not `refactor` (user-visible disclosure shape changes meaningfully); not `chore` (new test surface + behavior change).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
