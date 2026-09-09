"""One git worktree per session context.

Every GT-KB session has historically written into the same working tree and the
same git index as every other session. That is the mechanism behind the worst
incident in this repository's history: commit ``2f688c4ca`` swept 1,756 paths of
other sessions' uncommitted work into a single unreviewed commit and, in doing
so, silently removed a mandatory deny from the bridge compliance gate. It
recurred twice on 2026-09-08, and on the second occasion the only signal that
distinguished one session's bytes from another's was the file modification time.

This module gives each session its own checkout so that a peer's edit can no
longer reach anyone else, and so that a reviewer gets a preimage no peer can
move.

Two properties are deliberate.

**The path is derived, never stored.** ``DCL-INIT-BOUND-SESSION-IDENTITY-001``
fixes session identity in one immutable binding that carries no mutable
lifecycle state, so this module writes no pointer anywhere. The directory name
*is* the session identity, which also means any session can name the owner of
any checkout by reading one row through the shared source of truth rather than
by looking inside another harness's directory.

**A session worktree is always on a branch.** A commit made on a detached HEAD
inside a worktree is reachable only through that worktree; remove the checkout
and it survives only in the reflog. Twenty-eight of the forty-six checkouts that
predate this module are detached.

Nothing here deletes a checkout that holds work, and nothing commits on another
session's behalf. Abandoned work is preserved in place, on its own branch, or it
is left alone.
"""

from __future__ import annotations

import re
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "SESSION_BRANCH_PREFIX",
    "SESSION_CONTEXT_ID_RE",
    "WORKTREES_DIRNAME",
    "SessionWorktreeError",
    "WorktreeState",
    "classify_worktrees",
    "close_worktree",
    "is_session_context_id",
    "live_session_context_ids",
    "open_worktree",
    "session_branch",
    "show_worktree",
    "worktree_path",
]

WORKTREES_DIRNAME = ".worktrees"
SESSION_BRANCH_PREFIX = "session/"

# The binding service mints ``SENV-`` plus a uuid4 hex. Matching the shape lets
# the classifier tell a session checkout from the pre-lifecycle, work-item-named
# directories without consulting the database for every entry.
SESSION_CONTEXT_ID_RE = re.compile(r"^SENV-[0-9a-f]{32}$")

_GIT_TIMEOUT_SECONDS = 120


class SessionWorktreeError(RuntimeError):
    """A session worktree operation could not be completed.

    ``code`` is a stable token for callers that map outcomes to exit codes; the
    message is for the operator.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def is_session_context_id(value: str) -> bool:
    """Return whether ``value`` has the minted session-context-id shape."""
    return bool(SESSION_CONTEXT_ID_RE.match(str(value or "")))


def worktree_path(project_root: Path | str, session_context_id: str) -> Path:
    """Return the derived checkout path for one session context.

    This is the whole of the mapping. There is no registry, no pointer column
    and no marker file, so the path cannot drift from the identity.
    """
    if not is_session_context_id(session_context_id):
        raise SessionWorktreeError(
            "invalid_session_context_id",
            f"{session_context_id!r} is not a session context id; expected the minted SENV- form",
        )
    return Path(project_root).resolve() / WORKTREES_DIRNAME / session_context_id


def session_branch(session_context_id: str) -> str:
    """Return the branch a session's checkout lives on."""
    if not is_session_context_id(session_context_id):
        raise SessionWorktreeError(
            "invalid_session_context_id",
            f"{session_context_id!r} is not a session context id; expected the minted SENV- form",
        )
    return f"{SESSION_BRANCH_PREFIX}{session_context_id}"


def _git(project_root: Path | str, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    """Run one git command. ``--no-optional-locks`` keeps reads off the index lock."""
    return subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=_GIT_TIMEOUT_SECONDS,
        check=check,
    )


@dataclass(frozen=True)
class WorktreeState:
    """Everything known about one checkout, all of it read fresh.

    No field is cached anywhere: the classification is derived from
    ``git worktree list``, one ``git status`` and one ancestry test each time it
    is asked for, per the source-of-truth freshness rule.
    """

    path: Path
    session_context_id: str | None
    branch: str | None
    head: str | None
    binding_live: bool
    tracked_dirty: int
    untracked: int
    head_is_ancestor: bool
    classification: str
    candidate_action: str
    notes: tuple[str, ...] = field(default=())

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path.as_posix(),
            "session_context_id": self.session_context_id,
            "branch": self.branch,
            "head": self.head,
            "binding_live": self.binding_live,
            "tracked_dirty": self.tracked_dirty,
            "untracked": self.untracked,
            "head_is_ancestor": self.head_is_ancestor,
            "classification": self.classification,
            "candidate_action": self.candidate_action,
            "notes": list(self.notes),
        }


def live_session_context_ids(db_path: Path | str) -> frozenset[str]:
    """Return every session context id that still has a binding.

    Retirement deletes the binding row, so presence is liveness. A missing or
    unreadable database yields the empty set, which classifies every checkout as
    unowned and therefore never a removal candidate: the fail-closed direction.
    """
    path = Path(db_path)
    if not path.is_file():
        return frozenset()
    try:
        conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    except sqlite3.Error:
        return frozenset()
    try:
        rows = conn.execute("SELECT session_context_id FROM session_init_bindings").fetchall()
    except sqlite3.Error:
        return frozenset()
    finally:
        conn.close()
    return frozenset(str(row[0]) for row in rows if row and row[0])


def _parse_worktree_list(output: str) -> list[dict[str, str]]:
    """Parse ``git worktree list --porcelain`` into one record per checkout."""
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in output.splitlines():
        line = raw.rstrip()
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    if current:
        records.append(current)
    return records


def _integration_head(project_root: Path | str, integration_ref: str) -> str | None:
    result = _git(project_root, "rev-parse", "--verify", "--quiet", integration_ref)
    head = result.stdout.strip()
    return head or None


def _work_state(path: Path) -> tuple[int, int]:
    """Return (tracked modifications, untracked files) for one checkout."""
    result = _git(path, "status", "--porcelain")
    if result.returncode != 0:
        return (0, 0)
    tracked = 0
    untracked = 0
    for line in result.stdout.splitlines():
        if not line:
            continue
        if line.startswith("??"):
            untracked += 1
        else:
            tracked += 1
    return (tracked, untracked)


def _is_ancestor(project_root: Path | str, head: str | None, integration_head: str | None) -> bool:
    if not head or not integration_head:
        return False
    result = _git(project_root, "merge-base", "--is-ancestor", head, integration_head)
    return result.returncode == 0


def classify_worktrees(
    project_root: Path | str,
    db_path: Path | str,
    *,
    integration_ref: str = "develop",
) -> list[WorktreeState]:
    """Classify every registered checkout plus any orphan under ``.worktrees/``.

    Classifications:

    ``live``
        The name resolves to a binding that still exists. Never a candidate.
    ``abandoned_clean``
        Binding gone, no tracked modification, HEAD already contained in the
        integration head. Removable.
    ``abandoned_with_work``
        Binding gone, but tracked modifications or an unmerged HEAD. The bytes
        must be preserved on the checkout's own branch before it can be removed,
        and never by folding them into someone else's commit.
    ``unowned``
        A registered checkout whose name is not a session context id. Every
        checkout predating this module is in this class. Reported, never removed
        by a session.
    ``orphaned_checkout``
        A directory under ``.worktrees/`` that git does not know about.
    """
    root = Path(project_root).resolve()
    live = live_session_context_ids(db_path)
    integration_head = _integration_head(root, integration_ref)

    listing = _git(root, "worktree", "list", "--porcelain")
    states: list[WorktreeState] = []
    registered: set[Path] = set()

    for record in _parse_worktree_list(listing.stdout):
        raw_path = record.get("worktree")
        if not raw_path:
            continue
        path = Path(raw_path).resolve()
        registered.add(path)
        if path == root:
            continue

        branch = record.get("branch")
        if branch and branch.startswith("refs/heads/"):
            branch = branch[len("refs/heads/") :]
        head = record.get("HEAD")
        name = path.name
        notes: list[str] = []
        if "detached" in record:
            notes.append("detached HEAD: a commit here is reachable only from this checkout")

        tracked_dirty, untracked = _work_state(path)
        head_is_ancestor = _is_ancestor(root, head, integration_head)

        if is_session_context_id(name):
            session_id: str | None = name
            binding_live = name in live
        else:
            session_id = None
            binding_live = False
            notes.append("name is not a session context id; predates the session-worktree lifecycle")

        if session_id is not None and binding_live:
            classification, action = "live", "skip"
        elif session_id is None:
            classification, action = "unowned", "report_only"
        elif tracked_dirty or not head_is_ancestor:
            classification, action = "abandoned_with_work", "preserve_then_close"
        else:
            classification, action = "abandoned_clean", "close_session_worktree"

        states.append(
            WorktreeState(
                path=path,
                session_context_id=session_id,
                branch=branch,
                head=head,
                binding_live=binding_live,
                tracked_dirty=tracked_dirty,
                untracked=untracked,
                head_is_ancestor=head_is_ancestor,
                classification=classification,
                candidate_action=action,
                notes=tuple(notes),
            )
        )

    worktrees_root = root / WORKTREES_DIRNAME
    if worktrees_root.is_dir():
        for child in sorted(worktrees_root.iterdir()):
            if not child.is_dir() or child.resolve() in registered:
                continue
            states.append(
                WorktreeState(
                    path=child.resolve(),
                    session_context_id=child.name if is_session_context_id(child.name) else None,
                    branch=None,
                    head=None,
                    binding_live=False,
                    tracked_dirty=0,
                    untracked=0,
                    head_is_ancestor=False,
                    classification="orphaned_checkout",
                    candidate_action="report_only",
                    notes=("git does not know about this directory",),
                )
            )

    return sorted(states, key=lambda state: state.path.as_posix())


def _state_for(
    project_root: Path,
    path: Path,
    session_context_id: str,
    db_path: Path | str,
    integration_ref: str,
) -> WorktreeState:
    for state in classify_worktrees(project_root, db_path, integration_ref=integration_ref):
        if state.path == path:
            return state
    raise SessionWorktreeError(
        "not_registered",
        f"{path} is not a registered worktree for session {session_context_id}",
    )


def open_worktree(
    project_root: Path | str,
    session_context_id: str,
    *,
    db_path: Path | str,
    base: str | None = None,
    integration_ref: str = "develop",
) -> WorktreeState:
    """Create this session's checkout, or report the one that already exists.

    Idempotent by design: the hook that calls this fires on an init line, and an
    init that arrives twice must not produce a second checkout or an error the
    operator has to reason about.
    """
    root = Path(project_root).resolve()
    path = worktree_path(root, session_context_id)
    branch = session_branch(session_context_id)

    if path.exists():
        try:
            return _state_for(root, path, session_context_id, db_path, integration_ref)
        except SessionWorktreeError as exc:
            raise SessionWorktreeError(
                "path_occupied",
                f"{path} exists but is not a registered worktree; resolve it before opening a session checkout",
            ) from exc

    base_ref = base or integration_ref
    if _integration_head(root, base_ref) is None:
        raise SessionWorktreeError("unknown_base", f"base ref {base_ref!r} does not resolve")

    path.parent.mkdir(parents=True, exist_ok=True)
    branch_exists = _git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0
    args = ["worktree", "add"]
    if not branch_exists:
        args += ["-b", branch]
    args += [str(path)]
    if not branch_exists:
        args += [base_ref]
    else:
        args += [branch]

    result = _git(root, *args)
    if result.returncode != 0:
        raise SessionWorktreeError("git_worktree_add_failed", (result.stderr or result.stdout).strip())
    return _state_for(root, path, session_context_id, db_path, integration_ref)


def show_worktree(
    project_root: Path | str,
    session_context_id: str,
    *,
    db_path: Path | str,
    integration_ref: str = "develop",
) -> WorktreeState | None:
    """Return the state of one session's checkout, or ``None`` when it has none."""
    root = Path(project_root).resolve()
    path = worktree_path(root, session_context_id)
    for state in classify_worktrees(root, db_path, integration_ref=integration_ref):
        if state.path == path:
            return state
    return None


def close_worktree(
    project_root: Path | str,
    session_context_id: str,
    *,
    db_path: Path | str,
    integration_ref: str = "develop",
) -> WorktreeState:
    """Remove a session checkout that holds nothing, and delete its branch.

    Refuses whenever the checkout still holds work. Closing is a convenience for
    the clean case; it is never a way to discard bytes, because discarding
    another session's bytes is the failure this whole module exists to prevent.
    """
    root = Path(project_root).resolve()
    path = worktree_path(root, session_context_id)
    state = show_worktree(root, session_context_id, db_path=db_path, integration_ref=integration_ref)
    if state is None:
        raise SessionWorktreeError("no_worktree", f"session {session_context_id} has no registered worktree")

    if state.tracked_dirty or not state.head_is_ancestor:
        raise SessionWorktreeError(
            "holds_work",
            f"refusing to close {path}: {state.tracked_dirty} tracked modification(s), "
            f"head_is_ancestor={state.head_is_ancestor}. Commit on {state.branch} first; "
            "this command never discards work and never commits on a session's behalf.",
        )

    result = _git(root, "worktree", "remove", str(path))
    if result.returncode != 0:
        raise SessionWorktreeError("git_worktree_remove_failed", (result.stderr or result.stdout).strip())

    branch = session_branch(session_context_id)
    _git(root, "branch", "-d", branch)
    if path.exists() and not any(path.iterdir()):
        shutil.rmtree(path, ignore_errors=True)
    return state


def _registered_context_checkout(project_root: Path, session_context_id: str) -> Path:
    """Resolve only the caller's checkout, without reading peer work products."""
    path = worktree_path(project_root, session_context_id)
    if not path.resolve().is_relative_to(project_root.resolve() / WORKTREES_DIRNAME):
        raise SessionWorktreeError("checkout_outside_root", "The context checkout escapes the worktree root")
    records = _parse_worktree_list(_git(project_root, "worktree", "list", "--porcelain").stdout)
    expected_branch = "refs/heads/" + session_branch(session_context_id)
    if not any(
        Path(record.get("worktree", "")).resolve() == path.resolve() and record.get("branch") == expected_branch
        for record in records
    ):
        raise SessionWorktreeError(
            "checkout_not_registered", "The exact context checkout is not registered on its branch"
        )
    return path


def _artifact_bytes(root: Path, paths: list[str]) -> dict[str, bytes | None]:
    """Read a prevalidated concrete scope without following links outside it."""
    result = {}
    root = root.resolve()
    for relative in paths:
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise SessionWorktreeError("artifact_outside_root", "An artifact escapes its checkout")
        if path.exists() and not path.is_file():
            raise SessionWorktreeError("artifact_not_file", "Work-product transfer requires concrete file paths")
        result[relative] = path.read_bytes() if path.exists() else None
    return result


def _replace_artifacts(root: Path, postimages: dict[str, bytes | None]) -> None:
    """Apply only this operation's named files; restore them on ordinary failure."""
    import os
    import tempfile

    preimages = _artifact_bytes(root, list(postimages))
    written = []

    def put(relative, content):
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise SessionWorktreeError("artifact_outside_root", "An artifact escapes its checkout")
        if content is None:
            path.unlink(missing_ok=True)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".gtkb-write-", delete=False) as output:
                temporary = Path(output.name)
                output.write(content)
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    try:
        for relative, content in postimages.items():
            if content == preimages[relative]:
                continue
            put(relative, content)
            written.append(relative)
    except Exception as error:
        for relative in reversed(written):
            current = _artifact_bytes(root, [relative])[relative]
            if current != postimages[relative]:
                raise SessionWorktreeError(
                    "artifact_changed_during_recovery", "Another writer changed the affected artifact"
                ) from error
            put(relative, preimages[relative])
        raise


def materialize_context_worktree(
    project_root: Path,
    session_context_id: str,
    *,
    expected_head: str,
    artifacts: dict[str, str | None],
    snapshot,
    artifact_source: Path | None = None,
) -> dict[str, object]:
    """Derive this context's workspace from canonical work, never another worker."""
    root = project_root.resolve()
    path = worktree_path(root, session_context_id)
    branch = session_branch(session_context_id)
    if not path.exists():
        branch_head = _git(root, "rev-parse", "--verify", "--quiet", "refs/heads/" + branch)
        if branch_head.returncode == 0 and branch_head.stdout.strip() != expected_head:
            raise SessionWorktreeError("checkout_holds_history", "The context branch has work that must be preserved")
        path.parent.mkdir(parents=True, exist_ok=True)
        args = ["worktree", "add"]
        if branch_head.returncode != 0:
            args += ["-b", branch]
        args += [str(path), branch if branch_head.returncode == 0 else expected_head]
        result = _git(root, *args)
        if result.returncode:
            raise SessionWorktreeError("checkout_open_failed", result.stderr.strip())
    path = _registered_context_checkout(root, session_context_id)
    if _git(path, "rev-parse", "HEAD").stdout.strip() != expected_head:
        raise SessionWorktreeError(
            "checkout_base_changed", "Preserve this checkout's work and continue in a fresh context"
        )
    current = snapshot(sorted(artifacts), root=path)
    base = {}
    if artifacts:
        tree = _git(path, "ls-tree", "-rz", "--full-tree", expected_head, "--", *sorted(artifacts))
        if tree.returncode:
            raise SessionWorktreeError("checkout_base_unavailable", "The checkout base cannot be read")
        for entry in tree.stdout.split("\0"):
            if entry:
                metadata, relative = entry.split("\t", 1)
                base[relative] = metadata.split(" ")[2]
    changed = [
        relative
        for relative, wanted in artifacts.items()
        if current[relative] != wanted and current[relative] != base.get(relative)
    ]
    if changed:
        raise SessionWorktreeError(
            "checkout_has_local_work", "The context checkout contains edits that will not be overwritten"
        )
    source = (artifact_source or root).resolve()
    postimages = _artifact_bytes(source, sorted(artifacts))
    if snapshot(sorted(artifacts), root=source) != artifacts:
        raise SessionWorktreeError("artifact_preimage_changed", "Canonical work changed during context preparation")
    _replace_artifacts(path, postimages)
    if snapshot(sorted(artifacts), root=path) != artifacts:
        raise SessionWorktreeError("checkout_readback_failed", "The materialized context differs from canonical work")
    return {
        "path": str(path),
        "branch": branch,
        "head": expected_head,
        "artifact_preimages": artifacts,
    }


def publish_context_work(
    project_root: Path,
    session_context_id: str,
    *,
    artifact_paths: list[str],
    expected_artifacts: dict[str, str | None],
    snapshot,
    artifact_destination: Path | None = None,
    before_effect=None,
) -> dict[str, str | None]:
    """Copy the caller's scoped work to the canonical work product under a fence."""
    root = project_root.resolve()
    path = _registered_context_checkout(root, session_context_id)
    destination = (artifact_destination or root).resolve()
    if set(expected_artifacts) != set(artifact_paths):
        raise SessionWorktreeError("incomplete_artifact_preimage", "Supply the exact claimed artifact scope")
    result = snapshot(artifact_paths, root=path)
    postimages = _artifact_bytes(path, artifact_paths)
    # Recheck the source as well as the canonical destination before effects.
    if snapshot(artifact_paths, root=path) != result:
        raise SessionWorktreeError(
            "checkout_changed_during_publication", "The caller's work changed during publication"
        )
    if before_effect is not None:
        before_effect()
    current = snapshot(artifact_paths, root=destination)
    if current == result:
        return result  # Exact retry needs no mutation or durable receipt.
    if current != expected_artifacts:
        raise SessionWorktreeError("artifact_preimage_changed", "Canonical work changed after this context loaded it")
    _replace_artifacts(destination, postimages)
    if snapshot(artifact_paths, root=destination) != result:
        raise SessionWorktreeError("artifact_readback_failed", "Published work differs from the caller's artifacts")
    return result


def project_worktree(project_root: Path, project_id: str, *, create: bool = True, refresh_base: bool = False) -> Path:
    """Keep a project's uncommitted work out of the integration checkout."""
    import hashlib

    root = project_root.resolve()
    label = re.sub(r"[^A-Za-z0-9_.-]", "-", project_id)[:48]
    key = label + "-" + hashlib.sha256(project_id.encode("utf-8")).hexdigest()[:12]
    path = root / WORKTREES_DIRNAME / "projects" / key
    if not path.resolve().is_relative_to(root / WORKTREES_DIRNAME / "projects"):
        raise SessionWorktreeError("project_checkout_outside_root", "The project checkout escapes its directory")
    branch = "project/" + key
    if not path.exists():
        if not create:
            raise SessionWorktreeError("project_checkout_missing", "The project's current work checkout is unavailable")
        existing = _git(root, "rev-parse", "--verify", "--quiet", "refs/heads/" + branch)
        if existing.returncode == 0:
            raise SessionWorktreeError("project_branch_preserved", "An existing project branch needs reconciliation")
        head = _git(root, "rev-parse", "--verify", "HEAD")
        if head.returncode:
            raise SessionWorktreeError("project_base_missing", "The project requires a committed repository base")
        path.parent.mkdir(parents=True, exist_ok=True)
        opened = _git(root, "worktree", "add", "-b", branch, str(path), head.stdout.strip())
        if opened.returncode:
            raise SessionWorktreeError("project_checkout_open_failed", opened.stderr.strip())
    records = _parse_worktree_list(_git(root, "worktree", "list", "--porcelain").stdout)
    if not any(
        Path(record.get("worktree", "")).resolve() == path.resolve() and record.get("branch") == "refs/heads/" + branch
        for record in records
    ):
        raise SessionWorktreeError("project_checkout_unregistered", "The exact project checkout is not registered")
    if refresh_base:
        upstream = _git(root, "rev-parse", "--verify", "HEAD")
        if upstream.returncode:
            raise SessionWorktreeError("project_base_missing", "The integration commit is unavailable")
        current = _git(path, "rev-parse", "HEAD").stdout.strip()
        if current != upstream.stdout.strip():
            refreshed = _git(path, "merge", "--ff-only", upstream.stdout.strip())
            if refreshed.returncode:
                raise SessionWorktreeError(
                    "project_base_reconciliation_required",
                    "The committed integration result could not be incorporated without changing project work: "
                    + refreshed.stderr.strip(),
                )
    return path
