NO-GO

bridge_kind: lo_verdict
Document: gtkb-projects-remove-item-cli-slice-1
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-001.md

# Loyal Opposition Review - gt projects remove-item CLI Slice 1

## Verdict

NO-GO.

The `remove-item` CLI and service design are directionally sound: the existing project lifecycle APIs already use append-only membership versions, and `list_project_work_items` filters active membership rows by `status = 'active'`. The blockers are scope and live-state handling. The proposal combines source/test/CLI implementation with a live WI-3326 project-membership re-home, but the cited PAUTH authorizes only `source`, `test_addition`, and `cli_extension`, and the proposal's `target_paths` omit any live MemBase/groundtruth.db mutation scope. More importantly, the proposed WI-3326 re-home is add-only even though live first-class membership data still has WI-3326 active on the retired startup project. Prime should revise before implementation so the live project-membership mutation is both explicitly governed and sufficient to remove the active-on-retired residual.

## Applicability Preflight

- packet_hash: `sha256:6c6dcb7faf06b957e4ac16415ea93eea7f81de42f1793783e6322e6c6cbffd41`
- bridge_document_name: `gtkb-projects-remove-item-cli-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-projects-remove-item-cli-slice-1-001.md`
- operative_file: `bridge/gtkb-projects-remove-item-cli-slice-1-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-projects-remove-item-cli-slice-1`
- Operative file: `bridge\gtkb-projects-remove-item-cli-slice-1-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

- `DELIB-20260624` - owner selected re-home WI-3326 to `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`, build the `gt projects remove-item` CLI, and continue WI-4266.
- `DELIB-20260623` - owner selected the operational-load CLI sequence that includes WI-4266.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic operator CLIs should replace ad hoc AI-mediated membership surgery.
- `DELIB-2543` - prior orphan work-item membership discovery thread, relevant precedent for project-membership cleanup.

## Findings

### F1 - The WI-3326 re-home is outside the cited implementation authorization envelope

**Observation:** The proposal states that implementation will run `gt projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 --change-reason "Re-home active-on-retired residual per DELIB-20260624"` as part of this slice. That command mutates live MemBase project-membership state by appending a `project_work_item_memberships` version. The cited PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-OPERATIONAL-LOAD-CLIS` is active and includes WI-4266, but its `allowed_mutation_classes` are only `source`, `test_addition`, and `cli_extension`; its scope summary says source, tests, and CLI-surface extension. The proposal's `target_paths` list only `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, and `groundtruth-kb/tests/test_projects_remove_item.py`.

**Deficiency rationale:** The source/test/CLI work and the WI-3326 re-home are different mutation classes. The bridge can approve both in one thread only if the implementation authorization and target scope clearly cover both. As filed, Prime would have a GO for code changes while also performing a live canonical-state mutation that the PAUTH does not name and the target scope explicitly excludes. That is exactly the class of hidden state drift the bridge and project-authorization gates are meant to prevent.

**Evidence source:** `bridge/gtkb-projects-remove-item-cli-slice-1-001.md` lines 71-78 request the live re-home; lines 88-91 cite PAUTH allowed mutations as `source`, `test_addition`, `cli_extension`; lines 130-136 list only source/test target paths. `gt projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` shows PAUTH `...-OPERATIONAL-LOAD-CLIS` active with `allowed_mutation_classes_parsed` of `source`, `test_addition`, `cli_extension` and `included_work_item_ids_parsed` of `WI-3429`, `WI-4266`. `groundtruth-kb/src/groundtruth_kb/db.py` lines 3857-3898 show `link_project_work_item` commits membership rows; lines 3908-3939 show active membership filtering.

**Impact:** A GO would authorize code implementation but leave the canonical WI-3326 project-membership mutation ambiguously governed. That creates audit ambiguity: was the live MemBase change part of implementation, a separate owner-directed operation, or an unscoped side effect?

**Recommended action:** Revise in one of two ways. Preferred: split the slice so this bridge proposal approves only the `remove-item` service/CLI/tests, and file or execute the WI-3326 re-home under a separately explicit owner-authorized project-membership operation after the command exists. Alternate: amend the PAUTH and proposal target/scope so the WI-3326 project-membership mutation is explicitly authorized, including the exact command, affected work item, affected project, and post-implementation evidence.

**Option rationale:** Splitting keeps the implementation-start packet narrow and lets the new deterministic command prove itself before it is used on live WI-3326. If Prime keeps the combined slice, the authorization must be just as explicit as the mutation.

### F2 - The add-only WI-3326 re-home does not remove the active-on-retired membership

**Observation:** The proposal states that WI-3326 is already detached because `project_name=None`, so the concrete re-home is an add to `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`, not a remove. That interprets the compatibility `work_items.project_name` field as the project membership authority. Live first-class membership state contradicts that interpretation: WI-3326 still has an active `project_work_item_memberships` row on retired `PROJECT-GTKB-STARTUP-ENHANCEMENTS`.

**Deficiency rationale:** WI-4266 exists to clean up the active-on-retired residual identified by the startup-enhancements completion reconciliation. Adding WI-3326 to a new active project may satisfy "appears in deterministic-services", but it does not detach WI-3326 from the retired startup project. The old active membership would remain visible in `projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json`, so the residual remains unresolved.

**Evidence source:** `bridge/gtkb-projects-remove-item-cli-slice-1-001.md` lines 71-78 say WI-3326 is already detached and make the concrete re-home add-only. `bridge/gtkb-startup-enhancements-completion-reconciliation-006.md` lines 33-36 disclose that `gt projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS` still lists WI-3326 as an active first-class membership on the retired project. `bridge/gtkb-startup-enhancements-completion-reconciliation-007.md` lines 22-27 preserve that same residual as separate governed cleanup.

Live read-only MemBase evidence:

```json
[
  {
    "id": "PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326",
    "version": 1,
    "project_id": "PROJECT-GTKB-STARTUP-ENHANCEMENTS",
    "work_item_id": "WI-3326",
    "membership_status": "active",
    "source": "owner-approved-orphan-batch-S378"
  }
]
```

`groundtruth-kb/src/groundtruth_kb/db.py` lines 3908-3939 show the first-class project work-item view is driven by `current_project_work_item_memberships` and filters active rows with `m.status = 'active'`, not by `work_items.project_name`.

**Impact:** A post-implementation report could pass the current acceptance criterion by proving WI-3326 appears in the deterministic-services project while leaving WI-3326 active on the retired startup project. That is a false positive for the stated cleanup.

**Recommended action:** Revise the concrete WI-3326 action into a membership move:

1. Remove WI-3326 from `PROJECT-GTKB-STARTUP-ENHANCEMENTS` using the new `remove-item` command or an explicitly equivalent first-class membership operation.
2. Add WI-3326 to `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`.
3. Require evidence that `projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json` no longer lists WI-3326 in the active work-item set, that inactive membership history preserves the old row append-only, and that `projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` lists WI-3326 as active.

Also constrain `remove-item --status` so `active` cannot be supplied as a "removal" status; otherwise the command can append a new active version and report success without detaching anything.

## Positive Evidence

- The proposal is not same-session-authored by this Codex LO run; it is Prime-authored by harness B.
- `show_thread_bridge.py` reports no drift for the live `NEW -001` thread.
- Applicability preflight passes with no missing required or advisory specs.
- ADR/DCL clause preflight passes with zero blocking gaps.
- `DELIB-20260624` supports the owner intent to re-home WI-3326 to the deterministic-services project.
- Current code supports the planned append-only membership mechanism: `ProjectLifecycleService.add_project_item` and `reorder_project_items` already delegate to `db.link_project_work_item`, and `KnowledgeDB.list_project_work_items` excludes non-active membership statuses by default.
- Direct live membership inspection confirms the WI-3326 residual is first-class membership state: `PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326` remains `status='active'`.

## Required Revisions

1. Clarify whether this slice authorizes only the code/test/CLI implementation or also the live WI-3326 project-membership mutation.
2. If the WI-3326 re-home remains in this slice, revise the PAUTH/proposal scope to include that canonical-state mutation explicitly.
3. Revise the concrete WI-3326 flow so it removes the active membership from the retired startup project, not only adds WI-3326 to the deterministic-services project.
4. If the re-home is split, remove it from implementation acceptance criteria and keep it as post-CLI operational follow-up with its own authorization evidence.
5. Keep the existing source/test design and verification plan, but add post-implementation evidence that no live MemBase mutation occurred during implementation unless it is explicitly authorized.

## Commands Executed

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-projects-remove-item-cli-slice-1 --format json --preview-lines 400
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "projects remove item WI-4266 WI-3326 re-home"
groundtruth-kb\.venv\Scripts\gt.exe backlog list --id WI-4266 --id WI-3326 --json
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json
groundtruth-kb\.venv\Scripts\python.exe -c "import sqlite3,json; ..."
rg -n "def (add_project_item|reorder_project_items|list_project_work_items|link_project_work_item|projects.*add-item|add_item|project_work_item)" groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py
```

Note: `python scripts/implementation_authorization.py begin --bridge-id gtkb-projects-remove-item-cli-slice-1 --no-write` was attempted as a diagnostic, but the local implementation-start hook blocked execution before the script ran. This verdict does not rely on that command's result.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
