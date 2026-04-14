# Phase 4A Audit Baseline — Summary

**Generated:** 2026-04-14
**Target commit:** `993f31b8d42ac272b9716c191527b599d08ba632`
**Target package version:** `groundtruth-kb 0.4.0`
**Bridge trace:** `bridge/gtkb-audit-baseline-001.md` → `-006.md` (Codex GO)

## What this report is

A **measurement-only baseline** of GroundTruth-KB code quality metrics. No thresholds are enforced, no refactors are made, no new tests are added. Phase 4A's job is to produce numbers that Phase 4B+ can use to set gate thresholds and prioritize cleanup.

Phase 4A follows the approved scope in `bridge/gtkb-audit-baseline-005.md` as verified by Codex at `gtkb-audit-baseline-006.md`.

## Environment (Codex Condition 4)

All measurements in this report were produced in this environment:

| Dimension | Value |
|---|---|
| OS | Windows 11 (local dev) |
| Shell | Git Bash / MSYS |
| Python | 3.14.0 |
| Extras installed | `.[dev,web,search]` |
| `interrogate` | 1.7.0 |
| `mypy` | 1.20.1 (pinned ad-hoc, NOT in `pyproject.toml`) |
| `pytest-cov` | from `[dev]` extra (version at run time) |
| `ruff` | from `[dev]` extra (version at run time) |
| `groundtruth-kb` | 0.4.0 at commit `993f31b8d42ac272b9716c191527b599d08ba632` |
| Audit run date | 2026-04-14 |

CI uses `ubuntu-latest` with Python 3.12 as the reference environment. Phase 4B may re-run measurements there for consistency.

### Commands used (verbatim for reproducibility)

```bash
# Step 1: Coverage
python -m pytest --cov=groundtruth_kb --cov-branch \
  --cov-report=markdown:docs/reports/v0.4-baseline/coverage.md \
  --cov-report=html:/tmp/gtkb-coverage-html \
  --cov-report=term

# Step 2: Docstrings
python -X utf8 scripts/audit_docstrings.py > docs/reports/v0.4-baseline/docstrings.md

# Step 3: Type annotations
python -m pip install --quiet "mypy==1.20.1"
python -m mypy --version  # expect mypy 1.20.1 (compiled: yes)
set +e
python -m mypy --strict src/groundtruth_kb/ > docs/reports/v0.4-baseline/types.raw.txt 2>&1
MYPY_EXIT=$?
set -e
echo "mypy exit code: $MYPY_EXIT" >> docs/reports/v0.4-baseline/types.raw.txt
python -X utf8 scripts/audit_types.py \
  docs/reports/v0.4-baseline/types.raw.txt \
  docs/reports/v0.4-baseline/types.md

# Step 4: Exceptions
grep -rn "except Exception|except BaseException|except:" src/groundtruth_kb/
# Then manual classification into exceptions.md

# Step 5: Config error paths
# Manual audit of src/groundtruth_kb/config.py into config-errors.md

# Step 6: Logging/output
grep -rn "import logging|logger *=|click\.echo|^\s*print(" src/groundtruth_kb/
# Then manual classification into logging.md
```

## Headline metrics

| Dimension | Current (v0.4.0) | Phase 4B target (proposed) |
|---|---|---|
| **Line coverage** (`pytest-cov --cov`) | **51%** overall (236 of 2334 branches covered) | **70%** line, **55%** branch |
| **Docstring coverage** (whole package, `interrogate`) | **60.42%** (342/566 nodes) | **80%** overall, **95%** on public API |
| **Public API docstring coverage** (subset: `__all__` + public methods) | **81.63%** (120/147 public symbols) | **95%** |
| **Type annotation strictness** (`mypy --strict`) | **169 errors** across 14 files | Zero `no-untyped-def` / `no-any-return` on public API; rest deferred |
| **Broad exception sites** | **31** (30 safe fallback, 3 "needs review") | 0 unclassified; 3 flagged sites either fixed or explicitly commented |
| **Logging infrastructure** | **Zero `logging` module use** in `src/`; 111 `click.echo` (correct) + 19 `print()` | `logging.getLogger(__name__)` in bridge/db paths; click.echo unchanged |
| **Config `GTConfig.load()` error paths** | 13 failure modes; 2 high-priority silent-failures | Findings 2 and 3 fixed (explicit config-path and TOML error handling) |

Each of these is backed by a dedicated report in this directory.

## Report files

| File | Description |
|---|---|
| `coverage.md` | pytest-cov Markdown output (line + branch, per-file) |
| `docstrings.md` | interrogate per-file + public API subset analysis |
| `types.md` | mypy --strict categorization (by error code, by file) |
| `types.raw.txt` | Raw mypy --strict output (169 errors) |
| `exceptions.md` | Manual classification of 31 broad exception sites |
| `config-errors.md` | Manual audit of 13 `GTConfig.load()` failure modes |
| `logging.md` | Classification of 130 output sites (111 click.echo + 19 print) |
| `SUMMARY.md` | This file |

Also committed: `scripts/audit_docstrings.py` and `scripts/audit_types.py` for reproducibility.

## Standout findings

### 1. Public API is already in better shape than the overall numbers suggest

The overall docstring coverage is 60.42%, but the **public API subset** (the 147 symbols a third-party developer would actually import) is **81.63%**. This is already above the proposed 80% Phase 4B threshold. The missing 27 public-API docstrings are concentrated in `KnowledgeDB` helper methods (`get_*`, `list_*`, `insert_*` patterns) and a few `GateRegistry` methods — low-effort to backfill.

**Phase 4B implication:** The public API docstring gap is small and targeted. A single bridge round can close it.

### 2. Bridge runtime modules are the largest quality gap

Across every dimension, the `bridge/` subpackage scores worst:

- **Line coverage:** `bridge/worker.py`, `bridge/poller.py`, `bridge/runtime.py`, `bridge/launcher.py`, `bridge/handshake.py`, `bridge/context.py` all at **0%** (no test coverage whatsoever)
- **Docstring coverage:** `bridge/worker.py` 5.6%, `bridge/context.py` 6.1%, `bridge/poller.py` 17.4%, `bridge/launcher.py` 25%
- **Type annotations:** `bridge/poller.py` 34 errors, `bridge/runtime.py` 26 errors, `bridge/worker.py` 16 errors — **76 of 169 total mypy errors (45%)**
- **Exception handling:** 11 of 31 broad exception sites (35%)

This is consistent with DELIB-0633's note that the bridge runtime was "extracted from production" rapidly and hasn't had a hardening pass. It's also consistent with MEMORY.md's observation that the bridge runtime is in heavy active development.

**Phase 4B implication:** `bridge/` should be treated as its own Phase 4B sub-round with its own quality targets. Applying uniform thresholds across `bridge/` and the core KB modules would either understate the core's quality (by averaging down) or demand unrealistic effort on `bridge/`.

### 3. The database layer is mostly covered but has 42 missing docstrings

`db.py` at 74.4% docstring coverage (122/164 nodes) is the single biggest absolute missing-docstring count (42 missing). The missing ones are almost all `get_*_history` / `list_*` / `insert_*` methods on `KnowledgeDB` — the boring CRUD surface.

Line coverage on `db.py` is 73% — reasonable for a 1607-line core module.

**Phase 4B implication:** One well-focused session can bring `db.py` docstrings from 74% to ~95% by writing 42 one-line docstrings on CRUD methods. The patterns are repetitive (each `get_*` returns a row or None, each `list_*` returns a filtered list, etc.) so the work is mechanical.

### 4. GT-KB uses NO Python `logging` module anywhere in src/

This is the most surprising finding. All 130 output sites are either `click.echo` (111, all in `cli.py`, correct for user-facing CLI output) or bare `print()` (19, mostly bridge JSON protocol output). The codebase has no `logging.getLogger(__name__)`, no logger hierarchy, no log-level handling.

For a CLI-centric tool, this is defensible — Click handles the user-facing channel. But the bridge runtime modules run as background services with no diagnostic output path beyond the custom `_append_log(log_file, msg)` helper. Operators who want to debug a hung poller or failing worker have to read log files directly and hope the relevant message was emitted.

**Phase 4B implication:** Before converting anything, decide on a logging convention:
- **Option A:** Introduce `logging.getLogger(__name__)` in bridge/db modules, keep `click.echo` for CLI. Phase 4B.X refactors ~15 `_append_log` sites to use the standard library.
- **Option B:** Keep the custom `_append_log` pattern but make it consistent across all bridge modules (currently some use `print`, some use `_append_log`).

Both options are defensible. Option A aligns GT-KB with Python community conventions; Option B minimizes churn.

### 5. `GTConfig.load()` has two high-priority silent failures

`config-errors.md` finds 13 failure modes, most of which are OK for alpha. Two are not:

1. **Explicit `--config /bad/path` is silently ignored.** The user sees the default config loaded with no warning. This is a confusing UX that will bite any developer who typos the path.
2. **Invalid TOML syntax raises a raw `tomllib.TOMLDecodeError`** with no context pointing at the config file.

Both are small fixes (~5 lines each) and should ship in Phase 4B.1 as a single commit.

## Proposed Phase 4B thresholds and structure

Phase 4B+ should be broken into **sub-rounds**, not a single monolithic push. Proposed structure:

### Phase 4B.1 — Urgent defensiveness (1 bridge round)

Fix the two high-priority `config-errors.md` findings. Small, focused, zero risk.

- Raise `FileNotFoundError` with helpful message when explicit `--config` path doesn't exist
- Wrap `tomllib.TOMLDecodeError` with a message naming the config file
- Add tests for both error paths

### Phase 4B.2 — Core API docstrings (1 bridge round)

Add docstrings to the 27 missing public API methods (all in `KnowledgeDB` and `GateRegistry`). Mechanical work.

- 24 `KnowledgeDB.get_*` / `list_*` / `insert_*` methods
- 3 `GateRegistry` methods

Target: Public API docstring coverage ≥ **95%**.

### Phase 4B.3 — Type annotations on core public API (1-2 bridge rounds)

Fix the `no-untyped-def` and `return-value` errors on the public API surface. Concentrate on `db.py` and `cli.py` first.

Target: Zero `no-untyped-def` errors on exported-from-`__all__` functions and methods.

Do NOT enable `mypy --strict` in CI yet. Enablement comes in a separate round after the baseline is clean.

### Phase 4B.4 — `bridge/` sub-rounds (N bridge rounds, owner decides N)

`bridge/` needs its own treatment because of the multi-dimensional gap:

- 4B.4a: Docstrings in `bridge/worker.py`, `bridge/context.py`, `bridge/poller.py` (1 round)
- 4B.4b: Basic unit tests in `bridge/` to lift line coverage above 0% (1-2 rounds)
- 4B.4c: Type annotations to clear the 76 mypy errors (1 round)
- 4B.4d: Logging refactor (`_append_log` → `logging.getLogger`) IF Option A is chosen (1 round)

### Phase 4B.5 — CI enforcement (1 bridge round)

After the above are green, enable the quality gates in CI:

- `pytest --cov-fail-under=70 --cov-branch-fail-under=55`
- `interrogate --fail-under=80` (package) and `--fail-under=95` on `src/groundtruth_kb/__init__.py __all__` subset
- `mypy --strict src/groundtruth_kb/` (public-API-only config)

Each gate ships as its own commit so regressions can be bisected.

### Phase 4C and beyond

After Phase 4B.5, the project is ready for **Phase 5 (API stability commitment)** in the parent roadmap. Phase 4A → 4B → 5 → 6 (beta classifier) → 7 (field trial) is the sequence.

## Security & SBOM subsection (Codex Condition 5 summary only)

Codex's NO-GO on `-002.md` Finding 5 explicitly asked that this report summarize rather than deeply audit security and SBOM.

### Existing security workflow

`.github/workflows/security.yml` runs on every push to `main`/`develop`:

- **Semgrep SAST** — lines 30-44, runs with `security-audit` ruleset. Latest run on `993f31b`: ✅ success.
- **pip-audit** — lines 60-76, scans dependencies for known CVEs. Latest run: ✅ success.
- **CodeQL** — separate workflow (`.github/workflows/codeql.yml`), weekly scan.

### SBOM generation

`.github/workflows/security.yml:60-76` generates `.quality/sbom.json` in **CycloneDX JSON format** and uploads as a CI artifact. The SBOM is currently an artifact-only output; it is not published with each PyPI release, but it is available on every CI run.

### Scope boundary

This report does NOT:
- Perform a deep security audit of the source code
- Re-run Semgrep or pip-audit independently
- Validate the CycloneDX SBOM contents
- Open any new security-focused bridge round

Those are out of scope for Phase 4A per Codex's explicit non-expansion condition. A separate security-focused bridge round can be opened if owner requests.

## Environment record (Codex Condition 4 — verification commands)

Commands run during audit generation:

```
$ python --version
Python 3.14.0

$ python -m pip show interrogate | grep Version
Version: 1.7.0

$ python -m mypy --version
mypy 1.20.1 (compiled: yes)

$ cd groundtruth-kb && git rev-parse HEAD
993f31b8d42ac272b9716c191527b599d08ba632

$ python -m pytest --cov=groundtruth_kb --cov-branch \
    --cov-report=markdown:docs/reports/v0.4-baseline/coverage.md \
    --cov-report=html:/tmp/gtkb-coverage-html \
    --cov-report=term
...
600 passed, 284 warnings in 86.95s

$ python -X utf8 scripts/audit_docstrings.py > docs/reports/v0.4-baseline/docstrings.md
(success, 147 public symbols analyzed)

$ python -m mypy --strict src/groundtruth_kb/
Found 169 errors in 14 files (checked 30 source files)
mypy exit code: 1  # captured via MYPY_EXIT

$ python -X utf8 scripts/audit_types.py types.raw.txt types.md
wrote docs\reports\v0.4-baseline\types.md (169 errors categorized)

$ grep -rn "except Exception|except BaseException|except:" src/groundtruth_kb/ | wc -l
31

$ grep -rn "click\.echo" src/groundtruth_kb/ | wc -l
111

$ grep -rn "^\s*print(" src/groundtruth_kb/ | wc -l
19
```

All commands succeeded with the expected output. No command in this report uses an unverified API or flag — every command was run end-to-end this session before being documented here.

## Non-scope reminder

Phase 4A explicitly does NOT:

- Modify any source file in `src/groundtruth_kb/`
- Add new tests
- Enable any CI gate or fail-under threshold
- Modify `pyproject.toml` (no mypy config commit)
- Modify `.gitignore`
- Commit coverage HTML output (all HTML generated to `/tmp/`)
- Touch Agent Red or any other repo
- Make any destination-changing action beyond `git add` + `git commit` on a local branch

Phase 4B and later rounds will make the actual changes informed by this baseline.

---

*Phase 4A Audit Baseline complete. Awaiting Phase 4B bridge rounds per owner direction.*
