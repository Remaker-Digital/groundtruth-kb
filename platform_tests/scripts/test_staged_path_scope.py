"""Tests for scripts/check_staged_path_scope.py (WI-6690)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.check_staged_path_scope import check_staged_scope, matches_declared_pattern


def test_matches_declared_pattern() -> None:
    assert matches_declared_pattern("scripts/foo.py", "scripts/foo.py")
    assert matches_declared_pattern("scripts/foo.py", "scripts/*.py")
    assert matches_declared_pattern("src/groundtruth_kb/db.py", "src/**/*.py")
    assert not matches_declared_pattern("other/bar.py", "scripts/*.py")


def test_exact_declared_scope_passes(tmp_path: Path) -> None:
    declared = ["scripts/check_staged_path_scope.py", "platform_tests/scripts/test_staged_path_scope.py"]
    staged = ["scripts/check_staged_path_scope.py", "platform_tests/scripts/test_staged_path_scope.py"]

    code, msg = check_staged_scope(tmp_path, explicit_paths=declared, staged_paths_override=staged)
    assert code == 0
    assert "all 2 staged file(s) match declared scope" in msg


def test_subset_declared_scope_passes(tmp_path: Path) -> None:
    """Subset is legitimate for partial work (discriminating test)."""
    declared = ["scripts/check_staged_path_scope.py", "platform_tests/scripts/test_staged_path_scope.py"]
    staged = ["scripts/check_staged_path_scope.py"]

    code, msg = check_staged_scope(tmp_path, explicit_paths=declared, staged_paths_override=staged)
    assert code == 0
    assert "1 of 2 declared path(s) staged (valid subset" in msg


def test_extra_staged_path_fails_and_names_extras(tmp_path: Path) -> None:
    declared = ["scripts/check_staged_path_scope.py"]
    staged = [
        "scripts/check_staged_path_scope.py",
        "groundtruth-kb/src/groundtruth_kb/project/doctor.py",
    ]

    code, msg = check_staged_scope(tmp_path, explicit_paths=declared, staged_paths_override=staged)
    assert code == 1
    assert "1 staged path(s) exceed declared scope" in msg
    assert "groundtruth-kb/src/groundtruth_kb/project/doctor.py" in msg
    assert "Remedy: Unstage extra files using 'git restore --staged <file>'" in msg


def test_no_declared_scope_warns_and_passes(tmp_path: Path) -> None:
    staged = ["unrelated/scratch.txt"]

    code, msg = check_staged_scope(tmp_path, explicit_paths=None, staged_paths_override=staged)
    assert code == 0
    assert "WARN staged-path scope" in msg
    assert "comparison not performed" in msg


def test_empty_staged_passes(tmp_path: Path) -> None:
    code, msg = check_staged_scope(tmp_path, explicit_paths=["foo.py"], staged_paths_override=[])
    assert code == 0
    assert "no files staged in git index" in msg


def test_retired_packets_cannot_supply_comparison_scope(tmp_path: Path) -> None:
    state_dir = tmp_path / ".gtkb-state" / "implementation-authorizations"
    state_dir.mkdir(parents=True, exist_ok=True)
    packet_file = state_dir / "current.json"
    packet_data = {
        "bridge_id": "gtkb-sample-thread",
        "target_path_globs": ["scripts/alpha.py", "scripts/beta.py"],
    }
    packet_file.write_text(json.dumps(packet_data), encoding="utf-8")

    staged = ["scripts/alpha.py"]
    code, msg = check_staged_scope(tmp_path, explicit_paths=None, staged_paths_override=staged)
    assert code == 0
    assert "comparison not performed" in msg
    assert "gtkb-sample-thread" not in msg
    code, msg = check_staged_scope(tmp_path, explicit_paths=["other/file.py"], staged_paths_override=staged)
    assert code == 1
    assert "scripts/alpha.py" in msg
    assert "gtkb-sample-thread" not in msg
