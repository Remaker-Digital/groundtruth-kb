# 10. KB Tooling

This guide covers the practical use of the GroundTruth CLI, web UI, and configuration system. Where the preceding documents describe *when* and *why*, this one describes *how*.

## Installation

```bash
pip install groundtruth-kb
```

For the web UI (optional):

```bash
pip install groundtruth-kb[web]
```

For development (tests, linting):

```bash
pip install groundtruth-kb[dev]
```

## Initializing a project

```bash
gt init my-project
```

This creates a project directory with:

- `groundtruth.toml` — configuration file
- `groundtruth.db` — empty knowledge database

To seed with starter governance specs and example data:

```bash
gt --config my-project/groundtruth.toml seed --example
```

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

Relative paths in `groundtruth.toml` are resolved against the **config file's directory**, not the caller's working directory. This means `gt --config /path/to/project/groundtruth.toml summary` works correctly from any location.

## CLI commands

### `gt summary`

Display spec counts by status, test counts, and work item status:

```bash
gt summary
gt --config path/to/groundtruth.toml summary
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

### `gt serve`

Start the web UI:

```bash
gt serve                    # default port 8090
gt serve --port 9000        # custom port
gt serve --host 0.0.0.0     # listen on all interfaces
```

## Web UI

The web UI provides a read-only dashboard for browsing the knowledge database. It is served by a FastAPI application with Jinja2 templates.

Pages:

| Page | URL | Content |
|------|-----|---------|
| Dashboard | `/` | Spec counts, recent changes, status overview |
| Specifications | `/specs` | List with status filter |
| Spec detail | `/specs/{id}` | Full spec with version history |
| Tests | `/tests` | List with spec and result filters |
| Test detail | `/tests/{id}` | Full test with execution history |
| Operations | `/ops` | Operational procedures |
| Op detail | `/ops/{id}` | Procedure steps and variables |
| Environment | `/env` | Environment config entries |
| History | `/history` | Global change log with author filter |
| Assertions | `/assertions` | Assertion run results |

### Branding

The web UI supports project-specific branding via `groundtruth.toml`:

- `app_title`: page title and header text
- `brand_mark`: short text shown in the navigation (e.g., "GT", "MP")
- `brand_color`: primary color as hex (e.g., `#2563eb`)
- `logo_url`: optional URL to a logo image
- `legal_footer`: copyright or legal text in the page footer

## Python API

For scripts and automation, import `KnowledgeDB` directly:

```python
from groundtruth_kb import KnowledgeDB, GTConfig
from groundtruth_kb.gates import GateRegistry

# Load config and create gated DB
config = GTConfig.load()
registry = GateRegistry.from_config(
    config.governance_gates,
    gate_config=config.gate_config,
    project_root=config.project_root,
)
db = KnowledgeDB(db_path=config.db_path, gate_registry=registry)

# Insert a spec
db.insert_spec(
    "SPEC-001", "Users can create tasks",
    status="specified", changed_by="S1", change_reason="Initial requirement",
)

# List specs
for spec in db.list_specs(status="specified"):
    print(f"{spec['id']}: {spec['title']}")

db.close()
```

### Key methods

| Method | Purpose |
|--------|---------|
| `insert_spec()` / `update_spec()` | Create or version a specification |
| `insert_test()` / `update_test()` | Create or version a test |
| `insert_work_item()` / `update_work_item()` | Create or version a work item |
| `list_specs()` / `list_tests()` / `list_work_items()` | Query with filters |
| `get_spec()` / `get_test()` / `get_work_item()` | Get latest version by ID |
| `run_assertions()` | Execute assertions for a spec |
| `export_json()` / `import_json()` | Full database export/import |
| `summary_stats()` | Aggregate counts by status |
| `global_history()` | Cross-table change timeline |
