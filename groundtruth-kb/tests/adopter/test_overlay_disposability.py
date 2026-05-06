# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Slice 5.5 clean-adopter coverage for disposable ChromaDB overlays."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from groundtruth_kb.db import HAS_CHROMADB
from groundtruth_kb.project.chroma import regenerate
from groundtruth_kb.project.doctor_isolation import run_isolation_checks

requires_chromadb = pytest.mark.skipif(not HAS_CHROMADB, reason="ChromaDB not installed")


@requires_chromadb
def test_chroma_overlay_can_be_deleted_and_regenerated(clean_adopter: tuple[Path, Path]) -> None:
    """A clean adopter can lose the overlay and rebuild it from groundtruth.db."""
    adopter, doctor_root = clean_adopter
    chroma = adopter / ".groundtruth-chroma"

    first = regenerate(adopter)
    assert first.status == "regenerated"
    assert chroma.exists()

    shutil.rmtree(chroma)
    assert not chroma.exists()
    absent_checks = run_isolation_checks(adopter, "dual-agent", product_root=doctor_root)
    absent_by_name = {check.name: check for check in absent_checks}
    assert absent_by_name["isolation:chroma-regeneratable"].status == "pass"

    second = regenerate(adopter)
    assert second.status == "regenerated"
    assert chroma.exists()
    regenerated_checks = run_isolation_checks(adopter, "dual-agent", product_root=doctor_root)
    regenerated_by_name = {check.name: check for check in regenerated_checks}
    assert regenerated_by_name["isolation:chroma-regeneratable"].status == "pass"


def test_chroma_regenerate_rejects_non_adopter_target(tmp_path: Path) -> None:
    """The public API stays bounded to scaffolded adopters."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")

    with pytest.raises(ValueError, match="applications"):
        regenerate(outside)
