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
from schemathesis.checks import load_all_checks, CHECKS

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
    """No endpoint should return unexpected 500-class errors.

    Acceptable: 2xx, 3xx, 4xx, and 5xx codes declared in the OpenAPI spec.
    Unacceptable: 500-class errors that the endpoint didn't explicitly declare
    (indicates unhandled server error / missing error handling).
    """
    response = case.call()

    if response.status_code < 500:
        return  # Not a server error

    # Allow 5xx responses that the endpoint explicitly declares
    # (e.g. 502 on /api/packs/purchase for Stripe failures).
    # Schemathesis 4.x: use operation.responses (OpenApiResponses dict-like).
    declared_codes = set()
    if hasattr(case, 'operation') and hasattr(case.operation, 'responses'):
        declared_codes = {
            str(k) for k in case.operation.responses._inner.keys()
        }

    status_str = str(response.status_code)
    if status_str in declared_codes:
        return  # Declared 5xx — expected behavior

    assert False, (
        f"Undeclared server error {response.status_code} on "
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
    """Responses with declared schemas must conform to the OpenAPI spec.

    Schemathesis sends fuzz inputs that often trigger 401/403/422 error
    responses. These are expected — the API correctly rejects bad input.
    We only validate responses whose status code has a declared schema
    in the OpenAPI spec (typically 200, plus any explicit error schemas).
    Undeclared status codes (e.g. 422 from FastAPI validation, 401 from
    auth middleware) are accepted as long as they're not 500-class.
    """
    response = case.call()

    # Skip validation for 500-class errors (caught by test_api_no_server_errors)
    if response.status_code >= 500:
        return

    # Get declared response status codes for this operation.
    # Schemathesis 4.x: use operation.responses (OpenApiResponses dict-like).
    declared_codes = set()
    if hasattr(case, 'operation') and hasattr(case.operation, 'responses'):
        declared_codes = {
            str(k) for k in case.operation.responses._inner.keys()
        } - {'default'}

    # Only validate if this status code has a declared schema
    status_str = str(response.status_code)
    if declared_codes and status_str not in declared_codes:
        # Undeclared status code (e.g. 422, 401) — skip schema validation
        # but still assert it's not a server error
        assert response.status_code < 500
        return

    # Exclude unsupported_method check: Schemathesis 4.x sends TRACE requests
    # and expects 405. Our auth middleware returns 401 before method validation,
    # which is correct behavior (don't leak endpoint existence to unauthenticated
    # TRACE requests) but fails this check.
    load_all_checks()
    case.validate_response(
        response,
        excluded_checks=[
            # unsupported_method: sends TRACE expecting 405, our auth returns
            # 401 (correct — don't leak endpoint existence to unauthed probes).
            CHECKS.get_one("unsupported_method"),
            # positive_data_acceptance: rejects schema-valid data that violates
            # business rules OpenAPI can't express (conditional required fields,
            # path-param enums, external service dependencies). 25 endpoints
            # affected — all return correct 400s, not bugs. See SPEC-1839.
            CHECKS.get_one("positive_data_acceptance"),
        ],
    )
