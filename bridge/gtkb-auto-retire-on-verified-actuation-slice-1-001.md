NEW

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# Auto-Retire on VERIFIED - Slice 1 (Actuation Wiring)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-WI-4741-AUTO-RETIRE-ON-VERIFIED-AUTOMATION
Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4741
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", ".claude/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_auto_retire_on_verified.py"]

Document: gtkb-auto-retire-on-verified-actuation-slice-1

## Summary

Wire project-retirement actuation into the VERIFIED-finalization event so the last
VERIFIED verdict that completes a project's gating work items automatically retires
that project, fulfilling the intent of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
(which specifies retirement is automatic, no owner confirmation). Today actuation
exists only in the manual `gt projects complete-authorization` / `gt projects retire`
surfaces; `.claude/skills/verify/helpers/write_verdict.py` invokes no retirement, so
62 stale-active projects had to be retired by hand on 2026-06-22
(`gtkb-stale-active-project-retirement-batch`). This is Slice 1 of WI-4741.

## Slice Scope (Slice 1 of 2)

- **In scope (this slice):** actuation only. A new best-effort routine in
  `ProjectLifecycleService` that, given a just-VERIFIED bridge thread + its cited
  work items, retires any project whose gating member WIs are now all
  project-scoped-verified; called from `write_verdict.py` after a successful
  VERIFIED-finalization commit.
- **Out of scope (Slice 2, separate proposal):** the completion-detector
  archival-blindness fix (scanner + lifecycle reading VERIFIED coverage from the
  Deliberation Archive / archived threads, not only live `bridge/INDEX`).
- **Why actuation can land first / safely:** at VERIFIED-finalization time the
  thread is still live in `bridge/`, so its coverage is directly visible to the
  existing project-scoped reader. Archival-blindness can therefore only cause the
  completion check to *under-fire* for a project whose *other* gating threads have
  already archived (a conservative miss, never a wrong retirement). Slice 2 closes
  that retroactive gap.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v4) - the governing spec;
  retirement is automatic on VERIFIED completion. This slice implements its
  actuation.
- `GOV-STANDING-BACKLOG-001` - project authority must reflect real lifecycle state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites
  governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived tests below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are in-root GT-KB
  platform sources/tests under `E:\GT-KB` (in-root placement clause satisfied).
- `.claude/rules/bridge-essential.md` - VERIFIED finalization is bridge function.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
already requires automatic VERIFIED-driven retirement; this slice implements the
missing actuation. No new or revised requirement is needed.

## Prior Deliberations

- `DELIB-20265569` - owner AUQ build-now decision authorizing WI-4741 (2026-06-22).
- `DELIB-2275`/`DELIB-2276` (GO), `DELIB-2281`/`DELIB-20264756` (NO-GO) - "W1
  Retirement-Machinery Correction" history; this slice deliberately reuses the
  existing guards rather than re-inventing gating logic.
- `DELIB-20264096` (NO-GO) - gtkb-gov-project-retirement-spec-001.
- `WI-3481` (resolved) - premature auto-retire of incrementally-materialized
  multi-slice projects; its safeguard is reused, not bypassed.
- `WI-3316`/`WI-3443`/`WI-3462` (resolved) - prior completion-machinery work.

## Design

1. **New routine `ProjectLifecycleService.auto_retire_on_verified(verified_thread_slug,
   project_root, changed_by=...)`** (in
   `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`):
   - Find projects holding an active `implements` link to `verified_thread_slug`
     (`_implements_links_by_project`).
   - For each, reuse the EXISTING project-scoped gate verbatim:
     `_authorization_completion_ready(...)` over `_verified_work_items_by_project(project_root)`,
     with the active `plan_incomplete` completion-guard check
     (`_completion_guards_by_project`) and the non-VERIFIED-implements-thread check
     (`_non_verified_implements_threads_by_project`).
   - For each completion-ready project's active authorization(s), call the existing
     `complete_project_authorization(...)` (which auto-retires the project when it is
     the sole remaining active authorization), passing a clear `change_reason` citing
     this slice + the VERIFIED thread.
   - Return the list of retired project ids. NEVER raise: each project is wrapped in
     try/except `ProjectLifecycleError`; failures are logged and skipped.
2. **Wire into `write_verdict.py::finalize_verified_commit()`** after the VERIFIED
   verdict file is written and the commit SHA is obtained (the post-commit seam):
   lazily import `ProjectLifecycleService` (inside the call, wrapped in
   try/except `ImportError` so a missing package degrades gracefully), open
   `KnowledgeDB(project_root / "groundtruth.db")`, and call
   `auto_retire_on_verified(slug, project_root, changed_by="auto-verify-finalization")`.
   The whole actuation block is wrapped in a broad try/except that logs and swallows
   any error: **the VERIFIED verdict + commit must never be rolled back by an
   actuation failure** (retirement is a best-effort side effect, not part of the
   verdict transaction).

## Premature-Retirement Guards (reused verbatim, not re-invented)

Per the W1 / v3->v4 NO-GO history, this slice does NOT introduce new gating logic:
- **Project-scoped coverage only** - uses `_verified_work_items_by_project` (the v4
  F1 fix); never the diagnostics-only global `_all_verified_work_items`. A thread
  implementing project A cannot complete project B.
- **Active `plan_incomplete` completion guard** blocks retirement.
- **Non-VERIFIED implements-thread** on the project blocks retirement.
- **WI-3481 multi-slice safeguard** - coverage is read across all versions of each
  VERIFIED thread, so a project with anticipated-but-unfiled future gating WIs is
  not prematurely retired (its gating set is the active membership links).

## Spec-Derived Verification

New `platform_tests/scripts/test_auto_retire_on_verified.py`, mapped to WI-4741
acceptance + `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Behavior | Test |
|---|---|
| Auto-retire fires | project with gating WIs + active `implements` link to a thread; finalize that thread VERIFIED with all gating WIs covered -> project `status='retired'`, authorization completed |
| Guard blocks | same, but with an active `plan_incomplete` guard -> NOT retired |
| Unverified blocks | a gating WI not covered by the VERIFIED set -> NOT retired |
| Non-VERIFIED implements blocks | project also implements a non-VERIFIED thread -> NOT retired |
| NO-GO -012 F1 (cross-project) | two projects share a VERIFIED thread; only the one holding the `implements` link retires |
| Best-effort safety | actuation raising does NOT roll back the VERIFIED verdict/commit (finalize still succeeds) |

Commands: `python -m pytest platform_tests/scripts/test_auto_retire_on_verified.py -q`;
plus `python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q` (regression
of existing completion/retirement behavior); `ruff check` + `ruff format --check` on
the changed files.

## Risk / Rollback

- Risk: a missed guard could over-retire. Mitigated by reusing the existing,
  already-verified guard methods verbatim and by the comprehensive test matrix above.
- Risk: actuation error corrupts the verdict transaction. Mitigated by the broad
  best-effort wrapper (logs + swallows; never rolls back the verdict).
- Risk: import coupling (write_verdict.py -> groundtruth_kb). Mitigated by lazy
  import + `ImportError` degradation.
- Rollback: revert the two source edits + remove the test; retirement reverts to
  manual-only. Append-only project history means any auto-retired project is
  restorable via `gt projects update <ID> --status active`.

## Owner Decisions / Input

- AUQ 2026-06-22 "What should I do next?" -> **Build the auto-retire automation now**
  (recorded as `DELIB-20265569`), authorizing WI-4741 implementation via the standard
  propose -> GO -> implement -> VERIFIED path.

## Recommended Commit Type

`feat:` - adds a new automation capability (event-driven auto-retirement) by
implementing the actuation that `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
specifies.
