# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GT-KB upgrade rollback receipts.

Records the post-merge state needed to safely roll back a ``gt project
upgrade --apply`` operation. Receipt-mode resolution and write happen in
specific positions in the upgrade flow:

1. **Pre-flight** — :func:`resolve_receipt_mode` runs before any branch
   creation. It asks git (via ``git check-ignore --no-index``) whether the
   tentative receipt path would be ignored. Exit 0 → ``filesystem`` mode.
   Exit 1 → ``tracked`` mode. Any other exit → :class:`UnexpectedCheckIgnoreExit`.
2. **Payload commits** — normal file changes. The receipt is NOT written
   here.
3. **Merge** — payload branch merges into target branch, producing
   ``merge_commit``. Recorded in memory.
4. **Receipt write** — :func:`write_receipt` runs AFTER ``merge_commit``
   exists:

   - ``filesystem`` mode: write JSON file only. Not committed.
   - ``tracked`` mode: write JSON file, then make a SEPARATE post-merge
     receipt commit. The receipt commit is NOT part of the payload merge
     tree, so ``git revert -m 1 <merge_commit>`` cleanly reverts only the
     payload.

Authorizing bridge: ``bridge/gtkb-rollback-receipts-014.md`` (Codex GO,
2026-04-18). Full design: ``bridge/gtkb-rollback-receipts-013.md``.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal, TypedDict

ReceiptMode = Literal["tracked", "filesystem"]


class UnexpectedCheckIgnoreExit(RuntimeError):
    """Raised when ``git check-ignore --no-index`` exits with an unexpected code.

    Expected exits are 0 (path is ignored) and 1 (path is not ignored). Any
    other code indicates git-environment malfunction (missing binary, no
    repository, etc.) and is surfaced to pre-flight as a hard failure so
    the upgrade does not proceed with a guessed receipt mode.
    """

    def __init__(self, returncode: int, stderr: str) -> None:
        super().__init__(f"git check-ignore returned unexpected exit code {returncode}: {stderr!r}")
        self.returncode = returncode
        self.stderr = stderr


class ReceiptJSON(TypedDict):
    """v1 receipt schema. Written once per ``gt project upgrade --apply``.

    Fields:

    - ``schema_version``: must be ``"v1"``.
    - ``receipt_id``: opaque unique identifier (UUID or similar).
    - ``merge_commit``: full SHA of the payload merge commit.
    - ``target_branch``: branch the merge landed on.
    - ``from_version``: ``scaffold_version`` of the adopter project before
      the upgrade.
    - ``to_version``: ``__version__`` of GT-KB at upgrade time.
    - ``mode``: ``"tracked"`` or ``"filesystem"``.
    - ``created_at``: ISO-8601 UTC timestamp.
    - ``artifact_classes_touched``: list of artifact class names affected
      (e.g. ``["hook", "rule", "settings-hook-registration"]``).
    """

    schema_version: Literal["v1"]
    receipt_id: str
    merge_commit: str
    target_branch: str
    from_version: str
    to_version: str
    mode: ReceiptMode
    created_at: str
    artifact_classes_touched: list[str]


@dataclass
class ResolvedMode:
    """Pre-flight resolution result with supporting context."""

    mode: ReceiptMode
    receipt_path: Path
    adopter_root: Path
    notes: list[str] = field(default_factory=list)


def resolve_receipt_mode(adopter_root: Path, receipt_path: Path) -> ResolvedMode:
    """Resolve receipt mode from the adopter's current ``.gitignore`` state.

    Runs ``git check-ignore --no-index -- <receipt_path>`` against
    ``adopter_root``. Exit 0 means the path is ignored → ``filesystem``
    mode. Exit 1 means the path is not ignored → ``tracked`` mode. Any
    other exit raises :class:`UnexpectedCheckIgnoreExit`.

    The ``.gitignore`` state is NOT mutated by this call or by the upgrade
    flow. Adopters opt in to tracked receipts by adding the documented
    4-line re-inclusion block manually (see
    ``docs/reference/upgrade-receipts.md``).
    """
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--", str(receipt_path)],
        cwd=str(adopter_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return ResolvedMode(
            mode="filesystem",
            receipt_path=receipt_path,
            adopter_root=adopter_root,
            notes=["receipt path is covered by .gitignore — filesystem mode"],
        )
    if result.returncode == 1:
        return ResolvedMode(
            mode="tracked",
            receipt_path=receipt_path,
            adopter_root=adopter_root,
            notes=["receipt path not ignored — tracked mode"],
        )
    raise UnexpectedCheckIgnoreExit(result.returncode, result.stderr)


def write_receipt(
    resolved: ResolvedMode,
    receipt: ReceiptJSON,
) -> str:
    """Write ``receipt`` per ``resolved.mode``. Called AFTER merge_commit exists.

    In ``filesystem`` mode: writes the JSON file only. Returns the string
    ``"filesystem"``.

    In ``tracked`` mode: writes the JSON file, stages it, and makes a
    SEPARATE receipt commit on the adopter's current branch. Returns the
    SHA of the receipt commit.

    Precondition: the payload merge commit exists at ``receipt["merge_commit"]``
    and is reachable from the current branch tip. The caller is responsible
    for constructing a consistent receipt dict before calling this function.
    """
    resolved.receipt_path.parent.mkdir(parents=True, exist_ok=True)
    resolved.receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if resolved.mode == "filesystem":
        return "filesystem"

    subprocess.run(
        ["git", "add", "--", str(resolved.receipt_path)],
        cwd=str(resolved.adopter_root),
        check=True,
    )
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f"gt: upgrade receipt for {receipt['merge_commit'][:10]}",
        ],
        cwd=str(resolved.adopter_root),
        check=True,
    )
    sha_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(resolved.adopter_root),
        capture_output=True,
        text=True,
        check=True,
    )
    return sha_result.stdout.strip()


# ---------------------------------------------------------------------------
# C3: gtkb-upgrade-rollback — receipt-consuming API
# ---------------------------------------------------------------------------
# Per bridge/gtkb-upgrade-rollback-006.md GO. Consumes the receipts written by
# write_receipt() above to perform a safe ``git revert -m 1 <merge_commit>``
# rollback of the payload merge. No changes to receipt-writing behavior.


_MERGE_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_VALID_MODES = frozenset({"tracked", "filesystem"})


class ReceiptNotFoundError(RuntimeError):
    """No receipt matches the requested ID (or no receipts exist at all)."""


class ReceiptMalformedError(RuntimeError):
    """Receipt JSON file exists but is missing a required field, has wrong type, or fails validation."""


class ReceiptSchemaVersionMismatchError(ReceiptMalformedError):
    """Receipt has a schema_version other than the one C3 knows how to consume (currently 'v1')."""


class NotAMergeCommitError(RuntimeError):
    """Receipt references a commit that is not a two-parent merge commit."""


class MergeCommitNotInHistoryError(RuntimeError):
    """Receipt's merge_commit is not reachable from the current HEAD (already reverted, rebased, or branched)."""


class DirtyWorkingTreeError(RuntimeError):
    """Working tree has uncommitted changes; rollback refuses for safety."""


class RollbackFailedError(RuntimeError):
    """``git revert -m 1 <merge_commit>`` failed or produced unexpected state."""


@dataclass(frozen=True)
class FileEntry:
    """One file in a RollbackPlan.files_to_revert list.

    Status letter uses git's `--name-status` convention:
        A=added, M=modified, D=deleted, R=renamed, C=copied, T=type-changed.
    """

    status: str
    path: str


@dataclass(frozen=True)
class RollbackPlan:
    """What ``execute_rollback()`` would do for a given receipt."""

    receipt: ReceiptJSON
    merge_commit: str
    files_to_revert: list[FileEntry]


@dataclass(frozen=True)
class RollbackResult:
    """Outcome of a successful ``execute_rollback()`` call."""

    receipt_id: str
    merge_commit: str
    mode: Literal["revert-no-commit", "revert-commit"]
    commit_sha: str | None  # None when mode='revert-no-commit'
    files_reverted: list[FileEntry]


# ---------------------------------------------------------------------------
# Receipt IO + validation
# ---------------------------------------------------------------------------


_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "schema_version",
        "receipt_id",
        "merge_commit",
        "target_branch",
        "from_version",
        "to_version",
        "mode",
        "created_at",
        "artifact_classes_touched",
    }
)


def read_receipt(receipt_path: Path) -> ReceiptJSON:
    """Parse + validate a single receipt JSON file against the v1 schema.

    Raises ``ReceiptNotFoundError`` if the file doesn't exist,
    ``ReceiptSchemaVersionMismatchError`` if ``schema_version`` is not ``"v1"``,
    ``ReceiptMalformedError`` for any other schema violation.

    Validation applied:
        - All 9 required fields present (ReceiptMalformedError if missing).
        - ``schema_version == "v1"`` literal match.
        - ``receipt_id`` non-empty string.
        - ``merge_commit`` matches ``^[0-9a-f]{40}$`` (full lowercase SHA).
        - ``target_branch`` non-empty string.
        - ``from_version`` / ``to_version`` non-empty strings.
        - ``mode`` ∈ {'tracked', 'filesystem'}.
        - ``created_at`` parses via ``datetime.fromisoformat()``.
        - ``artifact_classes_touched`` is a list (may be empty).
    """
    if not receipt_path.exists():
        raise ReceiptNotFoundError(f"Receipt file does not exist: {receipt_path}")

    try:
        raw = json.loads(receipt_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReceiptMalformedError(f"Receipt JSON at {receipt_path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ReceiptMalformedError(f"Receipt JSON at {receipt_path} must be an object, got {type(raw).__name__}")

    missing = _REQUIRED_FIELDS - set(raw.keys())
    if missing:
        raise ReceiptMalformedError(f"Receipt at {receipt_path} missing required fields: {sorted(missing)}")

    schema_version = raw.get("schema_version")
    if schema_version != "v1":
        raise ReceiptSchemaVersionMismatchError(
            f"Receipt at {receipt_path} has schema_version={schema_version!r}; only 'v1' is supported."
        )

    def _require_nonempty_str(field_name: str) -> None:
        value = raw.get(field_name)
        if not isinstance(value, str) or not value:
            raise ReceiptMalformedError(
                f"Receipt at {receipt_path}: field {field_name!r} must be a non-empty string, got {value!r}"
            )

    for field_name in ("receipt_id", "target_branch", "from_version", "to_version"):
        _require_nonempty_str(field_name)

    merge_commit = raw.get("merge_commit")
    if not isinstance(merge_commit, str) or not _MERGE_SHA_RE.match(merge_commit):
        raise ReceiptMalformedError(
            f"Receipt at {receipt_path}: merge_commit must be a 40-char lowercase hex SHA, got {merge_commit!r}"
        )

    mode = raw.get("mode")
    if mode not in _VALID_MODES:
        raise ReceiptMalformedError(
            f"Receipt at {receipt_path}: mode must be one of {sorted(_VALID_MODES)}, got {mode!r}"
        )

    created_at = raw.get("created_at")
    if not isinstance(created_at, str):
        raise ReceiptMalformedError(
            f"Receipt at {receipt_path}: created_at must be a string, got {type(created_at).__name__}"
        )
    try:
        # Accept 'Z' suffix per RFC 3339 (Python 3.11+ fromisoformat handles this).
        datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReceiptMalformedError(
            f"Receipt at {receipt_path}: created_at {created_at!r} is not parseable as ISO-8601: {exc}"
        ) from exc

    artifact_classes = raw.get("artifact_classes_touched")
    if not isinstance(artifact_classes, list):
        raise ReceiptMalformedError(
            f"Receipt at {receipt_path}: artifact_classes_touched must be a list, got {type(artifact_classes).__name__}"
        )

    # All validated; return as ReceiptJSON.
    return ReceiptJSON(
        schema_version=schema_version,
        receipt_id=raw["receipt_id"],
        merge_commit=merge_commit,
        target_branch=raw["target_branch"],
        from_version=raw["from_version"],
        to_version=raw["to_version"],
        mode=mode,
        created_at=created_at,
        artifact_classes_touched=artifact_classes,
    )


def list_receipts(root: Path) -> list[ReceiptJSON]:
    """Return all valid receipts under ``.claude/upgrade-receipts/active/``.

    Sorted newest-first by ``created_at`` descending, with tie-break on
    ``receipt_id`` descending for determinism.

    Malformed receipt files are raised as ``ReceiptMalformedError`` —
    there is no silent skipping. If an adopter wants to clear broken
    receipts, they should remove the file rather than let the API drop it.
    """
    active_dir = root / ".claude" / "upgrade-receipts" / "active"
    if not active_dir.exists():
        return []

    receipts: list[ReceiptJSON] = [read_receipt(p) for p in sorted(active_dir.glob("*.json")) if p.is_file()]
    # Sort by (created_at, receipt_id) descending. Tuple ordering gives us
    # both keys in one pass.
    receipts.sort(key=lambda r: (r["created_at"], r["receipt_id"]), reverse=True)
    return receipts


def find_latest_receipt(root: Path) -> ReceiptJSON | None:
    """Return the newest receipt under ``.claude/upgrade-receipts/active/``, or None if none exist."""
    receipts = list_receipts(root)
    return receipts[0] if receipts else None


def find_receipt_by_id(root: Path, receipt_id: str) -> ReceiptJSON:
    """Return the receipt with the given ``receipt_id``, or raise ``ReceiptNotFoundError``."""
    for receipt in list_receipts(root):
        if receipt["receipt_id"] == receipt_id:
            return receipt
    raise ReceiptNotFoundError(f"No receipt with id {receipt_id!r} under {root}")


# ---------------------------------------------------------------------------
# Rollback planning + execution
# ---------------------------------------------------------------------------


def _is_clean_working_tree(root: Path) -> bool:
    """Return True iff ``git status --porcelain`` is empty in ``root``."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() == ""


def _assert_merge_commit_reachable(root: Path, merge_commit: str) -> None:
    """Raise ``MergeCommitNotInHistoryError`` if ``merge_commit`` is not reachable from HEAD."""
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", merge_commit, "HEAD"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise MergeCommitNotInHistoryError(
            f"Receipt references merge_commit {merge_commit!r}, but that commit "
            f"is not reachable from HEAD. Have you already reverted, rebased, "
            f"or branched away from the upgrade?"
        )


def _assert_is_two_parent_merge(root: Path, merge_commit: str) -> None:
    """Raise ``NotAMergeCommitError`` if ``merge_commit`` is not a 2-parent merge."""
    result = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", merge_commit],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=True,
    )
    tokens = result.stdout.strip().split()
    # Output format: '<merge_sha> <parent1_sha> <parent2_sha>' → 3 tokens.
    if len(tokens) != 3:
        raise NotAMergeCommitError(
            f"Receipt references {merge_commit!r} but it has "
            f"{len(tokens) - 1} parent(s); expected exactly 2 (a --no-ff "
            f"merge commit). Receipt may be corrupt or point at the wrong SHA."
        )


def _payload_files(root: Path, merge_commit: str) -> list[FileEntry]:
    """Return the list of files in the payload merge, per ``--first-parent`` diff.

    Uses ``git diff --name-status <merge>^1 <merge>`` per Codex F1: this is
    correct for ``--no-ff`` merge commits (unlike ``git show --name-only``
    which returns empty for them).
    """
    result = subprocess.run(
        ["git", "diff", "--name-status", f"{merge_commit}^1", merge_commit],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=True,
    )
    entries: list[FileEntry] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            # Rename/copy entries use "R100\told\tnew" format; take status + target path.
            parts = line.split("\t")
            if len(parts) >= 3:
                entries.append(FileEntry(status=parts[0][0], path=parts[-1]))
            continue
        status, path = parts
        entries.append(FileEntry(status=status[0], path=path))
    return entries


def plan_rollback(root: Path, *, receipt_id: str | None = None) -> RollbackPlan:
    """Compute a rollback plan without executing it.

    Validates:
        1. Receipt exists + schema-validates (via ``read_receipt``).
        2. Receipt's ``merge_commit`` is a two-parent merge (``NotAMergeCommitError`` if not).
        3. Receipt's ``merge_commit`` is reachable from HEAD (``MergeCommitNotInHistoryError`` if not).

    Does NOT require a clean working tree — planning is read-only.
    ``execute_rollback()`` will enforce the clean-tree precondition.
    """
    receipt: ReceiptJSON
    if receipt_id is None:
        latest = find_latest_receipt(root)
        if latest is None:
            raise ReceiptNotFoundError(f"No receipts found under {root / '.claude' / 'upgrade-receipts' / 'active'}")
        receipt = latest
    else:
        receipt = find_receipt_by_id(root, receipt_id)

    merge_commit = receipt["merge_commit"]
    _assert_is_two_parent_merge(root, merge_commit)
    _assert_merge_commit_reachable(root, merge_commit)

    files = _payload_files(root, merge_commit)
    return RollbackPlan(receipt=receipt, merge_commit=merge_commit, files_to_revert=files)


def execute_rollback(
    root: Path,
    plan: RollbackPlan,
    *,
    commit: bool = False,
) -> RollbackResult:
    """Execute the rollback for a previously-computed ``RollbackPlan``.

    Runs ``git revert -m 1 <merge_commit>``. If ``commit=False`` (default),
    adds ``--no-commit`` so the revert stays staged for adopter review.
    If ``commit=True``, the revert is auto-committed with a generated message.

    Preconditions:
        - Working tree clean (``git status --porcelain`` empty). Raises
          ``DirtyWorkingTreeError`` if not.
        - All plan-time invariants (merge-commit shape, reachability) still hold.
          Re-verified here for safety.

    Raises ``RollbackFailedError`` if the underlying ``git revert`` fails.
    """
    if not _is_clean_working_tree(root):
        raise DirtyWorkingTreeError(
            f"Working tree at {root} has uncommitted changes. Rollback refuses "
            f"to proceed. Stash, commit, or clean the working tree first."
        )

    # Re-verify merge-shape + reachability (guards against state-drift since plan_rollback).
    _assert_is_two_parent_merge(root, plan.merge_commit)
    _assert_merge_commit_reachable(root, plan.merge_commit)

    revert_cmd = ["git", "revert", "-m", "1", plan.merge_commit]
    if not commit:
        revert_cmd.append("--no-commit")

    result = subprocess.run(
        revert_cmd,
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RollbackFailedError(f"git revert failed (exit {result.returncode}): {result.stderr.strip()}")

    commit_sha: str | None = None
    if commit:
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
        commit_sha = sha_result.stdout.strip()

    mode: Literal["revert-no-commit", "revert-commit"] = "revert-commit" if commit else "revert-no-commit"
    return RollbackResult(
        receipt_id=plan.receipt["receipt_id"],
        merge_commit=plan.merge_commit,
        mode=mode,
        commit_sha=commit_sha,
        files_reverted=list(plan.files_to_revert),
    )
