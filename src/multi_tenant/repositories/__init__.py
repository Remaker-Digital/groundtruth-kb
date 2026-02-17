"""
Repository package — re-exports all repository classes and exceptions.

All existing imports via ``from src.multi_tenant.repository import X``
continue to work unchanged via the re-export barrel in repository.py.
Direct imports from this package are also supported:

    from src.multi_tenant.repositories import TenantRepository
    from src.multi_tenant.repositories.base import TenantScopedRepository

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

# Base classes and exceptions
from src.multi_tenant.repositories.base import (
    DocumentConflictError,
    DocumentNotFoundError,
    TenantIsolationError,
    TenantScopedRepository,
)

# Domain repositories (tenant-scoped)
from src.multi_tenant.repositories.tenant import TenantRepository
from src.multi_tenant.repositories.conversation import ConversationRepository
from src.multi_tenant.repositories.usage import UsageRepository
from src.multi_tenant.repositories.customer import CustomerProfileRepository
from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
from src.multi_tenant.repositories.memory import MemoryVectorRepository
from src.multi_tenant.repositories.preferences import PreferencesRepository
from src.multi_tenant.repositories.team import TeamMemberRepository

# Platform-scoped repositories
from src.multi_tenant.repositories.platform import (
    AuditLogRepository,
    PlatformConfigRepository,
    PlatformScopedRepository,
)

__all__ = [
    # Exceptions
    "TenantIsolationError",
    "DocumentNotFoundError",
    "DocumentConflictError",
    # Base classes
    "TenantScopedRepository",
    "PlatformScopedRepository",
    # Tenant-scoped repositories
    "TenantRepository",
    "ConversationRepository",
    "UsageRepository",
    "CustomerProfileRepository",
    "KnowledgeBaseRepository",
    "MemoryVectorRepository",
    "PreferencesRepository",
    "TeamMemberRepository",
    # Platform-scoped repositories
    "PlatformConfigRepository",
    "AuditLogRepository",
]
