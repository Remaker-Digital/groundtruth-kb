"""Tests for bridge module log record emission via stdlib logging.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from groundtruth_kb._logging import _PACKAGE_LOGGER, _setup_bridge_logging


@pytest.fixture(autouse=True)
def _clean_loggers() -> None:  # type: ignore[misc]
    """Reset logging state before each test."""
    pkg = logging.getLogger(_PACKAGE_LOGGER)
    for h in pkg.handlers[:]:
        pkg.removeHandler(h)
        h.close()
    pkg.setLevel(logging.WARNING)
    yield  # type: ignore[misc]
    for h in pkg.handlers[:]:
        pkg.removeHandler(h)
        h.close()


def test_poller_emits_info_on_scan(caplog: pytest.LogCaptureFixture) -> None:
    """Poller scan emits INFO-level log record."""
    poller_logger = logging.getLogger("groundtruth_kb.bridge.poller")
    with caplog.at_level(logging.INFO, logger=_PACKAGE_LOGGER):
        poller_logger.info("Scan found %d items", 5)
    assert any("Scan found 5 items" in r.message for r in caplog.records)
    assert any(r.levelno == logging.INFO for r in caplog.records if "Scan found" in r.message)


def test_worker_emits_info_on_dispatch(caplog: pytest.LogCaptureFixture) -> None:
    """Worker dispatch emits INFO record."""
    worker_logger = logging.getLogger("groundtruth_kb.bridge.worker")
    with caplog.at_level(logging.INFO, logger=_PACKAGE_LOGGER):
        worker_logger.info("dispatching resident worker run: targets=%s new=%d contexts=%d", "msg-1", 1, 1)
    assert any("dispatching resident worker run" in r.message for r in caplog.records)


def test_db_emits_warning_on_chromadb_fallback(caplog: pytest.LogCaptureFixture) -> None:
    """ChromaDB fallback logs WARNING."""
    db_logger = logging.getLogger("groundtruth_kb.db")
    with caplog.at_level(logging.WARNING, logger=_PACKAGE_LOGGER):
        db_logger.warning("ChromaDB search failed, falling back to SQLite LIKE: %s", "test error")
    assert any("ChromaDB search failed" in r.message for r in caplog.records)
    assert any(r.levelno == logging.WARNING for r in caplog.records if "ChromaDB" in r.message)


def test_db_emits_info_on_migration(caplog: pytest.LogCaptureFixture) -> None:
    """Migration completion logs INFO."""
    db_logger = logging.getLogger("groundtruth_kb.db")
    with caplog.at_level(logging.INFO, logger=_PACKAGE_LOGGER):
        db_logger.info("Applied migration: %s", "add type column")
    assert any("Applied migration" in r.message for r in caplog.records)


def test_bridge_default_writes_info_to_file(tmp_path: Path) -> None:
    """With GROUNDTRUTH_LOG_LEVEL unset, bridge logging writes INFO to file."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("GROUNDTRUTH_LOG_LEVEL", None)
        log_path = tmp_path / "bridge-test.log"
        _setup_bridge_logging(log_path)

    logger = logging.getLogger(_PACKAGE_LOGGER)
    logger.info("test info message")
    for h in logger.handlers:
        h.flush()

    content = log_path.read_text(encoding="utf-8")
    assert "test info message" in content
