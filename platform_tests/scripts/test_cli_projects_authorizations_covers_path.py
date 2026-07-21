"""Tests for gt projects authorizations --covers-path (GFR Slice C Finding 4.2).

Work item: WI-5647 (TEST-11692).
Governing: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import projects_cmd
from groundtruth_kb.db import KnowledgeDB


def _make_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "groundtruth.db"
    chroma_path = tmp_path / "chroma"
    db = KnowledgeDB(db_path=db_path, chroma_path=chroma_path)
    db.insert_deliberation(
        "DELIB-TEST",
        source_type="owner_conversation",
        title="Test deliberation",
        summary="Test",
        content="Test content",
        changed_by="test",
        change_reason="test setup",
    )
    db.insert_project("Test Project", "test", "test setup", id="PROJECT-TEST")
    db.insert_spec("SPEC-TEST-001", "Test Spec", "specified", "test", "test setup")
    db.insert_project_authorization(
        "PROJECT-TEST",
        "Source+Test Auth",
        "DELIB-TEST",
        "Test scope",
        "test",
        "test setup",
        id="PAUTH-SRC-TEST",
        allowed_mutation_classes=["source", "test"],
        included_spec_ids=["SPEC-TEST-001"],
    )
    db.insert_project_authorization(
        "PROJECT-TEST",
        "Config Only Auth",
        "DELIB-TEST",
        "Test scope",
        "test",
        "test setup",
        id="PAUTH-CONFIG-ONLY",
        allowed_mutation_classes=["config"],
        included_spec_ids=["SPEC-TEST-001"],
    )
    db.close()
    return db_path


class TestCoversPath:
    """Finding 4.2: --covers-path filters PAUTHs by mutation class."""

    def test_covers_path_filters_to_matching_pauth(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--covers-path with a source-class path returns only PAUTHs allowing 'source'."""
        db_path = _make_db(tmp_path)

        def _fake_project_service(ctx):
            from groundtruth_kb.project.lifecycle import ProjectLifecycleService

            db = KnowledgeDB(db_path=db_path, chroma_path=tmp_path / "chroma")
            return db, ProjectLifecycleService(db)

        monkeypatch.setattr("groundtruth_kb.cli._project_service", _fake_project_service)
        runner = CliRunner()
        result = runner.invoke(
            projects_cmd,
            ["authorizations", "PROJECT-TEST", "--covers-path", "scripts/foo.py"],
        )
        assert result.exit_code == 0
        assert "PAUTH-SRC-TEST" in result.output
        assert "PAUTH-CONFIG-ONLY" not in result.output

    def test_covers_path_no_match_clear_message(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--covers-path with no matching PAUTH prints clear message."""
        db_path = _make_db(tmp_path)

        def _fake_project_service(ctx):
            from groundtruth_kb.project.lifecycle import ProjectLifecycleService

            db = KnowledgeDB(db_path=db_path, chroma_path=tmp_path / "chroma")
            return db, ProjectLifecycleService(db)

        monkeypatch.setattr("groundtruth_kb.cli._project_service", _fake_project_service)
        runner = CliRunner()
        result = runner.invoke(
            projects_cmd,
            ["authorizations", "PROJECT-TEST", "--covers-path", "bridge/foo-001.md"],
        )
        assert result.exit_code == 0
        assert "No active project authorization covers path: bridge/foo-001.md" in result.output

    def test_covers_path_json_output(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--covers-path with --json emits filtered JSON array."""
        db_path = _make_db(tmp_path)

        def _fake_project_service(ctx):
            from groundtruth_kb.project.lifecycle import ProjectLifecycleService

            db = KnowledgeDB(db_path=db_path, chroma_path=tmp_path / "chroma")
            return db, ProjectLifecycleService(db)

        monkeypatch.setattr("groundtruth_kb.cli._project_service", _fake_project_service)
        runner = CliRunner()
        result = runner.invoke(
            projects_cmd,
            [
                "authorizations",
                "PROJECT-TEST",
                "--covers-path",
                "platform_tests/scripts/test_foo.py",
                "--json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["id"] == "PAUTH-SRC-TEST"
