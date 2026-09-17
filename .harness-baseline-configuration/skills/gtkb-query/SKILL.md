---
name: gtkb-query
description: Read current specifications, tests, test plans, work items, projects, bridge state and terminology from the native GT-KB authority through the gt CLI. Use when looking up project knowledge, checking a record's current status and version, finding open work items, or reviewing which tests a specification has.
argument-hint: "[query-type] [filter]"
allowed-tools: Bash, Read
license: "Proprietary - (c) 2026 Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: groundtruth-kb
  category: knowledge-management
  references:
    - references/api-reference.md
---
# Knowledge query

Read current canonical records through the native `gt` CLI. The authority is
the PostgreSQL service selected by `authority_url` in the project's
`groundtruth.toml` (or `GT_AUTHORITY_URL`); under GOV-SOT-SINGLETON-001 it is
the sole record source. There is no SQLite database or `KnowledgeDB` class to
import, and no fallback when the service is unavailable: an unavailable
authority is reported, never inferred from a file, a dashboard, a generated
projection or a prior session.

**Arguments:** `$ARGUMENTS[0]` = query type, remaining args = filters. Map them
to the commands below; [the CLI reference](references/api-reference.md) lists
every option and the response shapes.

## Quick Reference

| Query | Command |
|-------|---------|
| Operating status (authority, project, bridge, registry, formal) | `gt status --json` |
| One specification (GOV/SPEC/ADR/DCL/PB/REQ ids) | `gt spec show <ID> --json` |
| Specifications by keyword | `gt spec list --search "<text>" --limit 200 --json` |
| Specifications by status (`active`, `superseded`, `retired`) | `gt spec list --status active --limit 200 --json` |
| One test record | `gt tests show <TEST-ID> --json` |
| Tests linked to a specification | `gt tests list --spec-id <SPEC-ID> --limit 200 --json` |
| Tests by keyword | `gt tests list --search "<text>" --limit 200 --json` |
| Test plans, a plan's phases, one phase | `gt test-plans list --json`; `gt test-phases list --plan-id <PLAN-ID> --json`; `gt test-phases show <PHASE-ID> --json` |
| Open work items | `gt backlog list --status open --limit 200 --json` |
| Work items by keyword or priority | `gt backlog list --search "<text>" --json`; `gt backlog list --priority P1 --json` |
| One work item with its project membership | `gt backlog show <WI-ID> --json` |
| A work item's task context (project, formal roots, tests, predecessors) | `gt context work-item <WI-ID> --json` |
| Whether a work item's predecessors are available | `gt backlog readiness <WI-ID> --json` |
| Programs and projects | `gt projects list --kind program --json`; `gt projects list --kind project --status active --json`; `gt projects show <PROJECT-ID> --json` |
| Bridge queue and one attempt | `gt bridge queue --role pb --json` (or `--role lo`); `gt bridge show <document> --content --json` |
| Terminology | `gt terms list --status active --scope platform --json`; `gt terms show <TERM-ID> --json` |
| Version history of one record (R04) | `gt <domain> show <ID> --history --json`, e.g. `gt spec show <ID> --history --json` — available once the realignment update is installed; the current production service returns `authority_error` for this route |
| Deliberation history (R20–R23; read-only, no authorization or completion result) | `gt deliberations list --limit 200 --json`; `gt deliberations show <DELIB-ID> --json` — available once the realignment update is installed; the current production service returns `invalid_request` for these routes |

Omit `--json` for the human-readable rendering: `<ID> v<version>: <title>`,
then the body and the remaining fields.

## Reading results

- `list` returns at most `--limit` records (default 200) in deterministic ID
  order. A full page may have successors: repeat the same filters with
  `--after <last-returned-id>` until a short page returns. A listing is a
  bounded filter, not a semantic search, and does not prove absence.
- `show` returns the current version; with `--history` it also returns the
  recorded version chain (see the reference). A missing record is a typed
  `not_found` error naming the domain and id; an unreachable service is a typed
  authority error. Neither is a reason to open a database file, read a
  generated file, a dashboard or another harness's state.
- A specification's `status` (`active`, `superseded`, `retired`) is formal
  currency, not implementation or verification. A test record's `last_result`
  is an observed fact the writer never accepts from a client. A project reaches
  `verified` only through project finalization; a work item's
  `completion_evidence` names its Git commit.
- Every record carries `version`, `changed_by`, `changed_at` and
  `change_reason`. Quote the version a later amendment must name.

## Writing

This skill reads. Amendments use the domain writers with a freshly read
version: `gtkb-spec` (`gt spec record`), `gtkb-work-item` and `gtkb-projects`
(`gt backlog record`, `gt projects record`), and the bridge skills for
coordination. Never calculate a new ID from the largest ID in a listing;
creation is checked atomically with expected version zero.

## Key rules

- GOV-SOT-SINGLETON-001: the native authority behind the CLI is the one
  canonical home and reader for each fact; there is no second editable file
  map, cache or SQLite copy to query.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001: read at the decision boundary; a prior
  session's result, a projection or a dashboard is not current authority.
- Do not open a database file, import a `KnowledgeDB` class, or read another
  harness's configuration to recover knowledge.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
