NEW

bridge_kind: implementation_report
Document: gtkb-projects-remove-item-cli-slice-1
Version: 010
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-009.md GO
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: feat
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS
Work Item: WI-4266
Owner Decision: DELIB-20260623
author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 2026-06-03T17:34:38Z
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style, /loop dynamic mode)

# Implementation Report - `gt projects remove-item` (WI-4266) Slice 1

## Attribution Note (orphan-impl adoption)

The lifecycle service method, CLI command, and original 8 test functions in this
slice were authored by a prior Prime Builder session
(`author_session_context_id: 3975dda7-2644-4926-8822-013f4d7aa4f2`, per
`bridge/gtkb-projects-remove-item-cli-slice-1-008.md:16`). That session committed no
changes before its work-intent claim expired (TTL elapsed by ~1h22m as of
2026-06-03T18:13Z). The implementation matched the -008 spec on the service +
CLI surface and on 8/9 of the spec-derived tests, but did **not** add the
`test_cli_remove_item_rejects_empty_status` test required to close the F1
finding from `bridge/gtkb-projects-remove-item-cli-slice-1-007.md` and named
in the GO@-009 verdict (`-009.md:34-39`).

This session (`2026-06-03T17:34:38Z`) acquired the work-intent claim under the
file-bridge-protocol mandatory pre-drafting step, inspected the orphan impl
against the -008 spec, added the missing F1-closing test, and filed this
implementation report. The git commit therefore carries the orphan impl as
authored by the originating session under the GO@-009 authorization; the
F1-closing test addition is attributed to this session.

This adoption pattern follows the precedent recorded for the slice-B pickup in
`bridge/gtkb-startup-refractor-slice-b-local-settings-hygiene-*` (VERIFIED).
No source/CLI behavior was altered beyond adding the missing test.

## Summary

Implements WI-4266 code slice per the GO@-009 plan:

1. `ProjectLifecycleService.remove_project_item(project_id, work_item_id, *,
   changed_by, change_reason, status="removed")` — appends a non-active
   membership version (default `status="removed"`), carrying forward
   role/order/source from the current active membership. Append-only via
   `db.link_project_work_item(...)`. Fails closed when no active membership
   exists. **F2 non-active-status invariant:** raises `ProjectLifecycleError`
   on empty/whitespace or case-insensitive `active` input.

2. `gt projects remove-item PROJECT_ID WORK_ITEM_ID --change-reason <text>
   [--status removed] [--changed-by ...] [--json]` — registered Click command
   that delegates to the service and maps `ProjectLifecycleError` to a
   non-zero `click.ClickException`.

3. 9 test functions (17 parametrized cases) covering the spec-derived
   verification plan. The F1-closing
   `test_cli_remove_item_rejects_empty_status` (4 cases) was added by this
   session to close GO@-009's required CLI-level empty/whitespace verification.

No live MemBase mutation: all tests use a temporary `KnowledgeDB`; the commit
touches only the three target paths plus this report and the bridge index.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` — `+59 / -0`
  (new method `remove_project_item`)
- `groundtruth-kb/src/groundtruth_kb/cli.py` — `+40 / -0`
  (new command `projects_remove_item`)
- `groundtruth-kb/tests/test_projects_remove_item.py` — `+254 / -0` net
  (new file: 9 test functions, 17 parametrized cases)
- `bridge/gtkb-projects-remove-item-cli-slice-1-010.md` — this report
- `bridge/INDEX.md` — `NEW: ...-010.md` prepended

The split-out WI-3326 re-home move per `DELIB-20260624` is NOT in this commit.

## Recommended Commit Type

`feat` — net-new operator command (`gt projects remove-item`), new service
method (`ProjectLifecycleService.remove_project_item`), and new test module.
Per the proposal-standards Conventional-Commits discipline, this is a new
capability surface, not maintenance.

## Specification Links

Carried forward verbatim from the GO@-009 proposal `-008` Specification Links:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed and tracked through the file bridge.
- `GOV-STANDING-BACKLOG-001` — WI-4266 governed backlog item.
- `GOV-08` — membership state must reflect reality; the non-active-status
  invariant prevents a false-success that would misrepresent active state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under the
  operational-load-CLIs PAUTH; scope matches its mutation classes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item / Owner Decision metadata present.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — membership active → non-active transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all files under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).

## Prior Deliberations

Carried forward from `-008`:

- `DELIB-20260623` — owner "tackle the 5 / CLIs first"; WI-4266 sequence.
- `DELIB-20260624` — owner re-home decision (WI-3326 move; split-out follow-up).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic operator CLIs.
- `gtkb-bridge-revise-cli-slice-1` (VERIFIED) — sibling operational-load CLI
  precedent (surface and test patterns followed here).

## Owner Decisions / Input

- **Owner AUQ "Operational-load CLIs first"** (`DELIB-20260623`): authorizes
  WI-4266 as second operational-load CLI.
- **Owner AUQ "Re-home WI-3326 + continue"** (`DELIB-20260624`): authorizes
  the WI-3326 split-out follow-up (NOT in this slice).
- **`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS`**
  (active; WI-4266; mutation classes `source` / `test_addition` /
  `cli_extension`) — covers the source/CLI/test scope of this commit exactly.

No new owner decision is requested by this report. The adoption of orphan
impl follows the precedent established by prior slice-B-style adoptions and
does not introduce new owner-decision scope beyond what the GO@-009
proposal already carried.

## target_paths

Carried forward from `-008` (no expansion):

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_projects_remove_item.py`

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-STANDING-BACKLOG-001`, `GOV-08`,
the project-lifecycle model, and the operational-load-CLIs PAUTH govern. No
new specification capture required.

## Spec-Derived Verification Plan (executed)

| Specification | Test | Expected | Result |
|---|---|---|---|
| `GOV-08` removal detaches | `test_remove_project_item_detaches_active_membership` | WI absent from active list; `status=removed` version exists | **PASS** |
| append-only preserved | `test_remove_appends_version_preserves_history` | new version appended; prior active version remains | **PASS** |
| fail-closed: no active membership | `test_remove_nonexistent_membership_raises` | raises `ProjectLifecycleError` | **PASS** |
| F2 invariant (service) | `test_remove_rejects_active_status` (params: `active`/`Active`/`ACTIVE`/`  active  `/`""`/`"   "`) | each raises `ProjectLifecycleError`; active membership untouched | **PASS** (6 cases) |
| F2 invariant (CLI, active) | `test_cli_remove_item_rejects_active_status` | `--status active` exits non-zero | **PASS** |
| **F1 -007 (CLI, empty/whitespace)** | `test_cli_remove_item_rejects_empty_status` (params: `""`/`" "`/`"   "`/`"\t"`) | `--status ""` (and whitespace) exits non-zero; active membership untouched | **PASS** (4 cases) |
| role/order/source carry-forward | `test_remove_carries_forward_role_and_order` | removed version preserves prior role/order/source | **PASS** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_remove_then_readd_cycle` | active → removed → active round-trips | **PASS** |
| CLI wiring | `test_cli_remove_item_invokes_service` | command calls the service and reports the removal | **PASS** |
| no-live-mutation (rev #4) | post-impl `git diff` + temp-DB tests | commit touches only the 3 target paths; no live membership row added | **VERIFIED below** |

Test commands and observed results:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  groundtruth-kb/tests/test_projects_remove_item.py -q --no-header -p no:cacheprovider
# 17 passed in 3.88s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check \
  groundtruth-kb/src/groundtruth_kb/project/lifecycle.py \
  groundtruth-kb/src/groundtruth_kb/cli.py \
  groundtruth-kb/tests/test_projects_remove_item.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check \
  groundtruth-kb/src/groundtruth_kb/project/lifecycle.py \
  groundtruth-kb/src/groundtruth_kb/cli.py \
  groundtruth-kb/tests/test_projects_remove_item.py
# 3 files already formatted
```

All tests use a temporary `KnowledgeDB`; the live `groundtruth.db` is not
mutated by the test suite.

## Acceptance Criteria (per `-008`)

1. `remove_project_item` detaches an active membership (append-only non-active
   status), carries forward role/order/source, fails closed when none exists.
   **MET.** Tests 1, 2, 3, 7 confirm.
2. `remove_project_item` rejects empty/whitespace and case-insensitive
   `active`; the CLI surfaces the rejection as a non-zero `ClickException`.
   **MET.** Tests 4, 5, 6 confirm.
3. **CLI verification covers BOTH the `--status active` case and the
   empty/whitespace `--status` case.** **MET.** Tests 5 and 6 (with 4
   parametrized empty/whitespace cases under test 6) confirm.
4. `gt projects remove-item` is registered and delegates to the service.
   **MET.** Test 9 confirms via `CliRunner`.
5. New test module passes; `ruff check` + `ruff format --check` clean.
   **MET.** 17/17 PASS; ruff lint + format checks both pass.
6. Pre/post bridge preflights pass (no missing required specs; 0 blocking
   gaps). **VERIFIED below.**
7. No live MemBase mutation during implementation: the commit changes only
   the three target paths and adds no `project_work_item_memberships`
   version. **MET.** `git diff --name-only` over the staged commit shows only
   the three approved source/test paths plus the report and INDEX entry. All
   tests use a temporary database (see `_seed`/`_service` helpers in the test
   module).

## Risks / Rollback

- **Risk: false-success removal** (`--status active`/empty). Mitigation: the
  non-active-status invariant rejects both at both service and CLI surfaces;
  service + CLI tests cover active AND empty/whitespace (10 cases total
  across service and CLI surfaces).
- **Risk: removing a non-active membership.** Mitigation: fails closed when no
  active membership; append-only + carry-forward makes a mistaken removal
  reversible via `gt projects add-item`.
- **Risk: orphan-impl adoption introduces hidden divergence.** Mitigation:
  cross-checked diff against the `-008` Scope section verbatim; the only
  in-scope element missing from the orphan impl was the F1-closing CLI test,
  which this session added. No source/CLI behavior was altered.
- **Rollback:** clean `git revert` of this commit removes the new service
  method, CLI command, and test file; no live MemBase mutation to undo.

## In-Root Placement Evidence

All paths under `E:\GT-KB` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_projects_remove_item.py`

No `applications/` paths. No paths outside the GT-KB project root.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
```

Observed result (operative file: `bridge/gtkb-projects-remove-item-cli-slice-1-010.md`):

- packet_hash: `sha256:b2acd422c4570e0e0c9435c424fa92ec7c595011b1ba61e43494a0e7f9de77c7`
- bridge_document_name: `gtkb-projects-remove-item-cli-slice-1`
- content_source: `indexed_operative`
- preflight_passed: `true`
- warnings.missing_parent_dirs: `[]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

All 7 applicable specs (4 blocking + 3 advisory) are cited and matched, per
the Specification Links section above and the path/content matchers
recorded by the preflight tool.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
```

Observed result:

- Bridge id: `gtkb-projects-remove-item-cli-slice-1`
- Operative file: `bridge\gtkb-projects-remove-item-cli-slice-1-010.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (exit 0 = pass)

All 4 `must_apply` blocking-severity clauses
(`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`,
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`)
have satisfying evidence in this report.

## Split-Out Follow-Up (WI-3326 re-home — NOT in this slice)

Unchanged from `-008`. After this CLI receives VERIFIED, a separately-authorized
two-step move (under a `project_membership_mutation` authorization) will:

1. `gt projects remove-item PROJECT-GTKB-STARTUP-ENHANCEMENTS WI-3326 --change-reason "Detach active-on-retired residual per DELIB-20260624"`
2. `gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 --change-reason "Re-home per DELIB-20260624"`

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
