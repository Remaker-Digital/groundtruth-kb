"""
Tests verifying the Agent Red migration shim renders correctly.

Simulates the AR groundtruth.toml configuration and confirms that AR branding
(red color, "AR" mark, copyright footer, title) renders through the extracted
groundtruth-kb web package.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.web import create_app


@pytest.fixture()
def ar_config(tmp_path: Path) -> GTConfig:
    """GTConfig matching the Agent Red groundtruth.toml."""
    return GTConfig(
        db_path=tmp_path / "ar-test.db",
        project_root=tmp_path,
        app_title="Agent Red Knowledge DB",
        brand_mark="AR",
        brand_color="#ff3621",
        legal_footer="(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.",
    )


@pytest.fixture()
def ar_client(ar_config: GTConfig) -> TestClient:
    db = KnowledgeDB(db_path=ar_config.db_path, check_same_thread=False)
    db.insert_spec(
        id="SPEC-0001",
        title="Governance Spec",
        description="Test",
        status="verified",
        priority="P0",
        scope="governance",
        section="core",
        changed_by="seed",
        change_reason="shim test seed",
    )
    app = create_app(ar_config, db)
    client = TestClient(app)
    yield client
    db.close()


class TestARBranding:
    """AR branding must render identically through the extracted package."""

    def test_title_shows_agent_red(self, ar_client: TestClient):
        resp = ar_client.get("/")
        assert "Agent Red Knowledge DB" in resp.text

    def test_brand_mark_ar(self, ar_client: TestClient):
        resp = ar_client.get("/")
        assert ">AR<" in resp.text

    def test_brand_color_red(self, ar_client: TestClient):
        resp = ar_client.get("/")
        assert "#ff3621" in resp.text

    def test_brand_color_dark_red(self, ar_client: TestClient):
        resp = ar_client.get("/")
        # Darkened #ff3621 at 0.8 = #cc2b1a
        assert "#cc2b1a" in resp.text

    def test_legal_footer_remaker(self, ar_client: TestClient):
        resp = ar_client.get("/")
        assert "Remaker Digital" in resp.text
        assert "legal-footer" in resp.text

    def test_spec_detail_renders(self, ar_client: TestClient):
        resp = ar_client.get("/specs/SPEC-0001")
        assert resp.status_code == 200
        assert "Governance Spec" in resp.text
        assert ">AR<" in resp.text

    def test_all_routes_have_ar_mark(self, ar_client: TestClient):
        for path in ["/", "/specs", "/tests", "/ops", "/env", "/history", "/assertions"]:
            resp = ar_client.get(path)
            assert resp.status_code == 200
            assert ">AR<" in resp.text, f"AR brand mark missing on {path}"


class TestARConfigFromToml:
    """Verify GTConfig.load() correctly reads AR-style TOML values."""

    def test_load_ar_toml(self, tmp_path: Path):
        toml_content = """\
[groundtruth]
db_path = "./knowledge.db"
project_root = "../.."
app_title = "Agent Red Knowledge DB"
brand_mark = "AR"
brand_color = "#ff3621"
legal_footer = "(c) 2026 Remaker Digital"
"""
        toml_path = tmp_path / "groundtruth.toml"
        toml_path.write_text(toml_content, encoding="utf-8")

        config = GTConfig.load(config_path=toml_path)
        assert config.app_title == "Agent Red Knowledge DB"
        assert config.brand_mark == "AR"
        assert config.brand_color == "#ff3621"
        assert "Remaker Digital" in config.legal_footer
        # Paths should be anchored to the TOML directory
        assert config.db_path == tmp_path / "knowledge.db"
