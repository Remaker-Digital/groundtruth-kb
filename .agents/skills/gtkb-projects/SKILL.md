---
name: gtkb-projects
description: Inspect and reconcile GT-KB programs, execution projects, single-parent work membership, formal links and dependencies through the native CLI; state the owner operations (authorization, membership moves and new execution projects) for the owner to run.
license: "Proprietary - (c) 2026 Remaker Digital"
metadata:
  project: groundtruth-kb
  category: implementation and planning
---
# Project and work constitution

Use this skill for the assigned project's outcome, membership and ordering.
A program sequences projects. An execution project groups the interdependent
changes that finish and commit together. Every work item has exactly one
execution-project parent. A label or related Bridge citation is not membership.
Size the result before making records; unrelated unfinished work must not prevent
a cohesive project from finishing. Reconcile existing work before adding it.

Read the current `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` and
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` through `gt spec show` when
they apply. The operating-model rule explains their wider context.

## Read current state

Use the configured native authority through the CLI. Supply `--config <file>`
before the command when selecting another installation. An unavailable service
is a refusal, not permission to read a local SQLite copy or cached projection.

```powershell
gt projects list --kind program --json
gt projects list --kind project --status active --json
gt projects show <PROJECT-ID> --json
gt backlog list --status open --priority P1 --search "<search text>" --limit 20 --json
gt backlog show <WI-ID> --json
gt context work-item <WI-ID> --json
gt projects readiness <PROJECT-ID> --gate readiness --json
gt projects readiness <PROJECT-ID> --gate closure --json
gt backlog readiness <WI-ID> --json
```

Project readback includes current members, dependencies and formal links.
Work-item readback includes the exact current parent. List results are bounded
and ordered by ID; use `--after <last-ID>` to continue. Readiness explains the
current prerequisite outcome; it is not GO, verification or authorization.
Task context provides the explicit formal-relationship floor. Investigate the
complete applicable formal closure rather than assuming stored links are exhaustive.

## Create or amend current records

Use a UTF-8 JSON fields file containing only the fields to change. Every write
requires `--actor`, `--change-reason` and `--expected-version`. Version 0 asserts
a new record; an amendment names the exact version just read. On a conflict,
read the current state and reconsider the requested change before retrying.
Read back the returned canonical result. Attribution is not a permission carrier.
Agents create programs and work items and amend the descriptive fields of
existing projects. Creating an execution project is an owner operation.

```powershell
gt projects record --id <PROGRAM-ID> --kind program --fields-file <fields.json> --expected-version 0 --actor <actor> --change-reason "<reason>" --json
gt projects record --id <PROJECT-ID> --fields-file <fields.json> --expected-version <version> --actor <actor> --change-reason "<reason>" --json
gt backlog record --id <WI-ID> --project-id <PROJECT-ID> --fields-file <fields.json> --expected-version 0 --actor <actor> --change-reason "<reason>" --json
```

Project fields include `name`, `purpose`, `target_outcome`, `scope_note`, `rank`
and optional `parent_project_id` naming an active program. Kind is immutable.
Project authorization and terminal status are not generic fields to amend here.
Programs have no authorization value and cannot contain work items.

A new implementation item's fields include `title`, `description`,
`source_spec_id`, `source_test_id` and `priority`. Its test must be executable
and belong to an active test-plan phase. Amend current work through the same
`backlog record` operation with its current version. Use `implementation_order`
and `depends_on_work_items` for current work ordering. Keep lifecycle status
with the Bridge and project-finalization services.

## Reconcile membership

Each open item has one current parent. When an item belongs in another project,
state the move for the owner under Owner operations; agents do not move work
items. There is no routine detach-to-unparented operation. Unmatched defects
enter `PROJECT-GTKB-NEW-WORK-INTAKE`, and the owner moves them to an execution
project.

## Owner operations

Changing a project's authorization, moving a work item between projects and
creating an execution project are owner operations. Agent harnesses refuse these
commands in every context, bound or not. When work needs one, state the needed
change and the exact command, filled in from current readback; the owner runs it
in their own terminal. A headless context whose NEW needs an authorization
change authors BLOCKED instead. Only explicit owner direction sets
authorization; membership changes, a GO, an agent recommendation or a prior
decision narrative do not set it.

```powershell
gt projects set-authorization <PROJECT-ID> --authorization "not authorized" --expected-version <project-version> --actor <actor> --change-reason "<owner-directed change>" --json
gt projects set-authorization <PROJECT-ID> --authorization authorized --expected-version <project-version> --actor <actor> --change-reason "<owner-directed change>" --json
gt projects move-item --work-item-id <WI-ID> --from-project <CURRENT-PROJECT-ID> --to-project <DESTINATION-PROJECT-ID> --expected-version <membership-version> --membership-order 1 --actor <actor> --change-reason "<reason>" --json
gt projects record --id <PROJECT-ID> --kind project --fields-file <fields.json> --expected-version 0 --actor <actor> --change-reason "<reason>" --json
```

An authorization change rewrites the existing project row and returns it. It
grants no path scope or per-action permission and creates no authorization
artifact. The intake project remains not authorized. A NEW proposal rechecks its
current parent; an already initiated chain continues after an authorization
change.

A move is one atomic replacement of the item's current parent. It names the
membership version from work-item readback, not the work-item or project
version. Both projects keep their authorization. A commit-terminal member is
immutable. The move must preserve foreign work and satisfy current work
dependencies; inspect any refusal before changing the proposed topology. A new
execution project starts authorized; the standing intake project is the
exception.

## Reconcile formal sources and prerequisites

```powershell
gt projects formal-links list --project-id <PROJECT-ID> --status active --json
gt projects formal-links show <LINK-ID> --json
gt projects formal-links record --id <LINK-ID> --fields-file <fields.json> --expected-version <version> --actor <actor> --change-reason "<reason>" --json
gt projects dependencies list --dependent-project <PROJECT-ID> --json
gt projects dependencies list --prerequisite-project <PROJECT-ID> --json
gt projects dependencies show <DEPENDENCY-ID> --json
gt projects dependencies record --id <DEPENDENCY-ID> --fields-file <fields.json> --expected-version <version> --actor <actor> --change-reason "<reason>" --json
```

A new formal-link fields file names `project_id` and `artifact_ref` (the current
active formal-record ID), with optional `notes`. Use version 0 to create it.
Retire or reactivate it with `{"status":"retired"}` or `{"status":"active"}`.
Endpoints are immutable: retire the old link and create the intended new link.
This operation cannot write Bridge links or Git commit evidence.

A prerequisite fields file names `dependent_project_id`,
`prerequisite_project_id`, `dependency_kind: "requires_project_state"`,
`required_prerequisite_state`, `affected_gate` and `rationale`.
The required state is `active`, `verified`, `retired` or `cancelled`; the gate
is `readiness` or `closure`. A project depends on the named prerequisite outcome.
The service validates the whole active graph and refuses cycles, invalid
endpoints, duplicate edges and unreachable closed states. Read back the affected
project's readiness after a change. Dependencies never set authorization.

## Review and completion

Current roots are rechecked at Bridge effects and precommit. Removing a formal
relationship cannot be hidden by an old proposal citation. After a material
formal-intent change, reconcile the affected attempt. For VERIFIED but
uncommitted work, start a fresh proposal/review/implementation attempt on the
same work item, preserving membership and bytes and inheriting no GO.

Each member is independently verified for its exact path, Git mode and object
identity. When all members are VERIFIED, the complete result is committed once
through the native project commit workflow and normal hooks. Only the Loyal
Opposition context whose VERIFIED delivery returns `project_ready_for_commit: true`
makes the one project commit. Prime Builder never commits. Exclude Bridge payloads
and generated projections. Related messages, a passing selected test or an
edited status label cannot establish project completion.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

For an existing obsolete `bridge_thread` or `completion_guard` relationship,
inspect its exact ID and version through `gt projects show <PROJECT-ID> --json`.
The same record writer accepts only `{"status":"retired"}` for that row; it
preserves identity and history and cannot rewrite or reactivate it. Read the
exact retired row back with `gt projects formal-links show <LINK-ID> --json`.
The project's `artifact_links` shows active links only, so the retired row must
disappear there. Formal-link list remains limited to specifications; exact show
also supports these obsolete relationships for correction readback and does not
make them formal authority. Git activation evidence and closed projects cannot
be retired through this correction route. No raw-table edit or replacement
authorization carrier is involved.
