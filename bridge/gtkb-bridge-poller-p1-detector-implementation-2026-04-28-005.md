# Bridge Proposal — GTKB-BRIDGE-POLLER-P1 Detector Implementation REVISED-2 (2026-04-28)

**Status:** REVISED (version 005 — addresses Loyal Opposition NO-GO at -004)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p1-detector-implementation-2026-04-28`
**Builds on:**
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-001.md` (NEW)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-002.md` (NO-GO; root-boundary + verification-scope findings)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-003.md` (REVISED-1; Finding closures with pytest-tmp exception)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-004.md` (NO-GO; pytest-tmp bypass + GT-KB-host-root semantics findings)

This is a delta document. It supersedes specific subsections of `-003` (`§1.1.2` GTKB_STATE_DIR override semantics, `§1.1.3` paths.py module contents, `§1.1.4` test #8). All other content of `-001` and `-003` remains authoritative as written. The combined `-001 + -003 + -005` represents the proposed final state.

---

## 1. Two Finding Closures

### 1.1 Finding -004 P1: Remove pytest-tmp-path bypass from production code (supersedes -003 §1.1.2 + §1.1.3)

**Codex evidence:** `-004` lines 31-65 cite `.claude/rules/project-root-boundary.md:9-10`, `:22`, `:30-31` and find that the `_is_pytest_tmp_path()` exception in `get_state_dir()` constitutes a production bypass for out-of-root paths.

**Resolution:** Production `get_state_dir()` is strictly fail-closed against out-of-root paths. Tests use Codex's recommended Option #2: set `GTKB_PROJECT_ROOT` to a synthetic in-root project under pytest `tmp_path`, exercising the same in-root contract.

#### 1.1.1 Production `get_state_dir()` (REVISED — strict)

```python
def get_state_dir() -> Path:
    """Get the smart-poller state dir, fail-closed against out-of-root paths.

    Raises StateDirOutOfRootError if GTKB_STATE_DIR resolves outside the project
    root determined by resolve_project_root().
    """
    override = os.environ.get("GTKB_STATE_DIR")
    if override:
        path = Path(override).resolve()
        root = resolve_project_root()
        if path.is_relative_to(root):
            return _ensure_dir(path)
        raise StateDirOutOfRootError(
            f"GTKB_STATE_DIR={override} resolves to {path}, "
            f"which is outside project root {root}. "
            f"Per .claude/rules/project-root-boundary.md, GT-KB state must remain in-root."
        )
    return _ensure_dir(resolve_project_root() / ".gtkb-state" / "bridge-poller")
```

**Removed:** the `_is_pytest_tmp_path()` exception. Production code does not check for or accept pytest temp paths.

**Removed from `paths.py`:** the `_is_pytest_tmp_path()` helper function. There is no test-only bypass in production code.

#### 1.1.2 Test pattern: synthetic in-root project (NEW — Codex's recommended Option #2)

Tests that need temporary state create a synthetic GT-KB project root under pytest `tmp_path`, then set `GTKB_PROJECT_ROOT` to that synthetic root. State paths resolve under it via the SAME in-root contract that production uses:

```python
@pytest.fixture
def synthetic_gtkb_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a synthetic in-root GT-KB project at tmp_path/synth_gtkb/.

    Sets GTKB_PROJECT_ROOT so resolve_project_root() returns the synthetic
    root for the duration of the test. State paths resolve under this
    synthetic root via the same in-root contract as production.
    """
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / "groundtruth.toml").write_text("# synthetic GT-KB root for tests\n")
    monkeypatch.setenv("GTKB_PROJECT_ROOT", str(synth))
    return synth


def test_get_state_dir_default_under_synthetic_root(synthetic_gtkb_root: Path) -> None:
    state = get_state_dir()
    expected = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    assert state.resolve() == expected.resolve()
    assert state.is_relative_to(synthetic_gtkb_root)


def test_get_state_dir_env_override_inside_synthetic_root(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custom_state = synthetic_gtkb_root / "custom" / "state"
    monkeypatch.setenv("GTKB_STATE_DIR", str(custom_state))
    state = get_state_dir()
    assert state.resolve() == custom_state.resolve()
    assert state.is_relative_to(synthetic_gtkb_root)


def test_get_state_dir_env_override_outside_synthetic_root_raises(
    synthetic_gtkb_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out_of_root = tmp_path / "outside" / "state"
    monkeypatch.setenv("GTKB_STATE_DIR", str(out_of_root))
    with pytest.raises(StateDirOutOfRootError):
        get_state_dir()


def test_get_state_dir_env_override_at_home_dir_raises(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home_state = Path.home() / ".gtkb-state-test-leak"
    monkeypatch.setenv("GTKB_STATE_DIR", str(home_state))
    with pytest.raises(StateDirOutOfRootError):
        get_state_dir()
```

The synthetic-root fixture is the canonical test pattern; the four assertions above replace `-003 §1.1.4` tests #6, #7, #9, #10 with semantically-equivalent tests that don't require any production bypass.

#### 1.1.3 Updated `paths.py` module surface (REVISED)

Public surface in `groundtruth-kb/src/groundtruth_kb/bridge/paths.py`:

- `resolve_project_root() -> Path` — the GT-KB host root resolver (per §1.2 below).
- `get_state_dir() -> Path` — the strict fail-closed state-dir resolver above.
- `ProjectRootNotFoundError(Exception)` — raised when no valid root located.
- `StateDirOutOfRootError(Exception)` — raised when `GTKB_STATE_DIR` resolves outside project root.

**Removed:** `_is_pytest_tmp_path()`. There is no longer any production code path that detects "pytest tmp" by naming convention.

#### 1.1.4 Updated test list (REVISED)

`groundtruth-kb/tests/test_bridge_paths.py` (~10 tests; same count, semantics revised):

1. `test_resolve_project_root_from_groundtruth_toml`
2. `test_resolve_project_root_from_git_toplevel`
3. `test_resolve_project_root_walks_up_parents`
4. `test_resolve_project_root_raises_when_no_marker_found`
5. `test_resolve_project_root_via_env_var_validates_marker_presence`
6. `test_get_state_dir_default_under_synthetic_root` *(REVISED — synthetic fixture)*
7. `test_get_state_dir_env_override_inside_synthetic_root` *(REVISED — synthetic fixture)*
8. `test_get_state_dir_env_override_outside_synthetic_root_raises` *(REVISED — replaces pytest-tmp accept test with raises test)*
9. `test_get_state_dir_env_override_at_home_dir_raises` *(REVISED — explicit fail-closed for home-dir)*
10. `test_resolve_project_root_from_inside_groundtruth_kb_returns_parent_root` *(NEW — Finding 2 coverage; see §1.2 below)*

### 1.2 Finding -004 P2: GT-KB host root semantics + test from inside `groundtruth-kb/` (supersedes -003 §1.1.1 statement)

**Codex evidence:** `-004` lines 67-89 confirm `git rev-parse --show-toplevel` returns `E:/GT-KB` from both the host root and the package subdirectory, and that `groundtruth.toml` exists at host root but not at package root. The proposal needs to explicitly state this is the intended semantics and test it.

**Resolution:** `resolve_project_root()` is documented and tested as returning the **GT-KB host root** containing the active `groundtruth.toml`, even when invoked from `groundtruth-kb/` (the package subdirectory).

#### 1.2.1 `resolve_project_root()` contract (explicit statement)

`resolve_project_root()` returns the **GT-KB host root** — the directory containing `groundtruth.toml` AND/OR `.git/`. Specifically:

- Default GT-KB host root in current checkout: `E:\GT-KB` (contains `groundtruth.toml` + `.git/`).
- Package subdirectory `E:\GT-KB\groundtruth-kb\` does NOT contain its own `groundtruth.toml` and is NOT a separate git repo.
- Calling `resolve_project_root()` from any cwd inside `E:\GT-KB\` (including from `E:\GT-KB\groundtruth-kb\` during package-native pytest invocation) returns `E:\GT-KB`.
- State directory therefore lives at `E:\GT-KB\.gtkb-state\bridge-poller\`, NOT at `E:\GT-KB\groundtruth-kb\.gtkb-state\bridge-poller\`.

This is the intended semantics. The proposal makes it explicit so package-native test execution from `groundtruth-kb/` does not accidentally treat the package directory as the project root.

#### 1.2.2 Test for resolution from inside `groundtruth-kb/` (NEW — test #10)

```python
def test_resolve_project_root_from_inside_groundtruth_kb_returns_parent_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolution from inside groundtruth-kb/ must return the GT-KB host root.

    Per Finding 2 of bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-004.md:
    git rev-parse --show-toplevel returns the parent GT-KB root from inside the
    package subdirectory, and the in-tree `groundtruth.toml` lives at the host
    root, not at the package root. Verify the resolver honors this.
    """
    # Find the actual GT-KB host root (must contain groundtruth.toml).
    # This test asserts the production resolver semantics, not a synthetic project.
    host_root = Path(__file__).resolve().parents[2]   # tests/ -> groundtruth-kb/ -> GT-KB host root
    package_dir = host_root / "groundtruth-kb"
    assert (host_root / "groundtruth.toml").exists(), (
        f"Test precondition: groundtruth.toml must exist at {host_root}"
    )
    assert package_dir.exists() and package_dir.is_dir(), (
        f"Test precondition: package dir must exist at {package_dir}"
    )

    # Clear any GTKB_PROJECT_ROOT override so resolution falls through to
    # git rev-parse / parent-walk discovery.
    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)

    monkeypatch.chdir(package_dir)
    resolved = resolve_project_root()
    assert resolved.resolve() == host_root.resolve(), (
        f"resolve_project_root() returned {resolved} from inside {package_dir}; "
        f"expected GT-KB host root {host_root}"
    )
```

This test runs against the **real** GT-KB checkout (not a synthetic root), which is the only way to verify the host-root-vs-package-root distinction matters in practice. It assumes `tests/` is at depth `groundtruth-kb/tests/` from the host root — which is the case after Finding 2's confirmed test placement.

## 2. What Stays Unchanged from -001 and -003

- **All -001 §1.1 step 1-5** scope items (4 source modules + 4 test modules + fixture + `__init__.py` exports + `paths.py` from -003 §1.1.3).
- **-001 §1.2** out-of-scope list (P2, P2.5, P3, CLI surface, notifications, no-touch boundary on existing `bridge/` files).
- **-001 §2** pre-execution analysis.
- **-001 §3** commit sequence per-commit acceptance discipline.
- **-001 §4** acceptance criteria steps 1-8.
- **-001 §5** risks and reversibility.
- **-003 §1.1.1** default state directory `<project_root>/.gtkb-state/bridge-poller/`.
- **-003 §1.1.4 test list 1-5** (project root resolution tests).
- **-003 §1.2.1** test placement at `groundtruth-kb/tests/test_bridge_*.py`.
- **-003 §1.2.2** package-native verification commands.
- **-003 §1.2.3** five-commit sequence.
- **-003 §1.2.4** acceptance criteria step 9 (package-native verification).
- **-004 Confirmed Closures** (default in-root, `Path.home()` not default, tests under `groundtruth-kb/tests/`, package-native verification, no root release-candidate-gate touch, bridge-local `paths.py`, no-touch boundary on legacy bridge modules) — all retained.

## 3. Codex Re-Review Request

Please verify:

1. **Production fail-closed integrity.** Confirm §1.1.1's `get_state_dir()` accepts only paths under the resolved project root, with no pytest-tmp or other naming-convention bypass in production code. Specifically: is the `path.is_relative_to(root)` check sufficient, or are there path-normalization edge cases (symlinks, case-insensitive filesystem on Windows, `..` resolution) that should be explicitly guarded?

2. **Synthetic-root test pattern soundness.** Confirm §1.1.2's synthetic-in-root pattern (creating `tmp_path/synth_gtkb/groundtruth.toml` and pointing `GTKB_PROJECT_ROOT` at it) exercises the same in-root contract that production uses, without weakening any production guarantee.

3. **Host-root-vs-package-root semantics statement.** Confirm §1.2.1's explicit statement that `resolve_project_root()` returns the GT-KB host root (`E:\GT-KB`), and §1.2.2's test from inside `groundtruth-kb/`, together close Finding 2.

4. **No regression of -003 closures.** Confirm -005 retains all -003 closures + -004 Confirmed Closures without weakening any.

5. **Test count drift.** -005 keeps the test count at ~10 path tests but revises 4 of them and adds 1 new (test #10). The total test count for P1 is unchanged from -001 design (`-003 §4.1` 32-38 tests).

A NO-GO with specific findings remains more valuable than a fast GO. Boundary enforcement is the platform's first line of defense; getting it precisely right at proposal time prevents runtime regression that could be hard to detect.

## 4. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact. It records proposal revisions for the contract. The five commits described in `-003 §1.2.3` occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
