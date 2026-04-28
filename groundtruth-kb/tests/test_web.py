"""
Tests for the GroundTruth KB web UI.

Covers: route reachability, branding parameterization, color darkening,
dynamic author filtering, and default vs custom config rendering.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.web.app import _darken_hex, _validate_hex_color, create_app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def seeded_db(tmp_path):
    """Create a temporary DB with minimal seed data for route testing."""
    db_path = tmp_path / "test.db"
    db = KnowledgeDB(db_path=db_path, check_same_thread=False)

    # Seed one spec so detail routes work
    db.insert_spec(
        id="SPEC-001",
        title="Test Specification",
        description="A spec for testing the web UI.",
        status="implemented",
        priority="P1",
        scope="core",
        section="testing",
        changed_by="test-harness",
        change_reason="seed for web tests",
    )

    # Seed a test procedure
    db.insert_test_procedure(
        id="TEST-001",
        title="Test Procedure One",
        content="Step 1: verify something.",
        type="integration",
        changed_by="test-harness",
        change_reason="seed for web tests",
    )

    # Seed an operational procedure
    db.insert_op_procedure(
        id="OP-001",
        title="Operational Procedure One",
        type="deployment",
        changed_by="test-harness",
        change_reason="seed for web tests",
    )

    yield db
    db.close()


@pytest.fixture()
def default_config(tmp_path):
    """GTConfig with all defaults (GT blue theme)."""
    return GTConfig(db_path=tmp_path / "test.db", project_root=tmp_path)


@pytest.fixture()
def custom_config(tmp_path):
    """GTConfig with custom branding (simulates Agent Red)."""
    return GTConfig(
        db_path=tmp_path / "test.db",
        project_root=tmp_path,
        app_title="My Custom Project",
        brand_mark="MC",
        brand_color="#ff3621",
        legal_footer="(c) 2026 Custom Corp. All rights reserved.",
    )


@pytest.fixture()
def default_client(seeded_db, default_config):
    """Test client with default GT branding."""
    from starlette.testclient import TestClient

    app = create_app(default_config, seeded_db)
    return TestClient(app)


@pytest.fixture()
def custom_client(seeded_db, custom_config):
    """Test client with custom branding."""
    from starlette.testclient import TestClient

    app = create_app(custom_config, seeded_db)
    return TestClient(app)


# ---------------------------------------------------------------------------
# Color utility tests
# ---------------------------------------------------------------------------


class TestDarkenHex:
    def test_darken_black(self):
        assert _darken_hex("#000000") == "#000000"

    def test_darken_white(self):
        assert _darken_hex("#ffffff", 0.5) == "#7f7f7f"

    def test_darken_brand_red(self):
        result = _darken_hex("#ff3621", 0.8)
        assert result.startswith("#")
        assert len(result) == 7
        # Red channel: 0xff * 0.8 = 204 = 0xcc
        assert result == "#cc2b1a"

    def test_darken_default_blue(self):
        result = _darken_hex("#2563eb", 0.8)
        assert result.startswith("#")
        assert len(result) == 7

    def test_no_darkening(self):
        assert _darken_hex("#abcdef", 1.0) == "#abcdef"

    def test_strips_hash(self):
        assert _darken_hex("ff0000", 0.5) == "#7f0000"


# ---------------------------------------------------------------------------
# Route reachability tests — default branding
# ---------------------------------------------------------------------------


class TestRouteReachability:
    """Every route must return 200 (or 200 with content)."""

    def test_dashboard(self, default_client):
        resp = default_client.get("/")
        assert resp.status_code == 200
        assert "Dashboard" in resp.text

    def test_specs_list(self, default_client):
        resp = default_client.get("/specs")
        assert resp.status_code == 200
        assert "Specifications" in resp.text

    def test_spec_detail(self, default_client):
        resp = default_client.get("/specs/SPEC-001")
        assert resp.status_code == 200
        assert "Test Specification" in resp.text

    def test_spec_not_found(self, default_client):
        resp = default_client.get("/specs/NONEXISTENT")
        assert resp.status_code == 404

    def test_tests_list(self, default_client):
        resp = default_client.get("/tests")
        assert resp.status_code == 200
        assert "Test Procedures" in resp.text

    def test_test_detail(self, default_client):
        resp = default_client.get("/tests/TEST-001")
        assert resp.status_code == 200
        assert "Test Procedure One" in resp.text

    def test_test_not_found(self, default_client):
        resp = default_client.get("/tests/NONEXISTENT")
        assert resp.status_code == 404

    def test_ops_list(self, default_client):
        resp = default_client.get("/ops")
        assert resp.status_code == 200
        assert "Operational Procedures" in resp.text

    def test_op_detail(self, default_client):
        resp = default_client.get("/ops/OP-001")
        assert resp.status_code == 200
        assert "Operational Procedure One" in resp.text

    def test_op_not_found(self, default_client):
        resp = default_client.get("/ops/NONEXISTENT")
        assert resp.status_code == 404

    def test_env_list(self, default_client):
        resp = default_client.get("/env")
        assert resp.status_code == 200
        assert "Environment Config" in resp.text

    def test_history(self, default_client):
        resp = default_client.get("/history")
        assert resp.status_code == 200
        assert "Change History" in resp.text

    def test_assertions(self, default_client):
        resp = default_client.get("/assertions")
        assert resp.status_code == 200
        assert "Assertion Results" in resp.text


# ---------------------------------------------------------------------------
# Branding parameterization tests
# ---------------------------------------------------------------------------


class TestDefaultBranding:
    """Default GT branding appears when no custom config is provided."""

    def test_title_contains_gt(self, default_client):
        resp = default_client.get("/")
        assert "GroundTruth KB" in resp.text

    def test_brand_mark_gt(self, default_client):
        resp = default_client.get("/")
        # The brand mark "GT" should appear inside the brand-mark span
        assert ">GT<" in resp.text

    def test_default_blue_color(self, default_client):
        resp = default_client.get("/")
        assert "#2563eb" in resp.text

    def test_no_legal_footer_by_default(self, default_client):
        resp = default_client.get("/")
        assert "legal-footer" not in resp.text


class TestCustomBranding:
    """Custom branding from config appears in rendered HTML."""

    def test_custom_title(self, custom_client):
        resp = custom_client.get("/")
        assert "My Custom Project" in resp.text

    def test_custom_brand_mark(self, custom_client):
        resp = custom_client.get("/")
        assert ">MC<" in resp.text

    def test_custom_brand_color(self, custom_client):
        resp = custom_client.get("/")
        assert "#ff3621" in resp.text

    def test_custom_brand_color_dark(self, custom_client):
        resp = custom_client.get("/")
        # Darkened #ff3621 at 0.8 = #cc2b1a
        assert "#cc2b1a" in resp.text

    def test_legal_footer_rendered(self, custom_client):
        resp = custom_client.get("/")
        assert "Custom Corp" in resp.text
        assert "legal-footer" in resp.text

    def test_branding_on_every_page(self, custom_client):
        """Brand mark should appear on all pages (via base.html)."""
        for path in ["/", "/specs", "/tests", "/ops", "/env", "/history", "/assertions"]:
            resp = custom_client.get(path)
            assert ">MC<" in resp.text, f"Brand mark missing on {path}"


# ---------------------------------------------------------------------------
# Dynamic content tests
# ---------------------------------------------------------------------------


class TestDynamicContent:
    """Verify dynamic author dropdown and filter behavior."""

    def test_history_has_dynamic_authors(self, default_client):
        resp = default_client.get("/history")
        # The seed data was inserted by "test-harness"
        assert "test-harness" in resp.text

    def test_specs_filter_by_status(self, default_client):
        resp = default_client.get("/specs?status=implemented")
        assert resp.status_code == 200
        assert "SPEC-001" in resp.text

    def test_specs_filter_empty(self, default_client):
        resp = default_client.get("/specs?status=retired")
        assert resp.status_code == 200
        # Should not contain our test spec
        assert "SPEC-001" not in resp.text

    def test_dashboard_shows_counts(self, default_client):
        resp = default_client.get("/")
        # Should show at least 1 spec in summary
        assert "Total Specs" in resp.text

    def test_assertions_empty_state(self, default_client):
        resp = default_client.get("/assertions")
        # No assertion runs in seed data
        assert "gt assert" in resp.text

    def test_history_filter_by_author(self, default_client):
        resp = default_client.get("/history?changed_by=test-harness")
        assert resp.status_code == 200
        assert "test-harness" in resp.text

    def test_static_css_served(self, default_client):
        resp = default_client.get("/static/style.css")
        assert resp.status_code == 200
        assert "--brand:" in resp.text


# ---------------------------------------------------------------------------
# Color validation tests (Codex follow-up)
# ---------------------------------------------------------------------------


class TestColorValidation:
    """Validate hex color handling for malformed inputs."""

    def test_valid_hex_passthrough(self):
        assert _validate_hex_color("#ff3621") == "#ff3621"

    def test_valid_hex_without_hash(self):
        assert _validate_hex_color("2563eb") == "#2563eb"

    def test_invalid_hex_returns_default(self):
        assert _validate_hex_color("not-a-color") == "#2563eb"

    def test_empty_string_returns_default(self):
        assert _validate_hex_color("") == "#2563eb"

    def test_short_hex_returns_default(self):
        assert _validate_hex_color("#fff") == "#2563eb"

    def test_invalid_chars_returns_default(self):
        assert _validate_hex_color("#gg0000") == "#2563eb"

    def test_darken_invalid_color_uses_default(self):
        result = _darken_hex("garbage")
        # Should darken the default blue, not crash
        assert result.startswith("#")
        assert len(result) == 7


# ---------------------------------------------------------------------------
# Edge case branding tests (Codex follow-up)
# ---------------------------------------------------------------------------


class TestBrandingEdgeCases:
    """Edge cases identified by Codex advisory review."""

    def test_empty_brand_mark_falls_back_to_gt(self, seeded_db, tmp_path):
        from starlette.testclient import TestClient

        config = GTConfig(
            db_path=tmp_path / "test.db",
            project_root=tmp_path,
            brand_mark="",
        )
        client = TestClient(create_app(config, seeded_db))
        resp = client.get("/")
        assert resp.status_code == 200
        assert ">GT<" in resp.text

    def test_invalid_brand_color_uses_default(self, seeded_db, tmp_path):
        from starlette.testclient import TestClient

        config = GTConfig(
            db_path=tmp_path / "test.db",
            project_root=tmp_path,
            brand_color="not-valid",
        )
        client = TestClient(create_app(config, seeded_db))
        resp = client.get("/")
        assert resp.status_code == 200
        assert "#2563eb" in resp.text

    def test_logo_url_renders_img_tag(self, seeded_db, tmp_path):
        from starlette.testclient import TestClient

        config = GTConfig(
            db_path=tmp_path / "test.db",
            project_root=tmp_path,
            logo_url="/static/logo.png",
        )
        client = TestClient(create_app(config, seeded_db))
        resp = client.get("/")
        assert resp.status_code == 200
        assert 'src="/static/logo.png"' in resp.text
        assert "brand-logo" in resp.text

    def test_long_legal_footer_renders(self, seeded_db, tmp_path):
        from starlette.testclient import TestClient

        long_footer = "(c) 2026 " + "A" * 200 + ". All rights reserved."
        config = GTConfig(
            db_path=tmp_path / "test.db",
            project_root=tmp_path,
            legal_footer=long_footer,
        )
        client = TestClient(create_app(config, seeded_db))
        resp = client.get("/")
        assert resp.status_code == 200
        assert "AAAA" in resp.text
        assert "legal-footer" in resp.text
