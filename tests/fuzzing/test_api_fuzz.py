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
- Max examples per endpoint configurable via env vars:
  FUZZ_MAX_EXAMPLES_ERRORS (default: 10 remote, 100 local)
  FUZZ_MAX_EXAMPLES_SCHEMA (default: 5 remote, 50 local)
- 5-second deadline per test case
- Remote defaults tuned for 307 ops within 30min timeout

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

# Configurable example counts — reduce for container runs where 307 operations
# × max_examples × 2 test functions must complete within timeout_s.
# Container default: 10/5 (fits ~20min at ~200ms/request for 307 ops).
# Local default: 100/50 (more thorough, no timeout pressure).
_MAX_EXAMPLES_ERRORS = int(os.environ.get(
    "FUZZ_MAX_EXAMPLES_ERRORS",
    "10" if _FUZZ_TARGET_URL else "100",
))
_MAX_EXAMPLES_SCHEMA = int(os.environ.get(
    "FUZZ_MAX_EXAMPLES_SCHEMA",
    "5" if _FUZZ_TARGET_URL else "50",
))

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
    max_examples=_MAX_EXAMPLES_ERRORS,
    deadline=5000,  # 5s per test case
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
def test_api_no_server_errors(case):
    """No endpoint should return 500 for any schema-valid input.

    Acceptable responses: 2xx, 3xx, 400, 401, 403, 404, 409, 422, 429.
    Unacceptable: 500, 502, 503 (indicates unhandled server error).
    """
    # In Schemathesis 4.x, transport is set by the schema loader
    # (from_url → HTTP, from_asgi → ASGI). case.call() uses whichever
    # transport was configured — no separate call_asgi() needed.
    response = case.call()

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
    max_examples=_MAX_EXAMPLES_SCHEMA,
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
def test_api_responses_match_schema(case):
    """All responses must conform to the declared OpenAPI response schema."""
    response = case.call()
    case.validate_response(response)
