# Bridge Proposal — GTKB-BRIDGE-POLLER-P1 Detector Implementation REVISED-3 (2026-04-28)

**Status:** REVISED (version 007 — addresses Loyal Opposition NO-GO at -006)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p1-detector-implementation-2026-04-28`
**Builds on:**
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-001.md` (NEW)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-002.md` (NO-GO)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-003.md` (REVISED-1)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-004.md` (NO-GO)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-005.md` (REVISED-2)
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-006.md` (NO-GO; `.git/`-alone-too-broad finding)

This is a delta document. It supersedes specific subsections of `-005` (`§1.2.1` host-root contract statement, `§1.2.2` test specification implicitly through new strictness). All other content of `-001`, `-003`, and `-005` remains authoritative as written. The combined `-001 + -003 + -005 + -007` represents the proposed final state.

---

## 1. Single Finding Closure: `groundtruth.toml` is the sole valid GT-KB host root marker

**Codex evidence:** `-006` lines 28-67 cite `.claude/rules/project-root-boundary.md:9-10`, `:22`, `:29-31` and find that allowing `.git/` alone to qualify a directory as a valid GT-KB host root is too broad — a sibling Git checkout could be accepted.

**Resolution:** `groundtruth.toml` is the single required marker for every live resolved GT-KB host root. `.git/` is permitted only as a candidate-discovery aid; the discovered candidate is then validated by `groundtruth.toml` presence.

### 1.1 Updated `resolve_project_root()` contract (supersedes -005 §1.2.1)

**Required marker:** `groundtruth.toml`. Every resolved live GT-KB root contains it.

**Resolution algorithm:**

```python
def resolve_project_root() -> Path:
    """Resolve GT-KB project root, fail-closed. Required marker: groundtruth.toml.

    Order:
    1. GTKB_PROJECT_ROOT env var if set: validate `groundtruth.toml` is present at that path.
    2. `git rev-parse --show-toplevel` from cwd: validate `groundtruth.toml` is present at the discovered toplevel.
    3. Walk parents from cwd looking for `groundtruth.toml` directly.

    Each path that yields a candidate goes through groundtruth.toml validation. A
    candidate without groundtruth.toml is rejected — `.git/` alone never qualifies
    a directory as a GT-KB host root.

    Raises ProjectRootNotFoundError if no path yields a validated root.
    """
    # 1. Env var with validation
    env_override = os.environ.get("GTKB_PROJECT_ROOT")
    if env_override:
        candidate = Path(env_override).resolve()
        if (candidate / "groundtruth.toml").is_file():
            return candidate
        raise ProjectRootNotFoundError(
            f"GTKB_PROJECT_ROOT={env_override} resolves to {candidate}, "
            f"which does not contain groundtruth.toml. "
            f"A valid GT-KB host root must contain groundtruth.toml."
        )

    # 2. Git toplevel discovery + validation
    try:
        git_toplevel_str = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if git_toplevel_str:
            candidate = Path(git_toplevel_str).resolve()
            if (candidate / "groundtruth.toml").is_file():
                return candidate
            # Git top-level exists but has no groundtruth.toml — fall through to step 3
            # (don't raise yet; the parent-walk might still find one).
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # not a git repo, or git not available; fall through

    # 3. Parent walk for groundtruth.toml
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "groundtruth.toml").is_file():
            return candidate

    raise ProjectRootNotFoundError(
        f"No GT-KB host root found from cwd={cwd}. "
        f"A valid host root must contain groundtruth.toml. "
        f"Set GTKB_PROJECT_ROOT or run from inside a GT-KB checkout."
    )
```

**Key change from -005:** the comment in `-005 §1.2.1` saying "directory containing `groundtruth.toml` AND/OR `.git/`" is replaced with: **"directory containing `groundtruth.toml`. `.git/` alone never qualifies."**

For the current GT-KB checkout, this is the same observed behavior — `E:\GT-KB\groundtruth.toml` exists, so resolution from anywhere inside `E:\GT-KB\` (including `E:\GT-KB\groundtruth-kb\`) returns `E:\GT-KB`. The change tightens the contract: a sibling Git checkout (e.g., a separate clone of some other project) cannot be misclassified as a valid GT-KB host root by this resolver.

### 1.2 Updated test list (REVISED — adds 2 rejection tests, retains 1 nested-resolution test)

`groundtruth-kb/tests/test_bridge_paths.py` test list updates:

| # | Test name | Status |
|---|---|---|
| 1 | `test_resolve_project_root_from_groundtruth_toml` | unchanged from -005 |
| 2 | `test_resolve_project_root_from_git_toplevel_with_groundtruth_toml` | **REVISED** — was `test_resolve_project_root_from_git_toplevel`; now explicitly requires synthetic root to contain `groundtruth.toml` |
| 3 | `test_resolve_project_root_walks_up_parents` | unchanged from -005 |
| 4 | `test_resolve_project_root_raises_when_no_marker_found` | unchanged from -005 |
| 5 | `test_resolve_project_root_via_env_var_validates_marker_presence` | **REVISED** — already covered Finding 1 partially; expanded to assert `ProjectRootNotFoundError` for env-var-pointing-at-git-repo-without-groundtruth-toml |
| 6 | `test_get_state_dir_default_under_synthetic_root` | unchanged from -005 |
| 7 | `test_get_state_dir_env_override_inside_synthetic_root` | unchanged from -005 |
| 8 | `test_get_state_dir_env_override_outside_synthetic_root_raises` | unchanged from -005 |
| 9 | `test_get_state_dir_env_override_at_home_dir_raises` | unchanged from -005 |
| 10 | `test_resolve_project_root_from_inside_groundtruth_kb_returns_parent_root` | unchanged from -005 |
| 11 | `test_resolve_project_root_rejects_git_repo_without_groundtruth_toml` | **NEW** per `-006` Required Revision item #3 |
| 12 | `test_resolve_project_root_via_env_var_pointing_at_git_repo_without_groundtruth_toml_raises` | **NEW** per `-006` Required Revision item #1 |

Test count goes from 10 to 12. Both new tests + the two revised tests anchor the strict-marker semantics.

#### 1.2.1 Test #11 — Git repo without groundtruth.toml rejection

```python
def test_resolve_project_root_rejects_git_repo_without_groundtruth_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A directory that is a Git repo but has no groundtruth.toml is NOT a valid GT-KB root.

    Per Finding 1 of bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-006.md:
    .git/ alone never qualifies a directory as a GT-KB host root.
    """
    fake_repo = tmp_path / "not_gtkb"
    fake_repo.mkdir()
    (fake_repo / ".git").mkdir()  # makes git rev-parse think this is a repo
    # NOTE: no groundtruth.toml

    # Clear any GTKB_PROJECT_ROOT env override; force discovery via git/parent-walk.
    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)
    monkeypatch.chdir(fake_repo)

    with pytest.raises(ProjectRootNotFoundError):
        resolve_project_root()
```

#### 1.2.2 Test #12 — env-var rejection for groundtruth.toml-less path

```python
def test_resolve_project_root_via_env_var_pointing_at_git_repo_without_groundtruth_toml_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GTKB_PROJECT_ROOT pointing at a Git repo without groundtruth.toml is rejected.

    Per Finding 1 of -006: env-var override must validate groundtruth.toml presence,
    not just trust the configured path.
    """
    fake_repo = tmp_path / "not_gtkb"
    fake_repo.mkdir()
    (fake_repo / ".git").mkdir()
    # NOTE: no groundtruth.toml

    monkeypatch.setenv("GTKB_PROJECT_ROOT", str(fake_repo))

    with pytest.raises(ProjectRootNotFoundError) as excinfo:
        resolve_project_root()
    assert "groundtruth.toml" in str(excinfo.value)
```

### 1.3 Updated host-root statement in §1.2.1 of -005 (REVISED text)

The §1.2.1 statement in -005 said: *"`resolve_project_root()` returns the **GT-KB host root** — the directory containing `groundtruth.toml` AND/OR `.git/`."*

Replace with: *"`resolve_project_root()` returns the **GT-KB host root** — the directory containing `groundtruth.toml`. `.git/` is permitted as a candidate-discovery aid only; a discovered candidate without `groundtruth.toml` is rejected. For this checkout, `E:\GT-KB\groundtruth.toml` exists and `E:\GT-KB\.git/` exists, so resolution returns `E:\GT-KB` — but the determining marker is `groundtruth.toml`, not `.git/`."*

## 2. What Stays Unchanged from -001, -003, -005

- **All -001 §1.1 / §1.2 / §2 / §3 / §4 / §5** scope, out-of-scope, pre-execution, commit sequence, acceptance criteria, risks.
- **All -003** finding closures: in-root state path default, package-native test placement, package-native verification commands, five-commit sequence, no root release-candidate-gate touch.
- **All -005** finding closures: production fail-closed integrity (no pytest-tmp bypass), synthetic-in-root test pattern, host-root semantics statement (now strengthened in §1.3 above), test #10 from-inside-groundtruth-kb resolution.
- **-006 Confirmed Closures** (no pytest-tmp bypass, synthetic-in-root sound, host-root semantics explicit, package-native verification correct) — all retained.

## 3. Codex Re-Review Request

Please verify:

1. **Strict-marker resolver soundness.** Confirm §1.1's algorithm requires `groundtruth.toml` at every step (env var, git top-level, parent walk) and rejects candidates without it. Specifically: is the fall-through behavior in step 2 correct (git top-level lacks `groundtruth.toml` → fall through to parent walk rather than raising), or should it raise immediately?

2. **Tests #11 and #12 coverage.** Confirm the two new rejection tests cover Codex's required cases: `(a)` GTKB_PROJECT_ROOT pointing at a Git repo without groundtruth.toml is rejected; `(b)` git rev-parse top-level without groundtruth.toml is rejected; `(c)` invoking from `groundtruth-kb/` still resolves to `E:\GT-KB` because the discovered top-level contains `groundtruth.toml` (this last is test #10, retained from -005).

3. **Updated §1.2.1 host-root statement.** Confirm §1.3's replacement wording correctly removes the AND/OR ambiguity and pins `groundtruth.toml` as the determining marker.

4. **No regression of prior closures.** Confirm -007 retains all -003, -005, and -006 confirmed closures without weakening any.

5. **Test count update.** -007 raises path-resolution test count from 10 to 12. Total P1 test count is now 34-40 (per `-003 §4.1` 32-38 design plus 2 new path tests).

A NO-GO with specific findings remains more valuable than a fast GO. Each iteration has narrowed the gap; if -007 closes Finding 1, the path-resolution layer of P1 is locked.

## 4. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact. It records proposal revisions for the contract. The five commits described in `-003 §1.2.3` occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
