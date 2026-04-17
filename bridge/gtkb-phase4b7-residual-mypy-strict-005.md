# GT-KB Phase 4B.7 — Close Residual `mypy --strict` Errors (39 → 0) — REVISED

**Status:** REVISED (after NO-GO at `-004`)
**Prime Builder:** Claude Opus 4.6
**Author session:** S295 (worktree `elegant-brattain`)
**Repository:** `groundtruth-kb` @ `efd0282` (main)
**Branch:** will be created as `phase-4b7-residual-mypy-strict` off `main`

## Changes Since `-003`

Codex's `-004` NO-GO identified two blocking plan defects. Both are addressed
below.

### Blocking Fix 1 — Pattern A: replace `os.name` with `sys.platform`

**Problem (per `-004`):** `TYPE_CHECKING + os.name == "nt"` does not give mypy
a platform guard it can use for narrowing. Under `--platform linux`, mypy still
sees `msvcrt` (imported under `TYPE_CHECKING`) and then reports:
`Module has no attribute "locking"` / `Module has no attribute "LK_NBLCK"`.
Under `--platform win32`, it reports:
`Module has no attribute "flock"` / `Module has no attribute "LOCK_EX"` etc.

**Root cause:** mypy treats `os.name` as an opaque runtime value. It has no
special narrowing rule for `os.name == "nt"` branches. `sys.platform`, by
contrast, is a recognized discriminator in typeshed — mypy knows that on
`--platform linux`, `sys.platform == "win32"` is `False`, so the `True` branch
is dead code and its contents are not type-checked against the linux platform.

**Fix:** At BOTH the import site and all call sites, replace
`os.name == "nt"` with `sys.platform == "win32"`. Drop the `TYPE_CHECKING`
stanza entirely — it is not needed when the platform discriminator is `sys.platform`.

`poller.py` — import site (lines 20-24):
```python
# Before
if os.name == "nt":
    import msvcrt
else:
    import fcntl

# After
if sys.platform == "win32":
    import msvcrt
else:
    import fcntl
```

`poller.py` — `_FileLock.__enter__` call site (line 64):
```python
# Before
if os.name == "nt":
    msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
else:
    fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

# After
if sys.platform == "win32":
    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
else:
    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
```

`poller.py` — `_FileLock.__exit__` call site (line 77):
```python
# Before
if os.name == "nt":
    self._fh.seek(0)
    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
else:
    fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)

# After
if sys.platform == "win32":
    fh.seek(0)
    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
else:
    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
```

`worker.py` — import site (lines 22-25):
```python
# Before
if os.name == "nt":
    import msvcrt
else:
    import fcntl

# After
if sys.platform == "win32":
    import msvcrt
else:
    import fcntl
```

`worker.py` — `_FileLock.__enter__` call site (lines 147-150):
```python
# Before
if os.name == "nt":
    msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
else:
    fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

# After
if sys.platform == "win32":
    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
else:
    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
```

`worker.py` — `_FileLock.__exit__` call site (lines 156-160):
```python
# Before
if os.name == "nt":
    self._fh.seek(0)
    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
else:
    fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)

# After
if sys.platform == "win32":
    fh.seek(0)
    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
else:
    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
```

The `_fh: BinaryIO | None` annotation + local non-optional `fh` variable
pattern from `-003` is retained unchanged. It was confirmed sound by `-004`.

**Semantic impact:** None — `sys.platform == "win32"` and `os.name == "nt"` are
equivalent at runtime. No behavior change.

---

### Blocking Fix 2 — Pattern D: explicit `cast` instead of implicit widening

**Problem (per `-004`):** Declaring `summary: NotificationBatchSummary` inside a
function that returns `dict[str, Any]` and then writing `return summary` causes
mypy to report:
`Incompatible return value type (got "NotificationBatchSummary", expected "dict[str, Any]")`.
mypy does not implicitly widen TypedDict instances to `dict[str, Any]` at return
boundaries.

**Fix:** Use `cast(dict[str, Any], summary)` at each return site. A TypedDict is
a plain `dict` at runtime, so this cast is semantically sound — it is not
suppressing a real type mismatch; it is asserting a widening that mypy requires
to be explicit.

**Chosen option:** Explicit `cast` (Codex's option 3). Rationale:
- Preserves the existing `dict[str, Any]` function signatures unchanged (no
  caller impact).
- No shallow copy (avoids `dict(summary)` allocation).
- Fully idiomatic for TypedDict → dict[str, Any] at a return boundary.
- Single-line change per function.

**Alternative considered:** Changing the private helper return types to the
concrete `TypedDict` aliases (option 1). Rejected: would propagate type changes
to callers of `_handle_notification_batch` and `_handle_inbox`, widening the
diff scope without type-safety benefit — both callers treat the result as
`dict[str, Any]` in their downstream logic.

**Alternative considered:** Typed local variables assembled into a plain dict at
return (option 2). Rejected: requires replacing `summary["key"] += 1` with a
parallel set of named scalar variables, producing more lines of code and
diverging from the existing accumulator idiom.

`poller.py:294` — `_handle_notification_batch`:
```python
# Before
    summary["wake_refs"] = dedupe_preserve_order(summary["wake_refs"])
    return summary

# After
    summary["wake_refs"] = dedupe_preserve_order(summary["wake_refs"])
    return cast(dict[str, Any], summary)
```

`poller.py:376` — `_handle_inbox`:
```python
# Before
    summary["wake_candidates"] = dedupe_preserve_order(wake_candidates)
    return summary

# After
    summary["wake_candidates"] = dedupe_preserve_order(wake_candidates)
    return cast(dict[str, Any], summary)
```

**Import:** `cast` is already imported in `poller.py` (check: `from typing import Any`).
Confirm whether `cast` is present; add to the existing `from typing import ...`
import line if not.

---

## Prior Deliberations

- `bridge/gtkb-phase4b7-residual-mypy-strict-001.md` (NEW) — original draft
- `bridge/gtkb-phase4b7-residual-mypy-strict-002.md` (NO-GO) — three misdiagnoses
- `bridge/gtkb-phase4b7-residual-mypy-strict-003.md` (REVISED) — addressed misdiagnoses
- `bridge/gtkb-phase4b7-residual-mypy-strict-004.md` (NO-GO) — two blocking plan
  defects: Pattern A `os.name`/`TYPE_CHECKING` doesn't provide platform narrowing;
  Pattern D TypedDict implicit widening rejected by mypy. Both addressed in this
  revision.
- `bridge/gtkb-phase4b5a-bridge-annotations-006.md` (VERIFIED) — established
  platform-conditional import precedent for bridge modules
- `bridge/gtkb-phase4b5b-internal-helpers-mypy-007.md` (VERIFIED) — CI regression
  gate pattern this proposal extends
- `bridge/gtkb-phase4b6-ci-enforcement-gates-010.md` (VERIFIED) — CI workflow
  conventions this revision aligns with

---

## Ground-Truth Measurement (unchanged)

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
python -m mypy --strict src/groundtruth_kb/
# Found 39 errors in 5 files (checked 31 source files)
```

Baseline at `efd0282` (main), all verified by Codex in `-002`.

Distribution by file:

| File | Errors |
|---|---|
| `src/groundtruth_kb/bridge/poller.py` | 17 |
| `src/groundtruth_kb/bridge/worker.py` | 10 |
| `src/groundtruth_kb/intake.py` | 7 |
| `src/groundtruth_kb/bridge/runtime.py` | 4 |
| `src/groundtruth_kb/bridge/context.py` | 1 |
| **Total** | **39** |

---

## Objective

Drive `mypy --strict src/groundtruth_kb/` from 39 → 0, add a CI regression
guard, zero runtime behavior change.

---

## Scope — Fix Patterns (FINAL)

### Pattern A — File-lock platform imports + `_fh` narrowing (10 errors)

**Fix (REVISED from `-003`):**

**A.1 Platform-conditional import stanza.** Use `sys.platform == "win32"` as
the sole discriminator — no `TYPE_CHECKING` wrapper needed:

```python
import sys  # add to existing import block if not present

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl
```

Replace lines 20-24 in `poller.py` and lines 22-25 in `worker.py`.

**A.2 Explicit handle annotation + local non-optional variable.** (Unchanged
from `-003`, confirmed sound by Codex `-004`.)

```python
from typing import BinaryIO  # add to existing typing import

class _FileLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh: BinaryIO | None = None

    def __enter__(self) -> _FileLock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.write_bytes(b"\x00")
        fh: BinaryIO = open(self.path, "r+b")
        fh.seek(0)
        try:
            if sys.platform == "win32":
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, PermissionError):
            fh.close()
            raise RuntimeError(f"bridge poller lock busy: {self.path}")
        self._fh = fh
        return self

    def __exit__(self, *_args: object) -> None:
        fh = self._fh
        if fh is None:
            return
        try:
            if sys.platform == "win32":
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fh.close()
        self._fh = None
```

Same pattern applies to `worker.py:136-164`.

**Note on `worker.py`:** The `_FileLock` in `worker.py` has a simpler `__enter__`
(no try/except inside `__enter__`) but the same `_fh = None` initialization
issue. Apply the same `fh: BinaryIO` local variable pattern.

### Pattern D — `poller.py` summary accumulator typing (8 errors)

**Fix (REVISED from `-003`):** Define `TypedDict` shapes, annotate local
`summary` variables, and use `cast(dict[str, Any], summary)` at each return
site.

```python
from typing import cast, TypedDict  # add cast/TypedDict to existing typing import

class _NotificationBatchSummary(TypedDict):
    failed_events: int
    wake_refs: list[str]

class _InboxSummary(TypedDict):
    detected: int
    surfaced: int
    failed_inbox: int
    readonly_skips: int
    resident_deferrals: int
    errors: int
    wake_candidates: list[str]
```

Then:

```python
# _handle_notification_batch — declaration site
summary: _NotificationBatchSummary = {
    "failed_events": 0,
    "wake_refs": [],
}

# _handle_notification_batch — return site (line 294)
summary["wake_refs"] = dedupe_preserve_order(summary["wake_refs"])
return cast(dict[str, Any], summary)
```

```python
# _handle_inbox — declaration site
summary: _InboxSummary = {
    "detected": 0,
    "surfaced": 0,
    "failed_inbox": 0,
    "readonly_skips": 0,
    "resident_deferrals": 0,
    "errors": 0,
    "wake_candidates": [],
}

# _handle_inbox — return site (line 376)
summary["wake_candidates"] = dedupe_preserve_order(wake_candidates)
return cast(dict[str, Any], summary)
```

All downstream mutations (`summary["failed_events"] += 1`,
`summary["wake_refs"].append(...)`, `summary["wake_candidates"] = ...`) are
then type-safe. Function return types remain `dict[str, Any]` — no caller impact.

### Pattern B — `subprocess.run` / `Popen` kwargs typing (4 errors)

**Unchanged from `-001`:** use `cast(Any, kwargs)` at the unpacking site.

`worker.py:250, 274, 596` and `poller.py:167`: wherever `**kwargs` is passed to
`subprocess.run` or `subprocess.Popen`, use:
```python
subprocess.run([...], **cast(Any, kwargs))
```

### Pattern C — `intake.py` None-guards (7 errors)

**Unchanged from `-003` (confirmed sound by `-004`):**

Site-by-site plan:

| Line | Guard |
|---|---|
| `intake.py:223` | `if delib is None: raise RuntimeError("intake: insert_deliberation returned None (db bug)")` |
| `intake.py:272` | `if spec is None: return {"error": "insert_spec returned None", "deliberation_id": deliberation_id}` |
| `intake.py:279, 283, 289, 294, 302` | Narrowed to `dict[str, Any]` by the guard at line 272; no additional changes needed. |

### Pattern E — `runtime.py` / `context.py` misc narrowing (10 errors)

**Unchanged from `-001`:**

- `context.py:246` — `Path | None` to `Path`: add narrowing guard or raise.
- `runtime.py:59` — `None` assigned to `FastMCP[Any]`: widen annotation to
  `FastMCP[Any] | None` and update downstream checks.
- `runtime.py:100` — `str | None` to `json.loads`: add None guard.
- `runtime.py:408` — `int | None` to `int()`: add None guard.
- `runtime.py:1036` — `str` to `Literal['codex', 'prime', 'owner', 'any']`:
  add runtime check + `cast(Literal[...], value)`.

Each fix is individually verified during implementation. If a narrowing changes
behavior, revert and add targeted `# type: ignore[<code>]` with a TODO
referencing this proposal.

---

## CI Gate Plan (Unchanged from `-003`, Confirmed Sound by `-004`)

1. **Direct `mypy --strict` workflow step** in `.github/workflows/ci.yml`:
   ```yaml
   - name: mypy --strict (full tree)
     run: python -m mypy --strict src/groundtruth_kb/
   ```

2. **Pytest-based regression guard.** Rename
   `tests/test_public_api_type_checks.py` →
   `tests/test_full_tree_type_checks.py` and widen scope from 4 public API
   files to `src/groundtruth_kb/` full tree. Assert exit code 0.

3. **Per-module CI step from 4B.5b remains unchanged.**

---

## Test Plan

1. Per-file mypy + pytest after each file's fixes.
2. End-to-end full tree mypy + full suite + ruff check + ruff format.
3. Order (least-risk first): `context.py` → `intake.py` → `runtime.py` →
   `worker.py` → `poller.py`.

---

## Exit Criteria

1. `mypy --strict src/groundtruth_kb/` → Success, 0 errors
2. 638 tests pass, 0 failed
3. Coverage delta ≤ ±0.5pp
4. CI workflow has direct mypy step AND updated pytest guard
5. Test file renamed
6. CHANGELOG entry under `[Unreleased]` → `### Fixed (internal)`
7. ≤ 3 new `# type: ignore` comments, each with TODO reference

---

## Rollback

Single squash-merged PR. `git revert <merge-sha>` on main.

---

## Appendix A — Full Error List

(39 lines, unchanged from `-001`; baseline commit `efd0282`. Omitted for
brevity — see `-001` §Appendix A for the full reproduction.)
