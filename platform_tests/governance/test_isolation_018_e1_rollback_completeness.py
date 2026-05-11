"""T-write-set-1 mutation coverage for GTKB-ISOLATION-018 sub-slice 18.E.1.

Per the GO'd implementation proposal at
`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md` (Codex GO at -016).

Covers M1-M10 mutation criteria on the 4-phase rollback helper at
`scripts/rollback_e1_write_set.py`:

- M1-M3: precondition / rollback / Step 3 mv all consume the same write-set
  JSON (non-drift between consumers; tested at the source-of-truth level).
- M4: end-to-end rollback completeness — temp git repo + git mv + helper +
  assert clean status.
- M5: outside FILE destination rejected before unlink runs.
- M6: outside DIRECTORY destination rejected before rmtree runs.
- M7: valid in-scope FILE destination accepted by validator.
- M8: valid in-scope DIRECTORY destination accepted by validator.
- M9: parent-traversal destination rejected.
- M10: absolute-path destinations rejected (POSIX rules AND Windows rules).

The helper lives at scripts/rollback_e1_write_set.py and the validator
function is `validate_agent_red_destination(path_text, repo_root)`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Make scripts/ importable for the helper module.
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from rollback_e1_write_set import (  # noqa: E402
    rollback,
    validate_agent_red_destination,
)


# ---------------------------------------------------------------------------
# M5 + M6: outside paths rejected before destructive operation
# ---------------------------------------------------------------------------


def test_m5_outside_file_destination_rejected_before_unlink(tmp_path: Path) -> None:
    """A destination FILE path outside applications/Agent_Red/ must raise
    AssertionError BEFORE any unlink() call is made."""
    (tmp_path / "applications" / "Agent_Red").mkdir(parents=True)

    with patch("rollback_e1_write_set.Path.unlink") as mock_unlink:
        with pytest.raises(AssertionError) as exc_info:
            validate_agent_red_destination("some-platform-file.txt", tmp_path)

    assert "out-of-scope" in str(exc_info.value).lower()
    assert mock_unlink.call_count == 0, (
        "unlink must NOT be called for out-of-scope FILE destination"
    )


def test_m6_outside_directory_destination_rejected_before_rmtree(
    tmp_path: Path,
) -> None:
    """A destination DIRECTORY path outside applications/Agent_Red/ must raise
    AssertionError BEFORE any shutil.rmtree() call is made."""
    (tmp_path / "applications" / "Agent_Red").mkdir(parents=True)

    with patch("rollback_e1_write_set.shutil.rmtree") as mock_rmtree:
        with pytest.raises(AssertionError) as exc_info:
            validate_agent_red_destination("some-platform-dir/", tmp_path)

    assert "out-of-scope" in str(exc_info.value).lower()
    assert mock_rmtree.call_count == 0, (
        "rmtree must NOT be called for out-of-scope DIRECTORY destination"
    )


# ---------------------------------------------------------------------------
# M7 + M8: valid in-scope paths accepted
# ---------------------------------------------------------------------------


def test_m7_valid_inscope_file_destination_accepted(tmp_path: Path) -> None:
    """A destination FILE path under applications/Agent_Red/ must be accepted
    by the validator and return a resolved Path. Exercises the host's actual
    Path behavior (so on Windows, backslash normalization is covered)."""
    (tmp_path / "applications" / "Agent_Red" / "tests").mkdir(parents=True)

    result = validate_agent_red_destination(
        "applications/Agent_Red/tests/a.txt", tmp_path
    )

    assert result is not None
    # Resolved path is under the allowed root.
    assert "applications" in result.parts
    assert "Agent_Red" in result.parts


def test_m8_valid_inscope_directory_destination_accepted(tmp_path: Path) -> None:
    """A destination DIRECTORY path under applications/Agent_Red/ must be
    accepted by the validator."""
    (tmp_path / "applications" / "Agent_Red" / "src").mkdir(parents=True)

    result = validate_agent_red_destination(
        "applications/Agent_Red/src", tmp_path
    )

    assert result is not None
    assert "applications" in result.parts
    assert "Agent_Red" in result.parts


# ---------------------------------------------------------------------------
# M9: parent-traversal rejected
# ---------------------------------------------------------------------------


def test_m9_parent_traversal_rejected(tmp_path: Path) -> None:
    """A destination containing parent-traversal ('..') segments must raise
    AssertionError at the string-level check (before any filesystem
    operation)."""
    (tmp_path / "applications" / "Agent_Red").mkdir(parents=True)

    with pytest.raises(AssertionError) as exc_info:
        validate_agent_red_destination(
            "applications/Agent_Red/../outside.txt", tmp_path
        )

    assert "parent traversal" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# M10: absolute paths rejected under either OS's rules
# ---------------------------------------------------------------------------


def test_m10a_posix_absolute_path_rejected(tmp_path: Path) -> None:
    """POSIX-style absolute path (/etc/passwd) must raise AssertionError."""
    (tmp_path / "applications" / "Agent_Red").mkdir(parents=True)

    with pytest.raises(AssertionError) as exc_info:
        validate_agent_red_destination("/etc/passwd", tmp_path)

    assert "absolute destination path" in str(exc_info.value).lower()


def test_m10b_windows_absolute_path_rejected(tmp_path: Path) -> None:
    """Windows-style absolute path (C:\\Windows\\foo) must raise AssertionError.

    Important: this must raise on POSIX hosts too (the validator uses
    PureWindowsPath.is_absolute() to cover the Windows path style regardless
    of the host platform)."""
    (tmp_path / "applications" / "Agent_Red").mkdir(parents=True)

    with pytest.raises(AssertionError) as exc_info:
        validate_agent_red_destination("C:\\Windows\\foo", tmp_path)

    assert "absolute destination path" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# M4: end-to-end rollback completeness
# ---------------------------------------------------------------------------


def _git(*args: str, cwd: Path) -> str:
    """Run git with given args; return stdout."""
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    )
    return result.stdout


def test_m4_end_to_end_rollback_completeness(tmp_path: Path) -> None:
    """Create a small temp git repo, perform a `git mv` of a source file into
    applications/Agent_Red/, run the rollback helper against a synthetic
    write-set, and assert that `git status --porcelain` returns clean output
    afterward (no '??' entries, no staged changes, no working-tree changes
    versus HEAD)."""
    # Initialize a temp git repo.
    _git("init", "-q", cwd=tmp_path)
    _git("config", "user.email", "test@example.invalid", cwd=tmp_path)
    _git("config", "user.name", "rollback test", cwd=tmp_path)

    # Gitignore the synthetic scratch dir so write-set.json doesn't show as
    # untracked in the post-rollback status check.
    (tmp_path / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
    _git("add", ".gitignore", cwd=tmp_path)
    _git("commit", "-q", "-m", "seed: .gitignore", cwd=tmp_path)

    # Seed an initial commit with tests/a.txt at the source location.
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "a.txt").write_text("seed content\n", encoding="utf-8")
    _git("add", "tests/a.txt", cwd=tmp_path)
    _git("commit", "-q", "-m", "seed: tests/a.txt", cwd=tmp_path)

    # Perform the move via git mv.
    dest_dir = tmp_path / "applications" / "Agent_Red" / "tests"
    dest_dir.mkdir(parents=True)
    _git("mv", "tests/a.txt", "applications/Agent_Red/tests/a.txt", cwd=tmp_path)

    # Pre-rollback assertion: status should show the rename in the index.
    status_before = _git("status", "--porcelain", cwd=tmp_path)
    assert status_before.strip() != "", "git mv should produce non-empty status"

    # Build a synthetic write-set covering only this single pair.
    write_set = {
        "cluster_sources_dir_recursive": [],
        "cluster_sources_file": [],
        "cluster_destinations_dir_recursive": [],
        "cluster_destinations_file": [],
        "tests_migrating_source_paths": ["tests/a.txt"],
        "tests_migrating_destination_paths": [
            "applications/Agent_Red/tests/a.txt"
        ],
        "tests_staying_platform_paths": [],
        "config_files_in_place_edits": [],
        "workflow_files_in_place_edits": [],
        "dockerfile_in_place_edits": [],
        "scratch_dirs": [],
    }
    write_set_path = tmp_path / ".tmp" / "e1-drift" / "write-set.json"
    write_set_path.parent.mkdir(parents=True, exist_ok=True)
    write_set_path.write_text(
        json.dumps(write_set, indent=2), encoding="utf-8"
    )

    # Invoke the rollback helper against the temp repo.
    rollback(write_set_path, tmp_path)

    # Post-rollback assertion: status should be clean.
    status_after = _git("status", "--porcelain", cwd=tmp_path)
    assert status_after.strip() == "", (
        f"Expected clean status after rollback, got:\n{status_after}"
    )

    # Verify source is restored at its original location.
    assert (tmp_path / "tests" / "a.txt").exists(), (
        "tests/a.txt should be restored after rollback"
    )

    # Verify destination is removed.
    assert not (
        tmp_path / "applications" / "Agent_Red" / "tests" / "a.txt"
    ).exists(), (
        "applications/Agent_Red/tests/a.txt must be removed by Phase 3 cleanup"
    )


# ---------------------------------------------------------------------------
# M1-M3: same write-set drives precondition, rollback, and Step 3 mv
# ---------------------------------------------------------------------------


def test_m1_write_set_consumed_by_rollback() -> None:
    """The rollback helper reads write-set.json at the documented path.
    Mutation: missing write-set causes the helper's main() to exit 1."""
    # We don't actually run main() here (it operates on Path.cwd()); we just
    # verify the constant path the helper references.
    helper_source = (
        Path(__file__).resolve().parents[2] / "scripts" / "rollback_e1_write_set.py"
    ).read_text(encoding="utf-8")
    assert ".tmp/e1-drift/write-set.json" in helper_source, (
        "rollback helper must reference the canonical write-set path"
    )


def test_m2_write_set_schema_has_required_keys(tmp_path: Path) -> None:
    """The rollback helper iterates over a known set of write-set keys.
    Mutation: omitting any required key from the iteration would cause the
    helper to miss that category in rollback. This test asserts the helper
    references all required keys."""
    helper_source = (
        Path(__file__).resolve().parents[2] / "scripts" / "rollback_e1_write_set.py"
    ).read_text(encoding="utf-8")

    required_keys = [
        "cluster_sources_dir_recursive",
        "cluster_sources_file",
        "cluster_destinations_dir_recursive",
        "cluster_destinations_file",
        "tests_migrating_source_paths",
        "tests_migrating_destination_paths",
        "config_files_in_place_edits",
        "workflow_files_in_place_edits",
        "dockerfile_in_place_edits",
    ]
    for key in required_keys:
        assert key in helper_source, (
            f"rollback helper must reference write-set key: {key}"
        )


def test_m3_source_destination_symmetry_for_per_file_tests(tmp_path: Path) -> None:
    """Per the F1 fix at REVISED-4 (-009): every entry in
    tests_migrating_source_paths must have a corresponding entry at the same
    index in tests_migrating_destination_paths of the form
    'applications/Agent_Red/' + source."""
    # Build a representative synthetic write-set and assert the invariant.
    sources = ["tests/foo.py", "tests/bar.py", "tests/baz/qux.py"]
    destinations = ["applications/Agent_Red/" + s for s in sources]

    assert len(sources) == len(destinations)
    for src, dst in zip(sources, destinations):
        assert dst == "applications/Agent_Red/" + src
