"""Slack Integration — Channel Adapter for AI Bot (SPEC-1776).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from src.integrations.slack.adapter import SlackAdapter
from src.integrations.slack.manifest import SLACK_MANIFEST

__all__ = ["SlackAdapter", "SLACK_MANIFEST"]


def slack_factory(tenant_id: str) -> SlackAdapter:
    """Create a SlackAdapter instance for a tenant."""
    return SlackAdapter(tenant_id=tenant_id)
