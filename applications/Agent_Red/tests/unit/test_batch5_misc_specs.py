"""
Unit tests for miscellaneous Batch 5 specs.

Tests for WI 115, 201, 204, 297 — implementation verification tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

# Project root
ROOT = Path(__file__).resolve().parents[2]


class TestCustomerProfileUI:
    """WI 115: Customer profile viewer UI."""

    def test_customer_profile_api_module_exists(self) -> None:
        """The admin customer profile API module should exist."""
        module_path = ROOT / "src" / "multi_tenant" / "admin_customer_profile_api.py"
        assert module_path.exists(), \
            f"Customer profile API module should exist at {module_path}"

    def test_customer_profile_has_router(self) -> None:
        """The customer profile API module should define an APIRouter."""
        module_path = ROOT / "src" / "multi_tenant" / "admin_customer_profile_api.py"
        content = module_path.read_text(encoding="utf-8")
        assert "APIRouter" in content, \
            "Customer profile API should import APIRouter from FastAPI"
        assert "router = APIRouter(" in content, \
            "Customer profile API should instantiate a router"

    def test_customer_profile_router_prefix(self) -> None:
        """The customer profile router should be mounted on /api/admin/profiles."""
        module_path = ROOT / "src" / "multi_tenant" / "admin_customer_profile_api.py"
        content = module_path.read_text(encoding="utf-8")
        assert "/api/admin/profiles" in content, \
            "Customer profile router should use /api/admin/profiles prefix"

    def test_customer_profile_has_list_endpoint(self) -> None:
        """The customer profile API should have a GET list endpoint."""
        module_path = ROOT / "src" / "multi_tenant" / "admin_customer_profile_api.py"
        content = module_path.read_text(encoding="utf-8")
        assert "@router.get(" in content, \
            "Customer profile API should define at least one GET endpoint"

    def test_customer_profile_has_delete_endpoint(self) -> None:
        """The customer profile API should have a DELETE endpoint (GDPR)."""
        module_path = ROOT / "src" / "multi_tenant" / "admin_customer_profile_api.py"
        content = module_path.read_text(encoding="utf-8")
        assert "@router.delete(" in content, \
            "Customer profile API should define a DELETE endpoint for GDPR"


class TestSeedKnowledgeBase:
    """WI 201: Seed knowledge base with Agent Red product data."""

    def test_seed_script_exists(self) -> None:
        """The seed script should exist."""
        seed_path = ROOT / "scripts" / "seed_tenant.py"
        assert seed_path.exists(), \
            f"Seed script should exist at {seed_path}"

    def test_seed_script_has_kb_phase(self) -> None:
        """The seed script should include a knowledge base seeding phase."""
        seed_path = ROOT / "scripts" / "seed_tenant.py"
        content = seed_path.read_text(encoding="utf-8")
        assert "phase_5_knowledge_base" in content, \
            "Seed script should define phase_5_knowledge_base function"

    def test_seed_script_imports_kb_module(self) -> None:
        """The seed script should reference the seed_knowledge_base module."""
        seed_path = ROOT / "scripts" / "seed_tenant.py"
        content = seed_path.read_text(encoding="utf-8")
        assert "seed_knowledge_base" in content, \
            "Seed script should reference the seed_knowledge_base module"

    def test_seed_script_loads_articles(self) -> None:
        """The seed script should load KB articles to Cosmos."""
        seed_path = ROOT / "scripts" / "seed_tenant.py"
        content = seed_path.read_text(encoding="utf-8")
        assert "load_to_cosmos" in content, \
            "Seed script should call load_to_cosmos for KB article seeding"

    def test_seed_script_tracks_article_count(self) -> None:
        """The seed script should reference TOTAL_ARTICLES for reporting."""
        seed_path = ROOT / "scripts" / "seed_tenant.py"
        content = seed_path.read_text(encoding="utf-8")
        assert "TOTAL_ARTICLES" in content, \
            "Seed script should reference TOTAL_ARTICLES constant"


_branding_dir = ROOT / "branding" / "logo"


@pytest.mark.skipif(
    not _branding_dir.is_dir(),
    reason="branding/ not present (container environment)",
)
class TestFavicon:
    """WI 204: Favicon and app icons from icon-master.png."""

    def test_icon_master_source_exists(self) -> None:
        """The icon-master.png source file should exist in branding."""
        icon_path = _branding_dir / "PNG" / "icon-master.png"
        assert icon_path.exists(), \
            f"icon-master.png should exist at {icon_path}"

    def test_icon_master_svg_exists(self) -> None:
        """The icon-master.svg source file should exist in branding."""
        svg_path = _branding_dir / "SVG" / "icon-master.svg"
        assert svg_path.exists(), \
            f"icon-master.svg should exist at {svg_path}"

    def test_admin_has_favicon_files(self) -> None:
        """The admin standalone dist should have favicon PNG files."""
        favicon_paths = [
            ROOT / "admin" / "standalone" / "dist" / "favicon-32x32.png",
            ROOT / "admin" / "standalone" / "dist" / "favicon-16x16.png",
        ]
        for fp in favicon_paths:
            assert fp.exists(), f"Favicon file should exist at {fp}"

    def test_admin_has_pwa_icons(self) -> None:
        """The admin standalone dist should have PWA icon files."""
        icon_paths = [
            ROOT / "admin" / "standalone" / "dist" / "icon-192x192.png",
            ROOT / "admin" / "standalone" / "dist" / "icon-512x512.png",
        ]
        for ip in icon_paths:
            assert ip.exists(), f"PWA icon file should exist at {ip}"

    def test_admin_has_icon_master_svg_in_dist(self) -> None:
        """The admin standalone dist should include icon-master.svg."""
        svg_path = ROOT / "admin" / "standalone" / "dist" / "icon-master.svg"
        assert svg_path.exists(), \
            f"icon-master.svg should be copied to admin dist at {svg_path}"


class TestMaxTurnsMin:
    """WI 297: Enforce min=1 for max_turns on server."""

    @pytest.fixture()
    def fields_data(self) -> list[dict]:
        """Load and return the fields list from fields.yaml."""
        fields_path = ROOT / "src" / "multi_tenant" / "schema" / "fields.yaml"
        assert fields_path.exists(), f"fields.yaml should exist at {fields_path}"
        with open(fields_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("fields", [])

    def _find_max_turns_field(self, fields: list[dict]) -> dict | None:
        """Locate the max_ai_turns_before_escalation field definition."""
        for field in fields:
            if field.get("field_name") == "max_ai_turns_before_escalation":
                return field
        return None

    def test_fields_yaml_exists(self) -> None:
        """fields.yaml should exist at the expected schema path."""
        fields_path = ROOT / "src" / "multi_tenant" / "schema" / "fields.yaml"
        assert fields_path.exists(), f"fields.yaml should exist at {fields_path}"

    def test_max_turns_field_defined(self, fields_data: list[dict]) -> None:
        """fields.yaml should define the max_ai_turns_before_escalation field."""
        field = self._find_max_turns_field(fields_data)
        assert field is not None, \
            "fields.yaml should define max_ai_turns_before_escalation field"

    def test_max_turns_has_min_value(self, fields_data: list[dict]) -> None:
        """max_ai_turns_before_escalation should have a validation min_value."""
        field = self._find_max_turns_field(fields_data)
        assert field is not None, "Field not found"
        validation = field.get("validation", {})
        assert "min_value" in validation, \
            "max_ai_turns_before_escalation should have validation.min_value"

    def test_max_turns_min_value_is_at_least_one(self, fields_data: list[dict]) -> None:
        """max_ai_turns_before_escalation min_value should be >= 1.0."""
        field = self._find_max_turns_field(fields_data)
        assert field is not None, "Field not found"
        min_val = field["validation"]["min_value"]
        assert float(min_val) >= 1.0, \
            f"min_value should be >= 1.0, got {min_val}"

    def test_max_turns_is_integer_type(self, fields_data: list[dict]) -> None:
        """max_ai_turns_before_escalation should be an integer field."""
        field = self._find_max_turns_field(fields_data)
        assert field is not None, "Field not found"
        assert field.get("field_type") == "integer", \
            f"max_ai_turns field_type should be 'integer', got {field.get('field_type')}"

    def test_max_turns_has_max_value(self, fields_data: list[dict]) -> None:
        """max_ai_turns_before_escalation should have a max_value cap."""
        field = self._find_max_turns_field(fields_data)
        assert field is not None, "Field not found"
        validation = field.get("validation", {})
        assert "max_value" in validation, \
            "max_ai_turns_before_escalation should have validation.max_value"
        assert float(validation["max_value"]) > 1.0, \
            "max_value should be greater than 1.0"
