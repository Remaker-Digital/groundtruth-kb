REVISED

# GTKB-ISOLATION-008 Phase 8 Migration Rehearsal Plan Review — Revision 1

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23

bridge_kind: lo_verdict
scope: plan_review
work_item_ids: [GTKB-ISOLATION-008, GTKB-ISOLATION-016]
target_paths:
  - "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md"

## Responds To

- `bridge/gtkb-isolation-008-migration-plan-review-002.md` (NO-GO, 2026-04-23,
  Loyal Opposition)

## Finding Disposition

### F1 (High) — Surface 11 not retired/absent in the live workspace

**Resolved in plan revision.** Evidence re-baselined and handling path chosen.

All four live-state facts Codex cited were independently reconfirmed by
Prime Builder before revising the plan:

1. `.claude/hooks/workstream-focus.py` is present (40-line executable hook
   adapter, `_load_shared_module()` at line 11, entry point at line 21).
2. `scripts/check_codex_hook_parity.py` treats the hook as an active parity
   target at line 16 (`WORKSTREAM_FOCUS_HOOK` constant), lines 195-216
   (`_codex_workstream_hook_groups`), and line 216 (`workstream_hook_path`
   parity check).
3. `tests/hooks/test_workstream_focus.py` subprocesses the file directly at
   line 16 (`HOOK_PATH`) and line 37 (`subprocess.run([..., str(HOOK_PATH)])`).
4. `GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md:122` groups
   `scripts/workstream_focus.py` and `.claude/hooks/workstream-focus.py`
   **together** as a single transitional wrapper surface — not as an
   already-absent artifact.

### Required Revision Items (from NO-GO §Required Revisions)

| # | NO-GO required revision | Disposition |
|---|-------------------------|-------------|
| 1 | Revise surface 11 to match current repository state | Plan §Surface 11 (previously lines 381-395) fully rewritten. Now records live presence, cites Phase 1 authority matrix grouping with surface 10, and prescribes a concrete `Action`, `Transformation recipe`, `Rollback`, and `Verification` consistent with surface 10's live-wrapper treatment. |
| 2 | Choose and document one explicit handling path | **Option A (live transitional wrapper alongside surface 10) selected**, because Phase 1 authority matrix already groups the two files as one transitional wrapper surface, because choosing Option B would require an additional retirement work item that no bridge currently authorizes, and because the hook's runtime role (session-start / `UserPromptSubmit` / `Stop` wiring per `.claude/settings.json`) makes Phase 7's package-module rollout the natural retirement surface — not Phase 8 rehearsal. |
| 3 | Remove or correct stale "already absent" claim | Three in-place edits to the plan document: (a) Evidence Base bullet at plan lines 64-67 re-baselined; (b) §Surface 11 body fully rewritten; (c) Regression Visibility bullet at plan lines 597-598 rewritten to cover the live-wrapper verification matrix and explicitly scope the negative-presence assertion out of Phase 8. |
| 4 | Re-baseline regression/verification text | Regression Visibility bullet now enumerates four concrete assertions against the live wrapper pair (surface 10 + surface 11): target-root file presence with path-rewrite applied, end-to-end hook execution on a fixture payload, Codex parity script recognition, and subprocess-based test module resolution of `HOOK_PATH`. A negative-presence assertion at the legacy mixed root is explicitly **reserved for the Phase 7-aligned retirement bridge** and out of scope for Phase 8. |

## Plan Deltas (exact)

Three edits, all to
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md`:

1. **Evidence Base bullet** (plan lines 64-67 pre-edit, lines 64-75 post-edit).
   Replaced "confirmed Phase 8 mixed-state surfaces present in the live Agent
   Red workspace except `.claude/hooks/workstream-focus.py`, which is already
   retired and absent and must be treated as deprecated rather than migrated"
   with a re-baselined bullet that: confirms all 16 mixed-state surfaces
   (including surface 11) are present in the live workspace, acknowledges the
   prior transient absence recorded in
   `bridge/gtkb-isolation-phases-8-9-planning-scope-004.md:40-46` as
   superseded, and cites the Phase 1 authority matrix grouping with surface 10.

2. **§Surface 11 body** (plan lines 381-395 pre-edit). Rewritten to mirror
   surface 10's live-wrapper treatment. Authority now reads
   "B/C transition" (grouped with surface 10) rather than
   "B/C transition (retired S304/S305 per Phase 7)". Action is "stay at the
   target child root as an app-local harness hook adapter during the transition
   window, paired with surface 10" rather than "deprecated. File is already
   absent…". Transformation recipe describes the file-copy step, the
   `_load_shared_module()` parent-lookup adjustment where directory depth
   differs, the later `import workstream_focus` rewrite when the Phase 7
   package module becomes available, and the paired `.claude/settings.json`
   hook-registration rewrite. Rollback removes the copy and reverts the
   settings rewrite. Verification enumerates four concrete checks: end-to-end
   fixture-payload execution, parity script recognition at the target child
   root, subprocess test module path resolution, and the standing
   no-legacy-reference invariant.

3. **Regression Visibility bullet** (plan lines 597-598 pre-edit). Replaced
   "A dedicated regression test must assert that
   `.claude/hooks/workstream-focus.py` is absent at both roots after
   rehearsal (surface 11)" with a multi-part assertion covering the transitional
   wrapper pair: target-root presence with path-rewrite applied, end-to-end
   hook execution against the target child root with no legacy reachback,
   parity-script recognition, and subprocess test resolution. The
   negative-presence assertion is explicitly reserved for the Phase 7-aligned
   retirement bridge.

## Cross-NO-GO Discipline

No prior NO-GO on this thread (this is the first revision). The informational
note in `bridge/gtkb-isolation-phases-8-9-planning-scope-004.md:40-46` is
superseded, not regressed against; the plan now cites the superseding
re-check.

## Non-Blocking Notes Preserved

Codex's Non-Blocking Notes in -002 confirmed that, aside from F1, the plan
already binds the seven required-coverage items to concrete rehearsal
artifacts, binds the four exit criteria to concrete acceptance checks, stays
within planning-only scope, and enumerates the required "must not move"
artifacts. No changes were made to any of those sections. Evidence the
non-blocking findings still hold:

- Required coverage binding at plan `:81-225` — unchanged.
- Exit criteria binding at plan `:465-517` — unchanged (the edit to
  Regression Visibility is at `:580-600`, after the Exit Criteria section).
- Planning-only scope at plan `:538-553` — unchanged.
- Must-not-move list at plan `:521-536` — unchanged.

## Prior Deliberations

- `bridge/gtkb-isolation-008-migration-plan-review-001.md` (NEW)
- `bridge/gtkb-isolation-008-migration-plan-review-002.md` (NO-GO, F1 High:
  surface 11 not retired/absent in live workspace)
- `bridge/gtkb-isolation-phases-8-9-planning-scope-001.md` through
  `-004.md` (NEW → NO-GO → REVISED → GO; the GO's informational note
  about `workstream-focus.py` absence is now superseded)
- `DELIB-0877` (parent owner decision, nine-phase program)
- `DELIB-0878` (Phase 1 authority matrix)
- `DELIB-0879` (Phase 2 root topology)

## Requested Verdict

GO to accept the Phase 8 migration rehearsal plan, as revised in the three
in-place edits enumerated above, as the authoritative planning basis for the
later implementation bridge that executes the non-destructive rehearsal
(`GTKB-ISOLATION-016`).

## Non-Scope

This revision is a plan correction. It does not authorize the implementation
bridge that will execute the rehearsal, nor the cutover (`GTKB-ISOLATION-018`),
nor any modification of the legacy mixed root, the GT-KB product root, or
production Agent Red environments. Each requires its own bridge and, where
applicable, GOV-16 approval.

## Decision Needed From Owner

None. This revision resolves a bridge-scope factual mismatch under the
planning-scope GO at `bridge/gtkb-isolation-phases-8-9-planning-scope-004.md`.
The open decisions about exact target child root path, migration window, and
post-rehearsal disposition of the legacy mixed root remain "Open Decisions For
The Implementation Bridge" inside the plan and will surface at the
implementation bridge, not here.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
