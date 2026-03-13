"""
Config cache — in-memory TTL cache entry for resolved tenant config.

Decision #22: 60-second in-memory TTL per tenant. Cache is invalidated
on write. Each instance maintains its own cache — eventual consistency
within 60 seconds is acceptable for config changes.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.multi_tenant.cosmos_schema import TenantTier

# Decision #22 + SPEC-1751: 300-second in-memory cache (was 60s).
# At 680 tenants, 60s TTL causes excessive Cosmos reads. 300s reduces
# cache-miss rate by ~80%. Explicit invalidation on write keeps
# admin changes visible immediately.
CACHE_TTL_SECONDS = 300


@dataclass
class _CacheEntry:
    """In-memory cached resolved config for a tenant."""

    resolved: dict[str, Any]
    version: int
    tier: TenantTier
    expires_at: float  # time.monotonic() timestamp
