"""CQ-7: Merchant quality configuration (SPEC-0186 / WI-1517).

Tenant-level quality thresholds and preferences.  Merchants can
configure their quality sensitivity — e.g., stricter thresholds for
premium support, or relaxed thresholds during onboarding.

Configuration is stored in the tenant's Cosmos document and read at
conversation start.  When no config exists, sensible defaults apply.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MerchantQualityConfig(BaseModel):
    """Merchant-configurable quality settings.

    Stored in the tenant document under ``quality_config``.
    """

    quality_threshold: float = Field(
        default=3.5,
        ge=1.0,
        le=5.0,
        description="Minimum overall quality score to consider 'passing' (1.0-5.0)",
    )
    escalation_threshold: float = Field(
        default=2.5,
        ge=1.0,
        le=5.0,
        description="Quality below this triggers escalation consideration (1.0-5.0)",
    )
    consecutive_low_turns: int = Field(
        default=3,
        ge=1,
        le=10,
        description="How many consecutive low-quality turns before escalation",
    )
    enable_quality_feedback: bool = Field(
        default=True,
        description="Enable quality feedback loop (runtime prompt guidance)",
    )
    enable_quality_escalation: bool = Field(
        default=True,
        description="Enable quality-aware escalation recommendations",
    )


# Module-level default instance
DEFAULT_QUALITY_CONFIG = MerchantQualityConfig()


def get_merchant_quality_config(
    tenant_doc: dict[str, Any] | None = None,
) -> MerchantQualityConfig:
    """Read quality config from a tenant document, falling back to defaults.

    Args:
        tenant_doc: The tenant's Cosmos document (or None for defaults).

    Returns:
        MerchantQualityConfig with tenant-specific or default values.
    """
    if not tenant_doc:
        return DEFAULT_QUALITY_CONFIG

    raw = tenant_doc.get("quality_config")
    if not raw or not isinstance(raw, dict):
        return DEFAULT_QUALITY_CONFIG

    try:
        return MerchantQualityConfig(**raw)
    except Exception as exc:
        logger.warning(
            "Invalid quality_config in tenant doc, using defaults: %s", exc
        )
        return DEFAULT_QUALITY_CONFIG


def update_merchant_quality_config(
    tenant_doc: dict[str, Any],
    config: MerchantQualityConfig,
) -> dict[str, Any]:
    """Merge updated quality config into a tenant document.

    Returns the updated document dict (caller is responsible for
    persisting to Cosmos).
    """
    tenant_doc["quality_config"] = config.model_dump()
    return tenant_doc
