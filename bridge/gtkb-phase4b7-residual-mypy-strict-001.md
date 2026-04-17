# GT-KB Phase 4B.7 — Close Residual `mypy --strict` Errors (39 → 0)

**Status:** NEW
**Prime Builder:** Claude Opus 4.6
**Author session:** S295 (worktree `elegant-brattain`)
**Repository:** `groundtruth-kb` @ `efd0282` (main)
**Branch:** will be created as `phase-4b7-residual-mypy-strict` off `main`

## Prior Deliberations

This proposal is the natural terminal sub-round of the Phase 4B mypy track.
Prior work:

- `bridge/gtkb-phase4b4-mypy-strict-public-api-004.md` — **VERIFIED**. Closed
  48 errors on the public API surface (`db.py`, `config.py`, `cli.py`, `gates.py`).
- `bridge/gtkb-phase4b5a-bridge-annotations-006.md` — **VERIFIED**. Closed
  ~52 errors in `bridge/` runtime via pure annotation fixes (added `-> None`,
  typed parameters, `cast()` at well-defined boundaries). Explicitly scoped to
  annotative fixes; semantic narrowing was deferred to a follow-up.
- `bridge/gtkb-phase4b5b-internal-helpers-mypy-007.md` — **VERIFIED**. Closed
  40 errors across 5 internal helper modules and added a CI regression gate.
- `bridge/gtkb-phase4b6-ci-enforcement-gates-010.md` — **VERIFIED**. Added
  `mypy --strict` CI step, per-file coverage gates, docstring ratchet.

**This proposal finishes the job 4B.5a deferred.** It is not a re-opening of
prior scope; it is the explicitly-deferred semantic-narrowing tail that 4B.5a
identified and left alone.

## Ground-Truth Measurement

Run verbatim immediately before drafting this proposal:

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
python -m mypy --strict src/groundtruth_kb/
# Found 39 errors in 5 files (checked 31 source files)
```

Distribution by file (exact counts):

| File | Errors | Dominant pattern |
|---|---|---|
| `src/groundtruth_kb/bridge/poller.py` | 17 | `fcntl` None on Windows, `object` arithmetic from cfg dict, `Popen` kwargs |
| `src/groundtruth_kb/bridge/worker.py` | 10 | `fcntl` None on Windows, `subprocess.run` kwargs |
| `src/groundtruth_kb/intake.py` | 7 | Unguarded indexing of `dict[str, Any] \| None` from `db.get_*()` returns |
| `src/groundtruth_kb/bridge/runtime.py` | 4 | Misc narrowing (`str \| None` to `json.loads`, `int \| None` to `int()`, `str` to `Literal`, `None` to `FastMCP[Any]`) |
| `src/groundtruth_kb/bridge/context.py` | 1 | `Path \| None` assigned to `Path` |
| **Total** | **39** | |

Full error list is attached as a verbatim dump in §Appendix A below.

## Objective

Drive `mypy --strict src/groundtruth_kb/` from 39 errors to 0, add a CI
regression guard that locks the count at 0, and do so with zero runtime
behavior change (pure typing work).

## Scope — Fix Patterns

### Pattern A — `fcntl` platform-conditional imports (10 errors)

**Affected:** `bridge/poller.py:61-69`, `bridge/worker.py:145-150`.

**Root cause:** `fcntl` is a Unix-only module. The current code likely has a
`try/except ImportError` or `if sys.platform != "win32": import fcntl` pattern
that leaves `fcntl` as `None` in the Windows-branch type. Mypy then sees every
use as `None.flock(...)` and flags it.

**Fix:** Use `TYPE_CHECKING` import guard so mypy always sees the real module:

```python
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import fcntl  # type checker always sees Unix module
else:
    if sys.platform != "win32":
        import fcntl
    else:
        fcntl = None  # runtime fallback for Windows code paths
```

The runtime guards (`if fcntl is not None:` or `if sys.platform != "win32":`)
at each call site remain unchanged. Only the import stanza shifts.

Alternative if the current file-locking is dead code on Windows: wrap the
entire locking block with `if sys.platform != "win32":` at the call site and
add `# type: ignore[unreachable]` below for the Windows-only branch. Decision
will be made per file during implementation based on whether the lock is
currently called on Windows at all.

### Pattern B — `subprocess.run` / `Popen` kwargs dict typing (4 errors)

**Affected:** `worker.py:250, 274, 596`, `poller.py:167`.

**Root cause:** A `kwargs` dict is built as `dict[str, object]` (or inferred
as such because values are mixed `str | int | bool`). `subprocess.run` / `Popen`
expect `**kwargs` with specific types per key, not an `object`-valued dict.

**Fix:** Either (a) use `cast(Any, kwargs)` at the unpacking site, or (b) call
`subprocess.run` directly with keyword arguments instead of `**kwargs`. Choose
(a) if there are many call sites and the kwargs are dynamic; (b) otherwise.

### Pattern C — `intake.py` `dict | None` unguarded indexing (7 errors)

**Affected:** `intake.py:223, 272, 279, 283, 289, 294, 302`.

**Root cause:** `db.get_spec()`, `db.get_work_item()`, etc. return
`dict[str, Any] | None`. Call sites in `intake.py` use the result directly
with `result["key"]` without a None guard.

**Fix:** Add explicit None guards at each call site. The right pattern depends
on semantics: if None means "not found and that's an error," raise
`GTIntakeError("...")`; if None means "skip this step," use an early `return`.
Implementation will audit each of the 7 sites individually; expected outcome
is ~5 raise-on-None + ~2 early-return.

### Pattern D — `poller.py` config `object` arithmetic (8 errors)

**Affected:** `poller.py:283, 291, 293, 338, 341, 349, 368, 372`.

**Root cause:** A config dict is typed `dict[str, object]` (possibly from
`json.load` or `tomllib.load`). Values are fetched as `cfg["poll_interval"]`
and immediately used in `cfg["poll_interval"] + 1`. Mypy correctly flags the
`object + int` operand mismatch.

**Fix:** Narrow at the config-load boundary:

```python
@dataclass(frozen=True)
class PollerConfig:
    poll_interval: int
    max_items_per_spawn: int
    # ...

def _load_config() -> PollerConfig:
    raw = json.loads(CONFIG_PATH.read_text())
    return PollerConfig(
        poll_interval=int(raw["poll_interval"]),
        max_items_per_spawn=int(raw["max_items_per_spawn"]),
    )
```

Then downstream code uses `config.poll_interval` (typed `int`) instead of
`cfg["poll_interval"]` (typed `object`). If a typed dataclass is too invasive,
fall back to `int(cfg["poll_interval"])` at each use site.

### Pattern E — `runtime.py` / `context.py` / `worker.py` misc narrowing (10 errors)

Individual fixes, all mechanical:

- `context.py:246` — `Path | None` to `Path`: add `assert path is not None` or
  raise `GTContextError` on None branch.
- `runtime.py:59` — `None` to `FastMCP[Any]`: change variable annotation to
  `FastMCP[Any] | None` and update downstream checks.
- `runtime.py:100` — `str | None` to `json.loads`: add None guard.
- `runtime.py:408` — `int | None` to `int()`: add None guard.
- `runtime.py:1036` — `str` to `Literal['codex', 'prime', 'owner', 'any']`:
  either change upstream param type or add a runtime validation + `cast()`.
- `worker.py:145-150` — `BufferedRandom | None` narrowing: same `TYPE_CHECKING`
  approach as Pattern A OR tighten the init branch.
- `worker.py:596` — `int()` on `object`: same as Pattern D, narrow at source.

## Out of Scope (Explicitly)

- Line-coverage improvements (51% → 70%). Will be Phase 4B.8.
- Whole-package docstring coverage (60% → 80%). Will be Phase 4B.9.
- Structured-logging migration (0 → bridge/db). Will be Phase 4C or later.
- Broad-exception-site review (3 "needs review" entries). Separate sub-round.
- Any runtime behavior change. If a test failure reveals that a proposed
  narrowing breaks an existing contract, the narrowing is reverted and the
  error is added to a targeted `# type: ignore[<code>]` with a TODO comment,
  not "fixed" by changing behavior.

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| A narrowing changes runtime behavior (raise vs silent skip) | Medium | Run full test suite after each file's fixes; any new failure → revert that narrowing and use `# type: ignore[<code>]` with TODO |
| `fcntl` pattern change breaks Unix runtime | Medium | Test suite covers the locking path; manual check that `worker.py` / `poller.py` still acquire locks on Linux CI |
| `Popen` kwargs refactor changes signal handling / env inheritance | Low | `cast(Any, kwargs)` preserves exact runtime kwargs; no signature change |
| Config dataclass refactor breaks existing `cfg["key"]` call sites elsewhere | Low | Grep for `cfg[` usages before/after; only proceed with dataclass if ≤ 3 external call sites |
| Merge conflicts with concurrent work on `bridge/poller.py` (high-touch file) | Medium | Rebase before pushing; coordinate with any in-flight poller repair work |

## Test Plan

1. **Per-file:** After each file's fixes, run:
   ```bash
   python -m mypy --strict src/groundtruth_kb/<file>
   python -m pytest tests/ -x --tb=short
   ```
   Both must return 0/pass before moving to the next file.

2. **End-to-end:** After all 5 files are clean:
   ```bash
   python -m mypy --strict src/groundtruth_kb/   # expect: Success: no issues found in 31 source files
   python -m pytest tests/ --cov=groundtruth_kb  # expect: 638 pass, coverage unchanged ±0.5pp
   python -m ruff check src/ tests/              # expect: clean
   python -m ruff format --check src/ tests/     # expect: clean
   ```

3. **CI regression gate update:** Modify
   `tests/test_public_api_type_checks.py` (added in 4B.4) to run
   `mypy --strict` against **the entire `src/groundtruth_kb/` tree**, not just
   the public API files, and assert exit code 0. This locks the count at 0
   permanently. The existing per-module CI step in 4B.5b's gate continues to
   run as a faster pre-check.

4. **Order of file fixes (least-risk first):**
   1. `bridge/context.py` (1 error) — smallest surface
   2. `intake.py` (7 errors) — all the same pattern
   3. `bridge/runtime.py` (4 errors) — misc narrowing
   4. `bridge/worker.py` (10 errors) — fcntl + Popen
   5. `bridge/poller.py` (17 errors) — fcntl + Popen + config dataclass (biggest blast radius, highest-touch file)

## Exit Criteria

All must be true:

1. `python -m mypy --strict src/groundtruth_kb/` → `Success: no issues found in 31 source files`
2. `python -m pytest tests/` → 638 passed, 0 failed
3. Coverage delta: ≤ ±0.5 percentage points vs. baseline (no new test code expected)
4. `tests/test_public_api_type_checks.py` extended to cover full tree, asserts exit 0
5. PR merged to `main` with green CI on all 9 matrix jobs
6. CHANGELOG entry under `[Unreleased]` → `### Fixed (internal — no runtime behavior change)`
7. No new `# type: ignore` comments added without an accompanying TODO referencing a future follow-up, and the total count of such comments added is ≤ 3

## Rollback

Single PR, squash-merged. Rollback = `git revert <merge-sha>` on `main`. No
data migration, no config change, no runtime behavior change, so rollback is
trivial and safe at any point post-merge.

## Estimated Effort

- Drafting + investigation: already done (this proposal)
- Implementation: ~3 hours focused work (each file is mechanical)
- Test iteration: ~1 hour (run suite after each file)
- CI gate update + CHANGELOG: ~30 min
- Proposal/review cycle overhead: ~30 min
- **Total: ~5 hours wall-clock**

## Open Decisions Requested From Codex

1. **Config dataclass vs. inline casts for Pattern D.** Dataclass is
   cleaner but touches more files; inline casts are cheaper but uglier.
   Recommendation: dataclass, but willing to switch on review.

2. **`TYPE_CHECKING` guard vs. runtime-only wrap for Pattern A (`fcntl`).**
   `TYPE_CHECKING` is more idiomatic and reads cleaner; runtime-only wrap
   avoids the two-world confusion but adds `# type: ignore[unreachable]` lines.
   Recommendation: `TYPE_CHECKING`.

3. **`tests/test_public_api_type_checks.py` rename.** If the test now covers
   the full tree, "public_api" is misleading. Rename to
   `test_full_tree_type_checks.py`? Recommendation: yes, rename during this PR.

4. **Should `intake.py` None-guards raise `GTIntakeError` or `ValueError`?**
   Current code uses `GTConfigError` for config issues. Consistent choice
   requested. Recommendation: `GTIntakeError` (new exception class in the
   module) for semantic clarity.

## Appendix A — Full Error List (verbatim)

```
src\groundtruth_kb\bridge\context.py:246: error: Incompatible types in assignment (expression has type "Path | None", variable has type "Path")  [assignment]
src\groundtruth_kb\bridge\runtime.py:59: error: Incompatible types in assignment (expression has type "None", variable has type "FastMCP[Any]")  [assignment]
src\groundtruth_kb\bridge\runtime.py:100: error: Argument 1 to "loads" has incompatible type "str | None"; expected "str | bytes | bytearray"  [arg-type]
src\groundtruth_kb\bridge\runtime.py:408: error: Argument 1 to "int" has incompatible type "int | None"; expected "str | Buffer | SupportsInt | SupportsIndex"  [arg-type]
src\groundtruth_kb\bridge\runtime.py:1036: error: Argument 3 to "_insert_message" has incompatible type "str"; expected "Literal['codex', 'prime', 'owner', 'any']"  [arg-type]
src\groundtruth_kb\intake.py:223: error: Value of type "dict[str, Any] | None" is not indexable  [index]
src\groundtruth_kb\intake.py:272: error: Value of type "dict[str, Any] | None" is not indexable  [index]
src\groundtruth_kb\intake.py:279: error: Value of type "dict[str, Any] | None" is not indexable  [index]
src\groundtruth_kb\intake.py:283: error: Value of type "dict[str, Any] | None" is not indexable  [index]
src\groundtruth_kb\intake.py:289: error: Value of type "dict[str, Any] | None" is not indexable  [index]
src\groundtruth_kb\intake.py:294: error: Value of type "dict[str, Any] | None" is not indexable  [index]
src\groundtruth_kb\intake.py:302: error: Value of type "dict[str, Any] | None" is not indexable  [index]
src\groundtruth_kb\bridge\worker.py:145: error: Incompatible types in assignment (expression has type "BufferedRandom", variable has type "None")  [assignment]
src\groundtruth_kb\bridge\worker.py:146: error: "None" has no attribute "seek"  [attr-defined]
src\groundtruth_kb\bridge\worker.py:148: error: "None" has no attribute "fileno"  [attr-defined]
src\groundtruth_kb\bridge\worker.py:150: error: Module has no attribute "flock"  [attr-defined]
src\groundtruth_kb\bridge\worker.py:150: error: "None" has no attribute "fileno"  [attr-defined]
src\groundtruth_kb\bridge\worker.py:150: error: Module has no attribute "LOCK_EX"  [attr-defined]
src\groundtruth_kb\bridge\worker.py:150: error: Module has no attribute "LOCK_NB"  [attr-defined]
src\groundtruth_kb\bridge\worker.py:250: error: No overload variant of "run" matches argument types "list[str]", "dict[str, object]"  [call-overload]
src\groundtruth_kb\bridge\worker.py:274: error: No overload variant of "run" matches argument types "list[str]", "dict[str, object]"  [call-overload]
src\groundtruth_kb\bridge\worker.py:596: error: No overload variant of "int" matches argument type "object"  [call-overload]
src\groundtruth_kb\bridge\poller.py:61: error: Incompatible types in assignment (expression has type "BufferedRandom", variable has type "None")  [assignment]
src\groundtruth_kb\bridge\poller.py:62: error: "None" has no attribute "seek"  [attr-defined]
src\groundtruth_kb\bridge\poller.py:65: error: "None" has no attribute "fileno"  [attr-defined]
src\groundtruth_kb\bridge\poller.py:67: error: Module has no attribute "flock"  [attr-defined]
src\groundtruth_kb\bridge\poller.py:67: error: "None" has no attribute "fileno"  [attr-defined]
src\groundtruth_kb\bridge\poller.py:67: error: Module has no attribute "LOCK_EX"  [attr-defined]
src\groundtruth_kb\bridge\poller.py:67: error: Module has no attribute "LOCK_NB"  [attr-defined]
src\groundtruth_kb\bridge\poller.py:69: error: "None" has no attribute "close"  [attr-defined]
src\groundtruth_kb\bridge\poller.py:167: error: No overload variant of "Popen" matches argument types "list[str]", "dict[str, object]"  [call-overload]
src\groundtruth_kb\bridge\poller.py:283: error: Unsupported operand types for + ("object" and "int")  [operator]
src\groundtruth_kb\bridge\poller.py:291: error: "object" has no attribute "append"  [attr-defined]
src\groundtruth_kb\bridge\poller.py:293: error: Argument 1 to "dedupe_preserve_order" has incompatible type "object"; expected "list[str]"  [arg-type]
src\groundtruth_kb\bridge\poller.py:338: error: Unsupported operand types for + ("object" and "int")  [operator]
src\groundtruth_kb\bridge\poller.py:341: error: Unsupported operand types for + ("object" and "int")  [operator]
src\groundtruth_kb\bridge\poller.py:349: error: Unsupported operand types for + ("object" and "int")  [operator]
src\groundtruth_kb\bridge\poller.py:368: error: Unsupported operand types for + ("object" and "int")  [operator]
src\groundtruth_kb\bridge\poller.py:372: error: Unsupported operand types for + ("object" and "int")  [operator]
```

(39 lines, matches `wc -l` output from the measurement command.)
