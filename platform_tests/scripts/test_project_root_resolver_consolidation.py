"""Regression tests for WI-3354 project-root resolver consolidation."""

from __future__ import annotations

import builtins
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def categorize_module() -> ModuleType:
    return _load_module("assertion_categorize_wi3354", PROJECT_ROOT / "scripts" / "assertion_categorize.py")


@pytest.fixture(scope="module")
def retirement_module() -> ModuleType:
    return _load_module(
        "assertion_retirement_workflow_wi3354",
        PROJECT_ROOT / "scripts" / "assertion_retirement_workflow.py",
    )


@pytest.fixture(scope="module")
def benchmarks_common_module() -> ModuleType:
    return _load_module("benchmarks_common_wi3354", PROJECT_ROOT / "scripts" / "benchmarks" / "common.py")


def _build_worktree_project(tmp_path: Path) -> tuple[Path, Path]:
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")

    ident = [
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "-c",
        "commit.gpgsign=false",
    ]
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "groundtruth.toml").write_text("# synthetic GT-KB root\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "add", "groundtruth.toml"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "commit", "-m", "init"], cwd=canonical, check=True, capture_output=True)
    worktree = canonical / ".claude" / "worktrees" / "test-wt"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", *ident, "worktree", "add", "--detach", str(worktree)],
        cwd=canonical,
        check=True,
        capture_output=True,
    )
    return canonical, worktree


def _worktree_script_paths(worktree: Path) -> tuple[Path, Path, Path]:
    categorize = worktree / "scripts" / "assertion_categorize.py"
    retirement = worktree / "scripts" / "assertion_retirement_workflow.py"
    benchmarks = worktree / "scripts" / "benchmarks" / "common.py"
    benchmarks.parent.mkdir(parents=True, exist_ok=True)
    categorize.parent.mkdir(parents=True, exist_ok=True)
    for path in (categorize, retirement, benchmarks):
        path.touch()
    return categorize, retirement, benchmarks


def _assert_all_resolvers_return(
    categorize_module: ModuleType,
    retirement_module: ModuleType,
    benchmarks_common_module: ModuleType,
    expected: Path,
) -> None:
    assert categorize_module._resolve_project_root(None).resolve() == expected.resolve()
    assert retirement_module._resolve_project_root(None).resolve() == expected.resolve()
    assert benchmarks_common_module._resolve_project_root(None).resolve() == expected.resolve()


def test_resolvers_delegate_to_shared_paths_resolver(
    categorize_module: ModuleType,
    retirement_module: ModuleType,
    benchmarks_common_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from groundtruth_kb.bridge import paths as bridge_paths

    expected = tmp_path / "shared-root"
    expected.mkdir()
    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)
    monkeypatch.setattr(bridge_paths, "resolve_project_root", lambda: expected)

    _assert_all_resolvers_return(categorize_module, retirement_module, benchmarks_common_module, expected)


def test_resolvers_fallback_is_worktree_aware_when_package_unimportable(
    categorize_module: ModuleType,
    retirement_module: ModuleType,
    benchmarks_common_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    canonical, worktree = _build_worktree_project(tmp_path)
    categorize_path, retirement_path, benchmarks_path = _worktree_script_paths(worktree)
    original_import = builtins.__import__

    def fail_bridge_paths_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "groundtruth_kb.bridge.paths":
            raise ImportError("forced bridge paths import failure")
        return original_import(name, *args, **kwargs)

    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path / "no-git"))
    if os.name == "nt":
        monkeypatch.setenv("PATHEXT", "")
    monkeypatch.setattr(builtins, "__import__", fail_bridge_paths_import)
    monkeypatch.setattr(categorize_module, "__file__", str(categorize_path))
    monkeypatch.setattr(retirement_module, "__file__", str(retirement_path))
    monkeypatch.setattr(benchmarks_common_module, "__file__", str(benchmarks_path))

    _assert_all_resolvers_return(categorize_module, retirement_module, benchmarks_common_module, canonical)


def test_resolvers_preserve_explicit_and_env_contract(
    categorize_module: ModuleType,
    retirement_module: ModuleType,
    benchmarks_common_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    explicit = tmp_path / "explicit"
    env_root = tmp_path / "env-root"
    explicit.mkdir()
    env_root.mkdir()

    monkeypatch.setenv("GTKB_PROJECT_ROOT", str(env_root))

    assert categorize_module._resolve_project_root(str(explicit)).resolve() == explicit.resolve()
    assert retirement_module._resolve_project_root(str(explicit)).resolve() == explicit.resolve()
    assert benchmarks_common_module._resolve_project_root(explicit).resolve() == explicit.resolve()

    assert categorize_module._resolve_project_root(None).resolve() == env_root.resolve()
    assert retirement_module._resolve_project_root(None).resolve() == env_root.resolve()
    assert benchmarks_common_module._resolve_project_root(None).resolve() == env_root.resolve()
