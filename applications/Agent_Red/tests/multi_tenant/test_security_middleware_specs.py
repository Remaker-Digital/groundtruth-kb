"""Tests for security middleware specs — classes, functions, and headers.

Covers infrastructure specs for security middleware layer:
    SPEC-1389: size_limited_receive() function exists in security_middleware
    SPEC-1390: dispatch() method in JsonDepthValidationMiddleware
    SPEC-1391: send_with_security_headers() function exists in security_middleware
    SPEC-1393: X-Frame-Options header set by security_middleware
    SPEC-1394: X-XSS-Protection header set by security_middleware
    SPEC-1395: X-Frame-Options (duplicate — same header assertion)

Total: 12 tests

Note: size_limited_receive() and send_with_security_headers() are nested
functions inside __call__ methods. We verify their existence by inspecting
the source code of the containing method, since they are not directly
accessible as attributes.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect



# ===================================================================
# SPEC-1389: size_limited_receive() function exists in security_middleware
# ===================================================================


class TestSizeLimitedReceiveExists:
    """SPEC-1389: size_limited_receive() function exists in security_middleware."""

    def test_request_body_limit_middleware_class_exists(self):
        """RequestBodyLimitMiddleware is importable and is a class."""
        from src.multi_tenant.security_middleware import RequestBodyLimitMiddleware
        assert isinstance(RequestBodyLimitMiddleware, type)

    def test_request_body_limit_middleware_is_callable(self):
        """RequestBodyLimitMiddleware has an async __call__ method."""
        from src.multi_tenant.security_middleware import RequestBodyLimitMiddleware
        assert hasattr(RequestBodyLimitMiddleware, "__call__")
        assert inspect.iscoroutinefunction(RequestBodyLimitMiddleware.__call__)

    def test_size_limited_receive_defined_in_source(self):
        """size_limited_receive is defined as a nested function in __call__.

        Since it is a closure inside __call__, we verify its existence
        by inspecting the source code of the containing method.
        """
        from src.multi_tenant.security_middleware import RequestBodyLimitMiddleware
        source = inspect.getsource(RequestBodyLimitMiddleware.__call__)
        assert "size_limited_receive" in source
        assert "async def size_limited_receive" in source


# ===================================================================
# SPEC-1390: dispatch() method in JsonDepthValidationMiddleware
# ===================================================================


class TestJsonDepthValidationMiddlewareDispatch:
    """SPEC-1390: dispatch() method in JsonDepthValidationMiddleware."""

    def test_json_depth_validation_middleware_class_exists(self):
        """JsonDepthValidationMiddleware is importable and is a class."""
        from src.multi_tenant.security_middleware import JsonDepthValidationMiddleware
        assert isinstance(JsonDepthValidationMiddleware, type)

    def test_dispatch_method_exists(self):
        """JsonDepthValidationMiddleware has a dispatch method."""
        from src.multi_tenant.security_middleware import JsonDepthValidationMiddleware
        assert hasattr(JsonDepthValidationMiddleware, "dispatch")

    def test_dispatch_is_async(self):
        """JsonDepthValidationMiddleware.dispatch is an async method."""
        from src.multi_tenant.security_middleware import JsonDepthValidationMiddleware
        assert inspect.iscoroutinefunction(JsonDepthValidationMiddleware.dispatch)

    def test_dispatch_signature_has_request_and_call_next(self):
        """dispatch accepts request and call_next parameters."""
        from src.multi_tenant.security_middleware import JsonDepthValidationMiddleware
        sig = inspect.signature(JsonDepthValidationMiddleware.dispatch)
        param_names = list(sig.parameters.keys())
        assert "request" in param_names
        assert "call_next" in param_names


# ===================================================================
# SPEC-1391: send_with_security_headers() exists in security_middleware
# ===================================================================


class TestSendWithSecurityHeadersExists:
    """SPEC-1391: send_with_security_headers() function exists."""

    def test_security_headers_middleware_class_exists(self):
        """SecurityHeadersMiddleware is importable and is a class."""
        from src.multi_tenant.security_middleware import SecurityHeadersMiddleware
        assert isinstance(SecurityHeadersMiddleware, type)

    def test_send_with_security_headers_defined_in_source(self):
        """send_with_security_headers is defined as a nested function in __call__.

        Since it is a closure inside __call__, we verify its existence
        by inspecting the source code of the containing method.
        """
        from src.multi_tenant.security_middleware import SecurityHeadersMiddleware
        source = inspect.getsource(SecurityHeadersMiddleware.__call__)
        assert "send_with_security_headers" in source
        assert "async def send_with_security_headers" in source


# ===================================================================
# SPEC-1393: X-Frame-Options header set by security_middleware
# ===================================================================


class TestXFrameOptionsHeader:
    """SPEC-1393: X-Frame-Options header set by security_middleware."""

    def test_security_headers_dict_exists(self):
        """SECURITY_HEADERS dict is importable from security_middleware."""
        from src.multi_tenant.security_middleware import SECURITY_HEADERS
        assert isinstance(SECURITY_HEADERS, dict)

    def test_x_frame_options_is_deny(self):
        """X-Frame-Options header is set to DENY."""
        from src.multi_tenant.security_middleware import SECURITY_HEADERS
        assert SECURITY_HEADERS.get("X-Frame-Options") == "DENY"


# ===================================================================
# SPEC-1394: X-XSS-Protection header set by security_middleware
# ===================================================================


class TestXXSSProtectionHeader:
    """SPEC-1394: X-XSS-Protection header set by security_middleware."""

    def test_x_xss_protection_is_zero(self):
        """X-XSS-Protection header is set to '0' (modern best practice)."""
        from src.multi_tenant.security_middleware import SECURITY_HEADERS
        assert SECURITY_HEADERS.get("X-XSS-Protection") == "0"


# ===================================================================
# SPEC-1395: X-Frame-Options (duplicate assertion — same header)
# ===================================================================


class TestXFrameOptionsDuplicate:
    """SPEC-1395: X-Frame-Options header (duplicate confirmation)."""

    def test_x_frame_options_present_in_headers(self):
        """X-Frame-Options key exists in SECURITY_HEADERS dict."""
        from src.multi_tenant.security_middleware import SECURITY_HEADERS
        assert "X-Frame-Options" in SECURITY_HEADERS

    def test_x_frame_options_value_is_deny(self):
        """X-Frame-Options value is DENY (duplicate confirmation)."""
        from src.multi_tenant.security_middleware import SECURITY_HEADERS
        assert SECURITY_HEADERS["X-Frame-Options"] == "DENY"
