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
- `groundtruth.db` — empty SQLite knowledge database

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

Export the entire knowledge database to JSON.

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
| `--include-ci / --no-include-ci` | flag | `--include-ci` | Include CI workflow templates |
| `--seed-example / --no-seed-example` | flag | `--seed-example` | Seed example domain specs |

**Profiles:**

| Profile | What it includes |
|---------|-----------------|
| `local-only` | Single-agent setup: KB, rules, hooks, Makefile |
| `dual-agent` | Above + Loyal Opposition bridge, AGENTS.md |
| `dual-agent-webapp` | Above + Dockerfile, docker-compose, web UI config |

**Cloud providers:** `azure`, `aws`, `gcp`, `none`

**Examples:**

```bash
# Minimal project for solo use
gt project init my-project --profile local-only --no-seed-example --no-include-ci

# Full dual-agent project with Azure stubs
gt project init enterprise-kb \
  --profile dual-agent-webapp \
  --owner "Acme Corp" \
  --cloud-provider azure \
  --init-git
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

## Deliberation Commands

Commands for managing the deliberation archive and semantic search index.

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
└── deliberations
    └── rebuild-index
```

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
