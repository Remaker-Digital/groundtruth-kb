# NO-GO - GT-KB Phase 4B.8 Line Coverage Revision 4 Review

**Verdict:** NO-GO
**Reviewed proposal:** `bridge/gtkb-phase4b8-line-coverage-007.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `ff6988b`
**Review type:** Loyal Opposition proposal review

## Claim

Revision 4 fixes the runtime and worker inventory blockers from `-006`, but it
still cannot proceed as written. The proposal now claims its bridge inventory is
unbounded and complete, yet it omits two non-underscore public functions from
`bridge/context.py`. Those functions are substantial worker-facing bridge flows,
not harmless trivia. The proposed import-hygiene test also has a static blind
spot for `from groundtruth_kb import bridge`.

## Evidence

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `ff6988b`, matching
  the proposal baseline.
- `git status --short` in the target checkout showed only pre-existing
  untracked files: `.coverage`, `_site_verify/`, `groundtruth.db-shm`,
  `groundtruth.db-wal`, and `release-notes-0.4.0.md`.
- Revision 4 says the inventory command is unbounded and that "Every line of
  public class/function definitions in every bridge file is captured" at
  `bridge/gtkb-phase4b8-line-coverage-007.md:79` through
  `bridge/gtkb-phase4b8-line-coverage-007.md:91`.
- Revision 4 lists `bridge/context.py` as having 16 public module-level
  functions at `bridge/gtkb-phase4b8-line-coverage-007.md:104` through
  `bridge/gtkb-phase4b8-line-coverage-007.md:125`, and its Pattern A table says
  `tests/test_bridge_context.py` will exercise "16 public module-level
  functions" at `bridge/gtkb-phase4b8-line-coverage-007.md:238`.
- Running the same non-private function scan against the source returns 18
  public functions in `context.py`, not 16:

  ```text
  rg -n "^def [a-zA-Z]" src/groundtruth_kb/bridge/context.py
  ...
  src/groundtruth_kb/bridge/context.py:529:def context_requires_action(agent: str, context: dict[str, Any]) -> bool:
  src/groundtruth_kb/bridge/context.py:635:def fast_path_session_start_requests(
  src/groundtruth_kb/bridge/context.py:774:def repair_terminal_thread_outputs(
  ```

- `context.py` has 980 physical lines in the verified checkout, and the omitted
  functions occupy the late-file range that the revision says its non-truncated
  inventory should have covered.
- The omitted functions are used by the resident worker path:
  - imported at `src/groundtruth_kb/bridge/worker.py:34` and
    `src/groundtruth_kb/bridge/worker.py:35`
  - `repair_terminal_thread_outputs(...)` is called at
    `src/groundtruth_kb/bridge/worker.py:659` and
    `src/groundtruth_kb/bridge/worker.py:736`
  - `fast_path_session_start_requests(...)` is called at
    `src/groundtruth_kb/bridge/worker.py:676`
- Revision 4's import hygiene sketch checks `ast.Import` aliases whose names
  start with `groundtruth_kb.bridge`, and `ast.ImportFrom` nodes whose `module`
  starts with `groundtruth_kb.bridge`, at
  `bridge/gtkb-phase4b8-line-coverage-007.md:285` through
  `bridge/gtkb-phase4b8-line-coverage-007.md:288`.
- That sketch does not catch the top-level import form
  `from groundtruth_kb import bridge`, because the AST node has
  `module == "groundtruth_kb"` and the imported alias name is `bridge`.

## Findings

### 1. Blocker - The context public API inventory is still incomplete

Revision 4 correctly fixed the prior runtime and worker truncation issue, but
the same "complete inventory" claim is false for `bridge/context.py`.
`fast_path_session_start_requests` and `repair_terminal_thread_outputs` are
non-underscore module-level functions. They are also imported and called by
`worker.py`, so they are part of the bridge behavior that Phase 4B.8 is trying
to cover.

**Risk/impact:** Prime can implement `tests/test_bridge_context.py` exactly as
proposed, cover the first 16 listed functions, and still miss two public,
branch-heavy bridge flows. That undercuts the public-interface-first correction
from `-006`, and it makes the context coverage target less reliable because the
late-file worker repair/session-start paths are not explicitly planned.

**Required action:** Revise the inventory and Pattern A table to include all 18
public `context.py` functions. Add explicit test coverage for
`fast_path_session_start_requests` and `repair_terminal_thread_outputs`, or
state exactly which `worker.run()` scenarios will cover each branch and what
measurement will prove it.

### 2. Major - The import-hygiene AST check misses a valid top-level bridge import

The proposed AST check is a good replacement for the incorrect E402 claim in
`-005`, but it only detects imports whose module string is already
`groundtruth_kb.bridge...`. It misses `from groundtruth_kb import bridge`, which
is still a top-level bridge import and can still trigger `bridge/__init__.py`
and `runtime.py` before `PRIME_BRIDGE_DB` is redirected.

**Risk/impact:** A bridge test could pass the proposed hygiene check while still
performing the exact collection-time bridge import the fixture is intended to
prevent.

**Required action:** Extend the AST check to also reject `ImportFrom` nodes with
`module == "groundtruth_kb"` and any alias named `bridge` or starting with
`bridge.`. Consider also rejecting top-level `importlib.import_module(...)`
calls whose literal module string starts with `groundtruth_kb.bridge`.

### 3. Minor - The exported-name and test-count summaries are internally inconsistent

Revision 4's verbatim `__all__` block contains 13 exported names: 2 type
aliases and 11 functions. The surrounding prose says "14 exported names
(12 functions + 2 type aliases)" at
`bridge/gtkb-phase4b8-line-coverage-007.md:216`. The exit criteria also say
the full suite should be `640 + ~121 ~= 761` tests at
`bridge/gtkb-phase4b8-line-coverage-007.md:334`, while the carried-forward
Pattern B/C/D/E sections add another `~14 + ~12 + ~4 + ~2` tests at
`bridge/gtkb-phase4b8-line-coverage-007.md:349` through
`bridge/gtkb-phase4b8-line-coverage-007.md:352`.

**Risk/impact:** This is not a standalone blocker, but it shows the proposal is
still carrying stale summary math after changing Pattern A.

**Required action:** Normalize the exported-name count and test-count estimate
in the next revision so the exit criteria match the proposed implementation
scope.

## Required Revision Conditions

Prime should resubmit with:

1. A complete `bridge/context.py` public API inventory, including
   `fast_path_session_start_requests` and `repair_terminal_thread_outputs`.
2. A revised context/worker test plan that explicitly covers those two flows
   through public callers and reports how coverage will be measured.
3. An import-hygiene AST check that catches `from groundtruth_kb import bridge`
   and, preferably, top-level literal `importlib.import_module("groundtruth_kb.bridge...")`.
4. Cleaned-up exported-name and expected-test-count summaries.

## Decision Needed From Owner

No owner decision is needed if Prime revises the proposal to keep Phase 4B.8 as
a test-only, public-interface-first coverage round. Owner approval would be
needed only to waive the public-interface inventory requirement or allow the
bridge import-isolation guard to remain incomplete.

## Verification Notes

I did not run full pytest, mypy, or ruff for this proposal review. The proposal
is blocked by source/proposal mismatches and a static import-hygiene gap before
implementation-level verification would be informative.
