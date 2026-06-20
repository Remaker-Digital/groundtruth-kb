"""Tests for active legacy-root reference detection."""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.project.doctor import _check_active_legacy_root_references


def test_active_legacy_root_references_fails_settings_local_live_path(tmp_path: Path) -> None:
    settings_dir = tmp_path / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    (settings_dir / "settings.local.json").write_text(
        json.dumps({"allow": ["E:\\Claude-Playground\\CLAUDE-PROJECTS\\groundtruth-kb"]}),
        encoding="utf-8",
    )

    result = _check_active_legacy_root_references(tmp_path)

    assert result.status == "fail"
    assert ".claude/settings.local.json:1" in result.message


def test_active_legacy_root_references_allows_archive_only_rule_text(tmp_path: Path) -> None:
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "project-root-boundary.md").write_text(
        "`E:\\Claude-Playground` is an archive only. It is not a live GT-KB dependency.\n",
        encoding="utf-8",
    )

    result = _check_active_legacy_root_references(tmp_path)

    assert result.status == "pass"


def test_active_legacy_root_references_allows_forbidden_alias_map_row(tmp_path: Path) -> None:
    config_dir = tmp_path / "config" / "agent-control"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "system-interface-map.toml").write_text(
        "\n".join(
            [
                'id = "project-root"',
                'forbidden_aliases = ["E:\\\\Claude-Playground"]',
                'harness_caveats = "E:\\\\Claude-Playground is archive-only and must not be treated as '
                'live authority."',
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _check_active_legacy_root_references(tmp_path)

    assert result.status == "pass"


def test_active_legacy_root_references_allows_detector_constants(tmp_path: Path) -> None:
    source_dir = tmp_path / "groundtruth-kb" / "src" / "groundtruth_kb" / "project"
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "doctor.py").write_text(
        "_LEGACY_ROOT_MARKERS = (\n"
        '    "E:\\\\Claude-Playground",\n'
        '    "E:/Claude-Playground",\n'
        ")\n"
        'message="No active control-surface references to E:\\\\Claude-Playground"\n',
        encoding="utf-8",
    )

    result = _check_active_legacy_root_references(tmp_path)

    assert result.status == "pass"


def test_active_legacy_root_references_allows_hygiene_sweep_pattern_catalog(tmp_path: Path) -> None:
    config_dir = tmp_path / "config" / "governance"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "hygiene-sweep-patterns.toml").write_text(
        "\n".join(
            [
                "[[patterns]]",
                'id = "claude-playground"',
                'description = "Detect legacy root archive path references."',
                "content_patterns = [",
                '  "E:\\\\Claude-Playground",',
                '  "E:/Claude-Playground",',
                '  "//e/Claude-Playground",',
                '  "//E/Claude-Playground",',
                "]",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _check_active_legacy_root_references(tmp_path)

    assert result.status == "pass"


def test_active_legacy_root_references_fails_live_script_use(tmp_path: Path) -> None:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "uses_archive_root.py").write_text(
        'LIVE_ROOT = "E:\\\\Claude-Playground"\n',
        encoding="utf-8",
    )

    result = _check_active_legacy_root_references(tmp_path)

    assert result.status == "fail"
    assert "scripts/uses_archive_root.py:1" in result.message
