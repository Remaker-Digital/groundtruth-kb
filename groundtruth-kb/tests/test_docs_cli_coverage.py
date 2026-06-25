"""Regression tests for scripts/check_docs_cli_coverage.py (WI-3306)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PKG_ROOT / "scripts" / "check_docs_cli_coverage.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_docs_cli_coverage_under_test", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = _load_checker()


def test_cli_command_enumeration_covers_dashboard_commands() -> None:
    commands = checker.get_cli_commands()
    assert commands, "CLI enumeration must not be empty when groundtruth_kb is importable"
    assert "dashboard init" in commands
    assert "project init" in commands
    assert len(commands) >= checker.EXPECTED_MIN_COMMANDS


def test_project_init_snippet_guard_flags_missing_project_name(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    bad = docs / "sample.md"
    bad.write_text("Run `gt project init --profile local-only` first.\n", encoding="utf-8")

    original_docs = checker.DOCS_DIR
    checker.DOCS_DIR = docs
    try:
        failures = checker.check_project_init_snippets()
    finally:
        checker.DOCS_DIR = original_docs

    assert failures
    assert "missing PROJECT_NAME" in failures[0]


def test_live_release_version_language_passes_after_wi3306_remediation() -> None:
    failures = checker.check_live_release_version_language()
    assert failures == []


def test_docs_checker_main_passes_in_package_tree() -> None:
    rc = checker.main()
    assert rc == 0


def test_chromadb_install_message_uses_search_extra() -> None:
    failures = checker.check_chromadb_install_message()
    assert failures == []
