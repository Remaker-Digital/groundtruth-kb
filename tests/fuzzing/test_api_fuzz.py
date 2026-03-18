"""Schemathesis API fuzz testing (SPEC-1839 / WI-1467).

Generates test cases from the FastAPI OpenAPI specification and fuzz-tests
all public endpoints. Verifies:
- No 500 errors from any generated input
- All responses match OpenAPI schema
- No unhandled exceptions

Configuration:
- Max 100 test cases per endpoint
- 5-second timeout per case

Usage:
    pytest tests/fuzzing/test_api_fuzz.py -v --timeout=600

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import os

import schemathesis.openapi
from hypothesis import settings, HealthCheck

from src.app.factory import create_app
from src.app.routers import register_routers

# ---------------------------------------------------------------------------
# Create a test-mode FastAPI app with routers registered
# ---------------------------------------------------------------------------

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("RATE_LIMIT_DISABLED", "true")  # Don't rate-limit during fuzzing

app = create_app()
register_routers(app)

# Generate test cases from the OpenAPI schema (schemathesis v4 API)
schema = schemathesis.openapi.from_asgi("/openapi.json", app=app)


# ---------------------------------------------------------------------------
# Fuzz test: no 500 errors from any endpoint
# ---------------------------------------------------------------------------


@schema.parametrize()
@settings(
    max_examples=100,
    deadline=5000,  # 5s per test case
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
def test_api_no_server_errors(case):
    """No endpoint should return 500 for any schema-valid input.

    Acceptable responses: 2xx, 3xx, 400, 401, 403, 404, 409, 422, 429.
    Unacceptable: 500, 502, 503 (indicates unhandled server error).
    """
    response = case.call_asgi()

    # 500-class errors indicate bugs
    assert response.status_code < 500, (
        f"Server error {response.status_code} on "
        f"{case.method} {case.path}: {response.text[:200]}"
    )


# ---------------------------------------------------------------------------
# Fuzz test: responses match OpenAPI schema
# ---------------------------------------------------------------------------


@schema.parametrize()
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
def test_api_responses_match_schema(case):
    """All responses must conform to the declared OpenAPI response schema."""
    response = case.call_asgi()
    case.validate_response(response)
