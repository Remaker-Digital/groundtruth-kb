"""MCP Agent Plug-in Registry (SPEC-1706).

Configuration-driven agent discovery and dispatch.  Loads agent
definitions from agents.yaml and provides lookup, health check,
and capability queries.  Supports both internal domain agents
and external 3rd-party MCP servers.

Key constraints (SPEC-1706):
  - New agents MUST NOT require changes to existing code paths
  - Agent isolation is mandatory (container-level separation)
  - Configuration-driven discovery (no hard-coded registration)
  - MCP protocol is the standard interface for all communication

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CONFIG_PATH = Path(__file__).parent / "agents.yaml"


class AgentKind(str, Enum):
    """Kind classification for agents (SPEC-1852).

    core     — part of the standard customer-service pipeline
    peer     — independently routable via IntentRouter
    internal — infrastructure agent, not directly invocable by users

    Named 'agent_kind' (not 'agent_type') to avoid collision with
    base.py's agent_type routing identifier.
    """

    CORE = "core"
    PEER = "peer"
    INTERNAL = "internal"


# Backward-compat alias — do not use in new code
AgentType = AgentKind


class AgentCategory(str, Enum):
    """Categories for plug-in agents."""

    MARKETING = "marketing"
    AGENT_TO_AGENT = "agent-to-agent"
    COMMERCE = "commerce"
    ESCALATION = "escalation"
    SCHEDULING = "scheduling"
    EXTERNAL = "external"


class AgentStatus(str, Enum):
    """Lifecycle status of a plug-in agent."""

    AVAILABLE = "available"
    BETA = "beta"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class AuthType(str, Enum):
    """Authentication methods for agent connections."""

    INTERNAL = "internal"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    NONE = "none"


class SkillMode(str, Enum):
    """Execution mode for a skill (SPEC-1853).

    read     — no side effects (queries, lookups)
    mutate   — creates or modifies external state
    internal — system-only, not tenant-configurable
    """

    READ = "read"
    MUTATE = "mutate"
    INTERNAL = "internal"


# ---------------------------------------------------------------------------
# Skill definition (SPEC-1853)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SkillDefinition:
    """Immutable definition of an agent skill.

    skill_id format: "{agent_id}:{skill_name}" (SPEC-1853 req 1).
    Maps stable skill identity to underlying MCP tool names.
    """

    skill_id: str
    agent_id: str
    skill_name: str
    display_name: str
    description: str = ""
    mode: str = "read"
    mcp_tool_names: tuple[str, ...] = ()
    credential_types: tuple[str, ...] = ()
    enabled: bool = True

    @property
    def is_read_only(self) -> bool:
        return self.mode == SkillMode.READ.value


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PluginAgentDefinition:
    """Immutable definition of a plug-in agent loaded from agents.yaml."""

    agent_id: str
    display_name: str
    description: str
    spec_id: str
    category: str
    endpoint: str
    agent_kind: str = "peer"
    health_check: str = "/health"
    auth_type: str = "internal"
    credential_env: str = ""
    tier_gate: str = "professional"
    capabilities: tuple[str, ...] = ()
    skills: tuple[SkillDefinition, ...] = ()
    read_only: bool = True
    status: str = "available"
    is_external: bool = False

    def has_capability(self, cap: str) -> bool:
        """Check if this agent supports a given capability."""
        return cap in self.capabilities

    def resolve_endpoint(self, **kwargs: str) -> str:
        """Resolve endpoint with environment variables and template vars.

        Supports ${ENV_VAR:-default} syntax and {template_var} substitution.
        """
        endpoint = self.endpoint
        # Resolve ${ENV:-default} patterns
        if "${" in endpoint:
            import re
            for match in re.finditer(r'\$\{(\w+)(?::-(.*?))?\}', endpoint):
                env_key = match.group(1)
                default = match.group(2) or ""
                value = os.environ.get(env_key, default)
                endpoint = endpoint.replace(match.group(0), value)
        # Resolve {key} template vars
        for key, value in kwargs.items():
            endpoint = endpoint.replace(f"{{{key}}}", value)
        return endpoint


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class PluginAgentRegistry:
    """Singleton registry for plug-in MCP agents.

    Loads definitions from agents.yaml at startup.  Provides lookups
    by agent_id, capability, category, and tier.
    """

    _instance: PluginAgentRegistry | None = None

    def __init__(self) -> None:
        self._agents: dict[str, PluginAgentDefinition] = {}
        self._skills: dict[str, SkillDefinition] = {}
        self._pipeline_edges: list[tuple[str, str]] = []
        self._routing_rules: dict[str, dict[str, str]] = {}
        self._loaded = False

    @classmethod
    def get_instance(cls) -> PluginAgentRegistry:
        """Return the singleton registry instance."""
        if cls._instance is None:
            cls._instance = PluginAgentRegistry()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (testing only)."""
        cls._instance = None

    # -- Loading ------------------------------------------------------------

    def load_from_yaml(self, path: Path | None = None) -> int:
        """Load agent definitions from YAML config.

        Returns the number of agents loaded.
        """
        config_path = path or _CONFIG_PATH

        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML not installed — cannot load agents.yaml")
            self._loaded = True
            return 0

        if not config_path.exists():
            logger.warning("agents.yaml not found at %s", config_path)
            self._loaded = True
            return 0

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
        except Exception:
            logger.exception("Failed to parse agents.yaml")
            self._loaded = True
            return 0

        # Load pipeline edge topology
        raw_edges = config.get("pipeline_edges") or []
        self._pipeline_edges = [
            (e[0], e[1]) for e in raw_edges
            if isinstance(e, list) and len(e) == 2
        ]

        # Load routing rules (SPEC-1861 / ADR-003)
        raw_rules = config.get("routing_rules") or {}
        self._routing_rules = {
            intent: rule for intent, rule in raw_rules.items()
            if isinstance(rule, dict)
        }

        count = 0

        # Load internal agents
        for agent_id, agent_cfg in (config.get("agents") or {}).items():
            skills = self._parse_skills(agent_id, agent_cfg)
            defn = PluginAgentDefinition(
                agent_id=agent_id,
                display_name=agent_cfg.get("display_name", agent_id),
                description=agent_cfg.get("description", ""),
                spec_id=agent_cfg.get("spec_id", ""),
                category=agent_cfg.get("category", ""),
                endpoint=agent_cfg.get("endpoint", ""),
                agent_kind=agent_cfg.get("agent_kind", AgentKind.PEER.value),
                health_check=agent_cfg.get("health_check", "/health"),
                auth_type=agent_cfg.get("auth_type", "internal"),
                tier_gate=agent_cfg.get("tier_gate", "professional"),
                capabilities=tuple(agent_cfg.get("capabilities", [])),
                skills=skills,
                status=agent_cfg.get("status", "available"),
                is_external=False,
            )
            self._agents[agent_id] = defn
            self._register_skills(skills)
            count += 1

        # Load external MCP servers
        for server_id, server_cfg in (config.get("external_servers") or {}).items():
            skills = self._parse_skills(server_id, server_cfg)
            defn = PluginAgentDefinition(
                agent_id=server_id,
                display_name=server_cfg.get("display_name", server_id),
                description=server_cfg.get("description", ""),
                spec_id=server_cfg.get("spec_id", ""),
                category="external",
                endpoint=server_cfg.get("endpoint", ""),
                agent_kind=AgentKind.PEER.value,
                auth_type=server_cfg.get("auth_type", "none"),
                credential_env=server_cfg.get("credential_env", ""),
                tier_gate=server_cfg.get("tier_gate", "starter"),
                capabilities=tuple(server_cfg.get("capabilities", [])),
                skills=skills,
                read_only=server_cfg.get("read_only", True),
                status=server_cfg.get("status", "available"),
                is_external=True,
            )
            self._agents[server_id] = defn
            self._register_skills(skills)
            count += 1

        self._loaded = True
        logger.info(
            "Loaded %d plug-in agent definitions from %s",
            count,
            config_path,
        )
        return count

    def load_from_dict(self, definitions: dict[str, dict[str, Any]]) -> int:
        """Load agent definitions from a dict (testing)."""
        count = 0
        for agent_id, cfg in definitions.items():
            skills = self._parse_skills(agent_id, cfg)
            defn = PluginAgentDefinition(
                agent_id=agent_id,
                display_name=cfg.get("display_name", agent_id),
                description=cfg.get("description", ""),
                spec_id=cfg.get("spec_id", ""),
                category=cfg.get("category", ""),
                endpoint=cfg.get("endpoint", ""),
                agent_kind=cfg.get("agent_kind", AgentKind.PEER.value),
                health_check=cfg.get("health_check", "/health"),
                auth_type=cfg.get("auth_type", "internal"),
                credential_env=cfg.get("credential_env", ""),
                tier_gate=cfg.get("tier_gate", "professional"),
                capabilities=tuple(cfg.get("capabilities", [])),
                skills=skills,
                read_only=cfg.get("read_only", True),
                status=cfg.get("status", "available"),
                is_external=cfg.get("is_external", False),
            )
            self._agents[agent_id] = defn
            self._register_skills(skills)
            count += 1
        self._loaded = True
        return count

    @staticmethod
    def _parse_skills(
        agent_id: str, cfg: dict[str, Any]
    ) -> tuple[SkillDefinition, ...]:
        """Parse skill definitions from an agent config block."""
        raw_skills = cfg.get("skills") or {}
        results: list[SkillDefinition] = []
        for skill_name, skill_cfg in raw_skills.items():
            if not isinstance(skill_cfg, dict):
                continue
            skill_id = f"{agent_id}:{skill_name}"
            results.append(SkillDefinition(
                skill_id=skill_id,
                agent_id=agent_id,
                skill_name=skill_name,
                display_name=skill_cfg.get("display_name", skill_name),
                description=skill_cfg.get("description", ""),
                mode=skill_cfg.get("mode", SkillMode.READ.value),
                mcp_tool_names=tuple(skill_cfg.get("mcp_tool_names", [])),
                credential_types=tuple(skill_cfg.get("credential_types", [])),
                enabled=skill_cfg.get("enabled", True),
            ))
        return tuple(results)

    def _register_skills(self, skills: tuple[SkillDefinition, ...]) -> None:
        """Add skills to the global skill index."""
        for skill in skills:
            self._skills[skill.skill_id] = skill

    def _ensure_loaded(self) -> None:
        """Lazy-load from YAML on first access."""
        if not self._loaded:
            self.load_from_yaml()

    # -- Queries ------------------------------------------------------------

    def get(self, agent_id: str) -> PluginAgentDefinition | None:
        """Get a plug-in agent definition by ID."""
        self._ensure_loaded()
        return self._agents.get(agent_id)

    def list_available(
        self,
        *,
        category: str | None = None,
        capability: str | None = None,
        tier: str | None = None,
        include_external: bool = True,
    ) -> list[PluginAgentDefinition]:
        """List available plug-in agents, optionally filtered."""
        self._ensure_loaded()
        tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
        results = []

        for defn in self._agents.values():
            if defn.status in (AgentStatus.DISABLED.value, AgentStatus.DEPRECATED.value):
                continue
            if not include_external and defn.is_external:
                continue
            if category and defn.category != category:
                continue
            if capability and not defn.has_capability(capability):
                continue
            if tier:
                tenant_level = tier_order.get(tier, 0)
                required_level = tier_order.get(defn.tier_gate, 0)
                if tenant_level < required_level:
                    continue
            results.append(defn)

        return sorted(results, key=lambda d: d.display_name)

    def find_by_capability(self, capability: str) -> list[PluginAgentDefinition]:
        """Find all agents that provide a given capability."""
        self._ensure_loaded()
        return [
            defn for defn in self._agents.values()
            if defn.has_capability(capability) and defn.status != AgentStatus.DISABLED.value
        ]

    def get_internal_agents(self) -> list[PluginAgentDefinition]:
        """List only internal domain agents (not external MCP servers)."""
        return self.list_available(include_external=False)

    def get_external_servers(self) -> list[PluginAgentDefinition]:
        """List only external 3rd-party MCP servers."""
        self._ensure_loaded()
        return [
            defn for defn in self._agents.values()
            if defn.is_external and defn.status != AgentStatus.DISABLED.value
        ]

    @property
    def agent_count(self) -> int:
        """Total number of registered agents."""
        self._ensure_loaded()
        return len(self._agents)

    @property
    def loaded(self) -> bool:
        """Whether the registry has been loaded."""
        return self._loaded

    # -- Tool catalog -------------------------------------------------------

    def get_tool_catalog(
        self, *, tier: str | None = None
    ) -> list[dict[str, Any]]:
        """Build a tool catalog for LLM tool-use.

        Returns a list of tool definitions compatible with the OpenAI
        tool-use format (function name, description, parameters).
        Each capability maps to one tool.
        """
        catalog: list[dict[str, Any]] = []
        for defn in self.list_available(tier=tier):
            for cap in defn.capabilities:
                catalog.append({
                    "type": "function",
                    "function": {
                        "name": cap,
                        "description": f"[{defn.display_name}] {defn.description}",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Query or parameters for this capability",
                                },
                            },
                        },
                    },
                    "_agent_id": defn.agent_id,
                    "_endpoint": defn.endpoint,
                    "_is_external": defn.is_external,
                })
        return catalog

    def resolve_tool_agent(self, tool_name: str) -> PluginAgentDefinition | None:
        """Find which agent provides a given tool/capability."""
        self._ensure_loaded()
        for defn in self._agents.values():
            if defn.has_capability(tool_name):
                return defn
        return None

    # -- Agent kind queries (SPEC-1852) ------------------------------------

    def list_agents(
        self,
        *,
        agent_kind: str | None = None,
        include_disabled: bool = False,
    ) -> list[PluginAgentDefinition]:
        """List all registered agents with optional kind filter (SPEC-1852 req 7)."""
        self._ensure_loaded()
        results = []
        for defn in self._agents.values():
            if not include_disabled and defn.status in (
                AgentStatus.DISABLED.value, AgentStatus.DEPRECATED.value
            ):
                continue
            if agent_kind and defn.agent_kind != agent_kind:
                continue
            results.append(defn)
        return sorted(results, key=lambda d: d.agent_id)

    def get_core_agents(self) -> list[PluginAgentDefinition]:
        """List agents that are part of the standard pipeline."""
        return self.list_agents(agent_kind=AgentKind.CORE.value)

    def get_peer_agents(self) -> list[PluginAgentDefinition]:
        """List independently routable business agents."""
        return self.list_agents(agent_kind=AgentKind.PEER.value)

    def get_core_agent_ids(self) -> list[str]:
        """Return agent_ids for core pipeline agents (replaces PIPELINE_AGENTS)."""
        return [a.agent_id for a in self.get_core_agents()]

    def get_pipeline_edges(self) -> list[tuple[str, str]]:
        """Return pipeline edge topology (replaces PIPELINE_EDGES)."""
        self._ensure_loaded()
        return list(self._pipeline_edges)

    # -- Routing rules (SPEC-1861 / ADR-003) --------------------------------

    def get_routing_rule(self, intent: str) -> dict[str, str] | None:
        """Get the default routing rule for an intent (SPEC-1861).

        Returns dict with suggested_peer and skill, or None if no rule.
        Tenant overlay intent_routes take precedence over these defaults.
        """
        self._ensure_loaded()
        return self._routing_rules.get(intent)

    def get_all_routing_rules(self) -> dict[str, dict[str, str]]:
        """Return all configured routing rules."""
        self._ensure_loaded()
        return dict(self._routing_rules)

    # -- Skill queries (SPEC-1853) -----------------------------------------

    def get_skill(self, skill_id: str) -> SkillDefinition | None:
        """Get a skill definition by its stable skill_id."""
        self._ensure_loaded()
        return self._skills.get(skill_id)

    def list_skills(
        self,
        agent_id: str | None = None,
        *,
        mode: str | None = None,
        enabled_only: bool = True,
    ) -> list[SkillDefinition]:
        """List skills, optionally filtered by agent and mode (SPEC-1853 req 6)."""
        self._ensure_loaded()
        results = []
        for skill in self._skills.values():
            if agent_id and skill.agent_id != agent_id:
                continue
            if mode and skill.mode != mode:
                continue
            if enabled_only and not skill.enabled:
                continue
            results.append(skill)
        return sorted(results, key=lambda s: s.skill_id)

    def resolve_skill_to_tools(self, skill_id: str) -> tuple[str, ...]:
        """Map a skill_id to its underlying MCP tool name(s) (SPEC-1853 req 3)."""
        skill = self.get_skill(skill_id)
        if skill is None:
            return ()
        return skill.mcp_tool_names
