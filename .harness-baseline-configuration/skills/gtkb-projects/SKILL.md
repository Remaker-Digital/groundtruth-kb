---
name: gtkb-projects
description: Use GT-KB MemBase-backed project lifecycle commands to create, inspect, order, dependency-link, authorize, and retire first-class project records without creating a second backlog authority.
license: "Proprietary - (c) 2026 Remaker Digital"
metadata:
  project: groundtruth-kb
  category: implementation and planning
---
# gtkb-Projects

Use this skill when work needs deterministic project lifecycle operations through
the `gt projects` CLI surface.

## Authority

Project, sub-project, work item, backlog, MemBase, implementation proposal,
implementation report, and verification meanings come from:

- `.harness-baseline-configuration/rules/operating-model.md`
- `.harness-baseline-configuration/rules/canonical-terminology.md`

This skill does not redefine those terms. Projects organize known work in the
MemBase backlog; they do not replace `current_work_items` or create a separate
backlog source of truth.

**CLI-only backlog/project access:** agents MUST read and mutate backlog and
project state through the governed `gt backlog` and `gt projects` CLI surfaces
(or skills that invoke those commands). Do not open `groundtruth.db` with
SQLite, import `KnowledgeDB` for routine backlog browsing, or fetch the full
backlog and post-filter locally. Use CLI filters instead.

## Backlog Query Surface

Use `gt backlog list` for governed backlog reads. Prefer `--json` when another
tool needs structured output.

Exact-value filters (repeatable where noted):

```powershell
gt backlog list --json
gt backlog list --id WI-1234 --json
gt backlog list --project GTKB-X --priority P1 --stage open --json
gt backlog list --approval-state bridge_authorized --approval-state implementation_authorized --json
gt backlog list --origin defect --component backlog --resolution-status open --json
```

Field-specific pattern and range filters:

```powershell
gt backlog list --field source_owner_directive:DELIB-123 --json
gt backlog list --field related_bridge_threads:gtkb-thread-slug --json
gt backlog list --match title:*scanner* --json
gt backlog list --match id:WI-48* --json
gt backlog list --range priority:P1..P2 --json
gt backlog list --range implementation_order:1..10 --json
```

Project-membership and sort controls:

```powershell
gt backlog list --member-of PROJECT-GTKB-DISPATCHER-RELIABILITY --json
gt backlog list --sort priority --sort id --json
gt backlog list --sort implementation_order --sort-desc --json
gt backlog list --contains dispatcher --limit 20 --json
```

Use `gt backlog show <WI-ID> --json` for one item. Use `gt backlog status`
for project-level backlog summaries.

## Commands

Use plural `gt projects` for MemBase project lifecycle work. Keep singular
`gt project` for scaffold, doctor, upgrade, and rollback surfaces.

Read operations:

```powershell
gt projects list
gt projects list --json
gt projects list --field source_project_name:"Backlog Triage and Hygiene" --json
gt projects list --match name:*DISPATCHER* --sort rank --json
gt projects show <PROJECT-ID>
gt projects show <PROJECT-ID> --json
```

Mutating operations require `--change-reason` and append a new MemBase version:

```powershell
gt projects create "<name>" --change-reason "<reason>"
gt projects update <PROJECT-ID> --status active --change-reason "<reason>"
gt projects add-item <PROJECT-ID> <WI-ID> --order 1 --change-reason "<reason>"
gt projects reorder <PROJECT-ID> <WI-ID> <WI-ID> --change-reason "<reason>"
gt projects retire <PROJECT-ID> --change-reason "<reason>"
gt projects link-bridge <PROJECT-ID> <bridge-thread-slug> --change-reason "<reason>"
gt projects update <PROJECT-ID> --activation-status authorized --change-reason "<owner-directed reason>"
gt projects update <PROJECT-ID> --activation-status "not authorized" --change-reason "<owner-directed reason>"
```

Use `--json` when another tool or agent needs machine-readable output.

## Project Dependencies

Versioned MemBase dependency records are the sole dependency authority.
`dependent_project_id` depends on `prerequisite_project_id`; do not infer edge
direction from physical compatibility fields or use `from` / `to` terminology.
Workers must use the nested CLI and must not call
`KnowledgeDB.add_project_dependency()` or write dependency rows directly.

Create one dependency:

```powershell
gt projects dependencies add `
  --dependent-project <PROJECT-ID> `
  --prerequisite-project <PROJECT-ID> `
  --kind requires_project_state `
  --required-state retired `
  --affected-gate authorization `
  --rationale "<why this dependency is required>" `
  --provenance "<decision, proposal, or work-item evidence>" `
  --change-reason "<reason for this version>" `
  --json
```

Read and validate dependency state:

```powershell
gt projects dependencies show <DEPENDENCY-ID> --json
gt projects dependencies list --project <PROJECT-ID> --json
gt projects dependencies list --dependent-project <PROJECT-ID> --json
gt projects dependencies list --prerequisite-project <PROJECT-ID> --json
gt projects dependencies validate --json
```

Retire and recover an edge:

```powershell
gt projects dependencies retire <DEPENDENCY-ID> --change-reason "<reason>" --json
gt projects dependencies recover <DEPENDENCY-ID> --change-reason "<reason>" --json
```

The initial kind, `requires_project_state`, supports required prerequisite
states `active`, `completed`, `retired`, and `cancelled`, and affected gates
`readiness`, `authorization`, `promotion`, and `closure`. Mutations append
versions and validate the complete active graph. Self-edges, cycles, unknown or
invalid endpoints, duplicate semantic edges, unsupported kind/state/gate
values, and contradictory lifecycle transitions fail without mutation.

Readiness output names the dependency, both endpoints, current and required
states, satisfaction, the affected or blocked gate, provenance, and a recovery
route. An unsatisfied edge blocks only its declared gate. Dependency
satisfaction and ordering never change project `activation-status`, grant bridge `GO`, work
intent, implementation-start authority, or protected-file mutation authority.
Rendered DAGs and cached projections are views only; use
`gt projects dependencies validate --json` when current authority is required.

## Safety Rules

- Do not write directly to `groundtruth.db` for routine project lifecycle work.
- Do not open `groundtruth.db` with SQLite or read the backlog through
  `KnowledgeDB` for routine agent workflows; use `gt backlog list` /
  `gt backlog show` with CLI filters.
- Do not create new project or backlog authority tables.
- Do not use `gt projects link-bridge` to edit or recreate the retired
  aggregate queue artifact. This command records a project artifact link with
  `artifact_type="bridge_thread"` only.
- Keep `add-item` to one explicit work item at a time.
- Keep `reorder` scoped to one selected project. It must name the active
  membership set exactly, so omitted or extra work items fail closed.
- If a requested operation would update multiple projects or bulk-update work
  items, stop and file a follow-on bridge proposal or dry-run inventory packet.
- Only an owner-directed update may change the project's `activation-status`.
  The field does not bypass bridge proposal review, `GO`, `target_paths`,
  implementation reports, or Loyal Opposition verification.

## Verification

For implementation work that changes this skill or the project lifecycle
surface, run the focused CLI and parity checks named by the governing bridge
proposal, normally:

```powershell
python -m pytest platform_tests/scripts/test_projects_cli.py -q
python -m pytest platform_tests/scripts/test_project_authorization.py -q
python -m pytest platform_tests/scripts/test_cli_backlog_list.py -q
python -m pytest groundtruth-kb/tests/test_project_dependency_ordering.py platform_tests/scripts/test_projects_cli.py -q
python scripts/check_project_dependency_ordering.py --json
python scripts/check_harness_parity.py --all --validate
python -m pytest platform_tests/scripts/test_projects_skill_adapter.py -q
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
```

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
