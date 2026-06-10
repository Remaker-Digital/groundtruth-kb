import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from groundtruth_kb.cli import main


def test_register_command_success(tmp_path):
    runner = CliRunner()

    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = './groundtruth.db'\nproject_root = '.'\n", encoding="utf-8")

    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    db.close()

    result = runner.invoke(main, ["--config", str(toml_path), "application", "register", "foo"])
    assert result.exit_code == 0
    assert "Successfully registered" in result.output

    registry_file = tmp_path / "applications" / "registry.toml"
    assert registry_file.is_file()
    assert "foo" in registry_file.read_text(encoding="utf-8")

    app_toml = tmp_path / "applications" / "foo" / "application.toml"
    assert app_toml.is_file()
    assert 'name = "foo"' in app_toml.read_text(encoding="utf-8")


def test_register_mismatched_markers_fails(tmp_path):
    runner = CliRunner()
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = './groundtruth.db'\nproject_root = '.'\n", encoding="utf-8")
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    db.close()

    foo_dir = tmp_path / "applications" / "foo"
    foo_dir.mkdir(parents=True, exist_ok=True)
    json_marker = foo_dir / ".gtkb-app-isolation.json"
    json_marker.write_text('{"application": "Agent_Red"}', encoding="utf-8")

    result = runner.invoke(main, ["--config", str(toml_path), "application", "register", "foo"])
    assert result.exit_code != 0
    assert "slot-name mismatch" in result.output or "mismatch" in result.output.lower()


def test_register_cardinality_constraint_registry(tmp_path):
    runner = CliRunner()
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = './groundtruth.db'\nproject_root = '.'\n", encoding="utf-8")
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    db.close()

    result = runner.invoke(main, ["--config", str(toml_path), "application", "register", "foo"])
    assert result.exit_code == 0

    result = runner.invoke(main, ["--config", str(toml_path), "application", "register", "bar"])
    assert result.exit_code != 0
    assert "supports only one" in result.output or "unregister" in result.output
