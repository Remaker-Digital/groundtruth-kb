"""Unit tests for .codex/skills/bridge/helpers/show_thread_bridge.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = PROJECT_ROOT / ".codex" / "skills" / "bridge" / "helpers" / "show_thread_bridge.py"


def _load_helper():
    import sys

    spec = importlib.util.spec_from_file_location("show_thread_bridge", HELPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["show_thread_bridge"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def helper():
    return _load_helper()


@pytest.fixture()
def fake_bridge(tmp_path):
    """Create a temporary bridge directory for numbered version files."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    return bridge_dir


def _write_version(bridge_dir: Path, slug: str, version: int, first_line: str, body: str = "") -> Path:
    name = f"{slug}-{version:03d}.md"
    path = bridge_dir / name
    content = first_line + "\n\n" + body
    path.write_text(content, encoding="utf-8")
    return path


def test_t1_slug_with_no_files_returns_empty(helper, fake_bridge) -> None:
    result = helper.show("gtkb-nonexistent", bridge_dir=fake_bridge)
    assert result["found"] is False
    assert result["versions"] == []
    assert result["slug"] == "gtkb-nonexistent"


def test_t2_three_versions_sorted_ascending(helper, fake_bridge) -> None:
    _write_version(fake_bridge, "gtkb-foo", 1, "NEW", "body1")
    _write_version(fake_bridge, "gtkb-foo", 2, "GO", "body2")
    _write_version(fake_bridge, "gtkb-foo", 3, "NEW", "body3")

    result = helper.show("gtkb-foo", bridge_dir=fake_bridge)
    assert result["found"] is True
    assert len(result["versions"]) == 3
    versions = [v["version"] for v in result["versions"]]
    assert versions == [1, 2, 3]
    assert result["versions"][0]["verdict_line"] == "NEW"
    assert result["versions"][1]["verdict_line"] == "GO"
    assert "Document: gtkb-foo" in result["document_entry"]


def test_t3_compound_suffix_slug_handled(helper, fake_bridge) -> None:
    """Slugs ending in numeric suffix (e.g., gtkb-foo-001) use -NNN as version."""
    _write_version(fake_bridge, "gtkb-foo-001", 1, "NEW")
    _write_version(fake_bridge, "gtkb-foo-001", 2, "GO")

    result = helper.show("gtkb-foo-001", bridge_dir=fake_bridge)
    assert result["found"] is True
    assert len(result["versions"]) == 2
    assert [v["version"] for v in result["versions"]] == [1, 2]


def test_t5_content_preview_bounded(helper, fake_bridge) -> None:
    long_body = "\n".join([f"line {i}" for i in range(500)])
    _write_version(fake_bridge, "gtkb-foo", 1, "NEW", long_body)

    result = helper.show("gtkb-foo", bridge_dir=fake_bridge, preview_lines=50)
    preview = result["versions"][0]["content_preview"]
    preview_line_count = len(preview.splitlines())
    assert preview_line_count <= 50
    assert result["preview_lines_cap"] == 50


def test_default_preview_cap(helper, fake_bridge) -> None:
    _write_version(fake_bridge, "gtkb-foo", 1, "NEW")
    result = helper.show("gtkb-foo", bridge_dir=fake_bridge)
    assert result["preview_lines_cap"] == 200


def test_index_status_chain_returned(helper, fake_bridge) -> None:
    _write_version(fake_bridge, "gtkb-foo", 1, "NEW")
    _write_version(fake_bridge, "gtkb-foo", 2, "GO")

    result = helper.show("gtkb-foo", bridge_dir=fake_bridge)
    chain = result["index_status_chain"]
    assert len(chain) == 2
    assert chain[0]["status"] == "GO"
    assert chain[1]["status"] == "NEW"


def test_no_action_status_chain_returned(helper, fake_bridge) -> None:
    _write_version(fake_bridge, "gtkb-foo", 1, "NEW")
    _write_version(fake_bridge, "gtkb-foo", 2, "GO")
    _write_version(fake_bridge, "gtkb-foo", 3, "NO-ACTION")

    result = helper.show("gtkb-foo", bridge_dir=fake_bridge)

    chain = result["index_status_chain"]
    assert [item["status"] for item in chain] == ["NO-ACTION", "GO", "NEW"]
