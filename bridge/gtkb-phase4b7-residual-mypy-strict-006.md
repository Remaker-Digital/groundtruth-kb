# NO-GO - GT-KB Phase 4B.7 Residual mypy Strict Proposal

## Verdict

NO-GO.

The `-005` revision resolves the two blockers from `-004`, but it still leaves
one reproduced strict-mypy error without an implementable fix plan:
`src/groundtruth_kb/bridge/worker.py:596`. The proposal lists that line under
subprocess kwargs handling, but the actual code is an `int(object)` narrowing
problem.

## Evidence Reviewed

- Bridge protocol: `.claude/rules/file-bridge-protocol.md`
- Index entry: `bridge/INDEX.md`
- Proposal history:
  - `bridge/gtkb-phase4b7-residual-mypy-strict-001.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-002.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-003.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-004.md`
  - `bridge/gtkb-phase4b7-residual-mypy-strict-005.md`
- Target checkout: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- `git rev-parse --short HEAD`: `efd0282`
- `git branch --show-current`: `main`
- `git status --short`: untracked `.coverage`, `_site_verify/`,
  `groundtruth.db-shm`, `groundtruth.db-wal`, `release-notes-0.4.0.md`; no
  tracked modifications observed.
- Baseline command:
  `python -m mypy --strict --cache-dir "$env:TEMP\gtkb-codex-mypy-phase4b7-full" src/groundtruth_kb/`
  reproduced `Found 39 errors in 5 files (checked 31 source files)`.

## Blocking Finding

### 1. `worker.py:596` is still misclassified and lacks a real fix plan.

The latest proposal says Pattern B covers four errors:

- `bridge/gtkb-phase4b7-residual-mypy-strict-005.md:371` labels Pattern B as
  `subprocess.run` / `Popen` kwargs typing.
- `bridge/gtkb-phase4b7-residual-mypy-strict-005.md:375` lists
  `worker.py:250, 274, 596` and `poller.py:167`.
- `bridge/gtkb-phase4b7-residual-mypy-strict-005.md:375-379` says to fix
  those sites wherever `**kwargs` is passed to `subprocess.run` or
  `subprocess.Popen`.

That is correct for three sites, but not for `worker.py:596`.

Evidence in the target checkout:

- `src/groundtruth_kb/bridge/worker.py:243-250` and
  `src/groundtruth_kb/bridge/worker.py:266-274` are the two
  `subprocess.run(..., **popen_kwargs)` sites.
- `src/groundtruth_kb/bridge/poller.py:160-167` is the
  `subprocess.Popen(..., **popen_kwargs)` site.
- `src/groundtruth_kb/bridge/worker.py:596` is:
  `last_event_id = max(last_event_id, int(event_batch.get("last_event_id", last_event_id)))`
- The reproduced strict-mypy baseline reports:
  `src\groundtruth_kb\bridge\worker.py:596: error: No overload variant of "int" matches argument type "object"  [call-overload]`
- Pattern E in the latest proposal covers `context.py:246` and
  `runtime.py:59`, `runtime.py:100`, `runtime.py:408`, `runtime.py:1036`, but
  does not include `worker.py:596`
  (`bridge/gtkb-phase4b7-residual-mypy-strict-005.md:393-403`).

Risk/impact:

- Implementing `-005` as written would likely close the platform import,
  file-handle, subprocess kwargs, poller summary, intake, runtime, and context
  errors, but leave the `worker.py:596` `int(object)` error.
- The proposal's own new CI gate,
  `python -m mypy --strict src/groundtruth_kb/`, would still fail.

Required action:

- Add an explicit fix pattern for `worker.py:596`.
- The acceptable shape can be narrow and mechanical. For example, annotate
  `event_batch` as `dict[str, Any]` before the startup/non-startup branch, or
  assign `event_batch.get("last_event_id", last_event_id)` to a typed/cast
  temporary before calling `int(...)`.
- Verify the chosen pattern with strict mypy before returning for GO.

## Verified Non-Blocking Items

The two prior blockers from `-004` are addressed by `-005`:

- A strict-mode probe of the proposed `sys.platform == "win32"` file-lock
  import/call-site pattern passed under both `--platform linux` and
  `--platform win32`.
- A strict-mode probe of `TypedDict` summary accumulators returning via
  `cast(dict[str, Any], summary)` passed.
- A strict-mode probe of
  `subprocess.run(cmd, **cast(Any, kwargs))` passed.
- A strict-mode probe matching the `worker.py:596` inference issue failed in
  the current shape and passed when `event_batch: dict[str, Any]` was added.

## Conditions For A Revised GO

1. Keep the `-005` fixes for Pattern A and Pattern D; both are now
   mypy-verified at the strategy level.
2. Correct Pattern B to cover only the three subprocess kwargs sites:
   `worker.py:250`, `worker.py:274`, and `poller.py:167`.
3. Add a separate, concrete fix plan for `worker.py:596`.
4. Preserve the direct full-tree CI gate:
   `python -m mypy --strict src/groundtruth_kb/`.

