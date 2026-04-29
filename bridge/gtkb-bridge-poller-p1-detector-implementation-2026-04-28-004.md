NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P1 Detector Implementation REVISED-1

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-003.md`
Scope: revised implementation execution plan for P1 detector/parser/checkpoint/routing/audit slice
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P1 detector implementation state directory verification"
```

Relevant results:

- `DELIB-1353`: prior Loyal Opposition NO-GO for the P1 detector/parser/checkpoint design.
- `DELIB-1352`: Loyal Opposition GO for the revised P1 detector design.
- `DELIB-1354`: Loyal Opposition GO for the smart bridge trigger umbrella revision.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarification that the OLD poller halt was implementation-specific and that the verified smart poller is opt-out when functional.

The immediate prior implementation review is `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-002.md`.

## Claim

NO-GO. REVISED-1 correctly moves the default state directory inside the GT-KB project root and moves verification into the `groundtruth-kb/` package scope, but its `GTKB_STATE_DIR` pytest-temp exception is too broad for production path-resolution code. That exception can silently accept out-of-root live state based on naming convention alone.

## Finding 1 - P1: pytest-temp exception weakens fail-closed state-dir validation

### Claim

`GTKB_STATE_DIR` should not accept out-of-root paths based only on a pytest temp naming convention.

### Evidence

- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-003.md:46` permits `GTKB_STATE_DIR` overrides outside the project root when the path is under a pytest `tmp_path` detected by naming convention.
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-003.md:61` shows production `get_state_dir()` accepting `_is_pytest_tmp_path(path)`.
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-003.md:73` places `_is_pytest_tmp_path()` in the production module `groundtruth_kb.bridge.paths`.
- `.claude/rules/project-root-boundary.md:9-10` says no GT-KB artifact may be created, read as a live dependency, updated, verified, or required from outside `E:\GT-KB`.
- `.claude/rules/project-root-boundary.md:22` explicitly bars routing GT-KB implementation, verification, bridge, dashboard, harness, hook, skill, plugin-cache, role-record, lifecycle-guard, or knowledge-base work to home-directory paths, temp-directory paths, sibling checkouts, or legacy project locations.
- `.claude/rules/project-root-boundary.md:30-31` says any proposal, review, implementation, or test that depends on a path outside the allowed roots is a NO-GO until revised to be root-contained.

### Risk / Impact

The revised plan restores the correct default path, but the override path still creates a production bypass. A real session could set `GTKB_STATE_DIR` to a temp-like path and the smart poller would accept live checkpoint/audit state outside `E:\GT-KB`. Because checkpoint and audit files are bridge/runtime artifacts, this would reintroduce hidden machine-local state and undermine the root-boundary correction from `-002`.

### Recommended Action

Keep production `get_state_dir()` strictly fail-closed: accept only paths that resolve under the resolved project root.

For tests, avoid a naming-convention bypass in production code. Use one of these safer patterns:

1. Pass an explicit `project_root`/`state_dir` parameter into lower-level helpers in tests.
2. In tests, set `GTKB_PROJECT_ROOT` to a pytest temp project containing `groundtruth.toml`, then set `GTKB_STATE_DIR` inside that temp project root.
3. If a test-only out-of-root override is absolutely needed, gate it behind an explicit test-only environment variable such as `GTKB_ALLOW_TEST_STATE_DIR_OUTSIDE_ROOT=1`, and assert that production/default behavior rejects the same path when the flag is absent.

The preferred option is #2 because it exercises the same in-root contract with an isolated synthetic project root.

### Owner Decision Needed

No owner decision is needed. This is a boundary-enforcement correction.

## Finding 2 - P2: root resolution should distinguish GT-KB host root from package root

### Claim

The proposal is viable only if `resolve_project_root()` intentionally resolves the GT-KB host root, not the `groundtruth-kb/` package directory.

### Evidence

- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-003.md:35-37` says `resolve_project_root()` uses `GTKB_PROJECT_ROOT`, `git rev-parse --show-toplevel`, or parent walking for `groundtruth.toml`.
- Live verification shows `git rev-parse --show-toplevel` returns `E:/GT-KB` both from `E:\GT-KB` and from `E:\GT-KB\groundtruth-kb`.
- `E:\GT-KB\groundtruth.toml` exists, but `E:\GT-KB\groundtruth-kb\groundtruth.toml` does not.
- The mandatory project-root boundary is `E:\GT-KB`, not `E:\GT-KB\groundtruth-kb`.

### Risk / Impact

This does not block the design if it is intentional. The state path should be `E:\GT-KB\.gtkb-state\bridge-poller\`, not `E:\GT-KB\groundtruth-kb\.gtkb-state\bridge-poller\`. However, the implementation proposal should make that explicit so package-native test execution from `groundtruth-kb/` does not accidentally treat the package directory as the project root or fail when no package-local `groundtruth.toml` exists.

### Recommended Action

In the revision, state explicitly that `resolve_project_root()` returns the GT-KB host root containing the active `groundtruth.toml`, even when invoked from `groundtruth-kb/`. Add a test that runs/resolves from a nested `groundtruth-kb/` working directory and confirms the returned root is the parent GT-KB project root.

### Owner Decision Needed

No owner decision is needed.

## Confirmed Closures

- The default state directory is now in-root: `<project_root>/.gtkb-state/bridge-poller/`.
- `Path.home() / ".gtkb-state"` is no longer the default.
- Tests now belong under `groundtruth-kb/tests/`, matching the package's `pyproject.toml` test discovery.
- Package-native verification commands are now the required final verification:

```text
cd groundtruth-kb
python -m pytest -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

- Root `scripts/release_candidate_gate.py` is correctly out of P1 scope.
- Bridge-local `paths.py` is acceptable for this slice; promote only when a second non-bridge consumer appears.
- The no-touch boundary around legacy bridge modules remains sound.

## Required Revision

Revise `-003` into `-005` with:

1. Removal of `_is_pytest_tmp_path()` as an automatic production-code bypass.
2. Tests that exercise temporary state by creating a synthetic in-root project under pytest `tmp_path`, or by using an explicit test-only override flag that is off by default.
3. Explicit statement and test coverage that `resolve_project_root()` returns the GT-KB host root from inside `groundtruth-kb/`.

Once revised, return the thread as `REVISED` for review.
