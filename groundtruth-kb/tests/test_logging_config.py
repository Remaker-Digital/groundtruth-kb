"""Tests for groundtruth_kb._logging configuration module.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from groundtruth_kb._logging import (
    _PACKAGE_LOGGER,
    _setup_bridge_logging,
    configure_cli_logging,
)


@pytest.fixture(autouse=True)
def _clean_loggers() -> None:  # type: ignore[misc]
    """Reset logging state before each test to prevent cross-test leakage."""
    # Remove all handlers from root and package loggers
    root = logging.getLogger()
    pkg = logging.getLogger(_PACKAGE_LOGGER)
    for logger in (root, pkg):
        for h in logger.handlers[:]:
            logger.removeHandler(h)
            h.close()
    root.setLevel(logging.WARNING)
    pkg.setLevel(logging.WARNING)
    yield  # type: ignore[misc]
    # Cleanup after test
    for logger in (root, pkg):
        for h in logger.handlers[:]:
            logger.removeHandler(h)
            h.close()


class TestConfigureCliLogging:
    """Tests for configure_cli_logging()."""

    def test_configure_cli_logging_default_level(self) -> None:
        """Default is WARNING, handler is StreamHandler(stderr)."""
        configure_cli_logging()
        root = logging.getLogger()
        assert root.level == logging.WARNING
        assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)

    def test_configure_cli_logging_env_override(self) -> None:
        """GROUNDTRUTH_LOG_LEVEL=DEBUG sets DEBUG."""
        from groundtruth_kb._logging import _resolve_level

        with patch.dict(os.environ, {"GROUNDTRUTH_LOG_LEVEL": "DEBUG"}):
            assert _resolve_level("WARNING") == logging.DEBUG

    def test_configure_cli_logging_invalid_level(self) -> None:
        """Invalid level falls back to WARNING."""
        with patch.dict(os.environ, {"GROUNDTRUTH_LOG_LEVEL": "NOTAVALIDLEVEL"}):
            configure_cli_logging()
        root = logging.getLogger()
        assert root.level == logging.WARNING


class TestSetupBridgeLogging:
    """Tests for _setup_bridge_logging()."""

    def test_setup_bridge_logging_creates_file_handler(self, tmp_path: Path) -> None:
        """_setup_bridge_logging attaches FileHandler to package logger."""
        log_path = tmp_path / "test.log"
        _setup_bridge_logging(log_path)
        pkg = logging.getLogger(_PACKAGE_LOGGER)
        assert any(isinstance(h, logging.FileHandler) for h in pkg.handlers)

    def test_setup_bridge_logging_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Parent directory created if missing."""
        log_path = tmp_path / "deep" / "nested" / "test.log"
        _setup_bridge_logging(log_path)
        assert log_path.parent.exists()

    def test_setup_bridge_logging_writes_to_correct_path(self, tmp_path: Path) -> None:
        """Log records appear in the specified file."""
        log_path = tmp_path / "test.log"
        _setup_bridge_logging(log_path)
        logger = logging.getLogger(_PACKAGE_LOGGER)
        logger.info("hello from test")
        # Flush handlers
        for h in logger.handlers:
            h.flush()
        content = log_path.read_text(encoding="utf-8")
        assert "hello from test" in content

    def test_setup_bridge_logging_unwritable_path_falls_back_to_null_handler(self, tmp_path: Path) -> None:
        """When log_path parent is a file, falls back to NullHandler."""
        # Create a file where the parent dir should be, making mkdir fail
        blocker = tmp_path / "blocker"
        blocker.write_text("I am a file, not a directory")
        log_path = blocker / "test.log"
        _setup_bridge_logging(log_path)
        pkg = logging.getLogger(_PACKAGE_LOGGER)
        assert any(isinstance(h, logging.NullHandler) for h in pkg.handlers)
        assert not any(isinstance(h, logging.FileHandler) for h in pkg.handlers)

    def test_setup_bridge_logging_unwritable_path_emits_stderr_warning(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """When path is unwritable and stderr is available, writes warning."""
        blocker = tmp_path / "blocker"
        blocker.write_text("I am a file, not a directory")
        log_path = blocker / "test.log"
        _setup_bridge_logging(log_path)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "falling back to NullHandler" in captured.err

    def test_setup_bridge_logging_missing_stderr(self, tmp_path: Path) -> None:
        """When sys.stderr is None, no raise and NullHandler attached."""
        blocker = tmp_path / "blocker"
        blocker.write_text("I am a file, not a directory")
        log_path = blocker / "test.log"
        import sys

        original_stderr = sys.stderr
        try:
            sys.stderr = None  # type: ignore[assignment]
            # Must not raise
            _setup_bridge_logging(log_path)
        finally:
            sys.stderr = original_stderr
        pkg = logging.getLogger(_PACKAGE_LOGGER)
        assert any(isinstance(h, logging.NullHandler) for h in pkg.handlers)

    def test_setup_bridge_logging_idempotent(self, tmp_path: Path) -> None:
        """Calling twice does not duplicate handlers or leak file descriptors."""
        log_path = tmp_path / "test.log"
        _setup_bridge_logging(log_path)
        _setup_bridge_logging(log_path)
        pkg = logging.getLogger(_PACKAGE_LOGGER)
        # Should have exactly one handler (the second call replaces the first)
        assert len(pkg.handlers) == 1
        assert isinstance(pkg.handlers[0], logging.FileHandler)


class TestSplitDefaults:
    """Tests for split bridge/CLI level defaults."""

    def test_bridge_default_level_is_info(self, tmp_path: Path) -> None:
        """_setup_bridge_logging sets package logger level to INFO."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GROUNDTRUTH_LOG_LEVEL", None)
            log_path = tmp_path / "test.log"
            _setup_bridge_logging(log_path)
        pkg = logging.getLogger(_PACKAGE_LOGGER)
        assert pkg.level == logging.INFO

    def test_cli_default_level_is_warning(self) -> None:
        """configure_cli_logging sets root logger level to WARNING."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GROUNDTRUTH_LOG_LEVEL", None)
            configure_cli_logging()
        root = logging.getLogger()
        assert root.level == logging.WARNING

    def test_env_var_overrides_bridge_default(self, tmp_path: Path) -> None:
        """GROUNDTRUTH_LOG_LEVEL=WARNING overrides bridge's INFO default."""
        with patch.dict(os.environ, {"GROUNDTRUTH_LOG_LEVEL": "WARNING"}):
            log_path = tmp_path / "test.log"
            _setup_bridge_logging(log_path)
        pkg = logging.getLogger(_PACKAGE_LOGGER)
        assert pkg.level == logging.WARNING
