"""Narrow subprocess boundary for Git lifecycle operations."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from groundtruth_kb.git_lifecycle.models import OperationDenied

_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9._/-]+$")


def normalize_repo_path(repo_root: Path, value: str) -> str:
    """Return one safe repository-relative path without expanding pathspecs."""
    raw = value.strip().replace("\\", "/")
    while raw.startswith("./"):
        raw = raw[2:]
    path = Path(raw)
    if not raw or path.is_absolute() or ".." in path.parts:
        raise OperationDenied("unsafe_scope_path", "scope path must be repository-relative", path=value)
    if path.parts[0] == ".git" or not _SAFE_COMPONENT.fullmatch(raw):
        raise OperationDenied("unsafe_scope_path", "scope path is not a literal safe path", path=value)
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise OperationDenied("unsafe_scope_path", "scope path escapes repository root", path=value) from exc
    return path.as_posix()


class GitRepository:
    """Git operations constrained to one exact repository root."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        top = self.run("rev-parse", "--show-toplevel").stdout.strip()
        if Path(top).resolve() != self.root:
            raise OperationDenied(
                "repository_root_mismatch",
                "configured root is not the Git worktree root",
                configured=str(self.root),
                discovered=top,
            )

    def run(
        self,
        *args: str,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True,
            text=True,
            env={**os.environ, **(env or {})},
        )
        if check and completed.returncode != 0:
            reason = (completed.stderr or completed.stdout).strip()
            raise OperationDenied(
                "git_command_failed",
                "Git command failed",
                command=["git", *args],
                returncode=completed.returncode,
                reason=reason[:500],
            )
        return completed

    def current_branch(self) -> str:
        branch = self.run("symbolic-ref", "--quiet", "--short", "HEAD", check=False)
        if branch.returncode != 0 or not branch.stdout.strip():
            raise OperationDenied("detached_head", "Git lifecycle operations require an attached branch")
        return branch.stdout.strip()

    def head(self, ref: str = "HEAD") -> str:
        return self.run("rev-parse", "--verify", f"{ref}^{{commit}}").stdout.strip()

    def branch_exists(self, branch: str) -> bool:
        return self.run("show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False).returncode == 0

    def create_branch(self, branch: str, start_point: str) -> None:
        self.run("branch", branch, start_point)

    def checkout(self, branch: str) -> None:
        self.run("checkout", branch)

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        return self.run("merge-base", "--is-ancestor", ancestor, descendant, check=False).returncode == 0

    def status(self, paths: tuple[str, ...] | None = None) -> str:
        args = ["status", "--porcelain=v1", "--untracked-files=all"]
        if paths:
            args.extend(["--", *paths])
        return self.run(*args).stdout

    def is_clean(self, paths: tuple[str, ...] | None = None) -> bool:
        return not self.status(paths).strip()

    def committed_paths(self, commit_sha: str) -> tuple[str, ...]:
        result = self.run("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", commit_sha)
        return tuple(sorted(item for item in result.stdout.split("\0") if item))

    def parents(self, commit_sha: str) -> tuple[str, ...]:
        fields = self.run("show", "-s", "--format=%P", commit_sha).stdout.strip().split()
        return tuple(fields)

    def scoped_commit(self, paths: tuple[str, ...], message: str) -> str:
        """Commit only *paths*, preserving unrelated index and worktree state."""
        if not paths or self.is_clean(paths):
            raise OperationDenied("scope_has_no_changes", "no attributable changes exist in the bound scope")
        self.run("add", "--", *paths)
        committed = self.run("commit", "--only", "-m", message, "--", *paths, check=False)
        if committed.returncode != 0:
            self.run("reset", "-q", "HEAD", "--", *paths, check=False)
            raise OperationDenied(
                "scoped_commit_failed",
                "scoped Git commit failed",
                reason=(committed.stderr or committed.stdout).strip()[:500],
            )
        return self.head()

    def merge_no_ff(self, source_branch: str, message: str) -> str:
        merged = self.run("merge", "--no-ff", "--no-edit", "-m", message, source_branch, check=False)
        if merged.returncode != 0:
            self.run("merge", "--abort", check=False)
            raise OperationDenied(
                "promotion_merge_failed",
                "promotion merge failed without advancing lifecycle state",
                reason=(merged.stderr or merged.stdout).strip()[:500],
            )
        return self.head()
