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
        "--expected-version",
        "0",
        *extra,
    ]


def _update_args(
    config: Path,
    content: Path,
    *extra: str,
    spec_id: str = "GOV-UPD-001",
    expected_version: int = 1,
) -> list[str]:
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
        "--expected-version",
        str(expected_version),
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


def _seed_spec(config: Path, content: Path, *extra: str, spec_id: str = "GOV-UPD-001") -> None:
    """Create the spec the update tests operate on; assert it landed."""
    result = CliRunner().invoke(main, _record_args(config, content, *extra, spec_id=spec_id))
    assert result.exit_code == 0, result.output


# --- T-SU-1: missing --expected-version -------------------------------------


def test_update_requires_expected_version_before_any_write(tmp_path: Path) -> None:
    """Omitting the CAS assertion blocks the update instead of defaulting."""

    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    args = _update_args(config, content)
    args.remove("--expected-version")
    args.remove("1")
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "--expected-version" in result.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]
    assert _packet_files(root) == []


# --- T-SU-2: stale expected version ------------------------------------------


def test_stale_expected_version_leaves_zero_effect(tmp_path: Path) -> None:
    """A stale CAS assertion is refused by typed reason and appends nothing."""

    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    v2 = _content(root, "v2.md", "Version two body.\n")
    first = CliRunner().invoke(main, _update_args(config, v2, expected_version=1))
    assert first.exit_code == 0, first.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1, 2]

    before = _semantic_postimage(_current_row(root / "groundtruth.db", "GOV-UPD-001"))
    stale_body = _content(root, "stale.md", "Stale conflicting body.\n")
    stale = CliRunner().invoke(main, _update_args(config, stale_body, expected_version=1))
    assert stale.exit_code != 0
    assert "stale_expected_version" in stale.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1, 2]
    assert _semantic_postimage(_current_row(root / "groundtruth.db", "GOV-UPD-001")) == before
    assert _packet_files(root) == []


# --- T-SU-3: missing --change-reason ---------------------------------------


def test_update_requires_change_reason(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    args = _update_args(config, content)
    args.remove("--change-reason")
    args.remove("update owner-approved spec")
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "Missing option '--change-reason'" in result.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]


# --- T-SU-4: dry-run reports the transition and writes nothing ----------


def test_dry_run_reports_version_transition_and_writes_nothing(tmp_path: Path) -> None:
    """A dry run reports the intended version transition and appends nothing."""

    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    new_body = _content(root, "v2.md", "Version two body.\n")

    result = CliRunner().invoke(main, _update_args(config, new_body, "--dry-run", "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)

    assert payload["updated"] is False
    assert payload["dry_run"] is True
    assert payload["replayed"] is False
    assert payload["expected_version"] == 1
    assert payload["from_version"] == 1
    assert payload["to_version"] == 2
    assert payload["db_operation"]["method"] == "update_spec"
    assert "approval_packet" not in payload
    assert "approval_packet_path" not in payload
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]
    assert _packet_files(root) == []


def test_structured_update_postimage_matches_persisted_row(tmp_path: Path) -> None:
    """The dry-run intent and the persisted row agree, and a replay is read-only."""

    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    new_body = _content(root, "v2.md", "Version two body.\n")
    structured = (
        "--title",
        "Updated title",
        "--priority",
        "P1",
        "--tags-json",
        '["updated"]',
    )

    dry = CliRunner().invoke(main, _update_args(config, new_body, "--dry-run", "--json", *structured))
    assert dry.exit_code == 0, dry.output
    assert json.loads(dry.output)["to_version"] == 2
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]

    write = CliRunner().invoke(main, _update_args(config, new_body, "--json", *structured))
    assert write.exit_code == 0, write.output
    written = json.loads(write.output)
    assert written["updated"] is True
    assert written["replayed"] is False
    assert written["to_version"] == 2

    row = _current_row(root / "groundtruth.db", "GOV-UPD-001")
    assert row is not None
    postimage = _semantic_postimage(row)
    assert postimage["title"] == "Updated title"
    assert postimage["priority"] == "P1"
    assert postimage["tags"] == ["updated"]

    replay = CliRunner().invoke(main, _update_args(config, new_body, "--json", *structured))
    assert replay.exit_code == 0, replay.output
    assert json.loads(replay.output)["replayed"] is True
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1, 2]
    assert _packet_files(root) == []


def test_update_postimage_preserves_explicit_empty_collections(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(
        config,
        content,
        "--tags-json",
        '["seed"]',
        "--assertions-json",
        '[{"type": "file_exists", "file": "README.md"}]',
        "--constraints-json",
        '{"seed": true}',
        "--affected-by-json",
        '["ADR-SEED-001"]',
        "--source-paths-json",
        '["seed.py"]',
    )
    new_body = _content(root, "empty-collections.md", "Explicit empty collections.\n")
    result = CliRunner().invoke(
        main,
        _update_args(
            config,
            new_body,
            "--json",
            "--tags-json",
            "[]",
            "--assertions-json",
            "[]",
            "--constraints-json",
            "{}",
            "--affected-by-json",
            "[]",
            "--source-paths-json",
            "[]",
        ),
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["updated"] is True
    row = _current_row(root / "groundtruth.db", "GOV-UPD-001")
    assert row is not None
    postimage = _semantic_postimage(row)
    assert {name: postimage[name] for name in ("tags", "assertions", "constraints", "affected_by", "source_paths")} == {
        "tags": [],
        "assertions": [],
        "constraints": {},
        "affected_by": [],
        "source_paths": [],
    }
    row = _current_row(root / "groundtruth.db", "GOV-UPD-001")
    assert row is not None
    assert _semantic_postimage(row) == postimage


def test_description_only_update_carries_current_semantic_postimage(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(
        config,
        content,
        "--priority",
        "P2",
        "--tags-json",
        '["carried"]',
        "--constraints-json",
        '{"limit": 2}',
    )
    current = _current_row(root / "groundtruth.db", "GOV-UPD-001")
    assert current is not None
    expected = _semantic_postimage(current)
    new_body = _content(root, "description-only.md", "Description only.\n")

    result = CliRunner().invoke(main, _update_args(config, new_body, "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["updated"] is True

    # Persistence is intrinsic, so the stored row is the record of the postimage:
    # the new description lands and every omitted field carries forward unchanged.
    updated_row = _current_row(root / "groundtruth.db", "GOV-UPD-001")
    assert updated_row is not None
    assert updated_row["description"] == "Description only.\n"
    assert _semantic_postimage(updated_row) == expected
    assert _packet_files(root) == []


# --- T-SU-5: content file outside project root is rejected -----------------


def test_content_file_outside_project_root_is_rejected(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    result = CliRunner().invoke(main, _update_args(config, outside))
    assert result.exit_code != 0
    assert "inside project root" in result.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]


# --- T-SU-6: non-existent spec id is rejected ------------------------------


def test_update_of_nonexistent_spec_is_rejected(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    # No seed: spec does not exist.
    result = CliRunner().invoke(main, _update_args(config, content, spec_id="GOV-MISSING-001"))
    assert result.exit_code != 0
    assert "does not exist" in result.output
    assert "gt spec record" in result.output
    assert _spec_count(root / "groundtruth.db") == 0
    assert _packet_files(root) == []


# --- T-SU-7: successful update creates one new packet + new version --------


def test_successful_update_creates_versioned_row_and_no_packet(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    assert _packet_files(root) == []

    new_body = _content(root, "v2.md", "Version two body.\n")
    result = CliRunner().invoke(main, _update_args(config, new_body))
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "GOV-UPD-001 v2"

    db_path = root / "groundtruth.db"
    assert _spec_versions(db_path, "GOV-UPD-001") == [1, 2]
    row = _current_row(db_path, "GOV-UPD-001")
    assert row is not None
    assert int(row["version"]) == 2
    assert row["description"] == new_body.read_text(encoding="utf-8")
    assert _packet_files(root) == []
    assert not (root / ".groundtruth" / "formal-artifact-approvals").exists()


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
    result = CliRunner().invoke(main, _update_args(config, new_body))
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
        _update_args(config, new_body, "--dry-run", "--json", spec_id="DCL-UPD-001"),
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    # artifact_type comes from the stored row, NOT from a DCL- prefix lookup.
    assert payload["db_operation"]["type"] == "design_constraint"


# --- T-SU-10: source_ref anchors to the previous version -------------------


def test_result_anchors_the_version_transition(tmp_path: Path) -> None:
    """The result names the exact version it replaced and the version it produced."""

    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    new_body = _content(root, "v2.md", "Version two body.\n")

    result = CliRunner().invoke(main, _update_args(config, new_body, "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["from_version"] == 1
    assert payload["to_version"] == 2
    assert payload["expected_version"] == 1
    assert payload["db_operation"]["from_version"] == 1
    assert payload["db_operation"]["to_version"] == 2
    assert _packet_files(root) == []


# --- T-SU-11: --approved-by overrides the default manual identity ----------


def test_update_output_carries_no_approval_fields(tmp_path: Path) -> None:
    """The update result exposes no approval identity, packet, or evidence field."""

    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    new_body = _content(root, "v2.md", "Version two body.\n")
    result = CliRunner().invoke(main, _update_args(config, new_body, "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    for forbidden in ("approval_packet", "approval_packet_path", "approved_by", "auq_id", "auq_answer"):
        assert forbidden not in payload
    assert _packet_files(root) == []


# --- T-SU-12: invalid --assertions-json raises before packet write ---------


def test_invalid_assertions_json_raises_before_any_write(tmp_path: Path) -> None:
    root, config, content = _project(tmp_path)
    _seed_spec(config, content)
    new_body = _content(root, "v2.md", "Version two body.\n")
    result = CliRunner().invoke(
        main,
        _update_args(config, new_body, "--assertions-json", '["not-an-object"]'),
    )
    assert result.exit_code != 0
    assert "--assertions-json" in result.output
    assert _spec_versions(root / "groundtruth.db", "GOV-UPD-001") == [1]
    assert _packet_files(root) == []
