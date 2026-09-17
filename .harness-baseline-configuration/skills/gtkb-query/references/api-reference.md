# Native query CLI reference

Every query goes through the `gt` CLI to the authority selected by
`authority_url` in `groundtruth.toml` (or `GT_AUTHORITY_URL`). The commands
below are read-only; each was executed against the configured authority when
this reference was written, except the two routes marked "available once the
realignment update is installed" (`show --history` and the `deliberations`
group), whose option names were verified against the candidate's `--help`.
Unlisted options may exist in `--help` but are not documented here until they
are verified to behave.

## Common shape

- `<domain> list` options: `--limit N` (default 200, at least 1), `--after <ID>`
  (continue after that record id, same filters), `--search <text>`, `--json`.
- `<domain> show <ID>` options: `--history`, `--json`. Without `--json` the
  rendering is `<ID> v<version>: <title>`, the body, then `key: value` lines.
- `<domain> show <ID> --history` (R04) reads `/v1/<domain>/<id>/history` and
  returns `current` plus `history` entries (`version`, `changed_at`, `actor`,
  `reason`); text mode appends a `Version History:` block. Present on every
  domain's `show` (spec, tests, backlog, projects, test-plans, test-phases,
  terms, deliberations) — available once the realignment update is installed; the current production service returns `authority_error` for this route.
- Errors are typed: `not_found: Canonical record does not exist` with
  `{"domain": ..., "id": ...}`; `invalid_query: Unknown domain or unsupported
  filter` for a filter the domain does not accept; an authority error when the
  service refuses or is unreachable. There is no SQLite fallback.
- Records carry `id`, `version`, `changed_by`, `changed_at`, `change_reason`
  and the domain fields listed below.

## Status

```text
gt status
gt status --json
gt status --component authority --component registry --json
```

Fresh component reads (`authority`, `project`, `bridge`, `registry`,
`formal`, `session`), each PASS/UNKNOWN with its source and evidence. Nothing
in the output certifies a session context.

## Specifications

```text
gt spec show <ID> --json
gt spec list --search "<text>" --limit 200 --json
gt spec list --status active --limit 200 --json
gt spec list --status retired --limit 200 --json
gt spec list --search "<text>" --limit 200 --after <last-returned-id> --json
```

Ids cover every formal class: `GOV-*`, `SPEC-*`, `ADR-*`, `DCL-*`, `PB-*`,
`REQ-*` and legacy numeric ids. Fields: `title`, `type` (`requirement`,
`governance`, `design_constraint`, `architecture_decision`,
`protected_behavior`, ...), `status` (`active`, `superseded`, `retired`),
`description`, `assertions`, `constraints`, `tags`, `source_paths`, `parent`,
`affected_by`, `section`, `scope`, `priority`, `application_scope`,
`implementation_verified_at`, `retired_at`. `status` is formal currency only.

## Tests, test plans and phases

```text
gt tests show <TEST-ID> --json
gt tests list --spec-id <SPEC-ID> --limit 200 --json
gt tests list --search "<text>" --limit 200 --json
gt tests list --limit 200 --after <last-returned-id> --json
gt test-plans list --json
gt test-phases list --plan-id <PLAN-ID> --json
gt test-phases show <PHASE-ID> --json
```

Test fields: `title`, `spec_id`, `test_type`, `test_file`, `test_class`,
`test_function`, `expected_outcome`, `description`, `last_result`,
`last_executed_at`, `last_executed_on`, `application_scope`. Execution results
are observed facts; the writer refuses them from a client. Phase fields:
`plan_id`, `phase_order`, `title`, `description`, `gate_criteria`, `test_ids`,
`last_result`, `last_executed_at`.

## Work items (backlog)

```text
gt backlog list --status open --limit 200 --json
gt backlog list --search "<text>" --limit 200 --json
gt backlog list --priority P1 --limit 200 --json
gt backlog show <WI-ID> --json
gt backlog readiness <WI-ID> --json
gt context work-item <WI-ID> --json
```

`show` returns `work_item`, its single active `membership` (project id,
status, version) and `memberships`. `context work-item` adds the parent
project, formal roots, linked test and test-plan instructions and
`predecessors`. `readiness` explains whether each predecessor's required
result (for example `project_commit`) is satisfied. Work-item fields include
`title`, `description`, `component`, `priority`, `depends_on_work_items`,
`blocks_work_items`, `acceptance_summary`, `failure_description`,
`completion_evidence` (`git:<commit>` when committed).

## Programs and projects

```text
gt projects list --kind program --limit 200 --json
gt projects list --kind project --status active --limit 200 --json
gt projects show <PROJECT-ID> --json
```

Project fields: `kind`, `name`, `purpose`, `target_outcome`, `status`,
`authorization` (`authorized` or `not authorized`; the owner's only ordering
field), `parent_project_id`, `start_date`, `target_date`, `completed_at`,
`notes`. `show` also returns `artifact_links`. A project's `verified` status
comes only from project finalization.

## Bridge

```text
gt bridge queue --role pb --json
gt bridge queue --role lo --json
gt bridge show <document> --json
gt bridge show <document> --content --json
gt bridge state-report --json
```

`queue` lists `eligible` and `blocked` next actions for one role. `show`
returns the canonical `attempt` (head status and version, disposition, claim,
project and work item, verified artifacts, terminal commit) and, with
`--content`, the disposable `messages`. A bridge message is authoritative at
receipt only; re-read canonical state before acting on it.

## Terminology

```text
gt terms list --status active --scope platform --limit 200 --json
gt terms show <TERM-ID> --json
gt authority resolve "<term>" --scope platform --json
```

Fields: `canonical_term`, `definition`, `scope`, `authority_level`,
`lifecycle_status`, `accepted_synonyms`, `discouraged_synonyms`,
`forbidden_uses`, `source_authority`, `linked_artifacts`, `linked_services`.

## Deliberations (R20–R23, read-only history)

```text
gt deliberations list --limit 200 --json
gt deliberations list --source-type <type> --limit 200 --json
gt deliberations list --spec-id <SPEC-ID> --limit 200 --json
gt deliberations list --work-item-id <WI-ID> --limit 200 --json
gt deliberations list --search "<text>" --limit 200 --after <last-returned-id> --json
gt deliberations show <DELIB-ID> --json
gt deliberations show <DELIB-ID> --history --json
```

Available once the realignment update is installed; the current production service returns `invalid_request` for these routes. Deliberation
records are historical reasoning: they carry no authorization, currentness or
completion result. Filters the domain accepts: `--source-type`, `--spec-id`,
`--work-item-id`, plus the common `--search`, `--limit`, `--after`. Fields:
`spec_id`, `work_item_id`, `source_type`, `source_ref`, `title`, `summary`,
`content`, `content_hash`, `participants`, `outcome`, `session_id`,
`sensitivity`, `redaction_state`, `redaction_notes`, `origin_project`,
`origin_repo`.

## Writes are elsewhere

Amend records through the domain writers documented by `gtkb-spec`,
`gtkb-work-item`, `gtkb-projects` and the bridge skills: `gt <domain> record
--id <ID> --fields-file <fields.json> --expected-version <version> --actor
<current-context> --change-reason "<reason>" --json`, with zero only for
creation. Read the record back afterwards. No command here opens a database
file or imports a `KnowledgeDB` class.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
