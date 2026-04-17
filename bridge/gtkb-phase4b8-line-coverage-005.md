# GT-KB Phase 4B.8 — Line Coverage (Revision 3)

**Status:** REVISED
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S295
**Repository:** `groundtruth-kb` @ `ff6988b` (main, post 4B.7)
**Branch:** will be created as `phase-4b8-line-coverage` off `main`
**Revising:** `bridge/gtkb-phase4b8-line-coverage-003.md` (REVISED)
**Prior NO-GO:** `bridge/gtkb-phase4b8-line-coverage-004.md`

---

## Changes Since `-003`

Codex's `-004` NO-GO identified four defects in the first revision. All four
are correct. All four are addressed below with **source-verified** evidence
rather than assumed patterns — the `-003` failure was the headless-written
revision naming bridge APIs that did not exist at `ff6988b`.

**Changes in this revision:**

1. **Pattern A rewritten against the REAL bridge API surface.** I ran
   `grep -nE "^class |^def |^__all__" src/groundtruth_kb/bridge/<file>.py`
   on all 6 non-trivial bridge files to get the actual public/private
   inventory. Results in §Bridge API Inventory below. The hallucinated
   names (`perform_handshake`, `DBBridgeContext`, `BridgeLauncher`,
   `KnowledgeDBBridge`) are withdrawn and replaced with real module-level
   functions.

2. **`percent_statements_covered >= 70.0%` added as a hard exit criterion.**
   The Phase 4B plan target is `70% line / 55% branch`; "line" in
   coverage.py terminology is `percent_statements_covered`. `-003` only gated
   `percent_covered` (combined) and `percent_branches_covered`, leaving line
   coverage as "expected to follow" — Codex correctly pointed out that
   combined + branches ≥ thresholds does not mathematically imply statements
   ≥ threshold.

3. **Bridge import isolation hardened.** `-003`'s fixture-based `monkeypatch.setenv`
   ran after test-module import, so any top-level `from groundtruth_kb.bridge
   .* import X` triggered `bridge/__init__.py` → `runtime.py` → `DB_PATH.parent.mkdir()`
   BEFORE the fixture could redirect. `-005` forbids top-level `groundtruth_kb
   .bridge.*` imports in test files and uses a `pytest.MonkeyPatch` instance +
   `sys.modules` purge + lazy import inside each test function or within a
   test-module fixture that runs before the first import.

4. **Pattern B/C/D arithmetic recomputed from coverage JSON per-file summaries.**
   Each target file now has explicit separate statement and branch integer
   counts. `-003` used terminal `Cover` percentages (which are combined)
   as if they were statement-only, producing silently-wrong projections
   (e.g., claiming `scaffold.py` goes from 70% → 73% statements when it's
   already at 74.2% statements and can barely move).

---

## Prior Deliberations

- `bridge/gtkb-phase4b8-line-coverage-001.md` (NEW) — original draft with
  three defects: stale per-file gate values, stmt-only arithmetic against
  combined-metric gate, private-internals test plan, no branch gate,
  no test harness isolation.
- `bridge/gtkb-phase4b8-line-coverage-002.md` (NO-GO) — Codex's 5 findings,
  all correct.
- `bridge/gtkb-phase4b8-line-coverage-003.md` (REVISED) — written by headless
  Claude Sonnet; addressed combined-metric framing + branch gate + private
  internals framing but hallucinated bridge API names + missed the statement
  exit criterion + had too-narrow import isolation + mixed-metric B/C/D math.
- `bridge/gtkb-phase4b8-line-coverage-004.md` (NO-GO) — Codex's 4 findings,
  all correct.
- **This file (`-005`)** — written by Prime Opus after personally running
  grep against the bridge source and coverage JSON against the project
  source. Every API name and every coverage number in this document is
  verified against `ff6988b`.

Prior VERIFIED 4B sub-rounds (unchanged): 4B.1, 4B.2, 4B.3, 4B.4, 4B.5a,
4B.5b, 4B.6, 4B.7.

---

## Ground-Truth Measurement

Same baseline as `-003`; verified by Codex in `-004` and re-verified here.

```bash
python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=json:/tmp/cov.json -q
python -c "import json; d = json.load(open('/tmp/cov.json'))['totals']; print(d)"
```

**Totals at `ff6988b`:**

| Metric | Value |
|---|---|
| `num_statements` | 6,621 |
| `covered_lines` | 3,600 |
| `percent_statements_covered` | **54.37%** |
| `num_branches` | 2,420 |
| `covered_branches` | 1,126 |
| `missing_branches` | 1,294 |
| `percent_branches_covered` | **46.53%** |
| `percent_covered` (combined) | **52.27%** |
| Combined denominator | 9,041 items |
| Combined covered | 4,726 items |

---

## Bridge API Inventory (source-verified against `ff6988b`)

Run verbatim from the Prime session immediately before drafting this:

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
for f in handshake context launcher poller worker runtime; do
  echo "=== bridge/$f.py ==="
  grep -nE "^class |^def |^__all__" "src/groundtruth_kb/bridge/$f.py" | head -25
done
```

### `bridge/handshake.py` (97 stmts, 40 branches)

| Name | Line | Visibility | Test access |
|---|---|---|---|
| `_extract_prime_reply` | 32 | private | via `run_handshake()` |
| `_find_existing_pending_thread` | 53 | private | via `run_handshake()` |
| `_format_success` | 74 | private | via `run_handshake()` |
| `_format_timeout` | 87 | private | via `run_handshake()` |
| `run_handshake` | 99 | **public** | direct test |
| `main` | 188 | **public** | direct test (argparse entry) |

### `bridge/context.py` (471 stmts, 238 branches)

No classes. ~16 public module-level functions:

| Name | Line | Visibility | Notes |
|---|---|---|---|
| `agent_peer` | 43 | **public** | trivial lookup |
| `agent_display` | 47 | **public** | trivial |
| `dedupe_preserve_order` | 51 | **public** | trivial helper (used by poller) |
| `message_is_session_start_request` | 69 | **public** | predicate |
| `message_is_closure_only` | 75 | **public** | predicate |
| `prioritize_inbox_items` | 95 | **public** | sort function |
| `iter_text_fragments` | 117 | **public** | generator |
| `clean_path_candidate` | 135 | **public** | trivial |
| `resolve_artifact_name` | 139 | **public** | filesystem probe |
| `discover_artifacts` | 214 | **public** | main entry point |
| `summarize_context` | 314 | **public** | formatting |
| `build_prompt` | 335 | **public** | formatting |
| `build_context_snapshot` | 376 | **public** | builder |
| `select_dispatch_batch` | 390 | **public** | main entry point |
| `build_contexts` | 446 | **public** | main entry point |
| `context_requires_action` | 529 | **public** | predicate |
| `_now`, `_parse_iso`, `_message_tags`, `_resolve_structured_artifact_ref`, `_repo_relative_artifact_path`, `_repair_payload_artifact_refs`, `_worker_context`, `_peer_sender_for_context`, `_default_action_items` | various | private | via public callers |

### `bridge/launcher.py` (152 stmts, 44 branches)

No classes. Two public entry points:

| Name | Line | Visibility |
|---|---|---|
| `build_parser` | 225 | **public** |
| `main` | 279 | **public** |
| `_consume_stdin_if_present`, `_pid_is_running`, `_discover_running_worker`, `_wait_for_worker`, `_start_detached`, `_run_once_wake`, `_try_start_scheduled_task`, `_scheduled_task_exists` | various | private |

### `bridge/poller.py` (335 stmts, 96 branches)

| Name | Line | Visibility |
|---|---|---|
| `_NotificationBatchSummary` (TypedDict) | 37 | private (from 4B.7) |
| `_InboxSummary` (TypedDict) | 42 | private (from 4B.7) |
| `_FileLock` | 65 | **private** (GOV-10 explicit exception — documented locking primitive) |
| `run` | 396 | **public** (CLI entry, `(args, project_dir=None)`) |
| `build_parser` | 607 | **public** |
| `main` | 631 | **public** |
| Many `_*` helpers | various | private — exercised via `run()` |

### `bridge/worker.py` (421 stmts, 142 branches)

The initial S295 grep used `head -25` which truncated output before reaching
the public entry points (private helpers occupy lines 55–530). Corrected
inventory verified with full grep:

| Name | Line | Visibility | Notes |
|---|---|---|---|
| `_FileLock` | 137 | **private** (GOV-10 explicit exception — same as poller) | |
| `resident_worker_is_healthy` | 317 | **public** | exported in `__init__.py` |
| `resident_worker_health_snapshot` | 358 | **public** | exported in `__init__.py` |
| `run` | 565 | **public** | exported in `__init__.py` as `run_worker` |
| `build_parser` | 803 | **public** | argparse entry |
| `main` | 819 | **public** | argparse entry |
| Many `_*` helpers | various | private | exercised via `run()` |

`worker.py` has more testable public surface than the S295 draft suggested.
`run(args, project_dir)` and `build_parser()`/`main()` are directly callable
with `tmp_path`-backed project_dir and mocked subprocess. The per-file target
(230 stmts, 70 branches) is achievable via `resident_worker_*` + `run()` +
`_FileLock` tests. The test file count estimate is raised to ~18 to reflect
the broader surface.

### `bridge/runtime.py` (558 stmts, 230 branches)

**Only ONE public function in the entire file:**

| Name | Line | Visibility |
|---|---|---|
| `get_bridge_db` | 42 | **public** (returns `sqlite3.Connection`) |
| Everything else (`_normalize_json`, `_loads_json`, `_parse_iso`, `_peer_collaboration_message`, `_is_absolute_path`, `_normalize_artifact_refs`, `_normalize_action_items`, `_canonical_thread_id`, `_thread_id_for`, `_infer_message_kind`, `_validate_message_contract`, `_validate_thread_correlation`, `_thread_participants`, `_derive_thread_state`, `_thread_items`, `_row_to_dict`, `_recipient_matches`, `_thread_correlation_id`, `_message_is_protocol_ack`, `_notification_targets`, `_queue_notification`, `_insert_message`, `_ensure_schema`) | various | **private** |

**Testing `runtime.py` is the hard case.** There is no public sender API. The private functions are exercised in production by `bridge/__init__.py` importing them (module-level side effects) and by `run_handshake()` in `handshake.py` which calls internal runtime helpers.

**Approach for runtime.py testing (requires explicit GOV-10 exceptions):**

Three of runtime.py's private helpers are *the module's internal public contract* used by sibling bridge modules, not truly private-to-function. They deserve GOV-10 exceptions as "module-internal public API tested directly":

| Private helper | Called by | Justification for direct test |
|---|---|---|
| `_insert_message` | `_queue_notification`, `run_handshake` | Core persistence primitive; all bridge writes flow through it; test via temp DB |
| `_loads_json` | `_thread_items`, `_derive_thread_state`, test only path in runtime | Type-narrowing helper fixed in 4B.7 Pattern E; worth a direct regression test for the narrowing behavior |
| `_validate_message_contract` | `_insert_message` | Message schema guard; directly testable with dict fixtures |

Other runtime `_*` functions are exercised **only** via `get_bridge_db()` or `run_handshake()` → `_insert_message()` chain. Coverage will be accumulated through those public callers.

---

## Corrected Coverage Arithmetic (JSON-based, per-file)

Extracted via:

```bash
python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=json:/tmp/cov.json -q
python -c "
import json
d = json.load(open('/tmp/cov.json'))
for fp, data in sorted(d['files'].items()):
    s = data['summary']
    print(f'{fp} stmts={s[\"num_statements\"]} covered={s[\"covered_lines\"]} br={s[\"num_branches\"]} brcov={s[\"covered_branches\"]}')
"
```

### Per-file current state

| File | Stmts | StmtCov | Stmt% | Branches | BrCov | Br% | Combined% |
|---|---|---|---|---|---|---|---|
| `bridge/__init__.py` | 5 | 0 | 0.0% | 0 | 0 | n/a | 0% |
| `bridge/context.py` | 471 | 0 | 0.0% | 238 | 0 | 0.0% | 0% |
| `bridge/handshake.py` | 97 | 0 | 0.0% | 40 | 0 | 0.0% | 0% |
| `bridge/launcher.py` | 152 | 0 | 0.0% | 44 | 0 | 0.0% | 0% |
| `bridge/poller.py` | 335 | 0 | 0.0% | 96 | 0 | 0.0% | 0% |
| `bridge/runtime.py` | 558 | 0 | 0.0% | 230 | 0 | 0.0% | 0% |
| `bridge/worker.py` | 421 | 0 | 0.0% | 142 | 0 | 0.0% | 0% |
| `project/upgrade.py` | 104 | 21 | 20.2% | 46 | 0 | 0.0% | 14.00% |
| `project/doctor.py` | 258 | 150 | 58.1% | 84 | 35 | 41.7% | 54.09% |
| `project/scaffold.py` | 182 | 135 | 74.2% | 72 | 43 | 59.7% | 70.08% |
| `project/manifest.py` | 51 | 40 | 78.4% | 20 | 10 | 50.0% | 70.42% |

### Per-file targets (statement-only, branches tracked separately)

Targets are expressed as **integer counts** (not percentages) to avoid the
mixed-metric trap of `-003`. For each file, the "target stmt cov" is the
number of statements that must be covered after 4B.8 lands; the delta is
target minus current.

| File | Current stmts covered | Target stmts covered | Stmt Δ | Current br covered | Target br covered | Br Δ |
|---|---|---|---|---|---|---|
| `bridge/__init__.py` | 0 | 5 | +5 | 0 | 0 | 0 |
| `bridge/context.py` | 0 | 330 (70%) | **+330** | 0 | 140 (59%) | **+140** |
| `bridge/handshake.py` | 0 | 60 (62%) | **+60** | 0 | 22 (55%) | **+22** |
| `bridge/launcher.py` | 0 | 80 (53%) | **+80** | 0 | 20 (45%) | **+20** |
| `bridge/poller.py` | 0 | 200 (60%) | **+200** | 0 | 50 (52%) | **+50** |
| `bridge/runtime.py` | 0 | 330 (59%) | **+330** | 0 | 120 (52%) | **+120** |
| `bridge/worker.py` | 0 | 230 (55%) | **+230** | 0 | 70 (49%) | **+70** |
| `project/upgrade.py` | 21 | 65 (63%) | **+44** | 0 | 25 (54%) | **+25** |
| `project/doctor.py` | 150 | 190 (74%) | **+40** | 35 | 55 (65%) | **+20** |
| `project/scaffold.py` | 135 | 140 (77%) | **+5** | 43 | 55 (76%) | **+12** |
| `project/manifest.py` | 40 | 45 (88%) | **+5** | 10 | 13 (65%) | **+3** |
| **TOTAL Δ** | | | **+1,329 stmts** | | | **+482 branches** |

### Projected global metrics

- **Statements:** `3600 + 1329 = 4929 / 6621 = 74.4%` (target ≥70%, margin **+4.4pp**)
- **Branches:** `1126 + 482 = 1608 / 2420 = 66.4%` (target ≥55%, margin **+11.4pp**)
- **Combined:** `(4929 + 1608) / 9041 = 6537 / 9041 = 72.3%` (target ≥70%, margin **+2.3pp**)

All three targets met with meaningful buffers. Unlike `-003`'s 0.3pp combined margin, `-005` has **2.3pp on combined + 4.4pp on statements + 11.4pp on branches**.

---

## Objective

Drive all three coverage metrics above Phase 4B plan targets simultaneously:

- `percent_covered` (combined) ≥ **70.0%** — CI gate via `--cov-fail-under=70`
- `percent_statements_covered` ≥ **70.0%** — hard exit criterion (Phase 4B plan "70% line")
- `percent_branches_covered` ≥ **55.0%** — hard exit criterion (Phase 4B plan "55% branch")

Zero runtime behavior change. Pure test addition (plus one CI workflow line).

---

## Scope — Test Additions

### Import isolation requirement (addresses `-004` Finding 3)

**Every bridge test module MUST NOT import any `groundtruth_kb.bridge.*` at module level.**

The correct pattern for each bridge test file:

```python
"""tests/test_bridge_<module>.py

This module deliberately avoids top-level imports of groundtruth_kb.bridge.*
because bridge/__init__.py imports bridge.runtime, which reads PRIME_BRIDGE_DB
and creates DB_PATH.parent at module-load time. Importing before PRIME_BRIDGE_DB
is redirected would pollute ~/.claude/prime-bridge.
"""

import importlib
import os
import sys
from pathlib import Path

import pytest


@pytest.fixture
def isolated_bridge(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Purge any cached bridge modules and redirect PRIME_BRIDGE_DB to tmp_path.

    Returns a module-import helper:
        bridge_handshake = isolated_bridge("groundtruth_kb.bridge.handshake")
    Use this inside each test instead of top-level imports.
    """
    # Purge cached bridge modules so next import picks up the redirected env
    to_purge = [k for k in sys.modules if k.startswith("groundtruth_kb.bridge")]
    for k in to_purge:
        del sys.modules[k]

    bridge_db = tmp_path / "bridge.db"
    monkeypatch.setenv("PRIME_BRIDGE_DB", str(bridge_db))

    def _import(name: str):
        return importlib.import_module(name)

    yield _import

    # Post-test purge so subsequent tests in other files re-import cleanly
    to_purge = [k for k in sys.modules if k.startswith("groundtruth_kb.bridge")]
    for k in to_purge:
        del sys.modules[k]
```

Test functions then call `bridge_handshake = isolated_bridge("groundtruth_kb.bridge.handshake")` instead of `from groundtruth_kb.bridge import handshake` at the top of the file.

This guarantees:
- No top-level `groundtruth_kb.bridge.*` imports (enforced by `ruff` E402 / `isort` conventions + a ban comment at the top of every test file)
- `PRIME_BRIDGE_DB` is set before ANY bridge module loads
- The cache-purge ensures fixture state doesn't leak between tests in different modules
- Base CI `.[dev,web]` install is sufficient; MCP absence is handled by `runtime.py`'s existing `_HAS_MCP = False` path

### Pattern A — Bridge smoke tests

**Naming convention:** flat files `tests/test_bridge_<module>.py` (Codex `-002` Answer 1).

**GOV-10 compliance:** Tests exercise public functions where available. Explicit GOV-10 exceptions are granted for three private helpers, each justified:

| Private helper | File | Justification |
|---|---|---|
| `_FileLock` | `poller.py`, `worker.py` | Documented internal locking primitive; no public equivalent; `-001` precedent |
| `_insert_message` | `runtime.py` | Core persistence primitive; all bridge writes flow through it; `runtime.py` has no public sender API |
| `_loads_json` | `runtime.py` | Type-narrowing helper from 4B.7 Pattern E; direct regression test locks the narrowing behavior |
| `_validate_message_contract` | `runtime.py` | Message schema guard; directly testable with dict fixtures |

All other private helpers (`_handle_notification_batch`, `_handle_inbox`, `_load_state`, `_save_state`, `_check_*`, etc.) are exercised via public callers (`run()`, `run_doctor()`, etc.) and are NOT tested directly.

**Test files (estimated counts are LOWER bounds; add more as needed to hit per-file targets):**

| Test file | Public entry points | GOV-10 exceptions | Expected tests |
|---|---|---|---|
| `tests/test_bridge_handshake.py` | `run_handshake()`, `main()` | None | 10 |
| `tests/test_bridge_context.py` | `dedupe_preserve_order`, `prioritize_inbox_items`, `agent_peer`, `agent_display`, `message_is_session_start_request`, `message_is_closure_only`, `iter_text_fragments`, `clean_path_candidate`, `resolve_artifact_name`, `discover_artifacts`, `summarize_context`, `build_prompt`, `build_context_snapshot`, `select_dispatch_batch`, `build_contexts`, `context_requires_action` (all 16 public module-level functions) | None | 30 |
| `tests/test_bridge_launcher.py` | `build_parser`, `main` (subprocess + scheduled-task mocked) | None | 12 |
| `tests/test_bridge_poller.py` | `run()`, `build_parser()`, `main()`, `_NotificationBatchSummary` + `_InboxSummary` TypedDict shape verification | `_FileLock` | 18 |
| `tests/test_bridge_worker.py` | `resident_worker_is_healthy()`, `resident_worker_health_snapshot()`, `run()`, `build_parser()`, `main()` | `_FileLock` | 18 |
| `tests/test_bridge_runtime.py` | `get_bridge_db()`, then test via exception-list private helpers | `_insert_message`, `_loads_json`, `_validate_message_contract` | 22 |
| **Total Pattern A** | | | **~110** |

### Pattern B — `project/upgrade.py` tests

Add `tests/test_upgrade.py`. Public entry points to locate via grep before writing (not assuming names exist):

```bash
grep -nE "^def |^class " src/groundtruth_kb/project/upgrade.py
```

Test plan: exercise public upgrade functions with synthetic v0.x → v0.y fixtures; dry-run; invalid version error paths; missing target error paths.

**Target delta:** +44 stmts, +25 branches (69 combined items).

**Expected tests:** ~14.

### Pattern C — `project/doctor.py` additional tests

Extend existing `tests/test_doctor.py` (if it exists) or add new `tests/test_doctor_extended.py`. Exercise `run_doctor()` / equivalent public entry with synthetic KB fixtures that force each private `_check_*` helper to run via data shape.

**Target delta:** +40 stmts, +20 branches (60 combined items).

**Expected tests:** ~12.

### Pattern D — `project/scaffold.py` edge-case tests

Extend existing scaffold tests:
- Idempotent re-run
- Conflict with existing file
- All optional flags enabled

**Target delta:** +5 stmts, +12 branches (17 combined items).

**Expected tests:** ~4.

### Pattern E — `project/manifest.py` (new, small)

Add 2 tests covering the 5-stmt + 3-branch gap (error paths). Keeps manifest coverage trending upward and costs almost nothing.

**Target delta:** +5 stmts, +3 branches (8 combined items).

**Expected tests:** ~2.

### Pattern grand totals

| Pattern | Stmts Δ | Branches Δ | Combined Δ | Tests |
|---|---|---|---|---|
| A (bridge smoke tests) | +1,235 | +422 | +1,657 | ~110 |
| B (upgrade.py) | +44 | +25 | +69 | ~14 |
| C (doctor.py) | +40 | +20 | +60 | ~12 |
| D (scaffold.py) | +5 | +12 | +17 | ~4 |
| E (manifest.py) | +5 | +3 | +8 | ~2 |
| **TOTAL** | **+1,329** | **+482** | **+1,811** | **~142** |

Projected global: **74.4% stmts / 66.4% branches / 72.3% combined** — all above target.

---

## Out of Scope (Explicitly)

- Phase 4B.9 whole-package docstring coverage
- Phase 4C structured logging migration
- Phase 4D broad-exception review
- `bridge` extra in base CI (MCP-path tests must pass with `.[dev,web]` alone)
- Runtime behavior change — all edits are test-only (plus one CI workflow line)
- Runtime API reshape (introducing `KnowledgeDBBridge` class etc.) — the scope is PURE coverage of the existing API, not refactoring

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| `PRIME_BRIDGE_DB` module-level side effect pollutes `~/.claude` | High | `isolated_bridge` fixture purges `sys.modules` before setenv; test files BANNED from top-level bridge imports by a comment + ruff E402 enforcement |
| MCP-absent path breaks bridge tests | Medium | All tests must pass with `_HAS_MCP = False`; no tests rely on live FastMCP; any MCP-specific test marked `pytest.mark.skipif(not _HAS_MCP)` |
| Runtime private helpers hard to exercise | High | Only three private helpers granted GOV-10 exception; rest exercised through public callers with controlled inputs. If coverage falls short, EXPAND public-caller tests before adding more GOV-10 exceptions. |
| Combined 70% gate misses by ≤2pp | Low | Projection has +2.3pp margin on combined, +4.4pp on stmts, +11.4pp on branches |
| Projection error from test approximation | Medium | Each file's target is stated as an integer count; actual measurement after Pattern A will confirm whether Pattern B/C/D/E is needed, or whether Pattern A needs expansion |
| New tests reveal pre-existing bugs in bridge code | Medium | Stop and file a separate bridge entry; do not fix bugs under 4B.8 |
| `_FileLock` test race under parallel pytest | Low | Unique `tmp_path` per test |
| Grep didn't show an importable class/entry I should use | Low | If implementation finds a better API surface than the grep revealed, adjust the test file accordingly — the proposal's API list is a floor, not a ceiling |

---

## Test Plan

1. **Per-test-file:** after each new file, run:
   ```bash
   python -m pytest tests/test_bridge_<module>.py -v --tb=short
   python -m pytest --cov=groundtruth_kb.bridge.<module> --cov-branch --cov-report=term -q
   ```
   Verify: all new tests pass; per-file statement and branch counts reach the §Per-file targets table.

2. **Pattern A cumulative check** (after all 6 bridge smoke-test files land):
   ```bash
   python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=json:/tmp/cov.json -q
   python -c "
   import json
   d = json.load(open('/tmp/cov.json'))['totals']
   print(f'stmts={d[\"percent_covered_display\"]}%')
   print(f'branches={100*d[\"covered_branches\"]/d[\"num_branches\"]:.2f}%')
   print(f'combined={d[\"percent_covered\"]:.2f}%')
   "
   ```
   Assert: combined ≥65%, stmts ≥68%, branches ≥58%. (Intermediate — Pattern B/C/D/E still pending.)

3. **Adaptive checkpoint:** if Pattern A fell short of its projection, EXPAND bridge tests before proceeding to Pattern B/C/D/E. Do NOT add the CI gate until all three global targets are met.

4. **Full pattern cumulative check:**
   ```bash
   python -m pytest --cov=groundtruth_kb --cov-branch --cov-report=json:/tmp/cov.json -q
   ```
   Assert: all three metrics above target (`≥70% stmts`, `≥55% br`, `≥70% combined`).

5. **Full regression:**
   ```bash
   python -m pytest -q
   ```
   Assert: 640 + ~142 ≈ 782 passed, 0 failed.

6. **mypy --strict regression guard** (from 4B.7):
   ```bash
   python -m mypy --strict src/groundtruth_kb/
   ```
   Assert: `Success: no issues found in 31 source files`.

7. **Ruff:**
   ```bash
   python -m ruff check .
   python -m ruff format --check .
   ```
   Assert: both clean. Also verify no E402 violations (module-level imports after code) in new test files — this is how the top-level-bridge-import ban is mechanically enforced.

8. **CI workflow update:**
   Add `--cov-fail-under=70` to the pytest command in `.github/workflows/ci.yml`
   between lines 72–75 (the existing `--cov-branch` invocation). Per-file gates
   on lines 76–79 remain unchanged: `db.py 68`, `cli.py 72`, `config.py 92`,
   `gates.py 92`.

---

## Exit Criteria (all must be true)

1. `python -m coverage json` → `percent_covered` (combined) ≥ **70.0%**
2. `python -m coverage json` → `percent_statements_covered` ≥ **70.0%** ← **NEW in `-005`**
3. `python -m coverage json` → `percent_branches_covered` ≥ **55.0%**
4. `python -m pytest -q` → 640 + ~142 ≈ 782 passed, 0 failed
5. `python -m mypy --strict src/groundtruth_kb/` → Success, 0 errors
6. `python -m ruff check .` and `python -m ruff format --check .` both clean
7. `.github/workflows/ci.yml` gains `--cov-fail-under=70` on the main pytest invocation; per-file gates from 4B.6 unchanged (`db.py 68`, `cli.py 72`, `config.py 92`, `gates.py 92`)
8. No existing test deleted or skipped; no behavior change in `src/`
9. Bridge submodule reaches ≥55% statement coverage across all 6 non-trivial files
10. `project/upgrade.py` reaches ≥60% statement coverage
11. CHANGELOG entry under `[Unreleased]` → `### Added` (new tests) + `### Changed` (CI gate)
12. No top-level `groundtruth_kb.bridge.*` imports in any new test file (enforced by `isolated_bridge` fixture pattern + ruff E402)
13. Every GOV-10 private-helper exception is listed in the Pattern A table (4 total: `_FileLock` × 2 files, `_insert_message`, `_loads_json`, `_validate_message_contract`)

---

## Rollback

Single squash-merged PR. `git revert <merge-sha>` on main. Zero blast radius (test-only, no src/ behavior change).

---

## Change Methodology Commitment

Per the 4B.7 lesson AND the `-003` failure: **no API name or coverage number in this proposal is unsourced.**

- Every API name in the Bridge API Inventory came from `grep -nE "^class |^def |^__all__"` against the source at `ff6988b`
- Every coverage number in the Per-file targets table came from `coverage json` against the same baseline
- Every target integer is achievable given the file's total statement/branch count
- The projection arithmetic uses matched-denominator sums, not mixed percentages

If implementation reveals that any API name in this document is wrong (e.g., the grep missed a `@classmethod`), STOP and file a correction as a `-006` revision before continuing. Do not silently substitute a different name.

---

## Appendix A — Source Grep Evidence

Raw output from the grep command, verbatim:

```
=== bridge/handshake.py ===
32:def _extract_prime_reply(thread_payload: dict[str, Any]) -> dict[str, Any] | None:
53:def _find_existing_pending_thread() -> str | None:
74:def _format_success(thread_id: str, reply: dict[str, Any]) -> dict[str, Any]:
87:def _format_timeout(thread_id: str, timeout_seconds: int) -> dict[str, Any]:
99:def run_handshake(
188:def main() -> int:

=== bridge/context.py ===
27:def _now() -> datetime:
31:def _parse_iso(value: str | None) -> datetime | None:
43:def agent_peer(agent: str) -> str:
47:def agent_display(agent: str) -> str:
51:def dedupe_preserve_order(values: list[str]) -> list[str]:
62:def _message_tags(message: dict[str, Any]) -> set[str]:
69:def message_is_session_start_request(message: dict[str, Any]) -> bool:
75:def message_is_closure_only(message: dict[str, Any]) -> bool:
95:def prioritize_inbox_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
117:def iter_text_fragments(value: Any) -> list[str]:
135:def clean_path_candidate(raw: str) -> str:
139:def resolve_artifact_name(name: str, *, project_dir: Path) -> Path | None:
214:def discover_artifacts(context: dict[str, Any], *, project_dir: Path) -> list[dict[str, str]]:
314:def summarize_context(agent: str, context: dict[str, Any]) -> str:
335:def build_prompt(
376:def build_context_snapshot(
390:def select_dispatch_batch(
446:def build_contexts(
529:def context_requires_action(agent: str, context: dict[str, Any]) -> bool:

=== bridge/launcher.py ===
225:def build_parser() -> argparse.ArgumentParser:
279:def main() -> int:

=== bridge/poller.py ===
37:class _NotificationBatchSummary(TypedDict):
42:class _InboxSummary(TypedDict):
65:class _FileLock:
396:def run(args: argparse.Namespace, project_dir: Path | None = None) -> int:
607:def build_parser() -> argparse.ArgumentParser:
631:def main() -> int:

=== bridge/worker.py ===
137:class _FileLock:
317:def resident_worker_is_healthy(
358:def resident_worker_health_snapshot(
565:def run(args: argparse.Namespace, project_dir: Path | None = None) -> int:
803:def build_parser() -> argparse.ArgumentParser:
819:def main() -> int:

Note: S295 original grep used `head -25` which truncated before reaching
`run()`, `build_parser()`, and `main()`. The above shows the full public
inventory.

=== bridge/runtime.py ===
42:def get_bridge_db() -> sqlite3.Connection:
```

Private helpers omitted from each file's grep output for brevity; all `_*` functions below the public entries are exercised via the public callers listed in the Pattern A test table.
