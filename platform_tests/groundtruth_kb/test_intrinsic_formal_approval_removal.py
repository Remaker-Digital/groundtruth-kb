"""TEST-12151: canonical formal persistence carries no approval-process evidence.

Work item: WI-6897. Governing: DCL-ARTIFACT-APPROVAL-HOOK-001,
GOV-ARTIFACT-APPROVAL-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.

This module is the reviewed TEST-12151 selector at its canonical path. It is
written test-first and fails against the approval-packet implementation at the
frozen base; it passes once the intrinsic-persistence cutover lands.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from click.testing import CliRunner


def _repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "groundtruth-kb" / "src" / "groundtruth_kb").is_dir():
            return candidate
    raise AssertionError("GT-KB repository root is not discoverable")


REPO_ROOT = _repo_root()
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

SPEC_ID = "GOV-TEST-T12151-001"
FORBIDDEN_PROCESS_TOKENS = (
    ".groundtruth/formal-artifact-approvals",
    "approval_packet",
    "approval_state",
    "approved_by",
    "auq_answer",
    "auq_id",
    "owner_presented",
)


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    return root, config


def _content(root: Path, name: str, body: str) -> Path:
    path = root / name
    path.write_text(body, encoding="utf-8")
    return path


def _record_args(config: Path, content: Path, *, title: str = "Canonical formal persistence") -> list[str]:
    return [
        "--config",
        str(config),
        "spec",
        "record",
        "--id",
        SPEC_ID,
        "--title",
        title,
        "--status",
        "active",
        "--content-file",
        str(content),
        "--change-reason",
        "TEST-12151 isolated create",
        "--expected-version",
        "0",
        "--type",
        "governance",
        "--priority",
        "P0",
        "--scope",
        "isolated TEST-12151 fixture",
        "--section",
        "canonical_formal_persistence",
        "--handle",
        "gov-test-t12151-001",
        "--tags-json",
        '["test-12151"]',
        "--assertions-json",
        "[]",
        "--constraints-json",
        '{"complete_postimage":true,"exact_expected_version":true}',
        "--affected-by-json",
        "[]",
        "--testability",
        "automatable",
        "--source-paths-json",
        "[]",
        "--application-scope",
        "gtkb_platform",
        "--json",
    ]


def _update_args(config: Path, content: Path, expected_version: int, *, title: str) -> list[str]:
    return [
        "--config",
        str(config),
        "spec",
        "update",
        "--id",
        SPEC_ID,
        "--content-file",
        str(content),
        "--change-reason",
        "TEST-12151 isolated update",
        "--expected-version",
        str(expected_version),
        "--title",
        title,
        "--json",
    ]


def _invoke(args: list[str]):
    return CliRunner().invoke(main, args)


def _invoke_ok(args: list[str]):
    result = _invoke(args)
    assert result.exit_code == 0, result.output
    return result


def _current(root: Path) -> dict[str, object]:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        row = db.get_spec(SPEC_ID)
    finally:
        db.close()
    assert row is not None
    return row


def _versions(root: Path) -> list[int]:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        rows = db.get_spec_history(SPEC_ID)
    finally:
        db.close()
    return [int(row["version"]) for row in rows]


def _assert_no_process_directory(root: Path) -> None:
    assert not (root / ".groundtruth" / "formal-artifact-approvals").exists()


def test_intrinsic_formal_approval_and_process_artifact_absence(tmp_path: Path) -> None:
    """GOV-ARTIFACT-APPROVAL-001:positive; canonical postimage is authority."""

    root, config = _project(tmp_path)
    content = _content(root, "v1.md", "# Canonical formal persistence\n")
    result = _invoke_ok(_record_args(config, content))
    payload = json.loads(result.output)
    row = _current(root)

    assert int(row["version"]) == 1
    assert row["description"] == "# Canonical formal persistence\n"
    assert row["priority"] == "P0"
    assert row["provisional_until"] is None
    assert row["implementation_verified_at"] is None
    assert row["retired_at"] is None
    assert row["parent"] is None
    assert "approval_packet" not in payload
    assert "approval_packet_path" not in payload
    _assert_no_process_directory(root)


def test_all_formal_writers_share_canonical_persistence(tmp_path: Path) -> None:
    """DCL-ARTIFACT-APPROVAL-HOOK-001:positive; create and update share the contract."""

    root, config = _project(tmp_path)
    v1 = _content(root, "v1.md", "Version one.\n")
    v2 = _content(root, "v2.md", "Version two.\n")
    _invoke_ok(_record_args(config, v1))
    _invoke_ok(_update_args(config, v2, 1, title="Canonical formal persistence v2"))

    row = _current(root)
    assert int(row["version"]) == 2
    assert row["description"] == "Version two.\n"
    assert row["title"] == "Canonical formal persistence v2"
    assert _versions(root) == [2, 1]
    _assert_no_process_directory(root)

    record_help = _invoke(["spec", "record", "--help"])
    update_help = _invoke(["spec", "update", "--help"])
    assert record_help.exit_code == 0
    assert update_help.exit_code == 0
    combined_help = record_help.output + update_help.output
    for legacy_option in ("--auq-id", "--auq-answer", "--owner-presented", "--approved-by"):
        assert legacy_option not in combined_help
    assert "--expected-version" in record_help.output
    assert "--expected-version" in update_help.output


def test_failure_atomicity_and_exact_replay(tmp_path: Path) -> None:
    """Exact replay is read-only and an injected transaction failure appends nothing."""

    root, config = _project(tmp_path)
    v1 = _content(root, "v1.md", "Version one.\n")
    v2 = _content(root, "v2.md", "Version two.\n")
    v3 = _content(root, "v3.md", "Version three must roll back.\n")

    create_args = _record_args(config, v1)
    _invoke_ok(create_args)
    replayed_create = _invoke_ok(create_args)
    assert json.loads(replayed_create.output).get("replayed") is True
    assert _versions(root) == [1]

    update_args = _update_args(config, v2, 1, title="Canonical formal persistence v2")
    _invoke_ok(update_args)
    replayed_update = _invoke_ok(update_args)
    assert json.loads(replayed_update.output).get("replayed") is True
    assert _versions(root) == [2, 1]

    with sqlite3.connect(root / "groundtruth.db") as conn:
        conn.execute(
            """
            CREATE TRIGGER test_12151_injected_failure
            BEFORE INSERT ON specifications
            WHEN NEW.id = 'GOV-TEST-T12151-001' AND NEW.version = 3
            BEGIN
              SELECT RAISE(ABORT, 'injected mid-transaction failure');
            END
            """
        )
        conn.commit()

    failed = _invoke(_update_args(config, v3, 2, title="Must not persist"))
    assert failed.exit_code != 0
    assert _versions(root) == [2, 1]
    assert _current(root)["description"] == "Version two.\n"
    _assert_no_process_directory(root)


def test_stale_cas_and_collision_leave_zero_effect(tmp_path: Path) -> None:
    """GOV-ARTIFACT-APPROVAL-001:negative; stale and conflicting input append nothing."""

    root, config = _project(tmp_path)
    v1 = _content(root, "v1.md", "Version one.\n")
    v2 = _content(root, "v2.md", "Version two.\n")
    stale = _content(root, "stale.md", "Stale conflicting version.\n")
    collision = _content(root, "collision.md", "Record collision.\n")

    _invoke_ok(_record_args(config, v1))
    _invoke_ok(_update_args(config, v2, 1, title="Version two"))
    before = _current(root)

    stale_result = _invoke(_update_args(config, stale, 1, title="Stale"))
    assert stale_result.exit_code != 0
    assert "stale_expected_version" in stale_result.output
    assert _versions(root) == [2, 1]
    assert _current(root) == before

    collision_result = _invoke(_record_args(config, collision, title="Record collision"))
    assert collision_result.exit_code != 0
    assert "record_collision" in collision_result.output
    assert _versions(root) == [2, 1]
    assert _current(root) == before
    _assert_no_process_directory(root)


def test_clean_initialization_does_not_create_process_artifacts(tmp_path: Path) -> None:
    """A clean project remains free of approval-process storage after formal writes."""

    root, config = _project(tmp_path)
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    db.close()
    _assert_no_process_directory(root)

    v1 = _content(root, "v1.md", "Version one.\n")
    v2 = _content(root, "v2.md", "Version two.\n")
    _invoke_ok(_record_args(config, v1))
    _invoke_ok(_update_args(config, v2, 1, title="Version two"))
    _assert_no_process_directory(root)

    live_sources = [
        REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "cli_spec_record.py",
        REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "cli_spec_update.py",
    ]
    for source in live_sources:
        text = source.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_PROCESS_TOKENS:
            assert token not in text, f"{source.relative_to(REPO_ROOT)} retains {token}"


def test_current_reader_has_no_process_evidence_fallback(tmp_path: Path) -> None:
    """DCL-ARTIFACT-APPROVAL-HOOK-001:negative; malformed current state cannot fall back."""

    root, config = _project(tmp_path)
    v1 = _content(root, "v1.md", "Valid version one.\n")
    _invoke_ok(_record_args(config, v1))

    with sqlite3.connect(root / "groundtruth.db") as conn:
        conn.row_factory = sqlite3.Row
        current = dict(
            conn.execute(
                "SELECT * FROM current_specifications WHERE id = ? AND version = 1",
                (SPEC_ID,),
            ).fetchone()
        )
        # ``specifications`` declares ``rowid`` as an explicit
        # ``INTEGER PRIMARY KEY AUTOINCREMENT`` column, and
        # ``current_specifications`` is ``SELECT s.*``, so the view propagates it.
        # Copying it forward would reinsert version 1's surrogate key and fail on
        # ``UNIQUE constraint failed: specifications.rowid`` inside the fixture,
        # before any production code runs. Excluding it lets SQLite allocate a
        # fresh key while every semantic column is still copied verbatim.
        columns = [row[1] for row in conn.execute("PRAGMA table_info(specifications)") if row[1] != "rowid"]
        current["version"] = 2
        current["title"] = "Malformed current version"
        current["tags"] = "{not-json"
        current["changed_at"] = "2026-09-05T00:00:00Z"
        values = [current.get(column) for column in columns]
        placeholders = ",".join("?" for _ in columns)
        conn.execute(
            f"INSERT INTO specifications ({','.join(columns)}) VALUES ({placeholders})",
            values,
        )
        conn.commit()

    shown = _invoke(["--config", str(config), "spec", "show", SPEC_ID, "--json"])
    assert shown.exit_code != 0
    assert "canonical_row_integrity_failed" in shown.output
    assert "Valid version one" not in shown.output
    assert _versions(root) == [2, 1]
    _assert_no_process_directory(root)
