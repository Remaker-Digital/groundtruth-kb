"""FAB-17 (WI-4429): ChromaDB DA read-path reliability + canonical-store config.

Spec-derived tests for gtkb-fab-17-da-chroma-read-path:
- SPEC-2098 / GOV-08 (HYG-048): search_deliberations degrades to the SQLite-LIKE
  fallback (search_method="text_match") on a crashing OR stalling chroma store,
  with no crash and no multi-minute hang.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (Area 3): the single canonical chroma index
  dirname is read from config/governance/chroma-read-path.toml.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[2] / "groundtruth-kb" / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from groundtruth_kb import db as dbmod  # noqa: E402


def _make_db(tmp_path, monkeypatch):
    # Keep insert fast and chroma-free: the real _get_chroma_collection returns
    # None when HAS_CHROMADB is False, so insert skips chroma indexing.
    monkeypatch.setattr(dbmod, "HAS_CHROMADB", False)
    kdb = dbmod.KnowledgeDB(tmp_path / "groundtruth.db")
    kdb.insert_deliberation(
        id="DELIB-FAB17-TEST-0001",
        source_type="owner_conversation",
        title="alpha beta",
        summary="alpha beta gamma",
        content="alpha beta gamma delta epsilon",
        changed_by="test",
        change_reason="fab17 read-path test fixture",
    )
    return kdb


class _CrashCollection:
    def count(self):
        raise RuntimeError("simulated chroma contention")

    def query(self, *args, **kwargs):
        raise RuntimeError("simulated chroma contention")


class _StallCollection:
    def count(self):
        return 5

    def query(self, *args, **kwargs):
        time.sleep(10)
        raise AssertionError("query should have been abandoned by the timeout")


def test_search_degrades_on_chroma_crash(tmp_path, monkeypatch):
    kdb = _make_db(tmp_path, monkeypatch)
    monkeypatch.setattr(kdb, "_get_chroma_collection", lambda: _CrashCollection())
    results = kdb.search_deliberations("alpha")
    assert results, "SQLite-LIKE fallback must still find the inserted deliberation"
    assert all(r["search_method"] == "text_match" for r in results)


def test_search_degrades_on_chroma_timeout(tmp_path, monkeypatch):
    kdb = _make_db(tmp_path, monkeypatch)
    monkeypatch.setattr(kdb, "_get_chroma_collection", lambda: _StallCollection())
    monkeypatch.setattr(dbmod, "_CHROMA_QUERY_TIMEOUT_SECONDS", 0.3)
    start = time.monotonic()
    results = kdb.search_deliberations("alpha")
    elapsed = time.monotonic() - start
    assert elapsed < 3.0, f"search hung for {elapsed:.1f}s instead of degrading"
    assert results, "SQLite-LIKE fallback must still find the inserted deliberation"
    assert all(r["search_method"] == "text_match" for r in results)


def test_call_with_timeout_returns_value():
    assert dbmod._call_with_timeout(lambda: 42, 1.0) == 42


def test_call_with_timeout_raises_on_stall():
    with pytest.raises(TimeoutError):
        dbmod._call_with_timeout(lambda: time.sleep(5), 0.2)


def test_call_with_timeout_propagates_error():
    def _boom():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        dbmod._call_with_timeout(_boom, 1.0)


def test_canonical_chroma_dirname_reads_config(tmp_path, monkeypatch):
    monkeypatch.setattr(dbmod, "HAS_CHROMADB", False)
    cfg_dir = tmp_path / "config" / "governance"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "chroma-read-path.toml").write_text(
        'schema_version = 1\n\n[chroma]\ncanonical_dirname = ".groundtruth-chroma"\n',
        encoding="utf-8",
    )
    kdb = dbmod.KnowledgeDB(tmp_path / "groundtruth.db")
    assert kdb._canonical_chroma_dirname() == ".groundtruth-chroma"


def test_canonical_chroma_dirname_defaults_when_config_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(dbmod, "HAS_CHROMADB", False)
    kdb = dbmod.KnowledgeDB(tmp_path / "groundtruth.db")
    assert kdb._canonical_chroma_dirname() == dbmod._CANONICAL_CHROMA_DIRNAME_DEFAULT
