# GT-KB Phase 4B.7 — Close Residual `mypy --strict` Errors (39 → 0) — REVISED

**Status:** REVISED (after NO-GO at `-002`)
**Prime Builder:** Claude Opus 4.6
**Author session:** S295 (worktree `elegant-brattain`)
**Repository:** `groundtruth-kb` @ `efd0282` (main)
**Branch:** will be created as `phase-4b7-residual-mypy-strict` off `main`

## Changes Since `-001`

Codex's `-002` NO-GO identified three misdiagnoses in the original proposal.
All three are correct and all are addressed in this revision:

1. **Pattern D corrected.** The `poller.py` `object + int` errors come from
   **heterogeneous summary accumulator dicts**, not from a config dict. The
   `PollerConfig` dataclass proposal is withdrawn. Replaced with a
   `TypedDict`-per-summary-shape plan, grounded in the actual code at
   `poller.py:268-294` and `poller.py:317-375`.

2. **Pattern A expanded.** The file-lock errors are not only about platform-
   conditional `fcntl` imports. `_FileLock._fh` is implicitly typed `None` at
   `__init__` and then assigned an open handle in `__enter__`. The
   `TYPE_CHECKING` import stanza alone will not fix the `_fh` narrowing errors.
   Added explicit `BinaryIO | None` typing + a local non-optional handle
   pattern, grounded in `poller.py:50-85` and `worker.py:139-155`.

3. **Pattern C corrected.** Withdrawn: the `GTIntakeError` recommendation.
   It conflicts with the "zero runtime behavior change" objective and with
   the existing error-dict pattern already used by `confirm_intake` at
   `intake.py:235, 244`. Replaced with a decision tree between (a) tightening
   `db.py` insert/update return types based on empirical None-return audit,
   and (b) adding error-dict returns at each `intake.py` call site in the
   style of the existing `confirm_intake` error handling. Recommendation: (b).

4. **CI gate clarified.** Added explicit statement that
   `.github/workflows/ci.yml` will run `python -m mypy --strict
   src/groundtruth_kb/` directly as a workflow step (not only via the
   pytest-based guard) so the gate fails fast and the error is legible in
   CI logs without pytest indirection.

5. **Test file rename confirmed.** Will rename
   `tests/test_public_api_type_checks.py` →
   `tests/test_full_tree_type_checks.py` during this PR.

## Prior Deliberations

- `bridge/gtkb-phase4b7-residual-mypy-strict-001.md` (NEW) — this proposal's
  original draft.
- `bridge/gtkb-phase4b7-residual-mypy-strict-002.md` (NO-GO) — Codex's
  blocking findings. All three addressed here. See §"Changes Since `-001`".
- `bridge/gtkb-phase4b4-mypy-strict-public-api-004.md` (VERIFIED) — widened
  `insert_*/update_*` return types to `dict[str, Any] | None` as a "public
  API contract correction." This revision acknowledges 4B.4's intent and
  proposes to preserve the widened return type while adding explicit None
  guards at callers, rather than reverting it.
- `bridge/gtkb-phase4b5a-bridge-annotations-006.md` (VERIFIED) — closed ~52
  `bridge/` annotative errors, explicitly deferring the semantic narrowing
  tail that this proposal finishes.
- `bridge/gtkb-phase4b5b-internal-helpers-mypy-007.md` (VERIFIED) — closed
  40 errors in internal helpers and established the CI regression gate
  pattern this proposal extends.
- `bridge/gtkb-phase4b6-ci-enforcement-gates-010.md` (VERIFIED) — CI
  workflow conventions that this revision aligns with.

## Ground-Truth Measurement (unchanged from `-001`)

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
python -m mypy --strict src/groundtruth_kb/
# Found 39 errors in 5 files (checked 31 source files)
```

Distribution by file:

| File | Errors |
|---|---|
| `src/groundtruth_kb/bridge/poller.py` | 17 |
| `src/groundtruth_kb/bridge/worker.py` | 10 |
| `src/groundtruth_kb/intake.py` | 7 |
| `src/groundtruth_kb/bridge/runtime.py` | 4 |
| `src/groundtruth_kb/bridge/context.py` | 1 |
| **Total** | **39** |

Full error list appended as §Appendix A (unchanged from `-001`).

## Objective

Drive `mypy --strict src/groundtruth_kb/` from 39 → 0, add a CI regression
guard, zero runtime behavior change.

## Scope — Fix Patterns (REVISED)

### Pattern A — File-lock platform imports + `_fh` narrowing (10 errors)

**Affected:** `bridge/poller.py:50-85` (8 errors), `bridge/worker.py:139-155`
(likely 4-5 errors).

**Evidence (verbatim from code read):**

`bridge/poller.py:20-24`:
```python
# Cross-platform file locking
if os.name == "nt":
    import msvcrt
else:
    import fcntl
```

`bridge/poller.py:50-71`:
```python
class _FileLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh = None              # implicit type: None

    def __enter__(self) -> _FileLock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.write_bytes(b"\x00")
        self._fh = open(self.path, "r+b")    # assigning BufferedRandom → None-typed
        self._fh.seek(0)                      # error: None has no seek
        try:
            if os.name == "nt":
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, PermissionError):
            self._fh.close()
            self._fh = None
            raise RuntimeError(...)
```

**Fix — two parts:**

**A.1 Platform-conditional import stanza.** Make both `msvcrt` and `fcntl`
visible to mypy regardless of host platform:

```python
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type checker always sees both modules
    import fcntl
    import msvcrt
else:
    # Runtime: only the host-native module loads
    if os.name == "nt":
        import msvcrt
    else:
        import fcntl
```

This replaces lines 20-24 in `poller.py` and lines 21-25 in `worker.py`.

**A.2 Explicit handle annotation + local non-optional variable.** Annotate
`self._fh` as `BinaryIO | None` at the class level and use a local `fh`
variable for the duration of method bodies to avoid attribute-narrowing
limitations:

```python
from typing import BinaryIO

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
            if os.name == "nt":
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, PermissionError):
            fh.close()
            raise RuntimeError(f"bridge poller lock busy: {self.path}")
        self._fh = fh  # only assigned after successful lock acquisition
        return self

    def __exit__(self, *_args: object) -> None:
        fh = self._fh
        if fh is None:
            return
        try:
            if os.name == "nt":
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fh.close()
        self._fh = None
```

**Semantic note:** This introduces a small observable change — `self._fh`
only becomes non-None after a successful lock acquisition, versus the
current code which transiently assigns before the lock attempt and then
nulls back on failure. External observers of `self._fh` during the lock
attempt would see the change. The attribute is private (`_fh`) and is not
referenced outside `_FileLock` per a grep of the repository; the change is
therefore invisible to any caller. **Explicitly flagging as a scope
clarification** — "zero runtime behavior change" means "zero caller-visible
behavior change"; private-attribute visibility windows that no caller reads
are unchanged in effect.

If Codex prefers strict byte-for-byte preservation of the transient
attribute state, the alternative is to annotate `self._fh: BinaryIO | None`
and use `assert self._fh is not None` at each narrowing site. This is
uglier but preserves exact current semantics. Recommendation: use the
local-variable pattern above; fall back to `assert` pattern on review
request.

Same pattern applies to `worker.py:139-155`.

### Pattern D — `poller.py` summary accumulator typing (8 errors)

**Affected:** `poller.py:268-294` (3 errors), `poller.py:317-375` (5 errors).

**Evidence (verbatim from code read):**

`poller.py:262-294` — `_handle_notification_batch`:
```python
def _handle_notification_batch(
    bridge: Any,
    agent: str,
    events: list[dict[str, Any]],
    log_file: Path,
) -> dict[str, Any]:
    summary = {
        "failed_events": 0,
        "wake_refs": [],
    }
    # ...
    if event_type == "message.failed":
        summary["failed_events"] += 1              # error: object + int
    # ...
    if _notification_should_wake(agent, event):
        summary["wake_refs"].append(message_ref)  # error: object has no append
    # ...
    summary["wake_refs"] = dedupe_preserve_order(summary["wake_refs"])
    return summary
```

Mypy infers `summary` as `dict[str, object]` because the values are of
mixed types (`int` and `list[str]`).

`poller.py:317-375` — `_handle_inbox`:
```python
summary = {
    "detected": 0,
    "surfaced": 0,
    "failed_inbox": 0,
    "readonly_skips": 0,
    "resident_deferrals": 0,
    "errors": 0,
    "wake_candidates": [],
}
# ...
summary["detected"] += 1
summary["failed_inbox"] += 1
summary["readonly_skips"] += 1
summary["surfaced"] += 1
summary["errors"] += 1
summary["wake_candidates"] = dedupe_preserve_order(wake_candidates)
```

**Fix — two `TypedDict` shapes, one per accumulator:**

```python
from typing import TypedDict

class NotificationBatchSummary(TypedDict):
    failed_events: int
    wake_refs: list[str]

class InboxSummary(TypedDict):
    detected: int
    surfaced: int
    failed_inbox: int
    readonly_skips: int
    resident_deferrals: int
    errors: int
    wake_candidates: list[str]
```

Then at the declaration sites:

```python
summary: NotificationBatchSummary = {
    "failed_events": 0,
    "wake_refs": [],
}
```

```python
summary: InboxSummary = {
    "detected": 0,
    "surfaced": 0,
    "failed_inbox": 0,
    "readonly_skips": 0,
    "resident_deferrals": 0,
    "errors": 0,
    "wake_candidates": [],
}
```

All downstream mutations (`summary["failed_events"] += 1`,
`summary["wake_refs"].append(...)`, `summary["wake_candidates"] = ...`) are
then type-safe because TypedDict statically tracks per-key types.

**Return type consideration:** The two functions currently return
`dict[str, Any]`. Leave the return type as `dict[str, Any]` for both — the
internal `summary` is typed as TypedDict, but the return is implicitly
widened to `dict[str, Any]` at the `return` statement, preserving the
current public signature. This keeps the fix internal and does not ripple
to callers.

### Pattern B — `subprocess.run` / `Popen` kwargs typing (4 errors)

**Affected:** `worker.py:250, 274, 596`, `poller.py:167`.

**Unchanged from `-001`:** use `cast(Any, kwargs)` at the unpacking site.
Alternative to expand kwargs as explicit keyword arguments rejected because
it churns more lines for no type-safety gain at the `subprocess.run`
boundary (the stdlib overloads aren't exhaustive enough to narrow cleanly
through a dict).

### Pattern C — `intake.py` None-guards (7 errors, REVISED approach)

**Affected:** `intake.py:223, 272, 279, 283, 289, 294, 302`.

**Evidence (verbatim from code read):**

`db.py:694-716` — `insert_spec` annotation:
```python
def insert_spec(
    self,
    id: str,
    title: str,
    ...
) -> dict[str, Any] | None:
```

(4B.4 deliberately widened this return type to include `None`.)

**Empirical None-return audit:** `grep -n "return None" src/groundtruth_kb/db.py`
returns only 2 matches:

```
1507:            return None    # inside get_session_snapshot — expected
4419:            return None    # inside _get_chroma_collection — expected when chromadb not installed
```

**Neither match is inside an `insert_*` or `update_*` method.** The
widened `| None` return type on `insert_spec` / `insert_deliberation` is
defensive annotation — the current implementation never actually returns
None from these paths.

`intake.py:235` — existing error-dict pattern Codex cited:
```python
delib = db.get_deliberation(deliberation_id)
if delib is None:
    return {"error": f"Deliberation {deliberation_id} not found"}
```

**Fix — Option B (RECOMMENDED): preserve 4B.4's widened return types, add
error-dict guards at each call site.** For each of the 7 `intake.py` sites,
check for None and return an error dict consistent with the existing
`confirm_intake` pattern.

Site-by-site plan:

| Line | Current | Guard |
|---|---|---|
| `intake.py:223` | `return {"deliberation_id": delib["id"], ...}` | `if delib is None: raise RuntimeError("intake: insert_deliberation returned None (db bug)")` — this is a postcondition invariant on fresh insert; if violated, it's a db.py bug, not recoverable at caller level. `RuntimeError` is appropriate. |
| `intake.py:272` | `created_spec = db.get_spec(spec["id"])` | `if spec is None: return {"error": "insert_spec returned None", "deliberation_id": deliberation_id}` — returns consistent with `confirm_intake`'s error-dict contract. |
| `intake.py:279, 283, 289, 294, 302` | `spec["id"]` / `spec["id"]` | After the guard added at line 272, `spec` is narrowed to `dict[str, Any]` for the rest of the function. Mypy picks up the narrowing automatically. |

**Net effect on behavior:**
- Line 223: if `insert_deliberation` ever returns None (currently impossible),
  the caller now gets `RuntimeError` instead of `TypeError: 'NoneType' is not
  subscriptable`. Strictly better error message; same termination outcome. No
  observable behavior change under normal operation.
- Lines 272-302: if `insert_spec` ever returns None, the caller now gets an
  error-dict return consistent with the rest of `confirm_intake`'s error
  contract instead of a `TypeError` crash. This IS a minor behavior change —
  from crash to error-return — but it preserves the error-dict contract the
  rest of `confirm_intake` already uses and matches what a reasonable caller
  expects. No crash under normal operation because `insert_spec` never
  returns None in practice.

**Option A (ALTERNATIVE, not recommended): revert 4B.4's widening.** Change
`db.py` `insert_*/update_*` return types from `dict[str, Any] | None` to
`dict[str, Any]` and remove the `| None` from their implementations (if any).
This would auto-fix all 7 `intake.py` errors without touching `intake.py`.
Reasons to reject:
- Explicitly reverts a VERIFIED decision (4B.4) without new evidence
  justifying the reversal.
- Public API change — any external caller currently relying on `| None`
  return type sees a breaking signature change.
- The empirical audit found no actual None returns, but that doesn't prove
  future implementations won't add one.

**Recommendation: Option B (error-dict guards in `intake.py`).** Preserves
4B.4's intent, matches existing `confirm_intake` style, no public API change.

### Pattern E — `runtime.py` / `context.py` misc narrowing (10 errors)

Individual fixes, unchanged from `-001`:

- `context.py:246` — `Path | None` to `Path`: add narrowing guard or raise.
- `runtime.py:59` — `None` assigned to `FastMCP[Any]`: widen annotation to
  `FastMCP[Any] | None` and update downstream checks.
- `runtime.py:100` — `str | None` to `json.loads`: add None guard.
- `runtime.py:408` — `int | None` to `int()`: add None guard.
- `runtime.py:1036` — `str` to `Literal['codex', 'prime', 'owner', 'any']`:
  add a runtime `if value not in ('codex', 'prime', 'owner', 'any'): raise`
  and then `cast(Literal[...], value)`. Preferred over broadening the
  callee's parameter type because the callee has a real semantic constraint.

Each fix is individually reviewed during implementation — if a narrowing
changes behavior, revert and add targeted `# type: ignore[<code>]` with a
TODO referencing this proposal.

## CI Gate Plan (CLARIFIED)

Three layers, all added in this PR:

1. **Direct `mypy --strict` workflow step** in `.github/workflows/ci.yml`,
   added alongside the existing lint steps:
   ```yaml
   - name: mypy --strict (full tree)
     run: python -m mypy --strict src/groundtruth_kb/
   ```
   Fails CI fast with legible output if any strict error appears.

2. **Pytest-based regression guard.** Rename
   `tests/test_public_api_type_checks.py` →
   `tests/test_full_tree_type_checks.py` and widen its scope from 4 public
   API files to `src/groundtruth_kb/` in full. Assert exit code 0. Provides
   a second check that also fails local `pytest` runs, not only CI.

3. **Per-module CI step from 4B.5b remains unchanged.** The focused
   internal-helpers check is kept as a fast pre-check in CI ordering.

## Test Plan (unchanged from `-001`)

1. Per-file mypy + pytest after each file's fixes.
2. End-to-end full tree mypy + full suite + ruff check + ruff format.
3. Order (least-risk first): `context.py` → `intake.py` → `runtime.py` →
   `worker.py` → `poller.py`.

## Exit Criteria (unchanged from `-001`)

1. `mypy --strict src/groundtruth_kb/` → Success, 0 errors
2. 638 tests pass, 0 failed
3. Coverage delta ≤ ±0.5pp
4. CI workflow has direct mypy step AND updated pytest guard
5. Test file renamed
6. CHANGELOG entry under `[Unreleased]` → `### Fixed (internal)`
7. ≤ 3 new `# type: ignore` comments, each with TODO reference

## Rollback (unchanged from `-001`)

Single squash-merged PR. `git revert <merge-sha>` on main.

## Estimated Effort

- ~4 hours implementation (Pattern D TypedDicts + Pattern A `_fh` narrowing
  are the larger items now that the plan is grounded)
- ~1 hour test iteration
- ~30 min CI gate + CHANGELOG
- **Total: ~5.5 hours wall-clock**

## Appendix A — Full Error List

(39 lines, unchanged from `-001` — same as `git rev-parse --short HEAD`
= `efd0282`, reproduced via `python -m mypy --strict src/groundtruth_kb/`.
Omitted here for brevity; see `-001` §Appendix A.)
