from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "update_wiki_pages.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("update_wiki_pages", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_wiki_page_name_maps_in_root_source_slug_to_github_wiki_name() -> None:
    module = _load_module()

    assert module.wiki_page_name(Path("release-health.md")) == "Release-Health.md"
    assert module.wiki_page_name(Path("azure-enterprise-readiness.md")) == "Azure-Enterprise-Readiness.md"
    assert module.wiki_page_name(Path("Home.md")) == "Home.md"


def test_compare_pages_distinguishes_current_missing_and_different(tmp_path: Path) -> None:
    module = _load_module()
    source_dir = tmp_path / "groundtruth-kb" / "docs" / "wiki"
    wiki_dir = tmp_path / ".tmp" / "groundtruth-kb.wiki"
    source_dir.mkdir(parents=True)
    wiki_dir.mkdir(parents=True)
    (source_dir / "release-health.md").write_text("# Release Health\n", encoding="utf-8")
    (source_dir / "azure-enterprise-readiness.md").write_text("# Azure\n", encoding="utf-8")
    (source_dir / "Home.md").write_text("# Home\n", encoding="utf-8")
    (wiki_dir / "Release-Health.md").write_text("# Release Health\n", encoding="utf-8")
    (wiki_dir / "Azure-Enterprise-Readiness.md").write_text("# Azure stale\n", encoding="utf-8")

    rows = {row["wiki_page"]: row for row in module.compare_pages(source_dir, wiki_dir)}

    assert rows["Release-Health.md"]["status"] == "current"
    assert rows["Home.md"]["status"] == "missing"
    assert "Azure-Enterprise-Readiness.md" not in rows


def test_update_pages_copies_from_source_without_pushing(tmp_path: Path) -> None:
    module = _load_module()
    source_dir = tmp_path / "groundtruth-kb" / "docs" / "wiki"
    wiki_dir = tmp_path / ".tmp" / "groundtruth-kb.wiki"
    source_dir.mkdir(parents=True)
    (source_dir / "release-health.md").write_text("# Release Health\n\nCurrent.\n", encoding="utf-8")

    rows = module.update_pages(source_dir, wiki_dir)

    assert rows[0]["planned_action"] == "write"
    assert rows[0]["post_update_status"] == "current"
    assert (wiki_dir / "Release-Health.md").read_text(encoding="utf-8") == "# Release Health\n\nCurrent.\n"


def test_wiki_paths_must_stay_inside_project_root(tmp_path: Path) -> None:
    module = _load_module()

    with pytest.raises(ValueError, match="outside project root"):
        module._resolve_in_root(tmp_path.parent / "outside-wiki", tmp_path)


def test_script_no_longer_targets_agent_red_temp_wiki() -> None:
    text = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "agent-red.wiki" not in text
    assert "Agent Red wiki" not in text
    assert "groundtruth-kb.wiki" in text


def test_source_pages_only_includes_intentional_release_wiki_sources(tmp_path: Path) -> None:
    module = _load_module()
    source_dir = tmp_path / "groundtruth-kb" / "docs" / "wiki"
    source_dir.mkdir(parents=True)
    (source_dir / "release-health.md").write_text("# Release Health\n", encoding="utf-8")
    (source_dir / "azure-enterprise-readiness.md").write_text("# Azure draft\n", encoding="utf-8")
    (source_dir / "scratch.md").write_text("# Scratch\n", encoding="utf-8")

    assert [path.name for path in module.source_pages(source_dir)] == ["release-health.md"]


def test_readmes_reference_main_branch_and_release_health_source() -> None:
    root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    package_readme = (REPO_ROOT / "groundtruth-kb" / "README.md").read_text(encoding="utf-8")

    assert "branch=develop" not in root_readme
    assert "branch=main" in root_readme
    assert "groundtruth-kb/docs/wiki/release-health.md" in root_readme
    assert "docs/wiki/release-health.md" in package_readme
    assert "scripts/update_wiki_pages.py compare" in package_readme
    assert "Agent Red" not in package_readme
