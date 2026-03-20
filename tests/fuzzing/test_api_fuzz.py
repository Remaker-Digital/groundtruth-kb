"""Schemathesis API fuzz testing (SPEC-1839 / WI-1467).

Generates test cases from the OpenAPI specification and fuzz-tests all public
endpoints. Verifies:
- No 500 errors from any generated input
- All responses match OpenAPI schema
- No unhandled exceptions

Environment partitioning:
- STAGING: Set FUZZ_TARGET_URL to the live staging API FQDN. Schemathesis
  fetches the OpenAPI spec via HTTP and sends real requests. Tests the full
  deployed stack (Cosmos, Redis, middleware).
- DEVELOPMENT: Leave FUZZ_TARGET_URL unset. Schemathesis uses from_asgi()
  against the local FastAPI app (no network dependencies at init time).

Configuration:
- Max 100 test cases per endpoint (no-server-errors)
- Max 50 test cases per endpoint (schema validation)
- 5-second timeout per case

Usage (staging — via test host container):
    FUZZ_TARGET_URL=https://agent-red-staging.xxx.eastus.azurecontainerapps.io \
    FUZZ_API_KEY=ar_spa_plat_xxx \
    pytest tests/fuzzing/test_api_fuzz.py -v --timeout=600

Usage (development — local):
    pytest tests/fuzzing/test_api_fuzz.py -v --timeout=600

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import os

import schemathesis.openapi
from hypothesis import settings, HealthCheck

# ---------------------------------------------------------------------------
# Determine fuzz target: live staging API or local ASGI app
# ---------------------------------------------------------------------------

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("RATE_LIMIT_DISABLED", "true")

_FUZZ_TARGET_URL = os.environ.get("FUZZ_TARGET_URL", "")
_FUZZ_API_KEY = os.environ.get("FUZZ_API_KEY", "")

if _FUZZ_TARGET_URL:
    # STAGING: Fuzz the live deployed API — real Cosmos, Redis, middleware
    _headers = {"X-API-Key": _FUZZ_API_KEY} if _FUZZ_API_KEY else {}
    schema = schemathesis.openapi.from_url(
        f"{_FUZZ_TARGET_URL.rstrip('/')}/openapi.json",
        headers=_headers,
    )
else:
    # DEVELOPMENT: Fuzz the local ASGI app in-process
    from src.app.factory import create_app
    from src.app.routers import register_routers

    app = create_app()
    register_routers(app)
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
    if _FUZZ_TARGET_URL:
        response = case.call()
    else:
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
    if _FUZZ_TARGET_URL:
        response = case.call()
    else:
        response = case.call_asgi()
    case.validate_response(response)
