# `GTConfig.load()` Error Path Audit (Phase 4A)

Generated 2026-04-14 against `groundtruth-kb` commit `993f31b8d42ac272b9716c191527b599d08ba632`.

Source: manual read of `src/groundtruth_kb/config.py` (147 lines).

## Scope

This audit enumerates every way `GTConfig.load()` can fail and classifies each failure mode on two dimensions:

1. **Covered by tests?** — does the existing `tests/test_config.py` exercise this failure mode?
2. **Error message quality** — does the error include a specific message and a recovery suggestion?

Phase 4A is measurement only; Phase 4B will decide which gaps to fix.

## Resolution order

Per `config.py:4`: `constructor arg > env var (GT_*) > groundtruth.toml > defaults`.

- `config_path` passed explicitly OR searched via `_find_config()` (walks parents up to 10 levels)
- `_load_toml(config_path)` reads the TOML file
- `_load_env()` reads `GT_*` env vars
- Merged into a dict with overrides winning

## Failure modes

### 1. No `groundtruth.toml` anywhere

**Path:** `_find_config()` walks parents and finds nothing; returns `None`. `_load_toml(None)` returns `{}`. `load()` uses defaults.

- **Behavior:** Silent use of defaults. No warning.
- **Test coverage:** Probably yes (needs verification)
- **Error quality:** N/A (not an error; legitimate "no project config" state)
- **Assessment:** **OK**. Defaults are fine for exploration mode.

### 2. Explicit `config_path` points to a non-existent file

**Path:** `_load_toml(config_path)` at line 88 checks `config_path is None or not config_path.exists()` and returns `{}`.

- **Behavior:** **SILENT NO-OP.** User passes `gt --config /bad/path summary` and sees default config with no warning.
- **Test coverage:** Unknown — needs verification
- **Error quality:** 🚨 **BAD**. User has NO WAY to know their explicit `--config` flag was ignored.
- **Assessment:** **🚨 HIGH-PRIORITY FIX FOR PHASE 4B**. Should raise `FileNotFoundError` with a clear message: `"Config file not found: /bad/path. Use `gt --config /existing/path` or create the file."`

### 3. Explicit `config_path` points to a file with invalid TOML

**Path:** `_load_toml(config_path)` opens the file and calls `tomllib.load(f)`. `tomllib.TOMLDecodeError` is NOT caught. Propagates as unhandled exception up to the CLI.

- **Behavior:** User sees a raw TOML decoder traceback from Python's stdlib.
- **Test coverage:** Unknown
- **Error quality:** 🚨 **BAD**. Stack trace with no hint that `config_path` is the problem.
- **Assessment:** **🚨 MEDIUM-PRIORITY FIX FOR PHASE 4B**. Catch `tomllib.TOMLDecodeError`, re-raise as a custom `GTConfigError` with message: `"Invalid TOML in {config_path}: {error}. Check your groundtruth.toml syntax."`

### 4. File permissions denied

**Path:** `open(config_path, "rb")` at line 91 raises `PermissionError`. Not caught. Propagates.

- **Behavior:** User sees raw `PermissionError` traceback.
- **Test coverage:** Unlikely
- **Error quality:** 🚨 **BAD**. Same class as Finding 3.
- **Assessment:** **MEDIUM-PRIORITY FIX FOR PHASE 4B**. Wrap with clearer message: `"Cannot read config file {config_path}: permission denied."`

### 5. TOML file exists but has no `[groundtruth]` section

**Path:** `data.get("groundtruth", {})` returns `{}`. `load()` uses defaults for all fields.

- **Behavior:** Silent use of defaults even though the user has a TOML file. User may think their config is loaded.
- **Test coverage:** Possibly
- **Error quality:** LOW. No warning that the file's `[groundtruth]` section is missing.
- **Assessment:** **LOW-PRIORITY FIX FOR PHASE 4B**. Could log a one-line info: `"groundtruth.toml has no [groundtruth] section; using defaults"`.

### 6. TOML has `[groundtruth]` but unknown keys

**Path:** `merged = {...}`. Later `return cls(**{k: v for k, v in merged.items() if k in cls.__dataclass_fields__})` at line 81 filters out unknown keys.

- **Behavior:** Unknown keys are silently discarded.
- **Test coverage:** Unknown
- **Error quality:** LOW. User's typo in a key name is silently ignored.
- **Assessment:** **LOW-PRIORITY FIX FOR PHASE 4B**. Could log a warning: `"Unknown config keys ignored: [list]"`.

### 7. `db_path` / `project_root` / `chroma_path` with a non-absolute string

**Path:** Line 70-75 resolves relative paths against `anchor = config_path.resolve().parent` (or `Path.cwd()` if no config).

- **Behavior:** Relative paths are anchored correctly. This is actually good behavior.
- **Test coverage:** Yes, based on `tests/test_config.py` existence
- **Error quality:** Correct behavior, no error needed.
- **Assessment:** **OK**.

### 8. Env var `GT_DB_PATH` set to invalid path

**Path:** `_load_env()` reads the string value and puts it in the merged dict. Line 70-75 converts to `Path` object. No validation that the path is writable or that the parent directory exists.

- **Behavior:** `GTConfig` is constructed successfully. Downstream code (KnowledgeDB) will fail with SQLite connection error.
- **Test coverage:** Unlikely for env-var-with-invalid-path
- **Error quality:** LOW. Error surfaces late, in the DB layer, with SQLite-specific message.
- **Assessment:** **LOW-PRIORITY**. Validating paths upfront is a can-of-worms (is the parent dir supposed to exist? can we create it?). Leaving as a late-fail is defensible.

### 9. Env var `GT_GOVERNANCE_GATES` set to empty string or whitespace-only

**Path:** Line 79 splits on comma and filters empty strings: `[g.strip() for g in merged["governance_gates"].split(",") if g.strip()]`.

- **Behavior:** Empty list. Governance gates default to empty.
- **Test coverage:** Unknown
- **Error quality:** N/A (benign).
- **Assessment:** **OK**.

### 10. Constructor `overrides={db_path: 42}` (wrong type)

**Path:** `load()` passes the value through to `cls(**merged)`. Python dataclass accepts any value for a `Path` field because the type annotation is not enforced at runtime.

- **Behavior:** `GTConfig(db_path=42)` constructs successfully. Downstream `Path(db_path)` calls crash with `TypeError`.
- **Test coverage:** Unlikely
- **Error quality:** LOW. Error surfaces at first use, not at load time.
- **Assessment:** **LOW-PRIORITY**. Could add `__post_init__` runtime type checks, but that's a minor robustness gain.

### 11. TOML has `[gates]` section with malformed `plugins` list

**Path:** Line 100 assigns `result["governance_gates"] = gates_section["plugins"]` without validating the list structure.

- **Behavior:** Whatever `plugins` is (list, dict, string) is passed through. If it's not a list of strings, `GateRegistry.from_config()` will fail later.
- **Test coverage:** Unknown
- **Error quality:** LOW. Error surfaces in the gate loader, not at config load.
- **Assessment:** **LOW-PRIORITY**. Same as Finding 10.

### 12. TOML has `[gates.config.GateName]` with unknown gate class

**Path:** Line 104-105 passes the dict through. Error surfaces only when `GateRegistry.from_config()` can't find the gate class.

- **Behavior:** Late error from the gate loader.
- **Test coverage:** Unknown
- **Error quality:** Depends on `GateRegistry.from_config()` error message.
- **Assessment:** **OK-ish**, depends on the gate loader which is out of scope for this audit.

### 13. `_find_config()` depth limit (10 parents)

**Path:** Line 118: `for _ in range(10):`. If the user runs from 11+ levels deep, the config is not found.

- **Behavior:** Returns `None`, defaults used.
- **Test coverage:** Unlikely
- **Error quality:** No warning.
- **Assessment:** **LOW-PRIORITY**. 10 levels is almost always enough. Edge case for very deep directory structures.

## Summary table

| # | Mode | Severity | Current quality | Phase 4B priority |
|---|---|---|---|---|
| 1 | No config anywhere | N/A | OK (defaults) | — |
| 2 | Explicit `--config` non-existent | 🚨 HIGH | BAD (silent) | **HIGH** |
| 3 | Invalid TOML syntax | 🚨 HIGH | BAD (raw traceback) | **MEDIUM** |
| 4 | Permission denied | MEDIUM | BAD (raw traceback) | MEDIUM |
| 5 | No `[groundtruth]` section | LOW | LOW (silent) | LOW |
| 6 | Unknown TOML keys | LOW | LOW (silent) | LOW |
| 7 | Relative paths | N/A | OK | — |
| 8 | `GT_DB_PATH` bad path | LOW | LOW (late error) | LOW |
| 9 | `GT_GOVERNANCE_GATES` empty | N/A | OK | — |
| 10 | Constructor wrong type | LOW | LOW (late error) | LOW |
| 11 | Malformed `[gates.plugins]` | LOW | LOW (late error) | LOW |
| 12 | Unknown gate class | MEDIUM | depends | — |
| 13 | Depth-10 limit | LOW | LOW (silent) | LOW |

## Phase 4B priorities

**Urgent (ship in Phase 4B.1):**
1. Finding 2 — **Raise `FileNotFoundError` when `--config` path doesn't exist.** The current silent-ignore behavior will confuse any user who typos the path. Single-line fix in `_load_toml()`.
2. Finding 3 — **Wrap `tomllib.TOMLDecodeError`** with a clearer message pointing at the config file. Also a small fix.

**Nice-to-have (Phase 4B.2):**
3. Finding 4 — Wrap `PermissionError`.
4. Finding 5 — Log info when `[groundtruth]` section is missing.
5. Finding 6 — Log warning when unknown keys are filtered.

**Defer unless caller asks:**
- Findings 8, 10, 11, 13 — late-error semantics are OK for alpha maturity. Tighten only if users report confusion.

## Test coverage questions for Phase 4A

The audit flags "unknown" for several findings because I didn't read `tests/test_config.py` exhaustively. Phase 4A's commit includes this `config-errors.md` but does not add new tests. Phase 4B will:
1. Read `tests/test_config.py` to verify which failure modes are covered.
2. Add new tests for uncovered modes 2, 3, 4, 5, 6.
3. Implement the fixes from the priority list above.

## Non-blocking observation

The docstring audit (`docstrings.md`) shows `config.py` has **100% docstring coverage** — every function has a docstring. The issue is not missing documentation; it's missing error-path defense. These are orthogonal gaps.

---

*Generated as part of the Phase 4A measurement-only audit baseline.*
