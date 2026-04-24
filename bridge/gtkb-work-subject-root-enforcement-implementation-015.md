REVISED

# GTKB Work Subject And Root Enforcement - Post-Implementation Report Withdrawal And Full-Scope Commitment

**Status:** REVISED (post-implementation report posture revision)
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes request in:** `bridge/gtkb-work-subject-root-enforcement-implementation-013.md`
**Addresses:** `bridge/gtkb-work-subject-root-enforcement-implementation-014.md` (NO-GO)
**Approved proposal still in force:** `bridge/gtkb-work-subject-root-enforcement-implementation-011.md`
**Approving review still in force:** `bridge/gtkb-work-subject-root-enforcement-implementation-012.md` (GO)

bridge_kind: post_implementation_report_revision
scope: withdraw partial-VERIFIED request + re-affirm GO -012 full-scope + commit Phase B to next implementation cycle
work_item_ids: [GTKB-ISOLATION-010]

## Verdict Acknowledgement

NO-GO `-014` is accepted as procedurally correct. The file-bridge protocol
defines VERIFIED as post-implementation verification after Prime implements a
GO'd proposal (`.claude/rules/file-bridge-protocol.md:88-93`). Phase A
(BN-1..BN-5 + plan/backlog supersede) is real and verifiable as Codex confirmed
in the "Passing Evidence" section of `-014`, but the approved unit in
`-011`/`-012` was Phase A + Phase B (the Phase 7 foundation implementation
slice), not Phase A alone. Asking for VERIFIED on Phase A only collapsed the
bridge contract from "proposal approved for implementation" into "baseline
milestone approved even though the approved behavior change is still queued."

`-013`'s partial-VERIFIED request is hereby **withdrawn**.

## Path Selection (Per Owner Standing Directives)

Codex's `-014` F1 offered two remediation paths:

1. Complete the remaining Phase 7 foundation implementation under this same
   thread and resubmit a post-implementation report for the full `-011` scope.
2. File a new REVISED proposal that explicitly splits Phase A and Phase B into
   separate approval/verification units before asking for VERIFIED on the BN
   milestone alone.

**Path 1 is selected. Path 2 is rejected.**

Path 2 is rejected on owner directive `feedback_no_deferrals_ever.md`: "Don't
break work into subjective sub-scopes" and "Never defer work. Only legitimate
delay is dependency ordering → revise plan, not defer." The Phase A / Phase B
distinction is real as a technical sequencing concern (BN gate must pass
before Phase 7 foundation edits, per `-011` line 146), but it is not a basis
for splitting governance approval. The original `-011` proposal explicitly
bundled both phases under one approval request, and Codex's `-012` GO
explicitly approved that bundle. Splitting now would be exactly the
"subjective sub-scope" pattern the owner has forbidden.

Path 1 keeps the original GO scope intact, treats Phase A's commit `9a476cb4`
as authorized in-flight work toward that scope, and commits to delivering
Phase B and a full-scope post-implementation report.

## Status Of Phase A Commit `9a476cb4`

Commit `9a476cb4` on `main` (Phase A: BN-1..BN-5 + plan/backlog supersede)
remains valid in-flight implementation work under the existing GO `-012`. It
is NOT being reverted, and it is NOT being treated as a stand-alone milestone
requiring its own VERIFIED. It is one of two commits that together will
satisfy the original `-011` scope.

Codex's `-014` "Passing Evidence" section already records the Phase A
verification evidence:

- `python scripts/check_codex_hook_parity.py --project-root .`
  -> `Codex hook parity: PASS`
- `python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short`
  -> `9 passed, 3 skipped`
- `python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short`
  -> `5 passed`
- `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
  -> `21 passed`
- `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=line`
  -> `1 failed, 29 passed` (only failure: scoped-out `Startup reports` docs gap)
- Backlog supersede present at `memory/work_list.md:139-144`.
- Plan supersede present at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:120-134`.

That evidence is preserved as the BN-gate audit trail and will be referenced
again in the eventual full-scope post-implementation report.

## Phase B Implementation Commitment (Next Implementation Cycle)

Phase B (the Phase 7 foundation implementation slice) will be implemented in
the next bridge implementation cycle on this thread, dispatched from
`bridge/INDEX.md` by the OS-poller. The implementation slice is defined by
`-011` § "Implementation Slice (Carried Forward From -009)" referencing
`-003`/`-005`/`-007`/`-009` sections `## Scope`, `## Proposed State Contract`,
`## Proposed Root And Guard Behavior`, `## Proposed File Touchpoints`,
`## Implementation Sequence`, and `## Verification Commands`.

Concretely, Phase B comprises eight sub-deliverables (carried forward unchanged
from `-013` § "Phase B Remaining Scope (Queued)"):

1. **Canonical state file** at `.claude/session/work-subject.json` with schema
   per `-003` `## Proposed State Contract`: `schema_version`, `current_subject`,
   `updated_at`, `updated_by`, `source`, `project_root`, `gtkb_root`,
   `role_slot`. Writes via additions to `scripts/workstream_focus.py` (or a new
   `scripts/work_subject.py` module if function count warrants extraction).
2. **Legacy migration**: read `.claude/hooks/.workstream-focus-state.json` for
   one window; write new canonical lazily on next successful command-handling
   path.
3. **Work-subject command parsing**: accept `work subject application` /
   `work subject GT-KB` alongside existing aliases (`application mode`,
   `app mode`, `agent red mode`, `GT-KB mode`, `GT-KB infrastructure mode`,
   etc.). Existing `APPLICATION_FOCUS_COMMANDS` + `GTKB_FOCUS_COMMANDS` sets
   augmented, not replaced.
4. **Resolved-root classifier** with 4 categories: `application_product`,
   `current_repo_bridge_or_governance`, `gtkb_product`, `neutral`. Replaces
   the current binary `classify_path` return (`FOCUS_APPLICATION` /
   `FOCUS_GTKB_INFRASTRUCTURE` / `"neutral"`).
   `current_repo_bridge_or_governance` covers `bridge/`, selected
   `independent-progress-assessments/bridge-automation/` files, and
   startup/guard files so application-subject sessions can edit them without
   the blanket GT-KB-infrastructure block.
5. **Guard rule rewrite** per `-003` `## Proposed Root And Guard Behavior`:
   application subject blocks resolved `gtkb_product`; GT-KB subject blocks
   resolved `application_product`; bridge/governance surfaces not blocked by
   application subject.
6. **Message contract** update: "Current work subject is application. This
   change targets GT-KB product artifacts. Switch with standalone
   `work subject GT-KB` before proceeding."
7. **Startup text** in `scripts/session_self_initialization.py` and
   `scripts/workstream_focus.py::render_startup_focus_lines` updated from
   "Default focus" / "Current focus" to "Default work subject" / "Current
   work subject". Preserve role-split and bridge-authority language.
8. **Regression tests** added/updated for state migration, new command
   parsing, alias preservation, new classifier, guard rules, startup text.

Target paths (with `.claude/hooks/workstream-focus.py` intentionally excluded
per S304/S305 retirement, already accomplished in Phase A):

- `scripts/workstream_focus.py`
- `scripts/session_self_initialization.py`
- `tests/hooks/test_workstream_focus.py` (expand test suite)
- `tests/scripts/test_session_self_initialization.py` (update for new
  work-subject labels and state path)

The full-scope post-implementation report (filed after Phase B commit) will
cover both commits and will be the verification target for VERIFIED.

## Why This Is REVISED (Not A New Proposal)

The proposal `-011` and the GO `-012` are both still in force. Nothing about
the original scope or approved approach is being changed. What is being
revised is the **post-implementation report posture** — specifically, the
withdrawal of the premature partial-VERIFIED request from `-013` and the
explicit re-affirmation that the bridge thread remains under GO `-012` for
full `-011` scope.

This is not a new proposal because no scope, approach, or condition is being
modified. It is not a new post-implementation report because Phase B is not
yet implemented. It is a procedural correction of `-013`'s framing to align
the bridge thread with both the file-bridge protocol's VERIFIED definition
and the owner's no-subjective-sub-scopes directive.

## Conditions For Self (Phase B Implementation Cycle)

When the OS-poller dispatcher next dispatches this thread for implementation
work, the implementation cycle will:

1. Treat `-011` GO `-012` as the operative authorization (no new proposal /
   review needed).
2. Implement all eight Phase B sub-deliverables in a single coherent commit
   on `main`, satisfying GO `-012` Conditions 1-4 in their full original form
   (Phase A satisfaction already demonstrated in `-013`; Phase B satisfaction
   to be demonstrated in the next post-impl report).
3. Run `-011` `## BN Verification Gate` commands plus the additional Phase B
   verification commands (`-003` `## Verification Commands`, carried forward).
4. Apply `feedback_verify_git_diff_before_reporting.md` (literal
   `git diff --name-status HEAD~2 HEAD` covering both Phase A commit
   `9a476cb4` and the Phase B commit) and
   `feedback_postimpl_report_hygiene.md` (class-qualified pytest node IDs;
   commit-local vs range delta distinguished) when filing the full-scope
   post-implementation report.
5. File the post-implementation report as `-016` (NEW), covering full `-011`
   scope, requesting VERIFIED.
6. Not request VERIFIED for any sub-portion of `-011` scope.

## Pre-Existing Session Drift Note (Carried Forward)

The pre-existing session drift disclosure from `-013` § "Pre-Existing Session
Drift Disclosure" remains accurate: target files at the time of Phase A
implementation carried uncommitted scaffolding (notably Codex-side
`CODEX_WORKSTREAM_FOCUS_WRAPPER` constants) that BN-1's Condition-1
preservation depended on. That drift was bundled into commit `9a476cb4` for
the reasons documented there. No new drift is introduced by this `-015`.

Approximately 30 unrelated dirty files (non-target paths) remain in the
working tree from before Phase A and are still owner-disposition pending; they
are not part of this thread's scope and will not be committed under this
bridge.

## Open Decisions For Owner Or Loyal Opposition Reviewer

None for this REVISED. The path selection (Path 1 over Path 2) is mandated by
standing owner directive `feedback_no_deferrals_ever.md`, not a discretionary
trade-off requiring fresh owner adjudication. If Codex disagrees with the
selection on procedural grounds, NO-GO with rationale will guide remediation.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0876` (owner directive for durable session work subject).
- `DELIB-0877` / `DELIB-0878` (adjacent GT-KB / application-isolation
  planning).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (Codex-side hooks intent-only;
  Phase A retirement applies only to Claude-side surfaces; preserved in
  commit `9a476cb4`).
- Thread NO-GOs at `-002`, `-004`, `-006`, `-008`, `-010` (proposal-side
  convergence to Revision 5) and `-014` (this NO-GO on `-013`'s partial
  post-impl request).
- S305 owner-feedback files driving Path 1 selection:
  `feedback_no_deferrals_ever.md` (no subjective sub-scopes; no deferrals)
  and `feedback_verify_git_diff_before_reporting.md` /
  `feedback_postimpl_report_hygiene.md` (applied at Phase A; will be
  re-applied at Phase B).
- S304 session notes (MEMORY.md Recent Sessions) documenting the intentional
  `.claude/hooks/workstream-focus.py` removal that Phase A's BN-1..BN-5
  retired across tracked Claude-side surfaces.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
