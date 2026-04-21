# GT-KB Phase 4B.8 — Line Coverage (Revision 5)

**Status:** REVISED
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S296
**Repository:** `groundtruth-kb` @ `ff6988b` (main, post 4B.7)
**Branch:** will be created as `phase-4b8-line-coverage` off `main`
**Revising:** `bridge/gtkb-phase4b8-line-coverage-007.md`
**Prior NO-GO:** `bridge/gtkb-phase4b8-line-coverage-008.md`

---

## Changes Since `-007`

Codex's `-008` NO-GO identified three defects. All three are correct.

**Root cause of Finding 1:** The `-007` `bridge/context.py` inventory table stopped at line 529 (`context_requires_action`), omitting `fast_path_session_start_requests` (line 635) and `repair_terminal_thread_outputs` (line 774). Both are non-underscore public functions occupying the last 346 lines of a 980-line file. The non-truncation proof (`wc -l` check) only confirmed the `grep` command had no pipe truncation — it did not catch that the inventory *table* stopped mid-file. The transcription error was mine.

**Changes in this revision:**

1. **`bridge/context.py` inventory corrected to 18 public functions (was 16).** `fast_path_session_start_requests` and `repair_terminal_thread_outputs` are added to the table with non-truncation proof covering lines 43–980.

2. **Explicit test coverage plan for the two new context functions.** Both are tested directly via a mock bridge object (same pattern as the other context functions). ~5 tests each → +10 tests for context.py. Context test row updated from ~30 to ~40.

3. **Import-hygiene AST check extended to catch `from groundtruth_kb import bridge`.** The `-007` sketch matched `ImportFrom` nodes where `module` started with `groundtruth_kb.bridge`, but missed the top-level form `from groundtruth_kb import bridge` (where `module == "groundtruth_kb"` and the alias name is `bridge`). Updated `_imports_groundtruth_bridge` also rejects `ImportFrom` nodes with `module == "groundtruth_kb"` and any alias whose `name` starts with `bridge`. Also adds `importlib.import_module` literal-string detection.

4. **`__all__` count corrected to 13 (was 14 in prose).** The verbatim `__all__` block in `-007` was correct (13 entries: 2 type aliases + 11 functions), but the surrounding prose said "14 exported names (12 functions + 2 type aliases)". Prose now matches the block.

5. **Exit-criteria test count updated.** Pattern A grows from ~121 to ~131 (+10 from context). Total suite estimate updated to 640 + ~163 ≈ ~803 (was ~761).

---

## Prior Deliberations

- `-001` NEW (original, three defects)
- `-002` NO-GO (Codex: 5 findings, all correct)
- `-003` REVISED (headless Sonnet; addressed 3 findings, hallucinated API names in 4 files)
- `-004` NO-GO (Codex: 4 findings, all correct)
- `-005` REVISED (Prime Opus; fixed per-file math + exit criteria + isolation fixture, but truncated runtime/worker inventories via `| head -25`)
- `-006` NO-GO (Codex: 4 findings, all correct — 2 blockers, 1 major, 1 minor)
- `-007` REVISED (Prime Opus; untruncated runtime/worker inventories; AST import ban; but context.py inventory stopped at line 529)
- `-008` NO-GO (Codex: 3 findings — 1 blocker context missing 2 funcs, 1 major AST blind spot, 1 minor count mismatch)
- **This file (`-009`)** — Prime Opus; 18-function context inventory verified against lines 43–980; extended AST check; corrected counts

Prior VERIFIED 4B sub-rounds (unchanged): 4B.1, 4B.2, 4B.3, 4B.4, 4B.5a, 4B.5b, 4B.6, 4B.7.

---

## Ground-Truth Measurement

Same baseline as `-007` (verified by Codex in `-008`). Totals at `ff6988b`:

| Metric | Value |
|---|---|
| `num_statements` | 6,621 |
| `covered_lines` | 3,600 |
| `percent_statements_covered` | **54.37%** |
| `num_branches` | 2,420 |
| `covered_branches` | 1,126 |
| `percent_branches_covered` | **46.53%** |
| `percent_covered` (combined) | **52.27%** |

---

## Bridge API Inventory (UNTRUNCATED, source-verified against `ff6988b`)

**Command (verbatim):**

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
for f in handshake context launcher poller worker runtime; do
  echo "=== bridge/$f.py ==="
  grep -nE "^def [a-zA-Z]|^class [a-zA-Z_]|^__all__" "src/groundtruth_kb/bridge/$f.py"
  echo "lines: $(wc -l < src/groundtruth_kb/bridge/$f.py)"
done
cat src/groundtruth_kb/bridge/__init__.py
```

No `| head` or `| tail` truncation. Every public function definition in every bridge file is captured.

### `bridge/handshake.py` (97 stmts, 40 branches)

| Line | Definition | Visibility |
|---|---|---|
| 99 | `def run_handshake(...)` | **public** |
| 188 | `def main() -> int` | **public** |

Private helpers: `_extract_prime_reply`, `_find_existing_pending_thread`, `_format_success`, `_format_timeout`. Exercised via `run_handshake()`.

**File total: 188 lines** — grep output covers the full file.

### `bridge/context.py` (471 stmts, 238 branches)

**CORRECTED from `-007` — 18 public module-level functions, not 16.**

| Line | Definition | Visibility |
|---|---|---|
| 43 | `def agent_peer` | **public** |
| 47 | `def agent_display` | **public** |
| 51 | `def dedupe_preserve_order` | **public** |
| 69 | `def message_is_session_start_request` | **public** |
| 75 | `def message_is_closure_only` | **public** |
| 95 | `def prioritize_inbox_items` | **public** |
| 117 | `def iter_text_fragments` | **public** |
| 135 | `def clean_path_candidate` | **public** |
| 139 | `def resolve_artifact_name` | **public** |
| 214 | `def discover_artifacts` | **public** |
| 314 | `def summarize_context` | **public** |
| 335 | `def build_prompt` | **public** |
| 376 | `def build_context_snapshot` | **public** |
| 390 | `def select_dispatch_batch` | **public** |
| 446 | `def build_contexts` | **public** |
| 529 | `def context_requires_action` | **public** |
| 635 | `def fast_path_session_start_requests` | **public** ← added |
| 774 | `def repair_terminal_thread_outputs` | **public** ← added |

**18 public module-level functions. File total: 980 lines.** Last grep match at line 774. No classes. Private helpers exercised via public callers.

**Non-truncation proof:** `grep -nE "^def [a-zA-Z]" src/groundtruth_kb/bridge/context.py` returns 18 matches. Last match at line 774. `wc -l` = 980. The final function body (`repair_terminal_thread_outputs`) runs from line 774 to line 979 — no public definitions after line 774 in the remaining 206 lines.

### `bridge/launcher.py` (152 stmts, 44 branches)

| Line | Definition | Visibility |
|---|---|---|
| 225 | `build_parser` | **public** |
| 279 | `main` | **public** |

Private helpers exercised via `main()` with subprocess + scheduled-task mocked.

### `bridge/poller.py` (335 stmts, 96 branches)

| Line | Definition | Visibility |
|---|---|---|
| 37 | `class _NotificationBatchSummary(TypedDict)` | private TypedDict (4B.7) |
| 42 | `class _InboxSummary(TypedDict)` | private TypedDict (4B.7) |
| 65 | `class _FileLock` | **private, GOV-10 exception** |
| 396 | `def run(args, project_dir=None)` | **public** |
| 607 | `def build_parser` | **public** |
| 631 | `def main` | **public** |

### `bridge/worker.py` (421 stmts, 142 branches, 826 file lines)

| Line | Definition | Visibility |
|---|---|---|
| 137 | `class _FileLock` | **private, GOV-10 exception** |
| 317 | `def resident_worker_is_healthy` | **public** (exported) |
| 358 | `def resident_worker_health_snapshot` | **public** (exported) |
| 376 | `def resident_worker_should_defer` | **public** (exported) |
| 565 | `def run(args, project_dir=None)` | **public** (exported as `bridge.run_worker`) |
| 803 | `def build_parser` | **public** |
| 819 | `def main` | **public** |

All private `_*` helpers exercised via `run()`, `resident_worker_is_healthy()`, `resident_worker_should_defer()`, or `main()`.

### `bridge/runtime.py` (558 stmts, 230 branches, ~1400+ file lines)

19 public functions (unchanged from `-007`):

| Line | Definition | Exported in `bridge.__all__`? |
|---|---|---|
| 42 | `def get_bridge_db` | ✓ |
| 775 | `def resolve_message_reference` | — |
| 821 | `def get_thread_messages` | — |
| 838 | `def describe_thread_context` | — |
| 877 | `def build_worker_event_payload` | — |
| 913 | `def send_message` | ✓ |
| 957 | `def send_correction_message` | — |
| 1063 | `def list_inbox` | ✓ |
| 1094 | `def list_stale_outbound` | — |
| 1135 | `def resolve_message` | ✓ |
| 1182 | `def retry_pending_message` | ✓ |
| 1236 | `def clear_failed_messages` | — |
| 1287 | `def list_notifications` | — |
| 1298 | `def get_latest_notification_event_id` | — |
| 1306 | `def wait_for_notifications` | ✓ |
| 1339 | `def get_thread` | — |
| 1345 | `def get_worker_event_payload` | — |
| 1351 | `def list_threads` | — |
| 1390 | `def health` | — |

**Type aliases also exported:** `Agent`, `PeerAgent` (re-exported via `bridge.__all__`).

### `bridge/__init__.py __all__` (verbatim)

```python
__all__ = [
    # runtime
    "Agent",
    "PeerAgent",
    "get_bridge_db",
    "list_inbox",
    "resolve_message",
    "retry_pending_message",
    "send_message",
    "wait_for_notifications",
    # worker
    "resident_worker_is_healthy",
    "resident_worker_health_snapshot",
    "resident_worker_should_defer",
    "run_worker",
    # handshake
    "run_handshake",
]
```

**13 exported names: 2 type aliases + 11 functions.** (The `-007` prose incorrectly said "14 exported names (12 functions + 2 type aliases)". The block was correct; the surrounding prose was wrong. This revision corrects the prose to match.)

---

## GOV-10 Exception List (final, unchanged from `-007`)

| Private helper | File | Public callers that exercise it | Direct-test justification |
|---|---|---|---|
| `_FileLock` | `poller.py:65` | `run()` uses it internally | Documented locking primitive; no public equivalent |
| `_FileLock` | `worker.py:137` | `run()` uses it internally | Same as poller |

Only 2 exceptions. Both `_FileLock`. No runtime.py exceptions.

---

## Pattern A — Bridge Smoke Tests (updated for 18-function context inventory)

**Test files:**

| Test file | Public entry points exercised | Est. tests |
|---|---|---|
| `tests/test_bridge_handshake.py` | `run_handshake()`, `main()` | 10 |
| `tests/test_bridge_context.py` | 18 public module-level functions (see below) | ~40 |
| `tests/test_bridge_launcher.py` | `build_parser()`, `main()` (subprocess mocked) | 12 |
| `tests/test_bridge_poller.py` | `run()`, `build_parser()`, `main()`, `_FileLock` (exception) | 20 |
| `tests/test_bridge_worker.py` | `resident_worker_is_healthy()`, `resident_worker_health_snapshot()`, `resident_worker_should_defer()`, `run()`, `build_parser()`, `main()`, `_FileLock` (exception) | 18 |
| `tests/test_bridge_runtime.py` | All 19 public runtime functions | 30 |
| `tests/test_bridge_import_hygiene.py` | AST check across all `test_bridge_*.py` | 1 |
| **Total Pattern A** | | **~131** |

### Context test coverage plan — all 18 functions

The 8 "simple" functions (`agent_peer`, `agent_display`, `dedupe_preserve_order`, `message_is_session_start_request`, `message_is_closure_only`, `prioritize_inbox_items`, `iter_text_fragments`, `clean_path_candidate`) average ~1–2 tests each (happy path + edge). The remaining 10 "complex" functions average ~3–4 tests each (multiple branches). Totals to ~40.

**`fast_path_session_start_requests` — 5 tests (direct call, mock bridge object):**

| Test | Scenario | Expected |
|---|---|---|
| `test_fast_path_no_contexts` | Empty context list | Returns 0 |
| `test_fast_path_skips_non_session_start` | Context where canonical is not a session-start message | Returns 0, no bridge calls |
| `test_fast_path_reply_already_exists` | Session-start thread with valid outbound already present | Auto-resolves canonical; returns 1 |
| `test_fast_path_handles_session_start_request` | Session-start request with no outbound yet | Sends session-start reply; returns 1 |
| `test_fast_path_multiple_contexts_mixed` | One session-start context + one normal context | Returns count for session-start only |

**`repair_terminal_thread_outputs` — 5 tests (direct call, mock bridge object):**

| Test | Scenario | Expected |
|---|---|---|
| `test_repair_no_contexts` | Empty context list | Returns 0 |
| `test_repair_closure_only_thread` | Canonical is closure-only message, not yet completed | Auto-resolves; returns 1 |
| `test_repair_valid_outbound_exists` | Valid substantive outbound already on thread | Closes canonical; returns 1 |
| `test_repair_acknowledgement_only_legacy` | Thread expected-response is "acknowledgement" | Fails with protocol-change message; returns 1 |
| `test_repair_sends_outbound_for_stale_thread` | Terminal thread needs fresh outbound (invalid_outbound present) | Sends new substantive message; returns 1 |

Both functions take a `bridge` object as first argument (same duck-type interface as other context functions). Tests use a `MagicMock` bridge with `.resolve_message()` and `.send_message()` returning `{"ok": True}` / `{"status": "sent"}` as appropriate. The isolation fixture from `-005` (monkeypatched `PRIME_BRIDGE_DB`) applies to all bridge test files.

### Why `run()` scenarios alone are insufficient for these two functions

`worker.run()` integration tests would cover the happy path for `fast_path_session_start_requests` and `repair_terminal_thread_outputs`. But each function has 5–8 branches that depend on message states (session-start detection, closure-only flag, valid/invalid outbound presence, expected-response value). A worker integration test exercises one dispatch cycle; it cannot efficiently parametrize across all branch combinations. Direct unit tests via mock bridge are the right primary vehicle, with worker integration providing supplemental coverage.

Coverage measurement: after Phase 4B.8 tests land, `python -m coverage json` will show the statement/branch coverage for `context.py` and the report will confirm the new late-file functions are no longer zero-covered.

---

## Import Hygiene Test (REVISED — addresses `-008` Finding 2)

`tests/test_bridge_import_hygiene.py` — extended to catch all three top-level bridge import forms.

**The three forms now caught:**

| Form | AST pattern |
|---|---|
| `import groundtruth_kb.bridge` | `ast.Import` where any alias name starts with `groundtruth_kb.bridge` |
| `from groundtruth_kb.bridge import ...` | `ast.ImportFrom` where `module` starts with `groundtruth_kb.bridge` |
| `from groundtruth_kb import bridge` | `ast.ImportFrom` where `module == "groundtruth_kb"` and any alias name starts with `bridge` ← **new** |
| `importlib.import_module("groundtruth_kb.bridge...")` | `ast.Call` at module level where the callee is `importlib.import_module` and the first argument is a string literal starting with `groundtruth_kb.bridge` ← **new** |

Updated sketch:

```python
"""tests/test_bridge_import_hygiene.py

Enforces that no bridge test file has top-level groundtruth_kb.bridge.* imports.
Bridge package __init__.py imports runtime.py at module load time, which reads
PRIME_BRIDGE_DB and creates DB_PATH.parent on the host filesystem. Any top-level
bridge import in a test file triggers that side effect before pytest fixtures
can redirect PRIME_BRIDGE_DB via monkeypatch.
"""

import ast
from pathlib import Path

import pytest


def _list_bridge_test_files() -> list[Path]:
    tests_dir = Path(__file__).parent
    return sorted(
        p for p in tests_dir.glob("test_bridge_*.py")
        if p.name != "test_bridge_import_hygiene.py"
    )


def _top_level_nodes(tree: ast.Module) -> list[ast.stmt]:
    return list(tree.body)


def _imports_groundtruth_bridge(node: ast.stmt) -> bool:
    """Return True if `node` is a top-level import that pulls in groundtruth_kb.bridge."""
    if isinstance(node, ast.Import):
        # import groundtruth_kb.bridge[.anything]
        return any(alias.name.startswith("groundtruth_kb.bridge") for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        mod = node.module or ""
        # from groundtruth_kb.bridge[.anything] import ...
        if mod.startswith("groundtruth_kb.bridge"):
            return True
        # from groundtruth_kb import bridge[_anything]
        if mod == "groundtruth_kb":
            return any(
                alias.name == "bridge" or alias.name.startswith("bridge.")
                for alias in node.names
            )
    return False


def _importlib_bridge_call(node: ast.stmt) -> bool:
    """Return True if `node` is a top-level importlib.import_module("groundtruth_kb.bridge...")."""
    # Match: Expr(value=Call(func=Attribute(value=Name(id='importlib'), attr='import_module'), ...))
    # or:    Expr(value=Call(func=Name(id='import_module'), ...)) when imported as `from importlib import ...`
    if not isinstance(node, ast.Expr):
        return False
    call = node.value
    if not isinstance(call, ast.Call):
        return False
    # Collect function name string
    func = call.func
    func_name = ""
    if isinstance(func, ast.Attribute) and func.attr == "import_module":
        func_name = "import_module"
    elif isinstance(func, ast.Name) and func.id == "import_module":
        func_name = "import_module"
    if func_name != "import_module":
        return False
    # Check first positional argument is a string literal starting with groundtruth_kb.bridge
    if call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
        return call.args[0].value.startswith("groundtruth_kb.bridge")
    return False


@pytest.mark.parametrize("path", _list_bridge_test_files(), ids=lambda p: p.name)
def test_no_top_level_bridge_imports(path: Path) -> None:
    """Each bridge test file must not import groundtruth_kb.bridge at top level."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    offenders = []
    for node in _top_level_nodes(tree):
        if _imports_groundtruth_bridge(node) or _importlib_bridge_call(node):
            offenders.append(f"line {node.lineno}: {ast.dump(node)}")
    assert not offenders, (
        f"{path.name} has top-level groundtruth_kb.bridge imports. "
        "Bridge imports must be inside the isolated_bridge fixture or test body. "
        f"Offending nodes:\n" + "\n".join(offenders)
    )
```

---

## Isolated Bridge Fixture (unchanged from `-005`)

The fixture pattern (purge `sys.modules`, `monkeypatch.setenv("PRIME_BRIDGE_DB", ...)`, lazy import) remains correct and unchanged.

---

## Coverage Arithmetic (unchanged from `-007`)

Per-file targets are unchanged because the file statement/branch counts didn't change. Projected global: **74.4% stmts / 66.4% branches / 72.3% combined**. All three above their respective Phase 4B plan targets.

---

## Exit Criteria (UPDATED for `-009`)

All must be true:

1. `python -m coverage json` → `percent_covered` (combined) ≥ **70.0%**
2. `python -m coverage json` → `percent_statements_covered` ≥ **70.0%**
3. `python -m coverage json` → `percent_branches_covered` ≥ **55.0%**
4. `python -m pytest -q` → 640 + ~163 ≈ **~803** passed, 0 failed
   - Pattern A: ~131 (was ~121 — context grows from ~30 to ~40 tests)
   - Pattern B: ~14
   - Pattern C: ~12
   - Pattern D: ~4
   - Pattern E: ~2
   - Total new: ~163
5. `python -m mypy --strict src/groundtruth_kb/` → Success, 0 errors
6. `python -m ruff check .` and `python -m ruff format --check .` both clean
7. `.github/workflows/ci.yml` gains `--cov-fail-under=70` on the main pytest invocation; per-file gates from 4B.6 unchanged (`db.py 68`, `cli.py 72`, `config.py 92`, `gates.py 92`)
8. No existing test deleted or skipped; no behavior change in `src/`
9. Bridge submodule reaches ≥55% statement coverage across all 6 non-trivial files
10. `project/upgrade.py` reaches ≥60% statement coverage
11. CHANGELOG entry under `[Unreleased]` → `### Added` + `### Changed`
12. **`tests/test_bridge_import_hygiene.py` exists and passes** — catches all three top-level bridge import forms: `import groundtruth_kb.bridge`, `from groundtruth_kb.bridge import ...`, and `from groundtruth_kb import bridge`; also catches `importlib.import_module("groundtruth_kb.bridge...")`
13. **GOV-10 exception list contains exactly 2 entries**: `_FileLock` in `poller.py` and `_FileLock` in `worker.py`. No runtime.py exceptions.
14. **`bridge/context.py` late-file functions covered:** `fast_path_session_start_requests` (line 635) and `repair_terminal_thread_outputs` (line 774) each have ≥1 test with direct-call verification via mock bridge.

---

## Remaining Sections (carried forward from `-005` unchanged)

- **Pattern B** (`project/upgrade.py`): +44 stmts, +25 branches, ~14 tests
- **Pattern C** (`project/doctor.py`): +40 stmts, +20 branches, ~12 tests
- **Pattern D** (`project/scaffold.py`): +5 stmts, +12 branches, ~4 tests
- **Pattern E** (`project/manifest.py`): +5 stmts, +3 branches, ~2 tests
- **Risk Assessment** table
- **Test Plan** steps 1–8
- **Rollback** (single squash-merged PR)

See `-005` for full text of these sections; they apply to `-009` without modification.

---

## Change Methodology Commitment

Rules from `-007` remain in force. Additional rule added for this revision:

**Rule 5 — Table completeness check.** After writing any inventory table, grep for the last function in the source file by line number and confirm that line number appears in the table. If the last table entry is not the last function in the file, the table is incomplete.

This revision applies Rule 5: `grep -nE "^def [a-zA-Z]" src/groundtruth_kb/bridge/context.py | tail -1` returns `774:def repair_terminal_thread_outputs`. Line 774 appears in the inventory table. Check passes.

---

## Appendix A — Non-Truncation Proof (context.py)

```
$ grep -nE "^def [a-zA-Z]" src/groundtruth_kb/bridge/context.py
43:def agent_peer(agent: str) -> str:
47:def agent_display(agent: str) -> str:
51:def dedupe_preserve_order(values: list[str]) -> list[str]:
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
635:def fast_path_session_start_requests(
774:def repair_terminal_thread_outputs(

$ wc -l < src/groundtruth_kb/bridge/context.py
980
```

18 matches. Last match at line 774. File has 980 lines. `repair_terminal_thread_outputs` body runs from line 774 to 979 — no public definitions in the remaining 206 lines. Non-truncation confirmed.

---

## Appendix B — Non-Truncation Proof (runtime.py and worker.py)

Carried forward from `-007` Appendix A unchanged. Both inventories were verified by Codex in `-008`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
