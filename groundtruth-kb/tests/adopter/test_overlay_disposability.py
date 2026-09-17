"""The search cache is disposable: deleting it loses nothing and regeneration derives it again."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from groundtruth_kb.project import chroma as chroma_module
from groundtruth_kb.project.chroma import regenerate
from groundtruth_kb.project.doctor_isolation import run_isolation_checks


def test_chroma_overlay_can_be_deleted_and_regenerated(clean_adopter, fake_chromadb) -> None:
    adopter, host = clean_adopter
    first = regenerate(adopter)
    assert first.status == "regenerated"
    chroma = adopter / ".groundtruth-chroma"
    assert chroma.is_dir()
    shutil.rmtree(chroma)
    preview = regenerate(adopter, dry_run=True)
    assert preview.status == "would-regenerate" and preview.removed_paths == ()
    assert not chroma.exists(), "a preview never writes"
    checks = {check.name: check for check in run_isolation_checks(adopter, "dual-agent", product_root=host.parent)}
    assert checks["isolation:chroma-regeneratable"].status == "pass"
    second = regenerate(adopter)
    assert second.status == "regenerated" and chroma.is_dir()
    assert not list(adopter.rglob("groundtruth.db"))


def test_chroma_regenerate_rejects_non_application_target(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="groundtruth.toml"):
        regenerate(tmp_path)
    assert not (tmp_path / ".groundtruth-chroma").exists()


def _refuse_authority(url: str) -> None:
    raise AssertionError("no authority read for a refused cache target: " + url)


def test_chroma_regenerate_without_a_registry_accepts_only_the_default_cache(
    tmp_path: Path, fake_chromadb, native_application, monkeypatch
) -> None:
    """An application without ``.gtkb-app-isolation.json`` may regenerate the default cache child and nothing else."""
    application = tmp_path / "Alpha"
    application.mkdir()
    (application / "application.toml").write_text('[application]\nname = "Alpha"\n', encoding="utf-8")
    config = application / "groundtruth.toml"
    config.write_text(f'[groundtruth]\nauthority_url = "{native_application.client.url}"\n', encoding="utf-8")
    cache = application / ".groundtruth-chroma"
    cache.mkdir()
    (cache / "stale.txt").write_text("stale", encoding="utf-8")

    default = regenerate(application)

    assert default.status == "regenerated" and default.chroma_path == cache.resolve()
    assert not (cache / "stale.txt").exists() and (cache / "chroma.sqlite3").is_file()

    scratch = application / "scratch"
    scratch.mkdir()
    (scratch / "sentinel.txt").write_text("relocated cache target without a registry", encoding="utf-8")
    config.write_text(config.read_text(encoding="utf-8") + '\n[search]\nchroma_path = "scratch"\n', encoding="utf-8")
    monkeypatch.setattr(chroma_module, "AuthorityClient", _refuse_authority)
    with pytest.raises(chroma_module.CacheTargetError, match="only the default cache is accepted without a registry"):
        regenerate(application)
    assert (scratch / "sentinel.txt").read_text(encoding="utf-8") == "relocated cache target without a registry"
    assert (cache / "chroma.sqlite3").is_file()
