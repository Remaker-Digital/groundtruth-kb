"""Analytics mixin — fire-and-forget analytics event dispatch.

R10 refactoring — extracted from pipeline.py (session 39).
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import httpx

from src.chat.pipeline.constants import (
    AGENT_ANALYTICS_PATH,
    USE_AGENT_CONTAINERS,
)

if TYPE_CHECKING:
    from src.multi_tenant.pipeline_resilience import PipelineTimeoutBudget
    from src.multi_tenant.response_explainability import DecisionTraceBuilder

logger = logging.getLogger(__name__)


class AnalyticsMixin:
    """Mixin providing analytics dispatch for ChatPipeline.

    Methods on this mixin access instance attributes set by ChatPipeline.__init__:
    _an_agent, _agent_urls, _get_http_client().
    """

    async def _fire_analytics(
        self,
        tenant_id: str,
        conversation_id: str,
        intent: str,
        budget: PipelineTimeoutBudget,
        trace: DecisionTraceBuilder,
    ) -> None:
        """Send analytics event asynchronously (non-blocking).

        Routes via transport → HTTP → in-process (SPEC-1536).
        Analytics is fire-and-forget — failures never block the pipeline.
        """
        try:
            analytics_data = {
                "tenant_id": tenant_id,
                "conversation_id": conversation_id,
                "intent": intent,
                "stages": [
                    {
                        "stage": s.stage,
                        "elapsed_ms": s.elapsed_ms,
                        "succeeded": s.succeeded,
                    }
                    for s in budget.stages
                ],
                "total_latency_ms": budget.elapsed_ms,
            }

            # Priority 1: SLIM/NATS transport (SPEC-1536)
            sent = False
            try:
                from src.multi_tenant.agntcy_sdk_integration import (
                    _transport,
                    create_a2a_client,
                )

                if _transport is not None:
                    client = create_a2a_client("analytics-collector")
                    await client.send(analytics_data, headers={
                        "X-Tenant-Id": tenant_id,
                        "X-Conversation-Id": conversation_id,
                    })
                    sent = True
            except Exception:
                logger.debug("Transport analytics dispatch failed — falling back")

            if sent:
                return

            # Priority 2: HTTP container
            if USE_AGENT_CONTAINERS:
                try:
                    url = self._agent_urls.get("analytics-collector", "")
                    client = await self._get_http_client()
                    await client.post(
                        f"{url.rstrip('/')}{AGENT_ANALYTICS_PATH}",
                        json=analytics_data,
                        timeout=httpx.Timeout(connect=1.0, read=2.0, write=1.0, pool=1.0),
                    )
                    return
                except Exception:
                    logger.debug("HTTP analytics dispatch failed — falling back to in-process")

            # Priority 3: In-process agent (fallback)
            await self._an_agent.process(analytics_data, {})
        except Exception:
            # Analytics is fire-and-forget — never block the pipeline
            logger.debug(
                "Analytics event failed for conv=%s — non-critical",
                conversation_id,
            )
