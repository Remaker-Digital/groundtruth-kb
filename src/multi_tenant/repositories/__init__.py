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
from src.multi_tenant.repositories.platform_admin import PlatformAdminRepository
from src.multi_tenant.repositories.sla_snapshots import SLASnapshotRepository
from src.multi_tenant.repositories.verification import VerificationTokenRepository
from src.multi_tenant.repositories.incidents import IncidentRepository
from src.multi_tenant.repositories.alerts import AlertRuleRepository, AlertHistoryRepository
from src.multi_tenant.repositories.domain_index import DomainIndexRepository
from src.multi_tenant.repositories.agent_overlays import TenantAgentOverlayRepository
from src.multi_tenant.repositories.agent_bindings import AgentSkillBindingRepository

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
    "SLASnapshotRepository",
    "VerificationTokenRepository",
    "IncidentRepository",
    "AlertRuleRepository",
    "AlertHistoryRepository",
    "PlatformAdminRepository",
    "DomainIndexRepository",
    "TenantAgentOverlayRepository",
    "AgentSkillBindingRepository",
]
