REVISED

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# Auto-Retire on VERIFIED - WI-4741 (REVISED: reconciled member-WI completion criterion)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-WI-4741-AUTO-RETIRE-ON-VERIFIED-AUTOMATION
Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4741
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", ".claude/skills/verify/helpers/write_verdict.py", "scripts/project_verified_completion_scanner.py", "platform_tests/scripts/test_auto_retire_on_verified.py"]

Document: gtkb-auto-retire-on-verified-actuation-slice-1

## Why REVISED (supersedes the -002 GO)

The `-001` proposal (GO at `-002`) scoped the actuation to the existing
**implements-link-to-VERIFIED-thread** completion criterion. Owner investigation
this session corrected two premises:

1. The WI-4741 "detector archival-blindness" gap is **not real**: the scanner reads
   562 VERIFIED threads from live `bridge/` (all with Work Item ids); the DA has no
   `verified` outcome to query. The real detector gaps are (a) it only evaluates
   projects with an active authorization (33 of 64 active projects have none), and
   (b) its completion criterion (implements-link-to-VERIFIED coverage; only 32
   projects have it) diverges from the owner's retirement criterion.
2. Owner decision (AUQ, 2026-06-22): **reconcile to the member-WI criterion** - a
   project is complete when all its active member work items are in a terminal
   resolution state, evaluated by membership (not authorization-scoping).

This revision therefore changes the completion criterion used by the new
auto-retirement actuation AND the detector to match how the owner actually judges
retirement (and how the 62-project manual cleanup was judged). It supersedes the
separately-planned "Slice 2"; the criterion reconciliation is the detector fix.

## Reconciled Completion Criterion

New additive predicate in `ProjectLifecycleService`, e.g.
`member_completion_ready(project_id) -> bool`:

- the project has >= 1 **active member work item** (active `project_work_item_memberships`); AND
- every active member work item is in a terminal resolution status
  `{verified, resolved, retired, wont_fix, not_a_defect}`; AND
- the project has no active `plan_incomplete` completion guard.

This is project-scoped by construction (member WIs belong to the project), so it does
NOT reintroduce the v3->v4 cross-project false-positive class (that was about shared
*threads*; member WIs are project-specific). It is **additive**: the existing
authorization-completion machinery (`complete_project_authorization`,
`auto_complete_ready_authorizations`, the implements-link `_authorization_completion_ready`)
is left intact for its own purpose; this predicate is the retirement trigger that
matches the owner criterion.

## Design

1. **Predicate + retire routine** (`lifecycle.py`):
   `auto_retire_completed_projects(project_root, changed_by=...) -> list[str]` -
   iterate active projects; for each, if `member_completion_ready(project_id)`,
   retire via `retire_project(...)` (and retire the project's own membership links
   per existing `_retire_project_work_items` semantics where applicable) with a
   clear `change_reason`. Best-effort: per-project try/except `ProjectLifecycleError`,
   log + skip; NEVER raise.
2. **Actuation seam** (`write_verdict.py::finalize_verified_commit`, post-commit):
   on a successful VERIFIED finalization, lazily import `ProjectLifecycleService`
   (try/except `ImportError`) and call `auto_retire_completed_projects(...)`. The
   call **re-evaluates active projects' current member-WI state** rather than the
   just-VERIFIED thread's WIs - so it is correct regardless of whether/when the
   VERIFIED event has resolved the cited WIs' `resolution_status`. Wrapped in a broad
   try/except that logs and swallows: **the VERIFIED verdict/commit is never rolled
   back by an actuation failure**.
3. **Detector reconciliation** (`scripts/project_verified_completion_scanner.py`):
   add a membership-based completion view using the same `member_completion_ready`
   predicate over ALL active projects (not only those with active authorizations), so
   `gt backlog status` / batch detection report the projects the owner would retire.
   The existing authorization/implements-link readiness view is retained for its
   current consumers; the new view is additive.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governing spec (automatic
  VERIFIED-driven retirement); this implements its actuation on the owner-reconciled
  criterion.
- `GOV-STANDING-BACKLOG-001` - project authority reflects real lifecycle state.
- `GOV-08` - KB single source of truth.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are in-root under
  `E:\GT-KB` (in-root placement satisfied).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `.claude/rules/bridge-essential.md`

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
already requires automatic VERIFIED-driven retirement; the owner AUQ
(`DELIB-20265569` build-now; 2026-06-22 reconcile-criterion AUQ) clarifies the
operative completion criterion as member-WI-terminal. No new requirement.

## Prior Deliberations

- `DELIB-20265569` - owner AUQ build-now decision (WI-4741).
- 2026-06-22 AUQ "Re-scope Slice 2" -> **Reconcile to member-WI criterion** (this
  revision's central change; recorded via the owner-decision tracker).
- `DELIB-2275`/`2276` (GO), `DELIB-2281`/`20264756` (NO-GO) - W1 Retirement-Machinery
  Correction history; guards reused, not re-invented.
- `WI-3481` - premature multi-slice retirement risk (the member-WI predicate uses the
  active membership set, so anticipated-but-unfiled future members are not present and
  cannot trigger premature retirement).
- `DELIB-20264096` (NO-GO) - gtkb-gov-project-retirement-spec-001.

## Spec-Derived Verification

New `platform_tests/scripts/test_auto_retire_on_verified.py`:

| Behavior | Test |
|---|---|
| Auto-retire fires (member-WI) | project with all active member WIs terminal -> VERIFIED finalization -> project `status='retired'` |
| Open WI blocks | a member WI non-terminal -> NOT retired |
| Guard blocks | active `plan_incomplete` guard -> NOT retired |
| No-members blocks | project with 0 active member WIs -> NOT retired |
| Membership-scoped (no auth needed) | project with NO active authorization but all member WIs terminal -> detected/retired |
| Best-effort safety | actuation raising does NOT roll back the VERIFIED verdict/commit |
| Detector parity | scanner's new membership view lists the same projects the predicate retires |

Commands: `python -m pytest platform_tests/scripts/test_auto_retire_on_verified.py -q`;
`python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q` (regression of
existing authorization-completion machinery, which must be unchanged); `ruff check` +
`ruff format --check` on changed files.

## Risk / Rollback

- Risk: looser criterion (WI terminal-state vs bridge-VERIFIED coverage) retires more
  projects. Accepted per owner reconciliation; mitigated by the no-members / guard /
  open-WI guards and append-only reversibility (`gt projects update <ID> --status active`).
- Risk: changing existing machinery. Mitigated by making the predicate + actuation +
  detector view ADDITIVE; the existing authorization-completion path is untouched
  (regression test asserts it).
- Risk: actuation error corrupts the verdict transaction. Mitigated by best-effort
  swallow (never rolls back the verdict) + lazy import degradation.

## Owner Decisions / Input

- AUQ 2026-06-22 "What should I do next?" -> **Build the auto-retire automation now**
  (`DELIB-20265569`).
- AUQ 2026-06-22 "Re-scope Slice 2" -> **Reconcile to member-WI criterion** (this
  revision implements that decision; supersedes the implements-link criterion of `-001`).

## Recommended Commit Type

`feat:` - new event-driven auto-retirement capability on the owner-reconciled
member-WI completion criterion.
