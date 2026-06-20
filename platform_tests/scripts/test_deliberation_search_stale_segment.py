"""WI-4568: stale Chroma segment fast-fail and semantic-only fail-closed."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from click.testing import CliRunner

_SRC = Path(__file__).resolve().parents[2] / "groundtruth-kb" / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from groundtruth_kb import db as dbmod  # noqa: E402
from groundtruth_kb.cli import main  # noqa: E402


def _make_db(tmp_path: Path, monkeypatch, delib_id: str = "DELIB-STALE-0001") -> dbmod.KnowledgeDB:
    monkeypatch.setattr(dbmod, "HAS_CHROMADB", False)
    kdb = dbmod.KnowledgeDB(tmp_path / "groundtruth.db")
    kdb.insert_deliberation(
        id=delib_id,
        source_type="owner_conversation",
        title=f"{delib_id} staleprobe",
        summary="Fixture deliberation for staleprobe semantic search tests.",
        content="staleprobe transientprobe zeroprobe",
        changed_by="test",
        change_reason="WI-4568 stale segment search fixture",
    )
    monkeypatch.setattr(dbmod, "HAS_CHROMADB", True)
    return kdb


class _StaleSegmentCollection:
    def __init__(self) -> None:
        self.query_calls = 0

    def count(self) -> int:
        return 1

    def query(self, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        self.query_calls += 1
        raise RuntimeError("Failed to apply logs to the hnsw segment writer: Error querying knn")


class _TransientThenSuccessCollection:
    def __init__(self, delib_id: str) -> None:
        self.delib_id = delib_id
        self.query_calls = 0

    def count(self) -> int:
        return 1

    def query(self, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        self.query_calls += 1
        if self.query_calls == 1:
            raise RuntimeError("temporary grpc unavailable")
        return {
            "ids": [[f"{self.delib_id}::0"]],
            "distances": [[0.2]],
            "documents": [["semantic chunk"]],
            "metadatas": [[{"delib_id": self.delib_id}]],
        }


class _EmptyCollection:
    def count(self) -> int:
        return 0

    def query(self, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        raise AssertionError("query should not run when count is zero")


def test_stale_segment_error_fast_fails_without_retry(tmp_path: Path, monkeypatch) -> None:
    kdb = _make_db(tmp_path, monkeypatch)
    collection = _StaleSegmentCollection()
    monkeypatch.setattr(dbmod, "_CHROMA_QUERY_RETRIES", 4)
    monkeypatch.setattr(kdb, "_get_chroma_collection", lambda: collection)

    results = kdb.search_deliberations("staleprobe", limit=5)
    status = kdb._deliberation_search_status()

    assert collection.query_calls == 1
    assert results
    assert all(row["search_method"] == "text_match" for row in results)
    assert status["semantic_degraded"] is True
    assert status["degradation_reason"] == "stale_segment"


def test_transient_chroma_error_still_retries(tmp_path: Path, monkeypatch) -> None:
    kdb = _make_db(tmp_path, monkeypatch, delib_id="DELIB-TRANSIENT-0001")
    collection = _TransientThenSuccessCollection("DELIB-TRANSIENT-0001")
    monkeypatch.setattr(dbmod, "_CHROMA_QUERY_RETRIES", 1)
    monkeypatch.setattr(kdb, "_get_chroma_collection", lambda: collection)

    results = kdb.search_deliberations("transientprobe", limit=5)
    status = kdb._deliberation_search_status()

    assert collection.query_calls == 2
    assert results[0]["id"] == "DELIB-TRANSIENT-0001"
    assert results[0]["search_method"] == "semantic"
    assert status["semantic_succeeded"] is True
    assert status["semantic_degraded"] is False


def test_successful_empty_semantic_pass_is_not_degraded(tmp_path: Path, monkeypatch) -> None:
    kdb = _make_db(tmp_path, monkeypatch)
    monkeypatch.setattr(kdb, "_get_chroma_collection", lambda: _EmptyCollection())

    results = kdb.search_deliberations("missing-token", limit=5)
    status = kdb._deliberation_search_status()

    assert results == []
    assert status["semantic_succeeded"] is True
    assert status["semantic_degraded"] is False


def test_semantic_only_fails_closed_when_semantic_pass_degrades(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\napp_title = "test"\ndb_path = "./groundtruth.db"\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(dbmod, "HAS_CHROMADB", True)

    def _fake_search(self: dbmod.KnowledgeDB, _query: str, *, limit: int = 5) -> list[dict[str, Any]]:  # noqa: ARG001
        self._last_deliberation_search_status = {
            "semantic_expected": True,
            "semantic_attempted": True,
            "semantic_succeeded": False,
            "semantic_degraded": True,
            "degradation_reason": "stale_segment",
        }
        return [
            {
                "id": "DELIB-TEXT-ONLY",
                "version": 1,
                "title": "text-only fallback",
                "summary": "fallback row",
                "content": "fallback row",
                "search_method": "text_match",
                "score": None,
            }
        ]

    monkeypatch.setattr(dbmod.KnowledgeDB, "search_deliberations", _fake_search)
    result = CliRunner().invoke(
        main,
        ["--config", str(config), "deliberations", "search", "staleprobe", "--semantic-only"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "semantic search" in result.output
    assert "stale_segment" in result.output
    assert "DELIB-TEXT-ONLY" not in result.output
