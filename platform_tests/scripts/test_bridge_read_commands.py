from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.bridge import read_commands
from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.project.lifecycle import _WORK_ITEM_LINE_RE


def _write_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "groundtruth.toml"
    config_path.write_text(
        "\n".join(
            [
                "[groundtruth]",
                f'db_path = "{(tmp_path / "groundtruth.db").as_posix()}"',
                f'project_root = "{tmp_path.as_posix()}"',
                'app_title = "Bridge Read Commands Test"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def _write_bridge_file(root: Path, name: str, body: str) -> Path:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    path = bridge_dir / name
    path.write_text(body, encoding="utf-8")
    return path


def _invoke(config_path: Path, *args: str):
    return CliRunner().invoke(cli_main, ["--config", str(config_path), *args])


def test_show_thread_includes_status_tokenless_versions(tmp_path: Path) -> None:
    _write_bridge_file(
        tmp_path,
        "sample-thread-001.md",
        "# Legacy proposal heading\n\nWork Item: WI-4634\n",
    )
    _write_bridge_file(tmp_path, "sample-thread-002.md", "GO\n")
    _write_bridge_file(tmp_path, "sample-thread-003.md", "NEW\n")

    payload = read_commands.show_thread(tmp_path, "sample-thread")

    assert payload is not None
    assert payload["latest_status"] == "NEW"
    assert [row["version"] for row in payload["version_chain"]] == [3, 2, 1]
    legacy = payload["version_chain"][2]
    assert legacy["status"] == "Legacy"
    assert legacy["status_is_canonical"] is False


def test_threads_for_work_item_matches_any_version_and_reports_coverage(tmp_path: Path) -> None:
    _write_bridge_file(tmp_path, "sample-thread-001.md", "# Legacy proposal heading\n\nWork Item: WI-4634\n")
    _write_bridge_file(tmp_path, "sample-thread-002.md", "GO\n")
    _write_bridge_file(tmp_path, "other-thread-001.md", "NEW\n\nWork Item: WI-9999\n")
    _write_bridge_file(tmp_path, "verdict-only-001.md", "GO\n\nNo work item metadata here.\n")

    payload = read_commands.threads_for_work_item(tmp_path, "WI-4634")

    assert payload["match_count"] == 1
    assert payload["threads"][0]["slug"] == "sample-thread"
    assert payload["threads"][0]["latest_status"] == "GO"
    assert payload["threads"][0]["citing_paths"] == ["bridge/sample-thread-001.md"]
    assert payload["coverage_caveat"]["total_threads"] == 3
    assert payload["coverage_caveat"]["threads_with_work_item_metadata"] == 2


def test_work_item_regex_reuses_project_lifecycle_constant() -> None:
    assert read_commands.WORK_ITEM_LINE_RE.pattern == _WORK_ITEM_LINE_RE.pattern


def test_bridge_show_cli_json_and_not_found_exit(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _write_bridge_file(tmp_path, "sample-thread-001.md", "NEW\n")

    result = _invoke(config_path, "bridge", "show", "sample-thread", "--json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["latest_status"] == "NEW"
    assert payload["version_count"] == 1

    missing = _invoke(config_path, "bridge", "show", "missing-thread", "--json")
    assert missing.exit_code == 1
    assert json.loads(missing.output)["error"] == "bridge_thread_not_found"


def test_bridge_threads_cli_json_empty_and_malformed(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _write_bridge_file(tmp_path, "sample-thread-001.md", "NEW\n\nWork Item: WI-4634\n")
    _write_bridge_file(tmp_path, "empty-thread-001.md", "NEW\n")

    result = _invoke(config_path, "bridge", "threads", "--wi", "WI-4634", "--json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["match_count"] == 1
    assert payload["threads"][0]["slug"] == "sample-thread"
    assert payload["coverage_caveat"]["total_threads"] == 2

    empty = _invoke(config_path, "bridge", "threads", "--wi", "WI-1111", "--json")
    assert empty.exit_code == 0, empty.output
    assert json.loads(empty.output)["match_count"] == 0

    malformed = _invoke(config_path, "bridge", "threads", "--wi", "banana")
    assert malformed.exit_code == 2


def test_bridge_help_lists_read_commands(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)

    result = _invoke(config_path, "bridge", "--help")

    assert result.exit_code == 0, result.output
    assert "show" in result.output
    assert "threads" in result.output
