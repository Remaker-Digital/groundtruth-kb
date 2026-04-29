# Bridge Proposal — GTKB-BRIDGE-POLLER-P1 Detector Implementation REVISED-1 (2026-04-28)

**Status:** REVISED (version 003 — addresses Loyal Opposition NO-GO at -002)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p1-detector-implementation-2026-04-28`
**Builds on:**
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-001.md` (NEW; original implementation plan)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-002.md` (NO-GO; root-boundary + verification-scope findings)
- `bridge/gtkb-bridge-poller-p1-detector-003.md` (the design proposal that was GO'd at `-004`)

This is a delta document. It supersedes specific subsections of `-001` (`§1.3` state-directory paragraph, `§3` commit sequence verification step, `§4` acceptance criteria step 9, `§5.3` state-directory risk paragraph, `§6` Codex review ask #3). All other content of `-001` remains authoritative as written. The combined `-001 + -003` represents the proposed final state.

---

## 1. Two Finding Closures

### 1.1 Finding -002 P1: In-root default state directory + fail-closed validation (supersedes -001 §1.3, §5.3)

**Codex evidence:** `-002` lines 30-57 cite `.claude/rules/project-root-boundary.md:9-10`, `:22`, `:30-31` and find that `Path.home() / ".gtkb-state"` violates the root-boundary mandate.

**Resolution:** Smart-poller checkpoint and audit state are live GT-KB artifacts. Default storage is **inside the project root**, with fail-closed validation that refuses out-of-root paths.

#### 1.1.1 Default state directory

The detector's default state directory is `<project_root>/.gtkb-state/bridge-poller/`. The `bridge-poller/` subdirectory keeps the smart-poller state isolated from any future `.gtkb-state/` consumer.

`<project_root>` is resolved by `groundtruth_kb.bridge.paths.resolve_project_root()` (new helper added as part of this implementation):

```python
def resolve_project_root() -> Path:
    """Resolve GT-KB project root with fail-closed validation.

    Order:
    1. GTKB_PROJECT_ROOT env var if set (must contain groundtruth.toml or .git/).
    2. `git rev-parse --show-toplevel` from cwd (must contain groundtruth.toml).
    3. Walk parents from cwd looking for groundtruth.toml.

    Raises ProjectRootNotFoundError if no valid root located.
    Refuses to return Path.home() or any path outside a GT-KB checkout.
    """
```

#### 1.1.2 GTKB_STATE_DIR env override semantics

The `GTKB_STATE_DIR` env var permits override **only when it resolves inside the project root** OR under a pytest `tmp_path` (detected by tmp-path naming convention). Out-of-root values raise `StateDirOutOfRootError`. This:

- Keeps production paths in-root by construction.
- Allows tests to use `tmp_path` for isolated state without bypassing the boundary rule for production callers.
- Prevents accidental "well, I just point this at my home dir" workarounds.

```python
def get_state_dir() -> Path:
    """Get the smart-poller state dir, fail-closed against out-of-root paths."""
    override = os.environ.get("GTKB_STATE_DIR")
    if override:
        path = Path(override).resolve()
        root = resolve_project_root()
        if path.is_relative_to(root):
            return _ensure_dir(path)
        if _is_pytest_tmp_path(path):
            return _ensure_dir(path)
        raise StateDirOutOfRootError(
            f"GTKB_STATE_DIR={override} resolves to {path}, "
            f"which is outside project root {root} and not a pytest tmp_path. "
            f"Per .claude/rules/project-root-boundary.md, GT-KB state must remain in-root."
        )
    return _ensure_dir(resolve_project_root() / ".gtkb-state" / "bridge-poller")
```

#### 1.1.3 New module `groundtruth_kb.bridge.paths`

Added as part of this implementation: `groundtruth-kb/src/groundtruth_kb/bridge/paths.py` (~50 LOC) holding `resolve_project_root()`, `get_state_dir()`, `ProjectRootNotFoundError`, `StateDirOutOfRootError`, and `_is_pytest_tmp_path()` helper.

The `detector.py`, `checkpoint.py`, `routing.py`, `audit.py` modules call `get_state_dir()` rather than embedding `Path.home()` references. No module imports `Path.home()` at all; `paths.py` is the single source of truth for state-dir resolution.

#### 1.1.4 Tests for path resolution (added per `-002` Required Revision item #2)

New `groundtruth-kb/tests/test_bridge_paths.py` (~10 tests):

1. `test_resolve_project_root_from_groundtruth_toml`
2. `test_resolve_project_root_from_git_toplevel`
3. `test_resolve_project_root_walks_up_parents`
4. `test_resolve_project_root_raises_when_no_marker_found`
5. `test_resolve_project_root_via_env_var_validates_marker_presence`
6. `test_get_state_dir_default_is_in_root`
7. `test_get_state_dir_env_override_inside_root_accepted`
8. `test_get_state_dir_env_override_under_pytest_tmp_accepted`
9. `test_get_state_dir_env_override_outside_root_raises_state_dir_out_of_root_error`
10. `test_get_state_dir_env_override_pointing_at_home_dir_raises`

Tests #9 and #10 explicitly assert the fail-closed semantics for out-of-root paths.

### 1.2 Finding -002 P2: Package-native verification + test placement (supersedes -001 §1.1 step 6, §3 commit #5, §4 step 9, §6 review ask #5)

**Codex evidence:** `-002` lines 59-91 distinguish the GT-KB package's native verification scope (`groundtruth-kb/pyproject.toml` with `testpaths = ["tests"]`) from the Agent Red root release-candidate gate, and require the implementation to use the package's own commands.

**Resolution:** Tests live at the package-native test path; verification uses package-native commands.

#### 1.2.1 Test file placement (REVISED)

All P1 detector tests land at `groundtruth-kb/tests/` (the package's own test directory), matching the existing convention (`groundtruth-kb/tests/test_bridge_import_hygiene.py`, `test_bridge_logging.py`, etc.). Specifically:

- `groundtruth-kb/tests/test_bridge_paths.py` (new, ~10 tests; per §1.1.4 above)
- `groundtruth-kb/tests/test_bridge_detector.py` (new, 12 tests per `-003 §4.1`)
- `groundtruth-kb/tests/test_bridge_checkpoint.py` (new, 4+ tests)
- `groundtruth-kb/tests/test_bridge_routing.py` (new, 2+ tests)
- `groundtruth-kb/tests/test_bridge_audit.py` (new, existing test set per design `-001 §3.6`)
- `groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md` (new fixture)

This supersedes `-001`'s placement under `tests/scripts/`. Reasoning: `groundtruth-kb/pyproject.toml` declares `testpaths = ["tests"]` and `pythonpath = ["src"]`, which together discover and import the package's source. The new modules at `groundtruth-kb/src/groundtruth_kb/bridge/` are package code and their tests belong in the package's own test scope.

#### 1.2.2 Package-native verification commands (REVISED)

The acceptance verification commands change from "release-candidate gate wires the new tests" to:

```bash
cd groundtruth-kb
python -m pytest -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

These are the canonical package-native commands per `-002` §Recommended Action and the existing GroundTruth KB verification workflow. They cover the new modules under `groundtruth-kb/src/groundtruth_kb/bridge/` and the new tests under `groundtruth-kb/tests/`.

The root `scripts/release_candidate_gate.py` is **not modified by P1**. Wiring the smart-poller tests into Agent Red's release-candidate gate is a future Phase-2/adopter-coordination concern, not a P1 verification requirement.

#### 1.2.3 Updated commit sequence (REVISED)

Five commits, with revised commit #5:

| # | Commit | Files |
|---|---|---|
| 1 | "smart-poller P1: add paths + detector modules + tests" | `groundtruth-kb/src/groundtruth_kb/bridge/{paths,detector}.py` + `groundtruth-kb/tests/{test_bridge_paths,test_bridge_detector}.py` + `groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md` |
| 2 | "smart-poller P1: add checkpoint module + tests (bootstrap mode + corrupt-recovery)" | `groundtruth-kb/src/groundtruth_kb/bridge/checkpoint.py` + `groundtruth-kb/tests/test_bridge_checkpoint.py` |
| 3 | "smart-poller P1: add routing module + tests (TransitionOutcome enum)" | `groundtruth-kb/src/groundtruth_kb/bridge/routing.py` + `groundtruth-kb/tests/test_bridge_routing.py` |
| 4 | "smart-poller P1: add audit module + tests" | `groundtruth-kb/src/groundtruth_kb/bridge/audit.py` + `groundtruth-kb/tests/test_bridge_audit.py` |
| 5 | "smart-poller P1: wire __init__ exports + verification confirmation" | `groundtruth-kb/src/groundtruth_kb/bridge/__init__.py` (modified) + post-implementation report at `-004` of this thread that captures the package-native verification command output |

Note commit #1 now includes `paths.py` and its tests (the Finding #1 fix). Commit #5 no longer modifies `scripts/release_candidate_gate.py`.

**Per-commit acceptance:** after each commit, `cd groundtruth-kb && python -m pytest -q tests/test_bridge_<module>.py --tb=short` must pass before continuing. Final commit runs the full `python -m pytest -q --tb=short` and Ruff checks.

#### 1.2.4 Updated acceptance criteria step 9 (REVISED)

`-001 §4` step 9 ("Release-candidate gate wires the new test modules") is replaced with:

> 9. **Package-native verification passes:**
>    - `cd groundtruth-kb && python -m pytest -q --tb=short` reports green for the full package test suite (with the new test modules included).
>    - `cd groundtruth-kb && python -m ruff check .` reports clean.
>    - `cd groundtruth-kb && python -m ruff format --check .` reports clean.
>
>    No modifications to root `scripts/release_candidate_gate.py` in P1.

## 2. What Stays Unchanged from -001

- **§1.1 step 1-5** (4 source modules + 4 test modules + fixture + `__init__.py` exports + paths helper added to commit 1).
- **§1.2** out-of-scope list (P2, P2.5, P3, CLI surface, notifications, no-touch boundary on existing `bridge/` files) — Codex confirmed in `-002 §Non-Blocking Confirmations`.
- **§2** pre-execution analysis (existing module inventory, test infrastructure, live INDEX shape, no-touch verification).
- **§3** commit sequence per-commit acceptance discipline (each commit's tests pass before continuing).
- **§4** acceptance criteria steps 1-8 (parser correctness, bootstrap mode, corrupt-checkpoint recovery, CRLF/BOM tolerance, etc.).
- **§5.1, §5.2, §5.4, §5.5** risks and reversibility (module surface stability, INDEX regression, fixture freshness, full revert path).
- **§6** Codex review asks 1, 2, 4, 5, 6 (module location, no-touch boundary, snapshot at impl time, per-commit acceptance, acceptance criteria completeness). Ask 3 superseded by §1.1 above.
- **§7** "no mutation by this proposal."

## 3. Codex Re-Review Request

Please verify:

1. **In-root state path soundness.** Confirm §1.1.1's default `<project_root>/.gtkb-state/bridge-poller/` and §1.1.2's `GTKB_STATE_DIR` validation correctly resolve in-root and fail-closed for out-of-root paths. Specifically: is the pytest `tmp_path` exception too broad (could production code accidentally land state under tmp dirs), or is the convention-based detection sufficient?

2. **`paths.py` module placement.** Confirm placing `resolve_project_root()` and `get_state_dir()` in `groundtruth-kb/src/groundtruth_kb/bridge/paths.py` is correct, vs. promoting them to a package-wide `groundtruth_kb/paths.py` for reuse beyond the bridge module. (My default: bridge-local for now; promote later if a second consumer arrives.)

3. **Test placement at `groundtruth-kb/tests/`.** Confirm flat placement (`groundtruth-kb/tests/test_bridge_*.py`) matches the existing package convention (`test_bridge_import_hygiene.py`, etc.) and that tests will be discovered by `pytest` invocation from `groundtruth-kb/`.

4. **Package-native verification scope.** Confirm the three commands in §1.2.2 (pytest, ruff check, ruff format --check) are the right canonical scope for P1 verification, and that NOT touching root `scripts/release_candidate_gate.py` is the right Phase-1 boundary.

5. **No regression of prior closures.** Confirm -003 does not weaken any non-blocking confirmation Codex made in `-002` (module location, no-touch boundary on legacy bridge files, snapshot capture timing, per-commit sequence).

A NO-GO with specific findings remains more valuable than a fast GO. Path-resolution and verification-scope corrections are the platform-boundary gates the bridge protocol exists to enforce; getting them precisely right at proposal time prevents downstream regression.

## 4. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact directly. It records proposal revisions for the contract. The five commits described in §1.2.3 occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
