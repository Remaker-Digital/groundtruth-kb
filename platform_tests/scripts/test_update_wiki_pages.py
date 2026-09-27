from __future__ import annotations

import hashlib
import importlib.util
import json
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
    assert module.wiki_page_name(Path("settings.md")) == "Settings.md"
    assert module.wiki_page_name(Path("status.md")) == "Status.md"
    assert module.wiki_page_name(Path("azure-enterprise-readiness.md")) == "Azure-Enterprise-Readiness.md"
    assert module.wiki_page_name(Path("Home.md")) == "Home.md"
    assert module.wiki_page_name(Path("_Sidebar.md")) == "_Sidebar.md"
    assert module.wiki_page_name(Path("_Footer.md")) == "_Footer.md"


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
    assert rows["Azure-Enterprise-Readiness.md"]["status"] == "different"


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


def test_source_pages_only_includes_intentional_product_wiki_sources(tmp_path: Path) -> None:
    module = _load_module()
    source_dir = tmp_path / "groundtruth-kb" / "docs" / "wiki"
    source_dir.mkdir(parents=True)
    (source_dir / "release-health.md").write_text("# Release Health\n", encoding="utf-8")
    (source_dir / "azure-enterprise-readiness.md").write_text("# Azure draft\n", encoding="utf-8")
    (source_dir / "Home.md").write_text("# Home\n", encoding="utf-8")
    (source_dir / "_Sidebar.md").write_text("# Sidebar\n", encoding="utf-8")
    (source_dir / "settings.md").write_text("# Settings\n", encoding="utf-8")
    (source_dir / "status.md").write_text("# GTKB status\n", encoding="utf-8")
    (source_dir / "scratch.md").write_text("# Scratch\n", encoding="utf-8")

    assert {path.name for path in module.source_pages(source_dir)} == {
        "_Sidebar.md",
        "azure-enterprise-readiness.md",
        "Home.md",
        "release-health.md",
        "settings.md",
        "status.md",
    }


@pytest.mark.parametrize("status", ["missing", "different", "current"])
@pytest.mark.parametrize(
    "asset_name", ["assets/gtkb-home-empty-state.png", "assets/gtkb-settings-general.png", "assets/gtkb-status.png"]
)
def test_compare_pages_checks_asset_bytes_and_hashes(tmp_path: Path, status: str, asset_name: str) -> None:
    module = _load_module()
    source_dir = tmp_path / "source"
    wiki_dir = tmp_path / "wiki"
    source_asset = source_dir / asset_name
    source_asset.parent.mkdir(parents=True)
    content = b"\x89PNG\r\n\x1a\n\x00\xfffixture\r\n"
    source_asset.write_bytes(content)
    if status != "missing":
        target = wiki_dir / asset_name
        target.parent.mkdir(parents=True)
        target.write_bytes(content if status == "current" else b"stale image")

    rows = module.compare_pages(source_dir, wiki_dir)

    assert len(rows) == 1
    assert rows[0]["kind"] == "asset"
    assert rows[0]["wiki_page"] == asset_name
    assert rows[0]["status"] == status
    assert rows[0]["source_sha256"] == hashlib.sha256(content).hexdigest()
    if status == "current":
        assert rows[0]["wiki_sha256"] == rows[0]["source_sha256"]
    elif status == "missing":
        assert rows[0]["wiki_sha256"] == ""
    else:
        assert rows[0]["wiki_sha256"] == hashlib.sha256(b"stale image").hexdigest()


def test_update_pages_preserves_allowlisted_asset_bytes_only(tmp_path: Path) -> None:
    module = _load_module()
    source_dir = tmp_path / "source"
    wiki_dir = tmp_path / "wiki"
    (source_dir / "assets").mkdir(parents=True)
    assets = {
        "assets/gtkb-home-empty-state.png": b"\x89PNG\r\n\x1a\n\x00\xffhome\r\n",
        "assets/gtkb-settings-general.png": b"\x89PNG\r\n\x1a\n\x00\xfesettings\r\n",
        "assets/gtkb-status.png": b"\x89PNG\r\n\x1a\n\x00\xfdstatus\r\n",
    }
    for name, content in assets.items():
        (source_dir / name).write_bytes(content)
    (source_dir / "assets" / "private-capture.png").write_bytes(b"do not publish")
    (source_dir / "settings.md").write_text("# Settings\n", encoding="utf-8")

    rows = module.update_pages(source_dir, wiki_dir)

    assert len(rows) == 4
    assert all(row["post_update_status"] == "current" for row in rows)
    for name, content in assets.items():
        assert (wiki_dir / name).read_bytes() == content
    assert not (wiki_dir / "assets" / "private-capture.png").exists()
    assert (wiki_dir / "Settings.md").read_text(encoding="utf-8") == "# Settings\n"


def test_cli_dry_run_does_not_create_asset_checkout(tmp_path: Path, capsys) -> None:
    module = _load_module()
    source_dir = tmp_path / "groundtruth-kb" / "docs" / "wiki"
    wiki_dir = tmp_path / ".tmp" / "groundtruth-kb.wiki"
    (source_dir / "assets").mkdir(parents=True)
    (source_dir / "assets" / "gtkb-home-empty-state.png").write_bytes(b"\x89PNG\r\n\xff")
    (source_dir / "assets" / "gtkb-settings-general.png").write_bytes(b"\x89PNG\r\n\xfe")
    (source_dir / "assets" / "gtkb-status.png").write_bytes(b"\x89PNG\r\n\xfd")
    (source_dir / "Home.md").write_text("# Home\n", encoding="utf-8")

    assert module.main(["update", "--project-root", str(tmp_path), "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["dry_run"] is True
    assert result["summary"]["page_count"] == 1
    assert result["summary"]["asset_count"] == 3
    assert result["summary"]["drift_count"] == 4
    assert all(row["planned_action"] == "write" for row in result["pages"])
    assert not wiki_dir.exists()


def test_cli_compare_fails_on_asset_drift_and_passes_after_update(tmp_path: Path, capsys) -> None:
    module = _load_module()
    source_dir = tmp_path / "groundtruth-kb" / "docs" / "wiki"
    asset_name = "assets/gtkb-home-empty-state.png"
    (source_dir / "assets").mkdir(parents=True)
    (source_dir / asset_name).write_bytes(b"\x89PNG\r\n\xff")
    args = ["--project-root", str(tmp_path), "--json"]

    assert module.main(["compare", *args]) == 1
    assert module.main(["update", *args]) == 0
    capsys.readouterr()
    assert module.main(["compare", *args]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["summary"]["page_count"] == 0
    assert result["summary"]["asset_count"] == 1
    assert result["summary"]["drift_count"] == 0


def test_readmes_route_customers_to_the_wiki_and_reviewed_source() -> None:
    root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    package_readme = (REPO_ROOT / "groundtruth-kb" / "README.md").read_text(encoding="utf-8")

    assert "github.com/Remaker-Digital/groundtruth-kb/wiki" in root_readme
    assert "groundtruth-kb/docs/wiki/" in root_readme
    assert "docs/wiki/release-health.md" in package_readme
    assert "scripts/update_wiki_pages.py compare" in package_readme
    assert "Agent Red" not in package_readme
