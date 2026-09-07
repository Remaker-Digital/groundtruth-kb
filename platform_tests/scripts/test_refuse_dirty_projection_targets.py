"""Spec-derived tests for scripts/refuse_dirty_projection_targets.py (WI-5999).

Maps to the approved implementation proposal verification plan:

- clean set proceeds
- dirty set refuses and lists paths
- unnamed ``--force`` is rejected
- named ``--force-dirty`` overrides only listed paths
- git porcelain includes untracked files
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "refuse_dirty_projection_targets.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("refuse_dirty_projection_targets", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


helper = _load_module()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _init_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    _git(root, "config", "user.email", "wi5999@example.com")
    _git(root, "config", "user.name", "WI-5999 Test")
    tracked = root / "projections" / "tracked.txt"
    tracked.parent.mkdir()
    tracked.write_text("committed\n", encoding="utf-8")
    _git(root, "add", "projections/tracked.txt")
    _git(root, "commit", "-q", "-m", "seed")
    return root


def test_clean_set_proceeds(tmp_path: Path) -> None:
    root = _init_repo(tmp_path)
    code = helper.main(["--project-root", str(root), "projections/tracked.txt"])
    assert code == 0


def test_dirty_tracked_path_refuses_and_lists(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _init_repo(tmp_path)
    (root / "projections" / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    code = helper.main(["--project-root", str(root), "projections/tracked.txt"])
    captured = capsys.readouterr()
    assert code == helper.DIRTY_REFUSE_EXIT
    assert "projections/tracked.txt" in captured.err
    assert (root / "projections" / "tracked.txt").read_text(encoding="utf-8") == "dirty\n"


def test_untracked_path_is_dirty(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _init_repo(tmp_path)
    (root / "projections" / "new.txt").write_text("untracked\n", encoding="utf-8")
    code = helper.main(["--project-root", str(root), "projections/new.txt"])
    captured = capsys.readouterr()
    assert code == helper.DIRTY_REFUSE_EXIT
    assert "projections/new.txt" in captured.err


def test_bare_force_is_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _init_repo(tmp_path)
    (root / "projections" / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    code = helper.main(["--project-root", str(root), "--force", "projections/tracked.txt"])
    captured = capsys.readouterr()
    assert code == helper.USAGE_REFUSE_EXIT
    assert "bare --force is forbidden" in captured.err


def test_force_dirty_without_naming_path_refuses(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _init_repo(tmp_path)
    (root / "projections" / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    code = helper.main(
        ["--project-root", str(root), "--force-dirty", "projections/other.txt", "projections/tracked.txt"]
    )
    captured = capsys.readouterr()
    assert code == helper.DIRTY_REFUSE_EXIT
    assert "projections/tracked.txt" in captured.err


def test_force_dirty_with_exact_path_proceeds(tmp_path: Path) -> None:
    root = _init_repo(tmp_path)
    (root / "projections" / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    code = helper.main(
        ["--project-root", str(root), "--force-dirty", "projections/tracked.txt", "projections/tracked.txt"]
    )
    assert code == 0


def test_force_dirty_overrides_only_listed_paths(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _init_repo(tmp_path)
    (root / "projections" / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    (root / "projections" / "new.txt").write_text("untracked\n", encoding="utf-8")
    code = helper.main(
        [
            "--project-root",
            str(root),
            "--force-dirty",
            "projections/tracked.txt",
            "projections/tracked.txt",
            "projections/new.txt",
        ]
    )
    captured = capsys.readouterr()
    assert code == helper.DIRTY_REFUSE_EXIT
    assert "projections/new.txt" in captured.err
    assert "projections/tracked.txt" not in captured.err.split("dirty targets", 1)[-1]


def test_comma_separated_force_dirty_covers_all_dirty_paths(tmp_path: Path) -> None:
    root = _init_repo(tmp_path)
    (root / "projections" / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    (root / "projections" / "new.txt").write_text("untracked\n", encoding="utf-8")
    code = helper.main(
        [
            "--project-root",
            str(root),
            "--force-dirty",
            "projections/tracked.txt,projections/new.txt",
            "projections/tracked.txt",
            "projections/new.txt",
        ]
    )
    assert code == 0
