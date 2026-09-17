"""The PostgreSQL kernel cohort is tracked at its canonical paths, byte-identical to review.

WI-7707 brought four files under version control that previously existed only as untracked
working-tree files in a detached worktree. Until then a target git did not track could not enter a
project commit, so five work items — WI-7669, WI-7670, WI-7690, WI-7694 and WI-7714 — could reach
``VERIFIED`` and still never become terminal under canon section 7.

**The digests below are literal constants, deliberately.** The ``-002`` GO makes this a binding
condition. A test that instead read the originating worktree at runtime would be defective three
ways: it could not pass on a fresh clone, because the main tree tracks nothing under
``.worktrees/``; it would break the moment its own purpose was achieved, since the point of tracking
is that the cohort becomes removable; and it would make a committed regression test depend on an
untracked, non-reproducible directory. Pinning the reviewed digests instead proves byte-identity to
what was reviewed, survives cohort removal, and reproduces from a clone.

Each digest was published in ``bridge/gtkb-wi7707-postgres-kernel-cohort-tracking-001.md`` and
independently confirmed by the reviewer at ``-002``.

Re-pinned 2026-09-17 under owner ruling D8 after the independent reviewer confirmed the cohort
changes of the realignment (the explicit repository/scope transition and its integration cases;
``test_postgres_kernel.py`` unchanged). The digest case now measures the LF-normalized working-tree
content - the git-blob identity of the file under this repository's text normalization - so it
proves the reviewed final bytes on any checkout and before as well as after the commit that lands
them; the pinned values are the LF-normalized size and sha256 of those bytes.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

#: path -> (LF-normalized byte size, sha256 of the LF-normalized content) as reviewed. Do not recompute these from disk.
COHORT: dict[str, tuple[int, str]] = {
    "groundtruth-kb/src/groundtruth_kb/postgres_kernel.py": (
        140341,
        "f6dca15ab51b5f44a7b690ee5790e463f0394172924dba980758f3c1cf36437d",
    ),
    "groundtruth-kb/src/groundtruth_kb/postgresql_v1.sql": (
        17823,
        "4b5f8275cec878ade811adf5692436835ef06c147d79a24686a29dad327980fb",
    ),
    "groundtruth-kb/tests/test_postgres_kernel.py": (
        78379,
        "ced464f571211f32f87e15187dc82c96b58c2e5da665d92cd33a7092bb9d5f4c",
    ),
    # Re-pinned under WI-7669: the two side defects in this file were repaired,
    # which changes its blob. A reviewed-preimage pin is re-pinned under review
    # when the file legitimately changes; that is what the pin is for.
    "platform_tests/groundtruth_kb/test_postgres_kernel_integration.py": (
        73588,
        "7d44de9c101b58d639f23a981f59b582ed2a228d302ef4868fa11be1e1c0714e",
    ),
}


def _tracked(rel_path: str) -> bool:
    """True when git resolves the path in the index."""
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", rel_path],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _blob(rel_path: str) -> bytes:
    """The staged blob bytes for a path, not the working-tree file.

    This distinction is load-bearing rather than stylistic. ``core.autocrlf`` is ``true`` in this
    repository and ``.gitattributes`` specifies no ``eol`` rule for these paths, so git rewrites LF
    to CRLF in the working tree on checkout. Measured on already-tracked siblings: ``db.py`` carries
    10,233 CRLF pairs on disk against zero in its blob.

    Hashing the working-tree file would therefore make the pinned digests platform-dependent and
    fail on any fresh clone -- the precise defect the ``-002`` GO's binding condition exists to
    prevent, reached by a different route. The blob is the canonical content and is identical on
    every platform, so the digests below are digests *of the blob*.
    """
    result = subprocess.run(
        ["git", "show", f":{rel_path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
    assert result.returncode == 0, f"git cannot resolve a blob for {rel_path}"
    return result.stdout


def _normalized_content(rel_path: str) -> bytes:
    """The working-tree file with CRLF normalized to LF: the blob git stores for it under ``.gitattributes``.

    Reading the tracked content this way, rather than the staged blob, lets the digest case measure the
    bytes actually present in the tree under test - a qualification clone carries the candidate's changes
    in its working tree while its index is the production HEAD - and yields the same digest on a CRLF or an
    LF checkout and after the change is committed.
    """
    return (REPO_ROOT / rel_path).read_bytes().replace(b"\r\n", b"\n")


@pytest.mark.parametrize("rel_path", sorted(COHORT))
def test_kernel_cohort_files_are_tracked_at_canonical_paths(rel_path: str) -> None:
    """Terminality requires the target to be in the index, per canon section 7."""
    assert (REPO_ROOT / rel_path).is_file(), f"{rel_path} is absent from the working tree"
    assert _tracked(rel_path), f"{rel_path} exists but git does not track it, so it cannot enter a commit"


@pytest.mark.parametrize("rel_path", sorted(COHORT))
def test_kernel_cohort_files_match_the_reviewed_digests(rel_path: str) -> None:
    """Byte-identity to the reviewed content, measured on the LF-normalized tree file so it holds on any clone (D8)."""
    expected_size, expected_sha = COHORT[rel_path]
    data = _normalized_content(rel_path)
    assert len(data) == expected_size, f"{rel_path} normalized size {len(data)}, reviewed at {expected_size}"
    assert hashlib.sha256(data).hexdigest() == expected_sha, f"{rel_path} normalized content differs from reviewed"


@pytest.mark.parametrize("rel_path", sorted(COHORT))
def test_digests_are_platform_independent(rel_path: str) -> None:
    """The reviewed digests must not depend on the checkout's line endings.

    A digest taken from the working tree would differ between a Windows checkout and a POSIX one
    under this repository's ``core.autocrlf=true``. Asserting the blob carries no CRLF pins that
    down: if a future change introduced CRLF into the canonical content, the digests would silently
    become platform-specific again.
    """
    assert b"\r\n" not in _blob(rel_path), f"{rel_path} blob contains CRLF, making its digest platform-dependent"


def test_the_digest_table_is_literal_not_derived() -> None:
    """Guard the binding condition itself.

    The value of this suite depends on the digests being constants. If a later edit made them
    read from the originating worktree, the suite would silently stop proving anything about the
    reviewed bytes and would stop working on a clone.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    body = source.split("COHORT: dict[str, tuple[int, str]] = {", 1)[1].split("\n}", 1)[0]
    assert ".worktrees" not in body, "the digest table must not reference the originating worktree"
    assert "sha256(" not in body, "the digest table must be literal, not computed at import time"


def test_the_cohort_worktree_is_not_required() -> None:
    """The tracked copies stand alone.

    This is the outcome the work item exists to produce: the kernel survives removal of the
    detached worktree it was authored in.
    """
    for rel_path in COHORT:
        assert not rel_path.startswith(".worktrees"), "canonical paths must not live under .worktrees"
        assert _tracked(rel_path), f"{rel_path} must be tracked independently of any worktree"
