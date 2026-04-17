# Configuration Reference

All GroundTruth KB settings live in `groundtruth.toml` at the project root.
Run `gt config` to see the resolved values for your project.

## Resolution Order

Settings are resolved from four sources, where later sources override earlier:

1. **Defaults** — built into the package
2. **`groundtruth.toml`** — project configuration file
3. **Environment variables** — `GT_*` prefixed
4. **Constructor arguments** — when using the Python API directly

## Configuration File

### `[groundtruth]` section

Core project settings.

```toml
[groundtruth]
db_path = "./groundtruth.db"
project_root = "."
app_title = "My Project KB"
brand_mark = "MP"
brand_color = "#2563eb"
logo_url = "https://example.com/logo.png"
legal_footer = "Copyright 2026 My Company"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `db_path` | path | `./groundtruth.db` | Path to the SQLite MemBase |
| `project_root` | path | `.` | Root directory of the project (for assertion path resolution) |
| `app_title` | string | `GroundTruth KB` | Title shown in the web UI header and page title |
| `brand_mark` | string | `GT` | Short text shown in the web UI navigation |
| `brand_color` | string | `#2563eb` | Primary brand color as a hex value |
| `logo_url` | string | | Optional URL to a logo image for the web UI |
| `legal_footer` | string | | Copyright or legal text in the web UI footer |

!!! important "Path resolution"
    Relative paths (`db_path`, `project_root`, `chroma_path`) are resolved
    against the **config file's directory**, not the caller's working directory.
    This means `gt --config /path/to/project/groundtruth.toml summary` works
    correctly from any location.

### `[gates]` section

Governance gate plugins that enforce invariants at write time.

```toml
[gates]
plugins = ["my_project.gates:RequireTestGate", "my_project.gates:StatusFlowGate"]

[gates.config.RequireTestGate]
min_tests = 2

[gates.config.StatusFlowGate]
allowed_transitions = ["specified->implemented", "implemented->verified"]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `plugins` | list of strings | `[]` | Dotted Python import paths to gate classes |
| `config.<GateClass>` | dict | | Gate-specific configuration passed to the gate constructor |

Gate plugins are Python classes that implement the gate interface. They are
loaded by dotted path (e.g., `my_project.gates:MyGate`) and receive their
configuration subsection at initialization.

### `[search]` section

Semantic search backs the Deliberation Archive (DA) tier of ADR-0001: Three-Tier Memory Architecture.

Semantic search configuration for the Deliberation Archive (DA).

```toml
[search]
chroma_path = "./.groundtruth-chroma"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `chroma_path` | path | *unset* (`None`) | Directory for the ChromaDB persistent storage |

The `chroma_path` setting has three levels:

1. **Config default:** `None` (unset). The `GTConfig` dataclass does not
   assume ChromaDB is present.
2. **TOML override:** Set `chroma_path` in `[search]` to an explicit path.
   This is resolved relative to the config file's directory, like all paths.
3. **Runtime fallback:** When ChromaDB is installed and `chroma_path` is
   unset, the `KnowledgeDB` lazily creates the index at
   `<db_dir>/.groundtruth-chroma` on first use. This fallback keeps search
   data co-located with the database without requiring explicit config.

!!! note "Requires search extra"
    ChromaDB features require the `[search]` extra:
    ```bash
    pip install "groundtruth-kb[search]"
    ```

## Environment Variables

Every core setting has a corresponding `GT_*` environment variable that
overrides the TOML file value.

| Variable | Maps to | Example |
|----------|---------|---------|
| `GT_DB_PATH` | `db_path` | `GT_DB_PATH=/data/project.db` |
| `GT_PROJECT_ROOT` | `project_root` | `GT_PROJECT_ROOT=/app/src` |
| `GT_APP_TITLE` | `app_title` | `GT_APP_TITLE="Acme Project KB"` |
| `GT_BRAND_MARK` | `brand_mark` | `GT_BRAND_MARK=AC` |
| `GT_BRAND_COLOR` | `brand_color` | `GT_BRAND_COLOR=#e11d48` |
| `GT_LOGO_URL` | `logo_url` | `GT_LOGO_URL=https://example.com/logo.png` |
| `GT_LEGAL_FOOTER` | `legal_footer` | `GT_LEGAL_FOOTER="Copyright 2026 Acme"` |
| `GT_GOVERNANCE_GATES` | `governance_gates` | `GT_GOVERNANCE_GATES="mod:Gate1,mod:Gate2"` |

The `PORT` environment variable is also respected by `gt serve` for the
web UI port (separate from the config system).

## Config Auto-Discovery

When `--config` is not passed to `gt`, the CLI searches for `groundtruth.toml`
starting from the current working directory and walking up to 10 parent
directories. The first match is used.

```
current_dir/groundtruth.toml      ← checked first
current_dir/../groundtruth.toml   ← checked second
...                                ← up to 10 levels
```

If no config file is found, defaults are used and the database path
resolves relative to the current directory.

## Complete Example

```toml
# groundtruth.toml — full configuration example

[groundtruth]
db_path = "./groundtruth.db"
project_root = "."
app_title = "Acme Analytics KB"
brand_mark = "AA"
brand_color = "#e11d48"
logo_url = "https://acme.com/logo.svg"
legal_footer = "Copyright 2026 Acme Corp. All rights reserved."

[gates]
plugins = ["acme_gates:RequireTestGate"]

[gates.config.RequireTestGate]
min_tests = 1

[search]
chroma_path = "./.groundtruth-chroma"
```

## Python API

For programmatic access to configuration:

```python
from groundtruth_kb import GTConfig

# Auto-discover and load
config = GTConfig.load()

# Explicit config path
config = GTConfig.load(config_path=Path("path/to/groundtruth.toml"))

# Override at construction time
config = GTConfig.load(db_path="/custom/path.db", app_title="Custom Title")
```

See [Tooling](../method/10-tooling.md#python-api) for the full Python API
reference.

## Exceptions

`GTConfig.load()` raises typed exceptions when configuration cannot be
loaded, so library callers can distinguish between "no config supplied"
(exploration mode, defaults apply) and "caller asked for a specific file
that could not be used" (hard error).

| Exception | When raised | Recovery |
|-----------|-------------|----------|
| `FileNotFoundError` | An explicit `config_path` was supplied but the file does not exist. Auto-discovery (`config_path=None`) does **not** raise — it falls back to defaults when nothing is found. | Check the `--config` flag or create the file. Error message contains the attempted path. |
| `GTConfigError` | The file exists but contains invalid TOML syntax, **or** the file cannot be read due to a permissions problem. The original exception (`TOMLDecodeError` or `PermissionError`) is chained via `__cause__`. | Fix the TOML syntax or check file ownership and permissions. The error message names the offending file. |

```python
from groundtruth_kb import GTConfig, GTConfigError

try:
    config = GTConfig.load(config_path="/path/to/groundtruth.toml")
except FileNotFoundError as exc:
    # Explicit path doesn't exist
    print(f"Missing config: {exc}")
except GTConfigError as exc:
    # TOML syntax error or file permission problem
    print(f"Config load failure: {exc}")
    print(f"Underlying cause: {exc.__cause__}")
```

`GTConfigError` is exported from the package root as
`groundtruth_kb.GTConfigError` alongside `GTConfig` itself.

!!! note "CLI vs library behavior"
    The `gt` CLI uses `click.Path(exists=True)` on `--config`, so CLI users
    see a Click-level error (exit code 2) before `GTConfig.load()` is
    invoked. The behavior changes described above are observable by
    Python-level library callers.

## Warnings

`GTConfig.load()` emits `UserWarning` for config file conditions that are
not fatal but are likely to indicate a mistake.

| Warning | When emitted | What it means |
|---------|-------------|----------------|
| No `[groundtruth]` section | A TOML file was found but contains no `[groundtruth]` section. | The core settings will use env vars and defaults. `[gates]` and `[search]` sections, if present, are still applied. Often indicates a misspelled section name. |
| Unknown keys | The `[groundtruth]` section contains keys that are not recognized config fields. | The unknown keys are silently ignored. Often indicates a typo (e.g. `bran_color` instead of `brand_color`). The warning names all unknown keys. |

Warnings are issued via Python's standard `warnings` module at the
`GTConfig.load()` call site, so the warning location points at your code
rather than inside the library.

To treat configuration warnings as errors (useful in CI):

```python
import warnings
from groundtruth_kb import GTConfig

with warnings.catch_warnings():
    warnings.simplefilter("error", UserWarning)
    config = GTConfig.load()  # raises if any config warning is emitted
```

Or globally via the `PYTHONWARNINGS` environment variable or pytest's
`filterwarnings` option:

```ini
# pytest.ini / pyproject.toml
[tool.pytest.ini_options]
filterwarnings = ["error::UserWarning"]
```

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
