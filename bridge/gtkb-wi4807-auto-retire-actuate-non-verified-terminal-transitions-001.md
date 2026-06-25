NEW

# Defect-Fix Proposal — Actuate v6 project retirement on non-VERIFIED governed terminal transitions (WI-4807)

bridge_kind: prime_proposal
Document: gtkb-wi4807-auto-retire-actuate-non-verified-terminal-transitions
Version: 001
Date: 2026-06-25 UTC
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 001c9470-def0-4180-9ff4-98496473d790
author_model: claude-opus-4-8
author_model_version: opus-4.8
author_model_configuration: interactive-prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4807

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "platform_tests/scripts/test_auto_retire_on_resolve.py"]

## Claim

The `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6 automatic-retirement
actuator (`ProjectLifecycleService.auto_retire_completed_projects`) fires ONLY on
VERIFIED finalization. This proposal wires the existing v6 completion-check-and-retire
into the canonical NON-VERIFIED governed terminal-transition apply path
(`gt backlog resolve` / `gt backlog update --resolution-status <terminal>`), so a
project reaching all-active-members-terminal via ANY governed path retires
deterministically — honoring every existing v6 guard. A targeted per-project actuation
method avoids a full all-projects sweep on each resolve.

## Defect / Reproduction

`auto_retire_completed_projects` (`project/lifecycle.py:1268`) is reachable only from
`_auto_retire_completed_projects_after_verified` → `finalize_verified_commit` in the
three `write_verdict.py` copies (`.claude` / `.codex` / `.cursor`). The non-VERIFIED
governed apply path in `cli_backlog_update.py` (the shared implementation of both
`gt backlog resolve` and `gt backlog update`) calls `db.update_work_item(...)` and
never invokes the actuator. `project_verified_completion_scanner.py` only REPORTS
readiness; it does not actuate.

Live reproduction THIS session: PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS had all 13 of
its member work items reach terminal resolution via `gt backlog resolve` (non-VERIFIED
path), yet `project.status` remained `active` with `completed_at: None` until a manual
`gt projects retire` was issued. Per `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
v6 + `DELIB-20265881`, that retirement should have been automatic.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`,
`groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`,
`platform_tests/scripts/test_auto_retire_on_resolve.py`.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — the governing v6 spec; mandates automatic retirement on the all-active-members-terminal condition via ANY governed path. This fix closes the actuation gap for the non-VERIFIED paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority governing this proposal and its append-only numbered-file audit chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — project lifecycle is an artifact-state transition; automatic retirement keeps the project artifact state consistent with member-WI state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: this proposal cites all relevant governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by the Specification-Derived Verification Plan below: new pytest coverage for resolve-path actuation AND v6-guard preservation, with executed-command evidence to be supplied in the implementation report.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project + Work Item + Project Authorization metadata cite the reliability-fixes home (WI-4807 is an active member; STANDING PAUTH covers source + test_addition by membership).
- `GOV-STANDING-BACKLOG-001` — WI-4807 is the backlog authority for this work.
- `GOV-RELIABILITY-FAST-LANE-001` — eligibility basis for routing this small P2 reliability defect through the reliability fast-lane under the STANDING PAUTH.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are platform paths under `E:\GT-KB`; no application surface touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — automatic lifecycle actuation reduces manual owner steps, consistent with artifact-oriented development.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — a governed terminal transition is the lifecycle trigger that should drive the retirement actuation.

## Prior Deliberations

- `DELIB-20266124` — owner decision (AUQ, 2026-06-25): route WI-4807 through the reliability fast-lane and implement.
- `DELIB-20265963` / `DELIB-20265964` — WI-4750 auto-retire verify-helper parity (implementation report VERIFIED + LO GO); the sibling work that established the VERIFIED-path actuation helper this proposal complements.
- `DELIB-20265887` — owner approval closing WI-4755 as covered (v6 scanner `member_completion_status` + lifecycle alignment already exists) — confirms the v6 completion predicate this fix reuses is settled.
- `DELIB-20265881` — the v6 automatic-retirement decision WI-4807 cites as the requirement basis.

## Owner Decisions / Input

- `DELIB-20266124` (AskUserQuestion, 2026-06-25 interactive PB session): the owner was presented the investigation and three authorization options and chose **"Reliability fast-lane + implement"** — add WI-4807 to the active PROJECT-GTKB-RELIABILITY-FIXES (its `PAUTH-...-STANDING` covers `source` + `test_addition` by active membership) and proceed through the bridge cycle, accepting that this extends that project's in-progress freeze+drain by one work item. WI-4807 was linked as a member of PROJECT-GTKB-RELIABILITY-FIXES on 2026-06-25 per that decision.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6
(+ `DELIB-20265881`) already mandates automatic retirement on the
all-active-members-terminal condition via ANY governed path. This proposal closes the
implementation gap for the non-VERIFIED paths; no new or revised requirement is needed.

## Proposed Scope

**1. `project/lifecycle.py` — two additive methods on `ProjectLifecycleService`:**

- `auto_retire_project_if_ready(project_id, *, project_root, changed_by=PROJECTS_CHANGED_BY, change_reason=<v6 default>) -> dict[str, Any] | None`
  — the per-project body of the existing `auto_retire_completed_projects` loop, scoped to one project: gate on `self.member_completion_status(project_id)["completion_ready"]`; if ready, `self.retire_project(...)` + `self._retire_project_work_items(...)`; return the retirement record or `None` (not ready / `ProjectLifecycleError` logged-and-skipped, preserving the existing best-effort contract). All v6 guards (active-members-only, `plan_incomplete`, keep-open election, WI-3481 multi-slice safeguard) live inside `member_completion_status` and are therefore honored unchanged.
- `auto_retire_projects_for_work_item(work_item_id, *, project_root, changed_by=..., change_reason=...) -> list[dict[str, Any]]`
  — resolve the work item's active project memberships via the existing `list_projects(include_terminal=False)` + `list_project_work_items(project_id)` pattern (the same traversal `_work_item_in_other_active_project` uses), and call `auto_retire_project_if_ready` for each, collecting non-`None` records.
- `auto_retire_completed_projects` is refactored to delegate its loop body to `auto_retire_project_if_ready` (no behavior change; the existing sweep + its tests remain green).

**2. `cli_backlog_update.py` — wire the actuation into the terminal-transition apply path:**

- After the successful, non-dry-run `db.update_work_item(...)` (current line ~219–230), when the existing `is_terminal_transition` flag (line 161) is `True`, call `ProjectLifecycleService(db).auto_retire_projects_for_work_item(work_item_id, project_root=_PROJECT_ROOT, ...)`.
- Best-effort: wrap in `try/except` so a lifecycle error NEVER fails the already-committed work-item update (mirroring `_auto_retire_completed_projects_after_verified`). Surface any retirements in the returned payload (e.g., `result["auto_retired_projects"]`) so the CLI can report them.
- `gt backlog resolve` is a thin wrapper over this same apply path, so it inherits the actuation with no separate change.

**3. `platform_tests/scripts/test_auto_retire_on_resolve.py` — new regression coverage** (reusing the fixture pattern from the sibling `test_auto_retire_on_verified.py`).

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence (to be run + reported) |
| --- | --- |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6 (actuation on non-VERIFIED path) | `test_auto_retire_on_resolve.py::test_resolve_last_terminal_member_retires_ready_project` — resolving the final terminal member via the `cli_backlog_update` apply path retires the project (`status=retired`, members→retired). |
| v6 guards preserved (no premature retirement) | `test_...::test_resolve_does_not_retire_when_plan_incomplete`, `::test_resolve_does_not_retire_with_keep_open_election`, `::test_resolve_does_not_retire_multi_slice_guarded` — guarded/keep-open/multi-slice projects stay active after a member resolve. |
| Best-effort isolation | `test_...::test_resolve_succeeds_when_retire_raises` — a monkeypatched `auto_retire_project_if_ready` raising does NOT fail the resolve. |
| No regression in existing sweep + guards | `python -m pytest platform_tests/scripts/test_auto_retire_on_verified.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py` remain green. |
| Code quality | `ruff check` AND `ruff format --check` on all changed `.py` files. |

Exact commands (project venv interpreter) to be recorded in the implementation report:
`python -m pytest platform_tests/scripts/test_auto_retire_on_resolve.py platform_tests/scripts/test_auto_retire_on_verified.py -q`,
`ruff check <changed.py>`, `ruff format --check <changed.py>`.

## Acceptance Criteria

1. A non-VERIFIED governed terminal transition (`gt backlog resolve` / `gt backlog update --resolution-status <terminal>`) that brings a project to all-active-members-terminal deterministically retires it (`lifecycle_status=retired`; members→retired), honoring the v6 guards.
2. Guarded / keep-open / multi-slice projects are NOT prematurely retired by a member resolve (WI-3481 safeguard preserved).
3. A lifecycle error during actuation does not fail the work-item update (best-effort).
4. The existing VERIFIED-path sweep and its tests remain green; `auto_retire_completed_projects` behavior is unchanged.
5. `ruff check` and `ruff format --check` pass on all changed files.

## Risks / Rollback

- Risk: a resolve unexpectedly retires a project that should stay open. Mitigation: the actuation reuses `member_completion_status` (the same predicate the VERIFIED path uses), so eligibility is identical to the already-shipped sweep; the guard tests (criterion 2) lock this. Rollback: remove the `cli_backlog_update.py` call site (the lifecycle methods are additive and inert if uncalled).
- Risk: performance on hot resolve path. Mitigation: the per-project method scopes work to the transitioned WI's projects (O(WI's projects)), not a full sweep.
- Risk: a retirement side-effect surprises a caller of `gt backlog resolve`. Mitigation: actuation is best-effort and additive to the return payload; the update result is unchanged on the failure path.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (additive methods + delegation refactor)
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` (best-effort actuation call site)
- `platform_tests/scripts/test_auto_retire_on_resolve.py` (new regression coverage)

## Recommended Commit Type

`fix` — repairs broken automatic-retirement behavior on the non-VERIFIED governed terminal-transition paths; no new capability surface beyond closing the v6 actuation gap.
