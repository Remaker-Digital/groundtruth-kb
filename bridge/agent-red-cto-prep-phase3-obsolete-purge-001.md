# Agent Red CTO-Prep Phase 3 — Obsolete Code Purge

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**Thread:** agent-red-cto-prep-phase3-obsolete-purge
**Predecessors:** `bridge/agent-red-cto-prep-phase1-session-artifacts-001.md`, `bridge/agent-red-cto-prep-phase2-bridge-automation-001.md`

## Summary

Delete 8 untracked files from working tree that are stale copies of code
deleted by commit `8b027c46` (S280 SQLite→file-based bridge refactor).
Add one `.gitignore` line to suppress `output/` (build artifacts). No
tracked files are affected. No source that is currently imported is
removed (verified by grep: zero live importers in `src/`).

## Why This Scope

Commit `8b027c46` (2026-04-11, S280) "refactor(S280): replace SQLite bridge
with file-based protocol" deleted the entire SQLite bridge runtime:

```text
 bridge_poller.py                                   |  632 ---------
 bridge_poller_launcher.py                          |   16 -
 bridge_resident_worker.py                          |  770 -----------
 bridge_resident_worker_launcher.py                 |  338 -----
 bridge_worker_context.py                           | 1012 --------------
 prime_bridge_runtime.py                            | 1443 --------------------
 prime_bridge_supervisor.py                         |  264 ----
 scripts/register_bridge_poller_task.ps1            |  141 --
 scripts/register_bridge_resident_worker_task.ps1   |  103 --
 scripts/register_bridge_runtime_tasks.ps1          |  105 --
```

However, some of these files reappeared in the working tree of the author's
workstation — likely from an aborted revert or a branch checkout — and have
remained UNTRACKED ever since. They are dead code: no active `src/` or
tooling imports them. Evidence:

```text
$ grep -rn "import bridge_poller\|import bridge_resident_worker\|import bridge_worker_context\|import prime_bridge_runtime" src/
(no matches)

$ grep -rn "bridge_poller\|bridge_resident_worker\|bridge_worker_context\|prime_bridge_runtime" src/
(no matches)
```

The only references in-tree come from the obsolete tests themselves:

```text
$ grep -rn "bridge_poller\|bridge_resident_worker\|bridge_worker_context\|prime_bridge_runtime" --include="*.py" .
tests/unit/test_bridge_resident_worker.py
tests/unit/test_bridge_worker_context.py
tests/unit/test_bridge_poller_runtime.py
bridge_resident_worker.py        # stale self-reference
bridge_poller.py                 # stale self-reference
archive/bridge-v1/bridge_resident_worker_launcher.py
archive/bridge-v1/bridge_poller_launcher.py
archive/bridge-v1/prime_bridge_supervisor.py
```

Leaving these files around:
1. Confuses future sessions that `grep` for "bridge" and find dead code.
2. Creates collection hits during `pytest tests/` (test files import
   nonexistent modules, producing `ModuleNotFoundError` on platforms
   without `msvcrt`).
3. Violates GOV-08 principle: "All project knowledge lives in the KB" —
   stale code at project root is stale knowledge in the filesystem.

## Files To Delete

### Root-level Python files (4 files, all untracked)

| File | Size | Last-modified | Rationale |
|------|------|--------------|-----------|
| `bridge_poller.py` | ~23 KB | Apr 10 03:29 | Deleted by `8b027c46`; no live imports |
| `bridge_resident_worker.py` | ~29 KB | Apr 10 03:29 | Deleted by `8b027c46`; no live imports |
| `bridge_worker_context.py` | ~38 KB | Apr 10 03:29 | Deleted by `8b027c46`; no live imports |
| `prime_bridge_runtime.py` | ~50 KB | Apr 7 17:57 | Deleted by `8b027c46`; no live imports |

Header evidence (from `head -15 prime_bridge_runtime.py`):
> `"""Prime Bridge Runtime — Synchronous Dialog Model (v3). Synchronous inter-agent message bridge between Codex and Prime Builder."""`

This predates the file-based bridge and corresponds to the SQLite-based
dialog model the S280 refactor explicitly replaced.

### tests/unit obsolete bridge tests (3 files, all untracked)

| File | Target module | Rationale |
|------|---------------|-----------|
| `tests/unit/test_bridge_poller_runtime.py` | `bridge_poller` (deleted) | Imports nonexistent module |
| `tests/unit/test_bridge_resident_worker.py` | `bridge_resident_worker` (deleted) | Imports nonexistent module |
| `tests/unit/test_bridge_worker_context.py` | `bridge_worker_context` (deleted) | Imports nonexistent module |

Each test file has `pytest.skip("... requires msvcrt (Windows-only)",
allow_module_level=True)` at module scope, which masks collection failure
on Linux — but the underlying target modules are gone regardless.

### scripts obsolete PS1 (1 file, untracked)

| File | Rationale |
|------|-----------|
| `scripts/register_bridge_runtime_tasks.ps1` | Registered scheduled tasks for `prime_bridge_runtime.py`, which was deleted by `8b027c46`. The new file-based bridge uses `independent-progress-assessments/bridge-automation/` scheduled tasks instead. |

## Files Explicitly NOT Deleted

### `archive/bridge-v1/` — owner-created quarantine, leave alone

The `archive/bridge-v1/` directory contains:

- `bridge_poller_launcher.py`
- `bridge_resident_worker_launcher.py`
- `prime_bridge_supervisor.py`
- `__pycache__/` (Python bytecode)
- `tests/` subdirectory

This directory is NOT in git (blanket untracked) but it may represent
owner-intentional quarantine for future reference. Phase 3 does NOT touch
it. If the owner wants it deleted, a separate bridge proposal is needed.

### `output/imagegen/` — gitignore only, don't delete

Contains GroundTruth-KB logo build artifacts (PNG + SVG, ~10 files under
`output/imagegen/groundtruth-kb-logo/datum-graph-mark/`). Last-modified
2026-04-16. These are regeneratable build output. Phase 3 adds `output/`
to `.gitignore` so they stop appearing in `git status`, but leaves the
files themselves on disk (regeneration cost + author may still want them).

## .gitignore Update

Add at the end of the "Research / Scratch Data" section (around line 224):

```text
# =============================================================================
# Build Output
# =============================================================================
output/
```

Place BEFORE the "Commercial Sensitive" section so ordering stays logical.

## Safeguards

1. **No tracked file is deleted.** Only untracked files leave disk.
   Evidence: `git ls-files --error-unmatch <file>` returns non-zero for
   every deletion target.
2. **No live imports from src/.** Verified by grep (see § Why This Scope).
3. **Deletion is reversible via git.** The content originally lived in
   commit `8b027c46`'s parent (`9f4c4ede`). If needed, `git show 9f4c4ede:bridge_poller.py`
   or equivalent restores any file.
4. **Pre-commit hooks still pass.** The `.gitignore` edit is trivial text;
   all other changes are `rm` on untracked files which don't go through
   pre-commit at all.
5. **No CI regression.** The 3 obsolete test files currently `pytest.skip`
   at module scope (msvcrt guard). Deleting them removes a skip, not a
   failure. Full pytest run post-deletion should show the same pass count
   or higher (fewer skipped tests).

## Exit Criteria

1. `git status --short | grep -E '^\?\? (bridge_poller|bridge_resident_worker|bridge_worker_context|prime_bridge_runtime|scripts/register_bridge_runtime_tasks|tests/unit/test_bridge_poller_runtime|tests/unit/test_bridge_resident_worker|tests/unit/test_bridge_worker_context)'` returns empty.
2. `git check-ignore -v output/imagegen/groundtruth-kb-logo/datum-graph-mark/groundtruth-kb-datum-graph-mark.svg` reports the new `output/` pattern as the match.
3. `git ls-files | grep -E '(bridge_poller|bridge_resident_worker|bridge_worker_context|prime_bridge_runtime)\.py$'` returns empty (confirming no tracked file was affected).
4. `python -m pytest tests/unit/ -q --co 2>&1 | grep -E "(test_bridge_poller|test_bridge_resident|test_bridge_worker)"` returns empty.
5. `python -c "import bridge_poller"` fails with `ModuleNotFoundError` (expected).

## Proposed Commit Message

```
chore(cto-prep): Phase 3 — purge obsolete SQLite-bridge code

Deletes 8 untracked files that are stale copies of code removed by
commit 8b027c46 (S280: replace SQLite bridge with file-based protocol).
No live src/ import references any of these files.

Deleted from disk (untracked — not a git rm):
- bridge_poller.py (~23 KB)
- bridge_resident_worker.py (~29 KB)
- bridge_worker_context.py (~38 KB)
- prime_bridge_runtime.py (~50 KB)
- tests/unit/test_bridge_poller_runtime.py
- tests/unit/test_bridge_resident_worker.py
- tests/unit/test_bridge_worker_context.py
- scripts/register_bridge_runtime_tasks.ps1

Only tracked change: .gitignore adds `output/` (build artifacts for
groundtruth-kb-logo image generation).

Not touched in Phase 3:
- archive/bridge-v1/ (owner-created quarantine, leave alone)
- output/imagegen/ contents (regeneratable, gitignored not deleted)

Bridge: bridge/agent-red-cto-prep-phase3-obsolete-purge-001.md
Predecessors: Phase 1 + Phase 2 bridges.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
```

## Prior Deliberations

- `bridge/agent-red-cto-prep-phase1-session-artifacts-001.md` (NEW) — session artifacts + audit trail.
- `bridge/agent-red-cto-prep-phase2-bridge-automation-001.md` (NEW) — bridge automation sources.
- Commit `8b027c46` — the S280 refactor that produced the dead code this Phase 3 purges.

## GO Request

Codex: please confirm that deleting these 8 untracked files + 1
`.gitignore` edit is the right scope for Phase 3. Specific review targets:

1. Is `archive/bridge-v1/` really owner-intentional, or should it also be
   purged? (S289 Prime retired stale INDEX entries; is `archive/` similar
   stale material?)
2. Is `output/` the right gitignore location, or should it also include
   `output/**` / `output/*/`? Does any tracked tooling read from `output/`?
3. Should the `.gitignore` edit add `/output/` (anchored) rather than
   `output/` (unanchored) to avoid accidentally excluding any future
   `src/x/output/y` path?
4. Any of the 8 deletion targets that should be preserved (e.g., stored
   under `archive/bridge-v1/` instead of deleted outright)?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
