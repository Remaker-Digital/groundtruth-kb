"""MCP Agent Plug-in Dispatch (SPEC-1706).

Dispatches tool invocations to plug-in agents via MCP protocol.
Handles both internal domain agents (HTTP containers) and external
3rd-party MCP servers.  Integrates with the credential vault for
authenticated external connections.

The dispatch layer is called by the orchestrator when the LLM
selects a plug-in agent tool during the tool-use pattern.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from src.agents.plugins.registry import PluginAgentDefinition, PluginAgentRegistry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT_MS = 5_000
MAX_TIMEOUT_MS = 30_000


# ---------------------------------------------------------------------------
# Dispatch result
# ---------------------------------------------------------------------------


@dataclass
class PluginDispatchResult:
    """Result from dispatching a tool call to a plug-in agent."""

    tool_name: str
    agent_id: str
    success: bool
    content: Any = None
    error: str = ""
    elapsed_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


class PluginDispatcher:
    """Dispatches tool invocations to plug-in MCP agents.

    Resolves which agent handles a given tool, then routes the call
    to the agent's endpoint.  External servers use MCP protocol;
    internal agents use HTTP POST with JSON payload.
    """

    def __init__(
        self,
        registry: PluginAgentRegistry | None = None,
        http_client: Any = None,
    ) -> None:
        self._registry = registry or PluginAgentRegistry.get_instance()
        self._http = http_client
        self._call_count = 0
        self._error_count = 0

    async def dispatch(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        tenant_id: str = "",
        conversation_id: str = "",
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        **template_vars: str,
    ) -> PluginDispatchResult:
        """Dispatch a tool call to the appropriate plug-in agent.

        1. Resolve which agent provides the tool
        2. Route to internal (HTTP) or external (MCP) endpoint
        3. Return structured result with timing metadata
        """
        start = time.monotonic()
        self._call_count += 1

        defn = self._registry.resolve_tool_agent(tool_name)
        if defn is None:
            self._error_count += 1
            return PluginDispatchResult(
                tool_name=tool_name,
                agent_id="unknown",
                success=False,
                error=f"No agent registered for tool: {tool_name}",
                elapsed_ms=_elapsed(start),
            )

        try:
            if defn.is_external:
                result = await self._dispatch_external(
                    defn, tool_name, arguments,
                    tenant_id=tenant_id,
                    timeout_ms=timeout_ms,
                    **template_vars,
                )
            else:
                result = await self._dispatch_internal(
                    defn, tool_name, arguments,
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    timeout_ms=timeout_ms,
                    **template_vars,
                )

            return PluginDispatchResult(
                tool_name=tool_name,
                agent_id=defn.agent_id,
                success=True,
                content=result,
                elapsed_ms=_elapsed(start),
                metadata={
                    "endpoint": defn.resolve_endpoint(**template_vars),
                    "is_external": defn.is_external,
                    "category": defn.category,
                },
            )

        except Exception as exc:
            self._error_count += 1
            logger.exception(
                "Plugin dispatch failed: tool=%s agent=%s",
                tool_name,
                defn.agent_id,
            )
            return PluginDispatchResult(
                tool_name=tool_name,
                agent_id=defn.agent_id,
                success=False,
                error=str(exc),
                elapsed_ms=_elapsed(start),
            )

    async def _dispatch_internal(
        self,
        defn: PluginAgentDefinition,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        tenant_id: str = "",
        conversation_id: str = "",
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        **template_vars: str,
    ) -> Any:
        """Dispatch to an internal domain agent via HTTP POST."""
        endpoint = defn.resolve_endpoint(**template_vars)
        # Route to /tools/{tool_name} on the agent's container
        url = f"{endpoint}/tools/{tool_name}"

        payload = {
            "tool_name": tool_name,
            "arguments": arguments,
            "tenant_id": tenant_id,
            "conversation_id": conversation_id,
        }

        headers = {
            "Content-Type": "application/json",
            "X-Tenant-Id": tenant_id,
            "X-Conversation-Id": conversation_id,
        }

        if self._http is not None:
            response = await self._http.post(
                url, json=payload, headers=headers,
                timeout=min(timeout_ms, MAX_TIMEOUT_MS) / 1000,
            )
            return getattr(response, "json", lambda: {})()
        else:
            # No HTTP client — return mock response for dev
            logger.warning(
                "No HTTP client configured — returning mock for %s",
                tool_name,
            )
            return {"mock": True, "tool": tool_name, "agent": defn.agent_id}

    async def _dispatch_external(
        self,
        defn: PluginAgentDefinition,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        tenant_id: str = "",
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        **template_vars: str,
    ) -> Any:
        """Dispatch to an external 3rd-party MCP server.

        Uses the AGNTCY SDK's MCP client via create_mcp_client()
        for authenticated, protocol-compliant tool invocation.
        """
        endpoint = defn.resolve_endpoint(**template_vars)

        # Strip the agent prefix from tool_name for MCP call
        # e.g., "stripe.list_charges" → "list_charges"
        mcp_tool_name = tool_name.split(".", 1)[-1] if "." in tool_name else tool_name

        try:
            from src.multi_tenant.agntcy_sdk_integration import create_mcp_client

            auth_headers = {}
            if defn.credential_env:
                import os
                secret = os.environ.get(defn.credential_env, "")
                if secret:
                    auth_headers["Authorization"] = f"Bearer {secret}"

            mcp_cm = create_mcp_client(
                defn.agent_id,
                server_url=endpoint,
                auth_headers=auth_headers,
            )
            async with mcp_cm as session:
                await session.initialize()
                result = await session.call_tool(mcp_tool_name, arguments)
                return result

        except (ImportError, AttributeError, TypeError):
            logger.warning(
                "AGNTCY SDK not available or incompatible — falling back to HTTP for %s",
                defn.agent_id,
            )
            # HTTP fallback for external servers
            return await self._dispatch_internal(
                defn, tool_name, arguments,
                tenant_id=tenant_id,
                timeout_ms=timeout_ms,
                **template_vars,
            )

    # -- Binding-enforced dispatch (SPEC-1857) --------------------------------

    async def dispatch_with_binding(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        tenant_id: str,
        agent_id: str,
        skill_id: str,
        conversation_id: str = "",
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        **template_vars: str,
    ) -> PluginDispatchResult:
        """Dispatch a tool call with deny-by-default binding enforcement (SPEC-1857).

        1. Check binding for (tenant_id, agent_id, skill_id)
        2. If denied: emit denial event, return denied result
        3. If allowed: resolve credential from binding, dispatch
        """
        start = time.monotonic()
        self._call_count += 1

        from src.agents.plugins.bindings import SkillBindingService
        from src.agents.plugins.events import emit_invocation

        svc = SkillBindingService.get_instance()

        # WI-4014: Hydrate binding cache from Cosmos if not yet loaded
        if tenant_id not in svc._loaded_tenants:
            try:
                await svc.load_tenant_bindings(tenant_id)
            except Exception:
                logger.debug("Binding cache hydration failed in dispatch", exc_info=True)

        # Resolve skill mode from registry for mode enforcement
        skill_defn = self._registry.get_skill(skill_id)
        required_mode = skill_defn.mode if skill_defn else None

        check = svc.check_binding(
            tenant_id, agent_id, skill_id,
            required_mode=required_mode,
        )

        if check.denied:
            # SPEC-1857 req 6: Emit denial event
            emit_invocation(
                trace_id="",
                target_agent_id=agent_id,
                skill_id=skill_id,
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                result_class="denied",
                policy_verdict=check.policy_verdict,
                error_detail=check.reason,
            )
            self._error_count += 1
            return PluginDispatchResult(
                tool_name=tool_name,
                agent_id=agent_id,
                success=False,
                error=check.reason,
                elapsed_ms=_elapsed(start),
                metadata={
                    "policy_verdict": check.policy_verdict,
                    "skill_id": skill_id,
                },
            )

        # Dispatch with binding-resolved credential (SPEC-1858 req 2)
        result = await self.dispatch(
            tool_name,
            arguments,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            timeout_ms=timeout_ms,
            **template_vars,
        )

        # Attach binding metadata to result
        result.metadata["credential_ref"] = check.credential_ref
        result.metadata["skill_id"] = skill_id
        result.metadata["policy_verdict"] = "allowed"

        return result

    def get_bound_tool_catalog(
        self,
        tenant_id: str,
        *,
        tier: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build tool catalog filtered to bound skills only (SPEC-1857 req 5).

        Unbound tools do NOT appear in the catalog.
        """
        from src.agents.plugins.bindings import SkillBindingService
        svc = SkillBindingService.get_instance()
        bound_skills = set(svc.get_bound_skill_ids(tenant_id))

        full_catalog = self._registry.get_tool_catalog(tier=tier)
        filtered: list[dict[str, Any]] = []
        for tool in full_catalog:
            agent_id = tool.get("_agent_id", "")
            func_name = tool.get("function", {}).get("name", "")
            # Check if any skill for this agent+tool is bound
            for skill_id in bound_skills:
                if skill_id.startswith(f"{agent_id}:"):
                    # Check if this tool maps to this skill
                    skill_defn = self._registry.get_skill(skill_id)
                    if skill_defn and func_name in skill_defn.mcp_tool_names:
                        filtered.append(tool)
                        break
        return filtered

    # -- Health checks ------------------------------------------------------

    async def health_check(
        self, agent_id: str, **template_vars: str
    ) -> bool:
        """Check if a plug-in agent is healthy."""
        defn = self._registry.get(agent_id)
        if defn is None:
            return False

        endpoint = defn.resolve_endpoint(**template_vars)
        url = f"{endpoint}{defn.health_check}"

        try:
            if self._http is not None:
                response = await self._http.get(url, timeout=3.0)
                status = getattr(response, "status_code", 0)
                return 200 <= status < 300
        except Exception:
            pass
        return False

    async def health_check_all(
        self, **template_vars: str
    ) -> dict[str, bool]:
        """Check health of all registered plug-in agents."""
        results: dict[str, bool] = {}
        for defn in self._registry.list_available():
            results[defn.agent_id] = await self.health_check(
                defn.agent_id, **template_vars
            )
        return results

    # -- Stats --------------------------------------------------------------

    @property
    def call_count(self) -> int:
        """Total dispatch calls."""
        return self._call_count

    @property
    def error_count(self) -> int:
        """Total dispatch errors."""
        return self._error_count


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _elapsed(start: float) -> float:
    """Milliseconds since start."""
    return (time.monotonic() - start) * 1000
