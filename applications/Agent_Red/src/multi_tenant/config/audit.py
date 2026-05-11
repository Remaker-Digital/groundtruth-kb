# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Config audit logging — records config changes to the audit log.

Scrubs PII-classified fields before writing to the append-only
audit_log collection.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from src.multi_tenant.cosmos_schema import AuditEventType
from src.multi_tenant.tenant_config_schema import get_field_registry

logger = logging.getLogger(__name__)


async def _log_config_change(
    audit_repo: Any,
    tenant_id: str,
    actor: str,
    from_version: int,
    to_version: int,
    changes: dict[str, Any],
    reset: bool = False,
) -> None:
    """Log a config change to the audit log.

    Args:
        audit_repo: AuditLogRepository instance (or None to skip).
        tenant_id: Tenant identifier.
        actor: Who made the change.
        from_version: Previous version number.
        to_version: New version number.
        changes: Dict of field_name → {old, new} change records.
        reset: Whether this was a reset-to-defaults operation.
    """
    if audit_repo is None:
        return

    # Scrub potentially sensitive values from the audit payload
    scrubbed_changes: dict[str, Any] = {}
    registry = get_field_registry()
    for field_name, change in changes.items():
        field_def = registry.get(field_name)
        if field_def and field_def.pii_classification != "none":
            scrubbed_changes[field_name] = {"changed": True, "pii_scrubbed": True}
        else:
            scrubbed_changes[field_name] = change

    await audit_repo.log_event(
        event_type=AuditEventType.CONFIG_UPDATED,
        tenant_id=tenant_id,
        actor=actor,
        actor_type="user" if actor.startswith("user:") else "system",
        payload={
            "action": "reset_to_defaults" if reset else "update",
            "from_version": from_version,
            "to_version": to_version,
            "fields_changed": list(changes.keys()),
            "change_count": len(changes),
            "changes": scrubbed_changes,
        },
    )
