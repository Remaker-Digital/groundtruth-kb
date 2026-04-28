# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Read-only proof for :meth:`OwnershipResolver.classify_tree`.

Proposal §3.4 — SHA-256-per-file snapshot before/after classify_tree; must be
byte-identical. The tree walker must never write to the target tree.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from groundtruth_kb.project.ownership import OwnershipResolver


def _snapshot(tree_root: Path) -> dict[str, tuple[str, int, float]]:
    """Capture (sha256, size, mtime) for every file under *tree_root*."""
    snap: dict[str, tuple[str, int, float]] = {}
    for dirpath, _dirnames, filenames in os.walk(tree_root):
        for filename in filenames:
            full = Path(dirpath) / filename
            relpath = str(full.relative_to(tree_root)).replace(os.sep, "/")
            data = full.read_bytes()
            snap[relpath] = (
                hashlib.sha256(data).hexdigest(),
                len(data),
                full.stat().st_mtime,
            )
    return snap


def test_classify_tree_is_byte_identical_before_and_after(tmp_path: Path) -> None:
    """SHA-256 + size + mtime snapshot must be identical across a classify_tree call."""
    fixture = tmp_path / "fixture"
    fixture.mkdir()

    # Populate with a variety of files.
    (fixture / "groundtruth.db").write_bytes(b"fake sqlite body\x00\x01\x02")
    (fixture / "README.md").write_text("# fixture\n\ntest content\n", encoding="utf-8")
    (fixture / "src").mkdir()
    (fixture / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (fixture / "bridge").mkdir()
    (fixture / "bridge" / "x-001.md").write_text("# bridge 001\n", encoding="utf-8")
    (fixture / "memory").mkdir()
    (fixture / "memory" / "notes.md").write_text("# notes\n", encoding="utf-8")
    (fixture / "requirements-local.txt").write_text("pkg==1.0\n", encoding="utf-8")

    before = _snapshot(fixture)

    resolver = OwnershipResolver()
    rows = resolver.classify_tree(fixture)
    assert len(rows) > 0, "expected at least one classification row"

    after = _snapshot(fixture)

    assert before == after, "classify_tree mutated the target tree"


def test_classify_tree_never_creates_new_files(tmp_path: Path) -> None:
    """File inventory (by path) is identical before and after classify_tree."""
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "groundtruth.db").write_bytes(b"x")
    (fixture / "a.md").write_text("a\n", encoding="utf-8")
    (fixture / "sub").mkdir()
    (fixture / "sub" / "b.txt").write_text("b\n", encoding="utf-8")

    before_paths = {str(p.relative_to(fixture)) for p in fixture.rglob("*") if p.is_file()}

    resolver = OwnershipResolver()
    resolver.classify_tree(fixture)

    after_paths = {str(p.relative_to(fixture)) for p in fixture.rglob("*") if p.is_file()}
    assert before_paths == after_paths
