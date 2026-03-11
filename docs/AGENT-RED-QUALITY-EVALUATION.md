# Agent Red Customer Experience Quality Evaluation

**Date:** March 9, 2026  
**Scope:** Codebase quality, maintainability, correctness, and production-readiness review  
**Method:** Static repository review plus verification against in-repo tests, CI configuration, and operational artifacts

## Executive Summary

This review confirms that Agent Red is a production-oriented SaaS codebase with strong tenant isolation, substantial middleware hardening, broad test coverage, and real CI workflows already in place. The highest-risk gaps remain concentrated in the standalone admin password flow and in incomplete consolidation of auth-adjacent rate limiting.

The original report was directionally right on the major security concerns, but several supporting claims needed correction:

1. Coverage reporting already exists and is enforced at 70 percent in `pyproject.toml`, with shard-based CI in `.github/workflows/python-tests.yml`.
2. CI/CD configuration is not missing; both test and lint workflows are present.
3. Rate limiting is more nuanced than the first draft stated: the main tenant middleware limiter is still in-memory, but a reusable Redis-backed rate-limit backend already exists in `src/multi_tenant/security_hardening.py` and is wired at startup when `REDIS_URL` is configured.
4. Some operational documentation is stale and contradicts the current code, especially rate-limit procedure docs and the deprecated deployment runbook.

**Overall rating:** `B+`

This is a good codebase with a short list of important security and maintainability issues. The most important work is still to harden standalone admin auth and finish adopting shared/distributed rate-limiting primitives consistently.

## Review Basis

### Code reviewed directly

- `src/app/standalone_auth.py`
- `src/app/lifecycle.py`
- `src/app/routers.py`
- `src/multi_tenant/auth.py`
- `src/multi_tenant/middleware.py`
- `src/multi_tenant/security_middleware.py`
- `src/multi_tenant/security_hardening.py`
- `src/multi_tenant/api_versioning.py`
- `src/multi_tenant/otel_tracing.py`
- `src/multi_tenant/nats_isolation.py`
- `src/multi_tenant/superadmin_api.py`
- `.github/workflows/python-tests.yml`
- `.github/workflows/lint.yml`
- `pyproject.toml`
- `requirements.txt`
- `requirements-test.txt`
- `docs/operations/RELEASE-MANAGEMENT.md`
- `docs/operations/DEPLOYMENT-RUNBOOK.md`
- `docs/operations/rate-limit-test-procedure.md`

### Tests and artifacts reviewed directly

- `tests/test_forgot_password.py`
- `tests/multi_tenant/test_auth_middleware.py`
- `tests/multi_tenant/test_tier_rate_limits.py`
- `tests/multi_tenant/test_security_middleware.py`
- `tests/multi_tenant/test_api_versioning.py`
- `tests/unit/test_redis_rate_limit_backend.py`
- `tests/unit/test_code_quality_s132.py`
- `tests/multi_tenant/test_superadmin_api.py`
- `docs/tests/MASTER-TEST-EXECUTION-RESULTS-1.0.md`

### Local execution note

I installed a workspace-local Python test environment under `.codex_pydeps` and ran the focused suites that map directly to the main claims in this report.

Executed command:

```bash
python -m pytest tests/test_forgot_password.py tests/multi_tenant/test_auth_middleware.py tests/multi_tenant/test_tier_rate_limits.py tests/multi_tenant/test_security_middleware.py tests/multi_tenant/test_api_versioning.py tests/unit/test_redis_rate_limit_backend.py tests/unit/test_code_quality_s132.py -q --tb=short
```

Result: `242 passed` in about `103s`.

That local run confirms the report's core assertions around standalone reset behavior, auth and tenant middleware behavior, rate-limit abstractions, security middleware, API versioning, and the preserved code-quality follow-up work.

## Confidence Model

- `Confirmed`: visible directly in code or documentation reviewed in this pass.
- `Confirmed by tests/artifacts`: also supported by existing tests, CI configuration, or recorded test results in the repo.
- `Inferred`: reasonable conclusion from repository state, but still needs runtime or environment confirmation.
- `Unknown`: not enough evidence in scope.

## Tier 1: Must Resolve

### 1. Security and Authentication

#### Confirmed findings

- Standalone admin authentication still compares plaintext input directly against `_admin_current_password` in `src/app/standalone_auth.py`.
- The standalone admin cookie value is deterministically derived from the password using SHA-256 in `_compute_cookie_value()`.
- The module stores `_admin_current_password` in process memory and uses `_admin_cookie_value` derived from that password material.
- Reset-password UI and server-side validation still enforce only a 6-character minimum.
- Form POST routes for `/admin/standalone/_auth` and `/admin/standalone/_reset-password` do not show any explicit CSRF token validation.
- Session cookies are `HttpOnly`, `Secure`, `SameSite=Lax`, and 7-day.
- Reset tokens themselves are HMAC validated with constant-time signature comparison via `_hmac.compare_digest`, which is good.
- The forgot-password flow intentionally avoids email enumeration and is covered by tests in `tests/test_forgot_password.py`.

#### Security assessment

- `Password handling:` weak (`C`), confirmed.
- `Password policy:` weak (`D`), confirmed.
- `CSRF protection:` gap (`D`), confirmed.
- `Session cookie flags:` good (`B+`), confirmed.
- `Primary API auth architecture:` good (`A-`), confirmed.

#### Specific repository work already related to this area

- `SPEC-1621`: pre-auth failed-auth tracking in `TenantAuthMiddleware` and `PreAuthRateLimitMiddleware`.
- `SPEC-1622`: SMTP work offloaded with `asyncio.to_thread()`.
- `SPEC-1623`: background cleanup/lifespan migration for auth protection infrastructure.
- `SPEC-1667`: platform admin key isolation from tenant auth.
- `SPEC-1675`: stricter platform superadmin privilege guard.
- `SPEC-1676`: login notification wiring for SPA platform admin auth.
- `SPEC-1677` and `SPEC-1678`: account recovery and SPA recovery auth exemptions.
- `WI-0980` to `WI-0985`: code-quality/security-hardening follow-up work already codified in `tests/unit/test_code_quality_s132.py`.

#### Additional concrete work items to add

1. Replace standalone admin plaintext password comparison with Argon2id or bcrypt verification.
2. Remove password-derived cookie material; sign opaque session cookies with a server secret instead.
3. Stop retaining the active plaintext admin password in module state.
4. Add CSRF protection to browser form flows.
5. Raise minimum password length to at least 12 characters and enforce server-side.
6. Consider `__Host-` cookie naming and evaluate `SameSite=Strict` for standalone admin if UX permits.
7. Add explicit tests that prove missing CSRF tokens are rejected.

#### Automated verification example

```python
# Example future test file:
# tests/security/test_standalone_admin_hardening.py

from fastapi.testclient import TestClient


def test_login_without_csrf_token_is_rejected(client: TestClient):
    resp = client.post(
        "/admin/standalone/_auth",
        data={"password": "correct horse battery staple"},
        follow_redirects=False,
    )
    assert resp.status_code == 403


def test_login_with_valid_csrf_token_succeeds(client: TestClient):
    login_page = client.get("/admin/standalone/")
    csrf_token = extract_csrf_token(login_page.text)

    resp = client.post(
        "/admin/standalone/_auth",
        data={
            "password": "correct horse battery staple",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "set-cookie" in resp.headers


def test_password_hash_is_stored_not_plaintext(auth_store):
    record = auth_store.get_admin_credentials()
    assert record.password_hash.startswith("$argon2id$")
    assert "correct horse battery staple" not in repr(record)
```

## 2. Multi-Tenancy and Data Isolation

### Confirmed findings

- `TenantContext` is the central authenticated identity object and is injected per request.
- Widget keys are restricted by `WIDGET_KEY_ALLOWED_PREFIXES` to `/api/chat/`, `/ws/chat/`, and `/api/config`.
- `TenantAuthMiddleware` authenticates every non-exempt request and attaches tenant context before handlers run.
- `get_tenant_context()` prevents platform admin credentials from touching tenant-scoped endpoints.
- `nats_isolation.py` enforces tenant-prefixed subjects and rejects cross-tenant subject access.
- `TenantAuthMiddleware` also rejects a mismatched `?tenant=` URL parameter for non-platform-admin flows.

#### Assessment

- `Tenant isolation:` strong (`A`), confirmed.
- `Widget scope control:` strong (`A`), confirmed.
- `Transport-layer isolation via NATS:` strong (`A`), confirmed.

#### Specific repository work already related to this area

- `Decision #3`: tenant-scoped NATS topics.
- `Decision #14` and `Decision #15`: queue depth and NATS circuit breaking.
- `SPEC-1667`: platform-admin isolation.
- `WI-1045` / `SPEC-1657`: tenant URL parameter mismatch rejection.

#### Additional concrete work items to add

1. Add an explicit RBAC and auth-matrix document covering tenant key, user key, widget key, Shopify session, magic-link session, and SPA platform-admin auth.
2. Add audit logging around role changes, platform-admin operations, and tenant-tier overrides.
3. Add tests for widget access denial on every non-allowed prefix, not just representative paths.

#### Automated verification example

```python
def test_widget_key_cannot_access_billing_api(client, widget_key):
    resp = client.get(
        "/api/admin/tier-upgrade",
        headers={"X-Widget-Key": widget_key},
    )
    assert resp.status_code == 401 or resp.status_code == 403


def test_platform_admin_cannot_access_tenant_api(client, spa_key):
    resp = client.get(
        "/api/config",
        headers={"X-API-Key": spa_key},
    )
    assert resp.status_code == 403
```

## 3. Correctness and Business Logic

### Confirmed findings

- Layering is real: auth, middleware, repositories, schemas, chat pipeline, and admin APIs are split into separate modules.
- `security_middleware.py` enforces a 1 MB body limit and 50-level JSON depth validation, both covered by tests.
- Error handling is present but not fully standardized; middleware responses use simple `{"error": ...}` payloads, while FastAPI dependency failures often raise `HTTPException(detail=...)`.
- The standalone reset flow no longer changes the password in-memory after reset; it auto-logs in instead. This mitigates one multi-replica inconsistency class, but does not solve the underlying password-storage design.

#### Assessment

- `Core request validation:` good (`B+`), confirmed by tests.
- `Error contract consistency:` mixed (`B`), confirmed.

#### Specific repository work already related to this area

- `SPEC-1246`: request body limit.
- `SPEC-1248`: JSON depth limit.
- `SPEC-1622`: non-blocking SMTP calls.

#### Additional concrete work items to add

1. Standardize API error payloads across middleware and route handlers.
2. Add a documented error schema and enforce it in tests.
3. Add tests for cross-layer consistency of 401, 403, 429, and 500 responses.

## Tier 2: High-Value Refactors

### 4. Architecture and Design

#### Confirmed findings

- Domain grouping is clear across `src/app`, `src/chat`, `src/integrations`, and `src/multi_tenant`.
- `src/multi_tenant/superadmin_api.py` is a genuine maintenance hotspot: about 4,175 lines and 61 routed endpoints in one module.
- The codebase already has dedicated tests for superadmin behavior in `tests/multi_tenant/test_superadmin_api.py` and `tests/multi_tenant/test_superadmin_api_endpoints.py`.
- No obvious circular import failure is visible from the reviewed files, but no explicit cycle-check tool was found.

#### Assessment

- `Overall architecture:` good (`B+`), confirmed.
- `Superadmin module cohesion:` weak spot, confirmed.

#### Specific repository work already related to this area

- `RB-1`, `RB-2`, `RB-7`, `RB-8`: provider dashboard, tenant directory, billing health, deployment history tests are already represented in `test_superadmin_api.py`.

#### Additional concrete work items to add

1. Split `superadmin_api.py` into smaller routers by concern: tenant lifecycle, billing/expiry, observability, incidents/alerts, and platform configuration.
2. Add import-cycle detection in CI.
3. Add route/module ownership notes for the provider console.

### 5. Code Quality and Maintainability

#### Confirmed findings

- Ruff is configured in `pyproject.toml` and CI, but the lint workflow is intentionally non-blocking because the codebase still has about 600 style issues per workflow comment.
- A shared rate-limit abstraction already exists in `src/multi_tenant/security_hardening.py` (`RateLimitBackend`, `InMemoryRateLimitBackend`, `RedisRateLimitBackend`).
- Adoption is incomplete. Several modules still own their own local `_rate_limit` or equivalent dict-based sliding-window logic, including:
  - `src/app/standalone_auth.py`
  - `src/multi_tenant/magic_link_auth.py`
  - `src/multi_tenant/email_verification.py`
  - `src/multi_tenant/widget_otp_verification.py`
  - `src/multi_tenant/spa_recovery.py`
  - `src/multi_tenant/admin_apikey_api.py`
  - `src/multi_tenant/email_change.py`
- The main per-tenant `RateLimitMiddleware` is still in-memory, despite the presence of Redis-backed abstractions elsewhere.
- No `radon`, `vulture`, or `pydeps` tooling was found in the reviewed config.

#### Assessment

- `Naming and organization:` good (`B+`), confirmed.
- `Duplication in rate limiting:` mixed (`C+`), confirmed.
- `Lint discipline:` improving but not yet enforced, confirmed.

#### Specific repository work already related to this area

- `WI-0985` / `SPEC-1626`: distributed rate limiting abstraction already implemented.
- `tests/unit/test_redis_rate_limit_backend.py`: verifies Redis backend behavior.
- `tests/unit/test_code_quality_s132.py`: preserves the abstraction and related follow-up work.

#### Additional concrete work items to add

1. Migrate all auth-adjacent local rate-limit dicts to the shared backend abstraction.
2. Decide whether `RateLimitMiddleware` should also move to the shared backend or remain separate by design.
3. Make Ruff blocking after the current style backlog is reduced.
4. Add complexity, dead-code, and import-cycle checks to CI.

#### Automated verification example

```python
from src.multi_tenant.security_hardening import InMemoryRateLimitBackend


def test_magic_link_uses_shared_rate_limit_backend(monkeypatch):
    backend = InMemoryRateLimitBackend()
    monkeypatch.setattr(
        "src.multi_tenant.magic_link_auth.get_rate_limit_backend",
        lambda: backend,
    )

    assert backend.is_limited("ip:1.2.3.4", max_requests=3, window_seconds=300) is False
    assert backend.is_limited("ip:1.2.3.4", max_requests=3, window_seconds=300) is False
    assert backend.is_limited("ip:1.2.3.4", max_requests=3, window_seconds=300) is False
    assert backend.is_limited("ip:1.2.3.4", max_requests=3, window_seconds=300) is True
```

### 6. Testing

#### Confirmed findings

- `pytest`, `pytest-cov`, `pytest-xdist`, and `pytest-timeout` are declared in `requirements-test.txt`.
- Coverage is configured in `pyproject.toml` with `fail_under = 70`.
- The main CI test workflow shards tests across Python 3.12 and 3.13 and merges coverage artifacts.
- Existing repository artifacts report 1,826 Python tests plus integration and browser coverage in `docs/tests/MASTER-TEST-EXECUTION-RESULTS-1.0.md`.
- Focused tests exist for auth, middleware, security middleware, standalone reset flow, Redis-backed rate limiting, and code-quality regressions.
- `pytest-xdist` is installed but not used in the reviewed CI workflow.

#### Assessment

- `Test breadth:` strong (`A`), confirmed by tests and artifacts.
- `Coverage discipline:` strong (`A-`), confirmed.
- `Parallel test execution in CI:` partial (`B`), confirmed.

#### Specific repository work already related to this area

- `Work Item #104`: test infrastructure.
- `Work Item #105`: coverage gate.
- `WI-0980` to `WI-0986`: code-quality follow-up protections.
- `SPEC-1246`, `SPEC-1248`, `SPEC-1626`: covered by dedicated tests.

#### Additional concrete work items to add

1. Use `pytest-xdist` in CI where ordering permits.
2. Publish flake/slow-test metrics as CI artifacts.
3. Add tests specifically for CSRF rejection and secure standalone password storage after the hardening refactor.
4. Keep test artifact counts in docs synchronized with the current suite size.

## 7. Dependencies and Infrastructure

### Confirmed findings

- Core dependencies are modern: FastAPI, Pydantic v2, Redis client, OpenTelemetry, PyJWT, Azure SDKs.
- `redis[hiredis]` is already included in `requirements.txt`.
- `argon2-cffi` and `bcrypt` are not present.
- No `pip-audit` or `safety` workflow was found in the reviewed CI files.
- Terraform infrastructure exists under `infrastructure/terraform/`.

#### Assessment

- `Dependency freshness:` good (`B`), confirmed.
- `Vulnerability scanning:` gap in reviewed CI (`C`), confirmed.
- `Infrastructure as code:` good (`A`), confirmed.

#### Additional concrete work items to add

1. Add `argon2-cffi` or `bcrypt` as part of standalone-auth hardening.
2. Add dependency vulnerability scanning to CI.
3. Add dependency update automation or a scheduled review cadence.

## Tier 3: Important but Not Urgent

### 8. API Design

#### Confirmed findings

- API version headers are implemented by `ApiVersionMiddleware`.
- `API_VERSION` and `PRODUCT_VERSION` constants are tested.
- `src/app/routers.py` includes 46 router registrations, indicating a broad API surface.
- Widget-key scoping and platform-admin isolation are enforced in middleware rather than relying on route authors alone.

#### Assessment

- `API versioning:` strong (`A`), confirmed.
- `Auth/path scoping:` strong (`A`), confirmed.

#### Specific repository work already related to this area

- `WI #140`: API versioning headers.
- `SPEC-1667`, `SPEC-1675`: path and privilege isolation for platform admin.

#### Additional concrete work items to add

1. Add route-level deprecation notices as soon as the first API retirement path exists.
2. Standardize problem-detail responses for major error classes.

### 9. Scalability and Performance

#### Confirmed findings

- The app is largely stateless per request and tenant context is resolved per request.
- NATS JetStream tenant streams and async repositories are in place.
- The main per-tenant `RateLimitMiddleware` explicitly documents that it is suitable only for single-instance enforcement.
- A Redis-backed rate-limit backend exists and is startup-wired when `REDIS_URL` is set, but that backend currently protects shared auth-limit flows rather than the main tenant middleware path.

#### Assessment

- `Horizontal-scaling architecture:` good (`A-`), confirmed.
- `Remaining scale gap:` inconsistent distributed rate-limit adoption, confirmed.

#### Additional concrete work items to add

1. Decide whether per-tenant API request limiting must become distributed for multi-replica correctness.
2. Finish migration of auth-adjacent throttles to the shared backend.
3. Document which rate-limiters are replica-safe today and which are not.

### 10. Observability and Operations

#### Confirmed findings

- `TenantSpanProcessor`, `CorrelationContext`, and tenant-aware log filtering are implemented in `otel_tracing.py`.
- LLM token and estimated-cost attributes are tracked.
- `SecurityHeadersMiddleware` records request latency into SLA monitoring on a best-effort basis.
- `lifecycle.py` starts tracing, circuit breakers, NATS, alert delivery, and related services during app startup.
- Operational docs exist, but not all are current.

#### Assessment

- `Telemetry foundation:` strong (`A`), confirmed.
- `Operational-document consistency:` mixed (`B`), confirmed.

#### Specific repository work already related to this area

- `Decision #11` and `Decision #12`: tenant-aware telemetry and correlation chain.
- `SPEC-1540`: LLM token/cost attribution.
- `WI #39` and `WI #40`: tracing and logging context propagation.

#### Additional concrete work items to add

1. Add explicit SLO definitions and dashboards if not already externalized.
2. Add alert-routing ownership in docs; several contact fields remain `TBD`.
3. Keep version numbers and telemetry docs synchronized with current releases.

### 11. CI/CD and Deployment

#### Confirmed findings

- `.github/workflows/python-tests.yml` is a real PR and push workflow with sharded tests and merged coverage.
- `.github/workflows/lint.yml` exists but is non-blocking.
- `docs/operations/RELEASE-MANAGEMENT.md` is the current release document.
- `docs/operations/DEPLOYMENT-RUNBOOK.md` is explicitly marked deprecated and contains stale resource names.
- The stale deployment runbook still contains detailed procedures and could mislead operators if referenced accidentally.

#### Assessment

- `Test pipeline presence:` confirmed and good (`B+`).
- `Blocking quality gates:` partial (`B`).
- `Documentation safety for deployment:` mixed because of stale legacy docs (`C+`).

#### Specific repository work already related to this area

- `Work Item #104` and `#105`: test and coverage pipeline.
- `WI #148`, `#149`, `#150`: deployment, DR, maintenance docs.
- `WI #156`: Option C upgrade trigger in ops docs.

#### Additional concrete work items to add

1. Add security scanning to the existing CI workflow set.
2. Make lint gradually blocking.
3. Archive or heavily quarantine deprecated runbooks so operators do not use them accidentally.
4. Add a single canonical deployment/readiness/rollback document index.

## Tier 4: Process and Documentation

### 12. Documentation and Knowledge Sharing

#### Confirmed findings

- Core architecture and operations docs are present.
- The release-management document is current and materially better than the deprecated deployment runbook.
- The rate-limit operations procedure is stale: it still describes 10/50/200 RPM thresholds, while code and tests now enforce 500 RPM across tiers.
- `tests/multi_tenant/test_tier_rate_limits.py` explicitly includes stale-documentation checks, confirming the repository already knows about this drift.

#### Assessment

- `Documentation coverage:` strong (`A-`), confirmed.
- `Documentation consistency:` mixed due to stale operational docs, confirmed.

#### Specific repository work already related to this area

- `TEST-2863` and `TEST-2864`: stale documentation guardrails in `tests/multi_tenant/test_tier_rate_limits.py`.
- Deprecated notice already added to `docs/operations/DEPLOYMENT-RUNBOOK.md`.

#### Additional concrete work items to add

1. Update `docs/operations/rate-limit-test-procedure.md` to match current 500 RPM limits or clearly mark it historical.
2. Add an operations-doc index page marking canonical vs deprecated procedures.
3. Add a concise developer onboarding checklist.
4. Keep test-count claims in docs synchronized with the current suite.

### 13. Technical Debt Summary

#### Highest-value debt actually confirmed in this review

1. Standalone admin auth stores and compares password material unsafely.
2. Standalone admin form flows lack explicit CSRF protection.
3. Shared/distributed rate-limit primitives exist, but adoption is incomplete.
4. `superadmin_api.py` is too large and too broad.
5. Lint is present but not yet enforcing quality gates.
6. Operational docs contain stale procedures and contradictory thresholds.

## Prioritized Actions

### Immediate

1. Harden standalone admin password storage and session design.
2. Add CSRF protection to standalone admin form flows.
3. Raise password-policy enforcement server-side.
4. Add dependency vulnerability scanning to CI.
5. Update or quarantine stale rate-limit and deployment procedure docs.

### Near Term

1. Migrate duplicated auth-adjacent rate limiting to the shared backend abstraction.
2. Decide whether `RateLimitMiddleware` also needs distributed backing for multi-replica correctness.
3. Split `superadmin_api.py` by domain.
4. Make lint progressively blocking.

### Ongoing

1. Add import-cycle, dead-code, and complexity tooling.
2. Add explicit CSRF/security-hardening tests once the implementation lands.
3. Keep release docs, test artifacts, and operational procedures synchronized.

## Summary Ratings

| Category | Rating | Main Concern |
|----------|--------|--------------|
| Security and Authentication | `C+` | Standalone password handling and CSRF |
| Multi-Tenancy | `A` | No major issue identified |
| Correctness and Business Logic | `B+` | Error-contract consistency |
| Architecture and Design | `B+` | Oversized `superadmin_api.py` |
| Code Quality and Maintainability | `B-` | Incomplete rate-limit consolidation |
| Testing | `A-` | Fresh local execution unavailable in this environment |
| Dependencies and Infrastructure | `B` | Missing vulnerability-scan workflow |
| API Design | `A` | No major issue identified |
| Scalability and Performance | `A-` | Distributed rate-limit adoption incomplete |
| Observability and Operations | `A-` | Strong foundations, some stale ops docs |
| CI/CD and Deployment | `B+` | CI exists; some gates are still non-blocking |
| Documentation | `A-` | Canonical docs exist, but some stale docs remain |

**Overall rating:** `B+`

## Recommended Test-Solution Appendix

Use these commands once a pytest-capable environment is available:

```bash
python -m pytest tests/test_forgot_password.py -q --tb=short
python -m pytest tests/multi_tenant/test_auth_middleware.py -q --tb=short
python -m pytest tests/multi_tenant/test_tier_rate_limits.py -q --tb=short
python -m pytest tests/multi_tenant/test_security_middleware.py -q --tb=short
python -m pytest tests/unit/test_redis_rate_limit_backend.py -q --tb=short
```

For the new hardening work, add a focused suite such as:

```bash
python -m pytest tests/security/test_standalone_admin_hardening.py -q --tb=short
```

That suite should verify both:

- The issue reproduction path on the old implementation.
- The expected post-fix behavior on the new implementation.

---

Cross-reference:

- `CLAUDE-ARCHITECTURE.md`
- `docs/operations/RELEASE-MANAGEMENT.md`
- `docs/operations/SHOPIFY-APP-REVIEW-PREFLIGHT-CHECKLIST.md`
- `docs/tests/MASTER-TEST-EXECUTION-RESULTS-1.0.md`

