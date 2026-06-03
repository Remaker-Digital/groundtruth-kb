"""Regression tests for per-session pytest basetemp isolation (WI-3469).

Authority: bridge/gtkb-pytest-basetemp-session-isolation-002.md (GO);
PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001 under PROJECT-GTKB-MAY29-HYGIENE.

The tests exercise the root ``conftest.py`` hook directly with lightweight
config doubles, so they do not spawn nested pytest processes and run fast under
the suite's ``--timeout=30``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CONFTEST_PATH = _PROJECT_ROOT / "conftest.py"


def _load_root_conftest() -> ModuleType:
    """Load the project-root conftest.py as an importable module."""
    spec = importlib.util.spec_from_file_location("_gtkb_root_conftest", _CONFTEST_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _OptionDouble:
    def __init__(self, basetemp: str | None = None) -> None:
        self.basetemp = basetemp


class _ConfigDouble:
    def __init__(self, basetemp: str | None = None) -> None:
        self.option = _OptionDouble(basetemp)


def test_root_conftest_exists() -> None:
    assert _CONFTEST_PATH.is_file()


def test_session_leaf_name_encodes_pid_under_inroot_parent() -> None:
    """Pure path computation: leaf is ``<root>/.pytest-tmp/session-<pid>-<token>``."""
    mod = _load_root_conftest()

    leaf = mod._session_basetemp_leaf(_PROJECT_ROOT)

    assert leaf.parent.name == mod.PYTEST_TMP_PARENT_NAME
    assert leaf.name.startswith(f"session-{os.getpid()}-")


def test_hook_sets_and_creates_basetemp_when_unset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Success path with a clean (non-contaminated) leaf parent.

    Uses a tmp_path-rooted leaf so the eager ``mkdir`` succeeds deterministically
    regardless of the real in-root ``.pytest-tmp/`` ACL state (which a prior
    parallel run may have poisoned — the very condition this fix addresses).
    """
    mod = _load_root_conftest()
    fake_leaf = tmp_path / mod.PYTEST_TMP_PARENT_NAME / f"session-{os.getpid()}-abc123"
    monkeypatch.setattr(mod, "_session_basetemp_leaf", lambda root: fake_leaf)
    config = _ConfigDouble(basetemp=None)

    mod.pytest_configure(config)

    assert config.option.basetemp == str(fake_leaf)
    # The leaf is created eagerly so an unwritable parent fails at configure time.
    assert fake_leaf.is_dir()


def test_hook_is_noop_when_basetemp_already_set() -> None:
    mod = _load_root_conftest()
    chosen = str(_PROJECT_ROOT / ".tmp" / "explicit-basetemp")
    config = _ConfigDouble(basetemp=chosen)

    mod.pytest_configure(config)

    # Existing --basetemp automation is preserved byte-for-byte.
    assert config.option.basetemp == chosen


def test_two_sessions_get_distinct_nonnesting_leaves() -> None:
    mod = _load_root_conftest()

    leaf1 = mod._session_basetemp_leaf(_PROJECT_ROOT)
    leaf2 = mod._session_basetemp_leaf(_PROJECT_ROOT)

    assert leaf1 != leaf2
    # Neither leaf nests inside the other — parallel sessions cannot collide on
    # the same ACL-bearing subtree.
    assert leaf1 not in leaf2.parents
    assert leaf2 not in leaf1.parents
    # Both are siblings under the same in-root parent.
    assert leaf1.parent == leaf2.parent
    assert leaf1.parent.name == mod.PYTEST_TMP_PARENT_NAME


def test_distinct_pids_yield_distinct_leaves(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_root_conftest()

    monkeypatch.setattr(os, "getpid", lambda: 111111)
    leaf_a = mod._session_basetemp_leaf(_PROJECT_ROOT)
    monkeypatch.setattr(os, "getpid", lambda: 222222)
    leaf_b = mod._session_basetemp_leaf(_PROJECT_ROOT)

    assert "111111" in leaf_a.name
    assert "222222" in leaf_b.name
    assert leaf_a != leaf_b
    assert leaf_a not in leaf_b.parents
    assert leaf_b not in leaf_a.parents


def test_computed_parent_resolves_inside_project_root() -> None:
    mod = _load_root_conftest()

    leaf = mod._session_basetemp_leaf(_PROJECT_ROOT)

    # The basetemp parent must resolve inside the project root (root-boundary).
    assert _PROJECT_ROOT in leaf.resolve().parents


def test_hook_falls_back_gracefully_when_parent_unwritable(monkeypatch: pytest.MonkeyPatch) -> None:
    """An ACL-contaminated in-root parent must not hard-fail the suite.

    Simulates a poisoned ``.pytest-tmp/`` (the real failure observed during
    implementation: ``PermissionError`` creating a leaf under a locked parent)
    by forcing ``Path.mkdir`` to raise. The hook must swallow it and leave
    basetemp unset so pytest uses its default temp root.
    """
    mod = _load_root_conftest()

    def _raise_permission(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise PermissionError("simulated ACL-contaminated parent")

    monkeypatch.setattr(Path, "mkdir", _raise_permission)
    config = _ConfigDouble(basetemp=None)

    mod.pytest_configure(config)

    # Graceful fallback: basetemp left unset (pytest default), no exception.
    assert config.option.basetemp is None
