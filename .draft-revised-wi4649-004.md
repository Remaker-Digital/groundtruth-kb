REVISED

# Stale Git Worktree Metadata Auto-GC Diagnostic Slice — REVISED (resume from owner-directed DEFERRED park)

bridge_kind: prime_proposal
Document: gtkb-stale-git-worktree-autogc-diagnosis
Version: 004
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-stale-git-worktree-autogc-diagnosis-003.md (owner-directed DEFERRED park)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: claude-prime-interactive-may29-hygiene-drive-20260625
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style; may29-hygiene retirement drive

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4649

target_paths: ["independent-progress-assessments/repo-integrity/worktree-autogc-diagnosis/**"]

implementation_scope: repository_state_diagnostic_report
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Note — why this is REVISED, not a fresh proposal

This thread reached `GO` at `-002` (OpenRouter Loyal Opposition harness F) for a
narrow, read-only diagnostic slice. It was then parked `DEFERRED` at `-003`
(owner-directed) because the headless implementation-start authorization gate
(`scripts/implementation_authorization.py`) mis-classified the `-001`
`## Requirement Sufficiency` section as a requirement *gap* (a
forward-looking "needed only for a later destructive cleanup" sentence matched
the gap regex), producing an unbounded headless dispatch retry loop.

The `-003` recorded resume condition was: "this thread becomes actionable again
once the `scripts/implementation_authorization.py` Requirement-Sufficiency
false-positive is corrected." That fix has **landed** (HYG-046 / FAB-14): the
gap matcher now skips a future-scoped gap sentence via
`_FUTURE_SCOPED_GAP_CONTEXT_RE` (`scripts/implementation_authorization.py:925`).
Confirmed empirically this session: `requirement_sufficiency_state()` against
the `-001` body now returns `"sufficient"` (previously `"gap"`).

The diagnostic proposal content is unchanged from `-001`; only the external
impl-start blocker cleared. Because the `-003` DEFERRED park is the latest
status (not a `NO-GO`), the governed `revise_bridge` helper does not apply, and
Prime Builder cannot author an LO `GO` verdict. Per the owner's 2026-06-25
AskUserQuestion decision (below), this thread is re-entered as a Prime `REVISED`
proposal so Loyal Opposition issues a fresh `GO` on the now-implementable
read-only diagnostic. This clears the owner-directed DEFERRED park.

## Summary

This proposal requests a narrow, read-only diagnostic slice for `WI-4649`.
The work item records repeated Git auto-gc warnings that stale
`.git/worktrees/*` registrations could not be pruned and that unreachable loose
objects were accumulating. The PB task is evidence collection and follow-on
recommendation rather than cleanup.

The implementation will write a durable diagnostic report under
`independent-progress-assessments/repo-integrity/worktree-autogc-diagnosis/`.
It will record current `git worktree list --porcelain`,
`git count-objects -v`, and non-mutating metadata observations, then recommend
whether a later destructive cleanup proposal is warranted. This proposal
explicitly excludes `git worktree prune`, `git prune`, `git gc`, object
deletion, branch/ref movement, remote operations, and direct `.git` mutation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Requires PB work on protected project
  state to move through the governed file bridge; this document is the
  append-only implementation proposal for the diagnostic slice.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Requires this
  proposal to cite governing requirements rather than relying on implied
  process memory.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires explicit
  linkage to the active project, work item, and project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Requires the eventual
  implementation report to include verification derived from the cited
  requirements.
- `GOV-STANDING-BACKLOG-001` — WI-4649 is a hygiene backlog item captured under
  the standing directive to preserve fix-worthy defects for governed follow-up.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — The active project
  authorization allows proposing implementation for unimplemented May29
  Hygiene work items, including WI-4649.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Keeps the diagnostic target
  bounded to the GT-KB repository root and does not treat external worktree
  paths as live GT-KB artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Converts the observed repository
  hygiene issue into a durable report and follow-on decision surface.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Favors preserving the diagnostic as
  a reviewable artifact before any cleanup action.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — The observed recurring auto-gc
  warnings cross the threshold from chat observation into a tracked artifact.
- `.claude/rules/project-root-boundary.md` — The report path is inside
  `E:\GT-KB`; external paths are evidence only, not mutation targets.

## Prior Deliberations

- `DELIB-20263373` / `bridge/gtkb-fab-04-storage-reclamation-015.md` —
  Prior VERIFIED storage-reclamation work covered large generated artifacts and
  `.claude/worktrees` cleanup. WI-4649 is narrower: registered Git worktree
  metadata and auto-gc warnings in the current repository.
- `DELIB-FAB04-REMEDIATION-20260610` — Prior remediation deliberation for
  storage pressure supports the same artifact-first approach, but does not
  authorize destructive Git metadata cleanup here.
- `bridge/gtkb-git-repo-broken-blob-investigation-012.md` — Prior VERIFIED Git
  integrity investigation focused on a missing-blob/stash problem. WI-4649
  differs because the live symptom is stale worktree registration and loose
  object/gc warning behavior.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Supports turning repeated
  manual repository-state inspection into deterministic evidence and a
  potential future cleanup/check command rather than ad hoc session memory.
- `bridge/gtkb-stale-git-worktree-autogc-diagnosis-002.md` (GO) and `-003`
  (owner-directed DEFERRED park) — the prior actionable verdict and the park
  this REVISED resumes; the `-002` GO conditions (strictly read-only commands;
  follow-on recommendation section; no credential material; new discoveries are
  reported, not acted on) carry forward into implementation.

## Owner Decisions / Input

The owner authorized re-entering this owner-parked DEFERRED thread as a Prime
`REVISED` proposal via AskUserQuestion on 2026-06-25:

- Question: how to re-activate WI-4649 (DEFERRED@-003 with a still-valid LO
  GO@-002, resume precondition met) given that Prime Builder cannot author a GO
  and there is no governed `undefer` command.
- Owner answer: **"Re-file as REVISED for fresh LO GO"** — clean role boundary;
  Prime files REVISED, Loyal Opposition issues a fresh GO.

No further owner decision is required for the diagnostic-only implementation. The
active project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23`
includes WI-4649 and allows PB to propose implementation for May29 Hygiene work
items. Any later cleanup action that deletes Git metadata, prunes objects,
removes worktree registrations, or changes repository refs must be proposed
separately and must receive its own bridge GO plus any required owner approval.

## Requirement Sufficiency

Existing requirements are sufficient for the diagnostic slice. WI-4649, the
active May29 Hygiene project authorization, the file-bridge authority
requirements, and the project-root boundary rule provide enough direction for a
read-only report. A later destructive cleanup implementation is out of scope for
this diagnostic slice and would be proposed separately.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not record credential material; Git metadata and paths only. | Manual report review and bridge credential scan. |  |
| CQ-PATHS-001 | Yes | Write evidence only under the declared in-root report path. | `git diff --name-only -- independent-progress-assessments/repo-integrity/worktree-autogc-diagnosis` and bridge preflights. |  |
| CQ-COMPLEXITY-001 | N/A | No source code is changed. | Diff review. | Diagnostic report only. |
| CQ-CONSTANTS-001 | N/A | No runtime constants are changed. | Diff review. | Diagnostic report only. |
| CQ-SECURITY-001 | Yes | Do not execute destructive or remote Git operations. | Command log in the report must show only read-only commands. |  |
| CQ-DOCS-001 | Yes | Diagnostic findings and recommendations are written as a durable report. | Report existence/content checks. |  |
| CQ-TESTS-001 | Yes | Use read-only Git verification commands rather than pytest. | `git worktree list --porcelain`, `git count-objects -v`, and non-mutating metadata inspection. | No source behavior changes. |
| CQ-LOGGING-001 | N/A | No logging behavior changes. | Diff review. | Diagnostic report only. |
| CQ-VERIFICATION-001 | Yes | Exact commands and observed results are captured in the post-implementation report. | Loyal Opposition can reproduce the read-only commands. |  |

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: File this REVISED through the governed bridge
  path and inspect it with `gt bridge show gtkb-stale-git-worktree-autogc-diagnosis`.
  Expected result: latest status is `REVISED`, the version chain is intact, and
  no existing version is rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: Run
  `python scripts/bridge_applicability_preflight.py --bridge-id
  gtkb-stale-git-worktree-autogc-diagnosis --content-file <proposal> --json`.
  Expected result: required spec linkage has no missing required specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: Inspect proposal
  metadata and `gt projects show PROJECT-GTKB-MAY29-HYGIENE`. Expected result:
  the proposal cites the project, WI-4649, and the active project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: The eventual implementation
  report must include the read-only commands and observed outputs. Expected
  result: LO can reproduce or review the captured repository-state evidence.
- `GOV-STANDING-BACKLOG-001`: Run `gt backlog list` filtered to
  PROJECT-GTKB-MAY29-HYGIENE. Expected result: WI-4649 is present and open.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: Inspect the May29 Hygiene
  project authorizations. Expected result: the bounded-implementation
  authorization remains active and includes WI-4649.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and project-root boundary: Run
  `git diff --name-only --
  independent-progress-assessments/repo-integrity/worktree-autogc-diagnosis`.
  Expected result: the implementation diff is limited to the declared in-root
  report path.
- Diagnostic evidence: Run `git worktree list --porcelain`,
  `git count-objects -v`, and read-only inspection of `.git/worktrees/*/gitdir`
  files. Expected result: the report records stale/prunable worktree metadata
  and object-count state without deleting or mutating anything.

Allowed implementation commands are read-only:

```text
git status --short --branch
git worktree list --porcelain
git count-objects -v
Get-ChildItem .git\worktrees -Force
Get-Content .git\worktrees\<name>\gitdir
```

Explicitly out of scope for this proposal:

```text
git worktree prune
git prune
git gc
git fetch
git stash drop
Remove-Item / del / rmdir against .git or any worktree path
```

## Risk / Rollback

Risk is low because the proposed implementation writes only diagnostic report
files and runs only read-only Git inspection commands. The main risk is
mischaracterizing external temporary worktree paths as GT-KB-managed artifacts;
the report must keep those paths as evidence only.

Rollback is a normal single-commit revert of the diagnostic report. No
repository metadata cleanup is performed in this slice, so rollback does not
need to reconstruct deleted Git state.

## Recommended Commit Type

`chore:` — the eventual implementation is repository hygiene diagnosis and
durable reporting, not product behavior or test logic.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
