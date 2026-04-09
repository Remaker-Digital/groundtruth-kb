# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Campaigns Agent — Marketing Campaign Information MCP Server (SPEC-1707).

Provides campaign-aware tools for the AI pipeline: active campaigns,
discount codes, talking points, and conversation metrics tracking.

Integrations: Shopify Marketing, Mailchimp, Klaviyo, etc.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

AGENT_ID = "campaigns"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass
class Campaign:
    """Marketing campaign record."""

    campaign_id: str
    name: str
    status: str = "active"  # draft, active, paused, completed
    start_date: str = ""
    end_date: str = ""
    discount_codes: list[str] = field(default_factory=list)
    talking_points: list[str] = field(default_factory=list)
    channels: list[str] = field(default_factory=list)  # email, sms, social, chat
    target_audience: str = ""
    budget: float = 0.0
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class CampaignMetric:
    """Campaign conversation metric."""

    campaign_id: str
    conversation_id: str
    tenant_id: str
    event: str  # mentioned, code_shared, code_redeemed, conversion
    timestamp: str = ""


# ---------------------------------------------------------------------------
# Agent tools
# ---------------------------------------------------------------------------


class CampaignsAgentTools:
    """Tool implementations for the Campaigns Agent.

    Each method maps to an MCP tool capability defined in agents.yaml.
    """

    def __init__(self) -> None:
        self._campaigns: dict[str, list[Campaign]] = {}  # tenant_id → campaigns
        self._metrics: list[CampaignMetric] = []

    async def list_active(
        self,
        tenant_id: str,
        *,
        channel: str | None = None,
    ) -> list[dict[str, Any]]:
        """List active/scheduled campaigns for a tenant.

        Tool: campaigns.list_active
        """
        campaigns = self._campaigns.get(tenant_id, [])
        active = [c for c in campaigns if c.status in ("active", "scheduled")]
        if channel:
            active = [c for c in active if channel in c.channels]
        return [
            {
                "campaign_id": c.campaign_id,
                "name": c.name,
                "status": c.status,
                "discount_codes": c.discount_codes,
                "channels": c.channels,
                "start_date": c.start_date,
                "end_date": c.end_date,
            }
            for c in active
        ]

    async def get_discount_codes(
        self,
        tenant_id: str,
        *,
        campaign_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get available discount codes, optionally filtered by campaign.

        Tool: campaigns.get_discount_codes
        """
        campaigns = self._campaigns.get(tenant_id, [])
        if campaign_id:
            campaigns = [c for c in campaigns if c.campaign_id == campaign_id]

        codes = []
        for c in campaigns:
            if c.status == "active":
                for code in c.discount_codes:
                    codes.append({
                        "code": code,
                        "campaign_id": c.campaign_id,
                        "campaign_name": c.name,
                    })
        return codes

    async def get_talking_points(
        self,
        tenant_id: str,
        *,
        campaign_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get campaign talking points for the AI pipeline.

        Tool: campaigns.get_talking_points
        """
        campaigns = self._campaigns.get(tenant_id, [])
        if campaign_id:
            campaigns = [c for c in campaigns if c.campaign_id == campaign_id]

        points = []
        for c in campaigns:
            if c.status == "active" and c.talking_points:
                points.append({
                    "campaign_id": c.campaign_id,
                    "campaign_name": c.name,
                    "talking_points": c.talking_points,
                    "target_audience": c.target_audience,
                })
        return points

    async def track_metric(
        self,
        tenant_id: str,
        campaign_id: str,
        conversation_id: str,
        event: str,
    ) -> dict[str, Any]:
        """Track a campaign-related conversation metric.

        Tool: campaigns.track_metrics
        """
        metric = CampaignMetric(
            campaign_id=campaign_id,
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            event=event,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self._metrics.append(metric)
        logger.info(
            "Campaign metric: tenant=%s campaign=%s event=%s",
            tenant_id, campaign_id, event,
        )
        return {"recorded": True, "event": event, "campaign_id": campaign_id}

    # -- Test helpers -------------------------------------------------------

    def seed_campaign(self, tenant_id: str, campaign: Campaign) -> None:
        """Seed a campaign for testing."""
        if tenant_id not in self._campaigns:
            self._campaigns[tenant_id] = []
        self._campaigns[tenant_id].append(campaign)
