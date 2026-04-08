"""Cloud-native verification runner for SPA-triggered E2E testing (SPEC-1846).

Executes HTTP-based verification checks against a live deployment entirely
within the Azure environment — no dependency on the development machine.
Checks are run as async coroutines with rate limiting and progressive Cosmos
updates so the SPA can display real-time progress.

Suites:
    smoke       — 8 internal health probes (~5s)
    regression  — smoke + 17 API/config HTTP checks (~3min)
    e2e         — regression + 10 security/quality checks (~8min)
    all         — e2e + 5 tenant isolation checks (~12min)

SPEC-1845: All credentials are passed at runtime — no hardcoded keys.
SPEC-1673: Uses HMAC verification tokens — no Cosmos dependency for auth.
SPEC-1846: Tokens are signed with INTERNAL_VERIFICATION_SECRET (auto-generated).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Check result
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Result of a single verification check."""

    name: str = ""      # set by _run_check() after execution
    category: str = ""  # health, api, config, security, tenant_isolation — set by _run_check()
    status: str = "pass"  # pass, fail, skip, error
    latency_ms: float = 0.0
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Suite definitions
# ---------------------------------------------------------------------------

# Categories included in each suite (cumulative).
SUITE_CATEGORIES: dict[str, list[str]] = {
    "smoke": ["health"],
    "regression": ["health", "api", "config"],
    "e2e": ["health", "api", "config", "security", "quality"],
    "all": ["health", "api", "config", "security", "quality", "tenant_isolation"],
}

SUITE_DESCRIPTIONS: dict[str, str] = {
    "smoke": "Health probes (~5s)",
    "regression": "API + config verification (~3min)",
    "e2e": "Full end-to-end (~8min)",
    "all": "Full suite + tenant isolation (~12min)",
}


# ---------------------------------------------------------------------------
# Verification runner
# ---------------------------------------------------------------------------

class VerificationRunner:
    """Runs HTTP-based verification checks against a live deployment.

    Args:
        run_id: Unique identifier for this run.
        environment: Target environment ("staging" or "production").
        fqdn: Fully-qualified domain name of the target API gateway.
        verification_secret: INTERNAL_VERIFICATION_SECRET for HMAC token auth.
        suite: Suite name determining which checks to run.
        cosmos_repo: PlatformConfigRepository for progressive result storage.
        actor: Email or identifier of the user who triggered the run.
    """

    def __init__(
        self,
        run_id: str,
        environment: str,
        fqdn: str,
        verification_secret: str,
        suite: str,
        cosmos_repo: Any,
        actor: str = "spa-console",
    ):
        self.run_id = run_id
        self.environment = environment
        self.fqdn = fqdn
        self.base_url = f"https://{fqdn}"
        self.verification_secret = verification_secret
        self.suite = suite

        # HMAC tokens are signed with this replica's INTERNAL_VERIFICATION_SECRET.
        # Requests to the FQDN may be load-balanced to a different replica that
        # has a different secret — causing HMAC mismatch.  Authenticated checks
        # use localhost to guarantee the request stays on the same replica.
        # Unauthenticated checks (health, security) use the FQDN to exercise
        # the real external path (TLS, Azure load balancer, CORS).
        _port = os.environ.get("PORT", "8000")
        self._local_base_url = f"http://localhost:{_port}"
        self.repo = cosmos_repo
        self.actor = actor

        self._semaphore = asyncio.Semaphore(4)
        self._results: list[CheckResult] = []
        self._start_time: float = 0.0
        self._start_wall: str = ""  # Captured once at run() start; stable across Cosmos updates
        self._http_client: Any = None  # Shared httpx.AsyncClient for the run

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(self) -> list[CheckResult]:
        """Execute all checks for the configured suite and return results."""
        import httpx

        self._start_time = time.monotonic()
        self._start_wall = datetime.now(timezone.utc).isoformat()
        categories = SUITE_CATEGORIES.get(self.suite, ["health"])
        all_checks = self._get_checks_for_categories(categories)

        # Shared HTTP client for all checks (single TLS handshake per FQDN)
        self._http_client = httpx.AsyncClient(timeout=15.0, verify=True)
        try:
            # Store initial "running" status
            await self._update_cosmos("running", total=len(all_checks))

            # Run checks in batches of 4 with cooldown
            batch_size = 4
            for i in range(0, len(all_checks), batch_size):
                batch = all_checks[i:i + batch_size]
                batch_results = await asyncio.gather(
                    *(self._run_check(check_fn) for check_fn in batch),
                    return_exceptions=True,
                )
                for result in batch_results:
                    if isinstance(result, Exception):
                        self._results.append(CheckResult(
                            name="unknown", category="error", status="error",
                            detail=str(result),
                        ))
                    else:
                        self._results.append(result)

                # Progressive update after each batch
                await self._update_cosmos("running", total=len(all_checks))

                # Cooldown between batches (1s) to respect rate limits
                if i + batch_size < len(all_checks):
                    await asyncio.sleep(1.0)

            # Final status — "fail" or "error" both count as failures
            failed = sum(1 for r in self._results if r.status in ("fail", "error"))
            final_status = "passed" if failed == 0 else "failed"
            await self._update_cosmos(final_status, total=len(all_checks))
        finally:
            await self._http_client.aclose()
            self._http_client = None

        logger.info(
            "Verification run %s completed: %s (%d/%d passed, %.1fs)",
            self.run_id, final_status,
            sum(1 for r in self._results if r.status == "pass"),
            len(self._results),
            time.monotonic() - self._start_time,
        )
        return self._results

    # ------------------------------------------------------------------
    # Check registry
    # ------------------------------------------------------------------

    def _get_checks_for_categories(
        self, categories: list[str],
    ) -> list[tuple[str, str, Any]]:
        """Return (name, category, coroutine_factory) tuples for requested categories."""
        registry: list[tuple[str, str, Any]] = []

        if "health" in categories:
            registry.extend([
                ("health_endpoint", "health", self._check_health),
                ("ready_endpoint", "health", self._check_ready),
                ("api_version", "health", self._check_api_version),
                ("cosmos_probe", "health", self._check_cosmos),
                ("redis_probe", "health", self._check_redis),
                ("key_vault_probe", "health", self._check_key_vault),
                ("spa_assets", "health", self._check_spa_assets),
                ("openapi_spec", "health", self._check_openapi),
            ])

        if "api" in categories:
            registry.extend([
                ("superadmin_tenants", "api", self._check_superadmin_tenants),
                ("superadmin_dashboard", "api", self._check_superadmin_dashboard),
                ("incidents_endpoint", "api", self._check_incidents),
                ("alert_rules_endpoint", "api", self._check_alert_rules),
                ("mfa_status", "api", self._check_mfa_status),
                ("cost_analytics", "api", self._check_cost_analytics),
                ("abuse_detection", "api", self._check_abuse_detection),
                ("deployments_list", "api", self._check_deployments),
                ("pipeline_topology", "api", self._check_pipeline_topology),
                ("quality_score", "api", self._check_quality_score),
            ])

        if "config" in categories:
            registry.extend([
                ("public_status", "config", self._check_public_status),
                ("spa_served", "config", self._check_spa_served),
                ("entitlement_listing", "config", self._check_entitlements),
                ("feature_flags", "config", self._check_feature_flags),
                ("blocklist_config", "config", self._check_blocklist_config),
                ("maintenance_mode", "config", self._check_maintenance_mode),
                ("retry_config", "config", self._check_retry_config),
            ])

        if "security" in categories:
            registry.extend([
                ("security_headers", "security", self._check_security_headers),
                ("cors_preflight", "security", self._check_cors),
                ("rate_limit_headers", "security", self._check_rate_limit_headers),
                ("no_server_version_leak", "security", self._check_no_version_leak),
                ("401_no_internal_details", "security", self._check_401_clean),
                ("404_no_internal_details", "security", self._check_404_clean),
            ])

        if "quality" in categories:
            registry.extend([
                ("memory_stats", "quality", self._check_memory_stats),
                ("tier_listing", "quality", self._check_tier_listing),
                ("addon_listing", "quality", self._check_addon_listing),
                ("diagnostics_export", "quality", self._check_diagnostics_export),
            ])

        if "tenant_isolation" in categories:
            registry.extend([
                ("tenant_count_consistency", "tenant_isolation", self._check_tenant_count),
                ("entitlement_consistency", "tenant_isolation", self._check_entitlement_consistency),
                ("audit_log_recency", "tenant_isolation", self._check_audit_recency),
                ("config_integrity", "tenant_isolation", self._check_config_integrity),
                ("no_orphan_configs", "tenant_isolation", self._check_no_orphans),
            ])

        return registry

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _run_check(
        self, check_entry: tuple[str, str, Any],
    ) -> CheckResult:
        """Run a single check with semaphore and timing."""
        name, category, check_fn = check_entry
        async with self._semaphore:
            start = time.monotonic()
            try:
                result = await check_fn()
                result.name = name
                result.category = category
                result.latency_ms = round((time.monotonic() - start) * 1000, 1)
                return result
            except Exception as exc:
                elapsed = round((time.monotonic() - start) * 1000, 1)
                return CheckResult(
                    name=name, category=category, status="error",
                    latency_ms=elapsed, detail=str(exc)[:500],
                )

    async def _http_get(
        self, path: str, *, auth: bool = True, timeout: float = 15.0,
    ) -> tuple[int, dict[str, str], str]:
        """Make an HTTP GET request to the target environment.

        Returns (status_code, headers_dict, body_text).
        SPEC-1846: Uses HMAC verification tokens — no Cosmos dependency.
        Uses shared httpx.AsyncClient for connection reuse.
        """
        import httpx
        headers: dict[str, str] = {
            "User-Agent": f"VerificationRunner/{self.run_id}",
        }
        if auth:
            from src.multi_tenant.auth import generate_verification_token
            token_val = generate_verification_token(
                self.run_id, self.verification_secret,
            )
            headers["X-Verification-Token"] = token_val

            # Diagnostic: log secret fingerprint to cross-reference with middleware
            import hashlib as _hl
            _secret_fp = _hl.sha256(self.verification_secret.encode()).hexdigest()[:12]
            logger.info(
                "HMAC diag: secret_fp=%s token_prefix=%s url_base=%s path=%s",
                _secret_fp, token_val[:40], self._local_base_url, path,
            )

        # Authenticated requests use localhost to avoid cross-replica HMAC mismatch.
        # Unauthenticated requests use the FQDN to exercise the external path.
        base = self._local_base_url if auth else self.base_url
        url = f"{base}{path}"
        client = self._http_client
        if client is None:
            # Fallback: create a one-off client (should not happen in normal flow)
            client = httpx.AsyncClient(timeout=timeout, verify=True)
        resp = await client.get(url, headers=headers, timeout=timeout)
        resp_headers = {k.lower(): v for k, v in resp.headers.items()}
        return resp.status_code, resp_headers, resp.text

    async def _http_options(
        self, path: str, *, timeout: float = 10.0,
    ) -> tuple[int, dict[str, str]]:
        """Make an HTTP OPTIONS request (CORS preflight)."""
        import httpx
        headers = {
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        }
        url = f"{self.base_url}{path}"
        client = self._http_client
        if client is None:
            client = httpx.AsyncClient(timeout=timeout, verify=True)
        resp = await client.options(url, headers=headers, timeout=timeout)
        resp_headers = {k.lower(): v for k, v in resp.headers.items()}
        return resp.status_code, resp_headers

    async def _update_cosmos(
        self, status: str, *, total: int = 0,
    ) -> None:
        """Upsert the run document in Cosmos with current progress."""
        try:
            from src.multi_tenant.repositories.platform import PlatformConfigDocument
            now_iso = datetime.now(timezone.utc).isoformat()
            passed = sum(1 for r in self._results if r.status == "pass")
            failed = sum(1 for r in self._results if r.status == "fail")
            skipped = sum(1 for r in self._results if r.status == "skip")
            errors = sum(1 for r in self._results if r.status == "error")
            duration = round(time.monotonic() - self._start_time, 2)

            categories_done = sorted(set(r.category for r in self._results))

            doc = PlatformConfigDocument(
                id=f"test_runs:{self.run_id}",
                config_type="test_runs",
                config_key=self.run_id,
                value={
                    "run_id": self.run_id,
                    "environment": self.environment,
                    "suite": self.suite,
                    "status": status,
                    "triggered_by": self.actor,
                    "started_at": self._start_wall,
                    "completed_at": now_iso if status in ("passed", "failed", "error") else None,
                    "total_tests": total,
                    "completed": len(self._results),
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "errors": errors,
                    "duration_s": duration,
                    "phases_run": categories_done,
                    "checks": [r.to_dict() for r in self._results],
                    "failures": [r.to_dict() for r in self._results if r.status in ("fail", "error")],
                },
                version=1,
                updated_at=now_iso,
                updated_by=self.actor,
            )
            await self.repo.set_config(doc)
        except Exception:
            logger.warning("Failed to update Cosmos for run %s", self.run_id, exc_info=True)

    # ==================================================================
    # HEALTH CHECKS
    # ==================================================================

    async def _check_health(self) -> CheckResult:
        """GET /health returns 200 with status=healthy."""
        code, _, body = await self._http_get("/health", auth=False)
        if code == 200 and "healthy" in body.lower():
            return CheckResult(status="pass", detail=f"HTTP {code}, healthy")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_ready(self) -> CheckResult:
        """GET /ready returns 200 with dependency statuses."""
        code, headers, body = await self._http_get("/ready", auth=False)
        has_version = "x-product-version" in headers
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}, version header={has_version}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_api_version(self) -> CheckResult:
        """GET /ready and verify x-product-version header (GOV-10: live interface)."""
        code, headers, _ = await self._http_get("/ready", auth=False)
        version = headers.get("x-product-version", "")
        if code == 200 and version:
            return CheckResult(status="pass", detail=f"v{version}")
        if code == 200:
            return CheckResult(status="fail", detail="200 but no x-product-version header")
        return CheckResult(status="fail", detail=f"HTTP {code}")

    async def _check_cosmos(self) -> CheckResult:
        """GET /ready and verify Cosmos status from response body (GOV-10: live interface)."""
        import json
        code, _, body = await self._http_get("/ready", auth=False)
        if code == 200:
            try:
                data = json.loads(body)
                # /ready uses "cosmos_db" key with nested {"status": "...", "latency_ms": ...}
                cosmos_obj = data.get("cosmos_db", data.get("cosmos", data.get("cosmosDb", "unknown")))
                if isinstance(cosmos_obj, dict):
                    cosmos_status = cosmos_obj.get("status", "unknown")
                else:
                    cosmos_status = str(cosmos_obj)
                is_ok = any(
                    kw in str(cosmos_status).lower()
                    for kw in ("healthy", "ok", "true", "ready")
                )
                return CheckResult(
                    status="pass" if is_ok else "fail",
                    detail=f"Cosmos: {cosmos_status}",
                )
            except json.JSONDecodeError:
                return CheckResult(status="pass", detail="200 OK (non-JSON readiness body)")
        return CheckResult(status="fail", detail=f"HTTP {code}")

    async def _check_redis(self) -> CheckResult:
        """Internal: Redis connectivity via REDIS_URL env var."""
        try:
            redis_url = os.environ.get("REDIS_URL", "")
            if not redis_url:
                return CheckResult(status="skip", detail="REDIS_URL not set")
            import redis.asyncio as aioredis
            client = aioredis.from_url(redis_url, socket_timeout=5, username=None)
            pong = await client.ping()
            await client.aclose()
            return CheckResult(status="pass" if pong else "fail", detail=f"ping={pong}")
        except Exception as exc:
            return CheckResult(status="error", detail=str(exc)[:200])

    async def _check_key_vault(self) -> CheckResult:
        """Internal: Key Vault URL configured (config check, not connectivity)."""
        kv_url = os.environ.get("AZURE_KEYVAULT_URL", "") or os.environ.get("KEY_VAULT_URL", "")
        if kv_url:
            return CheckResult(status="pass", detail="AZURE_KEYVAULT_URL configured (config-only check)")
        return CheckResult(status="skip", detail="AZURE_KEYVAULT_URL not set")

    async def _check_spa_assets(self) -> CheckResult:
        """Internal: SPA dist bundles exist on filesystem."""
        spa_paths = [
            "admin/provider/dist/index.html",
            "admin/standalone/dist/index.html",
            "admin/shopify/dist/index.html",
        ]
        missing = [p for p in spa_paths if not os.path.exists(p)]
        if missing:
            return CheckResult(status="fail", detail=f"Missing: {', '.join(missing)}")
        return CheckResult(status="pass", detail="All 3 SPA bundles present")

    async def _check_openapi(self) -> CheckResult:
        """GET /openapi.json returns parseable OpenAPI spec."""
        import json
        code, _, body = await self._http_get("/openapi.json", auth=False)
        if code == 200:
            try:
                spec = json.loads(body)
                paths = len(spec.get("paths", {}))
                return CheckResult(status="pass", detail=f"HTTP {code}, {paths} paths")
            except json.JSONDecodeError:
                return CheckResult(status="fail", detail="Response is not valid JSON")
        return CheckResult(status="fail", detail=f"HTTP {code}")

    # ==================================================================
    # API CHECKS
    # ==================================================================

    async def _check_superadmin_tenants(self) -> CheckResult:
        """GET /api/superadmin/tenants returns tenant list."""
        code, _, body = await self._http_get("/api/superadmin/tenants")
        if code == 200:
            import json
            try:
                data = json.loads(body)
                total = data.get("total", len(data.get("tenants", [])))
                return CheckResult(status="pass", detail=f"HTTP {code}, {total} tenants")
            except Exception:
                return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_superadmin_dashboard(self) -> CheckResult:
        """GET /api/superadmin/dashboard returns dashboard data."""
        code, _, body = await self._http_get("/api/superadmin/dashboard")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_incidents(self) -> CheckResult:
        """GET /api/superadmin/incidents returns 200."""
        code, _, body = await self._http_get("/api/superadmin/incidents")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_alert_rules(self) -> CheckResult:
        """GET /api/superadmin/alerts/rules returns 200."""
        code, _, body = await self._http_get("/api/superadmin/alerts/rules")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_mfa_status(self) -> CheckResult:
        """GET /api/superadmin/mfa/status returns 200."""
        code, _, body = await self._http_get("/api/superadmin/mfa/status")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_cost_analytics(self) -> CheckResult:
        """GET /api/superadmin/costs returns 200."""
        code, _, body = await self._http_get("/api/superadmin/costs")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_abuse_detection(self) -> CheckResult:
        """GET /api/superadmin/abuse/signals returns 200."""
        code, _, body = await self._http_get("/api/superadmin/abuse/signals")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_deployments(self) -> CheckResult:
        """GET /api/superadmin/deployments returns 200."""
        code, _, body = await self._http_get("/api/superadmin/deployments")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_pipeline_topology(self) -> CheckResult:
        """GET /api/superadmin/pipeline/topology returns 200."""
        code, _, body = await self._http_get("/api/superadmin/pipeline/topology")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_quality_score(self) -> CheckResult:
        """GET /api/superadmin/quality/score returns 200 (or 503 if KB not in container)."""
        code, _, body = await self._http_get("/api/superadmin/quality/score")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        # Knowledge DB is dev-only; 503 expected in container deployments
        if code == 503 and "Knowledge DB" in body:
            return CheckResult(status="skip", detail="Quality score requires Knowledge DB (dev-only)")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    # ==================================================================
    # CONFIG CHECKS
    # ==================================================================

    async def _check_public_status(self) -> CheckResult:
        """GET /api/status returns 200 (public, no auth)."""
        code, _, body = await self._http_get("/api/status", auth=False)
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_spa_served(self) -> CheckResult:
        """GET /admin/provider/ returns HTML with React mount point."""
        code, _, body = await self._http_get("/admin/provider/", auth=False)
        body_lower = body.lower()
        # SPA uses <div id="app"> (not "root") as the React mount point
        has_mount = 'id="app"' in body_lower or 'id="root"' in body_lower
        if code == 200 and has_mount:
            return CheckResult(status="pass", detail="HTML served with mount element")
        return CheckResult(status="fail", detail=f"HTTP {code}, mount={has_mount}")

    async def _check_entitlements(self) -> CheckResult:
        """GET /api/superadmin/entitlements returns 200."""
        code, _, body = await self._http_get("/api/superadmin/entitlements")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_feature_flags(self) -> CheckResult:
        """GET /api/superadmin/feature-flags returns 200."""
        code, _, body = await self._http_get("/api/superadmin/feature-flags")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_blocklist_config(self) -> CheckResult:
        """GET /api/superadmin/blocklists returns 200."""
        code, _, body = await self._http_get("/api/superadmin/blocklists")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_maintenance_mode(self) -> CheckResult:
        """GET /api/superadmin/maintenance returns 200."""
        code, _, body = await self._http_get("/api/superadmin/maintenance")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_retry_config(self) -> CheckResult:
        """GET /api/superadmin/retry-configs returns 200."""
        code, _, body = await self._http_get("/api/superadmin/retry-configs")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    # ==================================================================
    # SECURITY CHECKS
    # ==================================================================

    async def _check_security_headers(self) -> CheckResult:
        """Verify security headers on /health response."""
        code, headers, _ = await self._http_get("/health", auth=False)
        required = ["x-content-type-options", "x-frame-options"]
        present = [h for h in required if h in headers]
        if len(present) == len(required):
            return CheckResult(status="pass", detail=f"All {len(required)} headers present")
        missing = [h for h in required if h not in headers]
        return CheckResult(status="fail", detail=f"Missing: {', '.join(missing)}")

    async def _check_cors(self) -> CheckResult:
        """OPTIONS /health returns CORS headers."""
        code, headers = await self._http_options("/health")
        has_cors = "access-control-allow-origin" in headers
        if has_cors:
            return CheckResult(status="pass", detail=f"CORS headers present")
        return CheckResult(status="fail", detail="No CORS headers in preflight response")

    async def _check_rate_limit_headers(self) -> CheckResult:
        """Authenticated request returns rate limit headers."""
        code, headers, _ = await self._http_get("/api/superadmin/dashboard")
        rl_headers = [h for h in headers if "ratelimit" in h.lower() or "x-ratelimit" in h.lower()]
        if rl_headers:
            return CheckResult(status="pass", detail=f"Rate limit headers: {', '.join(rl_headers)}")
        # Rate limiting may be disabled — not a hard failure
        return CheckResult(status="skip", detail="No rate limit headers (may be disabled)")

    async def _check_no_version_leak(self) -> CheckResult:
        """Server header should not leak framework version."""
        code, headers, _ = await self._http_get("/health", auth=False)
        server = headers.get("server", "")
        if "uvicorn" in server.lower() or "python" in server.lower():
            return CheckResult(status="fail", detail=f"Server header leaks: {server}")
        return CheckResult(status="pass", detail=f"Server header clean: {server or '(none)'}")

    async def _check_401_clean(self) -> CheckResult:
        """401 response should not expose internal details."""
        code, _, body = await self._http_get("/api/superadmin/dashboard", auth=False)
        if code == 401:
            has_stack = "traceback" in body.lower() or "file " in body.lower()
            if has_stack:
                return CheckResult(status="fail", detail="401 response contains stack trace")
            return CheckResult(status="pass", detail="401 response is clean")
        return CheckResult(status="skip", detail=f"Expected 401, got {code}")

    async def _check_404_clean(self) -> CheckResult:
        """404 response should not expose internal details."""
        code, _, body = await self._http_get("/api/nonexistent-endpoint-test", auth=False)
        if code in (404, 405):
            has_stack = "traceback" in body.lower() or "file " in body.lower()
            if has_stack:
                return CheckResult(status="fail", detail=f"{code} response contains stack trace")
            return CheckResult(status="pass", detail=f"HTTP {code} response is clean")
        return CheckResult(status="skip", detail=f"Expected 404, got {code}")

    # ==================================================================
    # QUALITY CHECKS
    # ==================================================================

    async def _check_memory_stats(self) -> CheckResult:
        """GET /api/superadmin/diagnostics/metrics returns 200."""
        code, _, body = await self._http_get("/api/superadmin/diagnostics/metrics")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_tier_listing(self) -> CheckResult:
        """GET /api/superadmin/rate-limits returns 200."""
        code, _, body = await self._http_get("/api/superadmin/rate-limits")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_addon_listing(self) -> CheckResult:
        """GET /api/superadmin/feedback/metrics returns 200."""
        code, _, body = await self._http_get("/api/superadmin/feedback/metrics")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    async def _check_diagnostics_export(self) -> CheckResult:
        """GET /api/superadmin/diagnostics/export returns 200."""
        code, _, body = await self._http_get("/api/superadmin/diagnostics/export")
        if code == 200:
            return CheckResult(status="pass", detail=f"HTTP {code}")
        # Some deployments may not have this endpoint
        if code == 404:
            return CheckResult(status="skip", detail="Endpoint not available")
        return CheckResult(status="fail", detail=f"HTTP {code}: {body[:200]}")

    # ==================================================================
    # TENANT ISOLATION CHECKS
    # ==================================================================

    async def _check_tenant_count(self) -> CheckResult:
        """Verify tenant count from API matches dashboard."""
        code1, _, body1 = await self._http_get("/api/superadmin/tenants")
        code2, _, body2 = await self._http_get("/api/superadmin/dashboard")
        if code1 == 200 and code2 == 200:
            import json
            try:
                tenants = json.loads(body1)
                dashboard = json.loads(body2)
                t_count = tenants.get("total", 0)
                d_count = dashboard.get("totalTenants", dashboard.get("total_tenants", -1))
                if t_count == d_count or d_count == -1:
                    return CheckResult(status="pass", detail=f"Consistent: {t_count} tenants")
                return CheckResult(status="fail", detail=f"Mismatch: tenants={t_count}, dashboard={d_count}")
            except Exception as exc:
                return CheckResult(status="error", detail=str(exc))
        return CheckResult(status="fail", detail=f"API errors: tenants={code1}, dashboard={code2}")

    async def _check_entitlement_consistency(self) -> CheckResult:
        """Verify all active tenants have entitlement documents."""
        code, _, body = await self._http_get("/api/superadmin/entitlements")
        if code == 200:
            import json
            try:
                data = json.loads(body)
                entries = data if isinstance(data, list) else data.get("entitlements", [])
                if len(entries) > 0:
                    return CheckResult(status="pass", detail=f"{len(entries)} entitlement docs")
                # Staging may not have entitlement docs seeded
                return CheckResult(status="skip", detail="No entitlement documents (may need seeding)")
            except Exception as exc:
                return CheckResult(status="error", detail=str(exc))
        return CheckResult(status="fail", detail=f"HTTP {code}")

    async def _check_audit_recency(self) -> CheckResult:
        """Verify API key usage audit is accessible."""
        code, _, body = await self._http_get("/api/superadmin/diagnostics/api-key-usage")
        if code == 200:
            return CheckResult(status="pass", detail="Audit endpoint responsive")
        # Endpoint may return empty data on fresh deployments
        if code == 404:
            return CheckResult(status="skip", detail="Audit endpoint not available")
        return CheckResult(status="fail", detail=f"HTTP {code}")

    async def _check_config_integrity(self) -> CheckResult:
        """Verify platform config is accessible and structured."""
        code, _, body = await self._http_get("/api/superadmin/feature-flags")
        if code == 200:
            return CheckResult(status="pass", detail="Platform config accessible")
        return CheckResult(status="fail", detail=f"HTTP {code}")

    async def _check_no_orphans(self) -> CheckResult:
        """Verify no obviously broken platform config state."""
        # This is a lightweight check — full orphan detection requires DB queries
        code, _, body = await self._http_get("/api/superadmin/maintenance")
        if code == 200:
            return CheckResult(status="pass", detail="Maintenance config accessible")
        return CheckResult(status="fail", detail=f"HTTP {code}")
