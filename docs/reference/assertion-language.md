# Assertion Language Reference

GroundTruth assertions are machine-checkable constraints attached to specifications.
They continuously verify that the codebase matches what was specified.

## Assertion Format

Assertions are stored as JSON arrays in the `assertions` field of specifications.
Each assertion is a dict with a `type` field and type-specific parameters.

```json
[
  {"type": "grep", "pattern": "def hello", "file": "src/main.py"},
  {"type": "file_exists", "path": "src/config.py"}
]
```

## Executable Types

### grep

Search file contents for a regex pattern.

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `type` | yes | | `"grep"` |
| `pattern` | yes | | Python regex pattern (aliases: `query`) |
| `file` | yes | | Relative file path or glob (aliases: `file_pattern`, `target`, `path`, `expected`) |
| `min_count` | no | `1` | Minimum number of matches required |
| `description` | no | | Human-readable explanation |

```json
{"type": "grep", "pattern": "class TaskStore", "file": "src/models.py", "description": "TaskStore class exists"}
```

### glob

Check that files matching a glob pattern exist.

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `type` | yes | | `"glob"` |
| `pattern` | yes | | Glob pattern (e.g., `**/*.py`) |
| `contains` | no | | Optional string that matched files must contain |
| `description` | no | | Human-readable explanation |

```json
{"type": "glob", "pattern": "tests/test_*.py", "description": "Test files exist"}
```

### grep_absent

Verify that a pattern does NOT appear in files (negative assertion).

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `type` | yes | | `"grep_absent"` |
| `pattern` | yes | | Python regex that must NOT match |
| `file` | yes | | Relative file path or glob |
| `description` | no | | Human-readable explanation |

```json
{"type": "grep_absent", "pattern": "SECRET_KEY|API_TOKEN", "file": "**/*.py", "description": "No hardcoded secrets"}
```

### file_exists

Check that a specific file exists and is a regular file (not a directory).

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `type` | yes | | `"file_exists"` |
| `file` | yes | | Relative file path (aliases: `path`) |
| `description` | no | | Human-readable explanation |

```json
{"type": "file_exists", "path": "src/config.py", "description": "Config module exists"}
```

### count

Grep with operator-based count comparison (more precise than `min_count`).

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `type` | yes | | `"count"` |
| `pattern` | yes | | Python regex pattern |
| `file` | yes | | Relative file path or glob |
| `operator` | no | `">="` | Comparison: `==`, `!=`, `>`, `>=`, `<`, `<=` |
| `expected` | no | `1` | Integer to compare against |
| `description` | no | | Human-readable explanation |

```json
{"type": "count", "pattern": "SAVE_FIELD", "file": "src/presets.py", "operator": "==", "expected": 8}
```

### json_path

Read a JSON or TOML file, navigate a dotted path, and compare the value.

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `type` | yes | | `"json_path"` |
| `file` | yes | | Relative path to `.json` or `.toml` file |
| `path` | yes | | Dotted path (e.g., `project.version`, `items.0.id`) |
| `expected` | no | | Expected value (omit to just check path exists) |
| `description` | no | | Human-readable explanation |

```json
{"type": "json_path", "file": "pyproject.toml", "path": "project.version", "expected": "1.0.0"}
```

## Composition Operators

### all_of

All child assertions must pass (logical AND).

```json
{
  "type": "all_of",
  "description": "Config is complete",
  "assertions": [
    {"type": "file_exists", "file": "groundtruth.toml"},
    {"type": "grep", "pattern": "project_root", "file": "groundtruth.toml"}
  ]
}
```

### any_of

At least one child must pass (logical OR). Skipped (non-machine) children do NOT
satisfy `any_of`.

```json
{
  "type": "any_of",
  "description": "Has config file",
  "assertions": [
    {"type": "file_exists", "file": "groundtruth.toml"},
    {"type": "file_exists", "file": "groundtruth.yaml"}
  ]
}
```

**Nesting limit:** Maximum depth of 3. Empty `assertions` arrays fail.

## Non-Machine Types

Any assertion type not listed above (e.g., `visual`, `behavioral`, `manual`) is
treated as a human note. These are stored in the database and displayed in reports
but are **skipped** during execution. They do not affect pass/fail outcomes.

## Path Confinement

All file paths are confined to the project root:

- **Absolute paths** are rejected (`/etc/passwd`, `C:\Windows`)
- **Parent traversal** is rejected (`../secret.txt`, `src/../../escape`)
- **Glob patterns** with `..` are rejected before traversal occurs
- **Symlink escapes** are caught by post-resolution boundary checks

## Field Aliases

Assertions accept multiple field names for convenience:

| Canonical | Aliases |
|-----------|---------|
| `pattern` | `query` |
| `file` | `file_pattern`, `target`, `path`, `expected` |

Aliases are valid at rest (in the database). They are normalized to canonical
form before execution.

## Schema Validation

Assertions are validated at write time in `insert_spec()`, `update_spec()`,
and `gt import`. Validation checks:

- Required fields present (or aliases)
- Operators in allowed set
- Path safety (no absolute paths or parent traversal)
- Composition depth and non-empty children
- Non-machine types pass without validation

Opt out with `validate_assertions=False` for tested migration tooling only.

## Running Assertions

```bash
# Run all assertions
gt assert

# Run for a single spec
gt assert --spec GOV-01

# Python API
from groundtruth_kb.assertions import run_all_assertions
summary = run_all_assertions(db, project_root)
```
