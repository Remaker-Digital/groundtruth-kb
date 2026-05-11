"""Zendesk Integration — Full Helpdesk Adapter (SPEC-1775).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from src.integrations.zendesk.adapter import ZendeskAdapter
from src.integrations.zendesk.manifest import ZENDESK_MANIFEST

__all__ = ["ZendeskAdapter", "ZENDESK_MANIFEST"]


def zendesk_factory(tenant_id: str) -> ZendeskAdapter:
    """Create a ZendeskAdapter instance for a tenant."""
    return ZendeskAdapter(tenant_id=tenant_id)
