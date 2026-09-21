# 10. KB Tooling

This guide covers the practical use of the GroundTruth CLI and configuration system. Where the preceding documents describe *when* and *why*, this one describes *how*.

## Installation

```bash
# Install from PyPI
pip install groundtruth-kb
```

For development (tests, linting):

```bash
pip install "groundtruth-kb[dev]"
```

Tooling terminology follows ADR-0001: Three-Tier Memory Architecture — MemBase, MEMORY.md, and the Deliberation Archive (DA).

## Initializing a project

```bash
gt init my-project
```

This creates a project directory with:

- `groundtruth.toml` — configuration file
- `groundtruth.db` — empty MemBase

To seed with starter governance specs and example data:

```bash
gt --config my-project/groundtruth.toml seed --example
```

## Bootstrapping a desktop-ready prototype

If you want the shortest path from installation to a usable application
scaffold, register the application with its GT-KB host and use the single
native initializer:

```bash
gt --config <host>/groundtruth.toml project init my-project --project-id <PROJECT> --host-root <host> --owner "Your Organization" --profile local-only --harness claude
```

This command creates, inside the registered application root:

- `groundtruth.toml` pointing at the host authority
- the selected harness configuration projected from the host baseline
- `.github/workflows/` using the profile-tiered CI templates
- the application's artifact-boundary registry

Specifications, tests and work items live in the host's PostgreSQL authority;
`--spec-scaffold minimal|full` writes the inferred starter specifications there.
No local database is created and nothing is committed.

## Configuration

All configuration lives in `groundtruth.toml`:

```toml
[groundtruth]
db_path = "./groundtruth.db"
project_root = "."
app_title = "My Project KB"
brand_mark = "MP"
brand_color = "#2563eb"
legal_footer = "Copyright 2026 My Company"

[gates]
plugins = ["my_project.gates:MyGate"]

[gates.config.MyGate]
# Gate-specific settings here
```

### Resolution order

Configuration values are resolved in this order (later overrides earlier):

1. Defaults (built into the package)
2. `groundtruth.toml` file
3. Environment variables (`GT_DB_PATH`, `GT_PROJECT_ROOT`, `GT_APP_TITLE`, etc.)
4. Constructor arguments (when using the Python API directly)

### Path resolution

Relative paths in `groundtruth.toml` are resolved against the **config file's directory**, not the caller's working directory. This means `gt --config /path/to/project/groundtruth.toml status` works correctly from any location.

## CLI commands

### `gt status`

Compact read-only operating status from fresh native reads (service, schema, session binding, formal catalog); unavailable facts are reported, never inferred:

```bash
gt status
gt --config path/to/groundtruth.toml status --json
```

### `gt assert`

Run all assertions against the codebase:

```bash
gt assert                    # all specs with assertions
gt assert --spec GOV-01      # single spec only
```

### `gt history`

Show recent changes across all artifact types:

```bash
gt history              # last 20 changes
gt history --limit 50   # more changes
```

### `gt export`

Export the database to JSON:

```bash
gt export --output backup.json
```

### `gt import`

Import data from a JSON export:

```bash
gt import backup.json           # full import (fails on conflicts)
gt import backup.json --merge   # merge mode (skips duplicates)
```

### `gt config`

Display current configuration values:

```bash
gt config
```

## Automation

For scripts and automation, drive the `gt` CLI: the record verbs (`show`, `list`, `record`) accept `--json` and read or write the authority selected by `authority_url` in `groundtruth.toml`. There is no local database to open: `show` reads `GET /v1/<domain>/<id>`, `list` reads `GET /v1/<domain>` and `record` writes `PUT /v1/<domain>/<id>` on that authority.

```bash
# Create a specification (--expected-version 0 asserts a new record)
gt spec record --id SPEC-001 --fields-file spec-001.json --expected-version 0 --actor S1 --change-reason "Initial requirement" --json

# List current specifications
gt spec list --status active --json
```

where `spec-001.json` holds only the authored fields:

```json
{
  "title": "Users can create tasks",
  "type": "requirement",
  "status": "active",
  "description": "Users can create tasks with a title and priority."
}
```

### Key verbs

| Verb | Purpose |
|------|---------|
| `gt spec record` | Create or version a specification |
| `gt tests record` | Create or version a test |
| `gt backlog record` | Create (`--project-id`) or version a work item |
| `gt spec list` / `gt tests list` / `gt backlog list` | Query with filters (`--search`, `--limit`, `--after`) |
| `gt spec show` / `gt tests show` / `gt backlog show` | Get the current record by ID |
| `gt <domain> show <ID> --history` | The record's version chain |
| `gt db postgres readback-current --output <file>` | Publish a canonical current-state readback manifest |
| `gt status` | Component status from fresh native reads |

A `record` write is a compare-and-set: `--expected-version 0` creates, the current version amends, and a stale version is refused with `cas_conflict`.

Assertions are evaluated by `gt assert`, which reads the current specifications from the authority and exits `0` when the aggregate result is `PASS`:

```bash
gt assert --json
gt assert --spec SPEC-001 --json
```
