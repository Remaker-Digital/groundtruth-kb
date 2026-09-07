"""Tests for the governed ``gt spec record`` CLI service."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.cli_spec_record import SpecRecordError, SpecRecordRequest, record_spec  # noqa: E402
from groundtruth_kb.config import GTConfig  # noqa: E402

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
        "--expected-version",
        "0",
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
            "SELECT * FROM current_specifications WHERE id = ?",
            (spec_id,),
        ).fetchone()


def _semantic_postimage(row: sqlite3.Row) -> dict[str, object]:
    structured = {"tags", "assertions", "constraints", "affected_by", "source_paths"}
    names = (
        "title",
        "status",
        "priority",
        "scope",
        "section",
        "handle",
        "tags",
        "assertions",
        "constraints",
        "affected_by",
        "testability",
        "source_paths",
        "application_scope",
    )
    return {
        name: json.loads(row[name]) if name in structured and row[name] is not None else row[name] for name in names
    }


def _packet_files(root: Path) -> list[Path]:
    packet_dir = root / ".groundtruth" / "formal-artifact-approvals"
    if not packet_dir.exists():
        return []
    return sorted(packet_dir.glob("*.json"))


def _service_config(root: Path) -> GTConfig:
    return GTConfig(db_path=root / "groundtruth.db", project_root=root)


def _service_request(content: Path, **overrides: object) -> SpecRecordRequest:
    values = {
        "spec_id": "GOV-TEST-001",
        "title": "Test spec",
        "status": "specified",
        "content_file": content,
        "change_reason": "record owner-approved spec",
        "expected_version": 0,
        "spec_type": None,
        "priority": None,
        "scope": None,
        "section": None,
        "handle": None,
        "tags_json": None,
        "assertions_json": None,
        "constraints_json": None,
        "affected_by_json": None,
        "testability": None,
        "source_paths_json": None,
        "application_scope": None,
        "dry_run": True,
    }
    values.update(overrides)
    return SpecRecordRequest(**values)


def test_record_requires_expected_version_before_any_write(tmp_path: Path) -> None:
    """Omitting the CAS assertion blocks the write instead of defaulting."""

    root, config, content = _project(tmp_path)
    args = _record_args(config, content)
    args.remove("--expected-version")
    args.remove("0")
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "--expected-version" in result.output
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_record_rejects_nonzero_expected_version(tmp_path: Path) -> None:
    """A nonzero expected version addresses an existing spec and belongs to update."""

    root, config, content = _project(tmp_path)
    args = _record_args(config, content)
    args[args.index("--expected-version") + 1] = "1"
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "--expected-version must be 0 for record" in result.output
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_dry_run_reports_intent_and_writes_nothing(tmp_path: Path) -> None:
    """A dry run reports the intended operation and creates no row and no artifact."""

    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(main, _record_args(config, content, "--dry-run", "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)

    assert payload["created"] is False
    assert payload["dry_run"] is True
    assert payload["replayed"] is False
    assert payload["expected_version"] == 0
    assert payload["id"] == "GOV-TEST-001"
    assert payload["row"] is None
    assert payload["db_operation"] == {
        "method": "insert_spec",
        "id": "GOV-TEST-001",
        "type": "governance",
        "status": "specified",
    }
    # Persistence is intrinsic: no approval surface is emitted at all.
    assert "approval_packet" not in payload
    assert "approval_packet_path" not in payload
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_structured_record_postimage_matches_persisted_row(tmp_path: Path) -> None:
    """The dry-run intent and the persisted row agree on the complete postimage."""

    root, config, content = _project(tmp_path)
    structured_args = (
        "--priority",
        "P1",
        "--scope",
        "platform",
        "--section",
        "Governance",
        "--handle",
        "record-handle",
        "--tags-json",
        '["approval", "café"]',
        "--assertions-json",
        '[{"type": "file_exists", "file": "README.md"}]',
        "--constraints-json",
        '{"mode": "strict"}',
        "--affected-by-json",
        '["ADR-TEST-001"]',
        "--testability",
        "structural",
        "--source-paths-json",
        '["groundtruth-kb/src/**/*.py"]',
        "--application-scope",
        "gtkb_platform",
    )
    expected = {
        "title": "Test spec",
        "status": "specified",
        "priority": "P1",
        "scope": "platform",
        "section": "Governance",
        "handle": "record-handle",
        "tags": ["approval", "café"],
        "assertions": [{"type": "file_exists", "file": "README.md"}],
        "constraints": {"mode": "strict"},
        "affected_by": ["ADR-TEST-001"],
        "testability": "structural",
        "source_paths": ["groundtruth-kb/src/**/*.py"],
        "application_scope": "gtkb_platform",
    }

    dry_result = CliRunner().invoke(main, _record_args(config, content, "--dry-run", "--json", *structured_args))
    assert dry_result.exit_code == 0, dry_result.output
    assert json.loads(dry_result.output)["row"] is None
    assert _spec_count(root / "groundtruth.db") == 0

    write_result = CliRunner().invoke(main, _record_args(config, content, "--json", *structured_args))
    assert write_result.exit_code == 0, write_result.output
    write_payload = json.loads(write_result.output)
    assert write_payload["created"] is True
    assert write_payload["replayed"] is False

    row = _spec_row(root / "groundtruth.db", "GOV-TEST-001")
    assert row is not None
    assert _semantic_postimage(row) == expected
    assert _packet_files(root) == []


def test_gap_state_spec_capture_dry_run_carries_context_and_writes_nothing(tmp_path: Path) -> None:
    root, _config, content = _project(tmp_path)
    request = _service_request(
        content,
        gap_state_capture=True,
        gap_state_bridge_id="gtkb-gap-state-spec-capture",
        gap_state_reason="requirement sufficiency gap-state proposal needs formal spec capture",
    )

    result = record_spec(_service_config(root), request)

    assert result["gap_state_capture"] is True
    assert result["dry_run"] is True
    assert result["db_operation"]["method"] == "insert_spec"
    assert result["db_operation"]["id"] == "GOV-TEST-001"
    assert "approval_packet" not in result
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_gap_state_spec_capture_requires_bridge_context_before_writes(tmp_path: Path) -> None:
    root, _config, content = _project(tmp_path)
    request = _service_request(
        content,
        gap_state_capture=True,
        gap_state_bridge_id="",
        gap_state_reason="missing bridge id should fail closed",
    )

    with pytest.raises(SpecRecordError, match="--gap-state-bridge-id"):
        record_spec(_service_config(root), request)

    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


def test_content_file_outside_project_root_is_rejected(tmp_path: Path) -> None:
    root, config, _content_file = _project(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    result = CliRunner().invoke(main, _record_args(config, outside))
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
            _record_args(config, selected_content, "--dry-run", "--json", *extra, spec_id=spec_id),
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["db_operation"]["type"] == expected_type
        assert payload["db_operation"]["id"] == spec_id


def test_record_creates_no_approvals_artifact_for_any_id_casing(tmp_path: Path) -> None:
    """Recording a spec emits the row only; no approvals artifact is created."""

    root, _config, content = _project(tmp_path)
    config = _service_config(root)
    spec_id = "GOV-MIXED-CASE-001"

    dry_run = record_spec(config, _service_request(content, spec_id=spec_id, dry_run=True))
    assert dry_run["id"] == spec_id
    assert "approval_packet_path" not in dry_run
    assert _packet_files(root) == []

    written = record_spec(config, _service_request(content, spec_id=spec_id, dry_run=False))
    assert written["created"] is True
    assert written["row"]["id"] == spec_id
    assert "approval_packet_path" not in written
    assert _packet_files(root) == []
    assert not (root / ".groundtruth" / "formal-artifact-approvals").exists()


def test_explicit_type_mismatch_is_rejected(tmp_path: Path) -> None:
    _root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, "--type", "requirement"),
    )
    assert result.exit_code != 0
    assert "does not match" in result.output


def test_identical_record_replays_and_differing_record_collides(tmp_path: Path) -> None:
    """Exact replay is read-only; a same-id record with different content collides."""

    root, config, content = _project(tmp_path)
    runner = CliRunner()

    first = runner.invoke(main, _record_args(config, content, "--json"))
    assert first.exit_code == 0, first.output
    assert json.loads(first.output)["created"] is True

    replay = runner.invoke(main, _record_args(config, content, "--json"))
    assert replay.exit_code == 0, replay.output
    replay_payload = json.loads(replay.output)
    assert replay_payload["replayed"] is True
    assert replay_payload["created"] is False
    assert _spec_count(root / "groundtruth.db") == 1

    other = _content(root, "other.md", "Different content entirely.\n")
    collision = runner.invoke(main, _record_args(config, other))
    assert collision.exit_code != 0
    assert "record_collision" in collision.output
    assert _spec_count(root / "groundtruth.db") == 1
    assert _packet_files(root) == []


def test_protected_behavior_requires_assertions(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, spec_id="PB-TEST-001"),
    )
    assert result.exit_code != 0
    assert "require a non-empty --assertions-json list" in result.output
    assert _spec_count(root / "groundtruth.db") == 0


def test_adr_requires_decision_structure(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _record_args(config, content, spec_id="ADR-TEST-001"),
    )
    assert result.exit_code != 0
    assert "ADR content missing" in result.output
    assert _spec_count(root / "groundtruth.db") == 0


def test_successful_dcl_record_creates_spec_row_and_no_packet(tmp_path: Path) -> None:
    root, config, _content_file = _project(tmp_path)
    content = _content(root, "dcl.md", "## Constraint\nThe system must keep this invariant.\n")
    result = CliRunner().invoke(main, _record_args(config, content, spec_id="DCL-TEST-001"))
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "DCL-TEST-001"
    assert _spec_count(root / "groundtruth.db") == 1
    row = _spec_row(root / "groundtruth.db", "DCL-TEST-001")
    assert row is not None
    assert row["type"] == "design_constraint"
    assert row["description"] == content.read_text(encoding="utf-8")
    assert _packet_files(root) == []


def test_record_output_carries_no_approval_fields(tmp_path: Path) -> None:
    """The recorded result exposes no approval identity, packet, or evidence field."""

    root, config, content = _project(tmp_path)
    result = CliRunner().invoke(main, _record_args(config, content, "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    for forbidden in ("approval_packet", "approval_packet_path", "approved_by", "auq_id", "auq_answer"):
        assert forbidden not in payload
    assert _packet_files(root) == []


def test_spec_record_is_not_hook_matched_but_cli_still_blocks_missing_cas(tmp_path: Path) -> None:
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

    args = _record_args(config, content)
    args.remove("--expected-version")
    args.remove("0")
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert _spec_count(root / "groundtruth.db") == 0
