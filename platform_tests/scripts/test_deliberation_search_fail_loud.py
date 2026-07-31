"""Spec-derived tests for WI-4563 deliberation-search fail-loud behavior."""

from __future__ import annotations

import sys
from pathlib import Path

from click.testing import CliRunner

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

import groundtruth_kb.db as db_mod  # noqa: E402
from groundtruth_kb.bridge.prior_deliberations import pre_populate_prior_deliberations  # noqa: E402
from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.db import DeliberationSearchDegradedError, KnowledgeDB  # noqa: E402


def test_required_semantic_search_raises_before_like_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(db_mod, "HAS_CHROMADB", True)
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db", chroma_path=tmp_path / "chroma")
    monkeypatch.setattr(db, "_get_chroma_collection", lambda: None)

    try:
        db.search_deliberations("governance topic", require_semantic=True)
    except DeliberationSearchDegradedError as exc:
        assert exc.status["semantic_degraded"] is True
        assert exc.status["degradation_reason"] == "collection_unavailable"
    else:  # pragma: no cover - assertion branch
        raise AssertionError("required semantic search returned fallback rows")


def test_default_search_still_returns_like_rows_with_degradation_status(monkeypatch, tmp_path):
    monkeypatch.setattr(db_mod, "HAS_CHROMADB", True)
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db", chroma_path=tmp_path / "chroma")
    monkeypatch.setattr(db, "_get_chroma_collection", lambda: None)
    db.insert_deliberation(
        id="DELIB-WI4563-LIKE",
        source_type="report",
        title="Governance topic",
        summary="Search fallback visibility.",
        content="The governance topic remains findable by explicit text fallback.",
        changed_by="test",
        change_reason="WI-4563 fixture",
    )

    rows = db.search_deliberations("governance topic")
    status = db._deliberation_search_status()

    assert rows[0]["id"] == "DELIB-WI4563-LIKE"
    assert rows[0]["search_method"] == "text_match"
    assert status["semantic_degraded"] is True
    assert status["degradation_reason"] == "collection_unavailable"


def test_cli_semantic_only_exits_loudly(monkeypatch):
    class FakeDB:
        def __init__(self, **_kwargs):
            pass

        def search_deliberations(self, _query, *, limit=5, require_semantic=False):  # noqa: ARG002
            raise DeliberationSearchDegradedError(
                "semantic degraded",
                status={
                    "semantic_degraded": True,
                    "degradation_reason": "chromadb_unavailable",
                },
            )

    monkeypatch.setattr("groundtruth_kb.cli.KnowledgeDB", FakeDB)

    result = CliRunner().invoke(main, ["deliberations", "search", "topic", "--semantic-only"])

    assert result.exit_code == 1
    assert "reason: chromadb_unavailable" in result.output


def test_prior_deliberation_prepopulation_records_degradation(tmp_path):
    class FailingDB:
        def search_deliberations(self, _query, *, limit=5, require_semantic=False):  # noqa: ARG002
            raise DeliberationSearchDegradedError(
                "semantic degraded",
                status={
                    "semantic_degraded": True,
                    "degradation_reason": "timeout",
                },
            )

    body = "# Proposal\n\n## Prior Deliberations\n\n"

    rendered = pre_populate_prior_deliberations(
        "watchdog-search",
        body,
        db=FailingDB(),
        glossary_path=tmp_path / "missing-glossary.md",
        log_path=False,
    )

    assert "Deliberation semantic search degraded (timeout)" in rendered
    assert "do not treat this section as an authoritative empty search result" in rendered
