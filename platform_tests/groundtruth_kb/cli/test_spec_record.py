"""Tests for the governed ``gt spec record`` CLI service."""

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
    content.write_text("Approved specification body.\n", encoding="utf-8")
    return root, config, content


def _content(root: Path, name: str, body: str) -> Path:
    path = root / name
    path.write_text(body, encoding="utf-8")
    return path


def _record_args(config: Path, content: Path, *extra: str, spec_id: str = "GOV-TEST-001") -> list[str]:
    return [
        "--config",
        str(config),
        "spec",
        "record",
        "--id",
        spec_id,
        "--title",
        "Test spec",
        "--status",
        "specified",
        "--content-file",
        str(content),
        "--change-reason",
        "record owner-approved spec",
        "--auq-id",
        "S344-AUQ-SPEC-1",
        "--auq-answer",
        "Approved",
        *extra,
    ]


def _spec_count(db_path: Path) -> int:
    if not db_path.exists():
        return 0
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) FROM current_specifications").fetchone()
    return int(row[0])


def _spec_row(db_path: Path, spec_id: str) -> sqlite3.Row | None:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT id, title, status, type, description FROM current_specifications WHERE id = ?",
            (spec_id,),
        ).fetchone()


def _packet_files(root: Path) -> list[Path]:
    packet_dir = root / ".groundtruth" / "formal-artifact-approvals"
    if not packet_dir.exists():
        return []
    return sorted(packet_dir.glob("*.json"))


def test_record_requires_owner_presented_before_packet_or_db_write(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(main, _record_args(config, content))
    assert result.exit_code != 0
    assert "--owner-presented" in result.output
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_record_requires_auq_evidence_before_packet_or_db_write(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    args = _record_args(config, content, "--owner-presented")
    args.remove("--auq-id")
    args.remove("S344-AUQ-SPEC-1")
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "Missing option '--auq-id'" in result.output
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_dry_run_constructs_valid_packet_and_writes_nothing(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(main, _record_args(config, content, "--owner-presented", "--dry-run", "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    packet = payload["approval_packet"]
    assert packet["artifact_type"] == "governance"
    assert packet["artifact_id"] == "GOV-TEST-001"
    assert packet["approved_by"] == "owner"
    assert packet["full_content"] == content.read_text(encoding="utf-8")
    assert payload["dry_run"] is True
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_content_file_outside_project_root_is_rejected(tmp_path: Path) -> None:
    root, config, _content_file = _project(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    result = CliRunner().invoke(main, _record_args(config, outside, "--owner-presented"))
    assert result.exit_code != 0
    assert "inside project root" in result.output
    assert _spec_count(root / "groundtruth.db") == 0


def test_prefixes_resolve_to_expected_artifact_types_in_dry_run(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    cases = {
        "GOV-TEST-001": ("governance", []),
        "SPEC-TEST-001": ("requirement", []),
        "REQ-TEST-001": ("requirement", []),
        "PB-TEST-001": ("protected_behavior", ["--assertions-json", '[{"id": "PB-TEST-001.A1"}]']),
        "ADR-TEST-001": (
            "architecture_decision",
            [],
        ),
        "DCL-TEST-001": ("design_constraint", []),
    }
    content_by_id = {
        "ADR-TEST-001": _content(
            root,
            "adr.md",
            "## Decision\nUse it.\n## Rationale\nBecause.\n## Consequences\nKnown.\n## Rejected Alternatives\nNone.\n",
        ),
        "DCL-TEST-001": _content(root, "dcl.md", "## Constraint\nMust hold.\n"),
    }
    for spec_id, (expected_type, extra) in cases.items():
        selected_content = content_by_id.get(spec_id, content)
        result = CliRunner().invoke(
            main,
            _record_args(config, selected_content, "--owner-presented", "--dry-run", "--json", *extra, spec_id=spec_id),
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["approval_packet"]["artifact_type"] == expected_type


def test_explicit_type_mismatch_is_rejected(tmp_path: Path) -> None:
    _root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--owner-presented", "--type", "requirement"),
    )
    assert result.exit_code != 0
    assert "does not match" in result.output


def test_existing_spec_id_is_rejected_instead_of_versioned(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    runner = CliRunner()
    first = runner.invoke(main, _record_args(config, content, "--owner-presented"))
    assert first.exit_code == 0, first.output
    second = runner.invoke(main, _record_args(config, content, "--owner-presented"))
    assert second.exit_code != 0
    assert "already exists" in second.output
    assert _spec_count(root / "groundtruth.db") == 1
    assert len(_packet_files(root)) == 1


def test_protected_behavior_requires_assertions(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--owner-presented", spec_id="PB-TEST-001"),
    )
    assert result.exit_code != 0
    assert "require a non-empty --assertions-json list" in result.output
    assert _spec_count(root / "groundtruth.db") == 0


def test_adr_requires_decision_structure(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--owner-presented", spec_id="ADR-TEST-001"),
    )
    assert result.exit_code != 0
    assert "ADR content missing" in result.output
    assert _spec_count(root / "groundtruth.db") == 0


def test_successful_dcl_record_creates_packet_and_spec_row(tmp_path: Path) -> None:
    root, config, _content_file = _project(tmp_path)
    content = _content(root, "dcl.md", "## Constraint\nThe system must keep this invariant.\n")
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--owner-presented", spec_id="DCL-TEST-001"),
    )
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "DCL-TEST-001"
    assert _spec_count(root / "groundtruth.db") == 1
    row = _spec_row(root / "groundtruth.db", "DCL-TEST-001")
    assert row is not None
    assert row["type"] == "design_constraint"
    assert row["description"] == content.read_text(encoding="utf-8")
    packets = _packet_files(root)
    assert len(packets) == 1
    packet = json.loads(packets[0].read_text(encoding="utf-8"))
    assert packet["artifact_id"] == "DCL-TEST-001"
    assert packet["artifact_type"] == "design_constraint"


def test_approved_by_overrides_default_identity(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--owner-presented", "--approved-by", "Mike"),
    )
    assert result.exit_code == 0, result.output
    packet = json.loads(_packet_files(root)[0].read_text(encoding="utf-8"))
    assert packet["approved_by"] == "Mike"


def test_spec_record_is_not_hook_matched_but_cli_still_blocks_missing_evidence(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "python -m groundtruth_kb.cli spec record --id GOV-TEST-001"},
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
    assert _spec_count(root / "groundtruth.db") == 0
