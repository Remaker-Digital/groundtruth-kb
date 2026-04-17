# Revised Post-Implementation Report v3: GroundTruth-KB Documentation Completion v0.3.0

## Session

- **Session:** S284
- **GO reference:** bridge/groundtruth-docs-completion-006.md
- **NO-GO references:** bridge/groundtruth-docs-completion-008.md, bridge/groundtruth-docs-completion-010.md
- **Repository:** E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
- **State:** All changes uncommitted, pending Codex verification

## NO-GO v2 Remediation (010 findings)

### P1: Drift checker omits CLI source and non-MD template scopes → FIXED

**Root cause:** `check_version_consistency()` only scanned `*.md` files, missing YAML templates and Python source.

**Fix:** Introduced `_collect_scannable_files()` that gathers all user-facing files:
- `docs/**/*.md`
- `templates/**/*` (`.md`, `.yml`, `.yaml`, `.py`, `.toml`, `.cfg`, `.txt`)
- `README.md`
- `src/groundtruth_kb/cli.py`

**New check: `check_no_bare_pypi_install()`** — scans all scannable files for `pip install groundtruth-kb` not followed by `[extra]`, `@`, or ` @`. This catches bare PyPI-style installs that would fail since the package is GitHub-only.

**ChromaDB CLI message check expanded:** `check_chromadb_install_message()` now also inspects `src/groundtruth_kb/cli.py` for the "ChromaDB is not installed" error message, verifying it uses the `groundtruth-kb[search]` install syntax.

**Evidence — files now covered by version scan:**
- `src/groundtruth_kb/cli.py:647` — `@v0.3.0` ✓
- `templates/ci/test.yml:32` — `@v0.3.0` ✓
- `templates/ci/deploy.yml:59` — `@v0.3.0` ✓

**Total drift checks now: 8** (CLI coverage, project init snippets, mkdocs nav, version consistency, bare PyPI detection, Python prereq, gt --version, ChromaDB message).

### P2: gt config ChromaDB display → FIXED (3-case implementation)

**Three cases implemented in `src/groundtruth_kb/cli.py:465-472`:**

1. **Explicit path set:** `chroma_path:       /path/to/chroma`
2. **Unset + ChromaDB installed:** `chroma_path:       (unset — runtime fallback: /abs/path/.groundtruth-chroma)`
   - Shows the *actual resolved* fallback path, not a placeholder
3. **Unset + ChromaDB absent:** `chroma_path:       (unset — chromadb not installed)`

**Three new tests in `tests/test_cli.py`:**
- `test_config_chroma_path_explicit` — verifies explicit path display
- `test_config_chroma_path_unset_chromadb_installed` — verifies runtime fallback display
- `test_config_chroma_path_unset_no_chromadb` — monkeypatches `import chromadb` to raise ImportError, verifies "not installed" display

## Verification Results

| Check | Result |
|-------|--------|
| `python -m pytest -q --tb=short -p no:cacheprovider` | **421 passed**, 1 warning (was 418; +3 chroma_path tests) |
| `python -m ruff check .` | **All checks passed!** |
| `python -m ruff format --check .` | **51 files already formatted** |
| `python scripts/check_docs_cli_coverage.py` | **All documentation checks passed.** (8 checks) |
| `python -m mkdocs build --strict` | **Documentation built in 0.69 seconds** |

## Cumulative File Changes (All Phases)

**New files (7):**
- `docs/reference/cli.md` — CLI reference (14 commands)
- `docs/reference/configuration.md` — Configuration reference (3-level chroma_path)
- `docs/reference/templates.md` — Templates inventory (30 files)
- `docs/method/13-deliberation-archive.md` — Deliberation archive guide
- `docs/start-here.md` — Getting started walkthrough
- `.github/workflows/docs-check.yml` — Docs drift CI (8 checks)
- `scripts/check_docs_cli_coverage.py` — Drift check script

**Modified files (25):**
- `src/groundtruth_kb/cli.py` — chroma_path 3-case display (+3 new lines for import check)
- `src/groundtruth_kb/__init__.py` — Version 0.3.0
- `tests/test_cli.py` — 3 new chroma_path display tests (34 CLI tests total)
- `mkdocs.yml` — 5 nav additions + Mermaid config
- 13 Mermaid diagrams across 9 method/reference docs
- Version ref updates across docs, templates, README (19 files, S283)

## Decision Needed

No owner decision required. Ready for Codex verification.
