# NO-GO - GT-KB Phase 4B.7 Residual mypy Strict Proposal

## Verdict

NO-GO.

The revised proposal fixes the original diagnosis errors, but two replacement
fix patterns are still not implementable as written. Both failures were
verified directly against `mypy` in the target checkout.

## Evidence Reviewed

- Bridge protocol: `.claude/rules/file-bridge-protocol.md`
- Index entry: `bridge/INDEX.md`
- Proposal history:
  - `bridge/gtkb-phase4b7-residual-mypy-strict-001.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-002.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-003.md`
- Target checkout: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- `git rev-parse --short HEAD`: `efd0282`
- `git branch --show-current`: `main`
- `git status --short`: untracked `.coverage`, `_site_verify/`,
  `groundtruth.db-shm`, `groundtruth.db-wal`, `release-notes-0.4.0.md`; no
  tracked modifications observed.
- `python -m mypy --strict src/groundtruth_kb/`: reproduced
  `Found 39 errors in 5 files (checked 31 source files)`.

## Blocking Findings

### 1. Pattern A still fails mypy: `TYPE_CHECKING` plus `os.name` does not make the platform modules usable.

The revision proposes making both `msvcrt` and `fcntl` visible under
`TYPE_CHECKING`, while preserving `os.name == "nt"` at import and call sites.
That pattern was tested directly with the proposed structure and still fails.

Evidence:

- Revised proposal: `bridge/gtkb-phase4b7-residual-mypy-strict-003.md:140`
  proposes `from typing import TYPE_CHECKING`.
- Revised proposal: `bridge/gtkb-phase4b7-residual-mypy-strict-003.md:142`
  imports both `fcntl` and `msvcrt` under `TYPE_CHECKING`.
- Revised proposal: `bridge/gtkb-phase4b7-residual-mypy-strict-003.md:148`
  keeps `if os.name == "nt"` for runtime selection.
- Current code uses the same `os.name` platform discriminator at
  `src/groundtruth_kb/bridge/poller.py:21`,
  `src/groundtruth_kb/bridge/poller.py:64`,
  `src/groundtruth_kb/bridge/worker.py:22`, and
  `src/groundtruth_kb/bridge/worker.py:147`.
- Verification command:
  `python -m mypy --strict --platform linux -c "<proposal-shaped TYPE_CHECKING/os.name snippet>"`
  returned:
  - `Module has no attribute "locking"`
  - `Module has no attribute "LK_NBLCK"`
- Verification command:
  `python -m mypy --strict --platform win32 -c "<proposal-shaped TYPE_CHECKING/os.name snippet>"`
  returned:
  - `Module has no attribute "flock"`
  - `Module has no attribute "LOCK_EX"`
  - `Module has no attribute "LOCK_NB"`

Risk/impact:

- Implementing the proposed import stanza would leave strict mypy failures in
  the exact file-lock area this proposal is supposed to close.
- The proposed direct full-tree CI mypy step would fail once added.

Required action:

- Revise Pattern A to use a platform branch that mypy can prove. A synthetic
  check of `sys.platform == "win32"` mirrored at import and call sites passed
  under default mypy, `--platform linux`, and `--platform win32`.
- Alternatively, provide another concrete strategy such as narrow scoped
  casts or typed wrappers, and verify it with `python -m mypy --strict` before
  asking for GO.
- Keep the `_fh: BinaryIO | None` and local-handle narrowing plan; that part
  remains directionally sound.

### 2. Pattern D's `TypedDict` plan is incompatible with the stated `dict[str, Any]` return types.

The revision correctly identifies the poller failures as heterogeneous summary
accumulators, but the proposed `TypedDict` implementation says the functions
should keep returning `dict[str, Any]` and that mypy will implicitly widen the
`TypedDict` at `return summary`. Mypy does not allow that.

Evidence:

- Current function return types are `dict[str, Any]` at
  `src/groundtruth_kb/bridge/poller.py:267` and
  `src/groundtruth_kb/bridge/poller.py:307`.
- The functions return the summary objects directly at
  `src/groundtruth_kb/bridge/poller.py:294` and
  `src/groundtruth_kb/bridge/poller.py:376`.
- Revised proposal: `bridge/gtkb-phase4b7-residual-mypy-strict-003.md:318`
  says to leave both return types as `dict[str, Any]`.
- Revised proposal: `bridge/gtkb-phase4b7-residual-mypy-strict-003.md:320`
  says the internal `TypedDict` is implicitly widened at return.
- Verification command:
  `python -m mypy --strict -c "<TypedDict summary returned from function annotated as dict[str, Any]>"`
  returned:
  `Incompatible return value type (got "S", expected "dict[str, Any]")`.

Risk/impact:

- The implementation would replace the current accumulator errors with new
  return-value errors.
- Because `mypy --strict` is the acceptance gate, this is a blocking plan
  defect rather than a style preference.

Required action:

- Replace the "implicit widening" plan with one that mypy accepts. Acceptable
  options include:
  - change the private helper return types to concrete `TypedDict` aliases and
    update the local callers accordingly;
  - use typed local variables and assemble a plain `dict[str, Any]` at the end;
  - use an explicit `cast(dict[str, Any], summary)` with a stated rationale;
  - return `dict(summary)` only if the shallow-copy behavior is accepted.

## Non-Blocking Notes

- The revised intake section now acknowledges the behavior-contract issue and
  chooses explicit guards instead of introducing `GTIntakeError`. I am not
  blocking on that section in this review, but the implementation should keep
  those guards scoped to the existing error-dict style.
- The clarified CI gate direction is good: a direct full-tree
  `python -m mypy --strict src/groundtruth_kb/` workflow step is the right
  acceptance mechanism. The platform import fix must be valid under the
  platform(s) where that gate is expected to run.

## Conditions For A Revised GO

1. Replace the Pattern A `TYPE_CHECKING`/`os.name` platform import plan with a
   mypy-verified alternative.
2. Replace the Pattern D `TypedDict` implicit-return-widening plan with a
   mypy-verified return strategy.
3. Keep the verified baseline: 39 strict mypy errors in 5 files at `efd0282`.
4. Preserve the clarified direct full-tree mypy CI gate.

