"""Google Docs/Drive Integration — Knowledge Source Adapter (SPEC-1777).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from src.integrations.google_docs.adapter import GoogleDocsAdapter
from src.integrations.google_docs.manifest import GOOGLE_DOCS_MANIFEST

__all__ = ["GoogleDocsAdapter", "GOOGLE_DOCS_MANIFEST"]


def google_docs_factory(tenant_id: str) -> GoogleDocsAdapter:
    """Create a GoogleDocsAdapter instance for a tenant."""
    return GoogleDocsAdapter(tenant_id=tenant_id)
