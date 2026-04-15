# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Agent provider schema for GroundTruth project scaffolding."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentProvider:
    """Definition of an AI agent provider for dual-agent project scaffolding.

    Attributes:
        provider_id: Unique identifier for the provider (e.g. ``claude-code``).
        display_name: Human-readable display name for use in templates.
        cli_command: Command name used to invoke the agent CLI.
        model_label: Model label string for documentation and templates.
        config_files: Tuple of config files this provider reads at session start.
        bridge_role: Either ``"prime"`` (builder) or ``"loyal-opposition"`` (reviewer).
        invocation_prompt_source: Template path for the session invocation prompt.
    """

    provider_id: str
    display_name: str
    cli_command: str
    model_label: str
    config_files: tuple[str, ...]
    bridge_role: str
    invocation_prompt_source: str


CLAUDE_CODE: AgentProvider = AgentProvider(
    provider_id="claude-code",
    display_name="Claude Code (Opus 4.6)",
    cli_command="claude",
    model_label="claude-opus-4-6",
    config_files=("CLAUDE.md", ".claude/settings.json"),
    bridge_role="prime",
    invocation_prompt_source="templates/project/prime-builder-prompt.md",
)

CODEX: AgentProvider = AgentProvider(
    provider_id="codex",
    display_name="GPT Codex (Loyal Opposition)",
    cli_command="codex",
    model_label="gpt-codex",
    config_files=("AGENTS.md",),
    bridge_role="loyal-opposition",
    invocation_prompt_source="templates/project/loyal-opposition-prompt.md",
)

_REGISTRY: dict[str, AgentProvider] = {
    CLAUDE_CODE.provider_id: CLAUDE_CODE,
    CODEX.provider_id: CODEX,
}


def get_provider(provider_id: str) -> AgentProvider:
    """Return provider by id or raise ValueError.

    Args:
        provider_id: The provider identifier string (e.g. ``"claude-code"``).

    Returns:
        The matching :class:`AgentProvider` instance.

    Raises:
        ValueError: If ``provider_id`` is not in the registry.
    """
    if provider_id not in _REGISTRY:
        valid = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"Unknown provider {provider_id!r}. Valid providers: {valid}")
    return _REGISTRY[provider_id]


def list_providers() -> list[AgentProvider]:
    """Return all registered providers in stable order.

    Returns:
        List of all :class:`AgentProvider` instances.
    """
    return list(_REGISTRY.values())
