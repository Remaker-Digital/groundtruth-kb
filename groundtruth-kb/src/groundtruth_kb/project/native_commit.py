"""Normal project commits with a native check before Git changes the reference.

The disposable index is a Git implementation detail. Canonical review remains
in the domain service; this module creates no approval or publication record.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import quote

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError


class ProjectCommitError(RuntimeError):
    pass


def _git(root: Path, *args: str, env=None, data=None, allow_absent=False) -> bytes:
    try:
        result = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "--literal-pathspecs",
                "-C",
                str(root),
                *args,
            ],
            input=data,
            env=env,
            capture_output=True,
            timeout=120,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProjectCommitError("git_unavailable: Git failed or exceeded its bounded execution time") from error
    if result.returncode and not (allow_absent and result.returncode == 1):
        raise ProjectCommitError(result.stderr.decode("utf-8", errors="replace").strip() or "Git command failed")
    return result.stdout


def _text(root: Path, *args: str, **kwargs) -> str:
    return _git(root, *args, **kwargs).decode("utf-8").strip()


def _index_entries(root: Path, env=None):
    result = {}
    identities = set()
    for entry in _git(root, "ls-files", "--stage", "-z", env=env).split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, object_id, stage = metadata.decode("ascii").split()
        if stage != "0" or mode not in {"100644", "100755"}:
            raise ProjectCommitError("index_not_regular: Resolve unsupported or unmerged index entries first")
        try:
            path = name.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ProjectCommitError("index_ambiguous: The index contains a non-UTF-8 path") from error
        identity = unicodedata.normalize("NFC", path).casefold()
        if identity in identities:
            raise ProjectCommitError("index_ambiguous: The index contains colliding path identities")
        identities.add(identity)
        result[path] = {"mode": mode, "object_id": object_id}
    return result


def _set_entries(root, env, artifacts):
    records = []
    width = len(_text(root, "rev-parse", "HEAD", env=env))
    for name, identity in sorted(artifacts.items()):
        metadata = "0 " + "0" * width if identity is None else identity["mode"] + " " + identity["object_id"]
        records.append((metadata + "\t" + name).encode("utf-8") + b"\0")
    _git(root, "update-index", "-z", "--index-info", env=env, data=b"".join(records))


def commit_reviewed_project(prepared, *, authority_url, project_id, native_context_id, message_file):
    root = Path(prepared["checkout"]["path"]).resolve()
    hooks = Path(prepared["hooks_path"]).resolve()
    parent = prepared["expected_parent"]
    branch = "refs/heads/" + prepared["checkout"]["branch"]
    inherited = {
        name
        for name in os.environ
        if name
        in {
            "GIT_DIR",
            "GIT_WORK_TREE",
            "GIT_COMMON_DIR",
            "GIT_INDEX_FILE",
            "GIT_NAMESPACE",
            "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES",
            "GIT_REPLACE_REF_BASE",
        }
        or (name.startswith("GIT_CONFIG_") and name != "GIT_CONFIG_NOSYSTEM")
    }
    if inherited:
        raise ProjectCommitError("git_environment_redirected: Remove Git repository/index/config overrides")
    if _text(root, "symbolic-ref", "--quiet", "HEAD") != branch or _text(root, "rev-parse", "HEAD") != parent:
        raise ProjectCommitError("checkout_base_changed: The registered branch or parent changed")
    configured = _text(root, "config", "--path", "--get", "core.hooksPath", allow_absent=True)
    if configured not in {".githooks", "./.githooks"} and (not configured or (root / configured).resolve() != hooks):
        raise ProjectCommitError("hooks_redirected: Install the canonical .githooks path before committing")
    reference_hook = hooks / "reference-transaction"
    if not reference_hook.is_file() or b"groundtruth_kb.project.native_commit" not in reference_hook.read_bytes():
        raise ProjectCommitError("commit_hook_missing: The native reference-transaction hook is not installed")
    index = Path(_text(root, "rev-parse", "--path-format=absolute", "--git-path", "index"))
    original = index.read_bytes() if index.exists() else None
    entries = _index_entries(root)
    # Preparation already protects local staged work. Recheck immediately before
    # any local commit operation in case the real index changed afterwards.
    base = {}
    for entry in _git(root, "ls-tree", "-rz", "--full-tree", parent).split(b"\0"):
        if entry:
            metadata, name = entry.split(b"\t", 1)
            mode, _, oid = metadata.decode("ascii").split()
            base[name.decode("utf-8")] = {"mode": mode, "object_id": oid}
    artifacts = prepared["reviewed_artifacts"]
    if any(
        entries.get(name)
        not in (
            base.get(name),
            wanted,
            {**base[name], "mode": wanted["mode"]} if base.get(name) and wanted else wanted,
        )
        for name, wanted in artifacts.items()
    ):
        raise ProjectCommitError("checkout_has_local_work: Preserve the overlapping staged work before committing")
    env = dict(os.environ)
    env.update(
        GIT_NO_REPLACE_OBJECTS="1",
        GTKB_PROJECT_COMMIT_PYTHON=sys.executable,
        GTKB_PROJECT_COMMIT_AUTHORITY=authority_url,
        GTKB_PROJECT_COMMIT_PROJECT=project_id,
        GTKB_PROJECT_COMMIT_CONTEXT=native_context_id,
        GTKB_PROJECT_COMMIT_VERSION=str(prepared["project_version"]),
        GTKB_PROJECT_COMMIT_PARENT=parent,
        GTKB_PROJECT_COMMIT_BRANCH=branch,
        GTKB_PROJECT_COMMIT_CHECKOUT=str(root),
    )
    # Git owns the location; temporary index files are removed on ordinary exit.
    with tempfile.TemporaryDirectory(prefix="gtkb-commit-", dir=index.parent) as temporary:
        disposable = Path(temporary) / "index"
        env["GIT_INDEX_FILE"] = str(disposable)
        _git(root, "read-tree", parent, env=env)
        tracked = set(base)
        paths = sorted(name for name, identity in artifacts.items() if identity is not None or name in tracked)
        _git(root, "add", "--", *paths, env=env)
        for name, identity in artifacts.items():
            if identity is not None:
                _git(
                    root,
                    "update-index",
                    "--chmod=" + ("+x" if identity["mode"] == "100755" else "-x"),
                    "--",
                    name,
                    env=env,
                )
        staged = _index_entries(root, env)
        if any(staged.get(name) != identity for name, identity in artifacts.items()):
            raise ProjectCommitError("reviewed_bytes_changed: The actual staged objects differ from the review")
        _git(
            root,
            "-c",
            "core.hooksPath=" + str(hooks),
            "commit",
            "--file",
            str(message_file),
            env=env,
        )
        candidate = _text(root, "rev-parse", "HEAD", env=env)
        if candidate == parent:
            raise ProjectCommitError("commit_not_confirmed: Git did not advance the context branch")
        # Update just the committed entries in a copy of the real index. Foreign
        # staged content and all working bytes are retained, including on refusal.
        if original is None:
            disposable.unlink(missing_ok=True)
            _git(root, "read-tree", parent, env=env)
        else:
            disposable.write_bytes(original)
        _set_entries(root, env, artifacts)
        lock = index.with_name(index.name + ".lock")
        try:
            with lock.open("xb") as stream:
                if (index.read_bytes() if index.exists() else None) != original:
                    raise ProjectCommitError(
                        "index_changed_after_commit: Preserve the index and confirm the existing candidate " + candidate
                    )
                stream.write(disposable.read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(lock, index)
        except FileExistsError as error:
            raise ProjectCommitError(
                "index_busy_after_commit: Preserve the index and confirm the existing candidate " + candidate
            ) from error
        finally:
            # Only delete a lock we created, never another process's lock.
            if "stream" in locals():
                lock.unlink(missing_ok=True)
        return candidate


def check_reference_transaction(state: str) -> None:
    if state != "prepared" or not os.environ.get("GTKB_PROJECT_COMMIT_PROJECT"):
        return
    prefix = "GTKB_PROJECT_COMMIT_"
    values = {
        name: os.environ[prefix + name]
        for name in (
            "AUTHORITY",
            "PROJECT",
            "CONTEXT",
            "VERSION",
            "PARENT",
            "BRANCH",
            "CHECKOUT",
        )
    }
    root = Path(values["CHECKOUT"]).resolve()
    if Path.cwd().resolve() != root or _text(root, "symbolic-ref", "--quiet", "HEAD") != values["BRANCH"]:
        raise ProjectCommitError("checkout_redirected: The commit callback is outside the registered branch")
    updates = [line.split() for line in sys.stdin.read().splitlines() if line]
    # A normal Git commit separately removes the transient AUTO_MERGE ref after
    # updating HEAD. This deletion carries no new branch or commit authority.
    updates = [
        row
        for row in updates
        if not (len(row) == 3 and row[2] == "AUTO_MERGE" and row[1] == "0" * len(values["PARENT"]))
    ]
    if not updates:
        return
    relevant = [row for row in updates if len(row) == 3 and row[2] in {"HEAD", values["BRANCH"]}]
    if not relevant or len(relevant) != len(updates):
        raise ProjectCommitError("unexpected_reference_update: Only the registered context branch may advance")
    identities = {(old, new) for old, new, _ in relevant}
    if len(identities) != 1:
        raise ProjectCommitError("unexpected_reference_update: The commit reference identities disagree")
    old, new = identities.pop()
    if old != values["PARENT"]:
        raise ProjectCommitError("checkout_base_changed: The prepared parent changed")
    result = AuthorityClient(values["AUTHORITY"]).request(
        "POST",
        f"/v1/projects/{quote(values['PROJECT'], safe='')}/check-commit",
        body={
            "native_context_id": values["CONTEXT"],
            "expected_version": int(values["VERSION"]),
            "expected_parent": old,
            "commit_id": new,
            "index_tree": _text(root, "write-tree"),
        },
    )
    if result.get("status") != "ready_to_update_reference":
        raise ProjectCommitError("fresh_verification_required: The current review no longer permits this commit")


if __name__ == "__main__":
    try:
        check_reference_transaction(sys.argv[1])
    except (
        ProjectCommitError,
        AuthorityClientError,
        OSError,
        KeyError,
        ValueError,
    ) as error:
        sys.stderr.write(f"{error}\n")
        raise SystemExit(1) from error


def reviewed_git_candidates(root, work_item_ids, artifacts):
    """Read possible completed effects from Git without visiting peer checkouts."""
    if not artifacts:
        raise ProjectCommitError("The attempt has no exact reviewed artifact identity")
    required = {f"({work_id})" for work_id in work_item_ids}
    refs = set(_text(root, "for-each-ref", "--format=%(objectname)", "refs/heads/session/").splitlines())
    refs.add(_text(root, "rev-parse", "HEAD"))
    found = []
    for commit_id in sorted(refs):
        message = _text(root, "show", "-s", "--format=%B", commit_id)
        if not required.issubset(set(re.findall(r"\(WI-[A-Za-z0-9_-]+\)", message))):
            continue
        tree = {}
        for entry in _git(root, "ls-tree", "-rz", "--full-tree", commit_id).split(b"\0"):
            if entry:
                metadata, raw_name = entry.split(b"\t", 1)
                try:
                    path = raw_name.decode("utf-8")
                except UnicodeDecodeError as error:
                    raise ProjectCommitError("Git contains a non-UTF-8 path; preserve its identity") from error
                mode, kind, object_id = metadata.decode("ascii").split()
                tree[path] = {"mode": mode, "object_id": object_id} if kind == "blob" else "unsupported"
        if all(tree.get(path) == identity for path, identity in artifacts.items()):
            found.append(commit_id)
    return found
