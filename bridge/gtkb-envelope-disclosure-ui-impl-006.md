REVISED

# Implementation Proposal — Envelope Open Disclosure Refactor (REVISED-2; addresses NO-GO -004 + Supplemental NO-GO -005)

bridge_kind: implementation_proposal
Document: gtkb-envelope-disclosure-ui-impl
Version: 006
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-envelope-disclosure-ui-impl-005.md (Supplemental LO NO-GO; also addresses bridge/gtkb-envelope-disclosure-ui-impl-004.md Codex NO-GO)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2d0a56f2-6886-4de5-baf0-799055b4ecc2
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

## Response to Supplemental NO-GO -005 (additive to Codex NO-GO -004)

Supplemental NO-GO at `bridge/gtkb-envelope-disclosure-ui-impl-005.md` (author session `7ee2f6b5-943b-48c9-ad27-12610b2ae7b4`) is **accepted in full**. Four findings from that review, plus one finding from Codex's prior `-004`:

### Codex -004 FINDING-P1-001 (false DELIB citation) — resolved

`DELIB-20260648` has been removed from `## Prior Deliberations` and `## Owner Decisions / Input`. It was incorrectly cited as "envelope-program PAUTH minting" in REVISED-1; the live DA record is about init-keyword optionality (WI-4291). The correct PAUTH v2 authorization is `DELIB-20260872`.

### Supplemental -005 FINDING-P1-001 (approval_state stripped by pipeline) — resolved

The `_backlog_items_from_membase` function projects each raw CLI row into `{id, title, body}` only, stripping `approval_state` before it can be used at the `eligible[:3]` filter sites. **Resolution:** expand the projection to also carry `approval_state` (defaulting to `""` when absent from the CLI row). The scope description and verification plan below reflect this additional `_backlog_items_from_membase` change, which remains within the existing `target_paths`.

### Supplemental -005 FINDING-P2-001 (resolution_status filter not tested) — resolved

Added `test_top_3_excludes_resolved_and_verified_wis` to the verification plan (maps to the `resolution_status in ('open','in_progress','blocked')` SPEC clause). The implementation notes whether `gt backlog list --json` applies this filter upstream or whether `_backlog_metrics` must apply it explicitly; the test covers the behavior regardless.

### Supplemental -005 FINDING-P2-002 (eligible[:3] at two sites) — resolved

`_backlog_metrics` at lines 1243 and 1249 computes `eligible[:3]` twice. **Resolution:** compute `top_priority = [eligible_filtered][:3]` once and reference `top_priority` in both the dict entry and the tuple return. Added `test_top_priority_dict_and_tuple_are_identical` to the verification plan.

### Supplemental -005 FINDING-P2-003 (SKILL.md discoverability misstatement) — resolved

The SKILL.md claim has been corrected in § Discoverability Fallback below. The corrected text acknowledges the phrase-enumeration gap honestly and bounds it by the WI-4301 timeline.

## Response to NO-GO -002

(carried forward from REVISED-1; unchanged) Codex's wrap-commands finding was fully addressed in REVISED-1 (-003): `### Wrap-Up Trigger Commands` section emission dropped, absence test added, WRAPUP_TRIGGER_COMMANDS constant + helper preserved. Those changes remain in this REVISED-2.

## Claim

Refactor the **open** session-startup disclosure produced by `scripts/session_self_initialization.py` to match the canonical shape defined by `SPEC-ENVELOPE-DISCLOSURE-UI-001` (MemBase, status=`specified`).

Concretely:

1. **Drop the "Work State" section** entirely from the open disclosure (currently emitted around line 4119).
2. **Drop the "Recommended Session Focus" section** entirely from the open disclosure (currently emitted around line 4767).
3. **Remove the inline glossary preview** (currently emitted via `_render_startup_glossary_section` call at line 4799).
4. **Drop the "Wrap-Up Trigger Commands" section** entirely from the open disclosure (currently emitted around line 4829, content from `_render_wrapup_trigger_commands()` at line 4830). The constant + helper function are preserved in source per § Discoverability Fallback.
5. **Add `approval_state` to the `_backlog_items_from_membase` projection** (currently at lines 1172-1178): extend the dict to `{id, title, body, approval_state}` so the field survives to the filter sites downstream.
6. **Add an `approval_state='implementation_authorized'` filter** to the top-3 priority eligibility logic in `_backlog_metrics`. Compute `top_priority = [item for item in eligible if item.get('approval_state') == 'implementation_authorized'][:3]` (or equivalent) once, and use `top_priority` at both consumption sites (the dict entry at line ~1243 and the tuple return at line ~1249) so the two surfaces remain consistent.
7. **Verify `resolution_status` filtering behavior** at `_backlog_items_from_membase` or `_backlog_metrics`: confirm whether `gt backlog list --json` defaults include `resolution_status` filtering, and if not, add an explicit filter for `resolution_status in ('open','in_progress','blocked')` at the appropriate site.
8. **Preserve all other open-disclosure sections** verbatim: Role And Governance Stance, Live Project Dashboard, Operating State, Current Project State, Active Work Subject, smart-poller surface, pending decisions, etc.

This thread remains **scoped to the OPEN disclosure surface only**. See § Scope Boundaries.

## Discoverability Fallback (Wrap-Up Triggers post-drop; corrected per -005 FINDING-P2-003)

Removing the inline `### Wrap-Up Trigger Commands` section drops the 17 NL trigger phrases from the startup disclosure. Discoverability post-drop:

1. **Natural usage:** active operators already know the phrases (institutional knowledge + usage). The matcher fires regardless of whether a reminder is present.
2. **Source constant:** `WRAPUP_TRIGGER_COMMANDS` at `scripts/session_self_initialization.py:625` remains the canonical enumerated list. It is the authoritative phrase reference until the WI-4301 surface lands.
3. **Phrase-enumeration gap:** `.claude/skills/kb-session-wrap/SKILL.md` is a procedural wrap-up guide and does NOT enumerate the 17 trigger phrases. New operators have no enumerated phrase reference between this impl and the WI-4301 capstone. This gap is acknowledged and bounded by the WI-4301 delivery timeline; the SPEC's "or equivalent on-demand surface" language explicitly permits this phasing.
4. **WI-4301 capstone closes the gap:** the SPEC's "Relocate to `gt help wrap` or equivalent on-demand surface" requirement is fully satisfied when WI-4301 or a dedicated follow-on WI lands the `gt session help wrap` CLI subcommand reading from the preserved `WRAPUP_TRIGGER_COMMANDS` constant.
5. **No silent feature regression:** the wrap-trigger matcher in the `UserPromptSubmit` hook continues to function on the canonical phrases regardless of surface coverage.

## Why Now

(unchanged) PAUTH v2 (DELIB-20260872, 2026-06-04) added `source`/`test_addition`/`hook_upgrade` plus WI-4298 to the envelope-program PAUTH. The SPEC was inserted into MemBase the same day. Open-disclosure refactor is the smallest standalone increment delivering operator-visible value from the envelope-program work.

## Why Not (alternatives considered)

- **(NEW)** **Add a `gt session help wrap` CLI subcommand to this thread** (rejected for scope reasons): would expand target_paths to include files under `groundtruth-kb/src/groundtruth_kb/`. WI-4299 impl creates that package and is the natural host. Documented fallback (§ Discoverability Fallback) is spec-compliant in the interim.
- Bundle into WI-4301 capstone (rejected): open-disclosure changes are self-contained, testable today, visible to every fresh session.
- Refactor close disclosure too (rejected): depends on missing wrap-procedure Python entry point.

## Prior Deliberations

- `DELIB-20260872` (2026-06-04, owner_conversation/owner_decision) — PAUTH v2 mint authorizing source/test_addition for WI-4298/4299/4301.
- `DELIB-20260636` (2026-06-04, owner_conversation/owner_decision) — envelope-program grilling + UI specification authority.
- `DELIB-2500` (2026-05-05, owner_conversation/owner_decision) — envelope-program foundation.
- `DELIB-2238` (2026-05-01, owner_conversation/owner_decision) — session envelope.
- Bridge `gtkb-envelope-disclosure-ui-redesign-001.md` + Codex GO at `-002.md` — design authority.
- Bridge `gtkb-envelope-disclosure-ui-impl-002.md` (this thread; Codex NO-GO) — wrap-commands defect addressed in REVISED-1.
- Bridge `gtkb-envelope-disclosure-ui-impl-004.md` (this thread; Codex NO-GO) — false DELIB-20260648 citation addressed in this REVISED-2.
- Bridge `gtkb-envelope-disclosure-ui-impl-005.md` (this thread; Supplemental LO NO-GO) — approval_state pipeline gap, resolution_status test gap, multi-site eligibility inconsistency, and discoverability misstatement addressed in this REVISED-2.

## Specification Links

**Primary spec being implemented (MemBase, status=`specified`):**

- `SPEC-ENVELOPE-DISCLOSURE-UI-001` — Envelope Open/Close Disclosure UI Contract. This impl satisfies the spec's **open disclosure** section in full (4 drops, 2 filter additions, 1 pipeline fix); the close disclosure section is deferred to WI-4301 capstone.

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

1. **DELIB-20260872** (2026-06-04, owner AUQ) — PAUTH v2 mint adding source/test_addition for WI-4298/4299/4301.
2. **DELIB-20260636** (2026-06-04, owner AUQ) — envelope-program grilling captured the 5 design points.
3. **WI-4298 status_detail** — owner-AUQ-recorded requirement set.

No fresh AUQ is required for this REVISED-2. The pipeline preservation of `approval_state` is a necessary mechanical expansion within the existing `target_paths` to implement the already-approved filter behavior. All other changes address NO-GO findings without scope expansion.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-ENVELOPE-DISCLOSURE-UI-001` (MemBase, status=`specified`) defines the canonical open-disclosure shape this impl realizes. The expanded scope (pipeline fix + both-site filter consistency + resolution_status test) are mechanical necessities of the existing filter requirements, not new requirements.

## Scope Boundaries (explicit)

**In scope (this REVISED-2):**

- `scripts/session_self_initialization.py`:
  - Drop 4 section headers (Work State, Recommended Session Focus, inline glossary, Wrap-Up Trigger Commands) from open disclosure.
  - Extend `_backlog_items_from_membase` projection to preserve `approval_state`.
  - Add `approval_state='implementation_authorized'` filter to `_backlog_metrics`; compute `top_priority` once, use at both `eligible[:3]` consumption sites.
  - Verify/add `resolution_status in ('open','in_progress','blocked')` filter at appropriate site.
  - Preserve `WRAPUP_TRIGGER_COMMANDS` constant + `_render_wrapup_trigger_commands()` helper.
- `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`:
  - New test file with all verification plan tests.

**Out of scope (deferred):**

- `gt session help wrap` CLI subcommand (WI-4299 / WI-4301 capstone).
- Close-disclosure render handler (depends on missing wrap-procedure entry point).
- Per-harness session-envelope archive integration.

## Spec-Derived Verification Plan (UPDATED — adds pipeline, resolution_status, and consistency tests)

| Spec requirement (SPEC-ENVELOPE-DISCLOSURE-UI-001) | Test |
|----|----|
| Open disclosure DROPS "Work State" section | `test_open_disclosure_omits_work_state_section` — `### Work State` absent |
| Open disclosure DROPS "Recommended Session Focus" section | `test_open_disclosure_omits_recommended_session_focus_section` |
| Open disclosure MOVES glossary inline (no inline glossary) | `test_open_disclosure_omits_inline_glossary_section` |
| Open disclosure MOVES wrap-commands list (no inline section) | `test_open_disclosure_omits_wrap_up_trigger_commands_section` — `### Wrap-Up Trigger Commands` absent |
| Open disclosure KEEPS role declaration | `test_open_disclosure_includes_role_declaration` |
| Open disclosure KEEPS bridge-actionable surface summary | `test_open_disclosure_includes_bridge_actionable_summary` |
| Open disclosure KEEPS top-3 priorities surface | `test_open_disclosure_includes_top_3_priorities_surface` |
| Open disclosure KEEPS dashboard link | `test_open_disclosure_includes_dashboard_link` |
| **(Pipeline fix)** `approval_state` field preserved through `_backlog_items_from_membase` | `test_backlog_items_preserve_approval_state_field` — fixture items with `approval_state` survive projection |
| Top-3 source filters by `approval_state='implementation_authorized'` only | `test_top_3_filters_by_approval_state` — non-implementation_authorized items excluded |
| **(NEW — resolution_status clause)** Top-3 excludes resolved/verified WIs | `test_top_3_excludes_resolved_and_verified_wis` — items with `resolution_status` not in `('open','in_progress','blocked')` excluded |
| **(NEW — consistency fix)** Dict `top_priority_actions` equals tuple return | `test_top_priority_dict_and_tuple_are_identical` — asserts both surfaces yield the same list |
| Top-3 selection is deterministic | `test_top_3_selection_is_deterministic` |
| Top-3 selection algorithm preserves priority + WI-id ordering | `test_top_3_selection_priority_then_wi_id` |
| `WRAPUP_TRIGGER_COMMANDS` constant + `_render_wrapup_trigger_commands` helper remain importable | `test_wrap_trigger_helper_preserved_for_capstone_reuse` |

**Verification commands:**

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_canonical_consistency.py platform_tests/scripts/test_session_self_initialization_imports.py platform_tests/scripts/test_session_self_initialization_topology_derive.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
```

## Risk / Rollback

Risk: open disclosure loaded by every fresh session via SessionStart. Defect in refactor could break startup. Mitigations: explicit tests for section presence/absence + filters + pipeline + consistency; canonical-consistency tests catch structural breaks; narrow scope. Rollback: single-commit `git revert <impl-commit>`.

## Bridge Filing (INDEX-Canonical)

This REVISED-2 is filed as version 006 in the existing `gtkb-envelope-disclosure-ui-impl` document chain. INDEX entry updated to insert `REVISED: bridge/gtkb-envelope-disclosure-ui-impl-006.md` at the top of the document version list.

## Pre-Filing Preflight Subsection

Applicability and clause preflights will be run against this REVISED-2 via `--bridge-id` after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking clause gaps.

## Recommended Commit Type

`feat` — net-new canonical envelope-program open disclosure shape (4 section drops + pipeline fix + dual-site eligibility filter + resolution_status filter + new test surface).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
