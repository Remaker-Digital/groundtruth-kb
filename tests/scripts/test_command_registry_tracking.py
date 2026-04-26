"""Release-gate test: the GT-KB command registry path must be tracked
in git, not gitignored.

Per the GT-KB command-surface architectural plan (GO'd at
bridge/gtkb-command-surface-004.md), the dispatcher hook (CS-2) reads
the command registry from .claude/commands/registry.json. The
.claude/* blanket ignore in .gitignore would normally hide that path
from fresh checkouts and adopter scaffolding. CS-1.5 patches the
ignore list to track the registry; this test ensures the patch
remains in effect.

A regression here means: a fresh clone or `gt project upgrade` adopter
would not receive the command registry. The dispatcher hook would
either fail to load or fall back to default behavior, breaking the
::cmd surface silently.

CS-1.5 ref: bridge/gtkb-command-surface-cs1-5-001.md (NEW),
            bridge/gtkb-command-surface-cs1-5-002.md (GO).
"""

from __future__ import annotations

import subprocess
from pathlib import Path


REGISTRY_PATH = ".claude/commands/registry.json"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_registry_path_exists() -> None:
    """The registry file must exist in the working tree."""
    path = _project_root() / REGISTRY_PATH
    assert path.exists(), (
        f"Command registry not present at {REGISTRY_PATH}. "
        "CS-1.5 must commit an empty stub so CS-2's dispatcher has "
        "a known starting state."
    )


def test_registry_path_is_not_gitignored() -> None:
    """`git check-ignore` must report no ignore rule for the registry path.

    A non-zero exit from `git check-ignore` means the path is NOT
    ignored, which is what we want.
    """
    result = subprocess.run(
        ["git", "check-ignore", "-v", REGISTRY_PATH],
        capture_output=True,
        text=True,
        cwd=_project_root(),
    )
    assert result.returncode != 0, (
        f"Command registry at {REGISTRY_PATH} is gitignored: "
        f"{result.stdout.strip()}. "
        "Adopter scaffolding and fresh checkouts will not receive the "
        "registry. Patch .gitignore to add a negation rule for "
        "`.claude/commands/registry.json` (see "
        "bridge/gtkb-command-surface-003.md §3.2)."
    )


def test_registry_path_is_tracked_in_git() -> None:
    """`git ls-files` must include the registry path.

    Even if check-ignore reports no rule, the file must actually be
    tracked (added + committed) for fresh checkouts to receive it.
    """
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", REGISTRY_PATH],
        capture_output=True,
        text=True,
        cwd=_project_root(),
    )
    assert result.returncode == 0, (
        f"Command registry at {REGISTRY_PATH} is not tracked in git: "
        f"{result.stderr.strip()}. "
        "CS-1.5 must `git add` the registry stub after patching "
        ".gitignore."
    )


def test_registry_loose_md_files_remain_local() -> None:
    """Defense in depth: loose *.md files under .claude/commands/ must
    remain ignored (the tracked-vs-local distinction per architectural
    plan §6).

    If a future change broadens the negation pattern to `*.md`, the
    six existing local-only command files would become tracked,
    surprising both the developer and adopters. This test catches that.
    """
    test_path = ".claude/commands/__cs1-5-test-loose-md__.md"
    project_root = _project_root()
    full_path = project_root / test_path
    full_path.write_text("# CS-1.5 test artifact; safe to delete\n")
    try:
        result = subprocess.run(
            ["git", "check-ignore", test_path],
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        assert result.returncode == 0, (
            f"Loose .md files under .claude/commands/ are no longer ignored. "
            "The tracked-vs-local distinction per architectural plan "
            "§6 has been broken. If this is intentional, update the "
            "architectural plan and CS-7 disposition; if not, narrow "
            "the negation pattern."
        )
    finally:
        full_path.unlink(missing_ok=True)
