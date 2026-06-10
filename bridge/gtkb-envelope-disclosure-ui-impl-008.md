REVISED

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2d0a56f2-6886-4de5-baf0-799055b4ecc2
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous session continuation

# Implementation Proposal — Envelope Open Disclosure Refactor (REVISED-3; addresses NO-GO -007)

bridge_kind: prime_proposal
Document: gtkb-envelope-disclosure-ui-impl
Version: 008
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-envelope-disclosure-ui-impl-007.md (Codex NO-GO; single finding)

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

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Response to NO-GO -007 (FINDING-P1-001)

**Accepted in full.** The proposal's `target_paths` omitted `platform_tests/scripts/test_session_self_initialization.py`, yet the verification command requires running it, and that file currently contains assertions for the sections being removed. This creates an authorization gap: Prime cannot both pass the verification command and stay within the approved scope without updating that file.

**Resolution:** Add `platform_tests/scripts/test_session_self_initialization.py` to `target_paths` and to the explicit scope section. The existing assertions that pin the old disclosure shape must be updated or removed as part of this implementation — they contradict `SPEC-ENVELOPE-DISCLOSURE-UI-001` and would otherwise cause the verification command to fail. See § Scope Boundaries and § Existing Test File Updates.

No other findings remain from the prior NO-GO chain. All prior resolutions (REVISED-1 and REVISED-2) are carried forward unchanged.

## Carried Forward from REVISED-2 (-006)

### Response to Supplemental NO-GO -005 (additive to Codex NO-GO -004) — resolved (unchanged)

See REVISED-2 for full text. Summary:
- Codex -004 FINDING-P1-001 (false DELIB citation): `DELIB-20260648` removed; correct PAUTH is `DELIB-20260872`.
- Supplemental -005 FINDING-P1-001 (approval_state stripped): `_backlog_items_from_membase` projection expanded to include `approval_state`.
- Supplemental -005 FINDING-P2-001 (resolution_status filter not tested): `test_top_3_excludes_resolved_and_verified_wis` added.
- Supplemental -005 FINDING-P2-002 (eligible[:3] at two sites): compute `top_priority` once, reference at both sites.
- Supplemental -005 FINDING-P2-003 (SKILL.md discoverability misstatement): corrected per § Discoverability Fallback.

### Response to NO-GO -002 (wrap-commands finding) — resolved (unchanged)

`### Wrap-Up Trigger Commands` section emission dropped, absence test added, `WRAPUP_TRIGGER_COMMANDS` constant + helper preserved.

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
9. **Update existing assertions in `platform_tests/scripts/test_session_self_initialization.py`** that assert the removed sections are present: these assertions now contradict `SPEC-ENVELOPE-DISCLOSURE-UI-001` and must be updated or removed. See § Existing Test File Updates.

This thread remains **scoped to the OPEN disclosure surface only**. See § Scope Boundaries.

## Existing Test File Updates

`platform_tests/scripts/test_session_self_initialization.py` currently contains assertions that pin the old disclosure shape. These must be updated as part of this implementation because they contradict `SPEC-ENVELOPE-DISCLOSURE-UI-001`:

| Location | Current assertion | Required change |
|---|---|---|
| Lines 1194-1207 | Asserts `Wrap-Up Trigger Commands`, accepted wrap commands, and `Recommended Session Focus` appear in startup report | Remove or relax assertions for the 4 dropped sections; add absence assertions aligned with the new shape |
| Lines 1360-1371 | Asserts `### Wrap-Up Trigger Commands` and `### Recommended Session Focus` appear in context | Same — remove or replace with absence assertions |
| Lines 1866-1868 | Asserts wrap-command section appears in generated hook context | Same — update to assert absence |

The existing test file retains all non-disclosure-shape test coverage. Only the assertions that conflict with the new SPEC-mandated shape are updated or removed. The dedicated new test file `test_session_self_initialization_disclosure_shape.py` provides the focused positive and negative coverage for the new shape; the existing file's changes are the minimum needed to make the verification command pass without false failures.

## Discoverability Fallback (Wrap-Up Triggers post-drop; corrected per -005 FINDING-P2-003)

(Unchanged from REVISED-2.)

1. **Natural usage:** active operators already know the phrases.
2. **Source constant:** `WRAPUP_TRIGGER_COMMANDS` at `scripts/session_self_initialization.py:625` remains the canonical enumerated list.
3. **Phrase-enumeration gap:** `.claude/skills/kb-session-wrap/SKILL.md` does NOT enumerate the 17 trigger phrases. Gap acknowledged and bounded by WI-4301 delivery timeline.
4. **WI-4301 capstone closes the gap.**
5. **No silent feature regression:** the wrap-trigger matcher continues to function.

## Why Now

(Unchanged.) PAUTH v2 (DELIB-20260872, 2026-06-04) added `source`/`test_addition`/`hook_upgrade` plus WI-4298 to the envelope-program PAUTH. Open-disclosure refactor is the smallest standalone increment delivering operator-visible value.

## Why Not (alternatives considered)

(Unchanged from REVISED-2.)

## Prior Deliberations

- `DELIB-20260872` (2026-06-04, owner_conversation/owner_decision) — PAUTH v2 mint authorizing source/test_addition for WI-4298/4299/4301.
- `DELIB-20260636` (2026-06-04, owner_conversation/owner_decision) — envelope-program grilling + UI specification authority.
- `DELIB-2500` (2026-05-05, owner_conversation/owner_decision) — envelope-program foundation.
- `DELIB-2238` (2026-05-01, owner_conversation/owner_decision) — session envelope.
- Bridge `gtkb-envelope-disclosure-ui-redesign-001.md` + Codex GO at `-002.md` — design authority.
- Bridge `gtkb-envelope-disclosure-ui-impl-002.md` (this thread; Codex NO-GO) — wrap-commands defect.
- Bridge `gtkb-envelope-disclosure-ui-impl-004.md` (this thread; Codex NO-GO) — false DELIB-20260648 citation.
- Bridge `gtkb-envelope-disclosure-ui-impl-005.md` (this thread; Supplemental LO NO-GO) — approval_state pipeline, resolution_status test, eligibility consistency, discoverability misstatement.
- Bridge `gtkb-envelope-disclosure-ui-impl-007.md` (this thread; Codex NO-GO) — target_paths omitted existing test file addressed in this REVISED-3.

## Specification Links

**Primary spec being implemented (MemBase, status=`specified`):**

- `SPEC-ENVELOPE-DISCLOSURE-UI-001` — Envelope Open/Close Disclosure UI Contract.

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

No fresh AUQ is required for this REVISED-3. Adding the existing test file to `target_paths` is a mechanical authorization fix required by the already-approved implementation scope; it does not expand the feature scope.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-ENVELOPE-DISCLOSURE-UI-001` (MemBase, status=`specified`) defines the canonical open-disclosure shape this impl realizes. The existing test-file assertion updates are mechanical necessities of the existing spec requirements.

## Scope Boundaries (explicit)

**In scope (this REVISED-3):**

- `scripts/session_self_initialization.py`:
  - Drop 4 section headers (Work State, Recommended Session Focus, inline glossary, Wrap-Up Trigger Commands) from open disclosure.
  - Extend `_backlog_items_from_membase` projection to preserve `approval_state`.
  - Add `approval_state='implementation_authorized'` filter to `_backlog_metrics`; compute `top_priority` once, use at both consumption sites.
  - Verify/add `resolution_status in ('open','in_progress','blocked')` filter.
  - Preserve `WRAPUP_TRIGGER_COMMANDS` constant + `_render_wrapup_trigger_commands()` helper.
- `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`:
  - New test file with all verification plan tests (new disclosure shape coverage).
- `platform_tests/scripts/test_session_self_initialization.py`:
  - Update or remove existing assertions that contradict `SPEC-ENVELOPE-DISCLOSURE-UI-001` (the sections being dropped). Only the assertions that pin the old shape are changed; all other test coverage is preserved.

**Out of scope (deferred):**

- `gt session help wrap` CLI subcommand (WI-4299 / WI-4301 capstone).
- Close-disclosure render handler.
- Per-harness session-envelope archive integration.

## Spec-Derived Verification Plan (unchanged from REVISED-2 except existing-file note)

| Spec requirement (SPEC-ENVELOPE-DISCLOSURE-UI-001) | Test |
|----|----|
| Open disclosure DROPS "Work State" section | `test_open_disclosure_omits_work_state_section` |
| Open disclosure DROPS "Recommended Session Focus" section | `test_open_disclosure_omits_recommended_session_focus_section` |
| Open disclosure MOVES glossary inline (no inline glossary) | `test_open_disclosure_omits_inline_glossary_section` |
| Open disclosure MOVES wrap-commands list (no inline section) | `test_open_disclosure_omits_wrap_up_trigger_commands_section` |
| Open disclosure KEEPS role declaration | `test_open_disclosure_includes_role_declaration` |
| Open disclosure KEEPS bridge-actionable surface summary | `test_open_disclosure_includes_bridge_actionable_summary` |
| Open disclosure KEEPS top-3 priorities surface | `test_open_disclosure_includes_top_3_priorities_surface` |
| Open disclosure KEEPS dashboard link | `test_open_disclosure_includes_dashboard_link` |
| **(Pipeline fix)** `approval_state` field preserved through `_backlog_items_from_membase` | `test_backlog_items_preserve_approval_state_field` |
| Top-3 source filters by `approval_state='implementation_authorized'` only | `test_top_3_filters_by_approval_state` |
| **(NEW — resolution_status clause)** Top-3 excludes resolved/verified WIs | `test_top_3_excludes_resolved_and_verified_wis` |
| **(NEW — consistency fix)** Dict `top_priority_actions` equals tuple return | `test_top_priority_dict_and_tuple_are_identical` |
| Top-3 selection is deterministic | `test_top_3_selection_is_deterministic` |
| Top-3 selection algorithm preserves priority + WI-id ordering | `test_top_3_selection_priority_then_wi_id` |
| `WRAPUP_TRIGGER_COMMANDS` constant + `_render_wrapup_trigger_commands` helper remain importable | `test_wrap_trigger_helper_preserved_for_capstone_reuse` |

**Verification commands:**

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_canonical_consistency.py platform_tests/scripts/test_session_self_initialization_imports.py platform_tests/scripts/test_session_self_initialization_topology_derive.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_self_initialization.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_self_initialization.py
```

## Risk / Rollback

Risk: open disclosure loaded by every fresh session via SessionStart. Defect in refactor could break startup. Mitigations: explicit tests for section presence/absence + filters + pipeline + consistency; canonical-consistency tests catch structural breaks; narrow scope. Updating existing test file is the minimum-change path (only old-shape assertions are touched, not the test structure). Rollback: single-commit `git revert <impl-commit>`.

## Applicability Preflight

- packet_hash: `sha256:bb141020768647e5b95a23ad3adfdb25ccbb06dcb7a51849c0c0fef0138fc98b`
- bridge_document_name: `gtkb-envelope-disclosure-ui-impl`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-envelope-disclosure-ui-impl-006.md`
- operative_file: `bridge/gtkb-envelope-disclosure-ui-impl-006.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

*(Preflight carried from -006; no spec citations changed in this revision. REVISED-3 is a target_paths scope fix only.)*

## Recommended Commit Type

`feat` — net-new canonical envelope-program open disclosure shape (4 section drops + pipeline fix + dual-site eligibility filter + resolution_status filter + new test surface + existing test file alignment).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
