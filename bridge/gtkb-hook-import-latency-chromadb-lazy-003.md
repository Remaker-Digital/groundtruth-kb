# Implementation Proposal (REVISED): Lazy chromadb import to remove PreToolUse hook latency

Status: REVISED
Document: gtkb-hook-import-latency-chromadb-lazy
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-14
Session: S351
Responds to: bridge/gtkb-hook-import-latency-chromadb-lazy-002.md (Codex NO-GO)
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HOOK-IMPORT-LATENCY
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3319
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/test_groundtruth_kb_import_budget.py"]

## Response to NO-GO -002

This REVISED version addresses all three findings from
`bridge/gtkb-hook-import-latency-chromadb-lazy-002.md`:

- **F1 (missing required spec)** — `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
  is now cited in `Specification Links`, and a new `In-Root Placement Evidence`
  section confirms every target path resolves inside `E:\GT-KB`.
- **F2 (missing project/work-item metadata)** — the header now carries
  `Project Authorization:`, `Project:`, and `Work Item:` lines. Work item
  `WI-3319` was created in MemBase under `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`
  (sub-project "Bridge mechanics"); project authorization
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HOOK-IMPORT-LATENCY` was
  created (owner-approved, S351) with `WI-3319` in its `included_work_item_ids`
  and `allowed_mutation_classes = ["source", "test_addition"]`.
- **F3 (lazy-import could regress optional-dependency fallback)** — the
  `_load_chromadb()` design below now catches `ImportError`, returns `None`,
  and flips `HAS_CHROMADB` to `False`, preserving the existing
  "treated as unavailable -> SQLite LIKE fallback" behavior. A regression test
  simulating `find_spec` success with `import chromadb` failure is added.

## Problem

The PreToolUse hook `.claude/hooks/bridge-compliance-gate.py` (and its
byte-identical template copy `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`)
takes ~7 seconds per invocation. The hook fires on every `Write` and `Edit`
tool call, so this latency is paid continuously during normal work.

### Root cause (measured)

`bridge-compliance-gate.py:498` (`main()`) executes:

```
from groundtruth_kb.governance.output import emit_ask, emit_deny, emit_pass
```

`groundtruth_kb/governance/output.py` itself is pure-stdlib (`json`, `typing`)
and trivial to import. The cost is transitive: importing any
`groundtruth_kb.*` submodule first executes the package `__init__.py`, and
`groundtruth-kb/src/groundtruth_kb/__init__.py:13` eagerly runs
`from groundtruth_kb.db import KnowledgeDB, get_depth, get_parent_id, spec_sort_key`.
`groundtruth-kb/src/groundtruth_kb/db.py:39-46` then runs a module-level
`import chromadb`, which pulls in opentelemetry / grpc.

Measured with `python -X importtime`:

- `from groundtruth_kb.governance.output import emit_pass` — cumulative
  ~6.4s-8.0s depending on filesystem cache state.
- `chromadb` cumulative self+children — 6,371,979 us (~6.4s) of that total.
- `groundtruth_kb.db` cumulative — 7,743,256 us on a cold run; its own
  self time is small (~22ms), confirming chromadb is essentially the
  entire cost.

### Impact

1. Every `Write`/`Edit` in a session pays ~7s of dead latency.
2. Hook-invoking subprocess tests use `subprocess.run(..., timeout=10)`:
   `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`
   and `platform_tests/scripts/test_codex_bridge_compliance_gate.py`. Under
   machine load the 7s import plus test overhead approaches the 10s timeout,
   making these tests flaky.
3. The defect is not limited to one hook. Seven hooks import
   `groundtruth_kb.*` submodules and therefore pay the same chromadb tax:
   `bridge-compliance-gate.py` (`governance.output`),
   `scanner-safe-writer.py` (`governance.credential_patterns` +
   `governance.output`, also a PreToolUse Write/Edit hook),
   `formal-artifact-approval-gate.py` (`governance.approval_packet`),
   `spec-event-surfacer.py` (`governance.output`),
   `glossary-expansion.py` (`db`),
   `intake-classifier.py` (`db`, `config`, `intake`),
   `bridge-axis-2-surface.py` (`bridge.detector`, `bridge.notify`).
   The `gt` CLI also pays it on every invocation.

A PreToolUse hook should complete in well under 1s. This is a defect.

## Proposed Change

Make `chromadb` a lazily-imported optional dependency in
`groundtruth-kb/src/groundtruth_kb/db.py`. This is the root-cause fix: it
removes the chromadb import from the `import groundtruth_kb` critical path,
so all seven hooks and the `gt` CLI benefit, not just one hook.

### Mechanism

Replace the module-level eager `try: import chromadb` block at `db.py:39-46`:

```
# ChromaDB optional dependency (ignore_missing_imports configured in pyproject.toml)
try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    chromadb = None  # type: ignore[assignment]
    HAS_CHROMADB = False
```

with availability detection that does not execute the chromadb package, plus
a lazy loader that preserves optional-dependency fallback semantics:

```
import importlib.util

# ChromaDB optional dependency. Availability is resolved cheaply at import
# time via find_spec (which locates the module spec WITHOUT executing the
# package, ~17ms measured). The chromadb module itself is imported lazily on
# first semantic-search use so `import groundtruth_kb` stays fast for hooks
# and the CLI.
try:
    HAS_CHROMADB = importlib.util.find_spec("chromadb") is not None
except (ImportError, ValueError):
    HAS_CHROMADB = False

chromadb = None  # type: ignore[assignment]  # populated lazily by _load_chromadb()


def _load_chromadb():
    """Import and cache the chromadb module on first use.

    Returns the chromadb module, or None when chromadb is unavailable OR when
    the lazy import fails. On lazy ImportError, HAS_CHROMADB is flipped to
    False so the optional-dependency contract (treat chromadb as unavailable,
    fall back to SQLite LIKE search) is preserved exactly as in the prior
    eager-import-with-except-ImportError design.
    """
    global chromadb, HAS_CHROMADB
    if chromadb is None and HAS_CHROMADB:
        try:
            import chromadb as _chromadb
        except ImportError:
            HAS_CHROMADB = False
            return None
        chromadb = _chromadb
    return chromadb
```

The consumption site `_get_chroma_collection()` (currently guarded by
`if not HAS_CHROMADB: return` at `db.py:5449`, constructing
`chromadb.PersistentClient(...)` at `db.py:5457`) is changed to resolve the
module lazily and return `None` if it is unavailable:

```
_chromadb = _load_chromadb()
if _chromadb is None:
    return None
self._chroma_client = _chromadb.PersistentClient(path=str(chroma_path))
```

Because `_get_chroma_collection()` already returns `None` today when
`HAS_CHROMADB` is false, every existing caller (including
`search_deliberations()`, which Codex noted calls `_get_chroma_collection()`
before its Chroma `try` block at `db.py:5643-5646`) already handles a `None`
collection by using the SQLite LIKE fallback. Routing the lazy-import-failure
case through the same `None` return reuses that fallback path with no new
branch. The `HAS_CHROMADB` guard at `db.py:5673` is a pure boolean read and is
unchanged.

### Why the `HAS_CHROMADB` contract is preserved

`HAS_CHROMADB` is read as a module attribute by `cli.py:3049`
(`getattr(_db_mod, "HAS_CHROMADB", False)`), `operating_state.py:220`,
`project/chroma.py:126`, and is imported at module load by
`tests/test_deliberations.py:13`, `tests/adopter/test_overlay_disposability.py:11`,
`tests/adopter/test_overlay_refresh.py:13`; several tests `monkeypatch.setattr`
it. Because `find_spec` keeps `HAS_CHROMADB` an eager, correct boolean
resolved at module import (not `None`-until-first-use), every one of these
readers and monkeypatch sites continues to work unchanged. No test file or
consumer module needs editing for the contract.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — this proposal is filed and reviewed through the file bridge; the bridge file lives under `bridge/`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this implementation proposal cites every governing specification it is aware of in this section.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan below derives executed tests from the linked specifications.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — the header carries the mandatory `Project Authorization`, `Project`, and `Work Item` metadata lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is a live GT-KB path inside `E:\GT-KB`; see the In-Root Placement Evidence section below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the work is tracked as durable MemBase artifacts: work item WI-3319, deliberation DELIB-S351-HOOK-IMPORT-LATENCY-AUTHORIZATION, and the project authorization.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across proposal, tests, and report is preserved through the bridge thread.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the bridge thread exposes the NEW, REVISED, GO, and VERIFIED lifecycle states for this change.
- `.claude/rules/file-bridge-protocol.md` — the protocol governing this proposal's structure and the specification-derived verification gate.
- `.claude/rules/codex-review-gate.md` — the mandatory pre-implementation review gate.
- `bridge/gov-process-spec-precondition-2026-04-29-005.md` — §2.3 Option A establishes the byte-identical active-hook / template-hook parity contract enforced by `test_hook_matches_template_or_documented_divergence`. This change leaves both hook files untouched, so the parity contract is satisfied unchanged.

## In-Root Placement Evidence

All target paths are repo-relative paths that resolve inside the GT-KB root
`E:\GT-KB`, satisfying `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
`.claude/rules/project-root-boundary.md`:

- `groundtruth-kb/src/groundtruth_kb/db.py` -> `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py` (existing platform source module; edit in place).
- `platform_tests/test_groundtruth_kb_import_budget.py` -> `E:\GT-KB\platform_tests\test_groundtruth_kb_import_budget.py` (new regression test under the existing in-root `platform_tests/` tree).

No target path is under `applications/`, no path leaves `E:\GT-KB`, and no
GT-KB artifact is created or read from `E:\Claude-Playground` or any
home-directory or temp location.

## Requirement Sufficiency

Existing requirements sufficient. The linked specifications govern the
bridge process and verification gates. The defect itself (a PreToolUse hook
must not take ~7s) does not require a new requirement; it is a correctness
and reliability fix to existing behavior. No new or revised specification is
needed before implementation.

## Prior Deliberations

- `DELIB-S351-HOOK-IMPORT-LATENCY-AUTHORIZATION` — the S351 owner decision
  (via AskUserQuestion) that selected project `GTKB-DETERMINISTIC-SERVICES-001`
  and approved creating `WI-3319` and the project authorization for this work.
- `DELIB-0704` — prior NO-GO on ChromaDB semantic search; required safe
  project-local Chroma behavior and credible Chroma test coverage. This
  proposal does not change Chroma index semantics; it only defers the import.
- `DELIB-0699` — later VERIFIED on ChromaDB semantic search; recorded that
  ChromaDB is optional/rebuildable and that ChromaDB indexing failures must
  not make canonical SQLite behavior appear failed. The F3 revision above is
  explicitly designed to honor this: a failed lazy import degrades to the
  SQLite LIKE fallback, not to an error.
- A `search_deliberations` scan for "hook latency chromadb", "lazy chromadb",
  and "hook startup performance" returned 0 results — no prior deliberation
  addresses the hook-import-latency topic itself.

## Test Plan (spec-to-test mapping)

A new regression test file `platform_tests/test_groundtruth_kb_import_budget.py`
will be added. It enforces the fix deterministically (no timing thresholds,
which would themselves be flaky):

1. **`test_chromadb_not_eagerly_imported`** — derives from
   DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 and the problem statement.
   Runs `python -c "import sys, groundtruth_kb; assert 'chromadb' not in sys.modules"`
   in a subprocess; asserts exit 0. Proves importing `groundtruth_kb` no
   longer pulls chromadb into the critical path.
2. **`test_has_chromadb_is_eager_bool`** — derives from the
   `HAS_CHROMADB`-contract analysis. Imports `groundtruth_kb.db.HAS_CHROMADB`
   and asserts it is a `bool` (not `None`), proving the eager-boolean contract
   relied on by `cli.py`, `operating_state.py`, `project/chroma.py`, and the
   deliberations/overlay test suites is preserved.
3. **`test_lazy_chromadb_loads_on_demand`** — derives from the lazy-load
   mechanism. When `HAS_CHROMADB` is true, calls `db._load_chromadb()` and
   asserts it returns a non-None module and that `chromadb` is then present
   in `sys.modules`. Skipped when chromadb is not installed.
4. **`test_lazy_chromadb_import_failure_degrades_gracefully`** — derives from
   F3 and `DELIB-0699`. Monkeypatches `db.HAS_CHROMADB = True`, `db.chromadb =
   None`, and forces `import chromadb` to raise `ImportError` (via a
   `sys.meta_path` finder or `monkeypatch` on `builtins.__import__`). Asserts
   `db._load_chromadb()` returns `None`, that `db.HAS_CHROMADB` is then
   `False`, and that `search_deliberations()` still returns SQLite-LIKE
   results without raising. Proves a broken/partial chromadb install degrades
   to the documented optional-dependency fallback rather than erroring.

Existing regression coverage to be executed unchanged as part of
verification (these exercise the chromadb / semantic-search path and the
`HAS_CHROMADB` contract):

- `groundtruth-kb/tests/test_deliberations.py`
- `groundtruth-kb/tests/test_cli_deliberations.py`
- `groundtruth-kb/tests/adopter/test_overlay_refresh.py`
- `groundtruth-kb/tests/adopter/test_overlay_disposability.py`
- `groundtruth-kb/tests/test_operating_state.py`
- `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`
- `platform_tests/scripts/test_codex_bridge_compliance_gate.py`

### Verification commands (to be run in the implementation report)

- `python -X importtime -c "from groundtruth_kb.governance.output import emit_pass"` — before/after, to record the latency drop.
- `python -m pytest platform_tests/test_groundtruth_kb_import_budget.py -v`
- `python -m pytest groundtruth-kb/tests/test_deliberations.py groundtruth-kb/tests/test_cli_deliberations.py groundtruth-kb/tests/adopter/test_overlay_refresh.py groundtruth-kb/tests/adopter/test_overlay_disposability.py groundtruth-kb/tests/test_operating_state.py -v`
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -v`
- `ruff check groundtruth-kb/src/groundtruth_kb/db.py platform_tests/test_groundtruth_kb_import_budget.py`

## Acceptance Criteria

1. `import groundtruth_kb` does not import `chromadb` (verified by
   `test_chromadb_not_eagerly_imported`).
2. `from groundtruth_kb.governance.output import emit_pass` measured with
   `-X importtime` completes in well under 1s (target; recorded in report).
3. `groundtruth_kb.db.HAS_CHROMADB` remains an eagerly-resolved `bool`.
4. A lazy-import `ImportError` degrades to `HAS_CHROMADB = False` + SQLite
   fallback, not an exception (verified by
   `test_lazy_chromadb_import_failure_degrades_gracefully`).
5. Semantic search / deliberations functionality is unchanged: the existing
   deliberations, overlay, and operating-state test suites pass.
6. The two bridge-compliance-gate hook files are unmodified and remain
   byte-identical; `test_hook_matches_template_or_documented_divergence`
   still passes.
7. New import-budget regression test file passes.

## Risk and Rollback

- **Risk: a broken chromadb install.** Addressed by F3: `_load_chromadb()`
  catches `ImportError`, returns `None`, and sets `HAS_CHROMADB = False`, so a
  broken/partial install degrades to the SQLite LIKE fallback — the same
  observable behavior as today's eager `try/except ImportError`. The failure
  timing moves from import-time to first-semantic-search-use, but the outcome
  (treated as unavailable) is identical, and test 4 locks it in.
- **Risk: a consumer reads `chromadb` (the module global) directly while
  it is still `None`.** Grep confirms the only `chromadb.`-attribute use in
  `db.py` is the `PersistentClient` site being converted; no other module
  imports `chromadb` from `groundtruth_kb.db`. Low risk.
- **Rollback:** revert `db.py` to the module-level eager import and delete
  the new test file. The change is confined to one source file plus one new
  test file; rollback is a single-file revert.

## Alternatives Considered

- **Make `bridge-compliance-gate.py` not import `groundtruth_kb` at all**
  (rely on its existing `except ImportError` fallback `emit_*` definitions).
  Rejected as the primary fix: it repairs only one of the seven affected
  hooks and leaves the `gt` CLI and `scanner-safe-writer.py` still paying
  ~7s. It also is not behavior-neutral as written — the hook's fallback
  `emit_deny` emits an extra `additionalContext` field that the canonical
  `governance.output.emit_deny` does not. The lazy-chromadb fix addresses the
  root cause for every consumer and needs no hook-file edits, so the
  byte-identical parity contract is not even engaged.
- **Lazy-load `db` from `groundtruth_kb/__init__.py` via PEP 562
  `__getattr__`.** Rejected: larger surface change to the package's public
  API import path, and unnecessary — `db.py`'s own import is fast once
  chromadb is removed from it.

## Recommended Commit Type

`perf:` — the change removes dead import latency from the hook critical
path with no behavior change. (Final type confirmed in the implementation
report per the Conventional Commits discipline.)

## Owner Decisions / Input

- The owner (Mike) directly tasked this investigation and fix in the S351
  session prompt, directing it be handled "via the bridge protocol (file an
  implementation proposal first)" and suggesting the lazy-chromadb approach.
- The owner confirmed via AskUserQuestion (S351) that this proposal is filed
  into the canonical main-repo bridge at `E:\GT-KB\bridge\`.
- The owner decided via AskUserQuestion (S351) that the work attaches to
  project `GTKB-DETERMINISTIC-SERVICES-001`.
- The owner approved via AskUserQuestion (S351) the creation of work item
  `WI-3319` and project authorization
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HOOK-IMPORT-LATENCY` as
  presented. All three decisions are archived as
  `DELIB-S351-HOOK-IMPORT-LATENCY-AUTHORIZATION`
  (`source_type=owner_conversation`, `outcome=owner_decision`), with the
  formal-artifact-approval packet at
  `.groundtruth/formal-artifact-approvals/2026-05-14-delib-s351-hook-import-latency-authorization.json`.
