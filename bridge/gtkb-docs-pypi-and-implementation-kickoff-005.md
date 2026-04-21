# Revised Post-Implementation Report: Part A — GT-KB Documentation Update

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Commits:** dbc3b95, 3db7235 (groundtruth-kb main)  
**Type:** Revised Post-Implementation Report (addressing NO-GO -004)

## NO-GO Findings Resolution

### Finding #1 — docs-check script rejects PyPI installs → FIXED

`check_no_bare_pypi_install()` renamed to `check_no_stale_github_install()`.
Logic inverted: now flags remaining `@ git+https://` references in current
docs instead of flagging PyPI-style installs. The publish.yml smoke test and
changelog are excluded (intentional GitHub refs).

Script header comment updated from "No bare PyPI-style install commands" to
"No stale GitHub-only install commands".

### Finding #2 — Remaining stale Git-only refs → FIXED

| File | Change |
|------|--------|
| `templates/ci/test.yml:32` | `groundtruth-kb[dev] @ git+...` → `groundtruth-kb[dev]` |
| `examples/task-tracker/.github/workflows/test.yml:32` | Same |
| `src/groundtruth_kb/cli.py:653` | ChromaDB install message → `pip install "groundtruth-kb[search]"` |

### Finding #3 — Contradictory "not published to PyPI" statements → FIXED

| File | Old | New |
|------|-----|-----|
| `docs/method/10-tooling.md:8` | "Install from GitHub (not published to PyPI)" | "Install from PyPI" |
| `docs/method/09-adoption.md:131` | "distributed via GitHub only (not PyPI)" | "published to PyPI" with version pin guidance |

### Finding #4 — Missing F1-F8 identifiers → FIXED

Feature mapping table in `docs/user-journey.md` now has an explicit ID column:
F1 (Schema Enrichment), F2 (Change Impact), F3 (Quality Gate), F4 (Constraint
Propagation), F5 (Intake), F6 (Scaffold), F7 (Dashboard), F8 (Reconciliation).

## Verification

```
$ python scripts/check_docs_cli_coverage.py
Checking CLI command coverage...
Checking gt project init snippets...
Checking mkdocs.yml nav references...
Checking version consistency...
Checking stale GitHub install detection...
Checking Python prerequisite...
Checking gt --version output...
Checking ChromaDB install message...

All documentation checks passed.
```

Exit code: 0. Zero issues.

## Conditions for VERIFIED (from -004) — Status

1. Update docs-check script → **DONE** (inverted to check for stale GitHub refs)
2. Remove remaining @v0.3.0 Git refs → **DONE** (3 files fixed)
3. Replace not-PyPI statements → **DONE** (2 files fixed)
4. Add F1-F8 identifiers → **DONE** (user-journey.md table updated)
5. Submit revised report with passing script output → **THIS REPORT**

## Total Changes (both commits combined)

- **23 files** changed across the groundtruth-kb repository
- **1 new file** created (docs/user-journey.md)
- **docs-check script** passes with 0 issues
- All current install guidance uses PyPI syntax
- No contradictory distribution statements remain in current docs
- User journey feature table has explicit F1-F8 traceability
