# Proposal: GroundTruth-KB Phase 4B.4 — Public API `mypy --strict` Fixes

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex GO)
**Parent baseline:** `bridge/gtkb-audit-baseline-008.md` (VERIFIED)
**Prior Phase 4B:**
- `bridge/gtkb-phase4b1-config-defensiveness-006.md` (VERIFIED, terminal)
- `bridge/gtkb-phase4b-housekeeping-004.md` (VERIFIED, terminal)
- `bridge/gtkb-phase4b2-medium-defensiveness-004.md` (VERIFIED, terminal)
- `bridge/gtkb-phase4b3-public-api-docstrings-004.md` (VERIFIED, terminal)

**Drafting history**: This proposal was drafted locally while Phase 4B.3
was still awaiting Codex GO, per Option A in the turn plan. While the
draft was being written (~15 minutes), the autonomous bridge pipeline
completed the entire Phase 4B.3 cycle: Codex posted GO, the poller
spawned a headless Prime (Sonnet) session, Sonnet implemented the
proposal (tests-first, then impl, then docs, then commits, then push,
then post-impl report — all in ~8.5 minutes of API time), and Codex
posted VERIFIED. The thread went from NEW → VERIFIED terminal without
any interactive-session participation. Phase 4B.3 is the first
fully-autonomous Phase 4 sub-round in this session. The 4B.4 draft
is now being posted because its unlock condition (4B.3 stable) is
satisfied.

**Prior deliberations search**: `search_deliberations()` for "mypy strict",
"public API type annotations", and "dict generic type parameters" returned
loose semantic matches only. No prior decisions directly on this scope.

## Summary

Closes the `mypy --strict` error surface on GroundTruth-KB's public API —
`db.py`, `config.py`, and `cli.py` — totaling **46 errors** per the Phase 4A
baseline at `docs/reports/v0.4-baseline/types.md`. Does not attempt to fix
all 169 errors in the repository; bridge runtime (84 errors = 49.7% of
total) gets its own Phase 4B.5, and internal helpers (`seed.py`,
`web/app.py`, `reconciliation.py`, `spec_scaffold.py`, `project/scaffold.py`
— 39 errors combined) are deferred to a later sub-round.

The value: users of `from groundtruth_kb import KnowledgeDB, GTConfig`
will get accurate static type information in their IDE. `mypy --strict`
will run clean on the public API files, enabling Phase 4B.6 to turn this
into a CI enforcement gate.

`gates.py` has zero mypy errors per the baseline and requires no changes.

## Non-goals

- **`bridge/` runtime type errors** (84 errors across 6 modules). Phase
  4B.5 track. The bridge/ modules are the single largest quality gap per
  the Phase 4A audit and warrant their own multi-round treatment.
- **Internal helpers** (`seed.py`, `web/app.py`, `reconciliation.py`,
  `spec_scaffold.py`, `project/scaffold.py`). These are not part of the
  public API surface and have a combined 39 errors. Defer to later.
- **CI enforcement gate for mypy.** Phase 4B.6 adds `mypy --strict` to
  the CI pipeline. 4B.4 only achieves local cleanliness; running it
  manually is the verification path.
- **New test cases for typed behavior.** Type annotations are
  compile-time constraints checked by mypy; no new pytest tests are
  added. The existing 637 tests (post-4B.3) continue to pass with
  zero changes.
- **Refactoring or API changes.** If a method's actual return value is
  `dict | None` and the old annotation said `dict`, the fix is to update
  the annotation — not to change the method's behavior.

## Scope

### 46 errors across 3 files

Per `docs/reports/v0.4-baseline/types.md` (Phase 4A baseline):

| File | Error count | Error code breakdown (estimated from samples) |
|---|---:|---|
| `src/groundtruth_kb/db.py` | 39 | Mostly `return-value` (mis-annotated optional returns) and `type-arg` (missing `[str, Any]` on `dict` hints) |
| `src/groundtruth_kb/cli.py` | 4 | Likely `no-untyped-def` on Click callbacks or `type-arg` on dict hints |
| `src/groundtruth_kb/config.py` | 3 | All `type-arg` per sample: `config.py:40`, `config.py:84`, `config.py:129` all "Missing type arguments for generic type 'dict'" |

### `gates.py` is already clean

`gates.py` is NOT in the baseline's "Errors by file" table. That means
`mypy --strict src/groundtruth_kb/gates.py` runs clean. The file
already has full type annotations and can be validated without changes.

### Recount before implementation

The Phase 4A baseline was measured at commit `993f31b`. Phase 4B.1
and 4B.2 edited `config.py` to add the new `GTConfigError` class,
`PermissionError` handling, and warning emissions. Those changes may
have shifted `config.py`'s error count. The implementation's first
step is to re-run `mypy --strict` against the current head
(`249cdd4` as of drafting) and record the actual error counts. The
46 number is the Phase 4A baseline; the implementation targets the
current-HEAD count (which may be slightly different).

## Design

### Error category strategy

The baseline's "Errors by category" table shows the top categories are
`type-arg` (66, 39.1%), `no-untyped-def` (24, 14.2%), `return-value`
(21, 12.4%), and `attr-defined` (20, 11.8%). For the public API subset:

**`type-arg` (missing generic parameters)**: mechanical fix. Examples:

```python
# Before (mypy error: type-arg)
gate_config: dict[str, dict] = field(default_factory=dict)

# After
gate_config: dict[str, dict[str, Any]] = field(default_factory=dict)
```

The same pattern applies to `list` without a type parameter, `tuple`
without types, etc. Fix: walk each `type-arg` error location and add
the correct generic parameters. Often `[str, Any]` is the right
answer for dicts whose values are heterogeneous.

**`return-value` (declared return type mismatches actual)**: semantic
fix. Examples from the baseline:

```
db.py:811 — Incompatible return value type (got "dict[str, Any] | None", expected "dict[str, Any]")
db.py:978 — Incompatible return value type (got "dict[str, Any] | None", expected "dict[str, Any]")
db.py:1648 — Incompatible return value type (got "dict[str, Any] | None", expected "dict[str, Any]")
```

The methods at those lines return `None` in some code paths (e.g., when
a row isn't found) but were annotated as always returning `dict`. Fix:
update the return annotation to `dict[str, Any] | None` so callers are
forced to handle the None case. This is a **public API contract change**
in the sense that type-checked callers may need to add None-handling,
but the runtime behavior is unchanged — the method was always returning
None, the annotation was just wrong.

**`no-untyped-def` (missing return type annotation)**: mechanical fix.
Add an explicit return type annotation. For methods that return `None`,
add `-> None`. For methods that return a value, infer the type from the
return statements and add it. No behavior changes.

**`attr-defined` (accessing undefined attribute)**: Usually a real bug
indicator. Requires case-by-case analysis. The samples are in `seed.py`
which is out of scope for 4B.4, so the public API subset may have zero
of these.

### Imports

Adding fully-typed dict signatures often requires importing `Any` from
`typing`:

```python
from typing import Any
```

Some files already have this import; others don't. Add the import to
files that need it.

### `mypy` as a dev dependency

The Phase 4A audit installed `mypy==1.20.1` ad-hoc via `pip install`.
For Phase 4B.4, mypy becomes a reproducible tool that contributors and
CI need to run. Add to `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    # ... existing dev dependencies ...
    "mypy==1.20.1",
]
```

The specific version pin matches Phase 4A to prevent spurious drift from
newer mypy releases changing error wording.

### No `pyproject.toml` [tool.mypy] section yet

Adding a `[tool.mypy]` section configures mypy globally for the repo.
That would be useful for 4B.6 (CI enforcement) but is premature for
4B.4, which only needs local cleanliness on 3 files. The implementer
can run:

```bash
python -m mypy --strict src/groundtruth_kb/db.py \
                        src/groundtruth_kb/config.py \
                        src/groundtruth_kb/cli.py \
                        src/groundtruth_kb/gates.py
```

And assert exit code 0. Phase 4B.6 will formalize this into a
`[tool.mypy]` section with `strict = true` and appropriate module
excludes for `bridge/` and `seed.py`.

## Test plan (not traditional tests-first)

Type annotations are compile-time constraints, not runtime behavior.
There are no pytest tests to add. The verification is a mypy run.

**Red state** (before implementation):

```
python -m mypy --strict src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py
Found N errors in M files (checked 4 source files)
```

Where N is the current-HEAD error count for the 4 files (expected ~46
per baseline, may have drifted slightly after Phase 4B.1/4B.2 edits).

**Green state** (after implementation):

```
python -m mypy --strict src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py
Success: no issues found in 4 source files
```

**Regression guard**: add a new test file
`tests/test_public_api_type_checks.py` with ONE test that invokes
mypy as a subprocess and asserts clean exit:

```python
"""Phase 4B.4: regression guard for public API mypy strict cleanliness.

Pins mypy --strict to green on the 4 public API source files so future
changes cannot silently regress the type surface. Skipped if mypy is
not installed (opt-in regression guard, not hard dependency).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PUBLIC_API_FILES = [
    "src/groundtruth_kb/db.py",
    "src/groundtruth_kb/config.py",
    "src/groundtruth_kb/cli.py",
    "src/groundtruth_kb/gates.py",
]


def test_public_api_mypy_strict_is_clean():
    """mypy --strict must report zero errors on the public API surface.

    Phase 4B.4 closed 46 baseline errors. This test pins the guarantee
    so future changes to db.py / config.py / cli.py / gates.py cannot
    silently regress the type surface.
    """
    if shutil.which("mypy") is None:
        pytest.skip("mypy not installed; install via pip install '.[dev]'")

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict"] + PUBLIC_API_FILES,
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"mypy --strict found issues on the public API surface:\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
```

This test:
- Skips gracefully if mypy isn't installed (so base-install CI runs that
  don't include `[dev]` extras don't break)
- Runs only on the 4 public API files (not the whole repo)
- Catches regressions introduced in future PRs that modify these files

Test count: 637 → 638 (after 4B.3 + this one test).

## Implementation sequence

1. **Recount errors** on current HEAD: `python -m pip install mypy==1.20.1`,
   then `python -m mypy --strict <4 files>`. Record the actual count for
   accurate reporting.
2. **Add `mypy==1.20.1` to `pyproject.toml` [dev] extra**. Install via
   `pip install -e ".[dev]"`.
3. **Write the regression test** `tests/test_public_api_type_checks.py`.
   Run — expect FAIL (mypy finds errors).
4. **Fix `config.py` errors** (3 baseline errors, probably still ~3):
   add `[str, Any]` or equivalent generic parameters. Re-run mypy on
   config.py — expect clean.
5. **Fix `cli.py` errors** (4 baseline errors): probably `no-untyped-def`
   or `type-arg`. Re-run mypy on cli.py — expect clean.
6. **Fix `gates.py`**: re-verify it's clean (baseline showed no errors,
   but recount). Should be no-op if baseline is accurate.
7. **Fix `db.py` errors** (39 baseline errors): this is the big one.
   Split into sub-steps:
   - Fix all `type-arg` first (mechanical, no semantic impact)
   - Fix all `return-value` second (add `| None` to return annotations
     where methods actually return None)
   - Fix remaining miscellaneous errors
8. **Re-run full mypy**: `python -m mypy --strict <4 files>` → expect
   `Success: no issues found in 4 source files`.
9. **Run regression test**: `python -m pytest tests/test_public_api_type_checks.py -v`
   → expect `1 passed`.
10. **Run full pytest suite**: expect **638 passed** (637 + the new
    regression guard).
11. **Run ruff + format + docs CLI coverage**: all green.
12. **Update `CHANGELOG.md`** under `[Unreleased]`:
    - Added: regression guard `tests/test_public_api_type_checks.py`
    - Internal: closed N `mypy --strict` errors on public API surface
    - Internal: added `mypy==1.20.1` to dev dependencies
13. **Commit in 4 chunks**:
    - `test(public-api): Phase 4B.4 mypy regression guard (red state)`
    - `build(deps): add mypy==1.20.1 to [dev] extra for Phase 4B.4`
    - `fix(public-api): Phase 4B.4 close mypy --strict errors in config.py + cli.py + gates.py`
    - `fix(db): Phase 4B.4 close mypy --strict errors in db.py`
14. **Push under Phase 4 pre-approval**, monitor CI for green.

## Committed file touchpoints

Expected diff scope:

| File | Change | Approx lines |
|---|---|---:|
| `pyproject.toml` | +`mypy==1.20.1` in `[dev]` extra | +1 |
| `tests/test_public_api_type_checks.py` | new file, 1 test | +50 |
| `src/groundtruth_kb/config.py` | +3 type annotation fixes | +3 changed |
| `src/groundtruth_kb/cli.py` | +~4 type annotation fixes | +~5 changed |
| `src/groundtruth_kb/db.py` | +~39 type annotation fixes | +~50 changed |
| `src/groundtruth_kb/gates.py` | zero changes if baseline accurate | 0 |
| `CHANGELOG.md` | +Unreleased entry | +15 |

Total: **~5-6 files, ~120-150 lines added, ~60 lines changed, 0 lines
deleted**. No functional behavior changes. `__all__` stays at 16.

## Verification steps Codex will run after implementation

1. `git log --oneline <4B.3-head>..HEAD` — expect 4 commits.
2. `git diff --stat <4B.3-head>..HEAD` — expect the files above.
3. `python -m mypy --strict src/groundtruth_kb/db.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/gates.py`
   — expect `Success: no issues found in 4 source files`.
4. `python -m pytest tests/test_public_api_type_checks.py -v` —
   expect `1 passed`.
5. `python -m pytest -q --tb=short -p no:cacheprovider` — expect
   `638 passed`.
6. `python -m ruff check .` / `python -m ruff format --check .` — both green.
7. `python scripts/check_docs_cli_coverage.py` — green.
8. `python -c "from groundtruth_kb import __all__; print(len(__all__))"` —
   expect `16` (unchanged).
9. Spot-check `KnowledgeDB.get_work_item` signature in an IDE or via
   `inspect.signature`:
   ```python
   import inspect
   from groundtruth_kb import KnowledgeDB
   print(inspect.signature(KnowledgeDB.get_work_item))
   ```
   Expect a signature with explicit return type, not `Any`.

## Risks and mitigations

1. **`return-value` fixes are type-contract changes.** Callers that
   assumed `db.get_spec(id) -> dict` will now see
   `db.get_spec(id) -> dict | None`. If any caller was written
   against the old annotation without None-handling, mypy will now flag
   them. This is the right outcome (it catches a latent bug) but could
   generate new failures in non-public-API files that call the public
   API. Mitigation: when fixing a `return-value` error, immediately run
   mypy on the whole `src/` to see if the fix cascades. If it does,
   fix those cascades in the same commit.

2. **mypy version drift.** Pinning to 1.20.1 matches Phase 4A's baseline.
   Later mypy versions may introduce new error codes or rephrase
   existing ones. Using a pinned version prevents false regressions
   when a new mypy is released. Phase 4B.6 can unpin or bump the
   version explicitly.

3. **Public API cascade on reconciliation.py / seed.py / bridge/.**
   These files use `KnowledgeDB` and may have `return-value` callers.
   If we fix `db.py:811` to return `dict | None`, any caller that does
   `db.get_spec(id)["type"]` would become a mypy error (accessing
   `[]` on a possibly-None value). Mitigation: we only fix the public
   API surface (4 files); we do NOT run mypy on the rest of the repo
   in 4B.4, so cascading errors in `seed.py`/`bridge/`/etc. won't
   fail this sub-round. They'll be caught and fixed in 4B.5 or later.

4. **Overlap with 4B.3 in `db.py`.** 4B.3 adds docstrings to 24
   methods in `db.py`; 4B.4 may modify the type annotations on those
   same methods. If the poller serializes them (4B.3 lands, then 4B.4),
   the result is a merge — 4B.4 reads the file with docstrings in place
   and adds types alongside. Low risk given serialization. If somehow
   4B.4 were to start before 4B.3 completed, the conflict would be on
   the method signature lines (where both docstrings and types attach).
   Mitigation: Phase 4B.4 does NOT start implementation until Phase 4B.3
   is VERIFIED (this is enforced by the poller's one-at-a-time behavior
   on the bridge INDEX).

5. **Scope creep temptation.** The audit flags 169 errors total;
   fixing only 46 of them may feel incomplete. Explicitly deferred:
   `bridge/` → 4B.5, `seed.py` / `web/app.py` / `reconciliation.py` /
   `spec_scaffold.py` / `project/scaffold.py` → later. This sub-round
   is strictly the public API surface.

## Standing checkpoint

- NO code written yet — this is the initial proposal DRAFT, held
  locally until Phase 4B.3 reaches stable status.
- When committed to bridge, the commit message will note that this
  proposal was drafted during the wait period.
- Implementation follows the tests-first-or-equivalent pattern: write
  the regression test, run it in red state, fix errors, run green.
- After implementation, all gates (ruff, format, pytest, docs coverage,
  mypy --strict on 4 files) green before committing.
- Commits go straight to push under the Phase 4 pre-approval.

Awaiting Phase 4B.3 stable state, then posting to bridge.

## Appendix: Phase 4B roadmap after this sub-round

| Sub-round | Focus | Status |
|---|---|---|
| 4B.1 | Config defensiveness (Findings 2+3) | ✅ VERIFIED |
| 4B-housekeeping | Anthropic redaction + `__main__.py` + exit codes + `checkout@v6` | ✅ VERIFIED |
| 4B.2 | Config defensiveness (Findings 4+5+6) | ✅ VERIFIED |
| 4B.3 | 27 public-API docstring gaps | awaiting Codex GO |
| **4B.4** | **`mypy --strict` cleanliness on 4 public API files** | **THIS DRAFT** |
| 4B.5 | `bridge/` runtime sub-rounds (0% coverage, 84 mypy errors, 6 modules) | not yet proposed (multi-round track) |
| 4B.5b | Internal helpers mypy (seed.py, web/, reconciliation, spec_scaffold, project) | not yet proposed |
| 4B.6 | CI enforcement gates (`--cov-fail-under`, `interrogate --fail-under`, `mypy --strict`) | not yet proposed (depends on 4B.3, 4B.4) |

End of proposal. Drafted locally; will be posted to bridge when 4B.3
reaches VERIFIED or stable status.
