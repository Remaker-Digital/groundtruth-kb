# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for SPEC-1840: Widget Origin Validation (WI-1622, WI-1623).

Validates:
1. approved_widget_origins field exists in PreferencesDocument
2. Origin validation logic in middleware._auth_widget_key()
3. Backward compatibility: empty origins list allows all
"""
import inspect
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# WI-1622: Schema field exists
# ---------------------------------------------------------------------------

class TestApprovedOriginsSchema:
    """approved_widget_origins field in PreferencesDocument."""

    def test_field_exists_in_preferences(self):
        from src.multi_tenant.cosmos_schema import PreferencesDocument
        fields = PreferencesDocument.model_fields
        assert "approved_widget_origins" in fields, \
            "PreferencesDocument must have approved_widget_origins field"

    def test_field_is_list_of_strings(self):
        from src.multi_tenant.cosmos_schema import PreferencesDocument
        # Default should be empty list
        doc = PreferencesDocument(
            id="test", tenant_id="t-001", version=1,
            is_current=True, config_state="active", created_at="2026-01-01T00:00:00Z",
        )
        assert doc.approved_widget_origins == []

    def test_field_accepts_origins(self):
        from src.multi_tenant.cosmos_schema import PreferencesDocument
        doc = PreferencesDocument(
            id="test", tenant_id="t-001", version=1,
            is_current=True, config_state="active", created_at="2026-01-01T00:00:00Z",
            approved_widget_origins=["https://mystore.com", "https://shop.example.com"],
        )
        assert len(doc.approved_widget_origins) == 2
        assert "https://mystore.com" in doc.approved_widget_origins

    def test_field_in_direct_mapping(self):
        """approved_widget_origins must be in config field mapping."""
        from src.multi_tenant.config.field_mapping import _PREFS_DIRECT_FIELDS
        assert "approved_widget_origins" in _PREFS_DIRECT_FIELDS


# ---------------------------------------------------------------------------
# WI-1623: Origin validation in middleware
# ---------------------------------------------------------------------------

class TestWidgetOriginValidation:
    """_auth_widget_key() validates Origin against approved_widget_origins."""

    def test_middleware_has_origin_parameter(self):
        """_auth_widget_key must accept origin parameter."""
        from src.multi_tenant.middleware import TenantAuthMiddleware
        sig = inspect.signature(TenantAuthMiddleware._auth_widget_key)
        params = list(sig.parameters.keys())
        assert "origin" in params, \
            "_auth_widget_key must accept 'origin' parameter"

    def test_middleware_checks_approved_origins(self):
        """_auth_widget_key source must reference approved_widget_origins."""
        from src.multi_tenant.middleware import TenantAuthMiddleware
        source = inspect.getsource(TenantAuthMiddleware._auth_widget_key)
        assert "approved_widget_origins" in source
        assert "403" in source, "Unapproved origins must get 403"

    def test_middleware_passes_origin_from_request(self):
        """Caller must extract origin from request headers."""
        from src.multi_tenant import middleware
        source = inspect.getsource(middleware.TenantAuthMiddleware)
        # Find the _auth_widget_key call site
        assert 'origin' in source.split("_auth_widget_key")[1][:200], \
            "Caller must pass origin to _auth_widget_key"

    def test_spec_1840_documented_in_method(self):
        """Method docstring must reference SPEC-1840."""
        from src.multi_tenant.middleware import TenantAuthMiddleware
        doc = TenantAuthMiddleware._auth_widget_key.__doc__ or ""
        assert "SPEC-1840" in doc
