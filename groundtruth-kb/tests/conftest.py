"""
Shared test fixtures for groundtruth-kb.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry


@pytest.fixture()
def runner() -> CliRunner:
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    """Create a project dir with groundtruth.toml and sample files."""
    toml = tmp_path / "groundtruth.toml"
    toml.write_text(
        f'[groundtruth]\ndb_path = "{(tmp_path / "groundtruth.db").as_posix()}"\n'
        f'project_root = "{tmp_path.as_posix()}"\napp_title = "Test Project"\n',
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def db(tmp_path: Path) -> KnowledgeDB:
    """Fresh KnowledgeDB with builtin gates in a temp directory."""
    db_path = tmp_path / "test.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


@pytest.fixture()
def db_no_gates(tmp_path: Path) -> KnowledgeDB:
    """KnowledgeDB without any governance gates."""
    db_path = tmp_path / "test_nogates.db"
    return KnowledgeDB(db_path=db_path)
