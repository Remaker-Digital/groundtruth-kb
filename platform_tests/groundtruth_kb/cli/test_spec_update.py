"""Tests for the governed ``gt spec update`` CLI service.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a temporary GT-KB project with config + a content file."""
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    content = root / "content.md"
    content.write_text("Updated specification body.\n", encoding="utf-8")
    return root, config, content


def _content(root: Path, name: str, body: str) -> Path:
    path = root / name
    path.write_text(body, encoding="utf-8")
    return path


def _record_args(config: Path, content: Path, *extra: str, spec_id: str = "GOV-UPD-001") -> list[str]:
    """Args to seed an existing spec via the verified ``gt spec record`` path."""
    return [
        "--config",
        str(config),
        "spec",
        "record",
        "--id",
        spec_id,
        "--title",
        "Seed spec",
        "--status",
        "specified",
        "--content-file",
        str(content),
        "--change-reason",
        "record owner-approved spec",
        "--auq-id",
        "S350-AUQ-SEED-1",
        "--auq-answer",
        "Approved",
        "--owner-presented",
        *extra,
    ]


def _update_args(config: Path, content: Path, *extra: str, spec_id: str = "GOV-UPD-001") -> list[str]:
    return [
        "--config",
        str(config),
        "spec",
        "update",
        "--id",
        spec_id,
        "--content-file",
        str(content),
        "--change-reason",
        "update owner-approved spec",
        "--auq-id",
        "S350-AUQ-UPD-1",
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


def _spec_versions(db_path: Path, spec_id: str) -> list[int]:
    """Return all stored versions for a spec id, ascending."""
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT version FROM specifications WHERE id = ? ORDER BY version",
            (spec_id,),
        ).fetchall()
    return [int(r[0]) for r in rows]


def _current_row(db_path: Path, spec_id: str) -> sqlite3.Row | None:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT id, version, title, status, type, description, priority FROM current_specifications WHERE id = ?",
            (spec_id,),
        ).fetchone()


def _packet_files(root: Path) -> list[Path]:
    packet_dir = root / ".groundtruth" / "formal-artifact-approvals"
    if not packet_dir.exists():
        return []
    return sorted(packet_dir.glob("*.json"))


def _seed_spec(config: Path, content: Path, *extra: str, spec_id: str = "GOV-UPD-001") -> None:
    """Create the spec the update tests operate on; assert it landed."""
    result = CliRunner().invoke(main, _record_args(config, content, *extra, spec_id=spec_id))
    assert result.exit_code == 0, result.output


# --- T-SU-1: missing --owner-presented -------------------------------------


def test_update_requires_owner_presented_before_packet_or_db_write(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    before = _packet_files(root)
    result = CliRunner().invoke(main, _update_args(config, content))
    assert result.exit_code != 0
    assert "--owner-presented" in result.output
    # No new version, no new packet beyond the seed create-time packet.
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]
    assert _packet_files(root) == before


# --- T-SU-2: missing AUQ evidence ------------------------------------------


def test_update_requires_auq_evidence_before_packet_or_db_write(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    before = _packet_files(root)
    args = _update_args(config, content, "--owner-presented")
    args.remove("--auq-id")
    args.remove("S350-AUQ-UPD-1")
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "Missing option '--auq-id'" in result.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]
    assert _packet_files(root) == before


# --- T-SU-3: missing --change-reason ---------------------------------------


def test_update_requires_change_reason(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    args = _update_args(config, content, "--owner-presented")
    args.remove("--change-reason")
    args.remove("update owner-approved spec")
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "Missing option '--change-reason'" in result.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]


# --- T-SU-4: dry-run constructs a valid packet and writes nothing ----------


def test_dry_run_constructs_valid_update_packet_and_writes_nothing(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    before = _packet_files(root)
    new_body = _content(root, "new.md", "Dry-run updated body.\n")
    result = CliRunner().invoke(main, _update_args(config, new_body, "--owner-presented", "--dry-run", "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    packet = payload["approval_packet"]
    assert packet["action"] == "update"
    assert packet["artifact_id"] == "GOV-UPD-001"
    assert packet["artifact_type"] == "governance"
    assert packet["full_content"] == new_body.read_text(encoding="utf-8")
    assert payload["dry_run"] is True
    assert payload["to_version"] == 2
    # No DB write, no new packet file.
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]
    assert _packet_files(root) == before


# --- T-SU-5: content file outside project root is rejected -----------------


def test_content_file_outside_project_root_is_rejected(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    result = CliRunner().invoke(main, _update_args(config, outside, "--owner-presented"))
    assert result.exit_code != 0
    assert "inside project root" in result.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]


# --- T-SU-6: non-existent spec id is rejected ------------------------------


def test_update_of_nonexistent_spec_is_rejected(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    # No seed: spec does not exist.
    result = CliRunner().invoke(main, _update_args(config, content, "--owner-presented", spec_id="GOV-MISSING-001"))
    assert result.exit_code != 0
    assert "does not exist" in result.output
    assert "gt spec record" in result.output
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


# --- T-SU-7: successful update creates one new packet + new version --------


def test_successful_update_creates_versioned_row_and_suffixed_packet(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    create_packets = _packet_files(root)
    assert len(create_packets) == 1  # the Slice-2 create-time packet

    new_body = _content(root, "v2.md", "Version two body.\n")
    result = CliRunner().invoke(main, _update_args(config, new_body, "--owner-presented"))
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "GOV-UPD-001 v2"

    db_path = root / "groundtruth.db"
    assert _spec_versions(db_path, "GOV-UPD-001") == [1, 2]
    row = _current_row(db_path, "GOV-UPD-001")
    assert row is not None
    assert int(row["version"]) == 2
    assert row["description"] == new_body.read_text(encoding="utf-8")

    packets = _packet_files(root)
    assert len(packets) == 2  # create-time + update-time, distinct files
    update_packet = next(p for p in packets if p not in create_packets)
    # The -v<new_version> suffix prevents collision with the create-time packet.
    assert update_packet.name.endswith("-GOV-UPD-001-v2.json")
    packet = json.loads(update_packet.read_text(encoding="utf-8"))
    assert packet["action"] == "update"
    assert packet["artifact_id"] == "GOV-UPD-001"


# --- T-SU-8: carry-forward semantics for omitted optional fields -----------


def test_omitted_optional_fields_carry_forward_previous_values(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    # Seed with a non-default priority so carry-forward is observable.
    _seed_spec(config, content, "--priority", "P2")
    db_path = root / "groundtruth.db"
    seed_row = _current_row(db_path, "GOV-UPD-001")
    assert seed_row is not None
    assert seed_row["priority"] == "P2"
    assert seed_row["title"] == "Seed spec"

    new_body = _content(root, "v2.md", "Version two body.\n")
    # Update supplies neither --priority nor --title: both must carry forward.
    result = CliRunner().invoke(main, _update_args(config, new_body, "--owner-presented"))
    assert result.exit_code == 0, result.output

    row = _current_row(db_path, "GOV-UPD-001")
    assert row is not None
    assert int(row["version"]) == 2
    assert row["priority"] == "P2"
    assert row["title"] == "Seed spec"
    assert row["status"] == "specified"
    # Explicitly-supplied content did change.
    assert row["description"] == new_body.read_text(encoding="utf-8")


# --- T-SU-9: artifact_type is read from the live spec row, not the prefix --


def test_artifact_type_is_derived_from_live_spec_row_not_id_prefix(tmp_path: Path) -> None:
    root, config, _content_file = _project(tmp_path)
    # Seed a DCL spec; its stored type is "design_constraint".
    dcl_body = _content(root, "dcl.md", "## Constraint\nThe system must keep this invariant.\n")
    _seed_spec(config, dcl_body, spec_id="DCL-UPD-001")
    db_path = root / "groundtruth.db"
    seed_row = _current_row(db_path, "DCL-UPD-001")
    assert seed_row is not None
    assert seed_row["type"] == "design_constraint"

    new_body = _content(root, "dcl-v2.md", "## Constraint\nThe invariant is now stricter.\n")
    result = CliRunner().invoke(
        main,
        _update_args(config, new_body, "--owner-presented", "--dry-run", "--json", spec_id="DCL-UPD-001"),
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    # artifact_type comes from the stored row, NOT from a DCL- prefix lookup.
    assert payload["approval_packet"]["artifact_type"] == "design_constraint"


# --- T-SU-10: source_ref anchors to the previous version -------------------


def test_packet_source_ref_anchors_to_previous_version(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    new_body = _content(root, "v2.md", "Version two body.\n")
    result = CliRunner().invoke(main, _update_args(config, new_body, "--owner-presented"))
    assert result.exit_code == 0, result.output

    update_packet = next(p for p in _packet_files(root) if p.name.endswith("-v2.json"))
    packet = json.loads(update_packet.read_text(encoding="utf-8"))
    # source_ref anchors the update to the version being superseded (v1).
    assert packet["source_ref"] == "GOV-UPD-001@v1"


# --- T-SU-11: --approved-by overrides the default manual identity ----------


def test_approved_by_overrides_default_identity(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    new_body = _content(root, "v2.md", "Version two body.\n")
    result = CliRunner().invoke(main, _update_args(config, new_body, "--owner-presented", "--approved-by", "Mike"))
    assert result.exit_code == 0, result.output
    update_packet = next(p for p in _packet_files(root) if p.name.endswith("-v2.json"))
    packet = json.loads(update_packet.read_text(encoding="utf-8"))
    assert packet["approved_by"] == "Mike"


# --- T-SU-12: invalid --assertions-json raises before packet write ---------


def test_invalid_assertions_json_raises_before_packet_write(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    before = _packet_files(root)
    new_body = _content(root, "v2.md", "Version two body.\n")
    result = CliRunner().invoke(
        main,
        _update_args(config, new_body, "--owner-presented", "--assertions-json", '{"not": "a list"}'),
    )
    assert result.exit_code != 0
    assert "--assertions-json" in result.output
    # No new version, no new packet file.
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]
    assert _packet_files(root) == before
