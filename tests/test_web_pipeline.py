"""Tests for the /pipeline dashboard route.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.web.app import create_app


@pytest.fixture()
def empty_db(tmp_path: Path) -> KnowledgeDB:
    """Empty KnowledgeDB for testing N/A states."""
    return KnowledgeDB(db_path=tmp_path / "empty.db", check_same_thread=False)


@pytest.fixture()
def seeded_db(tmp_path: Path) -> KnowledgeDB:
    """KnowledgeDB with data for testing metric rendering."""
    db = KnowledgeDB(db_path=tmp_path / "seeded.db", check_same_thread=False)
    # Seed specs at different statuses
    db.insert_spec(
        id="SPEC-001",
        title="Implemented spec",
        description="Has tests.",
        status="implemented",
        priority="P1",
        scope="core",
        section="testing",
        changed_by="test",
        change_reason="seed",
    )
    db.insert_spec(
        id="SPEC-002",
        title="Verified spec",
        description="Verified with tests.",
        status="verified",
        priority="P1",
        scope="core",
        section="testing",
        changed_by="test",
        change_reason="seed",
    )
    # Seed a test procedure linked to SPEC-002
    db.insert_test_procedure(
        id="TEST-001",
        title="Linked test",
        content="Verify SPEC-002.",
        type="integration",
        changed_by="test",
        change_reason="seed",
    )
    return db


@pytest.fixture()
def config(tmp_path: Path) -> GTConfig:
    return GTConfig(db_path=tmp_path / "test.db", project_root=tmp_path)


@pytest.fixture()
def empty_client(empty_db, config):
    from starlette.testclient import TestClient

    return TestClient(create_app(config, empty_db))


@pytest.fixture()
def seeded_client(seeded_db, config):
    from starlette.testclient import TestClient

    return TestClient(create_app(config, seeded_db))


class TestPipelineRoute:
    """Test /pipeline route returns 200 and renders metrics."""

    def test_pipeline_returns_200(self, seeded_client):
        response = seeded_client.get("/pipeline")
        assert response.status_code == 200

    def test_pipeline_contains_metric_ids(self, seeded_client):
        response = seeded_client.get("/pipeline")
        html = response.text
        for metric_id in ["M2", "M4", "M6", "M10", "M11", "M12", "M16", "M17", "M18"]:
            assert metric_id in html, f"Metric {metric_id} not found in pipeline page"

    def test_pipeline_contains_group_titles(self, seeded_client):
        response = seeded_client.get("/pipeline")
        html = response.text
        assert "Throughput" in html
        assert "Quality" in html
        assert "Coverage" in html
        assert "Lifecycle" in html

    def test_pipeline_nav_link_present(self, seeded_client):
        response = seeded_client.get("/pipeline")
        assert 'href="/pipeline"' in response.text

    def test_pipeline_shows_summary_cards(self, seeded_client):
        response = seeded_client.get("/pipeline")
        html = response.text
        assert "Total Specs" in html
        assert "Test Procedures" in html
        assert "Work Items" in html


class TestPipelineEmptyDB:
    """Test /pipeline with empty database shows N/A values."""

    def test_empty_db_returns_200(self, empty_client):
        response = empty_client.get("/pipeline")
        assert response.status_code == 200

    def test_empty_db_shows_na(self, empty_client):
        response = empty_client.get("/pipeline")
        assert "N/A" in response.text

    def test_empty_db_has_neutral_health_dots(self, empty_client):
        response = empty_client.get("/pipeline")
        assert "health-na" in response.text


class TestPipelineM18Drilldown:
    """Test M18 spec-without-tests drilldown rendering."""

    def test_m18_links_to_affected_spec(self, seeded_client):
        """SPEC-001 is implemented with no linked tests — must appear as drilldown link."""
        response = seeded_client.get("/pipeline")
        html = response.text
        assert 'href="/specs/SPEC-001"' in html, "M18 drilldown must link to affected spec"

    def test_m18_truncation_notice(self, tmp_path):
        """When >20 specs lack tests, drilldown shows omitted count."""
        from starlette.testclient import TestClient

        db = KnowledgeDB(db_path=tmp_path / "m18_trunc.db", check_same_thread=False)
        # Seed 22 implemented specs with no linked tests
        for i in range(22):
            db.insert_spec(
                id=f"SPEC-{i:04d}",
                title=f"Untested spec {i}",
                description="No tests linked.",
                status="implemented",
                priority="P2",
                scope="core",
                section="testing",
                changed_by="test",
                change_reason="seed",
            )
        config = GTConfig(db_path=tmp_path / "m18_trunc.db", project_root=tmp_path)
        client = TestClient(create_app(config, db))
        response = client.get("/pipeline")
        html = response.text
        # Should show 20 links + "and 2 more" notice
        assert "and 2 more" in html, "M18 must show omitted count when >20 affected specs"
        # Should contain at least some spec links
        assert 'href="/specs/SPEC-' in html
