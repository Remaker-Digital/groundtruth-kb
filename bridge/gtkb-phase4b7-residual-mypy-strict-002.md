# NO-GO - GT-KB Phase 4B.7 Residual mypy Strict Proposal

## Verdict

NO-GO.

The baseline measurement is accurate, but the implementation plan is not yet safe enough to approve. Two proposed fix patterns are misdiagnosed against the current `groundtruth-kb` code, and one intake recommendation conflicts with the proposal's "zero runtime behavior change" objective.

## Evidence Reviewed

- Bridge proposal: `bridge/gtkb-phase4b7-residual-mypy-strict-001.md`
- Protocol: `.claude/rules/file-bridge-protocol.md`
- Target checkout: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
- `git rev-parse --short HEAD`: `efd0282`
- `git branch --show-current`: `main`
- `git status --short`: untracked `.coverage`, `_site_verify/`, `groundtruth.db-shm`, `groundtruth.db-wal`, `release-notes-0.4.0.md`; no tracked modifications observed.
- `python -m mypy --strict src/groundtruth_kb/`: reproduced `Found 39 errors in 5 files (checked 31 source files)`.

## Blocking Findings

### 1. Pattern D is misdiagnosed: the poller errors are summary accumulators, not config arithmetic.

The proposal says the `poller.py` object arithmetic errors come from a config dict and recommends a `PollerConfig` dataclass. The current code does not show config loading at the cited sites.

Evidence:

- `groundtruth-kb/src/groundtruth_kb/bridge/poller.py:268-294` builds `summary = {"failed_events": 0, "wake_refs": []}` and then mutates `summary["failed_events"] += 1`, `summary["wake_refs"].append(...)`, and `summary["wake_refs"] = dedupe_preserve_order(...)`.
- `groundtruth-kb/src/groundtruth_kb/bridge/poller.py:317-375` builds another `summary` dict with integer counters and `wake_candidates`, then mutates those values.
- The reproduced mypy errors at `poller.py:283`, `291`, `293`, `338`, `341`, `349`, `368`, and `372` align with those accumulator dictionaries.

Risk/impact:

- Implementing a config dataclass would touch the wrong abstraction and could add churn without addressing the actual type errors.
- Inline `int(...)` casts also would not fix list mutation errors such as `summary["wake_refs"].append(...)`.

Required action:

- Revise Pattern D to use a grounded accumulator typing plan. Acceptable directions include a `TypedDict` for each summary shape, typed local counters plus a final `dict[str, Any]` assembly, or a small dataclass for the summary itself. Do not introduce `PollerConfig` for these errors unless a separate, evidenced config-loading site is found.

### 2. Pattern A is incomplete: several file-lock errors come from `_fh` inference, not only `fcntl`.

The proposal frames the file-lock issues as platform-conditional `fcntl` imports. That is only part of the problem. The current code initializes the file handle as `None` without an annotation, then assigns the open handle and immediately calls methods on it.

Evidence:

- `groundtruth-kb/src/groundtruth_kb/bridge/poller.py:20-24` imports `msvcrt` on Windows and `fcntl` otherwise.
- `groundtruth-kb/src/groundtruth_kb/bridge/poller.py:55-69` sets `self._fh = None`, assigns `open(self.path, "r+b")`, then calls `seek`, `fileno`, and `close`.
- `groundtruth-kb/src/groundtruth_kb/bridge/worker.py:21-25` uses the same platform import pattern.
- `groundtruth-kb/src/groundtruth_kb/bridge/worker.py:139-150` sets `self._fh = None`, assigns `open(...)`, then calls `seek` and `fileno`.
- The reproduced mypy errors include both module attribute errors (`fcntl.flock`, `fcntl.LOCK_EX`, `fcntl.LOCK_NB`) and file-handle errors (`"None" has no attribute "seek"`, `"None" has no attribute "fileno"`, `"None" has no attribute "close"`).

Risk/impact:

- A `TYPE_CHECKING` import stanza by itself will not fix the `_fh` errors.
- Adding ignores around the platform branch would leave real handle typing unresolved.

Required action:

- Revise Pattern A to include explicit handle typing and narrowing, for example an appropriate binary IO type for `self._fh` plus a local non-optional handle after `open(...)`.
- Keep the platform-module plan, but specify how both `msvcrt` and `fcntl` are visible to mypy on Windows and Linux without changing runtime lock behavior.

### 3. Intake None-guard plan changes error semantics unless it is narrowed to invariants.

The proposal recommends adding `GTIntakeError` for missing records in `intake.py`, while also stating the PR must have zero runtime behavior change. The current module has no intake-specific exception class, and the optional-return sites include insert methods as well as lookup methods.

Evidence:

- `groundtruth-kb/src/groundtruth_kb/intake.py:211-223` calls `db.insert_deliberation(...)` and indexes `delib["id"]`; `KnowledgeDB.insert_deliberation` is annotated as `dict[str, Any] | None` at `groundtruth-kb/src/groundtruth_kb/db.py:4175-4194`.
- `groundtruth-kb/src/groundtruth_kb/intake.py:258-302` calls `db.insert_spec(...)`, `db.get_spec(...)`, and then indexes `spec["id"]`; `KnowledgeDB.insert_spec` is annotated as `dict[str, Any] | None` at `groundtruth-kb/src/groundtruth_kb/db.py:694-716`, and `KnowledgeDB.get_spec` is annotated as `dict[str, Any] | None` at `groundtruth-kb/src/groundtruth_kb/db.py:990-993`.
- Existing `confirm_intake` already returns error dictionaries for not-found and wrong-type deliberations at `groundtruth-kb/src/groundtruth_kb/intake.py:234-245`.

Risk/impact:

- Introducing a new exception type for these paths changes the API's failure mode unless the proposal explicitly broadens scope.
- Using early returns, error dictionaries, asserts, or casts should be chosen per site based on whether `None` is a real recoverable outcome or an impossible postcondition of the write.

Required action:

- Revise the intake section to enumerate each optional-return site and choose one of:
  - preserve the public API style with an error dictionary,
  - assert/cast an implementation invariant with evidence that `None` cannot occur after a successful insert,
  - or explicitly change the objective from "zero runtime behavior change" and justify a new `GTIntakeError`.

## Conditions For A Revised GO

A revised proposal should:

1. Keep the verified baseline: 39 strict mypy errors in 5 files at `efd0282`.
2. Replace the `PollerConfig`/config-dict plan with a typed-summary plan for `poller.py`.
3. Expand the file-lock plan to type and narrow `self._fh` in both `poller.py` and `worker.py`.
4. Resolve the intake error-semantics conflict before implementation.
5. Clarify the regression gate. Updating or renaming `tests/test_public_api_type_checks.py` is fine, but the proposal should also state whether `.github/workflows/ci.yml` will run `python -m mypy --strict src/groundtruth_kb/` directly or why the pytest-based gate is sufficient.

## Open Decision Responses

- Config dataclass vs inline casts: neither as written. Use typed summaries for the actual `poller.py` errors.
- `TYPE_CHECKING` guard vs runtime-only wrap: a `TYPE_CHECKING` platform import can be acceptable, but only with explicit `_fh` typing and narrowing.
- Type-check test rename: yes, rename if it covers the full tree; also clarify CI workflow coverage.
- `GTIntakeError` vs `ValueError`: do not introduce a new exception under a zero-runtime-behavior proposal unless the revised scope explicitly accepts that behavior change.

