NEW

# Implementation Proposal — Envelope Open Disclosure Refactor (WI-4298 impl, scoped to open surface)

bridge_kind: prime_proposal
Document: gtkb-envelope-disclosure-ui-impl
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC

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

## Claim

Refactor the **open** session-startup disclosure produced by `scripts/session_self_initialization.py` to match the canonical shape defined by `SPEC-ENVELOPE-DISCLOSURE-UI-001` (MemBase, status=`specified`, inserted 2026-06-04T14:41:07Z per Codex GO at `bridge/gtkb-envelope-disclosure-ui-redesign-002.md`).

Concretely, this impl:

1. **Drops the "Work State" section** entirely from the open disclosure (currently emitted around `scripts/session_self_initialization.py:4119`). The bridge-actionable summary already covers the operationally-meaningful subset.
2. **Drops the "Recommended Session Focus" section** entirely from the open disclosure (currently emitted around line 4767). The top-3 priorities provide the forward path.
3. **Removes the inline glossary preview** (currently emitted via `_render_startup_glossary_section` call at line 4799). Glossary continues to be available via the existing AXIS 2 surface and `gt help` on-demand path; it is no longer inlined in startup disclosure.
4. **Adds an `approval_state='implementation_authorized'` filter** to the top-3 priority eligibility logic (currently at line 1243, `eligible[:3]`). The filter rejects WIs whose `approval_state` is one of `unapproved`, `auq_required`, or `auq_resolved` so the top-3 only surfaces implementation-ready work.
5. **Preserves all other open-disclosure sections** verbatim: Role And Governance Stance, Live Project Dashboard, Operating State, Current Project State, Active Work Subject, smart-poller surface, pending decisions, Wrap-Up Trigger Commands, etc.

This thread is **scoped to the OPEN disclosure surface only**. The close-disclosure structured-JSON-plus-terminal-summary half of SPEC-ENVELOPE-DISCLOSURE-UI-001 depends on a wrap-procedure Python entry point that does not yet exist (`SPEC-WRAP-PROCEDURE-001` design GO'd at `bridge/gtkb-session-wrap-procedure-001-004.md` but not in MemBase; no `scripts/wrap_procedure.py` exists yet). The close-disclosure render handler is properly part of the WI-4301 capstone (which integrates the wrap procedure + envelope durability + handoff service + disclosure surfaces). See § Scope Boundaries below.

## Why Now

PAUTH v2 (DELIB-20260872, 2026-06-04) added `source`/`test_addition`/`hook_upgrade` mutation classes plus WI-4298/4299/4301 to the envelope-program PAUTH's `included_work_item_ids` list, unblocking source-level implementation. The SPEC was inserted into MemBase the same day. With the spec landed and the PAUTH unblocked, the open-disclosure refactor is the smallest standalone increment that delivers operator-visible value from the envelope-program work.

Delaying until WI-4301 capstone is ready would bundle this refactor with substantial new work (wrap procedure + envelope durability schema + handoff service integration). Landing it now lets the open disclosure converge to its specified shape independently.

## Why Not (alternatives considered)

- **Bundle into WI-4301 capstone** (rejected): the open-disclosure changes are self-contained, testable today, and visible to every fresh session. Bundling defers operator-visible improvement for no compatibility benefit.
- **Refactor close disclosure too in this thread** (rejected): the close disclosure depends on a wrap-procedure Python entry point that doesn't exist (see § Scope Boundaries). Trying to land it here would either require implementing the missing wrap-procedure surface (out of scope) or stubbing it with non-functional code (defect-introducing).
- **Move the glossary section to a different existing section instead of removing inline** (rejected per SPEC): the SPEC body explicitly relocates glossary to AXIS 2 / `gt help`, not to a different inline slot.
- **Keep the inline glossary "for one more transition cycle"** (rejected): operating-model `placement` principle (`.claude/rules/canonical-terminology.md`) prefers clean placement to layered transitional surfaces. The AXIS 2 hook and `gt help` already exist as the canonical glossary access path; no transition is required.
- **Update the top-3 source filter via a config flag rather than code** (rejected): the SPEC mandates the filter; making it configurable would expose a behaviour that the SPEC explicitly forbids in the unconfigured form.

## Prior Deliberations

- `DELIB-20260872` (2026-06-04, owner_conversation/owner_decision) — PAUTH v2 mint authorizing source/test_addition for WI-4298/4299/4301.
- `DELIB-20260636` (2026-06-04, owner_conversation/owner_decision) — envelope-program grilling + UI specification authority.
- `DELIB-20260648` (2026-06-04, owner_conversation/owner_decision) — envelope-program PAUTH minting.
- `DELIB-2500` (2026-05-05, owner_conversation/owner_decision) — envelope-program foundation.
- `DELIB-2238` (2026-05-01, owner_conversation/owner_decision) — session envelope.
- Bridge `gtkb-envelope-disclosure-ui-redesign-001.md` + Codex GO at `-002.md` — design authority for the spec body inserted into MemBase as `SPEC-ENVELOPE-DISCLOSURE-UI-001`.

## Specification Links

**Primary spec being implemented (MemBase, status=`specified`):**

- `SPEC-ENVELOPE-DISCLOSURE-UI-001` — Envelope Open/Close Disclosure UI Contract. Inserted 2026-06-04T14:41:07Z by `gt-cli` per Codex GO at `bridge/gtkb-envelope-disclosure-ui-redesign-002.md`. This impl satisfies the spec's **open disclosure** section in full; the close disclosure section is deferred to WI-4301 capstone (see § Scope Boundaries).

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SESSION-SELF-INITIALIZATION-001` — the governance baseline this impl amends operationally.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

**Forward references (sibling WIs; informational only):**

- WI-4293 (session-envelope durability) — close-disclosure JSON writes into the per-harness archive directory this spec defines. Not exercised by this impl.
- WI-4294 (wrap procedure) — close-disclosure render handler is invoked by the wrap procedure. Not exercised by this impl.
- WI-4301 (impl umbrella) — the close-disclosure handler lands under the capstone.

## Owner Decisions / Input

This implementation proposal is fully authorized by existing owner-decision evidence captured via AskUserQuestion. No fresh AUQ is required:

1. **DELIB-20260872** (2026-06-04, owner AUQ) — owner approved PAUTH v2 mint adding `source`/`test_addition`/`hook_upgrade` mutation classes plus WI-4298/4299/4301 to the envelope-program PAUTH's `included_work_item_ids`. The two AUQs (PAUTH-mint approval + amendment-scope approval) authorize precisely this class of impl work.
2. **DELIB-20260648** (2026-06-04, owner AUQ) — envelope-program PAUTH v1 mint, authorizing the program as a whole.
3. **DELIB-20260636** (2026-06-04, owner AUQ) — envelope-program grilling captured the 5 design points for WI-4298 in WI status_detail, which became `SPEC-ENVELOPE-DISCLOSURE-UI-001` per the GO'd design.
4. **WI-4298 status_detail** — the 5 design points (open budget; keep/move/drop sections; top-3 source; close shape; producer) constitute the AUQ-recorded requirement set.

No new owner AUQ is required at this impl layer because PAUTH v2 covers the work and the spec defines what success looks like.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-ENVELOPE-DISCLOSURE-UI-001` (MemBase, status=`specified`) defines the canonical open-disclosure shape this impl realizes, including the 4 keep / 2 move / 2 drop / 1 source-filter requirements, with a determinism contract. No new spec is required. The close-disclosure portion of the spec is deferred to WI-4301 per § Scope Boundaries; this is a scope split, not a requirement gap.

## Scope Boundaries (explicit)

**In scope (this impl):**

- Modify `scripts/session_self_initialization.py` open-disclosure section emission (lines roughly 4119 "Work State", 4767 "Recommended Session Focus", 4799 glossary call, 1243 top-3 eligibility).
- Add `approval_state` filter to top-3 priority selection.
- Add tests under `platform_tests/scripts/` asserting the new disclosure shape (sections removed, top-3 filter applied).

**Out of scope (deferred to WI-4301 capstone):**

- Close-disclosure structured-JSON-plus-terminal-summary render handler. This depends on a wrap-procedure Python entry point (`SPEC-WRAP-PROCEDURE-001` design GO'd at `bridge/gtkb-session-wrap-procedure-001-004.md` but not yet in MemBase; no `scripts/wrap_procedure.py` exists). The close-disclosure handler lives at the wrap procedure's terminal-close-summary call-site, which doesn't exist yet.
- Per-harness session-envelope archive file format integration. This depends on `SPEC-SESSION-ENVELOPE-DURABILITY-001` (design GO'd at `bridge/gtkb-session-envelope-durability-001-006.md`, not in MemBase; the per-harness archive directory doesn't exist yet).
- AXIS 2 surface change to expose glossary on-demand. The existing AXIS 2 hook already delivers glossary entries; no change is required at this layer to enable glossary access after inline removal. If AXIS 2 needs explicit `gt help wrap`-style command surfacing, that is a separate WI under the capstone.
- `gt help wrap` or equivalent on-demand surface for the 17 NL wrap-trigger phrases. Currently the open disclosure includes a "Wrap-Up Trigger Commands" section listing them; the SPEC says move to `gt help wrap` — but this impl preserves the existing list inline because no `gt help wrap` surface exists yet to redirect to. Adding the command surface is a separate impl (likely WI-4296 dispatcher-rules-engine or WI-4301 capstone).

**Documentation discipline:** the impl proposal explicitly preserves the "Wrap-Up Trigger Commands" section (inline list of NL wrap triggers) because removing it before the `gt help wrap` surface exists would create a discoverability regression. This is a deliberate sequencing choice, not a partial implementation: the SPEC's "move to gt help wrap" requirement is satisfied later when both ends exist.

## Spec-Derived Verification Plan

Each spec requirement maps to a test in the new `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py` (or a clearly-named additional file):

| Spec requirement (SPEC-ENVELOPE-DISCLOSURE-UI-001) | Test |
|----|----|
| Open disclosure DROPS "Work State" section | `test_open_disclosure_omits_work_state_section` — generate disclosure, assert string `### Work State` is absent |
| Open disclosure DROPS "Recommended Session Focus" section | `test_open_disclosure_omits_recommended_session_focus_section` — generate disclosure, assert `### Recommended Session Focus` is absent |
| Open disclosure MOVES glossary inline (no inline glossary render) | `test_open_disclosure_omits_inline_glossary_section` — generate disclosure, assert glossary section header (e.g. `### Canonical Terminology Preview`) is absent |
| Open disclosure KEEPS role declaration | `test_open_disclosure_includes_role_declaration` — generate disclosure, assert `Role being assumed:` line present |
| Open disclosure KEEPS bridge-actionable surface summary | `test_open_disclosure_includes_bridge_actionable_summary` — generate disclosure, assert `File bridge: generated-time latest NEW/REVISED=` substring present |
| Open disclosure KEEPS top-3 priorities surface | `test_open_disclosure_includes_top_3_priorities_surface` — generate disclosure, assert top-3 surface element present |
| Open disclosure KEEPS dashboard link | `test_open_disclosure_includes_dashboard_link` — generate disclosure, assert `Dashboard: GroundTruth-KB Project Dashboard:` substring present |
| Top-3 source filters by `approval_state='implementation_authorized'` only | `test_top_3_filters_by_approval_state` — seed in-memory WI fixtures with mixed approval_states, assert only `implementation_authorized` survive into top-3 |
| Top-3 selection is deterministic for fixed inputs | `test_top_3_selection_is_deterministic` — invoke twice on same MemBase snapshot, assert byte-identical top-3 ordering |
| Top-3 selection algorithm preserves priority + WI-id ordering | `test_top_3_selection_priority_then_wi_id` — seed WIs with mixed priorities and IDs, assert highest-priority first; same-priority lowest WI-id first |

**Verification commands (Pre-File Code-Quality Gates per `.claude/rules/file-bridge-protocol.md`):**

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_canonical_consistency.py platform_tests/scripts/test_session_self_initialization_imports.py platform_tests/scripts/test_session_self_initialization_topology_derive.py -q --no-header -p no:cacheprovider
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
```

Existing tests in `platform_tests/scripts/test_session_self_initialization*.py` MUST continue to pass; any failures indicate either a regression OR an existing-test assertion against now-removed sections (which should be updated to match the new shape with explicit justification per `GOV-15 Test Fix Gate`).

## Risk / Rollback

**Risk:** the open disclosure is loaded by every fresh GroundTruth-KB session via the SessionStart hook chain (per `GOV-SESSION-SELF-INITIALIZATION-001`). A defect in the refactor could break startup for both Prime Builder and Loyal Opposition sessions until reverted.

**Mitigations:**

- Tests assert section presence/absence and top-3 filtering explicitly (see § Spec-Derived Verification Plan).
- Existing `test_session_self_initialization_canonical_consistency.py` validates structural invariants; any structural break surfaces immediately.
- The change is narrowly scoped to disclosure-section emission and one priority filter; the underlying data model is untouched.

**Rollback:** single-commit `git revert <impl-commit>` restores the prior disclosure shape. No MemBase mutation, no protected-narrative mutation, no schema change — rollback is mechanical.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of a fresh `gtkb-envelope-disclosure-ui-impl` document list in `bridge/INDEX.md`. The originating design thread `gtkb-envelope-disclosure-ui-redesign` is preserved as historical evidence and remains GO-terminal.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection: applicability and clause preflights will be run against this draft via `--content-file` before file write, and re-run against the indexed operative file after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking clause gaps.

## Recommended Commit Type

`feat` — this is a net-new capability surface (canonical envelope-program open disclosure shape) replacing legacy disclosure content. Not `refactor` because the user-visible disclosure shape changes meaningfully (4 sections dropped/moved + new top-3 filter); not `chore` because new test surface and behavior change land together.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
