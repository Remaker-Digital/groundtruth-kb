"""Tests for the governed ``gt deliberations record`` CLI service."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402

HOOK = REPO_ROOT / ".claude" / "hooks" / "formal-artifact-approval-gate.py"


def _project(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    content = root / "content.md"
    content.write_text("Approved deliberation body.\n", encoding="utf-8")
    return root, config, content


def _record_args(config: Path, content: Path, *extra: str) -> list[str]:
    return [
        "--config",
        str(config),
        "deliberations",
        "record",
        "--source-type",
        "owner_conversation",
        "--source-ref",
        "conversation:S344:test",
        "--title",
        "Owner decision",
        "--summary",
        "Owner approved recording a deliberation.",
        "--content-file",
        str(content),
        "--change-reason",
        "record owner-approved deliberation",
        "--auq-id",
        "S344-AUQ-1",
        "--auq-answer",
        "Approved",
        *extra,
    ]


def _deliberation_count(db_path: Path) -> int:
    if not db_path.exists():
        return 0
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) FROM current_deliberations").fetchone()
    return int(row[0])


def _packet_files(root: Path) -> list[Path]:
    packet_dir = root / ".groundtruth" / "formal-artifact-approvals"
    if not packet_dir.exists():
        return []
    return sorted(packet_dir.glob("*.json"))


def test_record_requires_owner_presented_before_db_write(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(main, _record_args(config, content))
    assert result.exit_code != 0
    assert "--owner-presented" in result.output
    assert _deliberation_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_record_requires_auq_evidence_before_db_write(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    args = _record_args(config, content, "--owner-presented")
    args.remove("--auq-id")
    args.remove("S344-AUQ-1")
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "Missing option '--auq-id'" in result.output
    assert _deliberation_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_dry_run_constructs_valid_packet_and_writes_nothing(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--owner-presented", "--dry-run", "--json"),
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    packet = payload["approval_packet"]
    assert packet["approved_by"] == "owner"
    assert packet["full_content"] == content.read_text(encoding="utf-8")
    assert payload["dry_run"] is True
    assert _deliberation_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_content_file_outside_project_root_is_rejected(tmp_path: Path) -> None:
    root, config, _content = _project(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    result = CliRunner().invoke(
        main,
        _record_args(config, outside, "--owner-presented"),
    )
    assert result.exit_code != 0
    assert "inside project root" in result.output
    assert _deliberation_count(root / "groundtruth.db") == 0


def test_successful_record_creates_packet_and_row(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--owner-presented"),
    )
    assert result.exit_code == 0, result.output
    delib_id = result.output.strip()
    assert delib_id.startswith("DELIB-")
    assert _deliberation_count(root / "groundtruth.db") == 1
    packets = _packet_files(root)
    assert len(packets) == 1
    packet = json.loads(packets[0].read_text(encoding="utf-8"))
    assert packet["artifact_id"] == delib_id
    assert packet["approved_by"] == "owner"


def test_duplicate_source_ref_and_content_returns_existing_id_without_second_row_or_packet(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    runner = CliRunner()
    first = runner.invoke(main, _record_args(config, content, "--owner-presented"))
    assert first.exit_code == 0, first.output
    second = runner.invoke(main, _record_args(config, content, "--owner-presented"))
    assert second.exit_code == 0, second.output
    assert second.output.strip() == first.output.strip()
    assert _deliberation_count(root / "groundtruth.db") == 1
    assert len(_packet_files(root)) == 1


def test_approved_by_overrides_default_identity(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--owner-presented", "--approved-by", "Mike"),
    )
    assert result.exit_code == 0, result.output
    packet = json.loads(_packet_files(root)[0].read_text(encoding="utf-8"))
    assert packet["approved_by"] == "Mike"


def test_record_is_not_hook_matched_but_cli_still_blocks_missing_evidence(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "python -m groundtruth_kb deliberations record --source-type report"},
    }
    hook = subprocess.run(
        [sys.executable, str(HOOK)],
        cwd=REPO_ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(hook.stdout) == {}

    result = CliRunner().invoke(main, _record_args(config, content))
    assert result.exit_code != 0
    assert _deliberation_count(root / "groundtruth.db") == 0
