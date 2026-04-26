"""Release-gate test: .groundtruth/session/snapshots/ must be gitignored.

Per bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2, GO at -006) §2,
W0 writes session-state metadata to .groundtruth/session/snapshots/<id>/manifest.json.
That directory must be gitignored so accidental staging via `git add -A` (which
the existing kb-session-wrap Phase 3 uses) cannot leak session state into git
history.

This test also catches the future class where W0 scope expands beyond
manifest-only without a corresponding policy update: if a transcript file
appears under the snapshots tree, W1's snapshots_non_manifest check fires
at error-severity, but this test ensures the path is at least gitignored
even if W1 hasn't run yet.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


SNAPSHOTS_DIR = ".groundtruth/session/snapshots"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_snapshots_directory_is_gitignored() -> None:
    """`git check-ignore` must report a matching rule for paths under snapshots/."""
    project_root = _project_root()
    test_path = f"{SNAPSHOTS_DIR}/example-session/manifest.json"
    result = subprocess.run(
        ["git", "check-ignore", "-v", test_path],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, (
        f"Expected `{SNAPSHOTS_DIR}/` to be gitignored. "
        f"git check-ignore returned exit {result.returncode}; "
        "session-state files would leak into git history if accidentally staged. "
        "Patch .gitignore to add `.groundtruth/session/snapshots/` "
        "(matches the existing .groundtruth/session/overlays/ precedent)."
    )


def test_snapshots_arbitrary_subpath_is_gitignored() -> None:
    """Defense in depth: any path under snapshots/ must be ignored, not just manifests."""
    project_root = _project_root()
    test_path = f"{SNAPSHOTS_DIR}/another-session/some-future-artifact.txt"
    result = subprocess.run(
        ["git", "check-ignore", "-v", test_path],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, (
        f"Expected arbitrary paths under {SNAPSHOTS_DIR}/ to be gitignored. "
        "If W0 scope ever expands beyond manifest-only, a transcript file "
        "must remain protected from accidental `git add -A` staging."
    )
