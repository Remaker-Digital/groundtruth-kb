"""Tests for API versioning constants.

Covers:
    - API_VERSION constant exists and equals "1.0.0"
    - PRODUCT_VERSION constant exists and equals "1.66.0"

Note: These are trivial constant checks. The ApiVersionMiddleware itself
is tested elsewhere via integration tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from src.multi_tenant.api_versioning import API_VERSION, PRODUCT_VERSION


# ---------------------------------------------------------------------------
# VER-01: API_VERSION constant
# ---------------------------------------------------------------------------


class TestApiVersionConstant:
    """Verify API_VERSION is defined correctly."""

    def test_api_version_exists(self):
        assert API_VERSION is not None

    def test_api_version_value(self):
        assert API_VERSION == "1.0.0"

    def test_api_version_is_string(self):
        assert isinstance(API_VERSION, str)


# ---------------------------------------------------------------------------
# VER-02: PRODUCT_VERSION constant
# ---------------------------------------------------------------------------


class TestProductVersionConstant:
    """Verify PRODUCT_VERSION is defined correctly."""

    def test_product_version_exists(self):
        assert PRODUCT_VERSION is not None

    def test_product_version_value(self):
        assert PRODUCT_VERSION == "1.74.0"

    def test_product_version_is_string(self):
        assert isinstance(PRODUCT_VERSION, str)
