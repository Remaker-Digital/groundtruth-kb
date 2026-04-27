"""Tests for Wave 2 Slice 5 _bridge_split.py.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice5-005.md`` (REVISED-2)
and ``-006`` (Codex GO with 5 implementation conditions).

All tests use ``bridge_root=`` parameter override (per Codex Slice 5
``-002`` non-blocking note 4) to point at fixture trees. No
monkeypatching of module constants; no live-root walks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _bridge_split  # noqa: E402


def _build_manifest(legacy_root: Path) -> dict[str, Any]:
    """Minimal Wave 2 manifest dict (already loaded shape)."""
    return {
        "target_root": str((legacy_root / "applications" / "Agent_Red").as_posix()),
        "legacy_root": str(legacy_root.as_posix()),
        "applications_namespace": str((legacy_root / "applications").as_posix()),
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "clone_with_history_filter",
        "excluded_paths": [],
    }


def _build_fixture_bridge(bridge_root: Path, threads: list[dict[str, str]]) -> None:
    """Create INDEX.md + per-thread file with the given metadata.

    Each thread dict: {name, status, version, metadata_block}.
    """
    bridge_root.mkdir(parents=True, exist_ok=True)
    index_lines = ["# Bridge Index\n", "\n"]
    for thread in threads:
        index_lines.append(f"Document: {thread['name']}\n")
        index_lines.append(f"{thread['status']}: bridge/{thread['name']}-{thread['version']}.md\n")
        index_lines.append("\n")
        thread_file = bridge_root / f"{thread['name']}-{thread['version']}.md"
        thread_file.write_text(
            f"{thread['status']}\n\n# Title\n\n**Status:** ...\n\n"
            f"{thread['metadata_block']}\n\n---\n\n"
            f"## Body\n\nbody.\n",
            encoding="utf-8",
        )
    (bridge_root / "INDEX.md").write_text("".join(index_lines), encoding="utf-8")


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    manifest = _build_manifest(tmp_path)
    result = _bridge_split.run(
        manifest,
        tmp_path / "out",
        dry_run=True,
        bridge_root=tmp_path / "bridge",
    )
    assert result["status"] == "skipped"
    assert result["output_files"] == []


def test_run_classifies_by_target_project_agent_red(tmp_path: Path) -> None:
    """target_project: agent-red → adopter."""
    bridge_root = tmp_path / "bridge"
    _build_fixture_bridge(
        bridge_root,
        [
            {
                "name": "test-thread",
                "status": "NEW",
                "version": "001",
                "metadata_block": (
                    "bridge_kind: implementation_slice\nwork_item_ids: [GTKB-FOO]\ntarget_project: agent-red\n"
                ),
            }
        ],
    )
    manifest = _build_manifest(tmp_path)
    result = _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    assert result["status"] == "ok"
    bs = json.loads((tmp_path / "out" / "bridge_split" / "bridge_split.json").read_text(encoding="utf-8"))
    assert len(bs["adopter_threads"]) == 1
    assert bs["adopter_threads"][0]["thread_name"] == "test-thread"
    assert bs["adopter_threads"][0]["classification_signal"] == "target_project_agent_red"
    assert bs["framework_threads"] == []


def test_run_classifies_by_target_project_groundtruth_kb(tmp_path: Path) -> None:
    """target_project: groundtruth-kb → framework."""
    bridge_root = tmp_path / "bridge"
    _build_fixture_bridge(
        bridge_root,
        [
            {
                "name": "test-thread",
                "status": "NEW",
                "version": "001",
                "metadata_block": ("bridge_kind: implementation_slice\ntarget_project: groundtruth-kb\n"),
            }
        ],
    )
    manifest = _build_manifest(tmp_path)
    _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    bs = json.loads((tmp_path / "out" / "bridge_split" / "bridge_split.json").read_text(encoding="utf-8"))
    assert len(bs["framework_threads"]) == 1
    assert bs["framework_threads"][0]["classification_signal"] == "target_project_groundtruth_kb"


def test_run_falls_back_to_work_item_ids_prefix(tmp_path: Path) -> None:
    """No target_project → fall back to work_item_ids prefix."""
    bridge_root = tmp_path / "bridge"
    _build_fixture_bridge(
        bridge_root,
        [
            {
                "name": "ar-thread",
                "status": "NEW",
                "version": "001",
                "metadata_block": ("bridge_kind: implementation_slice\nwork_item_ids: [AR-FOO-001]\n"),
            }
        ],
    )
    manifest = _build_manifest(tmp_path)
    _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    bs = json.loads((tmp_path / "out" / "bridge_split" / "bridge_split.json").read_text(encoding="utf-8"))
    assert len(bs["adopter_threads"]) == 1
    assert bs["adopter_threads"][0]["classification_signal"].startswith("work_item_ids_prefix:")


def test_run_falls_back_to_thread_name_pattern(tmp_path: Path) -> None:
    """gtkb-isolation-* without metadata signals → adopter via thread-name fallback."""
    bridge_root = tmp_path / "bridge"
    # No metadata block content in this thread file
    bridge_root.mkdir(parents=True)
    (bridge_root / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: gtkb-isolation-test\nNEW: bridge/gtkb-isolation-test-001.md\n",
        encoding="utf-8",
    )
    (bridge_root / "gtkb-isolation-test-001.md").write_text(
        "NEW\n\n# Title\n\n**Status:** ...\n\n## Body\n\nNo metadata.\n",
        encoding="utf-8",
    )
    manifest = _build_manifest(tmp_path)
    _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    bs = json.loads((tmp_path / "out" / "bridge_split" / "bridge_split.json").read_text(encoding="utf-8"))
    assert len(bs["adopter_threads"]) == 1
    assert bs["adopter_threads"][0]["classification_signal"] == "thread_name_gtkb_isolation"


def test_run_unclassified_thread_no_signal(tmp_path: Path) -> None:
    """Thread with no classification signal → unclassified with 'no_classification_signal'."""
    bridge_root = tmp_path / "bridge"
    bridge_root.mkdir(parents=True)
    (bridge_root / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: random-name-thread\nNEW: bridge/random-name-thread-001.md\n",
        encoding="utf-8",
    )
    (bridge_root / "random-name-thread-001.md").write_text(
        "NEW\n\n# Title\n\n**Status:** ...\n\n## Body\n",
        encoding="utf-8",
    )
    manifest = _build_manifest(tmp_path)
    result = _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    assert result["status"] == "ok"
    bs = json.loads((tmp_path / "out" / "bridge_split" / "bridge_split.json").read_text(encoding="utf-8"))
    assert len(bs["unclassified_threads"]) == 1
    assert bs["unclassified_threads"][0]["classification_signal"] == "no_classification_signal"
    assert any("unclassified_threads_present" in w for w in result["warnings"])


def test_metadata_parser_handles_key_value_format_not_yaml(tmp_path: Path) -> None:
    """Per Codex -002 non-blocking note 2: parse key-value before first ---,
    NOT YAML frontmatter delimiters at the very top."""
    file_text = (
        "NEW\n\n"
        "# Title\n\n"
        "**Status:** Running\n\n"
        "bridge_kind: implementation_slice\n"
        "work_item_ids: [GTKB-FOO]\n"
        "target_project: agent-red\n"
        "implementation_scope: foo\n\n"
        "---\n\n"
        "## Body\n"
    )
    metadata = _bridge_split._parse_metadata_block(file_text)
    assert metadata["bridge_kind"] == "implementation_slice"
    assert metadata["work_item_ids"] == "[GTKB-FOO]"
    assert metadata["target_project"] == "agent-red"


def test_run_returns_error_when_bridge_index_missing(tmp_path: Path) -> None:
    manifest = _build_manifest(tmp_path)
    result = _bridge_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        bridge_root=tmp_path / "nonexistent",
    )
    assert result["status"] == "error"
    assert any("bridge_index_missing" in w for w in result["warnings"])


def test_run_returns_error_when_index_has_no_threads(tmp_path: Path) -> None:
    bridge_root = tmp_path / "bridge"
    bridge_root.mkdir(parents=True)
    (bridge_root / "INDEX.md").write_text("# Bridge Index\n\n<!-- comment -->\n", encoding="utf-8")
    manifest = _build_manifest(tmp_path)
    result = _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    assert result["status"] == "error"
    assert any("no_threads_parsed" in w for w in result["warnings"])


def test_run_warns_when_referenced_bridge_file_missing(tmp_path: Path) -> None:
    """INDEX entry referencing non-existent file → warning, not error."""
    bridge_root = tmp_path / "bridge"
    bridge_root.mkdir(parents=True)
    (bridge_root / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: gtkb-isolation-missing\nNEW: bridge/gtkb-isolation-missing-001.md\n",
        encoding="utf-8",
    )
    manifest = _build_manifest(tmp_path)
    result = _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    assert result["status"] == "ok"
    assert any("bridge_file_missing" in w for w in result["warnings"])


def test_run_writes_result_json_on_ok_path(tmp_path: Path) -> None:
    """Per Slice 4 -006 F2: result.json must exist on ok path."""
    bridge_root = tmp_path / "bridge"
    _build_fixture_bridge(
        bridge_root,
        [
            {
                "name": "test-thread",
                "status": "NEW",
                "version": "001",
                "metadata_block": "target_project: agent-red\n",
            }
        ],
    )
    manifest = _build_manifest(tmp_path)
    result = _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    result_path = tmp_path / "out" / "bridge_split" / "result.json"
    assert result_path.exists()
    on_disk = json.loads(result_path.read_text(encoding="utf-8"))
    assert on_disk == result
    assert str(result_path) in on_disk["output_files"]


def test_run_writes_result_json_on_error_path(tmp_path: Path) -> None:
    manifest = _build_manifest(tmp_path)
    bridge_root = tmp_path / "bridge"
    bridge_root.mkdir()
    (bridge_root / "INDEX.md").write_text("# empty\n", encoding="utf-8")
    result = _bridge_split.run(manifest, tmp_path / "out", dry_run=False, bridge_root=bridge_root)
    assert result["status"] == "error"
    result_path = tmp_path / "out" / "bridge_split" / "result.json"
    assert result_path.exists()
    on_disk = json.loads(result_path.read_text(encoding="utf-8"))
    assert on_disk == result
