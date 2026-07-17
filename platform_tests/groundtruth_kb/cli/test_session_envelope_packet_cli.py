from __future__ import annotations

import json
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")
    startup_dir = root / "config" / "agent-control"
    startup_dir.mkdir(parents=True)
    (startup_dir / "SESSION-STARTUP-INDEX.md").write_text("startup index\n", encoding="utf-8")
    (startup_dir / "PRIME-BUILDER-STARTUP-OVERLAY.md").write_text("prime overlay\n", encoding="utf-8")
    (startup_dir / "LOYAL-OPPOSITION-STARTUP-OVERLAY.md").write_text("lo overlay\n", encoding="utf-8")
    return root, config


def test_session_envelope_packet_cli_emits_json_under_session_cap(tmp_path: Path) -> None:
    root, config = _project(tmp_path)

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "session",
            "envelope",
            "packet",
            "--kind",
            "session-envelope",
            "--cache-dir",
            str(root / ".cache"),
        ],
    )

    assert result.exit_code == 0, result.output
    packet = json.loads(result.output)
    assert packet["packet_kind"] == "session-envelope"
    assert packet["status"] == "ready"
    assert packet["budget"]["estimated_tokens"] <= 900
    assert packet["cache"]["cache_path"].endswith(".json")


def test_activity_packet_cli_emits_json_under_activity_cap(tmp_path: Path) -> None:
    root, config = _project(tmp_path)

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "session",
            "envelope",
            "packet",
            "--kind",
            "activity-packet",
            "--activity",
            "build",
            "--role",
            "prime-builder",
            "--cache-dir",
            str(root / ".cache"),
        ],
    )

    assert result.exit_code == 0, result.output
    packet = json.loads(result.output)
    assert packet["packet_kind"] == "activity-packet"
    assert packet["activity"] == "build"
    assert packet["status"] == "ready"
    assert packet["budget"]["estimated_tokens"] <= 500
    assert {descriptor["cache_policy"] for descriptor in packet["live_query_descriptors"]} == {"live_query_only"}


def test_activity_packet_cli_requires_activity(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "session",
            "envelope",
            "packet",
            "--kind",
            "activity-packet",
        ],
    )

    assert result.exit_code != 0
    assert "activity is required" in result.output
