"""MCP client for external tool server integration (AGNTCY Phase 3).

All MCP connections route through ``AgntcyFactory.create_client("MCP", ...)``
via ``create_mcp_client()`` in ``agntcy_sdk_integration.py`` (SPEC-1534).
No direct ``mcp`` SDK imports for client/session creation.

Wraps the AGNTCY MCP client with Agent Red conventions: per-tenant isolation,
shop_domain validation, PII scrubbing, circuit breaker, read-only policy gate,
timeout enforcement, and decision tracing.

Phase 3A scope: Shopify Storefront MCP (zero-auth, read-only, HTTP JSON-RPC 2.0).
Phase 3B scope: Stripe MCP (authenticated, read-only, HTTP remote at mcp.stripe.com).

Usage via AGNTCY factory::

    from src.multi_tenant.agntcy_sdk_integration import create_mcp_client

    mcp_cm = create_mcp_client(
        agent_topic="shopify-storefront",
        server_url="https://mcp.shopify.com",
        timeout_s=3.0,
    )
    async with mcp_cm as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("search_products", {"query": "..."})

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Tool classification prefixes
READ_PREFIXES = (
    "get_", "list_", "search_", "read_", "query_",
    "find_", "fetch_", "lookup_",
)
MUTATE_PREFIXES = (
    "create_", "update_", "delete_", "modify_", "set_",
    "add_", "remove_", "cancel_", "refund_",
)

# Default classification by server type (fail-safe: unknown = mutate)
SERVER_TYPE_DEFAULTS: dict[str, str] = {
    "shopify-storefront": "read",
    "shopify-customer-account": "mutate",
    "stripe": "mutate",
    "custom": "mutate",
}

# Default timeout for MCP tool calls (milliseconds)
DEFAULT_MCP_TIMEOUT_MS = 3_000


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class McpToolBlockedError(Exception):
    """Raised when a tool invocation is blocked by the read-only policy gate."""

    def __init__(self, tool_name: str, reason: str) -> None:
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(f"MCP tool '{tool_name}' blocked: {reason}")


class McpTimeoutError(Exception):
    """Raised when an MCP tool call exceeds its timeout budget."""

    def __init__(self, tool_name: str, timeout_ms: int, elapsed_ms: float) -> None:
        self.tool_name = tool_name
        self.timeout_ms = timeout_ms
        self.elapsed_ms = elapsed_ms
        super().__init__(
            f"MCP tool '{tool_name}' timed out: {elapsed_ms:.0f}ms > {timeout_ms}ms"
        )


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class McpServerConfig:
    """Configuration for a single MCP server registered to a tenant."""

    server_name: str
    server_url: str
    server_type: str = "custom"
    enabled: bool = True
    read_only: bool = True
    shop_domain: str | None = None
    tool_allowlist: list[str] = field(default_factory=list)
    timeout_ms: int = DEFAULT_MCP_TIMEOUT_MS
    credential_ref: str | None = None  # TenantSecretType value for auth lookup


@dataclass
class McpToolResult:
    """Result from invoking an MCP tool, enriched with tracing metadata."""

    tool_name: str
    content: list[dict[str, Any]]
    is_error: bool
    elapsed_ms: float
    server_name: str


@dataclass
class McpQueryResult:
    """Aggregated result from querying one or more MCP servers."""

    results: list[McpToolResult]
    context_text: str
    sources: list[dict[str, Any]]
    trace: dict[str, Any]
    total_elapsed_ms: float


# ---------------------------------------------------------------------------
# Shop domain validation
# ---------------------------------------------------------------------------


def validate_shop_domain(server_url: str, expected_domain: str) -> bool:
    """Validate that an MCP server URL matches the tenant's registered Shopify domain.

    Both hostnames must be ``*.myshopify.com``.  Comparison is case-insensitive.

    Args:
        server_url: The MCP server endpoint URL.
        expected_domain: The tenant's myshopify.com domain.

    Returns:
        ``True`` if the URL host matches the expected domain.
    """
    try:
        parsed = urlparse(server_url)
        url_host = (parsed.hostname or "").lower()
    except Exception:
        return False

    expected = expected_domain.lower()

    if not url_host.endswith(".myshopify.com"):
        return False
    if not expected.endswith(".myshopify.com"):
        return False

    return url_host == expected


# ---------------------------------------------------------------------------
# Tool classification + policy gate
# ---------------------------------------------------------------------------


def classify_tool(tool_name: str, server_type: str) -> str:
    """Classify a tool as ``"read"`` or ``"mutate"``.

    1. Check tool name prefixes.
    2. Fall back to server-type defaults.

    Args:
        tool_name: The MCP tool name.
        server_type: The server type (e.g. ``"shopify-storefront"``).

    Returns:
        ``"read"`` or ``"mutate"``.
    """
    name_lower = tool_name.lower()
    if any(name_lower.startswith(p) for p in READ_PREFIXES):
        return "read"
    if any(name_lower.startswith(p) for p in MUTATE_PREFIXES):
        return "mutate"
    return SERVER_TYPE_DEFAULTS.get(server_type, "mutate")


def is_tool_allowed(
    tool_name: str,
    server_type: str,
    read_only: bool,
    tool_allowlist: list[str],
) -> bool:
    """Check whether a tool invocation is permitted by the tenant's policy.

    Returns ``True`` if the tool passes both the classification gate and the
    allowlist filter.

    Args:
        tool_name: The MCP tool name.
        server_type: The server type string.
        read_only: Whether the server is in read-only mode.
        tool_allowlist: Explicit allowlist (empty = allow all passing tools).

    Returns:
        ``True`` if allowed.
    """
    classification = classify_tool(tool_name, server_type)

    # Read-only gate: block mutations on read-only servers
    if read_only and classification == "mutate":
        return False

    # Allowlist gate: if non-empty, only allow listed tools
    if tool_allowlist and tool_name not in tool_allowlist:
        return False

    return True


# ---------------------------------------------------------------------------
# MCP client
# ---------------------------------------------------------------------------


class AgentRedMcpClient:
    """Per-request MCP client for invoking tools on a single MCP server.

    Short-lived: created per KR invocation, not pooled across requests.

    Args:
        config: MCP server configuration.
        circuit_breaker: Circuit breaker instance for this server type.
        pii_scrubber: Optional PII scrubber for outbound queries.
    """

    def __init__(
        self,
        config: McpServerConfig,
        circuit_breaker: Any = None,
        pii_scrubber: Any = None,
    ) -> None:
        self._config = config
        self._breaker = circuit_breaker
        self._pii_scrubber = pii_scrubber
        self._session: Any = None
        self._read_stream: Any = None
        self._write_stream: Any = None
        self._cm_stack: Any = None
        self._available_tools: list[dict[str, Any]] = []

    @property
    def available_tools(self) -> list[dict[str, Any]]:
        """Return the list of tools discovered during ``connect()``."""
        return list(self._available_tools)

    async def connect(self, auth_headers: dict[str, str] | None = None) -> None:
        """Establish MCP session via AgntcyFactory and discover tools (SPEC-1534).

        All MCP connections route through ``create_mcp_client()`` from
        ``agntcy_sdk_integration.py``, which wraps
        ``AgntcyFactory.create_client("MCP", ...)``.  No direct ``mcp`` SDK
        imports for client/session creation.

        Args:
            auth_headers: Optional HTTP headers for authenticated servers
                (e.g. ``{"Authorization": "Bearer sk_..."}`` for Stripe MCP).

        Raises:
            RuntimeError: If connection fails.
        """
        import contextlib

        from src.multi_tenant.agntcy_sdk_integration import create_mcp_client

        timeout_s = self._config.timeout_ms / 1000

        # Create MCP client via AgntcyFactory (SPEC-1534)
        mcp_client_cm = create_mcp_client(
            agent_topic=self._config.server_name,
            server_url=self._config.server_url,
            timeout_s=timeout_s,
            auth_headers=auth_headers,
        )

        # Enter the factory-provided context manager
        self._cm_stack = contextlib.AsyncExitStack()
        self._session = await self._cm_stack.enter_async_context(mcp_client_cm)
        await self._session.initialize()

        # Discover available tools
        tools_result = await self._session.list_tools()
        self._available_tools = [
            {
                "name": t.name,
                "description": getattr(t, "description", None) or "",
                "input_schema": (
                    t.inputSchema.model_dump()
                    if hasattr(t.inputSchema, "model_dump")
                    else t.inputSchema
                ) if t.inputSchema else {},
            }
            for t in (tools_result.tools or [])
        ]
        logger.info(
            "MCP connected to %s: %d tools available (via AgntcyFactory)",
            self._config.server_name,
            len(self._available_tools),
        )

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> McpToolResult:
        """Invoke a single MCP tool with policy gate, PII scrubbing, and timeout.

        Args:
            tool_name: The tool to invoke.
            arguments: Tool arguments dict.

        Returns:
            ``McpToolResult`` with content and tracing metadata.

        Raises:
            McpToolBlockedError: If the tool is classified as mutating on a
                read-only server, or not in the allowlist.
            McpTimeoutError: If the call exceeds ``config.timeout_ms``.
            RuntimeError: If circuit breaker is open or session not connected.
        """
        import asyncio

        # 1. Policy gate
        if not is_tool_allowed(
            tool_name,
            self._config.server_type,
            self._config.read_only,
            self._config.tool_allowlist,
        ):
            classification = classify_tool(tool_name, self._config.server_type)
            if self._config.read_only and classification == "mutate":
                raise McpToolBlockedError(tool_name, "mutation_blocked")
            raise McpToolBlockedError(tool_name, "not_in_allowlist")

        # 2. Circuit breaker check
        if self._breaker and getattr(self._breaker, "is_open", False):
            from src.multi_tenant.pipeline_resilience import ServiceUnavailableError

            raise ServiceUnavailableError(f"mcp-{self._config.server_name}")

        # 3. PII scrub arguments
        scrubbed_args = arguments or {}
        if self._pii_scrubber and scrubbed_args:
            scrubbed_args = dict(scrubbed_args)
            for key, value in scrubbed_args.items():
                if isinstance(value, str):
                    scrubbed_args[key] = self._pii_scrubber.scrub_text(value)

        # 4. Call with timeout
        if not self._session:
            raise RuntimeError("MCP client not connected — call connect() first")

        start = time.monotonic()
        timeout_s = self._config.timeout_ms / 1000

        try:
            result = await asyncio.wait_for(
                self._session.call_tool(tool_name, scrubbed_args),
                timeout=timeout_s,
            )
            elapsed_ms = (time.monotonic() - start) * 1000

            # 5. Record success on breaker
            if self._breaker:
                self._breaker.record_success()

            # 6. Extract content
            content_list: list[dict[str, Any]] = []
            for item in (result.content or []):
                if hasattr(item, "text"):
                    content_list.append({"type": "text", "text": item.text})
                elif hasattr(item, "data"):
                    content_list.append({
                        "type": "image",
                        "data": item.data,
                        "mimeType": getattr(item, "mimeType", ""),
                    })
                else:
                    content_list.append({"type": "unknown", "raw": str(item)})

            return McpToolResult(
                tool_name=tool_name,
                content=content_list,
                is_error=bool(getattr(result, "isError", False)),
                elapsed_ms=round(elapsed_ms, 1),
                server_name=self._config.server_name,
            )

        except asyncio.TimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            if self._breaker:
                self._breaker.record_failure()
            raise McpTimeoutError(tool_name, self._config.timeout_ms, elapsed_ms)

        except McpTimeoutError:
            raise

        except Exception:
            if self._breaker:
                self._breaker.record_failure()
            raise

    async def close(self) -> None:
        """Close the HTTP session and release resources."""
        if self._cm_stack:
            try:
                await self._cm_stack.aclose()
            except Exception:
                logger.debug("Error closing MCP client", exc_info=True)
        self._session = None
        self._read_stream = None
        self._write_stream = None
        self._cm_stack = None


# ---------------------------------------------------------------------------
# Config builders and resolvers
# ---------------------------------------------------------------------------


def build_storefront_mcp_config(shop_domain: str) -> dict[str, Any]:
    """Build a default Shopify Storefront MCP server configuration dict.

    Args:
        shop_domain: The tenant's ``myshopify.com`` domain
            (e.g. ``"blanco-9939.myshopify.com"``).

    Returns:
        Dict matching ``McpServerConfig`` schema.
    """
    return {
        "server_name": "shopify-storefront",
        "server_url": f"https://{shop_domain}/api/mcp",
        "server_type": "shopify-storefront",
        "enabled": True,
        "read_only": True,
        "shop_domain": shop_domain,
        "tool_allowlist": [],
        "timeout_ms": DEFAULT_MCP_TIMEOUT_MS,
    }


def build_stripe_mcp_config() -> dict[str, Any]:
    """Build a default Stripe MCP server configuration dict.

    Stripe MCP is authenticated (Bearer token) and read-only for Cycle 5.
    The ``credential_ref`` links to ``TenantSecretType.STRIPE_API_KEY``
    for Key Vault credential lookup.

    Returns:
        Dict matching ``McpServerConfig`` schema.
    """
    return {
        "server_name": "stripe",
        "server_url": "https://mcp.stripe.com",
        "server_type": "stripe",
        "enabled": True,
        "read_only": True,  # LOCKED for Cycle 5
        "tool_allowlist": [],
        "timeout_ms": 5_000,  # Stripe is slower than Shopify Storefront
        "credential_ref": "stripe-api-key",
    }


def parse_mcp_server_config(raw: dict[str, Any]) -> McpServerConfig | None:
    """Parse a raw dict into a validated ``McpServerConfig``.

    Returns ``None`` if the dict is missing required fields or invalid.
    """
    try:
        server_name = raw.get("server_name")
        server_url = raw.get("server_url")
        if not server_name or not server_url:
            return None

        return McpServerConfig(
            server_name=str(server_name),
            server_url=str(server_url),
            server_type=str(raw.get("server_type", "custom")),
            enabled=bool(raw.get("enabled", True)),
            read_only=bool(raw.get("read_only", True)),
            shop_domain=raw.get("shop_domain"),
            tool_allowlist=list(raw.get("tool_allowlist", [])),
            timeout_ms=int(raw.get("timeout_ms", DEFAULT_MCP_TIMEOUT_MS)),
            credential_ref=raw.get("credential_ref"),
        )
    except (TypeError, ValueError) as exc:
        logger.warning("Invalid MCP server config: %s — %s", raw, exc)
        return None


def parse_mcp_server_configs(raw_list: list[dict[str, Any]]) -> list[McpServerConfig]:
    """Parse a list of raw dicts into validated ``McpServerConfig`` objects.

    Tolerant: skips entries that fail validation (logs warning).
    Returns only valid, enabled configs.
    """
    configs: list[McpServerConfig] = []
    for raw in raw_list:
        cfg = parse_mcp_server_config(raw)
        if cfg and cfg.enabled:
            configs.append(cfg)
    return configs


def resolve_mcp_configs(
    preferences: Any,
    tenant: Any,
) -> list[McpServerConfig]:
    """Resolve effective MCP server configurations for a tenant.

    Priority:
    1. If ``preferences.mcp_servers`` is non-empty and ``mcp_enabled`` is
       ``True``, parse and return those configs.
    2. If ``preferences.mcp_servers`` is empty BUT the tenant has
       ``shopify_integration_status == "connected"`` and ``shopify_shop_domain``
       is set, auto-generate a Storefront MCP config.
    3. Otherwise return empty list (no MCP augmentation).

    Args:
        preferences: ``PreferencesDocument`` or similar object with
            ``mcp_servers``, ``mcp_enabled``, ``shopify_integration_status``.
        tenant: ``TenantDocument`` or similar object with
            ``shopify_shop_domain``.

    Returns:
        List of validated, enabled ``McpServerConfig`` objects.
    """
    mcp_enabled = getattr(preferences, "mcp_enabled", False)
    mcp_servers = getattr(preferences, "mcp_servers", None) or []

    # Path 1: Explicit MCP configuration
    if mcp_servers and mcp_enabled:
        return parse_mcp_server_configs(mcp_servers)

    # Path 2: Auto-populate for connected integrations
    configs: list[McpServerConfig] = []

    # Path 2a: Auto-populate Shopify Storefront if connected
    shop_status = getattr(preferences, "shopify_integration_status", None)
    shop_domain = getattr(tenant, "shopify_shop_domain", None)

    if shop_status == "connected" and shop_domain:
        raw = build_storefront_mcp_config(shop_domain)
        cfg = parse_mcp_server_config(raw)
        if cfg:
            configs.append(cfg)

    # Path 2b: Auto-populate Stripe MCP if connected
    stripe_mcp_status = getattr(preferences, "stripe_mcp_status", None)
    stripe_mcp_enabled = getattr(preferences, "stripe_mcp_enabled", False)

    if stripe_mcp_status == "connected" and stripe_mcp_enabled:
        raw = build_stripe_mcp_config()
        cfg = parse_mcp_server_config(raw)
        if cfg:
            configs.append(cfg)

    if configs:
        return configs

    # Path 3: No MCP augmentation
    return []


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


async def create_tenant_mcp_client(
    config: McpServerConfig,
    tenant_id: str | None = None,
    tenant_shop_domain: str | None = None,
    pii_scrubber: Any = None,
    credential_cache: Any = None,
) -> AgentRedMcpClient:
    """Create an MCP client for a tenant's server configuration.

    Validates shop_domain for Shopify servers, resolves credentials for
    authenticated servers (via credential cache), and resolves the circuit
    breaker from the global registry.

    Args:
        config: MCP server configuration.
        tenant_id: The tenant identifier (required for credential resolution).
        tenant_shop_domain: The tenant's registered Shopify domain (for guard).
        pii_scrubber: Optional ``PiiScrubber`` instance.
        credential_cache: Optional ``McpCredentialCache`` for credential lookup.

    Returns:
        ``AgentRedMcpClient`` ready for ``connect()``.

    Raises:
        ValueError: If shop_domain validation fails.
    """
    # Shop domain guard for Shopify servers
    if config.server_type == "shopify-storefront" and tenant_shop_domain:
        if not validate_shop_domain(config.server_url, tenant_shop_domain):
            raise ValueError(
                f"MCP server URL {config.server_url} does not match "
                f"tenant domain {tenant_shop_domain}"
            )

    # Resolve circuit breaker
    breaker = None
    try:
        from src.multi_tenant.pipeline_resilience import get_circuit_breaker

        breaker = get_circuit_breaker(f"mcp-{config.server_type}")
    except Exception:
        logger.debug("No circuit breaker for mcp-%s", config.server_type)

    # Resolve credential for authenticated servers
    auth_headers: dict[str, str] | None = None
    if config.credential_ref and tenant_id:
        api_key = await _resolve_credential(
            tenant_id, config.credential_ref, credential_cache
        )
        if api_key:
            auth_headers = {"Authorization": f"Bearer {api_key}"}
        else:
            logger.warning(
                "No credential found for tenant=%s ref=%s — "
                "connecting without auth",
                tenant_id, config.credential_ref,
            )

    client = AgentRedMcpClient(
        config=config,
        circuit_breaker=breaker,
        pii_scrubber=pii_scrubber,
    )
    client._auth_headers = auth_headers  # Stored for connect()
    return client


async def _resolve_credential(
    tenant_id: str,
    credential_ref: str,
    credential_cache: Any = None,
) -> str | None:
    """Resolve a credential from cache (preferred) or directly from Key Vault.

    Args:
        tenant_id: The tenant identifier.
        credential_ref: The secret type string (e.g. ``"stripe-api-key"``).
        credential_cache: Optional ``McpCredentialCache`` instance.

    Returns:
        The credential string, or ``None`` if not found.
    """
    try:
        from src.multi_tenant.tenant_secret_service import (
            TenantSecretType,
            get_secret_service,
        )

        # Map credential_ref string to TenantSecretType enum
        secret_type = None
        for st in TenantSecretType:
            if st.value == credential_ref:
                secret_type = st
                break

        if secret_type is None:
            logger.warning(
                "Unknown credential_ref: %s", credential_ref,
            )
            return None

        svc = get_secret_service()

        if credential_cache is not None:
            # Use cache with fetcher
            async def _fetcher() -> str | None:
                await svc.initialize()
                return await svc.get_secret(tenant_id, secret_type)

            return await credential_cache.get(
                tenant_id, credential_ref, _fetcher,
            )
        else:
            # Direct fetch (no cache)
            await svc.initialize()
            return await svc.get_secret(tenant_id, secret_type)

    except Exception as exc:
        logger.warning(
            "Credential resolution failed: tenant=%s ref=%s error=%s",
            tenant_id, credential_ref, exc,
        )
        return None
