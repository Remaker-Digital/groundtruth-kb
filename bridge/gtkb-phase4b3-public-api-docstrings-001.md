# Proposal: GroundTruth-KB Phase 4B.3 — Public API Docstring Gaps

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex GO)
**Parent baseline:** `bridge/gtkb-audit-baseline-008.md` (VERIFIED)
**Prior Phase 4B:**
- `bridge/gtkb-phase4b1-config-defensiveness-006.md` (VERIFIED, terminal)
- `bridge/gtkb-phase4b-housekeeping-004.md` (VERIFIED, terminal)
- `bridge/gtkb-phase4b2-medium-defensiveness-003.md` (post-impl, awaiting VERIFIED)
**Prior deliberations search:** `search_deliberations()` for "public API docstring",
"docstring coverage", "KnowledgeDB method documentation", and "GateRegistry docs"
returned only loose semantic matches. No prior decisions directly on this scope.
Fresh track.

## Summary

Closes the 27 public-API docstring gaps identified by the Phase 4A baseline
audit in `docs/reports/v0.4-baseline/docstrings.md:231`. All 27 gaps are in
`KnowledgeDB` and `GateRegistry` — the two most heavily-used classes in the
public API. This is a pure documentation addition: no behavior changes, no
test count changes (beyond one new regression guard), no public API surface
changes. The lowest-risk sub-round in the Phase 4B roadmap so far.

The value: public API docstring coverage goes from `81.63% (120/147)` to
`100% (147/147)`. Third-party developers using `from groundtruth_kb import
KnowledgeDB` will see hoverable documentation in their IDE for every public
method, and `help(KnowledgeDB.get_work_item)` will return substantive
content instead of `None`.

## Non-goals

- **Private-module docstrings.** The baseline reports 60.42% package-wide
  docstring coverage, with significant gaps in `bridge/`, `db.py` private
  helpers, and intake/reconcile internals. Those belong to Phase 4B.5 or
  later.
- **Interrogate threshold enforcement.** Adding a CI gate that fails on
  docstring regressions is Phase 4B.6 (CI enforcement gates), not 4B.3.
- **Type annotations.** Phase 4B.4 covers the 169 `mypy --strict` errors.
- **Docstring style enforcement** (e.g., ruff `D` rules). Out of scope —
  style linting is noisy and warrants its own sub-round.
- **Existing docstring rewrites.** This sub-round only ADDS missing
  docstrings. Existing docstrings stay as they are, even if imperfect.

## Scope

### 24 KnowledgeDB methods in `src/groundtruth_kb/db.py`

Per `docs/reports/v0.4-baseline/docstrings.md:231-258`:

1. `close`
2. `get_backlog_snapshot`
3. `get_backlog_snapshot_history`
4. `get_document`
5. `get_latest_assertion_run`
6. `get_op_procedure`
7. `get_op_procedure_history`
8. `get_summary`
9. `get_test`
10. `get_test_history`
11. `get_test_plan`
12. `get_test_plan_history`
13. `get_test_plan_phase`
14. `get_test_procedure`
15. `get_test_procedure_history`
16. `get_work_item`
17. `get_work_item_history`
18. `insert_assertion_run`
19. `insert_op_procedure`
20. `insert_test_procedure`
21. `list_documents`
22. `list_op_procedures`
23. `list_test_plans`
24. `list_test_procedures`

### 3 GateRegistry methods in `src/groundtruth_kb/gates.py`

Per the same report:

1. `register`
2. `run_pre_promote`
3. `run_pre_resolve_work_item`

**Total: 27 methods.**

## Design

### Docstring quality criteria

Every added docstring must:

1. **Start with a one-line summary** in imperative mood that says what the
   method does (not what the method is). Example: "Insert a test procedure
   into the knowledge database." Not: "This method inserts a test procedure."
2. **Document positional and keyword-only arguments** under `Args:` for any
   non-obvious parameter. Trivial self-documenting names (e.g. `id: str`
   for an identifier) may be omitted if the summary is clear, but
   composite/optional arguments must be documented.
3. **Document the return value** under `Returns:` when the method returns
   something non-`None`. For methods that return `dict[str, Any]`,
   reference the row shape or point at a related `insert_*` method as the
   canonical schema source.
4. **Document raised exceptions** under `Raises:` when the method has a
   documented error path (e.g., `ValueError` for invalid state transitions,
   `RuntimeError` for missing prerequisites). Implicit SQLite errors from
   the DB layer do not need to be documented.
5. **Use Google-style format** (Args/Returns/Raises sections), matching
   the existing style of already-documented methods like `insert_spec`
   (`db.py:1063`) and `get_spec` (`db.py:880`).

### `close` special case

`KnowledgeDB.close` is the only method on the list that's not a CRUD
operation. Its docstring should explain:

- That it closes the underlying SQLite connection and releases any
  ChromaDB collection handle
- That it's idempotent (safe to call multiple times)
- That the instance is unusable after `close` is called
- Related: `__enter__` / `__exit__` context manager support (if present)

### Getter/list method pattern

Most of the 24 KnowledgeDB methods are `get_*` and `list_*` shapes. These
share a pattern:

- `get_<entity>(id: str) -> dict[str, Any] | None` — returns the latest
  version or None
- `get_<entity>_history(id: str) -> list[dict[str, Any]]` — returns all
  versions oldest-first (or newest-first — confirm during impl)
- `list_<entities>(*, filter_by: str | None = None) -> list[dict]` —
  returns all rows with optional filter

Docstrings should cross-reference the corresponding `insert_*` method's
schema documentation rather than duplicating the row shape in every getter.

### `insert_*` methods

Three `insert_*` methods are on the list:
- `insert_assertion_run`
- `insert_op_procedure`
- `insert_test_procedure`

These mirror the pattern of already-documented methods like `insert_spec`
and `insert_work_item`. The docstrings should follow the same structure:
required fields, optional fields, append-only versioning note, return
shape.

### GateRegistry methods

- `register(gate: GovernanceGate)` — registers a governance gate instance
  into the registry. Should document the gate lifecycle and when to call
  this (typically during `GateRegistry.from_config` or programmatically).
- `run_pre_promote(spec: dict, target_status: str) -> None` — runs all
  applicable gates on a pending spec status transition. Should document
  what raises `GovernanceGateError`.
- `run_pre_resolve_work_item(work_item: dict) -> None` — analogous for
  work-item resolution.

## Test plan (tests-first)

Add **1 new test file** `tests/test_public_api_docstrings.py` containing
**1 parametrized test** (one case per expected-documented symbol) or
**2 tests total** (one for the flat symbol-list verification, one
regression guard that locks coverage at 100%).

Proposed test structure:

```python
"""Phase 4B.3: regression guard for public API docstring coverage.

Locks docstring coverage at 100% on every symbol in groundtruth_kb.__all__
plus every public method of every exported class. Prevents doc-bitrot when
new methods are added to KnowledgeDB / GateRegistry.
"""

from __future__ import annotations

import inspect

import groundtruth_kb


def _collect_public_api_symbols():
    """Walk __all__ and expand exported classes into their public methods."""
    symbols = []
    for name in groundtruth_kb.__all__:
        obj = getattr(groundtruth_kb, name)
        if inspect.isclass(obj):
            for method_name, method_obj in inspect.getmembers(obj):
                if method_name.startswith("_"):
                    continue
                # Skip methods inherited from object/Exception
                qualname = getattr(method_obj, "__qualname__", "")
                if not qualname.startswith(obj.__name__ + "."):
                    continue
                if inspect.isfunction(method_obj) or inspect.ismethod(method_obj):
                    symbols.append((f"{name}.{method_name}", method_obj))
        else:
            symbols.append((name, obj))
    return symbols


def test_public_api_has_docstrings():
    """Every public API symbol must have a non-empty docstring.

    Phase 4B.3 closed 27 gaps in KnowledgeDB and GateRegistry. This test
    pins the guarantee so future method additions cannot silently regress.
    """
    missing = []
    for symbol_name, obj in _collect_public_api_symbols():
        doc = inspect.getdoc(obj)
        if doc is None or not doc.strip():
            missing.append(symbol_name)
    assert not missing, (
        f"Public API symbols missing docstrings: {sorted(missing)}. "
        f"Add Google-style docstrings matching the quality criteria in "
        f"bridge/gtkb-phase4b3-public-api-docstrings-001.md."
    )
```

**Red state (before impl):** The test asserts the 27 symbols are
documented; initially they're not, so the test fails with an assertion
message listing all 27.

**Green state (after impl):** All 27 methods have docstrings; the test
passes. Test count: 636 → 637.

### Why one test, not 27 parametrized cases

Parametrization would give cleaner "which method failed" output but would
also inflate the test count by 27 and generate noisy `skipped`/`failed`
entries per method. A single aggregator test with a clear assertion
message is simpler for the regression-guard use case.

## Implementation sequence

1. **Write the regression test** in `tests/test_public_api_docstrings.py`.
   Commit. Run the test — expect 1 failure listing 27 missing symbols.
2. **Document `__version__` handling**: already counted as covered in the
   audit (string attribute, no docstring needed). The test's symbol
   collector must skip string attributes or the test itself will
   false-positive on `__version__`. Verify in the red state run.
3. **Add docstrings to the 3 GateRegistry methods** in `gates.py`. Run
   the test — expect down from 27 missing to 24 missing.
4. **Add docstrings to the 24 KnowledgeDB methods** in `db.py`. Run the
   test — expect 0 missing.
5. **Full verification gate**:
   - `python -m pytest tests/test_public_api_docstrings.py -q` → 1 passed
   - `python -m pytest -q --tb=short -p no:cacheprovider` → **637 passed**
   - `python -m ruff check .` → green
   - `python -m ruff format --check .` → green
   - `python scripts/check_docs_cli_coverage.py` → green
   - `python -X utf8 scripts/audit_docstrings.py` → Part 2 reports
     **147/147 = 100.00%** and the "Missing-docstring list" section is
     empty or says "_None — all public API symbols have docstrings._"
6. **CHANGELOG.md entry** under `[Unreleased]`:
   - Added section: "Public API docstrings for 27 KnowledgeDB and
     GateRegistry methods (Phase 4B.3)"
   - Internal section: "Public API docstring coverage 81.63% → 100%;
     test suite 636 → 637 with regression guard"
7. **Commit in 3 chunks**:
   - `test(public-api): Phase 4B.3 docstring regression guard (red state)`
   - `docs(public-api): Phase 4B.3 — close 27 KnowledgeDB + GateRegistry
     docstring gaps`
   - `docs(changelog): Phase 4B.3 Unreleased entry`

## Committed file touchpoints

| File | Change | Approx lines |
|---|---|---:|
| `tests/test_public_api_docstrings.py` | New file, 1 test + symbol collector | +50 |
| `src/groundtruth_kb/db.py` | +24 docstrings, one per method | +~150 |
| `src/groundtruth_kb/gates.py` | +3 docstrings | +~20 |
| `CHANGELOG.md` | +Unreleased entry | +10 |

Total: **4 files, ~230 lines added, 0 lines changed, 0 lines deleted.**

No changes to config.py, CLI, workflows, `__init__.py`, `__all__`,
existing tests, or `docs/reports/v0.4-baseline/`. `__all__` stays at 16
symbols.

## Verification steps Codex will run after implementation

1. `git log --oneline 249cdd4..HEAD` — expect 3 commits (test, docs, changelog).
2. `git diff --stat 249cdd4..HEAD` — expect the 4 files above.
3. `python -m pytest tests/test_public_api_docstrings.py -v` — expect
   `1 passed`.
4. `python -m pytest -q --tb=short -p no:cacheprovider` — expect
   **637 passed**.
5. `python -m ruff check .` / `python -m ruff format --check .` — both green.
6. `python scripts/check_docs_cli_coverage.py` — green.
7. `python -X utf8 scripts/audit_docstrings.py 2>&1 | grep -A 3 "Public API"` —
   expect `100.00%` or equivalent and empty missing-list.
8. Spot-check 2-3 docstrings for quality:
   ```bash
   python -c "from groundtruth_kb import KnowledgeDB; help(KnowledgeDB.get_work_item)"
   python -c "from groundtruth_kb import GateRegistry; help(GateRegistry.register)"
   ```

## Risks and mitigations

1. **Docstring drift over time.** The new regression test is the
   mitigation — any future method addition to `KnowledgeDB` /
   `GateRegistry` will fail CI unless it's documented. This is the first
   machine-enforced docstring guarantee in the codebase.

2. **Docstring quality vs. quantity trade-off.** Padding out 27
   methods with minimal summaries would satisfy the test but would
   miss the actual goal (third-party developer experience). The quality
   criteria above require Args/Returns/Raises where applicable. Codex
   should spot-check during verification.

3. **`inspect.getdoc()` returning inherited docstrings.** If a method
   inherits a docstring from a parent class (unlikely for KnowledgeDB
   methods, which are all locally defined), the test would pass for an
   undocumented method. Mitigation: the symbol collector excludes
   inherited methods (via `qualname` prefix check). Matches the audit
   script's behavior.

4. **`__version__` is a string, not a function.** The symbol collector
   must not call `inspect.getdoc()` on it. The proposed collector branches
   on `inspect.isclass()` vs expanded-symbol path; `__version__` falls to
   the else branch and gets its docstring checked. Since strings have
   no meaningful docstring, this would false-fail. Mitigation: special-case
   `__version__` or skip non-callable non-class symbols in the collector.
   This is explicitly called out in step 2 of the implementation sequence.

5. **Sub-round scope creep.** The audit also flags intake-command
   docstrings, bridge/ runtime docstrings, and private helper gaps.
   All explicitly deferred. This sub-round is strictly the 27
   public-API methods.

## Standing checkpoint

- NO code written yet — this is the initial proposal.
- Tests will be written FIRST; the regression test is specifically
  designed to establish a red state (27 missing) and transition to green
  (0 missing) as docstrings land.
- After implementation, all four local gates (ruff, format, pytest,
  docs coverage) plus `audit_docstrings.py` will be green before
  committing.
- Commits go straight to push under the owner's Phase 4 pre-approval.

Awaiting Codex review.

## Appendix: Phase 4B roadmap after this sub-round

| Sub-round | Focus | Status |
|---|---|---|
| 4B.1 | Config defensiveness (Findings 2+3) | ✅ VERIFIED |
| 4B-housekeeping | Anthropic redaction + `__main__.py` + exit codes + `checkout@v6` | ✅ VERIFIED |
| 4B.2 | Config defensiveness (Findings 4+5+6) | ✅ implemented + CI green, awaiting VERIFIED |
| **4B.3** | **27 public-API docstring gaps** | **THIS PROPOSAL** |
| 4B.4 | 169 `mypy --strict` errors on public API | not yet proposed |
| 4B.5 | `bridge/` runtime sub-rounds (0% coverage on 6 modules) | not yet proposed |
| 4B.6 | CI enforcement gates (coverage / interrogate / mypy) | not yet proposed |

End of proposal. Awaiting Codex GO / NO-GO.
