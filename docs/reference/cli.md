# CLI Reference

Complete reference for all `gt` commands. For a guided introduction, see
[Start Here](../start-here.md). For conceptual context, see
[Tooling](../method/10-tooling.md).

## Global Options

Every command inherits these options from the `gt` root group:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--version` | flag | | Show version and exit |
| `--config <path>` | path | auto-discovered | Path to `groundtruth.toml` |
| `--help` | flag | | Show help and exit |

**Config auto-discovery:** When `--config` is omitted, GroundTruth searches
upward from the current directory for `groundtruth.toml`. Relative paths
inside the config file resolve against the **config file's directory**, not
the caller's working directory.

---

## Core Commands

### gt init

Create a new GroundTruth project with a config file and empty database.

```
gt init [PROJECT_NAME] [--dir <path>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `PROJECT_NAME` | argument | `my-project` | Name of the project |
| `--dir` | path | `./<PROJECT_NAME>` | Target directory |

**What it creates:**

- `groundtruth.toml` — configuration file
- `groundtruth.db` — empty SQLite MemBase

!!! note
    For a full project scaffold with hooks, rules, CI, and seed data,
    use [`gt project init`](#gt-project-init) or
    [`gt bootstrap-desktop`](#gt-bootstrap-desktop) instead.

---

### gt bootstrap-desktop

Create a same-day desktop prototype with a full project scaffold.

```
gt bootstrap-desktop <PROJECT_NAME> [options]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `PROJECT_NAME` | argument | *required* | Name of the project |
| `--dir` | path | `./<PROJECT_NAME>` | Target directory |
| `--owner` | string | `Your Organization` | Project owner or client name |
| `--project-type` | string | `AI Service Prototype` | Project type label |
| `--brand-mark` | string | `GT` | Short brand mark for the KB web UI |
| `--brand-color` | string | `#2563eb` | Primary brand color (hex) |
| `--copyright` | string | | Copyright notice for scaffolded files |
| `--include-ci / --no-include-ci` | flag | `--include-ci` | Include GitHub Actions CI templates |
| `--init-git` | flag | off | Initialize a git repository |
| `--seed-example / --no-seed-example` | flag | `--seed-example` | Seed example domain specs and tests |

**What it creates:**

- Configuration, database, and seed data
- `CLAUDE.md`, `MEMORY.md`, `BRIDGE-INVENTORY.md`
- `.claude/hooks/` — automation hooks
- `.claude/rules/` — agent behavior rules
- `.github/workflows/` — CI templates (when `--include-ci`)

**Example:**

```bash
gt bootstrap-desktop acme-analytics \
  --owner "Acme Corp" \
  --brand-color "#e11d48" \
  --copyright "Copyright 2026 Acme Corp" \
  --init-git
```

---

### gt seed

Load governance starter data and optionally example domain content.

```
gt seed [--example]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--example` | flag | off | Also load example domain specs and tests |

**Without `--example`:** loads 5 governance specifications (GOV-01 through
GOV-05) that define the GroundTruth method itself.

**With `--example`:** also loads example domain specifications and tests
demonstrating the method with a sample task-tracker application.

!!! tip
    If your project was created with `gt project init` or `gt bootstrap-desktop`,
    governance specs are already seeded. Running `gt seed` again is idempotent —
    duplicates are skipped.

---

### gt summary

Print specification, test, and work item counts grouped by status.

```
gt summary
```

No additional options. Output includes:

- Specification counts by status (specified, in-progress, implemented, verified)
- Test and procedure counts
- Work item counts by status
- Document count
- Assertion pass/fail summary

---

### gt history

Print recent changes across all artifact types.

```
gt history [--limit <n>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--limit` | integer | `20` | Number of recent changes to show |

Output is a timestamped list showing: table name, record ID, version,
title, changed_by, and change reason.

**Example:**

```bash
gt history --limit 50
```

---

### gt assert

Run feature assertions against the project codebase.

```
gt assert [--spec <id>] [--triggered-by <label>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--spec` | string | all specs | Run assertions for a single spec ID |
| `--triggered-by` | string | `cli` | Trigger label for the audit trail |

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | All assertions passed |
| `1` | One or more assertions failed |

**Examples:**

```bash
# Run all assertions
gt assert

# Run for a single specification
gt assert --spec GOV-01

# Run with a custom trigger label (for CI pipelines)
gt assert --triggered-by github-actions
```

For the assertion language syntax, see
[Assertion Language Reference](assertion-language.md).

---

### gt config

Show the resolved configuration values.

```
gt config
```

No additional options. Output includes:

- `db_path` — resolved database file path
- `project_root` — resolved project root directory
- `app_title` — web UI title
- `brand_mark` — short brand identifier
- `brand_color` — primary color hex value
- `logo_url` — optional logo URL
- `legal_footer` — copyright or legal text
- `governance_gates` — configured gate plugins

See [Configuration Reference](configuration.md) for the full list of
settings and resolution order.

---

### gt export

Export the entire MemBase to JSON.

```
gt export [--output <path>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--output` | path | auto-generated | Output JSON file path |

When `--output` is omitted, the file name is auto-generated based on
the database name and timestamp.

**Example:**

```bash
gt export --output backup-2026-04-12.json
```

---

### gt import

Import data from a JSON export file.

```
gt import <FILE> [--merge]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `FILE` | argument | *required* | Path to a JSON export file |
| `--merge` | flag | off | Merge mode: skip duplicates on conflict |

**Without `--merge`:** performs a strict import. Fails on duplicate
primary key conflicts and rejects unknown tables or columns.

**With `--merge`:** uses `INSERT OR IGNORE` semantics — existing records
are preserved and only new records are added.

**Validation:** the import validates assertion schemas before inserting.
Records with invalid assertions are rejected.

**Importable tables:** specifications, tests, test_procedures,
operational_procedures, assertion_runs, session_prompts,
environment_config, documents, test_coverage, test_plans,
test_plan_phases, work_items, backlog_snapshots, testable_elements,
quality_scores.

**Example:**

```bash
# Full import
gt import backup.json

# Merge into existing database
gt import teammate-export.json --merge
```

---

### gt serve

Start the GroundTruth KB web UI.

```
gt serve [--port <n>] [--host <addr>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--port` | integer | `8090` | Port number (also reads `PORT` env var) |
| `--host` | string | `127.0.0.1` | Host to bind to |

!!! note "Requires web extra"
    The web UI requires additional dependencies. Install with:
    ```bash
    pip install "groundtruth-kb[web]"
    ```

**Examples:**

```bash
# Default: localhost:8090
gt serve

# Custom port
gt serve --port 9000

# Listen on all interfaces (e.g., for Docker)
gt serve --host 0.0.0.0 --port 8080
```

---

## Project Commands

Project scaffold, workstation verification, and upgrade commands.

### gt project init

Scaffold a new GroundTruth project with a selected profile.

```
gt project init <PROJECT_NAME> [options]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `PROJECT_NAME` | argument | *required* | Name of the project |
| `--profile` | choice | `local-only` | Scaffold profile (see below) |
| `--owner` | string | | Organization or owner name |
| `--copyright` | string | | Copyright notice |
| `--cloud-provider` | choice | `none` | Cloud provider for infra stubs |
| `--dir` | path | `./<PROJECT_NAME>` | Target directory |
| `--init-git / --no-init-git` | flag | `--no-init-git` | Initialize a git repository |
| `--include-ci / --no-include-ci` | flag | `--include-ci` | Include CI workflows (all profiles generate CI by default; `--no-include-ci` suppresses all CI regardless of profile) |
| `--seed-example / --no-seed-example` | flag | `--seed-example` | Seed example domain specs |
| `--integrations / --no-integrations` | flag | `--no-integrations` | Generate optional integration config files (Dependabot, CodeRabbit) |
| `--python-version` | string | `3.11` | Python version used in generated CI workflows |

**Profiles:**

| Profile | What it includes | CI tier |
|---------|-----------------|---------|
| `local-only` | Single-agent setup: KB, rules, hooks, Makefile | minimal (ruff + gt assert only) |
| `dual-agent` | Above + Loyal Opposition bridge, AGENTS.md | standard (ruff + gt assert; pytest/mypy as advisory comments) |
| `dual-agent-webapp` | Above + Dockerfile, docker-compose, web UI config | full (pytest + ruff + gt assert + build.yml + deploy.yml) |

!!! note "CI tier is chosen by profile"
    All profiles generate CI by default. The `--include-ci/--no-include-ci` flag
    controls whether CI is generated at all — `--no-include-ci` suppresses all CI
    for any profile. The CI tier (minimal / standard / full) is always determined
    by the profile, not the flag.

**Cloud providers:** `azure`, `aws`, `gcp`, `none`

**Examples:**

```bash
# Minimal project for solo use (no CI, no example specs)
gt project init my-project --profile local-only --no-seed-example --no-include-ci

# Dual-agent project with full CI suppressed
gt project init my-project --profile dual-agent --no-include-ci

# Full dual-agent webapp with Azure stubs and integration files
gt project init enterprise-kb \
  --profile dual-agent-webapp \
  --owner "Acme Corp" \
  --cloud-provider azure \
  --integrations \
  --init-git

# Use Python 3.12 in generated CI workflows
gt project init my-project --python-version 3.12
```

---

### gt project doctor

Check workstation readiness and optionally install missing tools.

```
gt project doctor [--auto-install] [--profile <profile>] [--dir <path>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--auto-install` | flag | off | Auto-install safe missing tools |
| `--profile` | string | auto-detected | Profile to check against |
| `--dir` | path | `.` | Project directory |

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | All checks passed |
| `1` | One or more checks failed |

When `--profile` is omitted, the profile is auto-detected from
`groundtruth.toml` in the target directory.

**Example:**

```bash
# Check current project
gt project doctor

# Check and auto-install missing tools
gt project doctor --auto-install
```

---

### gt project upgrade

Update scaffold files to match the current GroundTruth version.

```
gt project upgrade [--dry-run | --apply] [--force] [--dir <path>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--dry-run / --apply` | flag | `--dry-run` | Preview changes without writing |
| `--force` | flag | off | Overwrite customized files |
| `--dir` | path | `.` | Project directory |

**Default behavior is dry-run.** The command shows what would change
without writing anything. Use `--apply` to execute the upgrade.

**Example:**

```bash
# Preview what would change
gt project upgrade

# Apply the upgrade
gt project upgrade --apply

# Force-overwrite customized files
gt project upgrade --apply --force
```

---

## Deliberation Archive (DA) Commands

Commands for managing the Deliberation Archive (DA) and semantic search index.

See ADR-0001: Three-Tier Memory Architecture for how these commands interact with MemBase.

### gt deliberations rebuild-index

Rebuild the ChromaDB semantic search index from the SQLite database.

```
gt deliberations rebuild-index
```

No additional options. Drops and recreates the ChromaDB collection,
re-indexing all current deliberations from the database. SQLite remains
the authoritative source of truth.

!!! note "Requires search extra"
    ChromaDB must be installed for this command:
    ```bash
    pip install "groundtruth-kb[search]"
    ```

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | Index rebuilt successfully |
| `1` | ChromaDB not installed or rebuild failed |

### gt deliberations add

Insert a new deliberation with a caller-supplied identifier (append-only).

```
gt deliberations add --id <DELIB_ID> --title <TITLE> \
  --source-type <TYPE> --source-ref <REF> \
  --summary <SUMMARY> (--content <BODY> | --content-file <PATH>) \
  [--outcome <OUTCOME>] [--spec-id <SPEC>] [--work-item-id <WI>] \
  [--session-id <SESSION>] [--participants "a,b,c"] \
  [--changed-by <USER>] [--change-reason <REASON>] [--json]
```

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--id` | yes | Deliberation identifier (e.g. `DELIB-0123`) |
| `--source-type` | yes | One of `lo_review`, `proposal`, `owner_conversation`, `report`, `session_harvest`, `bridge_thread` |
| `--source-ref` | yes | Source artifact reference (path, URL, bridge file) |
| `--title` | yes | Human-readable title |
| `--summary` | yes | One- or two-sentence summary |
| `--content` / `--content-file` | yes (one) | Deliberation body (mutually exclusive) |
| `--outcome` |  | One of `go`, `no_go`, `deferred`, `owner_decision`, `informational` |
| `--spec-id` |  | Link to existing spec at insert time |
| `--work-item-id` |  | Link to existing work item at insert time |
| `--session-id` |  | Session identifier (e.g. `S290`) |
| `--participants` |  | Comma-separated participants list |
| `--changed-by` |  | Audit actor (default `gt-cli`) |
| `--change-reason` |  | Audit reason (default `Created via gt deliberations add`) |
| `--json` |  | Emit the inserted row as JSON |

Content is redacted at the DB layer before storage. Both inline `--content`
and file-based `--content-file` paths go through the same redaction pipeline.

Use `add` when the caller owns the identifier. For source-content idempotency,
use `upsert` instead.

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | Deliberation inserted successfully |
| `1` | Database write failed (e.g. duplicate `id`, invalid foreign key) |
| `2` | Click validation error: missing required flag, invalid `--source-type` / `--outcome` choice, or `--content` / `--content-file` mutual-exclusion violation |

### gt deliberations upsert

Insert or update a deliberation keyed by `(source_type, source_ref, content_hash)`.
Auto-generates a `DELIB-NNNN` identifier when no match exists.

```
gt deliberations upsert --source-type <TYPE> --source-ref <REF> \
  --title <TITLE> --summary <SUMMARY> \
  (--content <BODY> | --content-file <PATH>) \
  [--outcome <OUTCOME>] [--spec-id <SPEC>] [--work-item-id <WI>] \
  [--session-id <SESSION>] [--participants "a,b,c"] \
  [--changed-by <USER>] [--change-reason <REASON>] [--json]
```

Same options as `add` **except** no `--id` flag (passing `--id` exits with
code 2). Prints the deliberation ID on success so shell scripts can capture
it. Idempotent on identical `(source_type, source_ref, content_hash)`.

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | Deliberation row written or matched (idempotent) |
| `1` | Database write failed |
| `2` | Click validation error, including passing `--id` (which `upsert` does not accept) |

### gt deliberations get

Fetch a deliberation by ID (latest version) or its full version history.

```
gt deliberations get <DELIB_ID> [--history] [--json]
```

| Parameter | Description |
|-----------|-------------|
| `DELIB_ID` | Deliberation identifier |
| `--history` | Return all versions instead of the latest |
| `--json` | Emit result as JSON |

**Exit codes:** `0` on success, `1` if the deliberation is not found.

### gt deliberations list

List deliberations with optional filters.

```
gt deliberations list [--spec-id <ID>] [--work-item-id <ID>] \
  [--source-type <TYPE>] [--session-id <SESSION>] \
  [--source-ref <REF>] [--outcome <OUTCOME>] [--limit <N>] [--json]
```

All filters are optional and combine with logical AND. `--limit` performs a
CLI-side slice on the matching rows.

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | Query completed (empty result is not an error) |
| `1` | Database access failed |
| `2` | Click validation error on filter choices (e.g. invalid `--source-type`) |

### gt deliberations search

Search deliberations by semantic similarity with SQLite LIKE text fallback.

```
gt deliberations search <QUERY> [--limit <N>] [--semantic-only] [--json]
```

| Parameter | Description |
|-----------|-------------|
| `QUERY` | Free-text search query |
| `--limit` | Maximum results (default 5) |
| `--semantic-only` | Require ChromaDB and reject SQLite LIKE fallback rows |
| `--json` | Emit results as JSON |

The default path preserves the Python API's behavior: ChromaDB is used when
available, otherwise SQLite LIKE fallback kicks in. This keeps the base-install
CLI fully functional without the `[search]` extra.

`--semantic-only` is an opt-in strict mode: it requires ChromaDB to be
installed and filters out any row tagged `search_method="text_match"`. Exits
with code `1` if ChromaDB is not installed.

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | Search completed (empty result is not an error) |
| `1` | `--semantic-only` requested but ChromaDB is not installed |
| `2` | Click validation error on flag values (e.g. non-integer `--limit`) |

### gt deliberations link

Link an existing deliberation to a spec or work item. Exactly one of
`--spec` or `--work-item` must be supplied.

```
gt deliberations link <DELIB_ID> (--spec <SPEC_ID> | --work-item <WI_ID>) \
  [--role <ROLE>]
```

| Parameter | Description |
|-----------|-------------|
| `DELIB_ID` | Deliberation identifier |
| `--spec` | Spec to link (mutually exclusive with `--work-item`) |
| `--work-item` | Work item to link (mutually exclusive with `--spec`) |
| `--role` | Relationship role (default `related`) |

The CLI validates that both the deliberation and the target artifact exist
before writing the link row. Exits with code `1` and a descriptive error if
either entity is missing. Exits with code `2` if neither or both of `--spec`
and `--work-item` are supplied.

---

## Intake Commands

Requirement intake pipeline — classify owner intent, capture candidates, and
promote confirmed candidates to KB specs.

### gt intake classify

Classify owner text into `directive`, `constraint`, `preference`, `question`,
or `exploration` intent categories with numeric confidence.

```
gt intake classify <TEXT>
```

### gt intake capture

Capture a requirement candidate as a deliberation with full audit evidence
(raw text, classification, confidence, proposed spec fields).

```
gt intake capture <TEXT> --title <TITLE> --section <SECTION> [options]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `TEXT` | argument | *required* | Raw owner text |
| `--title` | string | *required* | Proposed spec title |
| `--section` | string | *required* | Proposed section |
| `--scope` | string | | Proposed scope |
| `--type` | string | `requirement` | Spec type (requirement, governance, etc.) |
| `--authority` | string | `stated` | Spec authority (stated, inferred, etc.) |

### gt intake confirm

Confirm a captured candidate. Creates a KB spec using the proposed fields,
returns F2 impact analysis, F3 quality tier, and F4 applicable constraints.

```
gt intake confirm <DELIBERATION_ID>
```

### gt intake reject

Reject a captured candidate with a required reason.

```
gt intake reject <DELIBERATION_ID> --reason <REASON>
```

### gt intake list

List intake candidates, filtering non-intake deliberations by discriminator.

```
gt intake list [--pending]
```

---

## Health Commands

Session health dashboard for monitoring project metrics over time.

### gt health

Show current health with delta from the last captured snapshot.

```
gt health
```

When no prior snapshot exists, displays current metrics without deltas.

### gt health snapshot

Capture a health snapshot for a session and display the report.

```
gt health snapshot <SESSION_ID>
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `SESSION_ID` | argument | *required* | Session identifier (e.g., S288) |

Captures lifecycle metrics, summary, quality distribution, and constraint
coverage as a snapshot. Uses `INSERT OR REPLACE` so repeated captures for
the same session replace the previous snapshot.

### gt health trends

Show recent health snapshots with rendered reports.

```
gt health trends [-n <LIMIT>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-n` / `--limit` | integer | `5` | Number of recent snapshots to display |

---

## Knowledge base maintenance (F8)

### gt kb reconcile

Run provenance and consistency detectors against MemBase.
Each detector produces a report with zero or more findings; the command
prints each report and a total. Exit code is always 0 — this is a
reporting command, not a gate.

```
gt kb reconcile [--orphans] [--stale <N>] [--authority] [--duplicates]
                [--provisionals] [--all] [--project-root <path>]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--orphans` | flag | off | Run the orphaned-assertion detector. Finds machine assertions whose file targets (literal or glob) no longer exist on disk. |
| `--stale <N>` | integer | off | Run the stale-spec detector with N session snapshots as the staleness threshold. Uses an F7 snapshot window with same-section activity gating; falls back to `changed_at` timestamps + `section_activity_days` when snapshot history is thin. |
| `--authority` | flag | off | Run the authority-conflict detector. Finds stated-vs-inferred spec pairs in the same `(section, scope)` with overlapping machine assertion targets. |
| `--duplicates` | flag | off | Run the duplicate-spec detector. Reports spec pairs whose titles overlap by >=90% of tokens. |
| `--provisionals` | flag | off | Run the expired-provisional detector. Reports provisional specs (`authority='provisional'`) whose replacement spec has lifecycle `status` in `{implemented, verified}`. |
| `--all` | flag | off | Run every detector (`--stale` uses N=5 by default in this mode). |
| `--project-root` | path | cwd | Root used to resolve orphaned-assertion file targets. |

**Behavior notes:**

- **No flags is equivalent to `--all`.** Calling `gt kb reconcile` with no
  flags runs every detector — useful for full-project sweeps.
- **Non-dict assertions are silently skipped** by the orphan detector (the
  F8 "plain-text safety" guarantee), so reconciliation can traverse specs
  that mix machine and human-readable assertion lists without aborting.
- **Duplicate pairs are canonicalized** (`spec_a < spec_b`) so output is
  deterministic across runs.
- **Provisional detector uses `db.get_provisional_specs()`** which filters
  on `authority='provisional' AND provisional_until IS NOT NULL`. The
  replacement's lifecycle `status` determines whether the provisional is
  reported as expired. Replacements still at `specified` or `deprecated`
  do NOT trigger expiration — the provisional is still load-bearing.

**Examples:**

```
# Full sweep — run every detector on the current project
gt kb reconcile

# Orphan detection only, with explicit project root
gt kb reconcile --orphans --project-root /path/to/project

# Stale spec detection with a 10-session threshold
gt kb reconcile --stale 10

# Authority conflicts + duplicates combined
gt kb reconcile --authority --duplicates

# Check for expired provisionals (cleanup pass)
gt kb reconcile --provisionals
```

---

## Scaffold commands (F6)

### gt scaffold specs

Generate a starter set of specifications for the current project. The
scaffold creates governance, infrastructure, AI-component, and compliance
template specs at `authority='inferred'` so owners can review and promote
them to `authority='stated'` via `gt` spec-edit flows or the Python API.

```
gt scaffold specs [--profile <minimal|full>] [--apply | --dry-run]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--profile` | choice | `minimal` | Scaffold profile: `minimal` (governance + infra) or `full` (adds ai_components + compliance). |
| `--apply` / `--dry-run` | flag | `--dry-run` | Dry-run (default) shows what would be generated without writing. `--apply` persists generated specs with `authority='inferred'`. |

**Behavior:**

- **Pre-existing handles are skipped.** If a spec with the same `handle`
  already exists in the KB, the scaffold does not overwrite it — the
  conflict is reported in `skipped`.
- **Quality scoring is run in both dry-run and apply modes.** Each
  generated spec is scored via `score_spec_quality()`; the report surfaces
  any bronze or needs-work tier warnings so the owner can revise or drop
  them before promotion.
- **`authority='inferred'` is the default for generated specs.** Owners
  must explicitly promote to `authority='stated'` via `db.update_spec()`
  to mark them authoritative.

**Examples:**

```
# Preview the minimal scaffold without writing
gt scaffold specs

# Preview the full scaffold (governance + infra + AI + compliance)
gt scaffold specs --profile full

# Actually insert the full scaffold into the KB
gt scaffold specs --profile full --apply
```

**`gt project init` integration:** `gt project init` does NOT run the
scaffold by default. To include scaffold specs during project creation,
call `scaffold_project()` with `ScaffoldOptions(spec_scaffold=...)` from
the Python API. A CLI flag for this is planned for a future release.

---

## Command Tree

```
gt [--config <path>] [--version]
├── init [PROJECT_NAME] [--dir]
├── bootstrap-desktop <PROJECT_NAME> [--owner] [--project-type]
│   [--brand-mark] [--brand-color] [--copyright]
│   [--include-ci/--no-include-ci] [--init-git]
│   [--seed-example/--no-seed-example] [--dir]
├── seed [--example]
├── summary
├── history [--limit]
├── assert [--spec] [--triggered-by]
├── config
├── export [--output]
├── import <FILE> [--merge]
├── serve [--port] [--host]
├── intake
│   ├── classify <TEXT>
│   ├── capture <TEXT> --title --section [--scope] [--type] [--authority]
│   ├── confirm <DELIBERATION_ID>
│   ├── reject <DELIBERATION_ID> --reason
│   └── list [--pending]
├── health
│   ├── snapshot <SESSION_ID>
│   └── trends [-n <LIMIT>]
├── project
│   ├── init <PROJECT_NAME> [--profile] [--owner] [--copyright]
│   │   [--cloud-provider] [--dir] [--init-git/--no-init-git]
│   │   [--include-ci/--no-include-ci] [--seed-example/--no-seed-example]
│   ├── doctor [--auto-install] [--profile] [--dir]
│   └── upgrade [--dry-run/--apply] [--force] [--dir]
├── scaffold
│   └── specs [--profile <minimal|full>] [--apply/--dry-run]
├── kb
│   └── reconcile [--orphans] [--stale <N>] [--authority]
│       [--duplicates] [--provisionals] [--all] [--project-root <path>]
└── deliberations
    ├── rebuild-index
    ├── add --id <ID> --source-type --source-ref --title --summary
    │   (--content | --content-file) [--outcome] [--spec-id] [--work-item-id]
    │   [--session-id] [--participants] [--changed-by] [--change-reason] [--json]
    ├── upsert --source-type --source-ref --title --summary
    │   (--content | --content-file) [--outcome] [--spec-id] [--work-item-id]
    │   [--session-id] [--participants] [--changed-by] [--change-reason] [--json]
    ├── get <DELIB_ID> [--history] [--json]
    ├── list [--spec-id] [--work-item-id] [--source-type] [--session-id]
    │   [--source-ref] [--outcome] [--limit] [--json]
    ├── search <QUERY> [--limit] [--semantic-only] [--json]
    └── link <DELIB_ID> (--spec | --work-item) [--role]
```

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
