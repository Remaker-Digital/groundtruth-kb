"""Baseline migration — marks v1.0.0 schema as the starting point.

This is a no-op migration. It exists solely to establish the migration
tracking baseline. All subsequent migrations build on the 1.0.0 schema.

1.0.0 Schema (10 containers):
    - tenants (partition: /tenant_id)
    - conversations (partition: /tenant_id)
    - usage (partition: /tenant_id)
    - customer_profiles (partition: /tenant_id)
    - knowledge_bases (partition: /tenant_id)
    - memory_vectors (partition: /tenant_id)
    - preferences (partition: /tenant_id)
    - team_members (partition: /tenant_id)
    - platform_config (partition: /config_type)
    - audit_log (partition: /time_partition)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

VERSION = "000"
DESCRIPTION = "Baseline — marks v1.0.0 schema (10 containers, no changes)"


async def up(cosmos_manager: Any) -> None:
    """No-op. Establishes migration tracking baseline."""
    logger.info(
        "Baseline migration: v1.0.0 schema with 10 containers established. "
        "No schema changes applied."
    )
