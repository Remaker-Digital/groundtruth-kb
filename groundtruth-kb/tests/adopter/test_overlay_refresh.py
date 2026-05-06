# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Slice 5.5 clean-adopter coverage for ChromaDB overlay refresh."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import HAS_CHROMADB
from groundtruth_kb.project.chroma import regenerate
from groundtruth_kb.project.doctor_isolation import run_isolation_checks

requires_chromadb = pytest.mark.skipif(not HAS_CHROMADB, reason="ChromaDB not installed")


@requires_chromadb
def test_chroma_regenerate_replaces_stale_overlay(clean_adopter: tuple[Path, Path]) -> None:
    """Regeneration deletes stale cache files and leaves the doctor check green."""
    adopter, doctor_root = clean_adopter
    chroma = adopter / ".groundtruth-chroma"
    chroma.mkdir(parents=True, exist_ok=True)
    stale = chroma / "stale.txt"
    stale.write_text("not canonical", encoding="utf-8")

    result = regenerate(adopter)

    assert result.status == "regenerated"
    assert "stale.txt" in result.removed_paths
    assert not stale.exists()
    assert chroma.exists()
    checks = run_isolation_checks(adopter, "dual-agent", product_root=doctor_root)
    by_name = {check.name: check for check in checks}
    assert by_name["isolation:chroma-regeneratable"].status == "pass"


def test_chroma_regenerate_dry_run_json_does_not_write(
    clean_adopter: tuple[Path, Path],
    runner: CliRunner,
) -> None:
    """The public CLI exposes a non-mutating diff surface for refresh planning."""
    adopter, _doctor_root = clean_adopter
    chroma = adopter / ".groundtruth-chroma"
    assert not chroma.exists()

    result = runner.invoke(
        main,
        ["project", "chroma", "regenerate", "--dir", str(adopter), "--dry-run", "--json"],
    )

    assert result.exit_code == 0, f"output={result.output!r} exc={result.exception!r}"
    payload = json.loads(result.output)
    assert payload["status"] == "would-regenerate"
    assert payload["dry_run"] is True
    assert payload["chroma_path"] == str(chroma.resolve())
    assert not chroma.exists()


def test_chroma_regenerate_reports_optional_dependency_skip(
    clean_adopter: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing optional ChromaDB support is an explicit skip, not a silent pass."""
    from groundtruth_kb.project import chroma as chroma_module

    adopter, _doctor_root = clean_adopter
    chroma = adopter / ".groundtruth-chroma"
    chroma.mkdir(parents=True, exist_ok=True)
    marker = chroma / "existing.txt"
    marker.write_text("leave intact when regeneration cannot run", encoding="utf-8")
    monkeypatch.setattr(chroma_module._db_module, "HAS_CHROMADB", False)

    result = chroma_module.regenerate(adopter)

    assert result.status == "skipped"
    assert result.errors == ("ChromaDB not installed",)
    assert marker.exists()
