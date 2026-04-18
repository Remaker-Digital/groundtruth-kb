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
import subprocess
from dataclasses import dataclass, field
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
