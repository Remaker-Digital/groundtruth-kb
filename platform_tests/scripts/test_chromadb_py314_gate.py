"""Regression tests for the WI-4561 ChromaDB Python-3.14 availability gate.

Context: ``groundtruth_kb.db`` previously computed availability as
``importlib.util.find_spec("chromadb") is not None and sys.version_info < (3, 14)``.
On the gt venv (Python 3.14.0) that static ceiling force-disabled an installed,
functional chromadb, silently degrading semantic deliberation search to the
SQLite LIKE fallback. WI-4561 removed the ceiling and refactored the predicate
into the testable ``_compute_has_chromadb()`` helper.

These tests fail against the pre-fix source (``_compute_has_chromadb`` does not
exist, and the inline predicate returns False on Python >= 3.14) and pass after
the fix. They also pin the two contracts the fix must preserve:

1. Availability tracks actual chromadb presence with NO Python-version ceiling.
2. Genuine import failure still degrades gracefully (predicate returns False),
   so the optional-dependency fallback to SQLite LIKE is intact.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from groundtruth_kb import db
from groundtruth_kb.db import _compute_has_chromadb

DB_SOURCE_PATH = Path(__file__).resolve().parents[2] / "groundtruth-kb" / "src" / "groundtruth_kb" / "db.py"

_CHROMADB_PRESENT = importlib.util.find_spec("chromadb") is not None


def test_no_static_version_ceiling_on_py314(monkeypatch: pytest.MonkeyPatch) -> None:
    """With chromadb present, the predicate is True even under a stubbed 3.14.

    This is the core WI-4561 regression: the removed ``sys.version_info < (3, 14)``
    clause would have made this False on Python 3.14.
    """
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(sys, "version_info", (3, 14, 0))
    assert _compute_has_chromadb() is True


def test_predicate_true_above_314(monkeypatch: pytest.MonkeyPatch) -> None:
    """No ceiling regression for future interpreters either (e.g. 3.15)."""
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(sys, "version_info", (3, 15, 0))
    assert _compute_has_chromadb() is True


def test_degrades_when_spec_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """chromadb genuinely absent -> predicate False (LIKE fallback path)."""
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
    assert _compute_has_chromadb() is False


def test_degrades_on_valueerror(monkeypatch: pytest.MonkeyPatch) -> None:
    """find_spec ValueError (e.g. namespace edge case) -> predicate False."""

    def _raise(name: str) -> object:
        raise ValueError("boom")

    monkeypatch.setattr(importlib.util, "find_spec", _raise)
    assert _compute_has_chromadb() is False


def test_degrades_on_importerror(monkeypatch: pytest.MonkeyPatch) -> None:
    """find_spec ImportError -> predicate False (graceful degradation)."""

    def _raise(name: str) -> object:
        raise ImportError("boom")

    monkeypatch.setattr(importlib.util, "find_spec", _raise)
    assert _compute_has_chromadb() is False


@pytest.mark.skipif(not _CHROMADB_PRESENT, reason="chromadb not installed in this env")
def test_module_flag_reflects_real_environment() -> None:
    """End-to-end: on the real interpreter with chromadb present, HAS_CHROMADB is True.

    On the gt venv this exercises the actual Python 3.14 path that the stale gate
    broke.
    """
    assert _compute_has_chromadb() is True
    assert db.HAS_CHROMADB is True


def test_source_has_no_static_version_ceiling() -> None:
    """Guard against reintroduction of the static Python-version ceiling."""
    source = DB_SOURCE_PATH.read_text(encoding="utf-8")
    assert "sys.version_info < (3, 14)" not in source
