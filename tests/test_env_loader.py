"""Tests for the shared .env.local loader utility (R7 refactoring).

Verifies the three loading modes (setdefault, override, check_only)
and edge cases (missing file, comments, blank lines, malformed entries).

Run:
    python -m pytest tests/test_env_loader.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import os
from pathlib import Path

import pytest

from scripts._env import _parse_env_file, load_env_local


# ---------------------------------------------------------------------------
# R7-01 through R7-04: _parse_env_file() unit tests
# ---------------------------------------------------------------------------


class TestParseEnvFile:
    """Verify low-level .env file parser."""

    def test_r7_01_parses_key_value_pairs(self, tmp_path: Path):
        """Standard KEY=VALUE lines are parsed correctly."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("FOO=bar\nBAZ=qux\n")
        result = _parse_env_file(env_file)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_r7_02_skips_comments_and_blanks(self, tmp_path: Path):
        """Comments (#) and blank lines are ignored."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("# This is a comment\n\nKEY1=val1\n  # indented comment\n\nKEY2=val2\n")
        result = _parse_env_file(env_file)
        assert result == {"KEY1": "val1", "KEY2": "val2"}

    def test_r7_03_handles_values_with_equals(self, tmp_path: Path):
        """Values containing '=' are preserved (partition on first '=')."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("CONNECTION_STRING=host=localhost;port=5432\n")
        result = _parse_env_file(env_file)
        assert result == {"CONNECTION_STRING": "host=localhost;port=5432"}

    def test_r7_04_returns_empty_for_missing_file(self, tmp_path: Path):
        """Non-existent file returns empty dict without error."""
        env_file = tmp_path / "nonexistent.env"
        result = _parse_env_file(env_file)
        assert result == {}

    def test_r7_05_strips_whitespace(self, tmp_path: Path):
        """Keys and values are stripped of surrounding whitespace."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("  KEY1  =  value1  \nKEY2=value2\n")
        result = _parse_env_file(env_file)
        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_r7_06_skips_lines_without_equals(self, tmp_path: Path):
        """Lines without '=' are skipped (malformed)."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("GOOD=value\nmalformed_line\nALSO_GOOD=yes\n")
        result = _parse_env_file(env_file)
        assert result == {"GOOD": "value", "ALSO_GOOD": "yes"}

    def test_r7_07_empty_key_skipped(self, tmp_path: Path):
        """Line with empty key (e.g., '=value') is skipped."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("=no_key\nVALID=yes\n")
        result = _parse_env_file(env_file)
        assert result == {"VALID": "yes"}


# ---------------------------------------------------------------------------
# R7-08 through R7-13: load_env_local() integration tests
# ---------------------------------------------------------------------------


class TestLoadEnvLocal:
    """Verify load_env_local() modes and behavior."""

    def test_r7_08_setdefault_mode(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Default mode uses setdefault — existing env vars are NOT overwritten."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("R7_TEST_A=from_file\nR7_TEST_B=from_file\n")
        # Pre-set one var in the environment
        monkeypatch.setenv("R7_TEST_A", "from_env")
        load_env_local(env_file=env_file)
        # Existing var preserved, new var loaded
        assert os.environ["R7_TEST_A"] == "from_env"
        assert os.environ["R7_TEST_B"] == "from_file"
        # Cleanup
        monkeypatch.delenv("R7_TEST_B", raising=False)

    def test_r7_09_override_mode(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Override mode overwrites existing env vars."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("R7_TEST_C=from_file\n")
        monkeypatch.setenv("R7_TEST_C", "from_env")
        load_env_local(override=True, env_file=env_file)
        assert os.environ["R7_TEST_C"] == "from_file"

    def test_r7_10_check_only_mode(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """check_only mode returns dict without modifying os.environ."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("R7_TEST_D=should_not_appear\n")
        monkeypatch.delenv("R7_TEST_D", raising=False)
        result = load_env_local(check_only=True, env_file=env_file)
        assert result == {"R7_TEST_D": "should_not_appear"}
        assert "R7_TEST_D" not in os.environ

    def test_r7_11_returns_parsed_values(self, tmp_path: Path):
        """All modes return the parsed dict from the file."""
        env_file = tmp_path / ".env.local"
        env_file.write_text("KEY1=val1\nKEY2=val2\n")
        result = load_env_local(env_file=env_file)
        assert result == {"KEY1": "val1", "KEY2": "val2"}

    def test_r7_12_missing_file_silent(self, tmp_path: Path):
        """Missing .env.local is silently ignored (returns empty dict)."""
        env_file = tmp_path / "nonexistent.env"
        result = load_env_local(env_file=env_file)
        assert result == {}

    def test_r7_13_custom_env_file_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Custom env_file path is used instead of default."""
        custom = tmp_path / "custom.env"
        custom.write_text("R7_CUSTOM=hello\n")
        monkeypatch.delenv("R7_CUSTOM", raising=False)
        load_env_local(env_file=custom)
        assert os.environ["R7_CUSTOM"] == "hello"
        monkeypatch.delenv("R7_CUSTOM", raising=False)
