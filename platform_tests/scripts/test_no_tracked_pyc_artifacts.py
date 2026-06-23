"""Regression guard: no __pycache__ or .pyc artifacts may appear in the git index.

WI-4715 was created after WI-4701 observed a tracked Python cache artifact under
the generated Codex bridge-skill adapter surface. The current checkout has no
tracked cache artifacts, and .gitignore already covers both the __pycache__/
directory pattern and *.py[cod] file patterns. This test guards against future
regressions that would reintroduce tracked cache artifacts.

Spec-to-test mapping:
  GOV-FILE-BRIDGE-AUTHORITY-001:
      Lifecycle evidence — this test file and the post-implementation report
      form the durable artifact trail required by bridge governance.
      (test_no_tracked_pyc_files, test_pycache_dirs_are_gitignored,
       test_pyc_files_are_gitignored)
  GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001:
      WI-4715 is the authorized work item; tests document its closure.
      (test_no_tracked_pyc_files)
  DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001:
      Tests derive from the spec-to-test plan in the bridge proposal and
      must be executed against the implementation for VERIFIED verdict.
      (test_no_tracked_pyc_files, test_pyc_files_are_gitignored,
       test_pycache_dirs_are_gitignored)
  GOV-STANDING-BACKLOG-001:
      Closes WI-4715 without adding unapproved successor WIs.
      (test_no_tracked_pyc_files)
  GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 /
  DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001:
      Preserves the finding and closure evidence as a durable test artifact
      rather than a harness-local observation.
      (all tests)
  ADR-CODEX-HOOK-PARITY-FALLBACK-001:
      Representative Codex bridge-skill helper cache path must remain ignored.
      (test_pycache_dirs_are_gitignored, test_pyc_files_are_gitignored)
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_no_tracked_pyc_files() -> None:
    """git ls-files must not return any __pycache__ directory or .pyc file.

    WI-4715 closure guard: if any cache artifact becomes tracked in the index,
    this test fails and the regression is visible before CI promotion.

    Note on exit semantics: `git ls-files` exits 0 whether or not it finds any
    files; it lists tracked paths on stdout. A non-zero exit would indicate a
    git error, not an absence of matches. The assertion is on the filtered output
    being empty, not on the exit code of the downstream grep step.
    """
    project_root = _project_root()
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, f"git ls-files failed with exit {result.returncode}: {result.stderr}"

    cache_pattern = re.compile(r"(__pycache__|\.pyc$)")
    tracked_cache_files = [line for line in result.stdout.splitlines() if cache_pattern.search(line)]

    assert tracked_cache_files == [], (
        "Tracked __pycache__ or .pyc artifacts found in the git index. "
        "These must not be committed. Remove them with "
        "`git rm --cached <path>` and ensure .gitignore covers the pattern. "
        "Offending paths:\n  " + "\n  ".join(tracked_cache_files)
    )


def test_pycache_dirs_are_gitignored() -> None:
    """`git check-ignore` must match the representative Codex bridge-helper cache path.

    This asserts that the __pycache__/ ignore rule in .gitignore applies to the
    generated Codex bridge-skill adapter surface — the exact surface where
    WI-4701 observed the original tracked-cache regression.
    """
    project_root = _project_root()
    test_path = ".codex/skills/bridge/helpers/__pycache__/protected_write.cpython-314.pyc"
    result = subprocess.run(
        ["git", "check-ignore", "-v", test_path],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, (
        f"Expected Codex bridge-helper __pycache__ path to be gitignored. "
        f"git check-ignore returned exit {result.returncode} for '{test_path}'. "
        "If .gitignore no longer covers __pycache__ under .codex/skills/, "
        "patch it to add the pattern. "
        f"stdout: {result.stdout!r}  stderr: {result.stderr!r}"
    )


def test_pyc_files_are_gitignored() -> None:
    """`git check-ignore` must match a representative top-level .pyc path.

    The *.py[cod] pattern in .gitignore covers .pyc, .pyo, and .pyd files
    globally. This test asserts that coverage is still active so a future
    .gitignore edit cannot accidentally remove it without breaking this guard.
    """
    project_root = _project_root()
    test_path = "groundtruth-kb/src/groundtruth_kb/example_module.pyc"
    result = subprocess.run(
        ["git", "check-ignore", "-v", test_path],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, (
        f"Expected .pyc files to be globally gitignored via *.py[cod]. "
        f"git check-ignore returned exit {result.returncode} for '{test_path}'. "
        "If .gitignore no longer covers *.py[cod] globally, patch it to "
        "restore the pattern. "
        f"stdout: {result.stdout!r}  stderr: {result.stderr!r}"
    )
