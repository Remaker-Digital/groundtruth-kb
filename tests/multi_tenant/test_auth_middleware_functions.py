"""Tests for auth middleware function existence and signatures.

Covers infrastructure specs for authentication layer:
    SPEC-1384: verify_api_key() middleware function exists
    SPEC-1385: verify_user_api_key() middleware function exists
    SPEC-1386: verify_widget_key() middleware function exists

Total: 9 tests

These tests verify that the three authentication verification functions
exist, are async, and accept the expected parameters.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect

import pytest


# ===================================================================
# SPEC-1384: verify_api_key() middleware function exists
# ===================================================================


class TestVerifyApiKeyExists:
    """SPEC-1384: verify_api_key() middleware function exists."""

    def test_verify_api_key_is_importable(self):
        """verify_api_key can be imported from auth module."""
        from src.multi_tenant.auth import verify_api_key
        assert verify_api_key is not None

    def test_verify_api_key_is_async(self):
        """verify_api_key is an async function."""
        from src.multi_tenant.auth import verify_api_key
        assert inspect.iscoroutinefunction(verify_api_key)

    def test_verify_api_key_signature(self):
        """verify_api_key accepts api_key and lookup_fn parameters."""
        from src.multi_tenant.auth import verify_api_key
        sig = inspect.signature(verify_api_key)
        param_names = list(sig.parameters.keys())
        assert "api_key" in param_names
        assert "lookup_fn" in param_names


# ===================================================================
# SPEC-1385: verify_user_api_key() middleware function exists
# ===================================================================


class TestVerifyUserApiKeyExists:
    """SPEC-1385: verify_user_api_key() middleware function exists."""

    def test_verify_user_api_key_is_importable(self):
        """verify_user_api_key can be imported from auth module."""
        from src.multi_tenant.auth import verify_user_api_key
        assert verify_user_api_key is not None

    def test_verify_user_api_key_is_async(self):
        """verify_user_api_key is an async function."""
        from src.multi_tenant.auth import verify_user_api_key
        assert inspect.iscoroutinefunction(verify_user_api_key)

    def test_verify_user_api_key_signature(self):
        """verify_user_api_key accepts api_key and lookup_fn parameters."""
        from src.multi_tenant.auth import verify_user_api_key
        sig = inspect.signature(verify_user_api_key)
        param_names = list(sig.parameters.keys())
        assert "api_key" in param_names
        assert "lookup_fn" in param_names


# ===================================================================
# SPEC-1386: verify_widget_key() middleware function exists
# ===================================================================


class TestVerifyWidgetKeyExists:
    """SPEC-1386: verify_widget_key() middleware function exists."""

    def test_verify_widget_key_is_importable(self):
        """verify_widget_key can be imported from auth module."""
        from src.multi_tenant.auth import verify_widget_key
        assert verify_widget_key is not None

    def test_verify_widget_key_is_async(self):
        """verify_widget_key is an async function."""
        from src.multi_tenant.auth import verify_widget_key
        assert inspect.iscoroutinefunction(verify_widget_key)

    def test_verify_widget_key_signature(self):
        """verify_widget_key accepts widget_key and lookup_fn parameters."""
        from src.multi_tenant.auth import verify_widget_key
        sig = inspect.signature(verify_widget_key)
        param_names = list(sig.parameters.keys())
        assert "widget_key" in param_names
        assert "lookup_fn" in param_names
