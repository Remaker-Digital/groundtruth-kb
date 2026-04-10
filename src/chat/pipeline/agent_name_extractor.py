# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""NL agent name extraction for peer agent escalation (SPEC-1864).

Extracts agent names from natural language messages like "transfer to sales"
or "talk to the campaign agent" and resolves them to agent IDs using fuzzy
matching against the plugin registry.

Used as a fallback in IntentRouter after exact intent matching fails.
Conservative: high threshold (0.75), PEER agents only, no false positives.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import difflib
import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agents.plugins.registry import PluginAgentRegistry

logger = logging.getLogger(__name__)

# Regex patterns for agent reference extraction.
# Captures 1-3 words after escalation/transfer/routing phrases.
_ESCALATION_PHRASES = re.compile(
    r"(?:transfer\s+(?:me\s+)?to|escalate\s+to|talk\s+to|"
    r"connect\s+(?:me\s+)?(?:to|with)|route\s+to|"
    r"hand\s+off\s+to|send\s+(?:me\s+)?to|"
    r"let\s+(?:the\s+)?|I\s+need\s+(?:the\s+)?)"
    r"\s*(?:the\s+)?"
    r"(\w+(?:\s+\w+){0,2}?)(?:\s+(?:agent|team|bot|handle|help))?",
    re.IGNORECASE,
)

# Minimum similarity threshold for fuzzy matching
_MATCH_THRESHOLD = 0.75


def build_agent_name_index(
    registry: PluginAgentRegistry,
) -> dict[str, str]:
    """Build a normalized name → agent_id index from PEER agents only.

    Includes agent_id, display_name (lowercased), and common variations.
    """
    index: dict[str, str] = {}

    for defn in registry.list_agents():
        if defn.agent_kind != "peer":
            continue

        agent_id = defn.agent_id

        # Primary: agent_id itself (e.g., "sales", "campaigns")
        index[agent_id.lower()] = agent_id

        # Display name (e.g., "Sales Agent" → "sales agent")
        if defn.display_name:
            index[defn.display_name.lower()] = agent_id
            # Also index first word of display name (e.g., "Sales")
            first_word = defn.display_name.split()[0].lower()
            if first_word not in index:
                index[first_word] = agent_id

        # Underscore/hyphen variations (e.g., "bot_agent" → "bot agent")
        if "_" in agent_id or "-" in agent_id:
            normalized = agent_id.replace("_", " ").replace("-", " ").lower()
            index[normalized] = agent_id

    return index


def extract_agent_name(
    message: str,
    registry: PluginAgentRegistry,
) -> str | None:
    """Extract a peer agent ID from a natural language message.

    Returns the agent_id if a match is found above the threshold,
    or None if no agent reference is detected.

    Examples:
        "transfer to sales" → "sales"
        "talk to the Campaign Agent" → "campaigns"
        "escalate to bot" → "bot_agent"
        "just say hello" → None
    """
    if not message:
        return None

    index = build_agent_name_index(registry)
    if not index:
        return None

    # Extract candidate phrases from the message
    matches = _ESCALATION_PHRASES.findall(message)
    if not matches:
        return None

    index_keys = list(index.keys())

    for candidate in matches:
        candidate_lower = candidate.strip().lower()
        if not candidate_lower:
            continue

        # Exact match first
        if candidate_lower in index:
            agent_id = index[candidate_lower]
            logger.debug(
                "NL agent extraction: exact match '%s' → %s",
                candidate, agent_id,
            )
            return agent_id

        # Fuzzy match
        close = difflib.get_close_matches(
            candidate_lower, index_keys, n=1, cutoff=_MATCH_THRESHOLD,
        )
        if close:
            agent_id = index[close[0]]
            logger.debug(
                "NL agent extraction: fuzzy match '%s' ~ '%s' → %s",
                candidate, close[0], agent_id,
            )
            return agent_id

    return None
