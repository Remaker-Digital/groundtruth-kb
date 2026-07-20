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
    if not raw or not path.parts or path.is_absolute() or ".." in path.parts:
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

    def run_bytes(
        self,
        *args: str,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        completed = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True,
            env={**os.environ, **(env or {})},
        )
        if check and completed.returncode != 0:
            reason = (completed.stderr or completed.stdout).decode("utf-8", errors="replace").strip()
            raise OperationDenied(
                "git_command_failed",
                "Git command failed",
                command=["git", *args],
                returncode=completed.returncode,
                reason=reason[:500],
            )
        return completed

    def resolve_commit(self, source_ref: str) -> str:
        """Resolve one explicit, unambiguous commit reference."""
        if (
            not source_ref
            or source_ref != source_ref.strip()
            or source_ref.startswith("-")
            or any(character in source_ref for character in "\0\r\n")
        ):
            raise OperationDenied("source_ref_invalid", "source ref has an unsafe or ambiguous form")
        if not source_ref.startswith("refs/"):
            exact_namespaces = (
                f"refs/heads/{source_ref}",
                f"refs/tags/{source_ref}",
                f"refs/remotes/{source_ref}",
            )
            exact_matches = sum(
                self.run("show-ref", "--verify", "--quiet", candidate, check=False).returncode == 0
                for candidate in exact_namespaces
            )
            if exact_matches > 1:
                raise OperationDenied(
                    "source_ref_not_commit",
                    "source ref must resolve to one unambiguous commit",
                    source_ref=source_ref,
                )
        resolved = self.run(
            "rev-parse",
            "--verify",
            "--quiet",
            "--end-of-options",
            f"{source_ref}^{{commit}}",
            check=False,
        )
        lines = resolved.stdout.strip().splitlines()
        if (
            resolved.returncode != 0
            or "ambiguous" in resolved.stderr.lower()
            or len(lines) != 1
            or re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", lines[0]) is None
        ):
            raise OperationDenied(
                "source_ref_not_commit",
                "source ref must resolve to one unambiguous commit",
                source_ref=source_ref,
            )
        return lines[0].lower()

    def blob_at(self, commit_sha: str, path: str) -> tuple[str, str, bytes]:
        """Return the mode, object id, and exact blob bytes for one path."""
        listed = self.run_bytes("ls-tree", "-z", "--full-tree", commit_sha, "--", path)
        records = tuple(record for record in listed.stdout.split(b"\0") if record)
        if len(records) != 1 or b"\t" not in records[0]:
            raise OperationDenied(
                "source_path_missing",
                "selected source commit does not contain exactly one path blob",
                commit_sha=commit_sha,
                path=path,
            )
        metadata, encoded_path = records[0].split(b"\t", 1)
        try:
            mode, object_type, object_id = metadata.decode("ascii").split()
            listed_path = encoded_path.decode("ascii")
        except (UnicodeDecodeError, ValueError) as exc:
            raise OperationDenied(
                "source_path_invalid",
                "selected source path metadata is not canonical",
                commit_sha=commit_sha,
                path=path,
            ) from exc
        if listed_path != path or object_type != "blob" or mode not in {"100644", "100755"}:
            raise OperationDenied(
                "source_path_not_regular_file",
                "selected source path must be one exact regular-file blob",
                commit_sha=commit_sha,
                mode=mode,
                path=path,
            )
        payload = self.run_bytes("cat-file", "blob", object_id).stdout
        return mode, object_id.lower(), payload

    def target_status_z(self, path: str) -> bytes:
        return self.run_bytes(
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--",
            f":(top,literal){path}",
        ).stdout

    def unrelated_status_z(self, path: str) -> bytes:
        return self.run_bytes(
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--",
            ".",
            f":(top,exclude,literal){path}",
        ).stdout

    def index_snapshot(self) -> bytes:
        return self.run_bytes("ls-files", "--stage", "-z").stdout

    def restore_worktree_blob(self, path: str, payload: bytes) -> None:
        """Create one absent worktree file from exact committed blob bytes."""
        target = self.root / path
        try:
            target.resolve(strict=False).relative_to(self.root)
            target.parent.resolve(strict=False).relative_to(self.root)
        except ValueError as exc:
            raise OperationDenied("unsafe_scope_path", "restore path escapes repository root", path=path) from exc
        if target.exists() or target.is_symlink():
            raise OperationDenied("restore_target_reappeared", "restore target is no longer absent", path=path)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except OSError as exc:
            raise OperationDenied(
                "restore_target_write_failed",
                "restore target could not be created exclusively",
                path=path,
                reason=str(exc),
            ) from exc
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            target.unlink(missing_ok=True)
            raise OperationDenied(
                "restore_target_write_failed",
                "exact source blob could not be written to the restore target",
                path=path,
                reason=str(exc),
            ) from exc

    def worktree_blob(self, path: str) -> tuple[str, bytes]:
        target = self.root / path
        try:
            payload = target.read_bytes()
        except OSError as exc:
            raise OperationDenied(
                "restored_path_unreadable",
                "restored worktree path could not be read",
                path=path,
                reason=str(exc),
            ) from exc
        object_id = self.run("hash-object", "--no-filters", "--", path).stdout.strip().lower()
        return object_id, payload

    def remove_restored_path(self, path: str) -> None:
        target = self.root / path
        if target.is_file() or target.is_symlink():
            target.unlink()

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
