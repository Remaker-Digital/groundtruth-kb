"""GTKB-ISOLATION-018 Sub-slice 18.E.1 — 4-phase rollback helper.

Authored per the GO'd implementation proposal at
`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md` (Codex GO at -016).

The helper reverses the effects of Step 3 (atomic `git mv` of ~1,423 files) plus
Step 4/5/5b in-place edits. It reads the canonical write-set generated in
Step 0.5 (`.tmp/e1-drift/write-set.json`) and applies a 4-phase rollback:

Phase 1: reset the index for every path in the write-set (un-stages adds/deletes).
Phase 2: restore source-side paths and in-place-edited paths from HEAD.
Phase 3: explicitly remove destination-side untracked artifacts created by `git mv`.
         Containment-checked: only paths under applications/Agent_Red/ are touched.
Phase 4: prune ephemeral parent directories created by the slice (currently only
         applications/Agent_Red/config/).

The helper is invoked manually if Step 3-6 partial failure leaves the working
tree in a poisoned state. After Step 7 commit lands, rollback is `git revert
<commit-sha>` (single inverse-commit) and this helper is not needed.

Containment is the critical safety mechanism: `validate_agent_red_destination`
runs BEFORE both `unlink()` and `shutil.rmtree()` for every destination path,
rejecting absolute paths (POSIX and Windows rules), parent-traversal, and any
path that does not resolve under repo_root/applications/Agent_Red/.

Cross-platform: forward-slash repository-relative input is accepted regardless
of host OS. `Path.resolve() + Path.relative_to()` is used for real filesystem
containment, not lexical string prefix.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath


def validate_agent_red_destination(path_text: str, repo_root: Path) -> Path:
    """Validate that path_text is a repository-relative destination under
    applications/Agent_Red/. Return the resolved Path on success.

    Cross-platform: accepts forward-slash repository-relative input regardless
    of host OS. Uses `Path.resolve() + Path.relative_to()` to perform real
    filesystem containment, so Windows backslash normalization does not cause
    false negatives.

    Raises AssertionError when path_text:
    - is absolute under either POSIX or Windows path rules
    - contains parent-traversal segments ('..')
    - resolves outside the repo_root/applications/Agent_Red/ subtree

    The exception is raised via `raise AssertionError(...)` (not bare `assert`)
    so the safety check survives `python -O` (which strips bare asserts).
    """
    # 1. Reject absolute paths under EITHER OS's rules.
    if PurePosixPath(path_text).is_absolute() or PureWindowsPath(path_text).is_absolute():
        raise AssertionError(f"Refusing to remove absolute destination path: {path_text}")

    # 2. Reject parent traversal at the string layer (before any filesystem operation).
    normalized_parts = path_text.replace("\\", "/").split("/")
    if ".." in normalized_parts:
        raise AssertionError(f"Refusing to remove destination path with parent traversal: {path_text}")

    # 3. Resolve relative to repo_root and check containment via relative_to().
    candidate = (repo_root / path_text).resolve(strict=False)
    allowed_root = (repo_root / "applications" / "Agent_Red").resolve(strict=False)
    try:
        candidate.relative_to(allowed_root)
    except ValueError:
        raise AssertionError(f"Refusing to remove out-of-scope destination path: {path_text}")

    return candidate


def rollback(write_set_path: Path, repo_root: Path) -> None:
    """Apply the 4-phase rollback per the GO'd proposal.

    Phase 1: reset index for ALL write-set paths.
    Phase 2: restore source-side and in-place-edited paths from HEAD.
    Phase 3: explicitly remove destination-side untracked artifacts (with
             containment validation).
    Phase 4: prune ephemeral parent dirs created by the slice.
    """
    write_set = json.loads(write_set_path.read_text(encoding="utf-8"))

    # ---------- Phase 1: reset index for ALL write-set paths ----------
    all_index_paths: list[str] = []
    for key in (
        "cluster_sources_dir_recursive",
        "cluster_sources_file",
        "cluster_destinations_dir_recursive",
        "cluster_destinations_file",
        "tests_migrating_source_paths",
        "tests_migrating_destination_paths",
        "config_files_in_place_edits",
        "workflow_files_in_place_edits",
        "dockerfile_in_place_edits",
    ):
        all_index_paths.extend(write_set.get(key, []))

    for p in all_index_paths:
        subprocess.run(
            ["git", "restore", "--staged", "--", p],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )

    # ---------- Phase 2: restore source-side and in-place-edited paths from HEAD ----------
    sources_to_restore: list[str] = []
    for key in (
        "cluster_sources_dir_recursive",
        "cluster_sources_file",
        "tests_migrating_source_paths",
        "config_files_in_place_edits",
        "workflow_files_in_place_edits",
        "dockerfile_in_place_edits",
    ):
        sources_to_restore.extend(write_set.get(key, []))

    for p in sources_to_restore:
        subprocess.run(
            ["git", "checkout", "--", p],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )

    # ---------- Phase 3: explicitly remove destination-side untracked artifacts ----------
    # Each path is containment-validated BEFORE any destructive operation.
    destinations_to_clean: list[str] = []
    for key in (
        "cluster_destinations_dir_recursive",
        "cluster_destinations_file",
        "tests_migrating_destination_paths",
    ):
        destinations_to_clean.extend(write_set.get(key, []))

    for p in destinations_to_clean:
        # Containment check FIRST — applies to BOTH unlink and rmtree branches.
        resolved_path = validate_agent_red_destination(p, repo_root)
        if resolved_path.is_symlink() or resolved_path.is_file():
            resolved_path.unlink(missing_ok=True)
        elif resolved_path.is_dir():
            shutil.rmtree(resolved_path, ignore_errors=True)

    # ---------- Phase 4: prune ephemeral parent dirs created by the slice ----------
    # applications/Agent_Red/config/ is the only NEW parent created by this slice;
    # other destination parents (src, admin, widget, branding, tests) had their
    # entire subtrees handled in Phase 3 via cluster_destinations_dir_recursive
    # or tests_migrating_destination_paths.
    ephemeral_parents = [repo_root / "applications" / "Agent_Red" / "config"]

    for path in ephemeral_parents:
        if path.is_dir():
            try:
                path.rmdir()  # succeeds only if empty
            except OSError:
                pass  # not empty — leave it

    print("Multi-phase rollback complete.")


def main() -> int:
    repo_root = Path.cwd()
    write_set_path = Path(".tmp/e1-drift/write-set.json")
    if not write_set_path.exists():
        print(
            f"ERROR: write-set not found at {write_set_path}. Run Step 0 and Step 0.5 first to generate it.",
            file=sys.stderr,
        )
        return 1
    rollback(write_set_path, repo_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
